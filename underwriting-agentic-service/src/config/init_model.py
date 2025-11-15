from strands import Agent
from strands.models import BedrockModel
import os

# Create a Bedrock model instance
bedrock_model = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0"),
    temperature=0.1,
    top_p=0.8,
)

