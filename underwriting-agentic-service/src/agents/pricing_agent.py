from strands import Agent
from src.config.init_model import bedrock_model

class PricingAgent(Agent):

    model = bedrock_model
    name = "pricing_agent"
    system_prompt= "Computes risk score + premium; generates natural language explanation."

    tools = ["risk_rule_engine_tool", "premium_calculator_tool", "vehicle_insurance_recommendation"]

    instructions = """
    You compute:
    - Risk score (via risk_model tool)
    - Premium (via premium_calculator tool)
    - Price explanation (use RAG tool to fetch risk snippets)
    - Personalized recommendations (from RAG)

    Workflow:
    1. Receive intake payload.
    2. Call tool risk_model(user_data)
    3. Call tool premium_calculator()
    4. Retrieve risk reasoning from RAG
    5. Produce:
        {
          "premium": ...,
          "risk_score": ...,
          "explanation": ...,
          "breakdown": ...,
          "recommendations": ...
        }
    6. Return the pricing result.
    """
