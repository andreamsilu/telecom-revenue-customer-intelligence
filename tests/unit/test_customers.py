"""Unit tests for customer master generation."""

from __future__ import annotations

import pandas as pd
from src.config import load_settings
from src.generator import generate_customers, generate_regions
from src.validation import validate_customers


def test_customers_count_and_integrity() -> None:
    """Customer count matches profile and region references resolve."""
    settings = load_settings(profile_name="development", subscriber_count=500)
    regions = generate_regions()
    customers = generate_customers(settings, regions)
    report = validate_customers(customers, regions, expected_count=500)
    assert report.ok, report.errors
    assert customers["customer_id"].is_unique
    assert set(customers["customer_segment"]).issubset(
        {
            "Youth",
            "Mass Market",
            "High Value",
            "SME",
            "Corporate",
            "Rural",
            "Digital First",
        }
    )


def test_prepaid_dominates() -> None:
    """Prepaid accounts are the majority of the synthetic base."""
    settings = load_settings(profile_name="development", subscriber_count=2_000)
    customers = generate_customers(settings, generate_regions())
    prepaid_share = float((customers["account_type"] == "Prepaid").mean())
    assert prepaid_share >= 0.75


def test_urban_customers_prefer_data_oriented_segments() -> None:
    """Urban districts skew away from Rural segment relative to rural districts."""
    settings = load_settings(profile_name="development", subscriber_count=3_000)
    regions = generate_regions()
    customers = generate_customers(settings, regions)
    merged = customers.merge(
        regions[["region_id", "urbanization_level"]],
        on="region_id",
        how="left",
    )
    urban_rural_share = float(
        (
            merged.loc[merged["urbanization_level"] == "urban", "customer_segment"]
            == "Rural"
        ).mean()
    )
    rural_rural_share = float(
        (
            merged.loc[merged["urbanization_level"] == "rural", "customer_segment"]
            == "Rural"
        ).mean()
    )
    assert rural_rural_share > urban_rural_share


def test_customer_generation_is_deterministic() -> None:
    """Same seed and settings reproduce identical customer frames."""
    settings = load_settings(
        profile_name="development",
        subscriber_count=300,
        random_seed=42,
    )
    regions = generate_regions()
    first = generate_customers(settings, regions)
    second = generate_customers(settings, regions)
    pd.testing.assert_frame_equal(first, second)
