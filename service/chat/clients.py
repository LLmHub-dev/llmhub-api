from openai import OpenAI, AzureOpenAI
import threading
from decimal import Decimal


# Thread-safe singleton pattern for clients
class ClientPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ClientPool, cls).__new__(cls)
                cls._instance._initialize_clients(config)
            return cls._instance

    def _initialize_clients(self, config):
        """Initialize all API clients once at startup"""

        azure_openai_client = AzureOpenAI(
            azure_endpoint=config["AZURE_OPENAI_ENDPOINT"],
            api_key=config["AZURE_OPENAI_API_KEY"],
            api_version=config["AZURE_OPENAI_api_version"],
        )
        azure_meta_client = OpenAI(
            base_url=config["AZURE_META_ENDPOINT"],
            api_key=config["AZURE_META_API_KEY"],
        )

        self.clients = {
            config["AZURE_OPENAI_MODEL"]: {
                "client": azure_openai_client,
                "price_per_million_input": Decimal(
                    str(config["AZURE_OPENAI_PRICE_PER_MILLION_INPUT"])
                ),
                "price_per_million_output": Decimal(
                    str(config["AZURE_OPENAI_PRICE_PER_MILLION_OUTPUT"])
                ),
                "model": config["AZURE_OPENAI_MODEL"],
            },
            config["AZURE_META_MODEL"]: {
                "client": azure_meta_client,
                "price_per_million_input": Decimal(
                    str(config["AZURE_META_PRICE_PER_MILLION_INPUT"])
                ),
                "price_per_million_output": Decimal(
                    str(config["AZURE_META_PRICE_PER_MILLION_OUTPUT"])
                ),
                "model": config["AZURE_META_MODEL"],
            },
            "router": {
                "client": azure_meta_client,
                "price_per_million_input": Decimal(
                    str(config["AZURE_META_PRICE_PER_MILLION_INPUT"])
                ),
                "price_per_million_output": Decimal(
                    str(config["AZURE_META_PRICE_PER_MILLION_OUTPUT"])
                ),
                "model": config["AZURE_META_MODEL"],
            },
            # Add more clients/models here as needed
        }

    def get_client_info(self, model_name: str = None):
        """
        Get the configured client and pricing data for the given model name.

        Args:
            model_name (str): The model name ('azure_openai_model_name', 'azure_meta_model_name', etc.)

        Returns:
            dict: A dictionary with the "client" and the "price_per_million_input"/"price_per_million_output"

        Raises:
            ValueError: If the model_name is not recognized
        """
        if model_name not in self.clients:
            return self.clients["router"]
        return self.clients[model_name]
