"""Synthetic Tanzanian region and district reference generation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RegionSpec:
    """Static specification for a synthetic operating region."""

    region_code: str
    region_name: str
    urbanization_level: str
    population_weight: float
    data_adoption_factor: float
    mobile_money_adoption_factor: float
    voice_usage_factor: float
    commercial_potential_factor: float
    districts: tuple[str, ...]


# Representative regions only — not real operator market share.
_REGION_SPECS: tuple[RegionSpec, ...] = (
    RegionSpec(
        "DAR",
        "Dar es Salaam",
        "urban",
        0.22,
        1.35,
        1.30,
        0.85,
        1.40,
        ("Ilala", "Kinondoni", "Temeke"),
    ),
    RegionSpec(
        "ARU",
        "Arusha",
        "urban",
        0.08,
        1.15,
        1.10,
        0.95,
        1.15,
        ("Arusha City", "Meru"),
    ),
    RegionSpec(
        "MWA",
        "Mwanza",
        "urban",
        0.10,
        1.10,
        1.15,
        0.98,
        1.12,
        ("Nyamagana", "Ilemela"),
    ),
    RegionSpec(
        "DOD",
        "Dodoma",
        "peri-urban",
        0.07,
        1.00,
        1.05,
        1.05,
        1.05,
        ("Dodoma City", "Bahi"),
    ),
    RegionSpec(
        "MBE",
        "Mbeya",
        "peri-urban",
        0.07,
        0.95,
        1.00,
        1.10,
        1.00,
        ("Mbeya City", "Rungwe"),
    ),
    RegionSpec(
        "MOR",
        "Morogoro",
        "peri-urban",
        0.06,
        0.92,
        0.98,
        1.12,
        0.95,
        ("Morogoro Urban", "Kilosa"),
    ),
    RegionSpec(
        "TAN",
        "Tanga",
        "peri-urban",
        0.06,
        0.90,
        0.95,
        1.15,
        0.92,
        ("Tanga City", "Muheza"),
    ),
    RegionSpec(
        "KIL",
        "Kilimanjaro",
        "peri-urban",
        0.06,
        1.05,
        1.00,
        1.00,
        1.08,
        ("Moshi Urban", "Hai"),
    ),
    RegionSpec(
        "KAG",
        "Kagera",
        "rural",
        0.07,
        0.75,
        0.85,
        1.25,
        0.80,
        ("Bukoba Urban", "Muleba"),
    ),
    RegionSpec(
        "MTW",
        "Mtwara",
        "rural",
        0.05,
        0.70,
        0.80,
        1.30,
        0.75,
        ("Mtwara Urban", "Newala"),
    ),
    RegionSpec(
        "GEI",
        "Geita",
        "rural",
        0.08,
        0.78,
        0.90,
        1.20,
        0.88,
        ("Geita Town", "Chato"),
    ),
    RegionSpec(
        "TAB",
        "Tabora",
        "rural",
        0.08,
        0.72,
        0.82,
        1.28,
        0.78,
        ("Tabora Urban", "Nzega"),
    ),
)


def generate_regions() -> pd.DataFrame:
    """Build the region/district reference table with behavioural factors.

    Returns:
        One row per synthetic district, keyed by ``region_id``.
    """
    total_weight = sum(spec.population_weight for spec in _REGION_SPECS)
    if abs(total_weight - 1.0) > 1e-6:
        raise ValueError(
            f"Region population weights must sum to 1.0; found {total_weight}."
        )

    rows: list[dict[str, object]] = []
    for spec in _REGION_SPECS:
        district_weight = spec.population_weight / len(spec.districts)
        for index, district in enumerate(spec.districts, start=1):
            # Slight within-region variation for district commercial feel.
            urban_boost = 1.0 + (0.03 if index == 1 else -0.01)
            rows.append(
                {
                    "region_id": f"{spec.region_code}-{index:02d}",
                    "region_code": spec.region_code,
                    "region_name": spec.region_name,
                    "district_name": district,
                    "urbanization_level": spec.urbanization_level,
                    "population_weight": round(district_weight, 6),
                    "data_adoption_factor": round(
                        spec.data_adoption_factor * urban_boost, 4
                    ),
                    "mobile_money_adoption_factor": round(
                        spec.mobile_money_adoption_factor * urban_boost, 4
                    ),
                    "voice_usage_factor": round(
                        spec.voice_usage_factor / urban_boost, 4
                    ),
                    "commercial_potential_factor": round(
                        spec.commercial_potential_factor * urban_boost, 4
                    ),
                }
            )

    frame = pd.DataFrame(rows)
    weight_sum = float(frame["population_weight"].sum())
    if abs(weight_sum - 1.0) > 1e-5:
        raise ValueError(
            f"District population weights must sum to 1.0; found {weight_sum}."
        )
    return frame
