"""Unit tests for mobile money fees and campaign targeting effects."""

from __future__ import annotations

import numpy as np
import pandas as pd
from src.config import load_settings
from src.generator import (
    generate_campaign_responses,
    generate_campaigns,
    generate_customers,
    generate_mobile_money,
    generate_products,
    generate_regions,
)
from src.generator.fee_bands import fee_for_amount
from src.validation import (
    validate_campaign_responses,
    validate_campaigns,
    validate_mobile_money,
)


def test_fee_bands_match_schedule() -> None:
    """Successful MM fees follow configured bands; airtime uses fixed fee."""
    assert fee_for_amount(800, transaction_type="Send Money") == 50.0
    assert fee_for_amount(3_000, transaction_type="Cash Out") == 100.0
    assert fee_for_amount(10_000, transaction_type="Merchant Payment") == 250.0
    assert fee_for_amount(1_500, transaction_type="Airtime Purchase") == 30.0


def test_mobile_money_and_campaigns_small_base() -> None:
    """Small deterministic run validates fees, integrity, and targeting effect."""
    settings = load_settings(
        profile_name="development",
        subscriber_count=400,
        batch_size=200,
        random_seed=42,
    )
    regions = generate_regions()
    products = generate_products(settings)
    customers = generate_customers(settings, regions)
    mm = generate_mobile_money(
        settings,
        customers,
        regions,
        rng=np.random.default_rng(42 + 303),
    )
    campaigns = generate_campaigns(settings)
    responses = generate_campaign_responses(
        settings,
        customers,
        campaigns,
        rng=np.random.default_rng(42 + 404),
    )

    mm_report = validate_mobile_money(mm, customers)
    assert mm_report.ok, mm_report.errors
    camp_report = validate_campaigns(campaigns, products)
    assert camp_report.ok, camp_report.errors
    resp_report = validate_campaign_responses(responses, customers, campaigns)
    assert resp_report.ok, resp_report.errors

    # SME customers should generate more MM volume on average.
    merged = mm.merge(customers[["customer_id", "customer_segment"]], on="customer_id")
    sme_rate = merged["customer_segment"].eq("SME").mean()
    base_sme_share = customers["customer_segment"].eq("SME").mean()
    assert sme_rate > base_sme_share

    rates = responses.groupby("targeting_relevance")["converted"].mean()
    assert rates.get("relevant", 0) > rates.get("irrelevant", 1)


def test_campaign_response_deterministic() -> None:
    """Same seed reproduces identical campaign response frames."""
    settings = load_settings(
        profile_name="development",
        subscriber_count=150,
        random_seed=9,
    )
    regions = generate_regions()
    customers = generate_customers(settings, regions)
    campaigns = generate_campaigns(settings)
    first = generate_campaign_responses(
        settings, customers, campaigns, rng=np.random.default_rng(9 + 404)
    )
    second = generate_campaign_responses(
        settings, customers, campaigns, rng=np.random.default_rng(9 + 404)
    )
    pd.testing.assert_frame_equal(first, second)
