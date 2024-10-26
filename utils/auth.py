import jwt
import os
from typing import Optional, Dict, Any
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def create_access_token(data: dict) -> str:
    """
    Create a new JWT access token.

    :param data: A dictionary containing the payload data to encode.
    :return: A JWT token as a string.
    """
    try:
        encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise RuntimeError(f"Failed to create access token: {str(e)}")


def verify_token(token: str):
    """
    Verify a given JWT token.

    :param token: The JWT token to verify.
    :return: The decoded payload if the token is valid, otherwise None.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("user")
        if username is None:
            return False
        return True
    except jwt.PyJWTError:
        return False
