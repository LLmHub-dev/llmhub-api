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


@app.api_route("/v1/chat/completions", methods=["POST"])
async def index(
    request: CreateChatCompletionRequest, db: MongoClient = Depends(get_mongo_client)
):
    if request.messages[-1].role != "user":
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Ensure the final message in the messages array has the role 'user'.",
            headers={"Content-Type": "application/problem+json"},
        )
    content = request.messages[-1].content
    model = route(content, db)
    model = model.strip()
    response = RouterChatCompletion(model=model, request=request)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
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
