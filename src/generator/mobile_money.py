"""Mobile money transaction generation with fee-band revenue."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from src.config.settings import AppSettings
from src.generator.fee_bands import fee_for_amount
from src.utils.logging import get_logger

logger = get_logger(__name__)

_TX_TYPES = (
    "Cash In",
    "Cash Out",
    "Send Money",
    "Merchant Payment",
    "Bill Payment",
    "Bank Transfer",
    "Airtime Purchase",
)

_TYPE_WEIGHTS = np.array([0.18, 0.16, 0.28, 0.12, 0.10, 0.06, 0.10], dtype=float)

_CHANNELS = ("USSD", "mobile application", "agent", "bank")
_CHANNEL_WEIGHTS = np.array([0.45, 0.30, 0.20, 0.05], dtype=float)

_MERCHANT_CATEGORIES = (
    None,
    "Grocery",
    "Transport",
    "Utilities",
    "Retail",
    "Fuel",
    "Education",
)

_SEGMENT_MONTHLY_MU = {
    "Youth": 1.5,
    "Mass Market": 2.0,
    "High Value": 3.0,
    "SME": 5.5,
    "Corporate": 3.5,
    "Rural": 1.2,
    "Digital First": 2.8,
}

_STATUSES = ("Successful", "Failed", "Reversed")
_STATUS_WEIGHTS = np.array([0.92, 0.06, 0.02], dtype=float)


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
    """Month-level MM activity weight."""
    return {
        1: 0.86,
        2: 0.95,
        3: 1.00,
        4: 1.02,
        5: 1.00,
        6: 1.03,
        7: 1.05,
        8: 1.04,
        9: 1.06,
        10: 1.05,
        11: 1.10,
        12: 1.30,
    }[month]


def iter_mobile_money_batches(
    settings: AppSettings,
    customers: pd.DataFrame,
    regions: pd.DataFrame,
    *,
    rng: np.random.Generator | None = None,
) -> Iterator[pd.DataFrame]:
    """Yield monthly mobile money batches for memory-conscious persistence."""
    base_rng = rng or np.random.default_rng(settings.random_seed + 303)
    prepared = customers.merge(
        regions[["region_id", "region_name", "mobile_money_adoption_factor"]],
        on="region_id",
        how="left",
        validate="many_to_one",
    )
    if prepared["mobile_money_adoption_factor"].isna().any():
        raise ValueError("Customers missing region mobile money factors.")

    prepared = prepared[
        [
            "customer_id",
            "registration_date",
            "customer_segment",
            "region",
            "mobile_money_registered",
            "mobile_money_adoption_factor",
        ]
    ].copy()
    prepared["registration_date"] = pd.to_datetime(
        prepared["registration_date"]
    ).dt.date
    prepared["mobile_money_registered"] = prepared["mobile_money_registered"].astype(
        bool
    )

    region_names = regions["region_name"].astype(str).unique().tolist()
    batch_size = settings.batch_size
    seq = 0

    for month_start in _month_starts(settings.start_date, settings.end_date):
        season = _seasonality(month_start.month)
        if month_start.month == 12:
            next_month = date(month_start.year + 1, 1, 1)
        else:
            next_month = date(month_start.year, month_start.month + 1, 1)
        month_end = min(next_month - timedelta(days=1), settings.end_date)
        logger.info("Generating mobile money for %s", month_start.isoformat())

        for start in range(0, len(prepared), batch_size):
            batch = prepared.iloc[start : start + batch_size]
            frame, seq = _generate_month_mm(
                batch,
                month_start=month_start,
                month_end=month_end,
                season=season,
                region_names=region_names,
                rng=base_rng,
                start_seq=seq,
            )
            if not frame.empty:
                yield frame


def generate_mobile_money(
    settings: AppSettings,
    customers: pd.DataFrame,
    regions: pd.DataFrame,
    *,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """Generate the full mobile money frame (prefer batch iteration for large runs)."""
    frames = list(iter_mobile_money_batches(settings, customers, regions, rng=rng))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _generate_month_mm(
    customers: pd.DataFrame,
    *,
    month_start: date,
    month_end: date,
    season: float,
    region_names: list[str],
    rng: np.random.Generator,
    start_seq: int,
) -> tuple[pd.DataFrame, int]:
    """Generate MM rows for one customer batch and month."""
    rows: list[dict[str, object]] = []
    seq = start_seq

    for customer in customers.itertuples(index=False):
        if not bool(customer.mobile_money_registered):
            # Small chance of first-time registration activity later omitted;
            # unregistered customers generate no MM transactions.
            continue

        reg_date: date = customer.registration_date  # type: ignore[assignment]
        if reg_date > month_end:
            continue
        effective_start = max(month_start, reg_date)
        local_span = (month_end - effective_start).days
        if local_span < 0:
            continue

        segment = str(customer.customer_segment)
        mu = (
            _SEGMENT_MONTHLY_MU.get(segment, 2.0)
            * float(str(customer.mobile_money_adoption_factor))
            * season
        )
        n_events = int(rng.poisson(mu))
        if n_events <= 0:
            continue

        for _ in range(n_events):
            # Month-end uplift: bias day selection toward last 5 days.
            if rng.random() < 0.35:
                day_offset = max(0, local_span - int(rng.integers(0, 5)))
            else:
                day_offset = int(rng.integers(0, local_span + 1))
            event_day = effective_start + timedelta(days=day_offset)
            timestamp = datetime(
                event_day.year,
                event_day.month,
                event_day.day,
                int(rng.integers(6, 22)),
                int(rng.integers(0, 60)),
                0,
            )

            tx_type = str(rng.choice(_TX_TYPES, p=_TYPE_WEIGHTS))
            amount = float(np.round(rng.lognormal(mean=9.2, sigma=0.85), 2))
            if segment == "SME":
                amount *= 1.35
            elif segment == "Rural":
                amount *= 0.75
            amount = max(500.0, float(np.round(amount, 2)))

            status = str(rng.choice(_STATUSES, p=_STATUS_WEIGHTS))
            fee = (
                fee_for_amount(amount, transaction_type=tx_type)
                if status == "Successful"
                else 0.0
            )

            merchant = None
            if tx_type == "Merchant Payment":
                merchant = str(
                    rng.choice([c for c in _MERCHANT_CATEGORIES if c is not None])
                )

            dest = str(customer.region)
            if tx_type == "Send Money" and rng.random() < 0.45:
                dest = str(rng.choice(region_names))

            seq += 1
            rows.append(
                {
                    "transaction_id": f"MM-{seq:010d}",
                    "customer_id": customer.customer_id,
                    "transaction_timestamp": timestamp.isoformat(sep=" "),
                    "transaction_type": tx_type,
                    "amount": amount,
                    "fee_revenue": fee,
                    "channel": str(rng.choice(_CHANNELS, p=_CHANNEL_WEIGHTS)),
                    "merchant_category": merchant,
                    "origin_region": customer.region,
                    "destination_region": dest,
                    "transaction_status": status,
                }
            )

    if not rows:
        return pd.DataFrame(), seq
    return pd.DataFrame(rows), seq
