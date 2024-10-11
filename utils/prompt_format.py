def create_dynamic_prompt(dict_keys, dict_values):

    if len(dict_keys) != len(dict_values):
        raise ValueError("dict_keys and dict_values must have the same length.")
    if not dict_keys or not dict_values:
        raise ValueError("dict_keys and dict_values cannot be empty.")


    conditions = []
    for key, value in zip(dict_keys, dict_values):
        conditions.append(f"if the instruction is related to {key}, output '{value}'")
    condition_str = ". ".join(conditions)


    possible_outputs = []
    for value in dict_values:
        possible_outputs.append(f'"{value}"')
    output_str = ", ".join(possible_outputs)

    system_prompt = (
        f"You are a routing agent. Based on the provided instruction, {condition_str}. "
        f"Do not include any additional text or information in your response. "
        f"Your output must strictly be one of the following with no extra characters: {output_str}."
    )

    return system_prompt
