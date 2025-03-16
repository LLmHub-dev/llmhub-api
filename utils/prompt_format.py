from typing import Optional


def get_routing_info(
    config:dict,
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
        return f""" You are a routing agent responsible for selecting the appropriate model based on the instruction type. Follow these guidelines:
        - If the instruction is related to **coding**, output {config["ROUTER_CODING_MODEL"]}.
        - If the instruction involves **advanced logical reasoning or complexity**, output {config["ROUTER_LOGICAL_MODEL"]}.
        - For **general-purpose or friendly conversation**, output {config["ROUTER_CONVERSATION_MODEL"]}.
        Your response must strictly be one of the following with no extra characters or information:
        - {config["ROUTER_CODING_MODEL"]}
        - {config["ROUTER_LOGICAL_MODEL"]}
        - {config["ROUTER_CONVERSATION_MODEL"]}
        Now, this is the instruction:"""
    else:
        return None
