from strands import Agent
import os

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "bedrock").lower()

if MODEL_PROVIDER == "gemini":
    from strands.models.gemini import GeminiModel

    bedrock_model = GeminiModel(
        client_args={"api_key": os.getenv("GEMINI_API_KEY")},
        model_id=os.getenv("GEMINI_MODEL_ID", "gemini-flash-lite-latest"),
        params={"temperature": 0.1, "top_p": 0.8},
    )
else:
    from strands.models import BedrockModel

    bedrock_model = BedrockModel(
        model_id=os.getenv("BEDROCK_MODEL_ID"),
        temperature=0.1,
        top_p=0.8,
    )

