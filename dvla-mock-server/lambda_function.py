import json

# Load JSON at cold start
with open("vehicles.json", "r") as f:
    vehicles_data = json.load(f)

VEHICLES = {v["registration"].upper(): v for v in vehicles_data}

def lambda_handler(event, context):
    """
    Vehicle lookup function for AgentCore Gateway
    Expects: {"registrationNumber": "ABC123"}
    Returns: Vehicle data or error
    """
    
    # AgentCore Gateway passes parameters in 'body' as JSON string
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event.get('body', '{}'))
        else:
            body = event.get('body', {})
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    
    # Extract registration number
    registration = body.get('registrationNumber')
    
    if not registration:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'registrationNumber is required'})
        }
    
    # Lookup vehicle
    reg = registration.strip().upper()
    vehicle = VEHICLES.get(reg)
    
    if not vehicle:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'error': f'Vehicle not found for registration: {registration}'
            })
        }
    
    # Return vehicle data
    return {
        'statusCode': 200,
        'body': json.dumps(vehicle)
    }