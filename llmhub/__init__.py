import asyncpg
import logging
import time
import traceback
import uuid

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from contextlib import asynccontextmanager
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from llmhub.router import route
from config import load_config
from service.chat.clients import ClientPool
from service.chat.service_router import RouterChatCompletion
from utils.postgres import insert_api_call_log
from utils.auth import validate_request, verify_api_key
from pydantic_types.chat import (
    CreateChatCompletionRequest,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("llmhub-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application"""
    global client_pool
    client_pool = None
    global pool
    pool = None
    global config
    config = dict()
    try:
        config = load_config()
        logger.info("Initializing database connection pool")

        pool = await asyncpg.create_pool(
            config["DATABASE_URL"], min_size=5, max_size=20, timeout=30
        )
        logger.info("Database connection pool established successfully")

        client_pool = ClientPool(config)

        logger.info("API client pool initialized successfully")

        yield
    except asyncpg.PostgresError as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        logger.error(traceback.format_exc())
        raise
    finally:
        if pool:
            logger.info("Closing database connection pool")
            await pool.close()
            logger.info("Database connection pool closed")


# Initialize FastAPI app
app = FastAPI(
    title="LLMHub API",
    description="API for LLMHub platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log request/response details and add request ID"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()

    logger.info(
        f"Request started: {request.method} {request.url.path} (ID: {request_id})"
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"(ID: {request_id}) - Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"(ID: {request_id}) - Error: {str(e)} - Time: {process_time:.3f}s"
        )
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "request_id": request_id},
        )


@app.api_route("/v1/chat/completions", methods=["POST"])
async def index(
    request: Request,
    validation: bool = Depends(validate_request),
    authorization: list = Depends(verify_api_key),
):
    """Chat completion endpoint"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info(f"Processing chat completion request (ID: {request_id})")

    request_body = await request.json()

    if not authorization:
        logger.warning(f"Authorization failed (ID: {request_id})")
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        chat_request = CreateChatCompletionRequest(**request_body)
    except Exception as e:
        logger.warning(f"Request validation failed (ID: {request_id}): {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")

    try:
        # Route to appropriate model based on content
        model = route(
            msg=chat_request.messages[-1].content,
            client_pool=client_pool,
            model="automatic",
        ).strip()
        logger.info(f"Selected model: {model} (ID: {request_id})")

        # Get completion response
        response = RouterChatCompletion(
            model=model, request=chat_request, client_pool=client_pool
        )

        # Log API call to database asynchronously without waiting
        from asyncio import create_task

        create_task(
            insert_api_call_log(
                response_data=response,
                user_id=authorization[0],
                api_key_id=authorization[1],
                db_pg=pool,
            )
        )

        logger.info(f"Successfully processed chat completion (ID: {request_id})")
        return response

    except Exception as e:
        logger.error(f"Error processing chat completion: {str(e)} (ID: {request_id})")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}",
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles HTTP exceptions.
    Returns a standardized JSON response for HTTP exceptions.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} (ID: {request_id})"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "Error",
            "title": "Request Failed",
            "status": exc.status_code,
            "detail": (
                exc.detail
                if exc.detail
                else "An unexpected error occurred. Please verify your request and try again."
            ),
            "instance": str(request.url),
            "method": request.method,
            "request_id": request_id,
            "suggestion": "Ensure your request parameters are correct. If the issue persists, contact support: support@llmhub.dev",
        },
        headers=exc.headers if hasattr(exc, "headers") and exc.headers else {},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handles general exceptions.
    Returns a standardized JSON response for unhandled exceptions.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unhandled exception: {str(exc)} (ID: {request_id})")
    logger.error(traceback.format_exc())

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "Error",
            "title": "Internal Server Error",
            "status": HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "An unexpected error occurred on the server. Please try again later.",
            "instance": str(request.url),
            "method": request.method,
            "request_id": request_id,
            "support": "If the error persists, contact support: support@llmhub.dev",
        },
        headers={"Content-Type": "application/problem+json"},
    )


# Add health check endpoint
@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint for monitoring"""
    request_id = getattr(request.state, "request_id", "unknown")
    try:
        # Verify database connection is working
        if "pool" in globals() and pool:
            try:
                async with pool.acquire() as conn:
                    await conn.execute("SELECT 1")
                logger.info(f"Health check successful (ID: {request_id})")
                return {
                    "status": "healthy",
                    "services": {"database": "up"},
                    "request_id": request_id,
                }
            except Exception as db_error:
                logger.error(
                    f"Health check database error: {str(db_error)} (ID: {request_id})"
                )
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "services": {"database": "down"},
                        "detail": str(db_error),
                        "request_id": request_id,
                    },
                )
        else:
            logger.error(
                f"Health check failed: database pool not initialized (ID: {request_id})"
            )
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "services": {"database": "not initialized"},
                    "request_id": request_id,
                },
            )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)} (ID: {request_id})")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "detail": str(e), "request_id": request_id},
        )
