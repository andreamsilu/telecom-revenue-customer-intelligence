"""Validation helpers for usage and recharge datasets."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src.generator.pricing import load_usage_rates
from src.validation.reference import ValidationReport

REQUIRED_USAGE_COLUMNS = (
    "usage_date",
    "customer_id",
    "voice_minutes",
    "sms_count",
    "data_mb",
    "international_minutes",
    "roaming_minutes",
    "vas_events",
    "voice_revenue",
    "sms_revenue",
    "data_revenue",
    "international_revenue",
    "roaming_revenue",
    "vas_revenue",
    "total_usage_revenue",
)

REQUIRED_RECHARGE_COLUMNS = (
    "recharge_id",
    "customer_id",
    "recharge_timestamp",
    "recharge_type",
    "recharge_channel",
    "amount",
    "bundle_category",
    "bundle_size",
    "validity_days",
    "promotion_id",
    "region",
)

USAGE_VOLUME_COLUMNS = (
    "voice_minutes",
    "sms_count",
    "data_mb",
    "international_minutes",
    "roaming_minutes",
    "vas_events",
)

USAGE_REVENUE_COLUMNS = (
    "voice_revenue",
    "sms_revenue",
    "data_revenue",
    "international_revenue",
    "roaming_revenue",
    "vas_revenue",
)


def validate_daily_usage(
    frame: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    *,
    revenue_tolerance: float = 0.05,
) -> ValidationReport:
    """Validate usage schema, non-negativity, keys, and revenue derivation."""
    report = ValidationReport("daily_usage")
    missing = [c for c in REQUIRED_USAGE_COLUMNS if c not in frame.columns]
    if missing:
        report.errors.append(f"Missing columns: {missing}")
        return report

    if frame.empty:
        report.errors.append("daily_usage is empty.")
        return report

    for column in (
        USAGE_VOLUME_COLUMNS + USAGE_REVENUE_COLUMNS + ("total_usage_revenue",)
    ):
        if (frame[column] < 0).any():
            report.errors.append(f"Negative values found in {column}.")

    valid_customers = set(customers["customer_id"].astype(str))
    orphans = set(frame["customer_id"].astype(str)) - valid_customers
    if orphans:
        report.errors.append(
            f"Usage customer_id orphans (sample): {sorted(orphans)[:5]}"
        )

    component_sum = frame[list(USAGE_REVENUE_COLUMNS)].sum(axis=1)
    mismatch = (component_sum - frame["total_usage_revenue"]).abs() > revenue_tolerance
    if bool(mismatch.any()):
        report.errors.append(
            f"total_usage_revenue does not equal component sum for "
            f"{int(mismatch.sum())} rows (tolerance={revenue_tolerance})."
        )

    # Spot-check revenue derivation on a sample against catalogue rates.
    rates = load_usage_rates(products)
    sample = frame.sample(n=min(50, len(frame)), random_state=42)
    for row in sample.itertuples(index=False):
        voice_minutes = float(str(row.voice_minutes))
        voice_revenue = float(str(row.voice_revenue))
        data_mb = float(str(row.data_mb))
        data_revenue = float(str(row.data_revenue))
        expected_voice = voice_minutes * rates.voice_per_minute
        if abs(expected_voice - voice_revenue) > revenue_tolerance:
            report.errors.append(
                "voice_revenue is not derived from voice_minutes * rate."
            )
            break
        expected_data = data_mb * rates.data_per_mb
        if abs(expected_data - data_revenue) > revenue_tolerance:
            report.errors.append("data_revenue is not derived from data_mb * rate.")
            break

    return report


def validate_recharges(
    frame: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> ValidationReport:
    """Validate recharge schema, amounts, uniqueness, and referential integrity."""
    report = ValidationReport("recharges")
    missing = [c for c in REQUIRED_RECHARGE_COLUMNS if c not in frame.columns]
    if missing:
        report.errors.append(f"Missing columns: {missing}")
        return report

    if frame.empty:
        report.errors.append("recharges is empty.")
        return report

    if frame["recharge_id"].duplicated().any():
        report.errors.append("Duplicate recharge_id values.")

    if (frame["amount"] <= 0).any():
        report.errors.append("Non-positive recharge amounts found.")

    valid_customers = set(customers["customer_id"].astype(str))
    orphans = set(frame["customer_id"].astype(str)) - valid_customers
    if orphans:
        report.errors.append(
            f"Recharge customer_id orphans (sample): {sorted(orphans)[:5]}"
        )

    if "product_id" in frame.columns:
        product_ids = set(products["product_id"].astype(str))
        linked = frame["product_id"].dropna().astype(str)
        bad = set(linked) - product_ids
        if bad:
            report.errors.append(
                f"Unknown product_id values on recharges: {sorted(bad)[:5]}"
            )

    valid_types = {
        "airtime",
        "data bundle",
        "voice bundle",
        "SMS bundle",
        "combo bundle",
    }
    invalid_types = set(frame["recharge_type"].astype(str)) - valid_types
    if invalid_types:
        report.errors.append(f"Invalid recharge_type values: {invalid_types}")

    return report


@dataclass
class SeasonalityCheck:
    """Simple seasonality comparison result."""

    december_mean: float
    january_mean: float
    ok: bool
    messages: list[str] = field(default_factory=list)


def check_usage_seasonality(frame: pd.DataFrame) -> SeasonalityCheck:
    """Verify December activity exceeds January for data usage intensity."""
    dates = pd.to_datetime(frame["usage_date"])
    december = frame.loc[dates.dt.month == 12, "data_mb"].mean()
    january = frame.loc[dates.dt.month == 1, "data_mb"].mean()
    messages: list[str] = []
    ok = True
    if pd.isna(december) or pd.isna(january):
        ok = False
        messages.append("Missing January or December usage rows.")
    elif float(december) <= float(january):
        ok = False
        messages.append(
            f"Expected December mean data_mb ({december:.2f}) > "
            f"January ({january:.2f})."
        )
    return SeasonalityCheck(
        december_mean=float(december) if pd.notna(december) else 0.0,
        january_mean=float(january) if pd.notna(january) else 0.0,
        ok=ok,
        messages=messages,
    )
