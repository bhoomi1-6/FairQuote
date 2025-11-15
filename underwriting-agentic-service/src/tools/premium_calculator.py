from strands import tool

@tool(name="premium_calculator")
def premium_calculator(
    base_premium: float,
    risk_score: float,
    adjustments: dict
):
    """
    Deterministic premium calculator for the Insurance MAS.
    
    Parameters
    ----------
    base_premium : float
        The initial premium derived from vehicle characteristics.
        
    risk_score : float
        Final ML/actuarial risk score (0.0–1.0). 
        The risk multiplier becomes (1 + risk_score).
        
    adjustments : dict
        Dictionary of adjustment factors (as decimals).
        Example:
            {
                "age": -0.10,
                "postcode": 0.20,
                "claims": 0.05,
                "driving_history": -0.15
            }

    Returns
    -------
    dict
        {
            "base_premium": ...,
            "risk_multiplier": ...,
            "adjustment_multiplier": ...,
            "final_premium": ...,
            "breakdown": {
                "risk_score": ...,
                "risk_multiplier": ...,
                "adjustments": {...},
                "total_adjustment_percent": ...
            }
        }

    Formula
    -------
    final_premium = base_premium 
                    * (1 + risk_score) 
                    * (product of (1 + each adjustment))
    """

    # -----------------------------
    # Validate Inputs
    # -----------------------------
    if base_premium <= 0:
        raise ValueError("Base premium must be > 0")

    if not isinstance(adjustments, dict):
        raise ValueError("adjustments must be a dict of key -> decimal factor")

    # -----------------------------
    # Risk Multiplier
    # -----------------------------
    risk_multiplier = 1 + float(risk_score)

    # -----------------------------
    # Adjustment Multiplier
    # -----------------------------
    adjustment_multiplier = 1.0
    for k, v in adjustments.items():
        adjustment_multiplier *= (1 + float(v))

    # -----------------------------
    # Final Premium
    # -----------------------------
    final = base_premium * risk_multiplier * adjustment_multiplier

    # Round to 2 decimals for currency
    final_rounded = round(final, 2)

    # -----------------------------
    # Breakdown (important for MAS explainability)
    # -----------------------------
    total_adjustment_percent = sum(adjustments.values()) * 100

    breakdown = {
        "risk_score": risk_score,
        "risk_multiplier": risk_multiplier,
        "adjustments": adjustments,
        "total_adjustment_percent": total_adjustment_percent
    }

    return {
        "base_premium": base_premium,
        "risk_multiplier": risk_multiplier,
        "adjustment_multiplier": adjustment_multiplier,
        "final_premium": final_rounded,
        "breakdown": breakdown
    }
