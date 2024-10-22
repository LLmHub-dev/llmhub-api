import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse


def get_mongo_client() -> MongoClient:
    uri = load_mongo_uri()  # Assuming this function loads the MongoDB URI
    mongo_client = initialize_mongo_client(
        uri
    )  # Assuming this initializes a MongoClient
    return mongo_client


def load_mongo_uri():
    try:
        if os.getenv("MONGO_URI"):
            return os.getenv("MONGO_URI")

    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")


def initialize_mongo_client(uri):
    """Initialize and return MongoDB client."""
    try:
        client = MongoClient(uri, server_api=ServerApi("1"))
        return client
    except Exception as e:
        raise Exception(f"Failed to connect to MongoDB: {e}")


def get_mode_config(
    client, db_name="Routers", collection_name="route-config", mode="automatic"
):
    """Fetch the route configuration from MongoDB."""
    try:
        database = client[db_name]
        collection = database[collection_name]
        result = collection.find_one({"mode": mode})

        if result:
            return result.get("config", {})
        else:
            raise Exception(f"No route configuration found for mode: {mode}")
    except Exception as e:
        raise Exception(f"Error retrieving route configuration: {e}")


def get_sys_prompt_config(
    client, db_name="Routers", collection_name="route-config", mode="automatic"
):
    """Fetch the route configuration from MongoDB."""

    if mode == "automatic":
        return "You are a routing agent. Based on the provided instruction, if the instruction is related to coding, output 'claude-3.5-sonnet'. if the instruction is related to general, output 'mistral-nemo'. if the instruction is related to reasoning, output 'gpt-4o-mini'. Do not include any additional text or information in your response. Your output must strictly be one of the following with no extra characters: 'claude-3.5-sonnet', 'mistral-nemo', 'gpt-4o-mini'. Now this is the instruction:"
    try:
        database = client[db_name]
        collection = database[collection_name]
        result = collection.find_one({"mode": mode})

        if result:
            return result.get("system_prompt")
        else:
            raise Exception(f"No route configuration found for mode: {mode}")
    except Exception as e:
        print(e)
        raise Exception(f"Error retrieving route configuration: {e}", e)


def write_sys_prompt_config(
    client,
    system_prompt,
    db_name="Routers",
    collection_name="route-config",
    mode="automatic",
):
    """Write the system prompt to MongoDB."""
    try:
        database = client[db_name]
        collection = database[collection_name]
        query_filter = {"mode": mode}
        update_operation = {"$set": {"system_prompt": system_prompt}}
        result = collection.update_one(query_filter, update_operation)

        return

    except Exception as e:
        raise Exception(f"Error writing system prompt to database: {e}")
