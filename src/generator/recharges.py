"""Recharge event generation with catalogue-derived amounts."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from src.config.settings import AppSettings
from src.utils.logging import get_logger

logger = get_logger(__name__)

_CHANNELS = (
    "mobile money",
    "dealer",
    "bank",
    "mobile application",
    "USSD",
    "scratch card",
    "electronic recharge",
)

_CHANNEL_WEIGHTS = np.array([0.28, 0.22, 0.06, 0.14, 0.16, 0.08, 0.06], dtype=float)

# Segment → preferred recharge product_ids and relative weights.
_SEGMENT_PRODUCTS: dict[str, tuple[tuple[str, float], ...]] = {
    "Youth": (
        ("PRD-DATA-500MB-7D", 0.35),
        ("PRD-COMBO-DAILY", 0.25),
        ("PRD-DATA-1GB-7D", 0.15),
        ("AIRTIME", 0.20),
        ("PRD-SMS-100-7D", 0.05),
    ),
    "Mass Market": (
        ("AIRTIME", 0.30),
        ("PRD-DATA-1GB-7D", 0.25),
        ("PRD-DATA-5GB-30D", 0.15),
        ("PRD-VOICE-100-7D", 0.15),
        ("PRD-SMS-100-7D", 0.10),
        ("PRD-COMBO-DAILY", 0.05),
    ),
    "High Value": (
        ("PRD-DATA-15GB-30D", 0.35),
        ("PRD-DATA-5GB-30D", 0.25),
        ("AIRTIME", 0.20),
        ("PRD-COMBO-SME-30D", 0.10),
        ("PRD-VOICE-100-7D", 0.10),
    ),
    "SME": (
        ("PRD-COMBO-SME-30D", 0.35),
        ("AIRTIME", 0.25),
        ("PRD-DATA-5GB-30D", 0.20),
        ("PRD-VOICE-100-7D", 0.15),
        ("PRD-DATA-1GB-7D", 0.05),
    ),
    "Corporate": (
        ("PRD-CORP-PLAN", 0.55),
        ("AIRTIME", 0.20),
        ("PRD-DATA-15GB-30D", 0.15),
        ("PRD-COMBO-SME-30D", 0.10),
    ),
    "Rural": (
        ("AIRTIME", 0.35),
        ("PRD-VOICE-100-7D", 0.30),
        ("PRD-DATA-500MB-7D", 0.15),
        ("PRD-DATA-1GB-7D", 0.10),
        ("PRD-SMS-100-7D", 0.10),
    ),
    "Digital First": (
        ("PRD-DATA-5GB-30D", 0.30),
        ("PRD-DATA-1GB-7D", 0.25),
        ("PRD-DATA-15GB-30D", 0.15),
        ("AIRTIME", 0.15),
        ("PRD-COMBO-DAILY", 0.10),
        ("PRD-DATA-500MB-7D", 0.05),
    ),
}

_RECHARGE_TYPE_BY_CATEGORY = {
    "data_bundle": "data bundle",
    "voice_bundle": "voice bundle",
    "SMS_bundle": "SMS bundle",
    "combo_bundle": "combo bundle",
    "airtime": "airtime",
}

_AIRTIME_AMOUNTS = np.array([500, 1000, 2000, 5000, 10000, 20000], dtype=float)
_AIRTIME_WEIGHTS = np.array([0.15, 0.30, 0.25, 0.18, 0.08, 0.04], dtype=float)

_SEGMENT_MONTHLY_RECHARGE_MU = {
    "Youth": 2.2,
    "Mass Market": 2.5,
    "High Value": 3.2,
    "SME": 3.0,
    "Corporate": 2.0,
    "Rural": 1.8,
    "Digital First": 2.8,
}


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


def _seasonality(month: int) -> float:
    """Month-level recharge intensity."""
    return {
        1: 0.85,
        2: 0.95,
        3: 1.00,
        4: 1.02,
        5: 1.00,
        6: 1.03,
        7: 1.05,
        8: 1.04,
        9: 1.08,
        10: 1.05,
        11: 1.10,
        12: 1.28,
    }[month]


def iter_recharge_batches(
    settings: AppSettings,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    *,
    rng: np.random.Generator | None = None,
) -> Iterator[pd.DataFrame]:
    """Yield monthly recharge batches for memory-conscious persistence."""
    product_lookup: dict[str, dict[str, object]] = {
        str(product_id): {str(key): value for key, value in values.items()}
        for product_id, values in products.set_index("product_id")
        .to_dict(orient="index")
        .items()
    }
    base_rng = rng or np.random.default_rng(settings.random_seed + 202)
    prepared = customers[
        [
            "customer_id",
            "registration_date",
            "customer_segment",
            "region",
            "account_type",
        ]
    ].copy()
    prepared["registration_date"] = pd.to_datetime(
        prepared["registration_date"]
    ).dt.date
    batch_size = settings.batch_size
    recharge_seq = 0

    for month_start in _month_starts(settings.start_date, settings.end_date):
        season = _seasonality(month_start.month)
        if month_start.month == 12:
            next_month = date(month_start.year + 1, 1, 1)
        else:
            next_month = date(month_start.year, month_start.month + 1, 1)
        month_end = min(next_month - timedelta(days=1), settings.end_date)
        logger.info("Generating recharges for %s", month_start.isoformat())

        for start in range(0, len(prepared), batch_size):
            batch = prepared.iloc[start : start + batch_size]
            frame, recharge_seq = _generate_month_recharges(
                batch,
                month_start=month_start,
                month_end=month_end,
                season=season,
                product_lookup=product_lookup,
                rng=base_rng,
                start_seq=recharge_seq,
            )
            if not frame.empty:
                yield frame


def generate_recharges(
    settings: AppSettings,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    *,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """Generate the full recharges frame (prefer batch iteration for large runs)."""
    frames = list(iter_recharge_batches(settings, customers, products, rng=rng))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _generate_month_recharges(
    customers: pd.DataFrame,
    *,
    month_start: date,
    month_end: date,
    season: float,
    product_lookup: dict[str, dict[str, object]],
    rng: np.random.Generator,
    start_seq: int,
) -> tuple[pd.DataFrame, int]:
    """Generate recharge rows for one customer batch and month."""
    rows: list[dict[str, object]] = []
    seq = start_seq

    for customer in customers.itertuples(index=False):
        reg_date: date = customer.registration_date  # type: ignore[assignment]
        if reg_date > month_end:
            continue
        effective_start = max(month_start, reg_date)
        local_span = (month_end - effective_start).days
        if local_span < 0:
            continue

        segment = str(customer.customer_segment)
        mu = _SEGMENT_MONTHLY_RECHARGE_MU.get(segment, 2.0) * season
        if str(customer.account_type) == "Postpaid":
            mu *= 0.55
        n_events = int(rng.poisson(mu))
        if n_events <= 0:
            continue

        choices = _SEGMENT_PRODUCTS.get(segment, _SEGMENT_PRODUCTS["Mass Market"])
        product_ids = [item[0] for item in choices]
        weights = np.array([item[1] for item in choices], dtype=float)
        weights = weights / weights.sum()

        for _ in range(n_events):
            day_offset = int(rng.integers(0, local_span + 1))
            event_day = effective_start + timedelta(days=day_offset)
            hour = int(rng.integers(7, 22))
            minute = int(rng.integers(0, 60))
            timestamp = datetime(
                event_day.year, event_day.month, event_day.day, hour, minute, 0
            )

            product_id = str(rng.choice(product_ids, p=weights))
            channel = str(rng.choice(_CHANNELS, p=_CHANNEL_WEIGHTS))

            if product_id == "AIRTIME":
                amount = float(rng.choice(_AIRTIME_AMOUNTS, p=_AIRTIME_WEIGHTS))
                # Youth tend toward smaller airtime top-ups.
                if segment == "Youth" and amount > 5000:
                    amount = float(rng.choice(_AIRTIME_AMOUNTS[:4]))
                recharge_type = "airtime"
                bundle_category = None
                bundle_size = None
                validity_days = None
                promotion_id = None
            else:
                product = product_lookup[product_id]
                amount = float(product["unit_price"])  # type: ignore[arg-type]
                category = str(product["product_category"])
                recharge_type = _RECHARGE_TYPE_BY_CATEGORY.get(category, "combo bundle")
                bundle_category = category
                bundle_size = product["bundle_size"]
                validity_days = product["validity_days"]
                promotion_id = None

            seq += 1
            rows.append(
                {
                    "recharge_id": f"RCH-{seq:010d}",
                    "customer_id": customer.customer_id,
                    "recharge_timestamp": timestamp.isoformat(sep=" "),
                    "recharge_type": recharge_type,
                    "recharge_channel": channel,
                    "amount": round(amount, 2),
                    "bundle_category": bundle_category,
                    "bundle_size": bundle_size,
                    "validity_days": validity_days,
                    "promotion_id": promotion_id,
                    "region": customer.region,
                    "product_id": None if product_id == "AIRTIME" else product_id,
                }
            )

    if not rows:
        return pd.DataFrame(), seq
    return pd.DataFrame(rows), seq
