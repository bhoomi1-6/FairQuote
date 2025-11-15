from strands import Agent, tool, message

class PolicyAgent(Agent):

    name = "policy_generator"
    description = "Assembles policy document via RAG + templates."

    tools = ["policy_rag"]

    instructions = """
    Goals:
    - Use RAG to fetch relevant policy clauses
    - Assemble a complete insurance policy document
    - Use LLM to generate plain-English summaries
    - Maintain structure:
        - Definitions
        - Coverage
        - Exclusions
        - Limits
        - Conditions
    - Output PDF-ready markdown
    """

    @message(trigger="pricing.completed")
    def generate_policy(self, pricing_payload):
        self.emit("policy.completed", pricing_payload)
