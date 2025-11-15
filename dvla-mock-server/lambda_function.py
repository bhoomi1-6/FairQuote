import json

# Load JSON at cold start
with open("vehicles.json", "r") as f:
    vehicles_data = json.load(f)

VEHICLES = {v["registration"].upper(): v for v in vehicles_data}
API_KEY = "test-api-key"


def lambda_handler(event, context):

    # Support API Gateway + Lambda Function URLs
    method = (
        event.get("httpMethod") or
        event.get("requestContext", {}).get("http", {}).get("method") or
        ""
    ).upper()

    # Normalize headers
    headers = {k.lower(): v for k, v in event.get("headers", {}).items()}
    x_api_key = headers.get("x-api-key")

    if x_api_key != API_KEY:
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"detail": "Invalid API key"})
        }

    # Extract registration number
    registration = None

    if method == "GET":
        registration = event.get("queryStringParameters", {}).get("registrationNumber")

    elif method == "POST":
        try:
            body = json.loads(event.get("body", "{}"))
            registration = body.get("registrationNumber")
        except:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"detail": "Invalid JSON"})
            }

    else:
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"detail": "Method not allowed"})
        }

    # Validate
    if not registration:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"detail": "registrationNumber is required"})
        }

    reg = registration.strip().upper()
    vehicle = VEHICLES.get(reg)

    if not vehicle:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"detail": "Vehicle not found"})
        }

    # Good response
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(vehicle)
    }
