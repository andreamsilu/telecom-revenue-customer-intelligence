"""Churn and Retention Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.domain import retention_kpi_cards
from src.analytics.filter_views import regional_month_slice

from app.components.charts import render_metric_trend, render_regional_metric_bar
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


def render_churn_retention(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render churn KPIs, trends, and regional churn context."""
    marts = load_page_marts(
        options,
        filters,
        profile_name=profile_name,
        title="Churn and Retention",
        subtitle="Churn rate, revenue at risk, and high-value losses.",
    )
    if marts is None:
        return

    selection = to_selection(filters)
    render_base_composition(marts, filters)
    render_top_insight(marts, filters, module="Churn and Retention")
    safe_kpi_section(
        "KPI summary",
        lambda: retention_kpi_cards(marts.churn, filters.reporting_month),
    )

    render_evidence_label()
    st.subheader("Trend analysis")
    trend = trend_frame(marts.churn, filters)
    left, right = st.columns(2)
    with left:
        render_metric_trend(
            trend,
            y_col="churn_rate",
            title="Churn rate trend",
            y_label="Churn rate (%)",
            color="#C45C26",
        )
    with right:
        render_metric_trend(
            trend,
            y_col="revenue_lost_to_churn",
            title="Revenue lost to churn",
            y_label="TZS",
        )

    st.subheader("Regional comparison")
    render_regional_metric_bar(
        regional_month_slice(marts.regional, selection),
        value_col="newly_churned",
        title="Newly churned customers by region",
        value_label="Newly churned",
    )
