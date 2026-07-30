"""Build qualifying activity timelines from usage, recharges, and mobile money."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from src.utils.logging import get_logger

logger = get_logger(__name__)


def build_qualifying_activity(
    usage: pd.DataFrame,
    recharges: pd.DataFrame,
    mobile_money: pd.DataFrame,
) -> pd.DataFrame:
    """Return distinct qualifying activity dates per customer.

    Qualifying activity includes voice/SMS/data/international/roaming/VAS usage,
    any recharge, and successful mobile money transactions.
    """
    frames: list[pd.DataFrame] = []

    if not usage.empty:
        active_usage = usage[
            (usage["voice_minutes"] > 0)
            | (usage["sms_count"] > 0)
            | (usage["data_mb"] > 0)
            | (usage["international_minutes"] > 0)
            | (usage["roaming_minutes"] > 0)
            | (usage["vas_events"] > 0)
        ][["customer_id", "usage_date"]].copy()
        active_usage["activity_date"] = pd.to_datetime(
            active_usage["usage_date"]
        ).dt.normalize()
        frames.append(active_usage[["customer_id", "activity_date"]])

    if not recharges.empty:
        recharge_activity = recharges[["customer_id", "recharge_timestamp"]].copy()
        recharge_activity["activity_date"] = pd.to_datetime(
            recharge_activity["recharge_timestamp"]
        ).dt.normalize()
        frames.append(recharge_activity[["customer_id", "activity_date"]])

    if not mobile_money.empty:
        mm = mobile_money[mobile_money["transaction_status"] == "Successful"][
            ["customer_id", "transaction_timestamp"]
        ].copy()
        mm["activity_date"] = pd.to_datetime(mm["transaction_timestamp"]).dt.normalize()
        frames.append(mm[["customer_id", "activity_date"]])

    if not frames:
        return pd.DataFrame(columns=["customer_id", "activity_date"])

    activity = pd.concat(frames, ignore_index=True)
    activity["customer_id"] = activity["customer_id"].astype(str)
    activity = activity.drop_duplicates(
        subset=["customer_id", "activity_date"]
    ).sort_values(["customer_id", "activity_date"])
    logger.info(
        "Built qualifying activity timeline (%s customer-days)",
        f"{len(activity):,}",
    )
    return activity.reset_index(drop=True)


def select_attrition_cutoffs(
    customers: pd.DataFrame,
    recharges: pd.DataFrame,
    *,
    seed: int,
    attrition_rate: float = 0.14,
    earliest: date = date(2024, 6, 1),
    latest: date = date(2025, 6, 30),
) -> tuple[dict[str, date], dict[str, date]]:
    """Choose stop dates and optional return dates for engagement attrition.

    Returns:
        Tuple of (cutoff_by_customer, return_by_customer). Customers in
        ``return_by_customer`` resume activity on/after the return date,
        enabling Reactivated lifecycle states.
    """
    rng = np.random.default_rng(seed + 606)
    ids = customers["customer_id"].astype(str)
    recharge_counts = (
        recharges.groupby("customer_id").size()
        if not recharges.empty
        else pd.Series(dtype=int)
    )
    counts = ids.map(recharge_counts).fillna(0).astype(float)
    median = float(counts.median()) if len(counts) else 0.0
    weights = np.where(counts.to_numpy() <= median, 3.0, 1.0)
    weights = weights / weights.sum()

    n = max(1, int(round(attrition_rate * len(ids))))
    chosen = rng.choice(ids.to_numpy(), size=min(n, len(ids)), replace=False, p=weights)

    span_days = (latest - earliest).days
    cutoffs: dict[str, date] = {}
    returns: dict[str, date] = {}
    for customer_id in chosen:
        offset = int(rng.integers(0, span_days + 1))
        cutoff = earliest + timedelta(days=offset)
        cutoffs[str(customer_id)] = cutoff
        # ~30% return after at least 70 silent days (past churn threshold).
        if rng.random() < 0.30:
            gap = int(rng.integers(70, 120))
            return_date = cutoff + timedelta(days=gap)
            if return_date <= date(2025, 12, 15):
                returns[str(customer_id)] = return_date

    logger.info(
        "Selected %s attrition customers (%.1f%%), %s with return windows",
        f"{len(cutoffs):,}",
        100.0 * len(cutoffs) / max(len(ids), 1),
        f"{len(returns):,}",
    )
    return cutoffs, returns


def apply_attrition_cutoff(
    frame: pd.DataFrame,
    cutoffs: dict[str, date],
    returns: dict[str, date] | None = None,
    *,
    customer_col: str,
    timestamp_col: str,
) -> pd.DataFrame:
    """Drop rows in the silent window between cutoff and optional return."""
    if frame.empty or not cutoffs:
        return frame
    returns = returns or {}
    out = frame.copy()
    out["_customer_key"] = out[customer_col].astype(str)
    out["_ts"] = pd.to_datetime(out[timestamp_col]).dt.normalize()
    cutoff_series = out["_customer_key"].map(cutoffs)
    return_series = out["_customer_key"].map(returns)
    cutoff_ts = pd.to_datetime(cutoff_series)
    return_ts = pd.to_datetime(return_series)

    not_selected = cutoff_series.isna()
    before_cutoff = out["_ts"] <= cutoff_ts
    after_return = return_series.notna() & (out["_ts"] >= return_ts)
    keep = not_selected | before_cutoff | after_return
    trimmed = out.loc[keep].drop(columns=["_customer_key", "_ts"])
    return trimmed.reset_index(drop=True)
