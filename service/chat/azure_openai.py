import os
from openai import AzureOpenAI
import json

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")
AZURE_OPENAI_api_version = os.getenv("AZURE_OPENAI_api_version")


def Azure_OpenAI_Chat_Completions(request):
    """Generate chat completions using the Azure OpenAI model.

    Args:
        request: An object containing the parameters required for the chat completion.

    Returns:
        response: The response from the Azure OpenAI chat completion API.
    """
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_api_version,
    )

    response = client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
        messages=request.messages,
        temperature=request.temperature,
        top_p=request.top_p,
        n=request.n,
        stream=False,
        frequency_penalty=request.frequency_penalty,
        logprobs=request.logprobs,
        max_tokens=request.max_completion_tokens,
        presence_penalty=request.presence_penalty,
        stop=request.stop,
        user=request.user,
        tools=request.tools,
        tool_choice=request.tool_choice,
    )

    return response
