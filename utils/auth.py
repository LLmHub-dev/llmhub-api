import jwt
import os

# Load environment variables

SECRET_KEY = "af04c343a52c6eaf13e3b7701090db2aeb3eb2e0dce55cc6d53442e8f0645c92"
ALGORITHM = "HS256"


def create_access_token(data: dict):
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("user")
        if username is None:
            return None
        return True
    except jwt.PyJWTError:
        return None
