import jwt
import os
from typing import Optional, Dict, Any


from jwt.exceptions import InvalidTokenError, ExpiredSignatureError


from pydantic_types.chat import CreateChatCompletionRequest


from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse


from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
security = HTTPBearer()


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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": True})
        username: str = payload.get("userId")
        name: str = token
        if username is None:
            return None
        return [username, name]
    except jwt.PyJWTError:
        return None


def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    authorized = verify_token(credentials.credentials)
    if authorized is None:  # Corrected the comparison here
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API Key provided. Ensure that the correct key is being sent in the request header.",
            headers={"Content-Type": "application/problem+json"},
        )
    return authorized


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

    if request.tool_choice not in [None, "auto", "manual"]:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="tool_choice must be 'auto', 'manual', or omitted.",
            headers={"Content-Type": "application/problem+json"},
        )
    return True
