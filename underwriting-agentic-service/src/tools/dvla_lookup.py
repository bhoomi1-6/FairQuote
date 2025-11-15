from strands import tool
import requests
from dotenv import load_dotenv
load_dotenv()
import os

LAMBDA_URL = os.getenv("LAMBDA_URL")
API_KEY = os.getenv("DVLA_API_KEY")   # Should be "test-api-key"

@tool(name="dvla_lookup")
def dvla_lookup(registration: str):
    """
    Calls the AWS Lambda vehicle lookup service and returns DVLA-style mock data.
    """

    try:
        response = requests.get(
            LAMBDA_URL,
            params={"registrationNumber": registration},   # FIXED
            headers={"x-api-key": API_KEY}                # REQUIRED
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error: {str(http_err)}", "details": response.text}

    except Exception as e:
        return {"error": str(e)}
