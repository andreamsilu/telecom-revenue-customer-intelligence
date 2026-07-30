"""Shared helpers for analytical Streamlit pages."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import streamlit as st
from src.analytics.filter_views import (
    FilterSelection,
    apply_campaign_filters,
    customer_base_metrics,
)
from src.recommendations import generate_recommendations
from src.recommendations.models import Recommendation

from app.components.filters import FilterState
from app.components.insight_panel import render_insight_panel
from app.components.layout import (
    render_data_freshness,
    render_empty_state,
    render_page_header,
)
from app.services.data_loader import FilterOptions, MartBundle, load_mart_bundle


def to_selection(filters: FilterState) -> FilterSelection:
    """Convert Streamlit filter state into an analytics selection."""
    return FilterSelection(
        reporting_month=filters.reporting_month,
        start_month=filters.start_month,
        end_month=filters.end_month,
        regions=tuple(filters.regions),
        value_segments=tuple(filters.segments),
        account_types=tuple(filters.account_types),
        product_categories=tuple(filters.product_categories),
    )


def load_page_marts(
    options: FilterOptions,
    filters: FilterState,
    *,
    profile_name: str,
    title: str,
    subtitle: str,
) -> MartBundle | None:
    """Render header/freshness/filter scope and load marts."""
    render_page_header(title, subtitle)
    render_data_freshness(list(options.mart_paths))
    render_filter_scope_banner(filters)
    try:
        return load_mart_bundle(profile_name)
    except FileNotFoundError as exc:
        render_empty_state(str(exc))
        return None


def render_filter_scope_banner(filters: FilterState) -> None:
    """Show which filters are active and how they affect the page."""
    selection = to_selection(filters)
    chips: list[str] = [
        f"Month: {filters.reporting_month}",
        f"Trend: {filters.start_month} → {filters.end_month}",
    ]
    if selection.regions:
        chips.append("Regions: " + ", ".join(selection.regions))
    if selection.value_segments:
        chips.append("Value segments: " + ", ".join(selection.value_segments))
    if selection.account_types:
        chips.append("Account types: " + ", ".join(selection.account_types))
    if selection.product_categories:
        chips.append("Products: " + ", ".join(selection.product_categories))
    st.caption(" · ".join(chips))
    if selection.regional_scope:
        st.info(
            "Region filter is active: revenue/subscriber KPIs and trends use the "
            "selected regional slice. National churn / recharge / mobile-money "
            "headline rates stay portfolio-level.",
            icon="ℹ️",
        )


def render_base_composition(marts: MartBundle, filters: FilterState) -> None:
    """Show dim_customer match rate when dimension filters are set."""
    selection = to_selection(filters)
    if not selection.has_dimension_filters or marts.customers.empty:
        return
    matched, total, share = customer_base_metrics(marts.customers, selection)
    st.caption(
        f"Customer base in filter scope: **{matched:,}** of {total:,} "
        f"({share:.1f}%) from dim_customer."
    )


def page_recommendations(
    marts: MartBundle,
    filters: FilterState,
    *,
    module: str | None = None,
) -> list[Recommendation]:
    """Generate recommendations and optionally keep one module."""
    selection = to_selection(filters)
    campaign = apply_campaign_filters(marts.campaign, selection)
    regional = marts.regional
    if selection.regions:
        regional = regional[regional["region"].astype(str).isin(selection.regions)]
    recommendations = generate_recommendations(
        reporting_month=filters.reporting_month,
        executive_mart=marts.executive,
        revenue_mart=marts.revenue,
        subscriber_mart=marts.subscriber,
        churn_mart=marts.churn,
        recharge_mart=marts.recharge,
        regional_mart=regional,
        campaign_mart=campaign if not campaign.empty else marts.campaign,
    )
    if filters.regions:
        recommendations = [
            rec
            for rec in recommendations
            if rec.supporting_filters.get("region") in filters.regions
            or "region" not in rec.supporting_filters
        ]
    if module:
        modular = [rec for rec in recommendations if rec.module == module]
        if modular:
            return modular
    return recommendations


def render_top_insight(
    marts: MartBundle,
    filters: FilterState,
    *,
    module: str | None = None,
) -> None:
    """Show the top Finding → Impact → Action for the page."""
    recommendations = page_recommendations(marts, filters, module=module)
    render_insight_panel(recommendations[0] if recommendations else None)


def safe_kpi_section(
    label: str,
    builder: Callable[[], list],
) -> None:
    """Render a KPI section with KeyError protection."""
    st.subheader(label)
    try:
        cards = builder()
    except KeyError as exc:
        render_empty_state(f"KPI section unavailable: {exc}")
        return
    from app.components.kpi_card import render_kpi_cards

    render_kpi_cards(cards, columns=min(5, max(1, len(cards))))


def trend_frame(
    frame: pd.DataFrame,
    filters: FilterState,
) -> pd.DataFrame:
    """Filter a monthly mart to the selected trend range."""
    from src.analytics.breakdowns import filter_month_range

    return filter_month_range(
        frame,
        start_month=filters.start_month,
        end_month=filters.end_month,
    )
