"""Named generation and analytics profiles."""

from __future__ import annotations

from datetime import date
from typing import Final, TypedDict

from src.config.settings import ProfileName


class ProfileDefaults(TypedDict):
    """Default configuration values for a named profile."""

    profile_name: ProfileName
    subscriber_count: int
    start_date: date
    end_date: date
    reporting_month: date
    batch_size: int
    random_seed: int


PROFILE_NAMES: Final[tuple[ProfileName, ...]] = (
    "development",
    "demo",
    "portfolio",
)

_PROFILES: Final[dict[ProfileName, ProfileDefaults]] = {
    "development": {
        "profile_name": "development",
        "subscriber_count": 10_000,
        "start_date": date(2024, 1, 1),
        "end_date": date(2025, 12, 31),
        "reporting_month": date(2025, 12, 1),
        "batch_size": 2_000,
        "random_seed": 42,
    },
    "demo": {
        "profile_name": "demo",
        "subscriber_count": 25_000,
        "start_date": date(2024, 1, 1),
        "end_date": date(2025, 12, 31),
        "reporting_month": date(2025, 12, 1),
        "batch_size": 5_000,
        "random_seed": 42,
    },
    "portfolio": {
        "profile_name": "portfolio",
        "subscriber_count": 100_000,
        "start_date": date(2024, 1, 1),
        "end_date": date(2025, 12, 31),
        "reporting_month": date(2025, 12, 1),
        "batch_size": 10_000,
        "random_seed": 42,
    },
}


def get_profile_defaults(profile_name: ProfileName) -> ProfileDefaults:
    """Return immutable-style defaults for a known profile.

    Args:
        profile_name: One of development, demo, or portfolio.

    Returns:
        ProfileDefaults for the requested profile.

    Raises:
        KeyError: If the profile name is not registered.
    """
    try:
        return dict(_PROFILES[profile_name])  # type: ignore[return-value]
    except KeyError as exc:
        valid = ", ".join(PROFILE_NAMES)
        raise KeyError(
            f"Unknown profile '{profile_name}'. Valid profiles: {valid}."
        ) from exc


def list_profiles() -> list[ProfileName]:
    """Return the ordered list of supported profile names."""
    return list(PROFILE_NAMES)
