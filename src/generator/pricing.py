"""Product rate lookup helpers for derived revenue calculations."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class UsageRates:
    """PAYG unit rates in TZS used to derive usage revenue."""

    voice_per_minute: float
    sms_each: float
    data_per_mb: float
    international_per_minute: float
    roaming_per_minute: float
    vas_event: float


def load_usage_rates(products: pd.DataFrame) -> UsageRates:
    """Extract usage unit rates from the product catalogue.

    Args:
        products: Product reference frame.

    Returns:
        UsageRates for revenue derivation.

    Raises:
        KeyError: If a required usage product is missing.
    """
    by_id = products.set_index("product_id")["unit_price"].to_dict()
    required = {
        "PRD-VOICE-PER-MIN": "voice_per_minute",
        "PRD-SMS-EACH": "sms_each",
        "PRD-DATA-PAYG-MB": "data_per_mb",
        "PRD-INTL-PER-MIN": "international_per_minute",
        "PRD-ROAM-PER-MIN": "roaming_per_minute",
        "PRD-VAS-RING": "vas_event",
    }
    values: dict[str, float] = {}
    for product_id, field_name in required.items():
        if product_id not in by_id:
            raise KeyError(f"Missing required product rate: {product_id}")
        values[field_name] = float(by_id[product_id])
    return UsageRates(**values)


def derive_usage_revenue(
    voice_minutes: float,
    sms_count: float,
    data_mb: float,
    international_minutes: float,
    roaming_minutes: float,
    vas_events: float,
    rates: UsageRates,
) -> dict[str, float]:
    """Derive component and total usage revenue from volumes and rates.

    Args:
        voice_minutes: Domestic voice minutes.
        sms_count: SMS count.
        data_mb: Data megabytes.
        international_minutes: International minutes.
        roaming_minutes: Roaming minutes.
        vas_events: VAS event count.
        rates: PAYG unit rates.

    Returns:
        Mapping of revenue component columns including total.
    """
    voice_revenue = voice_minutes * rates.voice_per_minute
    sms_revenue = sms_count * rates.sms_each
    data_revenue = data_mb * rates.data_per_mb
    international_revenue = international_minutes * rates.international_per_minute
    roaming_revenue = roaming_minutes * rates.roaming_per_minute
    # VAS catalogue price is monthly; treat each event as a day-rate proxy.
    vas_revenue = vas_events * (rates.vas_event / 30.0)
    total = (
        voice_revenue
        + sms_revenue
        + data_revenue
        + international_revenue
        + roaming_revenue
        + vas_revenue
    )
    return {
        "voice_revenue": round(voice_revenue, 2),
        "sms_revenue": round(sms_revenue, 2),
        "data_revenue": round(data_revenue, 2),
        "international_revenue": round(international_revenue, 2),
        "roaming_revenue": round(roaming_revenue, 2),
        "vas_revenue": round(vas_revenue, 2),
        "total_usage_revenue": round(total, 2),
    }
