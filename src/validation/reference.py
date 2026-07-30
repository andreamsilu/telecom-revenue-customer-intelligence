"""Validation helpers for Phase 2 reference and customer datasets."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

REQUIRED_CALENDAR_COLUMNS = (
    "date",
    "day",
    "month",
    "month_name",
    "month_start",
    "quarter",
    "year",
    "day_of_week",
    "is_weekend",
    "is_month_end",
    "reporting_month",
    "seasonality_factor",
    "holiday_period_indicator",
)

REQUIRED_REGION_COLUMNS = (
    "region_id",
    "region_name",
    "district_name",
    "urbanization_level",
    "population_weight",
    "data_adoption_factor",
    "mobile_money_adoption_factor",
    "voice_usage_factor",
    "commercial_potential_factor",
)

REQUIRED_PRODUCT_COLUMNS = (
    "product_id",
    "product_name",
    "product_category",
    "service_type",
    "unit_price",
    "bundle_size",
    "validity_days",
    "target_segment",
    "active_from",
    "active_to",
)

REQUIRED_CUSTOMER_COLUMNS = (
    "customer_id",
    "registration_date",
    "region",
    "district",
    "gender",
    "age",
    "age_group",
    "occupation",
    "customer_segment",
    "account_type",
    "sim_type",
    "preferred_language",
    "acquisition_channel",
    "initial_status",
    "smartphone_indicator",
    "mobile_money_registered",
    "churn_date",
    "reactivation_date",
)

VALID_SEGMENTS = {
    "Youth",
    "Mass Market",
    "High Value",
    "SME",
    "Corporate",
    "Rural",
    "Digital First",
}

VALID_ACCOUNT_TYPES = {"Prepaid", "Postpaid"}
VALID_AGE_GROUPS = {"18-24", "25-34", "35-44", "45-54", "55+"}


@dataclass
class ValidationReport:
    """Structured validation outcome for a dataset."""

    dataset: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True when no critical errors were recorded."""
        return not self.errors


def _require_columns(
    frame: pd.DataFrame,
    required: tuple[str, ...],
    report: ValidationReport,
) -> None:
    missing = [col for col in required if col not in frame.columns]
    if missing:
        report.errors.append(f"Missing columns: {missing}")


def validate_calendar(frame: pd.DataFrame) -> ValidationReport:
    """Validate calendar schema and basic integrity."""
    report = ValidationReport("calendar")
    _require_columns(frame, REQUIRED_CALENDAR_COLUMNS, report)
    if report.errors:
        return report
    if frame["date"].duplicated().any():
        report.errors.append("Duplicate calendar dates found.")
    if frame.empty:
        report.errors.append("Calendar is empty.")
    return report


def validate_regions(frame: pd.DataFrame) -> ValidationReport:
    """Validate regions schema, uniqueness, and weight totals."""
    report = ValidationReport("regions")
    _require_columns(frame, REQUIRED_REGION_COLUMNS, report)
    if report.errors:
        return report
    if frame["region_id"].duplicated().any():
        report.errors.append("Duplicate region_id values.")
    weight_sum = float(frame["population_weight"].sum())
    if abs(weight_sum - 1.0) > 1e-4:
        report.errors.append(f"population_weight must sum to 1.0; found {weight_sum}.")
    urban_voice = frame.loc[
        frame["urbanization_level"] == "urban", "data_adoption_factor"
    ].mean()
    rural_voice = frame.loc[
        frame["urbanization_level"] == "rural", "voice_usage_factor"
    ].mean()
    rural_data = frame.loc[
        frame["urbanization_level"] == "rural", "data_adoption_factor"
    ].mean()
    if pd.notna(urban_voice) and pd.notna(rural_data) and urban_voice <= rural_data:
        report.warnings.append(
            "Expected urban data_adoption_factor > rural data_adoption_factor."
        )
    if pd.notna(rural_voice) and rural_voice <= 1.0:
        report.warnings.append("Rural voice_usage_factor is unexpectedly low.")
    return report


def validate_products(frame: pd.DataFrame) -> ValidationReport:
    """Validate product catalogue schema and price sanity."""
    report = ValidationReport("products")
    _require_columns(frame, REQUIRED_PRODUCT_COLUMNS, report)
    if report.errors:
        return report
    if frame["product_id"].duplicated().any():
        report.errors.append("Duplicate product_id values.")
    if (frame["unit_price"] < 0).any():
        report.errors.append("Negative unit_price values found.")
    categories = set(frame["product_category"].astype(str))
    expected = {
        "voice",
        "SMS",
        "data",
        "data_bundle",
        "voice_bundle",
        "SMS_bundle",
        "combo_bundle",
        "international",
        "roaming",
        "VAS",
        "mobile_money",
    }
    missing_cats = expected - categories
    if missing_cats:
        report.errors.append(f"Missing product categories: {sorted(missing_cats)}")
    return report


def validate_customers(
    frame: pd.DataFrame,
    regions: pd.DataFrame,
    *,
    expected_count: int | None = None,
) -> ValidationReport:
    """Validate customer master schema, counts, and referential integrity."""
    report = ValidationReport("customers")
    _require_columns(frame, REQUIRED_CUSTOMER_COLUMNS, report)
    if report.errors:
        return report

    if frame["customer_id"].duplicated().any():
        report.errors.append("Duplicate customer_id values.")
    if expected_count is not None and len(frame) != expected_count:
        report.errors.append(
            f"Expected {expected_count} customers; found {len(frame)}."
        )

    valid_region_ids = set(regions["region_id"].astype(str))
    if "region_id" in frame.columns:
        orphans = set(frame["region_id"].astype(str)) - valid_region_ids
        if orphans:
            report.errors.append(
                f"Customer region_id values missing from regions: {sorted(orphans)[:5]}"
            )

    region_districts = set(
        zip(
            regions["region_name"].astype(str),
            regions["district_name"].astype(str),
            strict=True,
        )
    )
    customer_pairs = set(
        zip(
            frame["region"].astype(str),
            frame["district"].astype(str),
            strict=True,
        )
    )
    bad_pairs = customer_pairs - region_districts
    if bad_pairs:
        report.errors.append(
            f"Customer region/district pairs not in regions reference: "
            f"{list(bad_pairs)[:5]}"
        )

    invalid_segments = set(frame["customer_segment"]) - VALID_SEGMENTS
    if invalid_segments:
        report.errors.append(f"Invalid customer_segment values: {invalid_segments}")

    invalid_accounts = set(frame["account_type"]) - VALID_ACCOUNT_TYPES
    if invalid_accounts:
        report.errors.append(f"Invalid account_type values: {invalid_accounts}")

    invalid_ages = set(frame["age_group"]) - VALID_AGE_GROUPS
    if invalid_ages:
        report.errors.append(f"Invalid age_group values: {invalid_ages}")

    prepaid_share = float((frame["account_type"] == "Prepaid").mean())
    if prepaid_share < 0.70:
        report.errors.append(
            f"Prepaid share {prepaid_share:.2%} is below expected dominance (>=70%)."
        )

    if frame["age"].min() < 18 or frame["age"].max() > 80:
        report.errors.append("Customer age outside expected bounds [18, 80].")

    return report
