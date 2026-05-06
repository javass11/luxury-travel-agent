from dataclasses import dataclass
from typing import List, Optional

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
import io
import base64


@dataclass
class TravelRedemptionOption:
    program_or_airline: str
    flight_number: str
    origin: str
    destination: str
    cabin: str
    cash_price_usd: Optional[float]
    miles_required: Optional[int]
    taxes_usd: Optional[float]
    cpp: Optional[float]


def cpp_color(cpp: float) -> str:
    """
    Color-code cpp values by redemption quality.
    Adjust thresholds based on your product's valuation model.
    """
    if cpp >= 5.0:
        return "#D4AF37"  # gold: exceptional value
    if cpp >= 3.0:
        return "#2E8B57"  # green: strong value
    if cpp >= 1.5:
        return "#4682B4"  # blue: fair value
    return "#A9A9A9"      # gray: weak value


def visualize_cpp_bar_chart(
    options: List[TravelRedemptionOption],
    title: str = "Cents Per Point Redemption Value",
    output_file: Optional[str] = None,
    return_base64: bool = False,
) -> Optional[str]:
    """
    Creates a horizontal bar chart of cpp values.
    Options without cpp values are excluded because cpp requires both cash price and miles data.

    Args:
        options: List of TravelRedemptionOption objects
        title: Chart title
        output_file: Optional file path to save PNG
        return_base64: If True, return base64-encoded image for web embedding

    Returns:
        Base64 string if return_base64=True, otherwise None
    """
    chart_options = [option for option in options if option.cpp is not None]

    if not chart_options:
        print("No cpp values available to visualize.")
        return None

    chart_options = sorted(chart_options, key=lambda item: item.cpp or 0, reverse=True)

    labels = [
        f"{option.program_or_airline} | {option.flight_number} | "
        f"{option.origin}→{option.destination} | {option.cabin}"
        for option in chart_options
    ]
    values = [option.cpp for option in chart_options]
    colors = [cpp_color(option.cpp or 0) for option in chart_options]

    plt.figure(figsize=(12, max(6, len(chart_options) * 0.65)))
    bars = plt.barh(labels, values, color=colors)

    plt.gca().invert_yaxis()
    plt.xlabel("Cents Per Point (cpp)")
    plt.title(title, fontsize=16, fontweight="bold")

    # Reference lines for value tiers.
    plt.axvline(1.5, color="#4682B4", linestyle="--", linewidth=1, alpha=0.6)
    plt.axvline(3.0, color="#2E8B57", linestyle="--", linewidth=1, alpha=0.6)
    plt.axvline(5.0, color="#D4AF37", linestyle="--", linewidth=1, alpha=0.8)

    plt.text(1.5, -0.6, "Fair", color="#4682B4", ha="center", fontsize=9)
    plt.text(3.0, -0.6, "Strong", color="#2E8B57", ha="center", fontsize=9)
    plt.text(5.0, -0.6, "Exceptional", color="#D4AF37", ha="center", fontsize=9)

    # Add numeric cpp labels to the end of each bar.
    for bar, value in zip(bars, values):
        width = bar.get_width()
        plt.text(
            width + 0.05,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f} cpp",
            va="center",
            fontsize=10,
        )

    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=200, bbox_inches="tight")
        print(f"Saved chart to {output_file}")

    if return_base64:
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=200, bbox_inches="tight")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        return f"data:image/png;base64,{image_base64}"

    plt.show()
    return None
