"""Additional analytical marts: campaign, regional, and executive KPI."""

from __future__ import annotations

import pandas as pd

from src.etl.comparisons import add_monthly_comparisons
from src.utils.logging import get_logger

logger = get_logger(__name__)


def build_campaign_performance_mart(
    campaigns: pd.DataFrame,
    responses: pd.DataFrame,
) -> pd.DataFrame:
    """Build campaign-level attributable performance metrics."""
    if responses.empty:
        return pd.DataFrame()

    stats = responses.groupby("campaign_id", as_index=False).agg(
        customers_contacted=("contacted", "sum"),
        responses=("responded", "sum"),
        conversions=("converted", "sum"),
        revenue_generated=("revenue_generated", "sum"),
        retained_after_30_days=("retained_after_30_days", "sum"),
        churned_after_campaign=("churned_after_campaign", "sum"),
    )
    mart = campaigns.merge(stats, on="campaign_id", how="left").fillna(
        {
            "customers_contacted": 0,
            "responses": 0,
            "conversions": 0,
            "revenue_generated": 0.0,
            "retained_after_30_days": 0,
            "churned_after_campaign": 0,
        }
    )
    mart["response_rate"] = mart["responses"] / mart["customers_contacted"].clip(
        lower=1
    )
    mart["conversion_rate"] = mart["conversions"] / mart["customers_contacted"].clip(
        lower=1
    )
    mart["roi"] = (mart["revenue_generated"] - mart["campaign_cost"]) / mart[
        "campaign_cost"
    ].clip(lower=1)
    mart["cost_per_acquisition"] = mart["campaign_cost"] / mart["conversions"].clip(
        lower=1
    )
    logger.info("Built campaign_performance_mart (%s rows)", f"{len(mart):,}")
    return mart


def build_regional_performance_mart(
    snapshot: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate monthly performance by customer region."""
    frame = snapshot.merge(
        customers[["customer_id", "region"]],
        on="customer_id",
        how="left",
    )
    grouped = frame.groupby(["reporting_month", "region"], as_index=False).agg(
        subscribers=("customer_id", "nunique"),
        active_subscribers=("lifecycle_status", lambda s: int((s == "Active").sum())),
        total_revenue=("monthly_revenue", "sum"),
        newly_churned=("newly_churned", "sum"),
        data_mb=("monthly_data_mb", "sum"),
        recharge_value=("recharge_value", "sum"),
    )
    grouped["arpu"] = grouped["total_revenue"] / grouped["active_subscribers"].clip(
        lower=1
    )
    mart = add_monthly_comparisons(
        grouped,
        month_col="reporting_month",
        value_cols=["total_revenue", "subscribers", "arpu", "newly_churned"],
        partition_cols=["region"],
    )
    logger.info("Built regional_performance_mart (%s rows)", f"{len(mart):,}")
    return mart


def build_executive_kpi_mart(
    revenue_mart: pd.DataFrame,
    subscriber_mart: pd.DataFrame,
    churn_mart: pd.DataFrame,
    recharge_mart: pd.DataFrame,
    mm_mart: pd.DataFrame,
) -> pd.DataFrame:
    """Combine headline KPIs into one executive monthly mart."""
    mart = revenue_mart[
        [
            "reporting_month",
            "total_revenue",
            "arpu",
            "total_revenue_previous_month_value",
            "total_revenue_month_over_month_change",
            "total_revenue_prior_year_value",
            "total_revenue_year_over_year_change",
            "total_revenue_rolling_3_month_average",
            "total_revenue_year_to_date_value",
        ]
    ].merge(
        subscriber_mart[
            [
                "reporting_month",
                "total_subscribers",
                "active_subscribers",
                "new_subscribers",
                "active_rate",
            ]
        ],
        on="reporting_month",
        how="outer",
    )
    mart = mart.merge(
        churn_mart[
            [
                "reporting_month",
                "churn_rate",
                "newly_churned",
                "newly_reactivated",
                "revenue_lost_to_churn",
            ]
        ],
        on="reporting_month",
        how="outer",
    )
    mart = mart.merge(
        recharge_mart[
            [
                "reporting_month",
                "total_recharge_value",
                "average_recharge_value",
                "recharge_frequency",
            ]
        ],
        on="reporting_month",
        how="outer",
    )
    mart = mart.merge(
        mm_mart[
            [
                "reporting_month",
                "active_users",
                "fee_revenue",
                "transaction_value",
            ]
        ].rename(
            columns={
                "active_users": "mobile_money_active_users",
                "fee_revenue": "mobile_money_fee_revenue",
                "transaction_value": "mobile_money_transaction_value",
            }
        ),
        on="reporting_month",
        how="outer",
    )
    mart = mart.sort_values("reporting_month").reset_index(drop=True)
    logger.info("Built executive_kpi_mart (%s rows)", f"{len(mart):,}")
    return mart
