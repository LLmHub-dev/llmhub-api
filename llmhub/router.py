import os
import json
import logging
from google.generativeai import GenerativeModel, configure as genai_configure
from utils.database import (
    get_custom_config,
    get_routing_info,
    write_custom_route_config,
)
from utils.prompt_format import create_custom_route_config
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_api_key():
    """
    Load the API key from a file or environment variable.
    """

    try:
        if os.getenv("GEMINI_API_KEY"):
            return os.getenv("GEMINI_API_KEY")

    except Exception as e:
        logging.error(f"Error loading API key: {e}")
        raise


def configure_genai(api_key):
    """
    Configure the GenAI API with the provided API key.
    """

    try:
        genai_configure(api_key=api_key)
        logging.info("GenAI API configured successfully.")

    except Exception as e:
        logging.error(f"Failed to configure GenAI API: {e}")
        raise


def call_genai_model(user_input):
    """
    Call the Generative AI model with the system prompt and user input.
    """

    try:
        model = GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_input)
        logging.info("Model response received successfully.")
        return response.text

    except Exception as e:
        logging.error(f"Error generating content with GenAI model: {e}")
        raise


def route(msg, mongo_client, model="automatic"):
    """
    Main function to initialize MongoDB, fetch route config, generate prompt, and call the GenAI model.
    """
    # Load MongoDB URI and initialize client
    route_info = get_routing_info(mongo_client)
    if not route_info:
        route_info = create_custom_route_config(mongo_client)
    api_key = load_api_key()
    configure_genai(api_key)
    response_text = call_genai_model(route_info + " " + msg)
    return response_text
