from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class RedemptionOption:
    name: str
    redemption_type: str  # "flight" or "hotel"
    cash_price: float
    points_required: int
    taxes_and_fees: float = 0.0
    notes: Optional[str] = None


@dataclass(frozen=True)
class EvaluatedRedemption:
    name: str
    redemption_type: str
    cash_price: float
    points_required: int
    taxes_and_fees: float
    cpp: float
    value_tier: str
    notes: Optional[str]


def calculate_cpp(
    cash_price: float,
    points_required: int,
    taxes_and_fees: float = 0.0,
) -> float:
    """
    Calculate cents per point.

    Formula:
        CPP = ((cash price - award taxes/fees) / points required) * 100
    """
    if cash_price < 0:
        raise ValueError("cash_price cannot be negative")

    if points_required <= 0:
        raise ValueError("points_required must be greater than zero")

    if taxes_and_fees < 0:
        raise ValueError("taxes_and_fees cannot be negative")

    net_redemption_value = max(cash_price - taxes_and_fees, 0)
    return round((net_redemption_value / points_required) * 100, 2)


def classify_cpp(cpp: float) -> str:
    """
    General travel-rewards value tiers.
    Adjust these thresholds for your own valuation model if needed.
    """
    if cpp >= 5.0:
        return "Exceptional"
    if cpp >= 3.0:
        return "Strong"
    if cpp >= 1.5:
        return "Good"
    if cpp >= 1.0:
        return "Modest"
    return "Poor"


def evaluate_redemptions(options: List[RedemptionOption]) -> List[EvaluatedRedemption]:
    """Evaluate and rank redemption options by CPP value"""
    evaluated = []

    for option in options:
        cpp = calculate_cpp(
            cash_price=option.cash_price,
            points_required=option.points_required,
            taxes_and_fees=option.taxes_and_fees,
        )

        evaluated.append(
            EvaluatedRedemption(
                name=option.name,
                redemption_type=option.redemption_type,
                cash_price=option.cash_price,
                points_required=option.points_required,
                taxes_and_fees=option.taxes_and_fees,
                cpp=cpp,
                value_tier=classify_cpp(cpp),
                notes=option.notes,
            )
        )

    return sorted(evaluated, key=lambda item: item.cpp, reverse=True)


def find_best_redemption(evaluated: List[EvaluatedRedemption]) -> Optional[EvaluatedRedemption]:
    """Find the redemption option with the highest CPP value"""
    if not evaluated:
        return None
    return max(evaluated, key=lambda item: item.cpp)


def redemption_to_dict(redemption: EvaluatedRedemption) -> dict:
    """Convert EvaluatedRedemption to dictionary for JSON response"""
    return {
        "name": redemption.name,
        "type": redemption.redemption_type,
        "cash_price": redemption.cash_price,
        "points_required": redemption.points_required,
        "taxes_and_fees": redemption.taxes_and_fees,
        "cpp": redemption.cpp,
        "value_tier": redemption.value_tier,
        "notes": redemption.notes,
    }
