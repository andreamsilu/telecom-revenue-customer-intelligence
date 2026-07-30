"""Unit tests for usage revenue derivation and generation rules."""

from __future__ import annotations

import numpy as np
import pandas as pd
from src.config import load_settings
from src.generator import (
    generate_customers,
    generate_daily_usage,
    generate_products,
    generate_recharges,
    generate_regions,
)
from src.generator.pricing import derive_usage_revenue, load_usage_rates
from src.validation import (
    check_usage_seasonality,
    validate_daily_usage,
    validate_recharges,
)


def test_usage_revenue_derived_from_rates() -> None:
    """Component revenues equal volume × catalogue unit rates."""
    settings = load_settings(profile_name="development")
    rates = load_usage_rates(generate_products(settings))
    derived = derive_usage_revenue(
        voice_minutes=10,
        sms_count=4,
        data_mb=5,
        international_minutes=1,
        roaming_minutes=0.5,
        vas_events=1,
        rates=rates,
    )
    assert derived["voice_revenue"] == round(10 * rates.voice_per_minute, 2)
    assert derived["sms_revenue"] == round(4 * rates.sms_each, 2)
    assert derived["data_revenue"] == round(5 * rates.data_per_mb, 2)
    component_total = sum(
        derived[key]
        for key in (
            "voice_revenue",
            "sms_revenue",
            "data_revenue",
            "international_revenue",
            "roaming_revenue",
            "vas_revenue",
        )
    )
    assert abs(component_total - derived["total_usage_revenue"]) < 0.01


def test_usage_and_recharge_generation_small_base() -> None:
    """Small deterministic run validates integrity and behavioural differentials."""
    settings = load_settings(
        profile_name="development",
        subscriber_count=120,
        batch_size=60,
        random_seed=42,
    )
    regions = generate_regions()
    products = generate_products(settings)
    customers = generate_customers(settings, regions)
    rng_usage = np.random.default_rng(42 + 101)
    rng_recharge = np.random.default_rng(42 + 202)

    usage = generate_daily_usage(settings, customers, regions, products, rng=rng_usage)
    recharges = generate_recharges(settings, customers, products, rng=rng_recharge)

    usage_report = validate_daily_usage(usage, customers, products)
    assert usage_report.ok, usage_report.errors
    recharge_report = validate_recharges(recharges, customers, products)
    assert recharge_report.ok, recharge_report.errors

    seasonality = check_usage_seasonality(usage)
    assert seasonality.ok, seasonality.messages

    merged = usage.merge(
        customers[["customer_id", "region_id", "customer_segment"]],
        on="customer_id",
        how="left",
    ).merge(
        regions[["region_id", "urbanization_level"]],
        on="region_id",
        how="left",
    )
    urban_data = merged.loc[merged["urbanization_level"] == "urban", "data_mb"].mean()
    rural_data = merged.loc[merged["urbanization_level"] == "rural", "data_mb"].mean()
    urban_voice = merged.loc[
        merged["urbanization_level"] == "urban", "voice_minutes"
    ].mean()
    rural_voice = merged.loc[
        merged["urbanization_level"] == "rural", "voice_minutes"
    ].mean()
    assert urban_data > rural_data
    assert rural_voice > urban_voice

    youth_bundle_share = float(
        
            recharges.merge(
                customers[["customer_id", "customer_segment"]], on="customer_id"
            )
            .loc[lambda df: df["customer_segment"] == "Youth", "recharge_type"]
            .isin(["data bundle", "combo bundle"])
            .mean()
        
    )
    rural_airtime_share = float(
        
            recharges.merge(
                customers[["customer_id", "customer_segment"]], on="customer_id"
            )
            .loc[lambda df: df["customer_segment"] == "Rural", "recharge_type"]
            .eq("airtime")
            .mean()
        
    )
    assert youth_bundle_share > 0.40
    assert rural_airtime_share > 0.20


def test_usage_generation_is_deterministic() -> None:
    """Same seed reproduces identical usage frames."""
    settings = load_settings(
        profile_name="development",
        subscriber_count=40,
        batch_size=20,
        random_seed=7,
    )
    regions = generate_regions()
    products = generate_products(settings)
    customers = generate_customers(settings, regions)

    first = generate_daily_usage(
        settings,
        customers,
        regions,
        products,
        rng=np.random.default_rng(7 + 101),
    )
    second = generate_daily_usage(
        settings,
        customers,
        regions,
        products,
        rng=np.random.default_rng(7 + 101),
    )
    pd.testing.assert_frame_equal(first, second)
