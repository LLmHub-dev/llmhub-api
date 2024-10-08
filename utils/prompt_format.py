def create_dynamic_prompt(prompt_data, dict_keys, dict_values):
    # Validate inputs
    if len(dict_keys) != len(dict_values):
        raise ValueError("dict_keys and dict_values must have the same length.")

    if not dict_keys or not dict_values:
        raise ValueError("dict_keys and dict_values cannot be empty.")

    # Create condition strings using dict_keys and dict_values
    conditions = []
    for key, value in zip(dict_keys, dict_values):
        conditions.append(f"if the instruction is related to {key}, output '{value}'")

    # Join conditions into a single string
    condition_str = ". ".join(conditions)

    # Format the possible outputs
    possible_outputs = []
    for value in dict_values:
        possible_outputs.append(f'"{value}"')

    # Join the possible outputs into a single string
    output_str = ", ".join(possible_outputs)

    # Build the system prompt
    system_prompt = (
        f"You are a routing agent. Based on the provided instruction, {condition_str}. "
        f"Do not include any additional text or information in your response. "
        f"Your output must strictly be one of the following with no extra characters: {output_str}."
    )
    
    prompt_data["system_prompt"] = system_prompt
    
    return prompt_data
