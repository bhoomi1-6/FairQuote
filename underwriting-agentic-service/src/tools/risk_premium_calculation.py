from risk_formula import risk_rule_engine_tool
from premium_calculator import premium_calculator_tool

user = {
    "age": 19,
    "occupation": "Delivery Driver",
    "postcode": "M12",
    "claim_history": 1,
    "driving_history_points": 3,
    "annual_mileage": 16000,
    "insurance_grade": 28,
    "income": "low",
    "car_usage": "commercial",
    "security": {
        "immobiliser": True
    }
}

risk = risk_rule_engine_tool(user)
premium = premium_calculator_tool(risk["risk_score"], user)

print("Risk:", risk)
print("Premium:", premium)
