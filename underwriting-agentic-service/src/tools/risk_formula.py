# risk_rule_engine.py

from typing import Dict, Any, Optional
from dataclasses import dataclass

try:
    from strands import tool  # type: ignore
    _HAS_STRANDS = True
except Exception:
    _HAS_STRANDS = False


# ============================
# 1. RISK WEIGHTS
# ============================

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


# ============================
# 2. FACTOR FUNCTIONS
# ============================

def _age_factor(age: int) -> float:
    if age < 21: return 1.0
    if 21 <= age <= 24: return 0.75
    if 25 <= age <= 55: return 0.15
    if 56 <= age <= 70: return 0.35
    return 0.60

def _occupation_factor(job: str) -> float:
    j = (job or "").lower()
    high = ["delivery", "taxi", "driver", "construction", "bartend"]
    med = ["nurse", "teacher", "customer service", "warehouse"]
    low = ["software", "engineer", "accountant", "it manager"]

    if any(h in j for h in high): return 0.9
    if any(m in j for m in med): return 0.4
    if any(l in j for l in low): return 0.1
    return 0.35

def _postcode_factor(pc: str) -> float:
    p = (pc or "").upper()
    if p.startswith(("M", "B")): return 0.9
    if p.startswith("S"): return 0.6
    if p.startswith(("RG", "GU", "AL")): return 0.15
    return 0.4

def _claims_factor(c: int) -> float:
    if c == 0: return 0.0
    if c == 1: return 0.35
    if c == 2: return 0.6
    return 0.85

def _points_factor(p: int) -> float:
    if p == 0: return 0.0
    if 1 <= p <= 3: return 0.3
    if 4 <= p <= 6: return 0.6
    return 0.95

def _mileage_factor(m: int) -> float:
    if m < 8000: return 0.05
    if m <= 15000: return 0.15
    return 0.35

def _vehicle_grade_factor(g: float) -> float:
    if g < 10: return 0.05
    if g <= 20: return 0.25
    if g <= 30: return 0.55
    return 0.85

def _income_factor(inc: str) -> float:
    i = (inc or "").lower()
    if i == "low": return 0.25
    if i == "medium": return 0.10
    if i == "high": return 0.0
    return 0.12

def _usage_factor(u: str) -> float:
    use = (u or "").lower()
    if use == "commercial": return 0.4
    if use == "commute": return 0.15
    return 0.05  # social


# ============================
# 3. VEHICLE BASE PREMIUM
# ============================

def compute_base_premium(vehicle: Dict[str, Any]) -> float:
    grade = float(vehicle.get("insurance_grade", 15))
    year = int(vehicle.get("year", 2020))
    engine = float(vehicle.get("engine_size", 1.4))

    base = 300.0

    base += grade * 12

    if engine < 1.2: base += 20
    elif engine < 1.6: base += 40
    elif engine < 2.0: base += 70
    else: base += 120

    age = 2025 - year
    if age > 12: base += 40
    elif age < 3: base += 30

    return round(base, 2)


# ============================
# 4. RISK ENGINE
# ============================

def compute_rule_based_risk(user: Dict[str, Any], weights: Optional[Dict[str, float]] = None):

    default = RiskWeights()
    w = default.as_dict() if weights is None else {**default.as_dict(), **weights}

    factors = {
        "age": _age_factor(int(user.get("age", 35))),
        "occupation": _occupation_factor(user.get("occupation", "")),
        "postcode": _postcode_factor(user.get("postcode", "")),
        "claims": _claims_factor(int(user.get("claim_history", 0))),
        "points": _points_factor(int(user.get("driving_history_points", 0))),
        "mileage": _mileage_factor(int(user.get("annual_mileage", 10000))),
        "vehicle_grade": _vehicle_grade_factor(float(user.get("insurance_grade", 15))),
        "income": _income_factor(user.get("income", "medium")),
        "usage": _usage_factor(user.get("car_usage", "commute")),
    }

    breakdown = {}
    raw_score = 0.0
    total_weight = sum(w.values())

    for k, val in factors.items():
        contrib = w[k] * val
        raw_score += contrib
        breakdown[k] = {
            "value": round(val, 4),
            "weight": round(w[k], 4),
            "contrib": round(contrib, 6)
        }

    normalized = raw_score / total_weight
    risk_score = max(0.0, min(1.0, normalized))

    return {
        "risk_score": round(risk_score, 4),
        "raw_score": round(raw_score, 6),
        "normalized_score": round(normalized, 6),
        "breakdown": breakdown,
        "weights": w,
    }


# ============================
# 5. RISK ENGINE + BASE PREMIUM
# ============================

def compute_rule_based_risk_with_base(user: Dict[str, Any], vehicle: Dict[str, Any]):
    risk = compute_rule_based_risk(user)
    base = compute_base_premium(vehicle)

    risk["base_premium"] = base
    return risk


# ============================
# 6. STRANDS TOOL
# ============================

if _HAS_STRANDS:
    @tool(name="risk_rule_engine")
    def risk_rule_engine_tool(user: Dict[str, Any], vehicle: Dict[str, Any]):
        return compute_rule_based_risk_with_base(user, vehicle)
else:
    def risk_rule_engine_tool(user: Dict[str, Any], vehicle: Dict[str, Any]):
        return compute_rule_based_risk_with_base(user, vehicle)
