"""Unit tests for Phase 2 reference generators."""

from __future__ import annotations

from src.config import load_settings
from src.generator import (
    generate_calendar,
    generate_products,
    generate_regions,
)
from src.validation import (
    validate_calendar,
    validate_products,
    validate_regions,
)


def test_calendar_covers_full_period() -> None:
    """Calendar contains one row per day in the configured window."""
    settings = load_settings(profile_name="development")
    frame = generate_calendar(settings)
    assert len(frame) == (settings.end_date - settings.start_date).days + 1
    assert validate_calendar(frame).ok
    december = frame[frame["month"] == 12]["seasonality_factor"].mean()
    january = frame[frame["month"] == 1]["seasonality_factor"].mean()
    assert december > january


def test_regions_weights_and_urban_rural_split() -> None:
    """Region weights sum to 1 and urban data factor exceeds rural."""
    frame = generate_regions()
    report = validate_regions(frame)
    assert report.ok, report.errors
    urban_data = frame.loc[
        frame["urbanization_level"] == "urban", "data_adoption_factor"
    ].mean()
    rural_data = frame.loc[
        frame["urbanization_level"] == "rural", "data_adoption_factor"
    ].mean()
    rural_voice = frame.loc[
        frame["urbanization_level"] == "rural", "voice_usage_factor"
    ].mean()
    urban_voice = frame.loc[
        frame["urbanization_level"] == "urban", "voice_usage_factor"
    ].mean()
    assert urban_data > rural_data
    assert rural_voice > urban_voice
    assert set(frame["region_name"]).issuperset(
        {"Dar es Salaam", "Arusha", "Mwanza", "Dodoma"}
    )


def test_products_cover_required_categories() -> None:
    """Product catalogue includes all Version 1 service categories."""
    settings = load_settings(profile_name="development")
    frame = generate_products(settings)
    report = validate_products(frame)
    assert report.ok, report.errors
    assert frame["product_id"].is_unique
    assert (frame["unit_price"] >= 0).all()
