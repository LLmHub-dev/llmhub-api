from service.chat.clients import ClientPool


def Azure_Meta_Chat_Completions(request, client_pool: ClientPool):
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
    # Get client from the pool instead of creating a new one
    client = client_pool.azure_meta_client

    # Prepare the parameters
    params = {
        "model": client_pool.azure_meta_model,
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

    # Remove None values for better performance
    params = {k: v for k, v in params.items() if v is not None}

    # API call to generate the response
    response = client.chat.completions.create(**params)

    return response
