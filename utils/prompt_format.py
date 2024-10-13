import logging
from utils.database import get_mode_config, write_sys_prompt_config

def create_dynamic_prompt(dict_keys, dict_values):

    if len(dict_keys) != len(dict_values):
        raise ValueError("dict_keys and dict_values must have the same length.")
    if not dict_keys or not dict_values:
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


def create_route_tag(mongo_client):

    models, intent = fetch_model_and_intent(mongo_client)
    logging.info(f"Models and intents fetched: {models}, {intent}")
    system_prompt = generate_prompt(models, intent)
    logging.info(f"Generated route tag")
    write_sys_prompt_config(mongo_client, system_prompt)
    return system_prompt
