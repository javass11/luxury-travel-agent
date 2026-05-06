from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RedemptionValue:
    redemption_type: str
    cash_price: float
    points_required: int
    taxes_and_fees: float
    cpp: float
    value_tier: str


def calculate_cpp(
    cash_price: float,
    points_required: int,
    taxes_and_fees: float = 0.0,
) -> float:
    """
    Calculate cents per point for a flight or hotel redemption.

    Formula:
        CPP = ((cash price - award taxes/fees) / points required) * 100

    Example:
        $4,000 flight, 80,000 miles, $200 taxes/fees
        (($4,000 - $200) / 80,000) * 100 = 4.75 cpp
    """
    if cash_price < 0:
        raise ValueError("cash_price cannot be negative")

    if points_required <= 0:
        raise ValueError("points_required must be greater than zero")

    if taxes_and_fees < 0:
        raise ValueError("taxes_and_fees cannot be negative")

    net_value = max(cash_price - taxes_and_fees, 0)
    return round((net_value / points_required) * 100, 2)


def classify_cpp(cpp: float) -> str:
    """
    Classify redemption quality using general travel-rewards thresholds.
    You can adjust these thresholds based on your own valuation model.
    """
    if cpp >= 5.0:
        return "Exceptional value"
    if cpp >= 3.0:
        return "Strong value"
    if cpp >= 1.5:
        return "Good value"
    if cpp >= 1.0:
        return "Modest value"
    return "Poor value"


def evaluate_redemption(
    redemption_type: str,
    cash_price: float,
    points_required: int,
    taxes_and_fees: float = 0.0,
) -> RedemptionValue:
    cpp = calculate_cpp(
        cash_price=cash_price,
        points_required=points_required,
        taxes_and_fees=taxes_and_fees,
    )

    return RedemptionValue(
        redemption_type=redemption_type,
        cash_price=cash_price,
        points_required=points_required,
        taxes_and_fees=taxes_and_fees,
        cpp=cpp,
        value_tier=classify_cpp(cpp),
    )


def redemption_to_dict(redemption: RedemptionValue) -> dict:
    """Convert RedemptionValue to dictionary for JSON response"""
    return {
        "type": redemption.redemption_type,
        "cash_price": redemption.cash_price,
        "points_required": redemption.points_required,
        "taxes_and_fees": redemption.taxes_and_fees,
        "cpp": redemption.cpp,
        "value_tier": redemption.value_tier,
    }
