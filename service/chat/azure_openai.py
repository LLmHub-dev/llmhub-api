from service.chat.clients import ClientPool


def Azure_OpenAI_Chat_Completions(request, client_pool: ClientPool, model):
    """Generate chat completions using the Azure OpenAI model.

    Args:
        request: An object containing the parameters required for the chat completion.

    Returns:
        response: The response from the Azure OpenAI chat completion API.
    """
    # Get client from the pool instead of creating a new one
    client_info = client_pool.get_client_info(model_name=model)
    client = client_info["client"]

    response = client.chat.completions.create(
        model=client_info["model"],
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
