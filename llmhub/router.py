import os
import logging
from typing import Optional
from openai import OpenAI
from openai.types.chat import ChatCompletion
from utils.database import get_routing_info

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def route_message(msg: str) -> Optional[str]:
    """
    Route a message to the LLM model and return the response.

    Args:
        msg: The input message to send to the model

    Returns:
        The text response from the model or None if an error occurred
    """
    try:
        api_key = os.getenv("AZURE_META_API_KEY")
        base_url = os.getenv("AZURE_META_ENDPOINT")

        if not api_key or not base_url:
            logger.error("API key or endpoint is missing")
            return None

        logger.info("Initializing OpenAI client")
        client = OpenAI(api_key=api_key, base_url=base_url)

        logger.debug(f"Sending message to model: {msg[:50]}...")
        response: ChatCompletion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": msg},
            ],
            stream=False,
        )

        logger.info("Message processed successfully")
        return response.choices[0].message.content
    except Exception as e:
        logger.exception(f"Error routing message: {str(e)}")
        return None


def route(msg: str, model: str = "automatic") -> Optional[str]:
    """
    Route a message with intelligent model selection.

    Args:
        msg: The user message to be processed
        model: The model to use, defaults to "automatic" for intelligent routing

    Returns:
        The generated response text or None if an error occurred
    """
    try:
        logger.info(f"Routing message with model preference: {model}")

        route_info = get_routing_info(model=model)
        if not route_info:
            logger.warning(f"Could not retrieve routing info for model: {model}")
            return None

        logger.debug("Retrieved routing information successfully")

        # Combine routing information with user message
        full_message = f"{route_info} {msg}"

        response_text = route_message(full_message)

        if response_text:
            logger.info("Successfully routed and received response")
            return response_text
        else:
            logger.error("Failed to get response from route_message")
            return None
    except Exception as e:
        logger.exception(f"Error in route function: {str(e)}")
        return None
