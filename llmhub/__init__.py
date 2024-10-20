import os


from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse


from starlette.status import HTTP_403_FORBIDDEN


from llmhub.router import route


from motor.motor_asyncio import AsyncIOMotorClient


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
            detail="Invalid API Key",
        )


app = FastAPI(dependencies=[Depends(verify_api_key)])


@app.api_route("/v1/chat/completions", methods=["GET", "POST"])
async def index(
    request: CreateChatCompletionRequest, db: MongoClient = Depends(get_mongo_client)
):
    content = request.messages[-1].content
    model = route(content, db)
    model = model.strip()
    response=RouterChatCompletion(model=model,request=request)
    return response

@app.get("/v1/hello/{name}")
async def get_name(name: str):
    return {"name": name}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )
