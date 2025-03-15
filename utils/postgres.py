import asyncpg
import uuid
from datetime import datetime
from decimal import Decimal
import logging
from pydantic_types.chat import ChatCompletion
from service.chat.clients import ClientPool


async def insert_api_call_log(
    model: str,
    client_pool: ClientPool,
    response_data: ChatCompletion,
    user_id: str,
    api_key_id: str,
    db_pg: asyncpg.Connection,  # Use asyncpg connection instead of AsyncSession
):
    """
    Inserts an API call log into the database.

    Parameters:
        response_data (ChatCompletion): The response data from the API (contains tokens, model, etc.).
        user_id (str): The ID of the user making the API call.
        api_key_id (str): The ID of the API key being used.
        db_pg (asyncpg.Connection): The asyncpg connection object.

    Returns:
        dict: The inserted log data or None if an error occurred.
    """
    client_info = client_pool.get_client_info(model)

    # The actual client
    # Pricing
    price_input = client_info["price_per_million_input"]
    price_output = client_info["price_per_million_output"]

    cost_for_input_tokens = response_data.usage.prompt_tokens * (
        price_input / 1_000_000
    )
    cost_for_output_tokens = response_data.usage.completion_tokens * (
        price_output / 1_000_000
    )
    total_credits_used = cost_for_input_tokens + cost_for_output_tokens

    log_data = {
        "id": str(uuid.uuid4()),
        "userId": user_id,
        "apiKeyId": api_key_id,
        "model_name": response_data.model,
        "prompt_tokens": response_data.usage.prompt_tokens,
        "completion_tokens": response_data.usage.completion_tokens,
        "total_tokens": response_data.usage.total_tokens,
        "credits_used": Decimal(total_credits_used).quantize(
            Decimal("0.000001")
        ),  # Ensure proper decimal conversion
        "timestamp": datetime.utcnow(),  # Default timestamp
    }

    try:
        # Insert the log into the database using asyncpg
        insert_query = """
        INSERT INTO api_call_logs (
            id,"userId", "apiKeyId", model_name, 
            prompt_tokens, completion_tokens, 
            total_tokens, credits_used, timestamp
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9
        ) RETURNING *;
        """

        # Execute the query and fetch the result
        result = await db_pg.fetchrow(
            insert_query,
            log_data["id"],
            log_data["userId"],
            log_data["apiKeyId"],
            log_data["model_name"],
            log_data["prompt_tokens"],
            log_data["completion_tokens"],
            log_data["total_tokens"],
            log_data["credits_used"],
            log_data["timestamp"],
        )

        if result:
            logging.info(f"Inserted log with ID: {result['userId']}")
            return dict(result)  # Convert to dictionary
        else:
            logging.error("No log inserted.")
            return None

    except Exception as e:
        # Log any errors that occur during the insertion process
        logging.error(f"Error inserting log: {str(e)}")
        return None
