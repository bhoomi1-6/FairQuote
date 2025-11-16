from premium_calculator import calculate_premium_with_explanation
import os

from dotenv import load_dotenv
load_dotenv()  # automatically looks for .env file in project root

os.environ.get("KNOWLEDGE_BASE_ID")
os.environ.get("AWS_REGION")


user = {
    "age": 24,
    "occupation": "Delivery Driver",
    "postcode": "M12",
    "claim_history": 2,
    "driving_history_points": 6,
    "annual_mileage": 16000,
    "insurance_grade": 28,
    "income": "low",
    "car_usage": "commercial",
    "security": {
        "alarm_cat1": True,
        "immobiliser": True
    }
}

print(calculate_premium_with_explanation(user, customer_id="12345"))
