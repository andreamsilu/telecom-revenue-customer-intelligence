"""Recommendation engine orchestrating deterministic rules."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from src.recommendations import rules as rule_module
from src.recommendations.models import Recommendation

PRIORITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def generate_recommendations(
    *,
    reporting_month: str,
    executive_mart: pd.DataFrame,
    revenue_mart: pd.DataFrame,
    subscriber_mart: pd.DataFrame,
    churn_mart: pd.DataFrame,
    recharge_mart: pd.DataFrame,
    regional_mart: pd.DataFrame,
    campaign_mart: pd.DataFrame,
) -> list[Recommendation]:
    """Run all recommendation rules and return sorted, deduplicated findings.

    Args:
        reporting_month: Month-start date (YYYY-MM-DD).
        executive_mart: Executive KPI mart.
        revenue_mart: Revenue monthly mart.
        subscriber_mart: Subscriber monthly mart.
        churn_mart: Churn monthly mart.
        recharge_mart: Recharge monthly mart.
        regional_mart: Regional performance mart.
        campaign_mart: Campaign performance mart.

    Returns:
        Deterministic list sorted by priority then recommendation_id.
    """
    month = pd.Timestamp(reporting_month).strftime("%Y-%m-%d")
    emitters: list[Callable[..., list[Recommendation]]] = [
        lambda: rule_module.rule_arpu_down_subscribers_up(executive_mart, month),
        lambda: rule_module.rule_subscribers_up_revenue_down(executive_mart, month),
        lambda: rule_module.rule_high_value_churn_elevated(churn_mart, month),
        lambda: rule_module.rule_data_growth_arpu_flat(revenue_mart, month),
        lambda: rule_module.rule_recharge_frequency_decline(recharge_mart, month),
        lambda: rule_module.rule_regional_subs_up_revenue_down(regional_mart, month),
        lambda: rule_module.rule_negative_campaign_roi(campaign_mart, month),
        lambda: rule_module.rule_high_conversion_weak_retention(campaign_mart, month),
        lambda: rule_module.rule_dormant_streak(subscriber_mart, month),
        lambda: rule_module.rule_churn_above_rolling_average(churn_mart, month),
    ]

    findings: list[Recommendation] = []
    seen: set[str] = set()
    for emit in emitters:
        for rec in emit():
            _validate_recommendation(rec)
            if rec.recommendation_id in seen:
                continue
            seen.add(rec.recommendation_id)
            findings.append(rec)

    findings.sort(key=lambda r: (PRIORITY_ORDER[r.priority], r.recommendation_id))
    return findings


def _validate_recommendation(rec: Recommendation) -> None:
    """Ensure required fields are populated (fail fast for bad rules)."""
    required: dict[str, Any] = {
        "recommendation_id": rec.recommendation_id,
        "reporting_period": rec.reporting_period,
        "module": rec.module,
        "finding": rec.finding,
        "metric_name": rec.metric_name,
        "business_impact": rec.business_impact,
        "recommended_action": rec.recommended_action,
        "priority": rec.priority,
        "responsible_department": rec.responsible_department,
    }
    missing = [name for name, value in required.items() if value in (None, "")]
    if missing:
        raise ValueError(f"Recommendation missing fields: {missing}")
    if rec.priority not in PRIORITY_ORDER:
        raise ValueError(f"Invalid priority: {rec.priority}")
