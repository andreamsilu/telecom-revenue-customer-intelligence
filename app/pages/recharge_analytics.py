"""Recharge Analytics Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.domain import recharge_kpi_cards
from src.analytics.filter_views import regional_month_slice

from app.components.charts import render_metric_trend, render_regional_metric_bar
from app.components.filters import FilterState
from app.pages._common import (
    load_page_marts,
    render_base_composition,
    render_top_insight,
    safe_kpi_section,
    to_selection,
    trend_frame,
)
from app.services.data_loader import FilterOptions


def render_recharge_analytics(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render recharge KPIs, trends, and regional recharge value."""
    marts = load_page_marts(
        options,
        filters,
        profile_name=profile_name,
        title="Recharge Analytics",
        subtitle="Top-up frequency, value, and cash-in intensity.",
    )
    if marts is None:
        return

    selection = to_selection(filters)
    render_base_composition(marts, filters)
    safe_kpi_section(
        "KPI summary",
        lambda: recharge_kpi_cards(marts.recharge, filters.reporting_month),
    )

    st.subheader("Trend analysis")
    trend = trend_frame(marts.recharge, filters)
    left, right = st.columns(2)
    with left:
        render_metric_trend(
            trend,
            y_col="recharge_frequency",
            title="Recharge frequency",
            y_label="Per active customer",
        )
    with right:
        render_metric_trend(
            trend,
            y_col="total_recharge_value",
            title="Total recharge value",
            y_label="TZS",
            color="#C45C26",
        )

    st.subheader("Regional comparison")
    render_regional_metric_bar(
        regional_month_slice(marts.regional, selection),
        value_col="recharge_value",
        title="Regional recharge value",
        value_label="Recharge value (TZS)",
    )
    render_top_insight(marts, filters, module="Recharge Analytics")
