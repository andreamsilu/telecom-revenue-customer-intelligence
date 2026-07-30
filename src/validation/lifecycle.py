"""Validation helpers for lifecycle snapshots and customer events."""

from __future__ import annotations

import pandas as pd

from src.generator.lifecycle import status_from_inactivity
from src.validation.reference import ValidationReport

REQUIRED_SNAPSHOT_COLUMNS = (
    "reporting_month",
    "customer_id",
    "lifecycle_status",
    "last_activity_date",
    "inactivity_days",
    "monthly_revenue",
    "rolling_3_month_revenue",
    "monthly_voice_minutes",
    "monthly_sms_count",
    "monthly_data_mb",
    "recharge_count",
    "recharge_value",
    "mobile_money_active",
    "mobile_money_transaction_value",
    "newly_registered",
    "newly_churned",
    "newly_reactivated",
    "tenure_months",
    "value_segment",
)

REQUIRED_EVENT_COLUMNS = (
    "event_id",
    "customer_id",
    "event_timestamp",
    "event_type",
    "event_channel",
    "region",
    "related_transaction_id",
    "event_value",
)

VALID_STATUSES = {"Active", "At Risk", "Dormant", "Churned", "Reactivated"}
VALID_VALUE_SEGMENTS = {
    "Low Value",
    "Medium Value",
    "High Value",
    "Very High Value",
}
VALID_EVENT_TYPES = {
    "SIM Registration",
    "SIM Swap",
    "Bundle Purchase",
    "Airtime Recharge",
    "Mobile Money Usage",
    "Complaint",
    "Churn",
    "Reactivation",
}


def validate_snapshot(
    frame: pd.DataFrame,
    customers: pd.DataFrame,
) -> ValidationReport:
    """Validate snapshot grain, status consistency, and referential integrity."""
    report = ValidationReport("customer_monthly_snapshot")
    missing = [c for c in REQUIRED_SNAPSHOT_COLUMNS if c not in frame.columns]
    if missing:
        report.errors.append(f"Missing columns: {missing}")
        return report
    if frame.empty:
        report.errors.append("customer_monthly_snapshot is empty.")
        return report

    if frame.duplicated(subset=["reporting_month", "customer_id"]).any():
        report.errors.append("Snapshot grain must be one row per customer per month.")

    orphans = set(frame["customer_id"].astype(str)) - set(
        customers["customer_id"].astype(str)
    )
    if orphans:
        report.errors.append(f"Snapshot customer orphans: {sorted(orphans)[:5]}")

    invalid_status = set(frame["lifecycle_status"]) - VALID_STATUSES
    if invalid_status:
        report.errors.append(f"Invalid lifecycle_status values: {invalid_status}")

    invalid_value = set(frame["value_segment"]) - VALID_VALUE_SEGMENTS
    if invalid_value:
        report.errors.append(f"Invalid value_segment values: {invalid_value}")

    # Status must match inactivity for non-reactivated rows.
    sample = frame[frame["lifecycle_status"] != "Reactivated"].head(500)
    for row in sample.itertuples(index=False):
        expected = status_from_inactivity(int(str(row.inactivity_days)))
        if expected != row.lifecycle_status:
            report.errors.append(
                f"Status mismatch for {row.customer_id} @ {row.reporting_month}: "
                f"inactivity={row.inactivity_days} status={row.lifecycle_status} "
                f"expected={expected}."
            )
            break

    reactivated = frame[frame["lifecycle_status"] == "Reactivated"]
    if not reactivated.empty and (reactivated["inactivity_days"] > 30).any():
        report.errors.append("Reactivated rows must have inactivity_days <= 30.")

    return report


def validate_customer_events(
    frame: pd.DataFrame,
    customers: pd.DataFrame,
) -> ValidationReport:
    """Validate customer event schema and keys."""
    report = ValidationReport("customer_events")
    missing = [c for c in REQUIRED_EVENT_COLUMNS if c not in frame.columns]
    if missing:
        report.errors.append(f"Missing columns: {missing}")
        return report
    if frame.empty:
        report.errors.append("customer_events is empty.")
        return report
    if frame["event_id"].duplicated().any():
        report.errors.append("Duplicate event_id values.")

    orphans = set(frame["customer_id"].astype(str)) - set(
        customers["customer_id"].astype(str)
    )
    if orphans:
        report.errors.append(f"Event customer orphans: {sorted(orphans)[:5]}")

    invalid_types = set(frame["event_type"].astype(str)) - VALID_EVENT_TYPES
    if invalid_types:
        report.errors.append(f"Invalid event_type values: {invalid_types}")

    return report
