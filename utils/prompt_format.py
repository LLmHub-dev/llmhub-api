from typing import Optional


def get_routing_info(
    model: str = "automatic",
) -> Optional[str]:
    """
    Fetch the routing system prompt from MongoDB.
    :param client: MongoDB client instance.
    :param db_name: Database name.
    :param collection_name: Collection name.
    :param mode: Mode of routing configuration.
    :return: Routing system prompt or default prompt for 'automatic' mode.
    :raises LookupError: If system prompt is not found for the given mode.
    """

    if model == "automatic":
        return """ You are a routing agent responsible for selecting the appropriate model based on the instruction type. Follow these guidelines:
        - If the instruction is related to **coding**, output 'claude-3.5-sonnet'.
        - If the instruction involves **logical reasoning or complexity**, output 'gpt-4o-mini'.
        - If the instruction contains **very long context texts**, output 'gemini-1.5-flash'.
        - If the instruction is for **summarization**, output 'mistral-nemo'.
        - For **general-purpose or friendly conversation**, output 'Llama-3.3-70B-Instruct'.
        Your response must strictly be one of the following with no extra characters or information:
        - 'claude-3.5-sonnet'
        - 'gpt-4o-mini'
        - 'gemini-1.5-flash'
        - 'mistral-nemo'
        - 'Llama-3.3-70B-Instruct'
        Now, this is the instruction:"""
    else:
        return None
