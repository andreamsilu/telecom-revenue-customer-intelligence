"""Subscriber Analytics Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.breakdowns import regional_revenue_slice
from src.analytics.domain import subscriber_kpi_cards

from app.components.charts import (
    render_lifecycle_stack,
    render_metric_trend,
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


def render_subscriber_analytics(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render subscriber KPIs, lifecycle trends, and regional comparison."""
    marts = load_page_marts(
        options,
        profile_name=profile_name,
        title="Subscriber Analytics",
        subtitle="Base growth, activity, and lifecycle movement.",
    )
    if marts is None:
        return

    safe_kpi_section(
        "KPI summary",
        lambda: subscriber_kpi_cards(marts.subscriber, filters.reporting_month),
    )

    st.subheader("Trend analysis")
    trend = trend_frame(marts.subscriber, filters)
    left, right = st.columns(2)
    with left:
        render_metric_trend(
            trend,
            y_col="total_subscribers",
            title="Total subscribers",
            y_label="Subscribers",
        )
    with right:
        render_lifecycle_stack(trend)

    st.subheader("Regional comparison")
    regional = regional_revenue_slice(
        marts.regional,
        reporting_month=filters.reporting_month,
        regions=filters.regions or None,
    )
    render_regional_subscribers_bar(regional)
    render_top_insight(marts, filters, module="Subscriber Analytics")
