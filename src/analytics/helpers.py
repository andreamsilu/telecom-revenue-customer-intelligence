"""Shared helpers for reading mart rows in KPI services."""

from __future__ import annotations

import pandas as pd

from src.analytics.comparisons import safe_float


def optional_float(value: object) -> float | None:
    """Return float or None when the cell is null/NaN."""
    number = safe_float(value, default=float("nan"))
    return None if number != number else number


def previous_month_value(
    frame: pd.DataFrame,
    reporting_month: str,
    column: str,
) -> float | None:
    """Lookup ``column`` on the prior calendar month row."""
    month_ts = pd.Timestamp(reporting_month)
    prev_month = (month_ts - pd.offsets.MonthBegin(1)).strftime("%Y-%m-%d")
    prev = frame[frame["reporting_month"].astype(str) == prev_month]
    if prev.empty or column not in prev.columns:
        return None
    return optional_float(prev.iloc[0][column])


def as_percent(rate_fraction: float) -> float:
    """Convert a 0–1 rate fraction to percent units."""
    return rate_fraction * 100.0
