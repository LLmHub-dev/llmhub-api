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
    db_pg: asyncpg.Pool,  # db_pg is now an asyncpg pool
):
    """
    Inserts an API call log into the database and updates the user's credit balance by subtracting the credits used.

    Parameters:
        model (str): The name of the model used.
        client_pool (ClientPool): The pool of client configurations.
        response_data (ChatCompletion): The response data from the API call.
        user_id (str): The ID of the user making the API call.
        api_key_id (str): The ID of the API key used.
        db_pg (asyncpg.Pool): The asyncpg pool object.

    Returns:
        dict: A dictionary with the inserted log and the updated credit balance,
              or None if an error occurred.
    """
    client_info = client_pool.get_client_info(model)
    router_client_info = client_pool.get_client_info("router")

    # Pricing details
    price_input = client_info["price_per_million_input"]
    price_output = client_info["price_per_million_output"]
    router_price_input = router_client_info["price_per_million_input"]
    router_price_output = router_client_info["price_per_million_output"]

    cost_for_input_tokens = (
        response_data.usage.prompt_tokens * (price_input / 1_000_000)
    ) + router_price_input
    cost_for_output_tokens = (
        response_data.usage.completion_tokens * (price_output / 1_000_000)
    ) + router_price_output
    total_credits_used = cost_for_input_tokens + cost_for_output_tokens

    log_data = {
        "id": str(uuid.uuid4()),
        "userId": user_id,
        "apiKeyId": api_key_id,
        "model_name": response_data.model,
        "prompt_tokens": response_data.usage.prompt_tokens,
        "completion_tokens": response_data.usage.completion_tokens,
        "total_tokens": response_data.usage.total_tokens,
        "credits_used": Decimal(total_credits_used).quantize(Decimal("0.000001")),
        "timestamp": datetime.utcnow(),
    }

    try:
        # Acquire a connection from the pool and start a transaction
        async with db_pg.acquire() as conn:
            async with conn.transaction():
                # Insert the API call log into the database
                insert_query = """
                INSERT INTO api_call_logs (
                    id, "userId", "apiKeyId", model_name, 
                    prompt_tokens, completion_tokens, 
                    total_tokens, credits_used, timestamp
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9
                ) RETURNING *;
                """
                log_result = await conn.fetchrow(
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

                if log_result:
                    logging.info(f"Inserted log with ID: {log_result['id']}")

                    # Update the user's credit balance in the "users" table
                    update_query = """
                    UPDATE users
                    SET "creditBalance" = "creditBalance" - $1
                    WHERE id = $2
                    RETURNING "creditBalance";
                    """
                    update_result = await conn.fetchrow(
                        update_query, log_result["credits_used"], user_id
                    )
                    if update_result:
                        logging.info(
                            f"User {user_id} credit balance updated to {update_result['creditBalance']}"
                        )
                        return {
                            "api_call_log": dict(log_result),
                            "updated_credit_balance": update_result["creditBalance"],
                        }
                    else:
                        logging.error(f"User not found with id: {user_id}")
                        return dict(log_result)
                else:
                    logging.error("No log inserted.")
                    return None

    except Exception as e:
        logging.error(f"Error in inserting log and updating credit balance: {str(e)}")
        return None

async def check_user_balance(
    db_pg: asyncpg.Pool,
    user_id: str,
):
    """
    Checks the user's credit balance in the "users" table.
    If the balance is less than $0.50, raises a ValueError.

    Parameters:
        db_pg (asyncpg.Pool): The asyncpg pool object.
        user_id (str): The ID of the user.

    Raises:
        ValueError: If the user is not found or the credit balance is insufficient.
    """
    try:
        async with db_pg.acquire() as conn:
            query = """
            SELECT "creditBalance" FROM users
            WHERE id = $1;
            """
            result = await conn.fetchrow(query, user_id)
            if result is None:
                error_msg = f"User with id not found."
                logging.error(error_msg)
                raise ValueError(error_msg)
            
            balance = result["creditBalance"]
            if balance < Decimal("0.5"):
                error_msg = f"Insufficient balance (${balance}). Minimum $0.50 required."
                logging.error(error_msg)
                raise ValueError(error_msg)
            # If the balance is sufficient, you can simply return or continue.
            logging.info(f"User {user_id} has sufficient balance: ${balance}")
            return balance

    except Exception as e:
        logging.error(f"Error checking user balance: {e}")
        raise
