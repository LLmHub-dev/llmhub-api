import os
from openai import OpenAI
import json

AZURE_MISTRAL_API_KEY = os.getenv("AZURE_MISTRAL_API_KEY")
AZURE_MISTRAL_ENDPOINT = os.getenv("AZURE_MISTRAL_ENDPOINT")


def Azure_Mistral_Chat_Completions(request):
    """Generate chat completions using the Azure Mistral model.

    Args:
        request: An object containing the parameters required for the chat completion.

    Returns:
        response: The response from the Azure OpenAI chat completion API.
    """
    client = OpenAI(
        base_url=AZURE_MISTRAL_ENDPOINT,
        api_key=AZURE_MISTRAL_API_KEY,
    )

    params = {
            "model": "mistral-nemo",
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_completion_tokens,
            "stop": request.stop,
            "user": request.user,
            "tools": request.tools,
            "tool_choice": request.tool_choice,
            "stream": False,  # Set to False by default
        }

        # Remove keys with None values (optional parameters)
    params = {k: v for k, v in params.items() if v is not None}

        # API call to generate the response
    response = client.chat.completions.create(**params)


    return response
