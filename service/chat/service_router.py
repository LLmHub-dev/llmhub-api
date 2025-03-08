from service.chat.azure_openai import Azure_OpenAI_Chat_Completions
from service.chat.azure_meta import Azure_Meta_Chat_Completions
from pydantic_types.chat import (
    ChatCompletion,
)


def RouterChatCompletion(model: str, request: dict) -> ChatCompletion:
    """
    Routes the request to the appropriate chat completion service based on the model.

    Args:
        model (str): The model to use for chat completion.
        request (dict): The request data for the model's completion service.

    Returns:
        ChatCompletion: The response from the chosen model's service.
    """
    if model == "gpt-4o-mini":
        return Azure_OpenAI_Chat_Completions(request)
    elif model == "meta-llama":
        return Azure_Meta_Chat_Completions(request)
    elif model == "claude-3.5-sonnet":
        return Azure_OpenAI_Chat_Completions(request)
    else:
        return Azure_OpenAI_Chat_Completions(request)
