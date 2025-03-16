import logging
from typing import Optional
from openai.types.chat import ChatCompletion
from utils.prompt_format import get_routing_info
from service.chat.clients import ClientPool

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def route_message(msg: str, client_pool: ClientPool) -> Optional[str]:
    """
    Route a message to the LLM model and return the response.

    Args:
        msg: The input message to send to the model

    Returns:
        The text response from the model or None if an error occurred
    """
    try:
        logger.info("Getting Client")
        client = client_pool.get_client_info("router")["client"]

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


def route(config:dict, msg: str, client_pool: ClientPool, model: str = "automatic") -> Optional[str]:
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

        route_info = get_routing_info(config=config,model=model)
        if not route_info:
            logger.warning(f"Could not retrieve routing info for model: {model}")
            return None

        logger.debug("Retrieved routing information successfully")

        # Combine routing information with user message
        full_message = f"{route_info} {msg}"

        response_text = route_message(msg=full_message, client_pool=client_pool)

        if response_text:
            logger.info("Successfully routed and received response")
            return response_text
        else:
            logger.error("Failed to get response from route_message")
            return None
    except Exception as e:
        logger.exception(f"Error in route function: {str(e)}")
        return None
