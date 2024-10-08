import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN
from FastAPI_Dir.router import route
from utils.database import get_mongo_client


API_KEY = os.getenv("API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# Set up structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )

async def get_db_client():
    return get_mongo_client(MONGO_URI)

@app.get("/v1/chat")
async def index(message: str, db_client=Depends(get_db_client)):
    model = route(message, db_client)
    return {"model": model}

@app.get("/v1/hello/{name}")
async def get_name(name: str):
    return {"name": name}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )