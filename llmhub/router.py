import os
import json
import logging
from google.generativeai import GenerativeModel, configure as genai_configure
from utils.database import (
    load_mongo_uri,
    initialize_mongo_client,
    get_mode_config,
    get_sys_prompt_config,
    write_sys_prompt_config,
)
from utils.prompt_format import create_dynamic_prompt


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_api_key(api_key_path="api_key.txt"):
    """
    Load the API key from a file or environment variable.
    """

    try:
        if os.getenv("GENAI_API_KEY"):
            return os.getenv("GENAI_API_KEY")

        with open(api_key_path, "r") as file:
            return file.readline().strip()

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


def fetch_model_and_intent(mongo_client):
    """
    Fetch model names and intents from MongoDB route configuration.
    """

    try:
        results = get_mode_config(mongo_client)
        models = results.values()
        intent = results.keys()
        return models, intent

    except Exception as e:
        logging.error(f"Error fetching route configuration from MongoDB: {e}")
        raise


def generate_prompt(models, intent):
    """
    Generate a dynamic prompt using the provided models and intents.
    """

    try:
        updated_prompt_data = create_dynamic_prompt(intent, models)
        logging.info("Dynamic prompt generated successfully.")
        return updated_prompt_data

    except Exception as e:
        logging.error(f"Error generating dynamic prompt: {e}")
        raise


def call_genai_model(prompt, user_input):
    """
    Call the Generative AI model with the system prompt and user input.
    """

    try:
        model = GenerativeModel("gemini-1.5-flash", system_instruction=prompt)
        response = model.generate_content(user_input)
        logging.info("Model response received successfully.")
        return response.text

    except Exception as e:
        logging.error(f"Error generating content with GenAI model: {e}")
        raise


def route(msg, mongo_client):
    """
    Main function to initialize MongoDB, fetch route config, generate prompt, and call the GenAI model.
    """
    # Load MongoDB URI and initialize client

    system_prompt = get_sys_prompt_config(mongo_client)

    if system_prompt == {}:

        models, intent = fetch_model_and_intent(mongo_client)
        logging.info(f"Models and intents fetched: {models}, {intent}")
        system_prompt = generate_prompt(models, intent)
        logging.info(f"Generated system prompt: {system_prompt}")
        write_sys_prompt_config(mongo_client, system_prompt)

    else:
        logging.info(f"Skipped route config:")
    api_key = load_api_key()
    configure_genai(api_key)
    # Call the GenAI model with the prompt
    user_input = msg
    response_text = call_genai_model(system_prompt, user_input)
    return response_text
