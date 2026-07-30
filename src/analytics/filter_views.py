"""Apply dashboard filters to analytical marts (pure functions, no Streamlit)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.analytics.breakdowns import filter_month_range
from src.analytics.types import KpiResult


@dataclass(frozen=True)
class FilterSelection:
    """Minimal filter fields used by analytics (avoids importing Streamlit types)."""

    reporting_month: str
    start_month: str
    end_month: str
    regions: tuple[str, ...] = ()
    value_segments: tuple[str, ...] = ()
    account_types: tuple[str, ...] = ()
    product_categories: tuple[str, ...] = ()

    @property
    def has_dimension_filters(self) -> bool:
        return bool(
            self.regions
            or self.value_segments
            or self.account_types
            or self.product_categories
        )

    @property
    def regional_scope(self) -> bool:
        return bool(self.regions)


def apply_regional_filter(
    regional_mart: pd.DataFrame,
    selection: FilterSelection,
) -> pd.DataFrame:
    """Filter regional mart by optional regions (all months retained)."""
    frame = regional_mart.copy()
    if selection.regions:
        frame = frame[frame["region"].astype(str).isin(selection.regions)]
    return frame.reset_index(drop=True)


def apply_segment_filter(
    segment_mart: pd.DataFrame,
    selection: FilterSelection,
) -> pd.DataFrame:
    """Filter value-segment mart by optional value segments."""
    frame = segment_mart.copy()
    if selection.value_segments:
        frame = frame[frame["value_segment"].astype(str).isin(selection.value_segments)]
    return frame.reset_index(drop=True)


def apply_campaign_filters(
    campaign_mart: pd.DataFrame,
    selection: FilterSelection,
) -> pd.DataFrame:
    """Filter campaigns by target region, target segment, and promoted product."""
    frame = campaign_mart.copy()
    if selection.regions and "target_region" in frame.columns:
        frame = frame[
            frame["target_region"].astype(str).isin(selection.regions)
            | frame["target_region"].isna()
        ]
    if selection.value_segments and "target_segment" in frame.columns:
        # Campaign target_segment may use marketing labels; keep loose contains match.
        mask = frame["target_segment"].isna()
        for seg in selection.value_segments:
            mask = mask | frame["target_segment"].astype(str).str.contains(
                seg, case=False, na=False
            )
        frame = frame[mask]
    if selection.product_categories and "promoted_product" in frame.columns:
        mask = pd.Series(False, index=frame.index)
        for product in selection.product_categories:
            mask = mask | frame["promoted_product"].astype(str).str.contains(
                product, case=False, na=False
            )
        frame = frame[mask]
    return frame.reset_index(drop=True)


def regional_month_slice(
    regional_mart: pd.DataFrame,
    selection: FilterSelection,
) -> pd.DataFrame:
    """Regional rows for the reporting month after region filter."""
    month = pd.Timestamp(selection.reporting_month).strftime("%Y-%m-%d")
    frame = apply_regional_filter(regional_mart, selection)
    frame = frame[frame["reporting_month"].astype(str) == month]
    cols = [
        c
        for c in (
            "reporting_month",
            "region",
            "subscribers",
            "active_subscribers",
            "total_revenue",
            "newly_churned",
            "data_mb",
            "recharge_value",
            "arpu",
        )
        if c in frame.columns
    ]
    return frame[cols].reset_index(drop=True)


def segment_month_slice(
    segment_mart: pd.DataFrame,
    selection: FilterSelection,
) -> pd.DataFrame:
    """Value-segment rows for the reporting month after segment filter."""
    month = pd.Timestamp(selection.reporting_month).strftime("%Y-%m-%d")
    frame = apply_segment_filter(segment_mart, selection)
    frame = frame[frame["reporting_month"].astype(str) == month]
    if frame.empty:
        return pd.DataFrame(columns=["value_segment", "total_revenue", "customers"])
    return (
        frame[["value_segment", "total_revenue", "customers"]]
        .sort_values("total_revenue", ascending=False)
        .reset_index(drop=True)
    )


def scoped_revenue_kpis(
    *,
    national_cards: list[KpiResult],
    regional_mart: pd.DataFrame,
    selection: FilterSelection,
) -> list[KpiResult]:
    """Replace revenue/subscriber cards with regional totals when scoped."""
    if not selection.regional_scope:
        return national_cards
    slice_ = regional_month_slice(regional_mart, selection)
    if slice_.empty:
        return national_cards
    revenue = float(slice_["total_revenue"].sum())
    subscribers = float(slice_["subscribers"].sum())
    active = float(
        slice_["active_subscribers"].sum()
        if "active_subscribers" in slice_.columns
        else subscribers
    )
    arpu = revenue / active if active else 0.0
    month = selection.reporting_month
    return [
        KpiResult(
            name="Scoped Revenue",
            value=revenue,
            unit="TZS",
            reporting_month=month,
            format_hint="currency",
        ),
        KpiResult(
            name="Scoped ARPU",
            value=arpu,
            unit="TZS",
            reporting_month=month,
            format_hint="currency",
        ),
        KpiResult(
            name="Scoped Subscribers",
            value=subscribers,
            unit="count",
            reporting_month=month,
            format_hint="integer",
        ),
        KpiResult(
            name="Regions in scope",
            value=float(len(selection.regions)),
            unit="count",
            reporting_month=month,
            format_hint="integer",
        ),
    ]


def scoped_revenue_trend(
    *,
    national_mart: pd.DataFrame,
    regional_mart: pd.DataFrame,
    selection: FilterSelection,
) -> pd.DataFrame:
    """Trend of total revenue — regional aggregate when regions are selected."""
    if selection.regional_scope:
        frame = apply_regional_filter(regional_mart, selection)
        frame = filter_month_range(
            frame,
            start_month=selection.start_month,
            end_month=selection.end_month,
        )
        if frame.empty:
            return pd.DataFrame(
                columns=[
                    "reporting_month",
                    "total_revenue",
                    "arpu",
                    "total_subscribers",
                ]
            )
        if "active_subscribers" in frame.columns:
            grouped = frame.groupby("reporting_month", as_index=False).agg(
                total_revenue=("total_revenue", "sum"),
                subscribers=("subscribers", "sum"),
                active_subscribers=("active_subscribers", "sum"),
            )
            active_col = "active_subscribers"
        else:
            grouped = frame.groupby("reporting_month", as_index=False).agg(
                total_revenue=("total_revenue", "sum"),
                subscribers=("subscribers", "sum"),
            )
            active_col = "subscribers"
        grouped["arpu"] = grouped["total_revenue"] / grouped[active_col].clip(lower=1)
        grouped["total_subscribers"] = grouped["subscribers"]
        return grouped.sort_values("reporting_month").reset_index(drop=True)
    return filter_month_range(
        national_mart,
        start_month=selection.start_month,
        end_month=selection.end_month,
    )


def customer_base_metrics(
    dim_customer: pd.DataFrame,
    selection: FilterSelection,
) -> tuple[int, int, float]:
    """Return (matched, total, share_pct) for dim filters."""
    total = len(dim_customer)
    if total == 0:
        return 0, 0, 0.0
    frame = dim_customer
    if selection.regions and "region" in frame.columns:
        frame = frame[frame["region"].astype(str).isin(selection.regions)]
    if selection.value_segments and "value_segment" in frame.columns:
        frame = frame[frame["value_segment"].astype(str).isin(selection.value_segments)]
    if selection.account_types and "account_type" in frame.columns:
        frame = frame[frame["account_type"].astype(str).isin(selection.account_types)]
    matched = len(frame)
    return matched, total, (matched / total) * 100.0
