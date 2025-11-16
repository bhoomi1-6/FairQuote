# risk_rule_engine.py

from typing import Dict, Any, Optional
from dataclasses import dataclass, field

try:
    # Optional: if using STRANDS, uncomment the next line and the @tool wrapper below
    from strands import tool  # type: ignore
    _HAS_STRANDS = True
except Exception:
    _HAS_STRANDS = False

@dataclass
class RiskWeights:
    age: float = 1.0
    occupation: float = 1.0
    postcode: float = 1.0
    claims: float = 1.5
    points: float = 1.5
    mileage: float = 0.6
    vehicle_grade: float = 0.8
    income: float = 0.4
    usage: float = 0.4

    def as_dict(self):
        return {
            "age": self.age,
            "occupation": self.occupation,
            "postcode": self.postcode,
            "claims": self.claims,
            "points": self.points,
            "mileage": self.mileage,
            "vehicle_grade": self.vehicle_grade,
            "income": self.income,
            "usage": self.usage,
        }

def _age_factor(age: int) -> float:
    """Return factor [0..1] for age (higher => more risky)."""
    if age < 21:
        return 1.0
    if 21 <= age <= 24:
        return 0.75
    if 25 <= age <= 55:
        return 0.15
    if 56 <= age <= 70:
        return 0.35
    return 0.60  # 71+

def _occupation_factor(occupation: str) -> float:
    o = (occupation or "").lower()
    high = ["delivery", "taxi", "driver", "construction", "bartend", "fast food"]
    med = ["nurse", "teacher", "customer service", "warehouse", "graphic"]
    low = ["software", "engineer", "accountant", "it manager", "scientist"]
    if any(h in o for h in high):
        return 0.9
    if any(m in o for m in med):
        return 0.4
    if any(l in o for l in low):
        return 0.1
    return 0.35

def _postcode_factor(postcode: str) -> float:
    p = (postcode or "").upper()
    if p.startswith(("M", "B")):
        return 0.9
    if p.startswith("S"):
        return 0.6
    if p.startswith(("RG", "GU", "AL")):
        return 0.15
    return 0.4

def _claims_factor(claims: int) -> float:
    if claims <= 0:
        return 0.0
    if claims == 1:
        return 0.35
    if claims == 2:
        return 0.6
    return 0.85  # 3+

def _points_factor(points: int) -> float:
    if points <= 0:
        return 0.0
    if 1 <= points <= 3:
        return 0.3
    if 4 <= points <= 6:
        return 0.6
    return 0.95

def _mileage_factor(miles: int) -> float:
    if miles < 8000:
        return 0.05
    if miles <= 15000:
        return 0.15
    return 0.35

def _vehicle_grade_factor(insurance_grade: float) -> float:
    if insurance_grade < 10:
        return 0.05
    if insurance_grade <= 20:
        return 0.25
    if insurance_grade <= 30:
        return 0.55
    return 0.85

def _income_factor(income: str) -> float:
    inc = (income or "").lower()
    if inc == "low":
        return 0.25
    if inc == "medium":
        return 0.10
    if inc == "high":
        return 0.0
    return 0.12

def _usage_factor(usage: str) -> float:
    u = (usage or "").lower()
    if u == "commercial":
        return 0.4
    if u == "commute":
        return 0.15
    return 0.05  # social / other

def compute_rule_based_risk(user: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Compute a deterministic risk score [0.0 - 1.0] using rule-based factors.
    Returns a dict:
      {
        "risk_score": float,
        "raw_score": float,
        "normalized_score": float,
        "breakdown": { factor: {value, weight, contrib}, ...},
        "weights": {...}
      }
    user: dict containing fields:
      - age (int)
      - occupation (str)
      - postcode (str)
      - claim_history (int)
      - driving_history_points (int)
      - annual_mileage (int)
      - insurance_grade (int or float)
      - income (str)
      - car_usage (str)
    weights: optional dict override for factor weights (keys as in RiskWeights)
    """
    # default weights
    default = RiskWeights()
    if weights is None:
        w = default.as_dict()
    else:
        # merge overrides
        w = default.as_dict()
        for k, v in (weights or {}).items():
            if k in w:
                w[k] = float(v)

    # pull inputs with safe defaults
    age = int(user.get("age", 35))
    occupation = user.get("occupation", "")
    postcode = user.get("postcode", "")
    claims = int(user.get("claim_history", 0))
    points = int(user.get("driving_history_points", 0))
    miles = int(user.get("annual_mileage", 10000))
    insurance_grade = float(user.get("insurance_grade", user.get("insurance_grade", 15)))
    income = user.get("income", "medium")
    usage = user.get("car_usage", "commute")

    # compute factor values (0..1 scale roughly)
    factors = {
        "age": _age_factor(age),
        "occupation": _occupation_factor(occupation),
        "postcode": _postcode_factor(postcode),
        "claims": _claims_factor(claims),
        "points": _points_factor(points),
        "mileage": _mileage_factor(miles),
        "vehicle_grade": _vehicle_grade_factor(insurance_grade),
        "income": _income_factor(income),
        "usage": _usage_factor(usage),
    }

    # breakdown contributions
    breakdown = {}
    total_weight = sum(w.values())
    raw_score = 0.0
    for k, factor_val in factors.items():
        weight = w.get(k, 0.0)
        contrib = weight * factor_val
        breakdown[k] = {"value": round(float(factor_val), 4), "weight": round(float(weight), 4), "contrib": round(float(contrib), 6)}
        raw_score += contrib

    # normalize to 0..1 by dividing by sum of weights*max_factor (max_factor here is 1.0)
    normalized = raw_score / total_weight if total_weight > 0 else 0.0

    # small random jitter could be added if desired — commented out for determinism
    # import random
    # normalized = normalized + random.uniform(-0.01, 0.01)

    # clamp to [0,1]
    risk_score = max(0.0, min(1.0, float(normalized)))

    return {
        "risk_score": round(risk_score, 4),
        "raw_score": round(raw_score, 6),
        "normalized_score": round(normalized, 6),
        "breakdown": breakdown,
        "weights": {k: round(v, 4) for k, v in w.items()}
    }


# Optional STRANDS tool wrapper — uncomment decorator if you have strands available
if _HAS_STRANDS:
    @tool(name="risk_rule_engine")
    def risk_rule_engine_tool(user: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        return compute_rule_based_risk(user, weights)
else:
    # expose a callable alias for non-Strands use
    def risk_rule_engine_tool(user: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        return compute_rule_based_risk(user, weights)


# # Example quick test function (not a full unit test)
# def _example():
#     user = {
#         "age": 24,
#         "occupation": "Delivery Driver",
#         "postcode": "M12",
#         "claim_history": 2,
#         "driving_history_points": 6,
#         "annual_mileage": 16000,
#         "insurance_grade": 28,
#         "income": "low",
#         "car_usage": "commercial"
#     }
#     print(compute_rule_based_risk(user))

# if __name__ == "__main__":
#     _example()
