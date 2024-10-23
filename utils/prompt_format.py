import logging
from typing import List, Tuple
from utils.database import get_custom_config, write_custom_route_config


def create_route_config_prmpt(dict_keys: List[str], dict_values: List[str]) -> str:
    """
    Creates a dynamic routing system prompt based on provided keys and values.

    :param dict_keys: List of instruction categories.
    :param dict_values: List of model names corresponding to the instruction categories.
    :return: A formatted system prompt string.
    :raises ValueError: If dict_keys and dict_values lengths do not match or if they are empty.
    """

    if len(dict_keys) != len(dict_values):
        logging.error("Mismatched lengths: dict_keys and dict_values must have the same length.")
        raise ValueError("dict_keys and dict_values must have the same length.")
    
    if not dict_keys or not dict_values:
        logging.error("Empty keys or values: dict_keys and dict_values cannot be empty.")
        raise ValueError("dict_keys and dict_values cannot be empty.")

    conditions = []
    for key, value in zip(dict_keys, dict_values):
        conditions.append(f"if the instruction is related to {key}, output '{value}'")
    condition_str = ". ".join(conditions)

    possible_outputs = []
    for value in dict_values:
        possible_outputs.append(f'"{value}"')
    output_str = ", ".join(possible_outputs)

    system_prompt = (
        f"You are a routing agent. Based on the provided instruction, {condition_str}. "
        f"Do not include any additional text or information in your response. "
        f"Your output must strictly be one of the following with no extra characters: {output_str}. Now this is the instruction: "
    )

    return system_prompt


def get_custom_model_n_intent(mongo_client) -> Tuple[List[str], List[str]]:
    """
    Fetch model names and intents from MongoDB route configuration.
    
    :param mongo_client: MongoDB client instance.
    :return: Tuple containing lists of models and intents.
    :raises RuntimeError: If the route configuration cannot be fetched.
    """
    try:
        results = get_custom_config(mongo_client)
        return list(results.values()), list(results.keys())

    except Exception as e:
        logging.error(f"Error fetching route configuration from MongoDB: {e}")
        raise RuntimeError(f"Error fetching route configuration: {e}")


def generate_custom_route_config(models: List[str], intents: List[str]) -> str:
    """
    Generate a dynamic prompt using the provided models and intents.
    
    :param models: List of model names.
    :param intents: List of corresponding intents.
    :return: Generated dynamic system prompt.
    :raises RuntimeError: If an error occurs during prompt generation.
    """

    try:
        updated_prompt_data = create_route_config_prmpt(intents, models)
        logging.info("Dynamic prompt generated successfully.")
        return updated_prompt_data

    except Exception as e:
        logging.error(f"Error generating dynamic prompt: {e}")
        raise RuntimeError(f"Error generating dynamic prompt: {e}")


def create_custom_route_config(mongo_client) -> str:
    """
    Create a route tag by fetching models and intents, generating the system prompt, 
    and writing it to the MongoDB configuration.
    
    :param mongo_client: MongoDB client instance.
    :return: Generated system prompt.
    :raises RuntimeError: If an error occurs during route tag creation.
    """
    try:
        models, intent = get_custom_model_n_intent(mongo_client)
        logging.info(f"Models and intents fetched: {models}, {intent}")
        route_config = generate_custom_route_config(models, intent)
        logging.info(f"Route tag created and stored successfully.")
        write_custom_route_config(mongo_client, route_config)
        return route_config

    except Exception as e:
        logging.error(f"Error creating route tag: {e}")
        raise RuntimeError(f"Error creating route tag: {e}")
