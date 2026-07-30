"""Regional Performance Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.breakdowns import regional_revenue_slice
from src.analytics.campaign_regional import regional_kpi_cards

from app.components.charts import (
    render_metric_trend,
    render_regional_bar,
    render_regional_subscribers_bar,
)
from app.components.filters import FilterState
from app.pages._common import (
    load_page_marts,
    render_top_insight,
    safe_kpi_section,
    trend_frame,
)
from app.services.data_loader import FilterOptions


def render_regional_performance(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render regional KPIs, trends for a focus region, and comparisons."""
    marts = load_page_marts(
        options,
        profile_name=profile_name,
        title="Regional Performance",
        subtitle="Geographic revenue, subscribers, and ARPU differences.",
    )
    if marts is None:
        return

    safe_kpi_section(
        "KPI summary",
        lambda: regional_kpi_cards(marts.regional, filters.reporting_month),
    )

    st.subheader("Trend analysis")
    focus_regions = (
        filters.regions
        or sorted(marts.regional["region"].dropna().astype(str).unique().tolist())[:1]
    )
    focus = focus_regions[0] if focus_regions else None
    if focus:
        regional_trend = marts.regional[marts.regional["region"].astype(str) == focus]
        regional_trend = trend_frame(regional_trend, filters)
        st.caption(f"Trends for focus region: **{focus}** (select in filters).")
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
    sliced = regional_revenue_slice(
        marts.regional,
        reporting_month=filters.reporting_month,
        regions=filters.regions or None,
    )
    c1, c2 = st.columns(2)
    with c1:
        render_regional_bar(sliced)
    with c2:
        render_regional_subscribers_bar(sliced)

    render_top_insight(marts, filters, module="Regional Performance")
