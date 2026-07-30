"""Validation helpers for ETL outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.generator.io import read_frame
from src.validation.reference import ValidationReport

REQUIRED_DIMS = (
    "dim_date",
    "dim_region",
    "dim_product",
    "dim_campaign",
    "dim_customer",
)
REQUIRED_FACTS = (
    "fact_usage_daily",
    "fact_recharge",
    "fact_mobile_money",
    "fact_campaign_response",
    "fact_customer_events",
)
REQUIRED_MARTS = (
    "customer_monthly_snapshot",
    "revenue_monthly_mart",
    "subscriber_monthly_mart",
    "churn_monthly_mart",
    "recharge_monthly_mart",
    "mobile_money_monthly_mart",
    "campaign_performance_mart",
    "regional_performance_mart",
    "executive_kpi_mart",
)

COMPARISON_SUFFIXES = (
    "_previous_month_value",
    "_month_over_month_change",
    "_prior_year_value",
    "_year_over_year_change",
    "_rolling_3_month_average",
    "_rolling_12_month_value",
    "_year_to_date_value",
)


def _load_processed(processed_dir: Path, name: str) -> pd.DataFrame:
    """Load a processed parquet/csv by stem name."""
    parquet = processed_dir / f"{name}.parquet"
    csv = processed_dir / f"{name}.csv"
    if parquet.exists():
        return read_frame(parquet)
    if csv.exists():
        return read_frame(csv)
    raise FileNotFoundError(f"Processed dataset not found: {name}")


def validate_processed_layer(
    processed_dir: Path,
    *,
    customers: pd.DataFrame,
    snapshot: pd.DataFrame,
) -> list[ValidationReport]:
    """Validate processed dimensions, facts, marts, and reconciliations."""
    reports: list[ValidationReport] = []

    existence = ValidationReport("processed_catalog")
    for name in (*REQUIRED_DIMS, *REQUIRED_FACTS, *REQUIRED_MARTS):
        parquet = processed_dir / f"{name}.parquet"
        csv = processed_dir / f"{name}.csv"
        if not parquet.exists() and not csv.exists():
            existence.errors.append(f"Missing processed dataset: {name}")
    reports.append(existence)
    if not existence.ok:
        return reports

    # Key uniqueness checks.
    key_report = ValidationReport("processed_keys")
    checks = {
        "dim_date": "date_key",
        "dim_region": "region_id",
        "dim_product": "product_id",
        "dim_campaign": "campaign_id",
        "dim_customer": "customer_id",
        "fact_recharge": "recharge_id",
        "fact_mobile_money": "transaction_id",
        "fact_customer_events": "event_id",
    }
    for name, key in checks.items():
        frame = _load_processed(processed_dir, name)
        if frame[key].duplicated().any():
            key_report.errors.append(f"{name}.{key} is not unique.")
    snap = _load_processed(processed_dir, "customer_monthly_snapshot")
    if snap.duplicated(subset=["reporting_month", "customer_id"]).any():
        key_report.errors.append("customer_monthly_snapshot grain is not unique.")
    reports.append(key_report)

    # Comparison columns present on revenue mart.
    comp_report = ValidationReport("mart_comparisons")
    revenue = _load_processed(processed_dir, "revenue_monthly_mart")
    for suffix in COMPARISON_SUFFIXES:
        col = f"total_revenue{suffix}"
        if col not in revenue.columns:
            comp_report.errors.append(f"revenue_monthly_mart missing {col}")
    reports.append(comp_report)

    # Revenue reconciliation: snapshot monthly totals vs revenue mart.
    recon = ValidationReport("revenue_reconciliation")
    snap_totals = (
        snapshot.groupby("reporting_month")["monthly_revenue"].sum().sort_index()
    )
    mart_totals = revenue.set_index("reporting_month")["total_revenue"].sort_index()
    aligned = snap_totals.align(mart_totals, join="inner")
    if aligned[0].empty:
        recon.errors.append("No overlapping months for revenue reconciliation.")
    else:
        delta = (aligned[0] - aligned[1]).abs().max()
        if float(delta) > 1.0:
            recon.errors.append(
                f"Revenue mart diverges from snapshot by up to {delta:.2f} TZS."
            )
    reports.append(recon)

    # Subscriber reconciliation.
    sub_report = ValidationReport("subscriber_reconciliation")
    subscribers = _load_processed(processed_dir, "subscriber_monthly_mart")
    snap_counts = snapshot.groupby("reporting_month")["customer_id"].nunique()
    mart_counts = subscribers.set_index("reporting_month")["total_subscribers"]
    aligned_s = snap_counts.align(mart_counts, join="inner")
    if (
        not aligned_s[0].empty
        and int((aligned_s[0] - aligned_s[1]).abs().max()) > 0
    ):
        sub_report.errors.append(
            "Subscriber mart counts do not match snapshot distinct customers."
        )
    reports.append(sub_report)

    # Referential: dim_customer covers customers.
    ref_report = ValidationReport("referential_integrity")
    dim_customer = _load_processed(processed_dir, "dim_customer")
    missing = set(customers["customer_id"].astype(str)) - set(
        dim_customer["customer_id"].astype(str)
    )
    if missing:
        ref_report.errors.append(f"dim_customer missing {len(missing)} customer_ids.")
    reports.append(ref_report)

    return reports
