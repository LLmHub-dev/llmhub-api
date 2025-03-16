import os
from dotenv import load_dotenv
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """
    Load environment variables from .env file and return them as a dictionary.

    Returns:
        Dict[str, Any]: Dictionary containing all environment variables
    """
    load_dotenv()
    config = {
        # AZURE OPENAI API
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", ""),
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        "AZURE_OPENAI_MODEL": os.getenv("AZURE_OPENAI_MODEL", ""),
        "AZURE_OPENAI_api_version": os.getenv("AZURE_OPENAI_api_version", ""),
        "AZURE_OPENAI_PRICE_PER_MILLION_INPUT": os.getenv(
            "AZURE_OPENAI_PRICE_PER_MILLION_INPUT"
        ),
        "AZURE_OPENAI_PRICE_PER_MILLION_OUTPUT": os.getenv(
            "AZURE_OPENAI_PRICE_PER_MILLION_OUTPUT"
        ),
        # AZURE META API
        "AZURE_META_API_KEY": os.getenv("AZURE_META_API_KEY", ""),
        "AZURE_META_ENDPOINT": os.getenv("AZURE_META_ENDPOINT", ""),
        "AZURE_META_MODEL": os.getenv("AZURE_META_MODEL", ""),
        "AZURE_META_PRICE_PER_MILLION_INPUT": os.getenv(
            "AZURE_META_PRICE_PER_MILLION_INPUT"
        ),
        "AZURE_META_PRICE_PER_MILLION_OUTPUT": os.getenv(
            "AZURE_META_PRICE_PER_MILLION_OUTPUT"
        ),
        # ROUTER PRICING
        "ROUTER_PRICE_PER_MILLION_INPUT": os.getenv("ROUTER_PRICE_PER_MILLION_INPUT"),
        "ROUTER_PRICE_PER_MILLION_OUTPUT": os.getenv("ROUTER_PRICE_PER_MILLION_OUTPUT"),
        # ROUTER MODEL
        "ROUTER_CODING_MODEL": os.getenv("ROUTER_CODING_MODEL", ""),
        "ROUTER_LOGICAL_MODEL": os.getenv("ROUTER_LOGICAL_MODEL", ""),
        "ROUTER_CONVERSATION_MODEL": os.getenv("ROUTER_CONVERSATION_MODEL", ""),
        # CONFIGURATION
        "SECRET_KEY": os.getenv("SECRET_KEY", ""),
        "ALGORITHM": os.getenv("ALGORITHM", ""),
        "DATABASE_URL": os.getenv("DATABASE_URL", ""),
    }

    for key, value in config.items():
        if not value and key != "ALGORITHM":
            logger.warning(f"Environment variable '{key}' is not set or empty")

    return config
