import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN
from llmhub.router import route
from fastapi.responses import JSONResponse
from utils.database import get_mongo_client
from utils.auth import verify_token
from pydantic_types.chat import CreateChatCompletionRequest, ChatCompletion, ChatCompletionChoice, Usage
API_KEY = os.getenv("API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
security = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    authorized = verify_token(credentials.credentials)
    if authorized != True:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )


app = FastAPI(dependencies=[Depends(verify_api_key)])


async def get_db_client():
    return get_mongo_client(MONGO_URI)


@app.get("/v1/chat/completions")
async def index(request: CreateChatCompletionRequest, db_client=Depends(get_db_client)):
    content=request.messages[-1].content

    model = route(content, db_client)
    model = model.strip()

    return ChatCompletion(
        id="llmhub.dev",
        object="chat.completion",
        created=1697723200,
        model=model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message={"role": "assistant", "content": model },
                finish_reason="stop"
            )
        ],
        usage=Usage(
            prompt_tokens=5,
            completion_tokens=10,
            total_tokens=15
        ),
        system_fingerprint="1234567"
    )


@app.get("/v1/hello/{name}")
async def get_name(name: str):
    return {"name": name}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )
