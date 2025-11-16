from strands import tool
import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LAMBDA_ARN = "arn:aws:lambda:us-east-1:029449502346:function:vehicle-lookup:1"

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION     = "us-east-1"

# Create AWS Lambda client
lambda_client = boto3.client(
    "lambda",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

@tool(name="dvla_lookup")
async def dvla_lookup(registration: str):
    """
    Invokes the DVLA Lambda directly by ARN and returns vehicle data.
    """
    registration = registration.strip().upper()

    payload = {
        "body": json.dumps({"registrationNumber": registration})
    }

    try:
        # Invoke Lambda
        response = lambda_client.invoke(
            FunctionName=LAMBDA_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload)
        )

        # Parse Lambda result
        response_payload = response["Payload"].read()
        parsed = json.loads(response_payload)

        # Lambda returns {"statusCode": ..., "body": "...json..."}
        if "body" in parsed:
            try:
                parsed["body"] = json.loads(parsed["body"])
            except:
                pass

        return parsed

    except Exception as e:
        return {"error": str(e)}
