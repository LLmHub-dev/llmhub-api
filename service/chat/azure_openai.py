import os
from openai import AzureOpenAI
import json

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")


def Azure_OpenAI_Chat_Completions(request):

    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-09-01-preview",
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=request.messages,
        temperature=request.temperature,
        top_p=request.top_p,
        n=request.n,
        stream="False",
        frequency_penalty=request.frequency_penalty,
        top_logprobs=request.top_logprobs,
        logprobs=request.logprobs,
        max_completion_tokens=request.max_completion_tokens,
        presence_penalty=request.presence_penalty,
        stop=request.stop,
        user=request.user,
        tools=request.tools,
        tool_choice=request.tool_choice,
    )

    return response
