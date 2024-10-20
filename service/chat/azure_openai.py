import os
from openai import AzureOpenAI
import json

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")


def Azure_Chat_Completions(request):

    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-09-01-preview",
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=request.messages
    )

    return response
