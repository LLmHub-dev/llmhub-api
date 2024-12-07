import os


from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.responses import JSONResponse


from contextlib import asynccontextmanager


from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)


from llmhub.router import route


from service.chat.service_router import RouterChatCompletion


import asyncpg


from utils.database import get_mongo_client
from utils.auth import verify_token, validate_request, verify_api_key


from pymongo import MongoClient


from pydantic_types.chat import (
    CreateChatCompletionRequest,
)


from dotenv import load_dotenv


from utils.postgres import insert_api_call_log


load_dotenv()


mongo_client: MongoClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongo_client
    global pool
    # Startup logic
    mongo_client = get_mongo_client()

    # Initialize SQLAlchemy engine and session maker
    DATABASE_URL = os.getenv("DATABASE_URL")  # Ensure DATABASE_URL is in your .env
    pool = await asyncpg.create_pool(DATABASE_URL)
    
    yield  
    # Shutdown logic
    if mongo_client:
        mongo_client.close()
        mongo_client = None

    if pool:
        pool.close()

app = FastAPI(lifespan=lifespan)

@app.api_route("/v1/chat/completions", methods=["POST"])
async def index(
    request: CreateChatCompletionRequest,
    validation: bool = Depends(validate_request),
    authorization: list = Depends(verify_api_key),
):
    if validation and authorization:
        model = route(request.messages[-1].content, mongo_client).strip()
        response = RouterChatCompletion(model=model, request=request)
        await insert_api_call_log(
            response_data=response,
            user_id=authorization[0],
            api_key_id=authorization[1],
            db_pg=pool,
        )
        return response


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
            "title": "HTTP Error",
            "status": exc.status_code,
            "detail": "An error occurred. Please check your request and try again.",
        },
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handles general exceptions.
    Returns a standardized JSON response for unhandled exceptions.
    """
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "Error",
            "title": "Internal Server Error",
            "status": HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Please retry the request. If the error persists, check server logs for more detailed information or contact support: prateek@llmhub.dev",
        },
        headers={"Content-Type": "application/problem+json"},
    )


#@app.middleware("http")
#async def add_security_headers(request: Request, call_next):
#    response = await call_next(request)
#    response.headers["X-Content-Type-Options"] = "nosniff"
#    response.headers["X-Frame-Options"] = "DENY"
#    response.headers["Content-Security-Policy"] = "default-src 'self'"
#    return response