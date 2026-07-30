"""Revenue Analytics Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.executive import revenue_kpi_cards
from src.analytics.filter_views import (
    regional_month_slice,
    scoped_revenue_kpis,
    scoped_revenue_trend,
    segment_month_slice,
)

from app.components.charts import (
    render_metric_trend,
    render_regional_bar,
    render_revenue_trend,
    render_segment_bar,
)
from app.components.filters import FilterState
from app.pages._common import (
    load_page_marts,
    render_base_composition,
    render_top_insight,
    safe_kpi_section,
    to_selection,
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
        filters,
        profile_name=profile_name,
        title="Revenue Analytics",
        subtitle="Top-line revenue, ARPU context, and monetisation mix.",
    )
    if marts is None:
        return

    selection = to_selection(filters)
    render_base_composition(marts, filters)

    def _cards() -> list:
        national = revenue_kpi_cards(marts.revenue, filters.reporting_month)
        return scoped_revenue_kpis(
            national_cards=national,
            regional_mart=marts.regional,
            selection=selection,
        )

    safe_kpi_section("KPI summary", _cards)

    st.subheader("Trend analysis")
    trend = scoped_revenue_trend(
        national_mart=marts.revenue,
        regional_mart=marts.regional,
        selection=selection,
    )
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
        render_regional_bar(regional_month_slice(marts.regional, selection))
    with c2:
        render_segment_bar(segment_month_slice(marts.segment, selection))
    render_top_insight(marts, filters, module="Revenue Analytics")
