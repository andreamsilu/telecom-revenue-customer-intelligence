"""Daily usage generation with derived revenue."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date, timedelta

import numpy as np
import pandas as pd

from src.config.settings import AppSettings
from src.generator.pricing import UsageRates, load_usage_rates
from src.utils.logging import get_logger

logger = get_logger(__name__)

_SEGMENT_MULTIPLIERS: dict[str, dict[str, float]] = {
    "Youth": {
        "voice": 0.70,
        "sms": 1.25,
        "data": 1.35,
        "intl": 0.40,
        "roam": 0.20,
        "vas": 1.40,
        "active_days": 12,
    },
    "Mass Market": {
        "voice": 1.00,
        "sms": 1.00,
        "data": 1.00,
        "intl": 0.50,
        "roam": 0.25,
        "vas": 0.80,
        "active_days": 11,
    },
    "High Value": {
        "voice": 1.20,
        "sms": 0.90,
        "data": 1.50,
        "intl": 1.40,
        "roam": 1.10,
        "vas": 0.70,
        "active_days": 16,
    },
    "SME": {
        "voice": 1.55,
        "sms": 1.15,
        "data": 0.95,
        "intl": 0.90,
        "roam": 0.60,
        "vas": 0.50,
        "active_days": 15,
    },
    "Corporate": {
        "voice": 1.35,
        "sms": 0.85,
        "data": 1.45,
        "intl": 1.60,
        "roam": 2.00,
        "vas": 0.40,
        "active_days": 18,
    },
    "Rural": {
        "voice": 1.45,
        "sms": 0.85,
        "data": 0.55,
        "intl": 0.25,
        "roam": 0.10,
        "vas": 0.45,
        "active_days": 9,
    },
    "Digital First": {
        "voice": 0.75,
        "sms": 0.95,
        "data": 1.70,
        "intl": 0.70,
        "roam": 0.50,
        "vas": 1.10,
        "active_days": 14,
    },
}

_CONSUMER_SEGMENTS = {"Youth", "Mass Market", "Rural", "Digital First"}


def _month_starts(start: date, end: date) -> list[date]:
    """Return first day of each month in the inclusive period."""
    months: list[date] = []
    current = start.replace(day=1)
    last = end.replace(day=1)
    while current <= last:
        months.append(current)
        year = current.year + (1 if current.month == 12 else 0)
        month = 1 if current.month == 12 else current.month + 1
        current = date(year, month, 1)
    return months


def _days_in_month(month_start: date, period_end: date) -> list[date]:
    """Return calendar days in month clipped to the configured end date."""
    if month_start.month == 12:
        next_month = date(month_start.year + 1, 1, 1)
    else:
        next_month = date(month_start.year, month_start.month + 1, 1)
    last_day = min(next_month - timedelta(days=1), period_end)
    days: list[date] = []
    current = month_start
    while current <= last_day:
        days.append(current)
        current += timedelta(days=1)
    return days


def _seasonality(month: int) -> float:
    """Month-level activity weight."""
    return {
        1: 0.88,
        2: 0.95,
        3: 1.00,
        4: 1.02,
        5: 1.00,
        6: 1.03,
        7: 1.05,
        8: 1.04,
        9: 1.06,
        10: 1.05,
        11: 1.08,
        12: 1.22,
    }[month]


def _trend_factors(month_start: date, period_start: date) -> tuple[float, float]:
    """Return (data_trend, voice_trend) based on months since period start."""
    months_elapsed = (month_start.year - period_start.year) * 12 + (
        month_start.month - period_start.month
    )
    data_trend = 1.0 + 0.035 * months_elapsed
    voice_trend = max(0.75, 1.0 - 0.008 * months_elapsed)
    return data_trend, voice_trend


def prepare_customer_usage_frame(
    customers: pd.DataFrame,
    regions: pd.DataFrame,
) -> pd.DataFrame:
    """Merge customers with regional behavioural factors for usage generation."""
    cols = [
        "customer_id",
        "registration_date",
        "customer_segment",
        "region_id",
        "account_type",
    ]
    missing = [c for c in cols if c not in customers.columns]
    if missing:
        raise ValueError(f"customers missing columns: {missing}")

    merged = customers[cols].merge(
        regions[
            [
                "region_id",
                "data_adoption_factor",
                "voice_usage_factor",
                "urbanization_level",
            ]
        ],
        on="region_id",
        how="left",
        validate="many_to_one",
    )
    if merged["data_adoption_factor"].isna().any():
        raise ValueError("Some customers have region_id values missing from regions.")
    merged["registration_date"] = pd.to_datetime(merged["registration_date"]).dt.date
    return merged


def iter_usage_batches(
    settings: AppSettings,
    customers: pd.DataFrame,
    regions: pd.DataFrame,
    products: pd.DataFrame,
    *,
    rng: np.random.Generator | None = None,
) -> Iterator[pd.DataFrame]:
    """Yield monthly usage batches for memory-conscious persistence.

    Only active usage days are emitted (sparse daily grain), not a full
    customer-day panel.
    """
    rates = load_usage_rates(products)
    base_rng = rng or np.random.default_rng(settings.random_seed + 101)
    prepared = prepare_customer_usage_frame(customers, regions)
    batch_size = settings.batch_size

    for month_start in _month_starts(settings.start_date, settings.end_date):
        month_days = _days_in_month(month_start, settings.end_date)
        season = _seasonality(month_start.month)
        data_trend, voice_trend = _trend_factors(month_start, settings.start_date)
        logger.info(
            "Generating usage for %s (%s days)",
            month_start.isoformat(),
            len(month_days),
        )

        for start in range(0, len(prepared), batch_size):
            batch = prepared.iloc[start : start + batch_size]
            frame = _generate_month_batch(
                batch,
                month_days=month_days,
                season=season,
                data_trend=data_trend,
                voice_trend=voice_trend,
                rates=rates,
                rng=base_rng,
            )
            if not frame.empty:
                yield frame


def generate_daily_usage(
    settings: AppSettings,
    customers: pd.DataFrame,
    regions: pd.DataFrame,
    products: pd.DataFrame,
    *,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """Generate the full daily usage frame (prefer batch iteration for large runs)."""
    frames = list(iter_usage_batches(settings, customers, regions, products, rng=rng))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _generate_month_batch(
    customers: pd.DataFrame,
    *,
    month_days: list[date],
    season: float,
    data_trend: float,
    voice_trend: float,
    rates: UsageRates,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate sparse daily usage rows for one customer batch and month."""
    if customers.empty or not month_days:
        return pd.DataFrame()

    weekday_flags = np.array([d.weekday() >= 5 for d in month_days], dtype=bool)
    day_labels = np.array([d.isoformat() for d in month_days])
    month_day_dates = np.array(month_days, dtype=object)

    customer_ids: list[str] = []
    day_indices: list[int] = []
    voice_mults: list[float] = []
    sms_mults: list[float] = []
    data_mults: list[float] = []
    intl_mults: list[float] = []
    roam_mults: list[float] = []
    vas_mults: list[float] = []
    data_factors: list[float] = []
    voice_factors: list[float] = []
    is_consumer: list[bool] = []
    is_business: list[bool] = []

    for customer in customers.itertuples(index=False):
        reg_date: date = customer.registration_date  # type: ignore[assignment]
        eligible_idx = np.flatnonzero(month_day_dates >= reg_date)
        if eligible_idx.size == 0:
            continue

        segment = str(customer.customer_segment)
        mult = _SEGMENT_MULTIPLIERS.get(segment, _SEGMENT_MULTIPLIERS["Mass Market"])
        n_active = int(
            np.clip(rng.poisson(mult["active_days"] * season), 1, eligible_idx.size)
        )
        chosen = rng.choice(eligible_idx, size=n_active, replace=False)

        customer_ids.extend([str(customer.customer_id)] * n_active)
        day_indices.extend(chosen.tolist())
        voice_mults.extend([mult["voice"]] * n_active)
        sms_mults.extend([mult["sms"]] * n_active)
        data_mults.extend([mult["data"]] * n_active)
        intl_mults.extend([mult["intl"]] * n_active)
        roam_mults.extend([mult["roam"]] * n_active)
        vas_mults.extend([mult["vas"]] * n_active)
        data_factor = float(str(customer.data_adoption_factor))
        voice_factor = float(str(customer.voice_usage_factor))
        data_factors.extend([data_factor] * n_active)
        voice_factors.extend([voice_factor] * n_active)
        is_consumer.extend([segment in _CONSUMER_SEGMENTS] * n_active)
        is_business.extend([segment in {"SME", "Corporate"}] * n_active)

    if not customer_ids:
        return pd.DataFrame()

    n_rows = len(customer_ids)
    day_idx = np.asarray(day_indices, dtype=int)
    is_weekend = weekday_flags[day_idx]
    consumer = np.asarray(is_consumer, dtype=bool)
    business = np.asarray(is_business, dtype=bool)

    weekend_data = np.where(is_weekend & consumer, 1.20, 1.0)
    weekday_biz = np.where((~is_weekend) & business, 1.25, 1.0)

    voice_minutes = np.maximum(
        0.0,
        rng.lognormal(mean=2.4, sigma=0.55, size=n_rows)
        * np.asarray(voice_mults)
        * np.asarray(voice_factors)
        * voice_trend
        * season
        * weekday_biz,
    )
    sms_count = rng.poisson(
        np.maximum(0.1, np.asarray(sms_mults) * 6.0 * season)
    ).astype(int)
    data_mb = np.maximum(
        0.0,
        rng.lognormal(mean=4.0, sigma=0.70, size=n_rows)
        * np.asarray(data_mults)
        * np.asarray(data_factors)
        * data_trend
        * season
        * weekend_data,
    )

    intl_mult_arr = np.asarray(intl_mults)
    roam_mult_arr = np.asarray(roam_mults)
    vas_mult_arr = np.asarray(vas_mults)
    intl = np.where(
        rng.random(n_rows) < (0.08 * intl_mult_arr),
        rng.exponential(1.5, size=n_rows) * intl_mult_arr * season,
        0.0,
    )
    roam = np.where(
        rng.random(n_rows) < (0.03 * roam_mult_arr),
        rng.exponential(2.0, size=n_rows) * roam_mult_arr * season,
        0.0,
    )
    vas_events = (rng.random(n_rows) < (0.05 * vas_mult_arr)).astype(int)

    voice_minutes = np.round(voice_minutes, 2)
    data_mb = np.round(data_mb, 2)
    intl = np.round(intl, 2)
    roam = np.round(roam, 2)

    voice_revenue = np.round(voice_minutes * rates.voice_per_minute, 2)
    sms_revenue = np.round(sms_count * rates.sms_each, 2)
    data_revenue = np.round(data_mb * rates.data_per_mb, 2)
    international_revenue = np.round(intl * rates.international_per_minute, 2)
    roaming_revenue = np.round(roam * rates.roaming_per_minute, 2)
    vas_revenue = np.round(vas_events * (rates.vas_event / 30.0), 2)
    total_usage_revenue = np.round(
        voice_revenue
        + sms_revenue
        + data_revenue
        + international_revenue
        + roaming_revenue
        + vas_revenue,
        2,
    )

    return pd.DataFrame(
        {
            "usage_date": day_labels[day_idx],
            "customer_id": customer_ids,
            "voice_minutes": voice_minutes,
            "sms_count": sms_count,
            "data_mb": data_mb,
            "international_minutes": intl,
            "roaming_minutes": roam,
            "vas_events": vas_events,
            "voice_revenue": voice_revenue,
            "sms_revenue": sms_revenue,
            "data_revenue": data_revenue,
            "international_revenue": international_revenue,
            "roaming_revenue": roaming_revenue,
            "vas_revenue": vas_revenue,
            "total_usage_revenue": total_usage_revenue,
        }
    )
