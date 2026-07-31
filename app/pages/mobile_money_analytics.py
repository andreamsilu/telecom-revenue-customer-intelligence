"""Mobile Money Analytics Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.domain import mobile_money_kpi_cards
from src.analytics.filter_views import segment_month_slice

from app.components.charts import render_metric_trend, render_segment_bar
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


def render_mobile_money_analytics(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render insight first, then mobile money KPIs and evidence charts."""
    marts = load_page_marts(
        options,
        filters,
        profile_name=profile_name,
        title="Mobile Money Analytics",
        subtitle="Active users, fee revenue, and transaction reliability.",
    )
    if marts is None:
        return

    selection = to_selection(filters)
    render_base_composition(marts, filters)
    render_top_insight(marts, filters, module=None)
    safe_kpi_section(
        "KPI summary",
        lambda: mobile_money_kpi_cards(marts.mobile_money, filters.reporting_month),
    )

    render_evidence_label()
    st.subheader("Trend analysis")
    trend = trend_frame(marts.mobile_money, filters)
    left, right = st.columns(2)
    with left:
        render_metric_trend(
            trend,
            y_col="active_users",
            title="Mobile money active users",
            y_label="Users",
        )
    with right:
        render_metric_trend(
            trend,
            y_col="fee_revenue",
            title="Fee revenue",
            y_label="TZS",
            color="#C45C26",
        )

    st.subheader("Segment comparison")
    render_segment_bar(segment_month_slice(marts.segment, selection))
