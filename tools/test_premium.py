from premium_calculator import premium_calculator

result = premium_calculator(
    base_premium=400,
    risk_score=0.22,   # 22% uplift
    adjustments={
        "age": -0.10,
        "occupation": -0.05,
        "postcode": 0.20,
        "claims": 0.05
    }
)

print(result)
