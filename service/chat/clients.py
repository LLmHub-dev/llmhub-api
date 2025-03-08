import os
from openai import OpenAI, AzureOpenAI
import threading


# Thread-safe singleton pattern for clients
class ClientPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ClientPool, cls).__new__(cls)
                cls._instance._initialize_clients()
            return cls._instance

    def _initialize_clients(self):
        """Initialize all API clients once at startup"""
        # Azure OpenAI client
        self.azure_openai_client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_api_version"),
        )
        self.azure_openai_model = os.getenv("AZURE_OPENAI_MODEL")

        # Azure Meta client
        self.azure_meta_client = OpenAI(
            base_url=os.getenv("AZURE_META_ENDPOINT"),
            api_key=os.getenv("AZURE_META_API_KEY"),
        )
        self.azure_meta_model = os.getenv("AZURE_META_MODEL")

        # Azure Mistral client
        self.azure_mistral_client = OpenAI(
            base_url=os.getenv("AZURE_MISTRAL_ENDPOINT"),
            api_key=os.getenv("AZURE_MISTRAL_API_KEY"),
        )

        # Google Gemini client (add your initialization here)
        # self.google_gemini_client = ...


# Create a global instance for importing
client_pool = ClientPool()
