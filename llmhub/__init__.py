import os
import asyncpg

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from llmhub.router import route
from service.chat.service_router import RouterChatCompletion
from utils.postgres import insert_api_call_log
from utils.auth import validate_request, verify_api_key
from pydantic_types.chat import (
    CreateChatCompletionRequest,
)


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    DATABASE_URL = os.getenv("DATABASE_URL")
    pool = await asyncpg.create_pool(DATABASE_URL)

    yield

    if pool:
        await pool.close()


app = FastAPI(lifespan=lifespan)


@app.api_route("/v1/chat/completions", methods=["POST"])
async def index(
    request: CreateChatCompletionRequest,
    validation: bool = Depends(validate_request),
    authorization: list = Depends(verify_api_key),
):
    if validation and authorization:
        try:
            model = route(request.messages[-1].content, model="automatic").strip()
            response = RouterChatCompletion(model=model, request=request)
            await insert_api_call_log(
                response_data=response,
                user_id=authorization[0],
                api_key_id=authorization[1],
                db_pg=pool,
            )

            return response
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles HTTP exceptions.
    Returns a standardized JSON response for HTTP exceptions.
    """
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
            "suggestion": "Ensure your request parameters are correct. If the issue persists, contact support: support@llmhub.dev",
        },
        headers=exc.headers,
    )


async def global_exception_handler(request: Request, exc: Exception):
    """
    Handles general exceptions.
    Returns a standardized JSON response for unhandled exceptions.
    """
    error_id = request.headers.get("X-Request-ID", "N/A")  # If request tracking is used

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "Error",
            "title": "Internal Server Error",
            "status": HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "An unexpected error occurred on the server. Please try again later.",
            "instance": str(request.url),
            "method": request.method,
            "error_id": error_id,
            "support": "If the error persists, contact support: support@llmhub.dev",
        },
        headers={"Content-Type": "application/problem+json"},
    )
