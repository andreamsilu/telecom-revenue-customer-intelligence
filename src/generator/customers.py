"""Synthetic customer master-data generation."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from src.config.settings import AppSettings

_GENDERS = ("Female", "Male", "Other")
_LANGUAGES = ("Swahili", "English", "Swahili")  # Swahili-weighted
_ACQUISITION_CHANNELS = (
    "Dealer",
    "Retail Store",
    "USSD",
    "Mobile App",
    "Roadshow",
    "Corporate Sales",
)

_OCCUPATIONS_BY_SEGMENT: dict[str, tuple[str, ...]] = {
    "Youth": ("Student", "Unemployed", "Informal Trader", "Other"),
    "Mass Market": (
        "Informal Trader",
        "Salaried Employee",
        "Transport Worker",
        "Other",
        "Unemployed",
    ),
    "High Value": ("Professional", "Business Owner", "Salaried Employee"),
    "SME": ("Business Owner", "Informal Trader", "Professional"),
    "Corporate": ("Professional", "Public Servant", "Salaried Employee"),
    "Rural": ("Farmer", "Informal Trader", "Transport Worker", "Other"),
    "Digital First": (
        "Student",
        "Professional",
        "Salaried Employee",
        "Business Owner",
    ),
}

# Base segment mix; rural urbanization shifts mass toward Rural segment later.
_BASE_SEGMENT_WEIGHTS = np.array(
    [0.18, 0.34, 0.08, 0.10, 0.04, 0.14, 0.12],
    dtype=float,
)
_SEGMENTS = (
    "Youth",
    "Mass Market",
    "High Value",
    "SME",
    "Corporate",
    "Rural",
    "Digital First",
)


def _age_group(age: int) -> str:
    """Map age to the standard age-group band."""
    if age <= 24:
        return "18-24"
    if age <= 34:
        return "25-34"
    if age <= 44:
        return "35-44"
    if age <= 54:
        return "45-54"
    return "55+"


def _segment_weights_for_urbanization(level: str) -> list[float]:
    """Adjust segment mix by urbanization level."""
    weights = _BASE_SEGMENT_WEIGHTS.copy()
    if level == "urban":
        weights[5] *= 0.35  # Rural
        weights[6] *= 1.40  # Digital First
        weights[2] *= 1.25  # High Value
        weights[4] *= 1.50  # Corporate
    elif level == "rural":
        weights[5] *= 2.20  # Rural
        weights[6] *= 0.45
        weights[4] *= 0.35
        weights[0] *= 0.80  # Youth slightly lower
    else:  # peri-urban
        weights[5] *= 1.20
        weights[3] *= 1.15  # SME
    normalized = weights / weights.sum()
    return [float(value) for value in normalized]


def _sample_age(rng: np.random.Generator, segment: str) -> int:
    """Sample age consistent with segment."""
    if segment == "Youth":
        return int(rng.integers(18, 26))
    if segment == "Corporate":
        return int(rng.integers(28, 56))
    if segment == "High Value":
        return int(rng.integers(30, 58))
    if segment == "SME":
        return int(rng.integers(25, 55))
    if segment == "Rural":
        return int(rng.integers(22, 60))
    return int(rng.integers(18, 60))


def _registration_date(
    rng: np.random.Generator,
    start: date,
    end: date,
) -> date:
    """Sample registration date with more acquisitions earlier in the window."""
    span_days = (end - start).days
    # Beta skew toward earlier tenure while still allowing late joins.
    u = float(rng.beta(1.4, 2.2))
    offset = int(u * span_days)
    return start + timedelta(days=offset)


def generate_customers(
    settings: AppSettings,
    regions: pd.DataFrame,
) -> pd.DataFrame:
    """Generate the synthetic customer master for the active profile.

    Args:
        settings: Validated settings including subscriber count and seed.
        regions: Region/district reference frame from ``generate_regions``.

    Returns:
        Customer master DataFrame with one row per subscriber.
    """
    if regions.empty:
        raise ValueError("regions frame must not be empty.")

    rng = np.random.default_rng(settings.random_seed)
    n = settings.subscriber_count

    region_weights = regions["population_weight"].to_numpy(dtype=float)
    region_weights = region_weights / region_weights.sum()
    region_indices = rng.choice(len(regions), size=n, p=region_weights)
    selected = regions.iloc[region_indices].reset_index(drop=True)

    records: list[dict[str, object]] = []
    for i in range(n):
        urbanization = str(selected["urbanization_level"].iloc[i])
        segment = str(
            rng.choice(_SEGMENTS, p=_segment_weights_for_urbanization(urbanization))
        )
        age = _sample_age(rng, segment)
        occupations = _OCCUPATIONS_BY_SEGMENT[segment]
        occupation = str(rng.choice(occupations))

        prepaid_prob = {
            "Corporate": 0.25,
            "High Value": 0.55,
            "SME": 0.70,
            "Digital First": 0.82,
            "Youth": 0.95,
            "Mass Market": 0.92,
            "Rural": 0.96,
        }[segment]
        account_type = "Prepaid" if rng.random() < prepaid_prob else "Postpaid"

        esim_prob = 0.18 if urbanization == "urban" else 0.05
        if segment in {"Digital First", "Corporate", "High Value"}:
            esim_prob += 0.10
        sim_type = "eSIM" if rng.random() < esim_prob else "Physical SIM"

        smartphone_prob = {
            "urban": 0.78,
            "peri-urban": 0.62,
            "rural": 0.42,
        }[urbanization]
        if segment in {"Digital First", "Youth", "Corporate", "High Value"}:
            smartphone_prob = min(0.95, smartphone_prob + 0.12)
        smartphone = bool(rng.random() < smartphone_prob)

        mm_prob = float(selected["mobile_money_adoption_factor"].iloc[i]) * 0.55
        if segment in {"SME", "High Value", "Corporate"}:
            mm_prob = min(0.95, mm_prob + 0.15)
        if segment == "Rural":
            mm_prob *= 0.85
        mm_registered = bool(rng.random() < min(0.95, mm_prob))

        channel_probs = np.array([0.30, 0.22, 0.18, 0.12, 0.10, 0.08], dtype=float)
        if segment == "Corporate":
            channel_probs = np.array([0.10, 0.15, 0.05, 0.15, 0.05, 0.50])
        elif segment == "Digital First":
            channel_probs = np.array([0.10, 0.10, 0.25, 0.40, 0.10, 0.05])
        channel_probs = channel_probs / channel_probs.sum()
        channel = str(rng.choice(_ACQUISITION_CHANNELS, p=channel_probs))

        reg_date = _registration_date(rng, settings.start_date, settings.end_date)

        records.append(
            {
                "customer_id": f"CUST-{i + 1:07d}",
                "registration_date": reg_date.isoformat(),
                "region": str(selected["region_name"].iloc[i]),
                "district": str(selected["district_name"].iloc[i]),
                "region_id": str(selected["region_id"].iloc[i]),
                "gender": str(rng.choice(_GENDERS, p=[0.49, 0.49, 0.02])),
                "age": age,
                "age_group": _age_group(age),
                "occupation": occupation,
                "customer_segment": segment,
                "account_type": account_type,
                "sim_type": sim_type,
                "preferred_language": str(rng.choice(_LANGUAGES)),
                "acquisition_channel": channel,
                "initial_status": "Active",
                "smartphone_indicator": smartphone,
                "mobile_money_registered": mm_registered,
                "churn_date": None,
                "reactivation_date": None,
            }
        )

    frame = pd.DataFrame.from_records(records)
    if frame["customer_id"].duplicated().any():
        raise ValueError("Duplicate customer_id values generated.")
    if len(frame) != n:
        raise ValueError(f"Expected {n} customers; generated {len(frame)}.")
    return frame
