"""Executive and revenue KPI services."""

from __future__ import annotations

import pandas as pd

from src.analytics.comparisons import (
    percent_change,
    percentage_point_change,
    period_snapshot,
    safe_float,
)
from src.analytics.helpers import previous_month_value
from src.analytics.loaders import row_for_month
from src.analytics.types import KpiResult


def executive_kpi_cards(
    executive_mart: pd.DataFrame,
    reporting_month: str,
) -> list[KpiResult]:
    """Build executive KPI cards for a reporting month."""
    row = row_for_month(executive_mart, reporting_month)
    month = str(row["reporting_month"])
    revenue = period_snapshot(row, "total_revenue")
    arpu = safe_float(row["arpu"])
    arpu_prev = previous_month_value(executive_mart, month, "arpu")
    subs = safe_float(row["total_subscribers"])
    active = safe_float(row["active_subscribers"])
    # ETL stores churn_rate as percent units (100 * share of actives).
    churn = safe_float(row["churn_rate"])
    churn_prev = previous_month_value(executive_mart, month, "churn_rate")

    return [
        KpiResult(
            name="Total Revenue",
            value=safe_float(revenue["current"]),
            unit="TZS",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=revenue["mom_pct"],
            comparison_method="pct",
            format_hint="currency",
        ),
        KpiResult(
            name="ARPU",
            value=arpu,
            unit="TZS",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=percent_change(arpu, arpu_prev),
            comparison_method="pct",
            format_hint="currency",
        ),
        KpiResult(
            name="Total Subscribers",
            value=subs,
            unit="count",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=percent_change(
                subs,
                previous_month_value(executive_mart, month, "total_subscribers"),
            ),
            comparison_method="pct",
            format_hint="integer",
        ),
        KpiResult(
            name="Active Subscribers",
            value=active,
            unit="count",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=percent_change(
                active,
                previous_month_value(executive_mart, month, "active_subscribers"),
            ),
            comparison_method="pct",
            format_hint="integer",
        ),
        KpiResult(
            name="Churn Rate",
            value=churn,
            unit="%",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=percentage_point_change(churn, churn_prev),
            comparison_method="pp",
            format_hint="rate",
        ),
    ]


def revenue_kpi_cards(
    revenue_mart: pd.DataFrame,
    reporting_month: str,
) -> list[KpiResult]:
    """Build revenue-domain KPI cards including YoY and rolling context."""
    row = row_for_month(revenue_mart, reporting_month)
    month = str(row["reporting_month"])
    total = period_snapshot(row, "total_revenue")
    data = period_snapshot(row, "data_mb")
    recharge = period_snapshot(row, "recharge_value")
    return [
        KpiResult(
            name="Total Revenue",
            value=safe_float(total["current"]),
            unit="TZS",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=total["mom_pct"],
            comparison_method="pct",
            format_hint="currency",
        ),
        KpiResult(
            name="Total Revenue YoY",
            value=safe_float(total["current"]),
            unit="TZS",
            reporting_month=month,
            comparison_label="YoY",
            comparison_value=total["yoy_pct"],
            comparison_method="pct",
            format_hint="currency",
        ),
        KpiResult(
            name="Rolling 3-Month Revenue Avg",
            value=safe_float(total["rolling_3_month_average"] or 0.0),
            unit="TZS",
            reporting_month=month,
            format_hint="currency",
        ),
        KpiResult(
            name="YTD Revenue",
            value=safe_float(total["year_to_date_value"] or 0.0),
            unit="TZS",
            reporting_month=month,
            format_hint="currency",
        ),
        KpiResult(
            name="Data Usage Volume",
            value=safe_float(data["current"]),
            unit="MB",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=data["mom_pct"],
            comparison_method="pct",
            format_hint="number",
        ),
        KpiResult(
            name="Recharge Value",
            value=safe_float(recharge["current"]),
            unit="TZS",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=recharge["mom_pct"],
            comparison_method="pct",
            format_hint="currency",
        ),
    ]
