import google.generativeai as genai
import os
import time
from pydantic_types.chat import (
    ChatCompletion,
    ChatCompletionChoice,
    Usage,
)


def Gemini_Chat_Completions(request):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    chat_history = [{"role": msg.role, "parts": msg.content} for msg in request.messages]

    chat = model.start_chat(
        history=chat_history,
    )
    response = chat.send_message(request.messages[-1].content)
    current_unix_timestamp = int(time.time())
    return ChatCompletion(
        id="llmhub-gemini-1.5-flash",
        object="chat.completion",
        created=current_unix_timestamp,
        model="gemini-1.5-flash",
        choices=[
            ChatCompletionChoice(
                index=0,
                message={"role": "assistant", "content": response.text},
                finish_reason="stop",
            )
        ],
        usage=Usage(
            prompt_tokens=response.usage_metadata.prompt_token_count,
            completion_tokens=response.usage_metadata.candidates_token_count,
            total_tokens=response.usage_metadata.total_token_count,
        ),
        system_fingerprint="llmhub-v1-gemini",
    )
