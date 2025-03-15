import os
from openai import OpenAI, AzureOpenAI
import threading


# Thread-safe singleton pattern for clients
class ClientPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls,config):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ClientPool, cls).__new__(cls)
                cls._instance._initialize_clients(config)
            return cls._instance

    def _initialize_clients(self,config):
        """Initialize all API clients once at startup"""
        # Azure OpenAI client
        self.azure_openai_client = AzureOpenAI(
            azure_endpoint=config["AZURE_OPENAI_ENDPOINT"],
            api_key=config["AZURE_OPENAI_API_KEY"],
            api_version=config["AZURE_OPENAI_api_version"],
        )
        self.azure_openai_model = config["AZURE_OPENAI_MODEL"]

        # Azure Meta client
        self.azure_meta_client = OpenAI(
            base_url=config["AZURE_META_ENDPOINT"],
            api_key=config["AZURE_META_API_KEY"],
        )
        self.azure_meta_model = config["AZURE_META_MODEL"]

    def get_client(self, provider):
        """
        Get client and model by provider name

        Args:
            provider (str): The provider name ('azure_openai', 'azure_meta', etc.)

        Returns:
            tuple: (client, model_name) for the requested provider

        Raises:
            ValueError: If the provider is not supported
        """
        if provider == self.azure_openai_model:
            return self.azure_openai_client
        elif provider == self.azure_meta_model:
            return self.azure_meta_client
        # Uncomment when implementing Google Gemini
        # elif provider == "google_gemini":
        #     return self.google_gemini_client, os.getenv("GOOGLE_GEMINI_MODEL")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
