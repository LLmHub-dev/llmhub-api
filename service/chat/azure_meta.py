import os
from openai import OpenAI
import json

AZURE_META_API_KEY = os.getenv("AZURE_META_API_KEY")
AZURE_META_ENDPOINT = os.getenv("AZURE_META_ENDPOINT")


def Azure_Meta_Chat_Completions(request):

    client = OpenAI(
        base_url=AZURE_META_ENDPOINT,
        api_key=AZURE_META_API_KEY,
    )

    response = client.chat.completions.create(
        model="Meta-Llama-3.1-8B-Instruc",
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
