"""Campaign and regional KPI services."""

from __future__ import annotations

import pandas as pd

from src.analytics.comparisons import percent_change, safe_float
from src.analytics.helpers import as_percent, optional_float
from src.analytics.types import KpiResult


def campaign_kpi_summary(campaign_mart: pd.DataFrame) -> list[KpiResult]:
    """Summarise campaign portfolio KPIs (campaign grain, not month grain)."""
    if campaign_mart.empty:
        return []
    contacted = float(campaign_mart["customers_contacted"].sum())
    conversions = float(campaign_mart["conversions"].sum())
    revenue = float(campaign_mart["revenue_generated"].sum())
    cost = float(campaign_mart["campaign_cost"].sum())
    roi_pct = ((revenue - cost) / cost * 100.0) if cost else 0.0
    conversion_rate = as_percent(conversions / contacted) if contacted else 0.0
    return [
        KpiResult(
            name="Campaign Portfolio ROI",
            value=roi_pct,
            unit="%",
            reporting_month="campaign_portfolio",
            format_hint="rate",
        ),
        KpiResult(
            name="Campaign Conversion Rate",
            value=conversion_rate,
            unit="%",
            reporting_month="campaign_portfolio",
            format_hint="rate",
        ),
        KpiResult(
            name="Campaign Attributed Revenue",
            value=revenue,
            unit="TZS",
            reporting_month="campaign_portfolio",
            format_hint="currency",
        ),
    ]


def regional_kpi_cards(
    regional_mart: pd.DataFrame,
    reporting_month: str,
) -> list[KpiResult]:
    """Build top and lowest regional revenue KPI cards for a month."""
    month = pd.Timestamp(reporting_month).strftime("%Y-%m-%d")
    frame = regional_mart[regional_mart["reporting_month"].astype(str) == month]
    if frame.empty:
        return []
    top = frame.sort_values("total_revenue", ascending=False).iloc[0]
    bottom = frame.sort_values("total_revenue", ascending=True).iloc[0]
    top_prev = optional_float(top.get("total_revenue_previous_month_value"))
    return [
        KpiResult(
            name=f"Top Region Revenue ({top['region']})",
            value=safe_float(top["total_revenue"]),
            unit="TZS",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=percent_change(safe_float(top["total_revenue"]), top_prev),
            comparison_method="pct",
            format_hint="currency",
        ),
        KpiResult(
            name=f"Lowest Region Revenue ({bottom['region']})",
            value=safe_float(bottom["total_revenue"]),
            unit="TZS",
            reporting_month=month,
            format_hint="currency",
        ),
    ]
