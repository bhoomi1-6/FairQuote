from strands import Agent, tool, message

class PricingAgent(Agent):

    name = "pricing_agent"
    description = "Computes risk score + premium; generates natural language explanation."

    tools = ["risk_model", "premium_calculator", "rag_explainer"]

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
    6. Emit event `pricing.completed`
    """

    @message(trigger="pricing.requested")
    def compute_price(self, intake_data):
        self.emit("pricing.completed", intake_data)
