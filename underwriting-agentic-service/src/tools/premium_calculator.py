# premium_calculator.py

from typing import Dict, Any
from risk_formula import risk_rule_engine_tool
from rag_explainer import vehicle_insurance_rag

try:
    from strands import tool
    _HAS_STRANDS = True
except Exception:
    _HAS_STRANDS = False


# --------------------------------------------
# 1. AGE-BASED BASE PREMIUM TABLE
# --------------------------------------------
BASE_PREMIUM_TABLE = [
    ((17, 20), 2200),
    ((21, 24), 1600),
    ((25, 34), 800),
    ((35, 49), 650),
    ((50, 69), 550),
    ((70, 99), 1100),
]


def get_base_premium(age: int) -> float:
    for (low, high), price in BASE_PREMIUM_TABLE:
        if low <= age <= high:
            return price
    return 900  # fallback


# --------------------------------------------
# 2. MULTIPLIERS
# --------------------------------------------
def vehicle_multiplier(insurance_grade: float) -> float:
    if insurance_grade < 10:
        return 0.95
    if insurance_grade <= 20:
        return 1.00
    if insurance_grade <= 30:
        return 1.15
    return 1.30


def mileage_multiplier(mileage: int) -> float:
    if mileage < 3000:
        return 1.05
    if mileage <= 7000:
        return 1.00
    if mileage <= 12000:
        return 1.10
    return 1.25


def usage_multiplier(usage: str) -> float:
    u = (usage or "").lower()
    if u == "social":
        return 1.00
    if u == "commute":
        return 1.10
    if u in ("commercial", "business"):
        return 1.20
    return 1.10


# --------------------------------------------
# 3. SECURITY DISCOUNTS
# --------------------------------------------
SECURITY_DISCOUNTS = {
    "alarm_cat1": 0.05,
    "immobiliser": 0.03,
    "tracker": 0.05,
    "telematics": 0.20,
}


def apply_security_discounts(premium: float, security: Dict[str, bool]):
    total_discount = 0.0
    for feature, enabled in security.items():
        if enabled:
            total_discount += SECURITY_DISCOUNTS.get(feature, 0.0)

    total_discount = min(total_discount, 0.40)
    after = premium * (1 - total_discount)
    return after, total_discount


# --------------------------------------------
# 4. FULL PREMIUM CALCULATION
# --------------------------------------------
def compute_premium(risk_score: float, user: Dict[str, Any]) -> Dict[str, Any]:
    age = int(user.get("age", 35))
    mileage = int(user.get("annual_mileage", 8000))
    insurance_grade = float(user.get("insurance_grade", 15))
    usage = user.get("car_usage", "commute")
    security = user.get("security", {})

    base = get_base_premium(age)
    v_mult = vehicle_multiplier(insurance_grade)
    m_mult = mileage_multiplier(mileage)
    u_mult = usage_multiplier(usage)
    risk_mult = 1 + (risk_score * 1.5)

    before_security = base * v_mult * m_mult * u_mult * risk_mult
    after_security, sec_discount = apply_security_discounts(before_security, security)

    return {
        "base_premium": round(base, 2),
        "vehicle_multiplier": round(v_mult, 3),
        "mileage_multiplier": round(m_mult, 3),
        "usage_multiplier": round(u_mult, 3),
        "risk_multiplier": round(risk_mult, 3),
        "premium_before_security": round(before_security, 2),
        "security_discount_rate": round(sec_discount, 3),
        "final_premium": round(after_security, 2),
    }


# --------------------------------------------
# 5. STRANDS TOOL WRAPPERS
# --------------------------------------------
if _HAS_STRANDS:
    @tool(name="premium_calculator")
    def premium_calculator_tool(risk_score: float, user: Dict[str, Any]):
        return compute_premium(risk_score, user)
else:
    def premium_calculator_tool(risk_score: float, user: Dict[str, Any]):
        return compute_premium(risk_score, user)


# --------------------------------------------
# 6. PREMIUM WITH RAG EXPLANATION
# --------------------------------------------
def calculate_premium_with_explanation(user: Dict[str, Any], customer_id: str):
    risk_data = risk_rule_engine_tool(user)
    risk_score = risk_data["risk_score"]

    premium_details = compute_premium(risk_score, user)

    rag_query = (
        f"Explain this vehicle insurance calculation.\n"
        f"Risk score: {risk_score}\n"
        f"Breakdown: {risk_data['breakdown']}\n"
        f"Premium details: {premium_details}"
    )

    rag_expl = vehicle_insurance_rag(rag_query, customer_id)

    return {
        "premium_details": premium_details,
        "risk_score": risk_score,
        "risk_breakdown": risk_data["breakdown"],
        "rag_explanation": rag_expl,
    }


# Optional Strands wrapper
if _HAS_STRANDS:
    @tool(name="premium_with_explanation")
    def premium_with_explanation_tool(user: Dict[str, Any], customer_id: str):
        return calculate_premium_with_explanation(user, customer_id)
