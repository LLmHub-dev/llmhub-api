import os
from openai import OpenAI
import json

AZURE_MISTRAL_API_KEY = os.getenv("AZURE_MISTRAL_API_KEY")
AZURE_MISTRAL_ENDPOINT = os.getenv("AZURE_MISTRAL_ENDPOINT")


def Azure_Mistral_Chat_Completions(request):

    client = OpenAI(
        base_url=AZURE_MISTRAL_ENDPOINT,
        api_key=AZURE_MISTRAL_API_KEY,
    )

    response = client.chat.completions.create(
        model="mistral-nemo",
        messages=request.messages,
        temperature=request.temperature,
        top_p=request.top_p,
        n=request.n,
        stream=False,
        logprobs=request.logprobs,
        max_tokens=request.max_completion_tokens,
        stop=request.stop,
        user=request.user,
        tools=request.tools,
        tool_choice=request.tool_choice,
    )

    return response
