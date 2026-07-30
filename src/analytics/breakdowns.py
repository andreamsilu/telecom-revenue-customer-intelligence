"""Presentation breakdowns derived from marts (pure analytics)."""

from __future__ import annotations

import pandas as pd


def filter_month_range(
    frame: pd.DataFrame,
    *,
    start_month: str,
    end_month: str,
    month_col: str = "reporting_month",
) -> pd.DataFrame:
    """Return rows whose month falls within an inclusive [start, end] range."""
    months = frame[month_col].astype(str)
    return frame[(months >= start_month) & (months <= end_month)].copy()


def regional_revenue_slice(
    regional_mart: pd.DataFrame,
    *,
    reporting_month: str,
    regions: list[str] | None = None,
) -> pd.DataFrame:
    """Slice regional revenue for a reporting month (optional region filter)."""
    month = pd.Timestamp(reporting_month).strftime("%Y-%m-%d")
    frame = regional_mart[regional_mart["reporting_month"].astype(str) == month].copy()
    if regions:
        frame = frame[frame["region"].isin(regions)]
    return frame[
        ["reporting_month", "region", "subscribers", "total_revenue", "arpu"]
    ].reset_index(drop=True)


def revenue_by_value_segment(
    segment_mart: pd.DataFrame,
    *,
    reporting_month: str,
) -> pd.DataFrame:
    """Return value-segment revenue for one reporting month from the segment mart."""
    month = pd.Timestamp(reporting_month).strftime("%Y-%m-%d")
    frame = segment_mart[segment_mart["reporting_month"].astype(str) == month]
    if frame.empty:
        return pd.DataFrame(columns=["value_segment", "total_revenue", "customers"])
    return (
        frame[["value_segment", "total_revenue", "customers"]]
        .sort_values("total_revenue", ascending=False)
        .reset_index(drop=True)
    )
