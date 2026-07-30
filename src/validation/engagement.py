"""Validation helpers for mobile money and campaign datasets."""

from __future__ import annotations

import pandas as pd

from src.generator.fee_bands import fee_for_amount
from src.validation.reference import ValidationReport

REQUIRED_MM_COLUMNS = (
    "transaction_id",
    "customer_id",
    "transaction_timestamp",
    "transaction_type",
    "amount",
    "fee_revenue",
    "channel",
    "merchant_category",
    "origin_region",
    "destination_region",
    "transaction_status",
)

REQUIRED_CAMPAIGN_COLUMNS = (
    "campaign_id",
    "campaign_name",
    "start_date",
    "end_date",
    "campaign_cost",
    "target_segment",
    "target_region",
    "campaign_channel",
    "promoted_product",
    "business_objective",
)

REQUIRED_RESPONSE_COLUMNS = (
    "campaign_id",
    "customer_id",
    "contacted",
    "responded",
    "converted",
    "conversion_date",
    "revenue_generated",
    "pre_campaign_revenue",
    "campaign_period_revenue",
    "post_campaign_revenue",
    "retained_after_30_days",
    "churned_after_campaign",
)

VALID_MM_TYPES = {
    "Cash In",
    "Cash Out",
    "Send Money",
    "Merchant Payment",
    "Bill Payment",
    "Bank Transfer",
    "Airtime Purchase",
}

VALID_MM_STATUSES = {"Successful", "Failed", "Reversed"}


def validate_mobile_money(
    frame: pd.DataFrame,
    customers: pd.DataFrame,
) -> ValidationReport:
    """Validate MM schema, fees, statuses, and customer referential integrity."""
    report = ValidationReport("mobile_money_transactions")
    missing = [c for c in REQUIRED_MM_COLUMNS if c not in frame.columns]
    if missing:
        report.errors.append(f"Missing columns: {missing}")
        return report
    if frame.empty:
        report.errors.append("mobile_money_transactions is empty.")
        return report

    if frame["transaction_id"].duplicated().any():
        report.errors.append("Duplicate transaction_id values.")
    if (frame["amount"] < 0).any():
        report.errors.append("Negative MM amounts found.")
    if (frame["fee_revenue"] < 0).any():
        report.errors.append("Negative fee_revenue values found.")

    invalid_types = set(frame["transaction_type"].astype(str)) - VALID_MM_TYPES
    if invalid_types:
        report.errors.append(f"Invalid transaction_type values: {invalid_types}")

    invalid_status = set(frame["transaction_status"].astype(str)) - VALID_MM_STATUSES
    if invalid_status:
        report.errors.append(f"Invalid transaction_status values: {invalid_status}")

    orphans = set(frame["customer_id"].astype(str)) - set(
        customers["customer_id"].astype(str)
    )
    if orphans:
        report.errors.append(f"MM customer_id orphans (sample): {sorted(orphans)[:5]}")

    successful = frame[frame["transaction_status"] == "Successful"].head(100)
    for row in successful.itertuples(index=False):
        expected = fee_for_amount(
            float(str(row.amount)),
            transaction_type=str(row.transaction_type),
        )
        if abs(expected - float(str(row.fee_revenue))) > 0.01:
            report.errors.append(
                "fee_revenue does not match configured fee bands for "
                f"{row.transaction_id}."
            )
            break

    non_success = frame[frame["transaction_status"] != "Successful"]
    if not non_success.empty and (non_success["fee_revenue"] != 0).any():
        report.errors.append(
            "Non-successful MM transactions must have fee_revenue = 0."
        )

    return report


def validate_campaigns(
    frame: pd.DataFrame,
    products: pd.DataFrame,
) -> ValidationReport:
    """Validate campaign catalogue schema and product references."""
    report = ValidationReport("campaigns")
    missing = [c for c in REQUIRED_CAMPAIGN_COLUMNS if c not in frame.columns]
    if missing:
        report.errors.append(f"Missing columns: {missing}")
        return report
    if frame["campaign_id"].duplicated().any():
        report.errors.append("Duplicate campaign_id values.")
    if (frame["campaign_cost"] <= 0).any():
        report.errors.append("Non-positive campaign_cost values.")

    bad_products = set(frame["promoted_product"].astype(str)) - set(
        products["product_id"].astype(str)
    )
    if bad_products:
        report.errors.append(
            f"Unknown promoted_product values: {sorted(bad_products)[:5]}"
        )

    required_names = {
        "Back to School",
        "Ramadan",
        "Christmas",
        "Data Weekend",
        "Student Offer",
        "SME Promotion",
    }
    missing_names = required_names - set(frame["campaign_name"].astype(str))
    if missing_names:
        report.errors.append(f"Missing required campaigns: {sorted(missing_names)}")

    return report


def validate_campaign_responses(
    frame: pd.DataFrame,
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> ValidationReport:
    """Validate response schema, flag consistency, and referential integrity."""
    report = ValidationReport("campaign_responses")
    missing = [c for c in REQUIRED_RESPONSE_COLUMNS if c not in frame.columns]
    if missing:
        report.errors.append(f"Missing columns: {missing}")
        return report
    if frame.empty:
        report.errors.append("campaign_responses is empty.")
        return report

    orphans_c = set(frame["customer_id"].astype(str)) - set(
        customers["customer_id"].astype(str)
    )
    if orphans_c:
        report.errors.append(
            f"Response customer_id orphans (sample): {sorted(orphans_c)[:5]}"
        )

    orphans_cmp = set(frame["campaign_id"].astype(str)) - set(
        campaigns["campaign_id"].astype(str)
    )
    if orphans_cmp:
        report.errors.append(f"Response campaign_id orphans: {sorted(orphans_cmp)[:5]}")

    converted_without_response = frame["converted"] & ~frame["responded"]
    if converted_without_response.any():
        report.errors.append("converted=True requires responded=True.")

    responded_without_contact = frame["responded"] & ~frame["contacted"]
    if responded_without_contact.any():
        report.errors.append("responded=True requires contacted=True.")

    bad_revenue = frame["converted"] & (frame["revenue_generated"] <= 0)
    if bad_revenue.any():
        report.errors.append("converted rows must have positive revenue_generated.")

    return report
