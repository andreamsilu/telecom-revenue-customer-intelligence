"""Unit tests for configuration loading and validation."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError
from src.config import list_profiles, load_settings
from src.config.settings import AppSettings


def test_load_settings_default_development() -> None:
    """Default profile settings load and resolve paths."""
    settings = load_settings(profile_name="development")
    assert settings.profile_name == "development"
    assert settings.subscriber_count == 10_000
    assert settings.start_date == date(2024, 1, 1)
    assert settings.end_date == date(2025, 12, 31)
    assert settings.reporting_month == date(2025, 12, 1)
    assert len(settings.period_month_starts()) == 24


def test_all_profiles_are_valid() -> None:
    """Each named profile produces a valid settings object."""
    profiles = list_profiles()
    assert profiles == ["development", "demo", "portfolio"]

    expected_subscribers = {
        "development": 10_000,
        "demo": 25_000,
        "portfolio": 100_000,
    }
    for name in profiles:
        settings = load_settings(profile_name=name)
        assert settings.profile_name == name
        assert settings.subscriber_count == expected_subscribers[name]
        assert len(settings.period_month_starts()) == 24


def test_invalid_subscriber_count_fails() -> None:
    """Non-positive subscriber counts are rejected."""
    with pytest.raises(ValidationError):
        AppSettings(subscriber_count=0)

    with pytest.raises(ValidationError):
        AppSettings(subscriber_count=-1)


def test_invalid_date_range_fails() -> None:
    """Start date must be strictly earlier than end date."""
    with pytest.raises(ValidationError):
        AppSettings(
            start_date=date(2025, 1, 1),
            end_date=date(2024, 12, 31),
            reporting_month=date(2024, 6, 1),
        )


def test_reporting_month_outside_range_fails() -> None:
    """Reporting month must fall inside the configured period."""
    with pytest.raises(ValidationError):
        AppSettings(
            start_date=date(2024, 1, 1),
            end_date=date(2025, 12, 31),
            reporting_month=date(2026, 1, 1),
        )


def test_period_must_contain_24_complete_months() -> None:
    """Historical window must span exactly 24 complete months."""
    with pytest.raises(ValidationError, match="24 complete months"):
        AppSettings(
            start_date=date(2024, 1, 1),
            end_date=date(2025, 6, 30),
            reporting_month=date(2025, 6, 1),
        )


def test_reporting_month_normalized_to_month_start() -> None:
    """Reporting month values are normalized to day 1."""
    settings = AppSettings(reporting_month=date(2025, 12, 15))
    assert settings.reporting_month == date(2025, 12, 1)


def test_load_settings_applies_overrides() -> None:
    """Explicit overrides replace profile defaults after validation."""
    settings = load_settings(
        profile_name="development",
        batch_size=1_500,
        random_seed=7,
    )
    assert settings.batch_size == 1_500
    assert settings.random_seed == 7
    assert settings.subscriber_count == 10_000
