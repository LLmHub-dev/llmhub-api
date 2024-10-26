import os


from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse


from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


from llmhub.router import route


from service.chat.service_router import RouterChatCompletion


from utils.database import get_mongo_client
from utils.auth import verify_token


from pymongo import MongoClient


from pydantic_types.chat import (
    CreateChatCompletionRequest,
    ChatCompletion,
    ChatCompletionChoice,
    Usage,
)


from dotenv import load_dotenv


load_dotenv()
security = HTTPBearer()


def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    authorized = verify_token(credentials.credentials)
    if authorized != True:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API Key provided. Ensure that the correct key is being sent in the request header.",
            headers={"Content-Type": "application/problem+json"},
        )


app = FastAPI(dependencies=[Depends(verify_api_key)])

# Global variable to hold the MongoDB client
mongo_client: MongoClient = None


async def start_mongo_client():
    global mongo_client
    mongo_client = get_mongo_client()
    return mongo_client


@app.on_event("startup")
async def startup_event():
    global mongo_client
    mongo_client = await start_mongo_client()


@app.on_event("shutdown")
async def shutdown_event():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        mongo_client = None


@app.api_route("/v1/chat/completions", methods=["POST"])
async def index(
    request: CreateChatCompletionRequest,
):
    validated = validate_request(request)
    if validated:
        model = route(request.messages[-1].content, mongo_client).strip()
        response = RouterChatCompletion(model=model, request=request)
        return response


def validate_request(request: CreateChatCompletionRequest):
    """
    Validates the chat completion request.
    Raises an HTTP 400 exception if validation fails.
    """
    if request.messages[-1].role != "user":
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Ensure the final message in the messages array has the role 'user'.",
            headers={"Content-Type": "application/problem+json"},
        )

    if not (0 <= request.temperature <= 2):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Temperature must be between 0 and 2.",
            headers={"Content-Type": "application/problem+json"},
        )

    if not (0 <= request.top_p <= 1):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="top_p must be between 0 and 1.",
            headers={"Content-Type": "application/problem+json"},
        )

    if request.n < 1:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="n must be a positive integer.",
            headers={"Content-Type": "application/problem+json"},
        )

    if request.top_logprobs < 1:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="top_logprobs must be a positive integer.",
            headers={"Content-Type": "application/problem+json"},
        )

    if not (-2.0 <= request.presence_penalty <= 2.0):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="presence_penalty must be between -2.0 and 2.0.",
            headers={"Content-Type": "application/problem+json"},
        )

    if not (-2.0 <= request.frequency_penalty <= 2.0):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="frequency_penalty must be between -2.0 and 2.0.",
            headers={"Content-Type": "application/problem+json"},
        )

    if request.max_completion_tokens is not None and request.max_completion_tokens <= 0:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="max_completion_tokens must be a positive integer if specified.",
            headers={"Content-Type": "application/problem+json"},
        )

    if request.stop is not None:
        if len(request.stop) > 4:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="stop can include up to 4 sequences.",
                headers={"Content-Type": "application/problem+json"},
            )
        if any(len(seq) == 0 for seq in request.stop):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="stop sequences must not be empty.",
                headers={"Content-Type": "application/problem+json"},
            )

    if request.tool_choice not in [None, 'auto', 'manual']:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="tool_choice must be 'auto', 'manual', or omitted.",
            headers={"Content-Type": "application/problem+json"},
        )
    return True

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles HTTP exceptions.
    Returns a standardized JSON response for HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": "HTTP Error",
            "status": exc.status_code,
            "detail": exc.detail,
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
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Please retry the request. If the error persists, check server logs for more detailed information or contact support: prateek@llmhub.dev",
        },
        headers={"Content-Type": "application/problem+json"},
    )
