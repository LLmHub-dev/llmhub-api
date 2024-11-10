import os
from openai import OpenAI
import json

AZURE_META_API_KEY = os.getenv("AZURE_META_API_KEY")
AZURE_META_ENDPOINT = os.getenv("AZURE_META_ENDPOINT")


def Azure_Meta_Chat_Completions(request):
    """Generate chat completions using the Azure Meta model.

    Args:
        request: An object containing the parameters required for the chat completion.
            The expected attributes are:
            - messages: A list of message objects for the chat.
            - temperature: A float to control randomness (optional).
            - max_completion_tokens: Maximum number of tokens for the response (optional).
            - frequency_penalty: Controls repetition penalty (optional).
            - stop: Stop sequence(s) for the completion (optional).
            - user: The user identifier (optional).
            - tools: Tools to be used with the model (optional).
            - tool_choice: Specific tool choice for the model (optional).
    Returns:
        response: The response from the Azure OpenAI chat completion API or error message.
    """
    client = OpenAI(
            base_url=AZURE_META_ENDPOINT,
            api_key=AZURE_META_API_KEY,
        )

        # Prepare the parameters
    params = {
            "model": "Meta-Llama-3.1-8B",
            "messages": request.messages,
            "temperature": request.temperature,
            "frequency_penalty": request.frequency_penalty,
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
