from strands import tool


@tool(name="risk_model")
def risk_model(user_data: dict):
    """
    Simple weighted score:
    age_weight + postcode_factor + claims_factor ...
    Returns numeric risk score 0–1.
    """
