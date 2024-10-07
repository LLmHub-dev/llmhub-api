import azure.functions as func
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN
import fastapi
from FastAPI_Dir.router import route

API_KEY = "llmhub.dev"  # Replace with your actual API key
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )


app = fastapi.FastAPI(dependencies=[Depends(verify_api_key)])


@app.get("/v1/chat")
async def index(message: str):
    model=route(message)

    return {
        "model": model,
    }


@app.get("/v1/hello/{name}")
async def get_name(name: str):
    return {
        "name": name,
    }
