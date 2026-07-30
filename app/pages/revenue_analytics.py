"""Revenue Analytics Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.breakdowns import regional_revenue_slice, revenue_by_value_segment
from src.analytics.executive import revenue_kpi_cards

from app.components.charts import (
    render_metric_trend,
    render_regional_bar,
    render_revenue_trend,
    render_segment_bar,
)
from app.components.filters import FilterState
from app.pages._common import (
    load_page_marts,
    render_top_insight,
    safe_kpi_section,
    trend_frame,
)
from app.services.data_loader import FilterOptions


def render_revenue_analytics(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render revenue KPIs, trends, and segment/regional comparisons."""
    marts = load_page_marts(
        options,
        profile_name=profile_name,
        title="Revenue Analytics",
        subtitle="Top-line revenue, ARPU context, and monetisation mix.",
    )
    if marts is None:
        return

    safe_kpi_section(
        "KPI summary",
        lambda: revenue_kpi_cards(marts.revenue, filters.reporting_month),
    )

    st.subheader("Trend analysis")
    trend = trend_frame(marts.revenue, filters)
    left, right = st.columns(2)
    with left:
        render_revenue_trend(trend)
    with right:
        render_metric_trend(
            trend,
            y_col="arpu",
            title="ARPU trend",
            y_label="ARPU (TZS)",
            color="#C45C26",
        )

    st.subheader("Segment or regional comparison")
    c1, c2 = st.columns(2)
    with c1:
        render_regional_bar(
            regional_revenue_slice(
                marts.regional,
                reporting_month=filters.reporting_month,
                regions=filters.regions or None,
            )
        )
    with c2:
        render_segment_bar(
            revenue_by_value_segment(
                marts.segment, reporting_month=filters.reporting_month
            )
        )
    render_top_insight(marts, filters, module="Revenue Analytics")
