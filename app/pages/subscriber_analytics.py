"""Subscriber Analytics Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.domain import subscriber_kpi_cards
from src.analytics.filter_views import regional_month_slice, scoped_revenue_kpis

from app.components.charts import (
    render_lifecycle_stack,
    render_metric_trend,
    render_regional_subscribers_bar,
)
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


def render_subscriber_analytics(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render subscriber KPIs, lifecycle trends, and regional comparison."""
    marts = load_page_marts(
        options,
        filters,
        profile_name=profile_name,
        title="Subscriber Analytics",
        subtitle="Base growth, activity, and lifecycle movement.",
    )
    if marts is None:
        return

    selection = to_selection(filters)
    render_base_composition(marts, filters)

    def _cards() -> list:
        national = subscriber_kpi_cards(marts.subscriber, filters.reporting_month)
        return scoped_revenue_kpis(
            national_cards=national,
            regional_mart=marts.regional,
            selection=selection,
        )

    safe_kpi_section("KPI summary", _cards)

    st.subheader("Trend analysis")
    if selection.regional_scope:
        from src.analytics.filter_views import scoped_revenue_trend

        trend = scoped_revenue_trend(
            national_mart=marts.subscriber,
            regional_mart=marts.regional,
            selection=selection,
        )
        render_metric_trend(
            trend,
            y_col="total_subscribers",
            title="Scoped subscribers",
            y_label="Subscribers",
        )
    else:
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
    render_regional_subscribers_bar(regional_month_slice(marts.regional, selection))
    render_top_insight(marts, filters, module="Subscriber Analytics")
