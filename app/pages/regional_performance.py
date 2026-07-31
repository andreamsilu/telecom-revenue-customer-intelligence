"""Regional Performance Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.campaign_regional import regional_kpi_cards
from src.analytics.filter_views import apply_regional_filter, regional_month_slice

from app.components.charts import (
    render_metric_trend,
    render_regional_bar,
    render_regional_subscribers_bar,
)
from app.components.filters import FilterState
from app.components.narrative_panel import render_evidence_label
from app.pages._common import (
    load_page_marts,
    render_base_composition,
    render_top_insight,
    safe_kpi_section,
    to_selection,
    trend_frame,
)
from app.services.data_loader import FilterOptions


def render_regional_performance(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render insight first, then regional KPIs and evidence charts."""
    marts = load_page_marts(
        options,
        filters,
        profile_name=profile_name,
        title="Regional Performance",
        subtitle="Geographic revenue, subscribers, and ARPU differences.",
    )
    if marts is None:
        return

    selection = to_selection(filters)
    render_base_composition(marts, filters)
    regional_all = apply_regional_filter(marts.regional, selection)
    render_top_insight(marts, filters, module="Regional Performance")

    safe_kpi_section(
        "KPI summary",
        lambda: regional_kpi_cards(regional_all, filters.reporting_month),
    )

    render_evidence_label()
    st.subheader("Trend analysis")
    focus_regions = (
        list(selection.regions)
        or sorted(regional_all["region"].dropna().astype(str).unique().tolist())[:1]
    )
    focus = focus_regions[0] if focus_regions else None
    if focus:
        regional_trend = regional_all[regional_all["region"].astype(str) == focus]
        regional_trend = trend_frame(regional_trend, filters)
        st.caption(f"Trends for focus region: **{focus}**")
        left, right = st.columns(2)
        with left:
            render_metric_trend(
                regional_trend,
                y_col="total_revenue",
                title=f"{focus} revenue",
                y_label="TZS",
            )
        with right:
            render_metric_trend(
                regional_trend,
                y_col="arpu",
                title=f"{focus} ARPU",
                y_label="TZS",
                color="#C45C26",
            )
    else:
        st.warning("No region available for trend analysis.")

    st.subheader("Regional comparison")
    sliced = regional_month_slice(marts.regional, selection)
    c1, c2 = st.columns(2)
    with c1:
        render_regional_bar(sliced)
    with c2:
        render_regional_subscribers_bar(sliced)
