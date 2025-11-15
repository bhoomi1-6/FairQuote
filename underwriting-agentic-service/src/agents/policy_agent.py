from strands import Agent
from src.config.init_model import bedrock_model

class PolicyAgent(Agent):

    model = bedrock_model
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
