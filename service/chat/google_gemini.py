import google.generativeai as genai
import os
import time
from pydantic_types.chat import (
    ChatCompletion,
    ChatCompletionChoice,
    Usage,
)

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]


def Google_Gemini_Chat_Completions(request):
    """Generate chat completions using the Google Gemini model.

    Args:
        request: An object containing the parameters required for the chat completion.

    Returns:
        response: The response from the Gemini chat completion API.
    """
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    chat_history = [
        {"role": "model" if msg.role == "assistant" else "user", "parts": msg.content}
        for msg in request.messages
    ]
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
