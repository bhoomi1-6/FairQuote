from strands import tool

@tool(name="premium_calculator")
def premium_calculator(risk_score: float, factors: dict):
    """
    Deterministic formula:
    Base * (1 + risk_score) * adjustments
    """
