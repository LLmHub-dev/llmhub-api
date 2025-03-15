from service.chat.clients import ClientPool


def Azure_Meta_Chat_Completions(request, client_pool: ClientPool, model):
    """
    Generate chat completions using the Azure Meta model.

    Args:
        request: An object containing the parameters required for the chat completion.
            - messages: A list of message objects for the chat.
            - temperature: A float to control randomness (optional).
            - max_completion_tokens: Maximum number of tokens for the response (optional).
            - frequency_penalty: Controls repetition penalty (optional).
            - stop: Stop sequence(s) for the completion (optional).
            - user: The user identifier (optional).
            - tools: Tools to be used with the model (optional).
            - tool_choice: Specific tool choice for the model (optional).
        client_pool: A pool that returns cached/configured clients.
        model: The name or key used to look up the client and model details.

    Returns:
        The response from the Azure OpenAI chat completion API.
    """
    client_info = client_pool.get_client_info(model_name=model)
    client = client_info["client"]

    # Prepare parameters in a single pass
    params = {
        "model": client_info["model"],
        "messages": request.messages,
        "temperature": request.temperature,
        "frequency_penalty": request.frequency_penalty,
        "max_tokens": request.max_completion_tokens,
        "stop": request.stop,
        "user": request.user,
        "tools": request.tools,
        "tool_choice": request.tool_choice,
        "stream": False,  # explicitly set streaming off
    }

    # Drop any keys whose values are None
    params = {k: v for k, v in params.items() if v is not None}

    # Make the API call
    return client.chat.completions.create(**params)
