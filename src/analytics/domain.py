"""Subscriber, retention, recharge, and mobile money KPI services."""

from __future__ import annotations

import pandas as pd

from src.analytics.comparisons import (
    percent_change,
    percentage_point_change,
    period_snapshot,
    safe_float,
)
from src.analytics.helpers import as_percent, optional_float, previous_month_value
from src.analytics.loaders import row_for_month
from src.analytics.types import KpiResult


def subscriber_kpi_cards(
    subscriber_mart: pd.DataFrame,
    reporting_month: str,
) -> list[KpiResult]:
    """Build subscriber KPI cards."""
    row = row_for_month(subscriber_mart, reporting_month)
    month = str(row["reporting_month"])
    total = period_snapshot(row, "total_subscribers")
    new_subs = period_snapshot(row, "new_subscribers")
    active_rate = as_percent(safe_float(row["active_rate"]))
    active_rate_prev = optional_float(row.get("active_rate_previous_month_value"))
    active_rate_prev_pct = (
        None if active_rate_prev is None else as_percent(active_rate_prev)
    )
    return [
        KpiResult(
            name="Total Subscribers",
            value=safe_float(total["current"]),
            unit="count",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=total["mom_pct"],
            comparison_method="pct",
            format_hint="integer",
        ),
        KpiResult(
            name="Active Rate",
            value=active_rate,
            unit="%",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=percentage_point_change(active_rate, active_rate_prev_pct),
            comparison_method="pp",
            format_hint="rate",
        ),
        KpiResult(
            name="New Subscribers",
            value=safe_float(new_subs["current"]),
            unit="count",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=new_subs["mom_pct"],
            comparison_method="pct",
            format_hint="integer",
        ),
    ]


def retention_kpi_cards(
    churn_mart: pd.DataFrame,
    reporting_month: str,
) -> list[KpiResult]:
    """Build retention/churn KPI cards (rates use percentage points)."""
    row = row_for_month(churn_mart, reporting_month)
    month = str(row["reporting_month"])
    churn = period_snapshot(row, "churn_rate")
    lost = period_snapshot(row, "revenue_lost_to_churn")
    hv = safe_float(row["high_value_churned"])
    # Rate MoM must use percentage points, not percent change.
    churn_pp = percentage_point_change(
        safe_float(churn["current"]),
        churn["previous_month"],
    )
    return [
        KpiResult(
            name="Churn Rate",
            value=safe_float(churn["current"]),
            unit="%",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=churn_pp,
            comparison_method="pp",
            format_hint="rate",
        ),
        KpiResult(
            name="Revenue Lost to Churn",
            value=safe_float(lost["current"]),
            unit="TZS",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=lost["mom_pct"],
            comparison_method="pct",
            format_hint="currency",
        ),
        KpiResult(
            name="High-Value Churned Customers",
            value=hv,
            unit="count",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=percent_change(
                hv,
                previous_month_value(churn_mart, month, "high_value_churned"),
            ),
            comparison_method="pct",
            format_hint="integer",
        ),
    ]


def recharge_kpi_cards(
    recharge_mart: pd.DataFrame,
    reporting_month: str,
) -> list[KpiResult]:
    """Build recharge KPI cards."""
    row = row_for_month(recharge_mart, reporting_month)
    month = str(row["reporting_month"])
    freq = period_snapshot(row, "recharge_frequency")
    avg_value = period_snapshot(row, "average_recharge_value")
    total = period_snapshot(row, "total_recharge_value")
    return [
        KpiResult(
            name="Recharge Frequency",
            value=safe_float(freq["current"]),
            unit="per active customer",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=freq["mom_pct"],
            comparison_method="pct",
            format_hint="number",
        ),
        KpiResult(
            name="Average Recharge Value",
            value=safe_float(avg_value["current"]),
            unit="TZS",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=avg_value["mom_pct"],
            comparison_method="pct",
            format_hint="currency",
        ),
        KpiResult(
            name="Total Recharge Value",
            value=safe_float(total["current"]),
            unit="TZS",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=total["mom_pct"],
            comparison_method="pct",
            format_hint="currency",
        ),
    ]


def mobile_money_kpi_cards(
    mm_mart: pd.DataFrame,
    reporting_month: str,
) -> list[KpiResult]:
    """Build mobile money KPI cards."""
    row = row_for_month(mm_mart, reporting_month)
    month = str(row["reporting_month"])
    users = period_snapshot(row, "active_users")
    fees = period_snapshot(row, "fee_revenue")
    fail_rate = as_percent(safe_float(row["failed_transaction_rate"]))
    fail_prev = optional_float(row.get("failed_transaction_rate_previous_month_value"))
    fail_prev_pct = None if fail_prev is None else as_percent(fail_prev)
    return [
        KpiResult(
            name="Mobile Money Active Users",
            value=safe_float(users["current"]),
            unit="count",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=users["mom_pct"],
            comparison_method="pct",
            format_hint="integer",
        ),
        KpiResult(
            name="Mobile Money Fee Revenue",
            value=safe_float(fees["current"]),
            unit="TZS",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=fees["mom_pct"],
            comparison_method="pct",
            format_hint="currency",
        ),
        KpiResult(
            name="Failed Transaction Rate",
            value=fail_rate,
            unit="%",
            reporting_month=month,
            comparison_label="MoM",
            comparison_value=percentage_point_change(fail_rate, fail_prev_pct),
            comparison_method="pp",
            format_hint="rate",
        ),
    ]
