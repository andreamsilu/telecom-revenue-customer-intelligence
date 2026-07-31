"""Executive month-story narratives from KPI movements and recommendations.

Builds deterministic Finding-style storytelling text for the UI.
Business interpretation belongs here — not in Streamlit pages.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.analytics.comparisons import (
    percent_change,
    percentage_point_change,
    safe_float,
)
from src.analytics.helpers import previous_month_value
from src.analytics.loaders import row_for_month
from src.recommendations.models import Recommendation

# Absolute MoM % below this is treated as flat for headline wording.
_FLAT_BAND_PCT = 0.5
# Churn pp move below this is treated as stable.
_CHURN_FLAT_PP = 0.1


@dataclass(frozen=True)
class MonthStory:
    """Structured executive narrative for a reporting month."""

    period_label: str
    headline: str
    movements: tuple[str, ...]
    drivers: tuple[str, ...]
    priority_action: str | None
    closing: str


def build_month_story(
    executive_mart: pd.DataFrame,
    reporting_month: str,
    recommendations: list[Recommendation],
) -> MonthStory:
    """Compose a month-in-review story from national KPIs and fired rules.

    Args:
        executive_mart: Executive monthly mart.
        reporting_month: Month-start date (YYYY-MM-DD).
        recommendations: Priority-sorted recommendations for the month.

    Returns:
        Deterministic ``MonthStory`` for executive display.
    """
    row = row_for_month(executive_mart, reporting_month)
    month = str(row["reporting_month"])
    period = pd.Timestamp(month).strftime("%B %Y")

    revenue = safe_float(row["total_revenue"])
    revenue_prev = previous_month_value(executive_mart, month, "total_revenue")
    arpu = safe_float(row["arpu"])
    arpu_prev = previous_month_value(executive_mart, month, "arpu")
    subs = safe_float(row["total_subscribers"])
    subs_prev = previous_month_value(executive_mart, month, "total_subscribers")
    churn = safe_float(row["churn_rate"])
    churn_prev = previous_month_value(executive_mart, month, "churn_rate")

    rev_chg = percent_change(revenue, revenue_prev)
    arpu_chg = percent_change(arpu, arpu_prev)
    subs_chg = percent_change(subs, subs_prev)
    churn_pp = percentage_point_change(churn, churn_prev)

    movements = (
        _movement_line("Total revenue", rev_chg, unit="%"),
        _movement_line("ARPU", arpu_chg, unit="%"),
        _movement_line("Subscribers", subs_chg, unit="%"),
        _churn_line(churn_pp),
    )

    headline = _headline(
        period=period,
        rev_chg=rev_chg,
        arpu_chg=arpu_chg,
        subs_chg=subs_chg,
        churn_pp=churn_pp,
    )
    drivers = tuple(rec.finding for rec in recommendations[:3])
    priority_action = recommendations[0].recommended_action if recommendations else None
    closing = _closing(recommendations, rev_chg=rev_chg, churn_pp=churn_pp)

    return MonthStory(
        period_label=period,
        headline=headline,
        movements=movements,
        drivers=drivers,
        priority_action=priority_action,
        closing=closing,
    )


def _movement_line(label: str, change: float | None, *, unit: str) -> str:
    if change is None:
        return f"{label}: prior-month comparison unavailable."
    if abs(change) < _FLAT_BAND_PCT:
        return f"{label}: broadly flat MoM ({change:+.1f}{unit})."
    direction = "up" if change > 0 else "down"
    return f"{label}: {direction} {abs(change):.1f}{unit} MoM."


def _churn_line(change_pp: float | None) -> str:
    if change_pp is None:
        return "Churn rate: prior-month comparison unavailable."
    if abs(change_pp) < _CHURN_FLAT_PP:
        return f"Churn rate: stable MoM ({change_pp:+.2f} pp)."
    direction = "up" if change_pp > 0 else "down"
    return f"Churn rate: {direction} {abs(change_pp):.2f} pp MoM."


def _headline(
    *,
    period: str,
    rev_chg: float | None,
    arpu_chg: float | None,
    subs_chg: float | None,
    churn_pp: float | None,
) -> str:
    """Pick the dominant commercial story for the month."""
    # Dilution story: base grows while monetisation weakens.
    if (
        subs_chg is not None
        and arpu_chg is not None
        and subs_chg > _FLAT_BAND_PCT
        and arpu_chg < -_FLAT_BAND_PCT
    ):
        return (
            f"{period}: the base expanded while ARPU softened — "
            "growth is diluting monetisation."
        )
    # Retention risk.
    if churn_pp is not None and churn_pp > _CHURN_FLAT_PP:
        severity = "materially" if churn_pp >= 0.5 else "modestly"
        return (
            f"{period}: churn moved {severity} higher, putting "
            "retained revenue and high-value cohorts at risk."
        )
    # Revenue contraction.
    if rev_chg is not None and rev_chg < -_FLAT_BAND_PCT:
        return (
            f"{period}: top-line revenue contracted MoM — "
            "commercial focus should shift to recovery levers."
        )
    # Healthy expansion.
    if rev_chg is not None and rev_chg > _FLAT_BAND_PCT:
        return (
            f"{period}: revenue advanced MoM — "
            "protect the gains while testing where growth is thinning."
        )
    return (
        f"{period}: headline KPIs are largely steady MoM — "
        "use segment and regional views to find pockets of underperformance."
    )


def _closing(
    recommendations: list[Recommendation],
    *,
    rev_chg: float | None,
    churn_pp: float | None,
) -> str:
    if recommendations:
        top = recommendations[0]
        return (
            f"Priority for leadership: {top.priority} action owned by "
            f"{top.responsible_department} — {top.business_impact}"
        )
    if churn_pp is not None and churn_pp > _CHURN_FLAT_PP:
        return (
            "No rule-based priority fired, but rising churn warrants "
            "Retention review of at-risk and dormant cohorts."
        )
    if rev_chg is not None and rev_chg < -_FLAT_BAND_PCT:
        return (
            "No rule-based priority fired — Commercial should still "
            "diagnose product-mix and regional revenue gaps."
        )
    return (
        "No Critical/High rule fired for this month — maintain monitoring "
        "and dig into underperforming regions or value segments."
    )
