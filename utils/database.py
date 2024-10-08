import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse


def get_mongo_client(uri):
    uri = load_mongo_uri()
    mongo_client = initialize_mongo_client(uri)
    return mongo_client

def load_mongo_uri(file_path='mongo_uri.txt'):
    """Load MongoDB URI from a file."""
    try:
        if os.getenv('MONGO_URI'):
            return os.getenv('MONGO_URI')
        with open(file_path, 'r') as file:
            uri = file.readline().strip()
        return uri
    except FileNotFoundError:
        raise Exception(f"File {file_path} not found. Please ensure the file path is correct.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")

def initialize_mongo_client(uri):
    """Initialize and return MongoDB client."""
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        return client
    except Exception as e:
        raise Exception(f"Failed to connect to MongoDB: {e}")

def get_mode_config(client, db_name="Routers", collection_name="route-config", mode="automatic"):
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


def get_sys_prompt_config(client, db_name="Routers", collection_name="route-config", mode="automatic"):
    """Fetch the route configuration from MongoDB."""
    try:
        database = client[db_name]
        collection = database[collection_name]
        result = collection.find_one({"mode": mode})

        if result:
            return result.get("system_prompt", {})
        else:
            raise Exception(f"No route configuration found for mode: {mode}")
    except Exception as e:
        raise Exception(f"Error retrieving route configuration: {e}")

def write_sys_prompt_config(client, system_prompt, db_name="Routers", collection_name="route-config", mode="automatic"):
    """Write the system prompt to MongoDB."""
    try:
        database = client[db_name]
        collection = database[collection_name]
        query_filter = {"mode" : mode}
        update_operation = { '$set' :
            { "system_prompt" : system_prompt }
        }
        result = collection.update_one(query_filter, update_operation)

        return

    except Exception as e:
        raise Exception(f"Error writing system prompt to database: {e}")