"""Baseline tests for the deterministic pricing engine (no LLM involved).

Expected numbers were worked out by hand from the formulas in
src/tools/risk_formula.py and src/tools/premium_calculator.py, not copied
from the code's output. Tests marked xfail(strict=True) document KNOWN BUGS:
when the bug is fixed the test starts passing, strict mode then fails the run,
and you remove the marker. That is the regression-test workflow.
"""
from datetime import date

import pytest

from src.tools.premium_calculator import compute_premium
from src.tools.risk_formula import (
    RiskWeights,
    compute_base_premium,
    compute_rule_based_risk,
    compute_rule_based_risk_with_base,
)


def test_weights_sum_is_8_2():
    # 1+1+1 (age, occupation, postcode) + 1.5+1.5 (claims, points)
    # + 0.6 + 0.8 + 0.4 + 0.4 = 8.2. The risk score is normalised by this.
    assert sum(RiskWeights().as_dict().values()) == pytest.approx(8.2)


def test_low_risk_worked_example():
    user = {
        "age": 30, "occupation": "software engineer", "postcode": "RG1",
        "claim_history": 0, "driving_history_points": 0, "annual_mileage": 6000,
        "income": "high", "car_usage": "social", "insurance_grade": 12,
    }
    vehicle = {"insurance_grade": 12, "year": 2020, "engine_size": 1.4}

    risk = compute_rule_based_risk_with_base(user, vehicle)
    # raw = .15 + .10 + .15 + 0 + 0 + .6*.05 + .8*.25 + 0 + .4*.05 = 0.65
    # 0.65 / 8.2 = 0.0793
    assert risk["risk_score"] == pytest.approx(0.0793, abs=1e-4)
    # base = 300 + 12*12 + 40 (engine 1.4L) + 0 (vehicle age 5) = 484
    assert risk["base_premium"] == pytest.approx(484.0)

    premium = compute_premium(risk["risk_score"], risk["base_premium"], user)
    # multipliers all 1.00 except risk: 1 + 0.0793*1.5 = 1.11895
    # 484 * 1.11895 = 541.57
    assert premium["final_premium"] == pytest.approx(541.57, abs=0.01)


def test_high_risk_worked_example_with_security_discount():
    user = {
        "age": 19, "occupation": "Delivery Driver", "postcode": "M12",
        "claim_history": 1, "driving_history_points": 3, "annual_mileage": 16000,
        "income": "low", "car_usage": "commercial", "insurance_grade": 28,
        "security": {"immobiliser": True},
    }
    vehicle = {"insurance_grade": 28, "year": 2018, "engine_size": 1.6}

    risk = compute_rule_based_risk_with_base(user, vehicle)
    # raw = 1.0 + .9 + .9 + 1.5*.35 + 1.5*.3 + .6*.35 + .8*.55 + .4*.25 + .4*.4 = 4.685
    # 4.685 / 8.2 = 0.5713
    assert risk["risk_score"] == pytest.approx(0.5713, abs=1e-4)
    # base = 300 + 28*12 + 70 (engine 1.6 to <2.0) + 0 = 706
    assert risk["base_premium"] == pytest.approx(706.0)

    premium = compute_premium(risk["risk_score"], risk["base_premium"], user)
    # 706 * 1.15 (grade 28) * 1.25 (16k miles) * 1.20 (commercial) * 1.85695 = 2261.49
    assert premium["premium_before_security"] == pytest.approx(2261.49, abs=0.01)
    # immobiliser = 3% discount -> 2193.64
    assert premium["final_premium"] == pytest.approx(2193.64, abs=0.01)


def test_all_security_features_add_up_to_33_percent():
    # NOTE: premium_calculator caps the discount at 40%, but the discount table
    # can only ever add up to 0.05 + 0.03 + 0.05 + 0.20 = 0.33, so the cap is
    # currently unreachable (dead code). Worth knowing if asked about it.
    user = {"security": {"alarm_cat1": True, "immobiliser": True, "tracker": True,
                         "telematics": True}}
    out = compute_premium(0.0, 1000.0, user)
    assert out["security_discount_rate"] == pytest.approx(0.33)


def test_risk_score_stays_between_0_and_1_for_worst_case():
    worst = {
        "age": 17, "occupation": "taxi", "postcode": "M1", "claim_history": 9,
        "driving_history_points": 12, "annual_mileage": 50000, "income": "low",
        "car_usage": "commercial", "insurance_grade": 50,
    }
    score = compute_rule_based_risk(worst)["risk_score"]
    assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------- known bugs

@pytest.mark.xfail(strict=True, reason=(
    "BUG: a misnamed or missing field silently falls back to a default "
    "(e.g. claims -> 0) so the quote is wrong with no error. Fix: validate "
    "the input with a Pydantic model and reject incomplete data."))
def test_misnamed_field_must_not_silently_default():
    with pytest.raises(Exception):
        compute_rule_based_risk({"age": 30, "claims": 3})  # key should be claim_history


@pytest.mark.xfail(strict=True, reason=(
    "BUG: vehicle age is computed from a hard-coded 2025, so it is wrong "
    "from 2026 onwards. Fix: inject today's year."))
def test_vehicle_age_surcharge_uses_current_year():
    this_year = date.today().year
    old = compute_base_premium({"insurance_grade": 15, "year": this_year - 13, "engine_size": 1.4})
    newer = compute_base_premium({"insurance_grade": 15, "year": this_year - 5, "engine_size": 1.4})
    assert old - newer == pytest.approx(40.0)  # >12 years old adds 40
