from strands import tool
import httpx
import os
from dotenv import load_dotenv

# Load environment variables at import time
load_dotenv()

LAMBDA_URL = os.getenv("LAMBDA_URL")  # e.g., https://cm4fcoh7ph4meec5jxek26ewyy0jxqxq.lambda-url.eu-north-1.on.aws/
API_KEY = os.getenv("DVLA_API_KEY")   # e.g., "test-api-key"

@tool(name="dvla_lookup")
async def dvla_lookup(registration: str):
    """
    Calls the mock DVLA Lambda URL and returns vehicle data.
    Input: vehicle registration number (UK format).
    """
    if not LAMBDA_URL or not API_KEY:
        return {"error": "LAMBDA_URL or DVLA_API_KEY not set in environment"}

    registration = registration.strip().upper()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                LAMBDA_URL,
                params={"registrationNumber": registration},
                headers={"x-api-key": API_KEY},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data

    except httpx.HTTPStatusError as e:
        # Returns body for debugging
        try:
            error_body = e.response.json()
        except:
            error_body = e.response.text
        return {"error": f"HTTP error: {e}", "details": error_body}

    except Exception as e:
        return {"error": str(e)}
