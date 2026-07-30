"""Mobile Money Analytics Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.breakdowns import revenue_by_value_segment
from src.analytics.domain import mobile_money_kpi_cards

from app.components.charts import render_metric_trend, render_segment_bar
from app.components.filters import FilterState
from app.pages._common import (
    load_page_marts,
    render_top_insight,
    safe_kpi_section,
    trend_frame,
)
from app.services.data_loader import FilterOptions


def render_mobile_money_analytics(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render mobile money KPIs, trends, and segment context."""
    marts = load_page_marts(
        options,
        profile_name=profile_name,
        title="Mobile Money Analytics",
        subtitle="Active users, fee revenue, and transaction reliability.",
    )
    if marts is None:
        return

    safe_kpi_section(
        "KPI summary",
        lambda: mobile_money_kpi_cards(marts.mobile_money, filters.reporting_month),
    )

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
    st.caption(
        "Value-segment revenue mix provides wallet-adjacent monetisation context "
        "alongside mobile money KPIs."
    )
    render_segment_bar(
        revenue_by_value_segment(marts.segment, reporting_month=filters.reporting_month)
    )
    render_top_insight(marts, filters, module=None)
