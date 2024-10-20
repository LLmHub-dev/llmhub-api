from service.chat.azure_openai import Azure_OpenAI_Chat_Completions
from service.chat.gemini import Gemini_Chat_Completions
from pydantic_types.chat import (
    ChatCompletion,
    ChatCompletionChoice,
    Usage,
)


def RouterChatCompletion(model: str, request):
    if model == "gpt-4o-mini":
        return Azure_OpenAI_Chat_Completions(request)
    elif model == "gemini-1.5-flash":
        return Gemini_Chat_Completions(request)
    else:
        return ChatCompletion(
            id="llmhub.dev",
            object="chat.completion",
            created=1697723200,
            model=model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message={"role": "assistant", "content": model},
                    finish_reason="stop",
                )
            ],
            usage=Usage(prompt_tokens=5, completion_tokens=10, total_tokens=15),
            system_fingerprint="1234567",
        )
