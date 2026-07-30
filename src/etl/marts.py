"""Build analytical monthly marts from snapshot and facts."""

from __future__ import annotations

from datetime import date

import pandas as pd

from src.etl.comparisons import add_monthly_comparisons
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _month_start_series(timestamps: pd.Series) -> pd.Series:
    """Normalize timestamps to month-start date strings."""
    values = pd.to_datetime(pd.Series(timestamps), errors="coerce")
    return pd.Series(
        [
            None
            if pd.isna(value)
            else date(int(value.year), int(value.month), 1).isoformat()
            for value in values
        ],
        index=values.index,
        dtype="object",
    )


def build_revenue_monthly_mart(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue metrics by reporting month."""
    grouped = (
        snapshot.groupby("reporting_month", as_index=False)
        .agg(
            total_revenue=("monthly_revenue", "sum"),
            voice_minutes=("monthly_voice_minutes", "sum"),
            sms_count=("monthly_sms_count", "sum"),
            data_mb=("monthly_data_mb", "sum"),
            recharge_value=("recharge_value", "sum"),
            mobile_money_transaction_value=("mobile_money_transaction_value", "sum"),
            active_subscribers=(
                "lifecycle_status",
                lambda s: int((s == "Active").sum()),
            ),
        )
        .sort_values("reporting_month")
    )
    grouped["arpu"] = grouped["total_revenue"] / grouped["active_subscribers"].clip(
        lower=1
    )
    mart = add_monthly_comparisons(
        grouped,
        month_col="reporting_month",
        value_cols=["total_revenue", "arpu", "data_mb", "recharge_value"],
    )
    logger.info("Built revenue_monthly_mart (%s rows)", f"{len(mart):,}")
    return mart


def build_subscriber_monthly_mart(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Aggregate subscriber and lifecycle counts by month."""
    grouped = snapshot.groupby("reporting_month", as_index=False).agg(
        total_subscribers=("customer_id", "nunique"),
        active_subscribers=("lifecycle_status", lambda s: int((s == "Active").sum())),
        at_risk_subscribers=("lifecycle_status", lambda s: int((s == "At Risk").sum())),
        dormant_subscribers=("lifecycle_status", lambda s: int((s == "Dormant").sum())),
        churned_subscribers=("lifecycle_status", lambda s: int((s == "Churned").sum())),
        reactivated_subscribers=(
            "lifecycle_status",
            lambda s: int((s == "Reactivated").sum()),
        ),
        new_subscribers=("newly_registered", "sum"),
    )
    grouped["active_rate"] = grouped["active_subscribers"] / grouped[
        "total_subscribers"
    ].clip(lower=1)
    mart = add_monthly_comparisons(
        grouped,
        month_col="reporting_month",
        value_cols=[
            "total_subscribers",
            "active_subscribers",
            "new_subscribers",
            "active_rate",
        ],
    )
    logger.info("Built subscriber_monthly_mart (%s rows)", f"{len(mart):,}")
    return mart


def build_churn_monthly_mart(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Build monthly churn rate building blocks and comparisons."""
    frame = snapshot.copy()
    frame["reporting_month"] = pd.to_datetime(frame["reporting_month"])
    frame = frame.sort_values(["customer_id", "reporting_month"])
    frame["was_active_prior"] = (
        frame.groupby("customer_id")["lifecycle_status"]
        .shift(1)
        .isin(["Active", "Reactivated"])
    )
    frame["_month"] = frame["reporting_month"].dt.strftime("%Y-%m-%d")

    base = frame.groupby("_month", as_index=False).agg(
        newly_churned=("newly_churned", "sum"),
        newly_reactivated=("newly_reactivated", "sum"),
        active_at_month_start=("was_active_prior", "sum"),
    )
    base = base.rename(columns={"_month": "reporting_month"})

    lost = (
        frame.loc[frame["newly_churned"]]
        .groupby("_month")["monthly_revenue"]
        .sum()
        .rename("revenue_lost_to_churn")
    )
    hv = (
        frame.loc[
            frame["newly_churned"]
            & frame["value_segment"].isin(["High Value", "Very High Value"])
        ]
        .groupby("_month")
        .size()
        .rename("high_value_churned")
    )
    mart = (
        base.merge(lost, left_on="reporting_month", right_index=True, how="left")
        .merge(hv, left_on="reporting_month", right_index=True, how="left")
        .fillna({"revenue_lost_to_churn": 0.0, "high_value_churned": 0})
    )
    mart["high_value_churned"] = mart["high_value_churned"].astype(int)
    mart["churn_rate"] = (
        100.0 * mart["newly_churned"] / mart["active_at_month_start"].clip(lower=1)
    )
    mart = add_monthly_comparisons(
        mart,
        month_col="reporting_month",
        value_cols=["churn_rate", "newly_churned", "revenue_lost_to_churn"],
    )
    logger.info("Built churn_monthly_mart (%s rows)", f"{len(mart):,}")
    return mart


def build_recharge_monthly_mart(recharges: pd.DataFrame) -> pd.DataFrame:
    """Aggregate recharge metrics by month."""
    frame = recharges.copy()
    frame["reporting_month"] = _month_start_series(frame["recharge_timestamp"])
    grouped = frame.groupby("reporting_month", as_index=False).agg(
        recharge_count=("recharge_id", "count"),
        total_recharge_value=("amount", "sum"),
        average_recharge_value=("amount", "mean"),
        unique_customers=("customer_id", "nunique"),
    )
    grouped["recharge_frequency"] = grouped["recharge_count"] / grouped[
        "unique_customers"
    ].clip(lower=1)
    mart = add_monthly_comparisons(
        grouped,
        month_col="reporting_month",
        value_cols=[
            "total_recharge_value",
            "recharge_count",
            "average_recharge_value",
            "recharge_frequency",
        ],
    )
    logger.info("Built recharge_monthly_mart (%s rows)", f"{len(mart):,}")
    return mart


def build_mobile_money_monthly_mart(mobile_money: pd.DataFrame) -> pd.DataFrame:
    """Aggregate mobile money metrics by month."""
    frame = mobile_money.copy()
    frame["reporting_month"] = _month_start_series(frame["transaction_timestamp"])
    success_mask = frame["transaction_status"] == "Successful"
    grouped = frame.groupby("reporting_month", as_index=False).agg(
        transaction_count=("transaction_id", "count"),
        successful_count=(
            "transaction_status",
            lambda s: int((s == "Successful").sum()),
        ),
        transaction_value=("amount", "sum"),
        fee_revenue=("fee_revenue", "sum"),
        active_users=("customer_id", "nunique"),
    )
    succ_val = (
        frame.loc[success_mask]
        .groupby(frame.loc[success_mask, "reporting_month"])["amount"]
        .sum()
        .rename("successful_transaction_value")
    )
    grouped = grouped.merge(
        succ_val, left_on="reporting_month", right_index=True, how="left"
    )
    grouped["successful_transaction_value"] = grouped[
        "successful_transaction_value"
    ].fillna(0.0)
    grouped["failed_transaction_rate"] = 1.0 - (
        grouped["successful_count"] / grouped["transaction_count"].clip(lower=1)
    )
    mart = add_monthly_comparisons(
        grouped,
        month_col="reporting_month",
        value_cols=[
            "transaction_value",
            "fee_revenue",
            "active_users",
            "failed_transaction_rate",
        ],
    )
    logger.info("Built mobile_money_monthly_mart (%s rows)", f"{len(mart):,}")
    return mart
