import os
import logging


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection


from typing import Optional, Dict
from prisma import Prisma


from pydantic_types.chat import ChatCompletion

logging.basicConfig(level=logging.INFO)


def get_mongo_client() -> MongoClient:
    """
    Fetch MongoDB client from environment variable.
    :return: MongoClient instance.
    :raises ValueError: If MongoDB URI is not found in environment variables.
    """
    uri = os.getenv("MONGO_URI")
    if not uri:
        logging.error("MONGO_URI not found in environment variables.")
        raise ValueError("MONGO_URI not set in environment variables.")

    try:
        client = MongoClient(uri, server_api=ServerApi("1"))
        return client
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")


def get_custom_config(
    client: MongoClient,
    db_name: str = "Routers",
    collection_name: str = "route-config",
    mode: str = "automatic",
) -> Dict:
    """
    Fetch the route configuration from MongoDB.
    :param client: MongoDB client instance.
    :param db_name: Database name.
    :param collection_name: Collection name.
    :param mode: Mode of routing configuration.
    :return: Configuration dictionary.
    :raises LookupError: If configuration is not found for the given mode.
    """
    try:
        collection: Collection = client[db_name][collection_name]
        result = collection.find_one({"mode": mode})

        if result:
            return result.get("config", {})
        else:
            raise Exception(f"No route configuration found for mode: {mode}")
    except Exception as e:
        logging.error(f"Error retrieving route configuration: {e}")
        raise LookupError(f"Error retrieving route configuration: {e}")


def get_routing_info(
    model: str = "automatic",
) -> Optional[str]:
    """
    Fetch the routing system prompt from MongoDB.
    :param client: MongoDB client instance.
    :param db_name: Database name.
    :param collection_name: Collection name.
    :param mode: Mode of routing configuration.
    :return: Routing system prompt or default prompt for 'automatic' mode.
    :raises LookupError: If system prompt is not found for the given mode.
    """

    if model == "automatic":
        return """ You are a routing agent responsible for selecting the appropriate model based on the instruction type. Follow these guidelines:
        - If the instruction is related to **coding**, output 'claude-3.5-sonnet'.
        - If the instruction involves **logical reasoning or complexity**, output 'gpt-4o-mini'.
        - If the instruction contains **very long context texts**, output 'gemini-1.5-flash'.
        - If the instruction is for **summarization**, output 'mistral-nemo'.
        - For **general-purpose or friendly conversation**, output 'meta-llama'.
        Your response must strictly be one of the following with no extra characters or information:
        - 'claude-3.5-sonnet'
        - 'gpt-4o-mini'
        - 'gemini-1.5-flash'
        - 'mistral-nemo'
        - 'meta-llama'
        Now, this is the instruction:"""


def write_custom_route_config(
    client: MongoClient,
    system_prompt: str,
    db_name: str = "Routers",
    collection_name: str = "route-config",
    mode: str = "automatic",
) -> None:
    """
    Write the system prompt to MongoDB.
    :param client: MongoDB client instance.
    :param system_prompt: System prompt to store.
    :param db_name: Database name.
    :param collection_name: Collection name.
    :param mode: Mode of routing configuration.
    :raises ValueError: If system_prompt is None.
    :raises RuntimeError: If the write operation to MongoDB fails.
    """
    try:
        if system_prompt is None:
            logging.error("Route Info cannot be None.")
            raise ValueError("Route Info cannot be None.")
        collection: Collection = client[db_name][collection_name]
        query_filter = {"mode": mode}
        update_operation = {"$set": {"system_prompt": system_prompt}}
        result = collection.update_one(query_filter, update_operation)
        return

    except Exception as e:
        logging.error(f"Error writing Route Info to database: {e}")
        raise RuntimeError(f"Error writing Route Info to database: {e}")

async def insert_api_call_log(
    response_data:ChatCompletion,
    user_id: str,
    api_key_id: str,
    db: Prisma
):
    """
    Inserts an API call log into the database.

    Parameters:
        response_data (dict): The response data from the API (contains tokens, model, etc.).
        user_id (str): The ID of the user making the API call.
        api_key_id (str): The ID of the API key being used.
        db (Prisma): The Prisma database client.

    Returns:
        dict: The inserted log data or None if an error occurred.
    """
    # Prepare the data to insert
    log_data = {
        'userId': user_id,
        'apiKeyId': api_key_id,
        'model_name': response_data.model,
        'prompt_tokens': response_data.usage.prompt_tokens,
        'completion_tokens': response_data.usage.completion_tokens,
        'total_tokens': response_data.usage.total_tokens,
        'credits_used': response_data.usage.total_tokens,  # To be calculated later
    }

    try:
        api_call_log = await db.apicalllog.create(data=log_data)
        logging.info(f"Inserted log with ID: {api_call_log.id}")

        return api_call_log
    except Exception as e:
        # Log any errors that occur during the insertion process
        logging.error(f"Error inserting log: {str(e)}")
        return None  # Return None to indicate failure