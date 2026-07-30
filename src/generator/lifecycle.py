"""Customer lifecycle status rules derived from inactivity days."""

from __future__ import annotations

from typing import Literal

LifecycleStatus = Literal[
    "Active",
    "At Risk",
    "Dormant",
    "Churned",
    "Reactivated",
]

VALUE_SEGMENTS = (
    "Low Value",
    "Medium Value",
    "High Value",
    "Very High Value",
)


def status_from_inactivity(
    inactivity_days: int,
    *,
    previously_churned: bool = False,
) -> LifecycleStatus:
    """Map inactivity days to lifecycle status.

    Boundary rules:
    - Active: 0–30 days
    - At Risk: 31–45 days
    - Dormant: 46–59 days
    - Churned: 60+ days
    - Reactivated: previously churned and now Active band (≤30)

    Args:
        inactivity_days: Days since last qualifying activity (as of month-end).
        previously_churned: Whether the customer has ever been Churned before
            this assessment (including prior months).

    Returns:
        Lifecycle status label.
    """
    if inactivity_days < 0:
        raise ValueError(f"inactivity_days must be >= 0; got {inactivity_days}.")

    if previously_churned and inactivity_days <= 30:
        return "Reactivated"
    if inactivity_days <= 30:
        return "Active"
    if inactivity_days <= 45:
        return "At Risk"
    if inactivity_days <= 59:
        return "Dormant"
    return "Churned"


def assign_value_segment(
    rolling_3_month_revenue: float, thresholds: tuple[float, float, float]
) -> str:
    """Assign value segment from rolling 3-month revenue and quantile thresholds.

    Thresholds are ``(p50, p75, p90)`` of positive rolling revenue in the
    reporting month (computed across customers). Zero/missing revenue maps to
    Low Value.

    Args:
        rolling_3_month_revenue: Customer rolling revenue.
        thresholds: Ordered cut points for Medium / High / Very High.

    Returns:
        One of Low / Medium / High / Very High Value.
    """
    p50, p75, p90 = thresholds
    revenue = float(rolling_3_month_revenue)
    if revenue <= 0:
        return "Low Value"
    if revenue <= p50:
        return "Low Value"
    if revenue <= p75:
        return "Medium Value"
    if revenue <= p90:
        return "High Value"
    return "Very High Value"
