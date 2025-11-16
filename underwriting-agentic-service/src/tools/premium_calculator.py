# premium_calculator.py

from typing import Dict, Any
from risk_formula import risk_rule_engine_tool


try:
    from strands import tool
    _HAS_STRANDS = True
except:
    _HAS_STRANDS = False


# ============================
# 1. MULTIPLIERS
# ============================

def vehicle_multiplier(grade: float) -> float:
    if grade < 10: return 0.95
    if grade <= 20: return 1.00
    if grade <= 30: return 1.15
    return 1.30

def mileage_multiplier(miles: int) -> float:
    if miles < 3000: return 1.05
    if miles <= 7000: return 1.00
    if miles <= 12000: return 1.10
    return 1.25

def usage_multiplier(usage: str) -> float:
    u = (usage or "").lower()
    if u == "social": return 1.00
    if u == "commute": return 1.10
    if u in ("commercial", "business"): return 1.20
    return 1.10


# ============================
# 2. SECURITY DISCOUNTS
# ============================

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
    return premium * (1 - total_discount), total_discount


# ============================
# 3. FULL PREMIUM CALCULATOR
# ============================

def compute_premium(risk_score: float, base_premium: float, user: Dict[str, Any]) -> Dict[str, Any]:
    mileage = int(user.get("annual_mileage", 8000))
    grade = float(user.get("insurance_grade", 15))
    usage = user.get("car_usage", "commute")
    security = user.get("security", {})

    v_mult = vehicle_multiplier(grade)
    m_mult = mileage_multiplier(mileage)
    u_mult = usage_multiplier(usage)
    risk_mult = 1 + (risk_score * 1.5)

    before_sec = base_premium * v_mult * m_mult * u_mult * risk_mult
    after_sec, sec_discount = apply_security_discounts(before_sec, security)

    return {
        "base_premium": round(base_premium, 2),
        "vehicle_multiplier": round(v_mult, 3),
        "mileage_multiplier": round(m_mult, 3),
        "usage_multiplier": round(u_mult, 3),
        "risk_multiplier": round(risk_mult, 3),
        "premium_before_security": round(before_sec, 2),
        "security_discount_rate": round(sec_discount, 3),
        "final_premium": round(after_sec, 2),
    }


# ============================
# 4. STRANDS TOOL WRAPPER
# ============================

if _HAS_STRANDS:
    @tool(name="premium_calculator")
    def premium_calculator_tool(risk_score: float, base_premium: float, user: Dict[str, Any]):
        return compute_premium(risk_score, base_premium, user)
else:
    def premium_calculator_tool(risk_score: float, base_premium: float, user: Dict[str, Any]):
        return compute_premium(risk_score, base_premium, user)


def show_risk(user: Dict[str, Any], vehicle: Dict[str, Any], customer_id: str):
    # Get risk score + base premium
    risk_data = risk_rule_engine_tool(user, vehicle)
    risk_score = risk_data["risk_score"]
    base_premium = risk_data["base_premium"]

    # ----- DEBUG / LOGGING: print risk output -----
    print("\n===== RISK MODEL OUTPUT =====")
    print(f"Risk Score: {risk_data['risk_score']}")
    print(f"Base Premium (vehicle-based): {risk_data['base_premium']}")
    print("Breakdown:")
    for factor, info in risk_data["breakdown"].items():
        print(f"  {factor}: value={info['value']}, weight={info['weight']}, contrib={info['contrib']}")
    print("================================\n")



    return {
        "risk_score": risk_score,
        "risk_breakdown": risk_data["breakdown"],
    }
