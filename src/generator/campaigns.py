"""Synthetic marketing campaign catalogue generation."""

from __future__ import annotations

from datetime import date

import pandas as pd

from src.config.settings import AppSettings


def generate_campaigns(settings: AppSettings) -> pd.DataFrame:
    """Build the Version 1 campaign catalogue spanning the historical period.

    Args:
        settings: Application settings (period bounds for sanity).

    Returns:
        Campaigns DataFrame.
    """
    _ = settings  # period validated upstream; campaigns are fixed calendar events
    catalog: list[dict[str, object]] = [
        {
            "campaign_id": "CMP-2024-BTS",
            "campaign_name": "Back to School",
            "start_date": "2024-09-01",
            "end_date": "2024-09-30",
            "campaign_cost": 180_000_000.0,
            "target_segment": "Youth",
            "target_region": None,
            "campaign_channel": "SMS + Social",
            "promoted_product": "PRD-DATA-500MB-7D",
            "business_objective": "Acquire and grow youth data usage",
        },
        {
            "campaign_id": "CMP-2024-RAM",
            "campaign_name": "Ramadan",
            "start_date": "2024-03-10",
            "end_date": "2024-04-10",
            "campaign_cost": 220_000_000.0,
            "target_segment": "Mass Market",
            "target_region": None,
            "campaign_channel": "USSD + SMS",
            "promoted_product": "PRD-COMBO-DAILY",
            "business_objective": "Lift recharge and combo bundle uptake",
        },
        {
            "campaign_id": "CMP-2024-XMS",
            "campaign_name": "Christmas",
            "start_date": "2024-12-01",
            "end_date": "2024-12-31",
            "campaign_cost": 300_000_000.0,
            "target_segment": "Mass Market",
            "target_region": None,
            "campaign_channel": "App + SMS",
            "promoted_product": "PRD-DATA-5GB-30D",
            "business_objective": "Maximise December revenue and engagement",
        },
        {
            "campaign_id": "CMP-2025-DWE",
            "campaign_name": "Data Weekend",
            "start_date": "2025-05-01",
            "end_date": "2025-05-31",
            "campaign_cost": 95_000_000.0,
            "target_segment": "Digital First",
            "target_region": "Dar es Salaam",
            "campaign_channel": "Mobile App",
            "promoted_product": "PRD-DATA-1GB-7D",
            "business_objective": "Grow weekend data in urban digital segment",
        },
        {
            "campaign_id": "CMP-2025-STU",
            "campaign_name": "Student Offer",
            "start_date": "2025-02-01",
            "end_date": "2025-02-28",
            "campaign_cost": 110_000_000.0,
            "target_segment": "Youth",
            "target_region": None,
            "campaign_channel": "Campus + SMS",
            "promoted_product": "PRD-DATA-500MB-7D",
            "business_objective": "Retain students with affordable data",
        },
        {
            "campaign_id": "CMP-2025-SME",
            "campaign_name": "SME Promotion",
            "start_date": "2025-07-01",
            "end_date": "2025-07-31",
            "campaign_cost": 160_000_000.0,
            "target_segment": "SME",
            "target_region": None,
            "campaign_channel": "Dealer + Account Manager",
            "promoted_product": "PRD-COMBO-SME-30D",
            "business_objective": "Grow SME voice, data, and mobile money",
        },
        {
            "campaign_id": "CMP-2025-XMS",
            "campaign_name": "Christmas",
            "start_date": "2025-12-01",
            "end_date": "2025-12-31",
            "campaign_cost": 320_000_000.0,
            "target_segment": "High Value",
            "target_region": None,
            "campaign_channel": "App + SMS",
            "promoted_product": "PRD-DATA-15GB-30D",
            "business_objective": "Protect high-value December ARPU",
        },
        {
            "campaign_id": "CMP-2024-RUR",
            "campaign_name": "Rural Voice Boost",
            "start_date": "2024-06-01",
            "end_date": "2024-06-30",
            "campaign_cost": 75_000_000.0,
            "target_segment": "Rural",
            "target_region": "Tabora",
            "campaign_channel": "Dealer + USSD",
            "promoted_product": "PRD-VOICE-100-7D",
            "business_objective": "Stimulate rural voice recharge",
        },
    ]

    frame = pd.DataFrame(catalog)
    if frame["campaign_id"].duplicated().any():
        raise ValueError("Duplicate campaign_id values.")

    for _, row in frame.iterrows():
        start = date.fromisoformat(str(row["start_date"]))
        end = date.fromisoformat(str(row["end_date"]))
        if start > end:
            raise ValueError(f"Campaign {row['campaign_id']} has start after end.")
        if float(row["campaign_cost"]) <= 0:
            raise ValueError(f"Campaign {row['campaign_id']} cost must be positive.")

    return frame
