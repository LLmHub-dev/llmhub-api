import os
import json
import logging
import google.generativeai as genai
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


def configure_genai():
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        logging.info("API configured successfully.")

    except Exception as e:
        logging.error(f"Failed to configure GenAI API: {e}")
        raise


def infer_model_gemini(user_input):
    """
    Call the Generative AI model with the system prompt and user input.
    """

    try:
        configure_genai()
        model = genai.GenerativeModel("gemini-1.5-flash-8b")
        response = model.generate_content(user_input)
        logging.info("Model response received successfully.")
        return response.text

    except Exception as e:
        logging.error(f"Error generating content with GenAI model: {e}")
        raise


def route(msg, mongo_client, model="automatic"):
    route_info = get_routing_info(mongo_client)
    if not route_info:
        route_info = create_custom_route_config(mongo_client)
    response_text = infer_model_gemini(route_info + " " + msg)
    return response_text
