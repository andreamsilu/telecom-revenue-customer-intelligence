"""Executive Overview Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.breakdowns import (
    filter_month_range,
    regional_revenue_slice,
    revenue_by_value_segment,
)
from src.analytics.executive import executive_kpi_cards
from src.recommendations import generate_recommendations

from app.components.charts import (
    render_regional_bar,
    render_revenue_trend,
    render_segment_bar,
    render_subscriber_mix,
)
from app.components.filters import FilterState
from app.components.insight_panel import render_insight_panel
from app.components.kpi_card import render_kpi_cards
from app.components.layout import (
    render_data_freshness,
    render_empty_state,
    render_page_header,
)
from app.services.data_loader import FilterOptions, MartBundle, load_mart_bundle


def render_executive_overview(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render the Executive Overview page using analytics services."""
    render_page_header(
        "Executive Overview",
        "National headline KPIs, trends, and metric-supported recommendations.",
    )
    render_data_freshness(list(options.mart_paths))

    try:
        marts = load_mart_bundle(profile_name)
    except FileNotFoundError as exc:
        render_empty_state(
            f"{exc} Run `python -m scripts.run_pipeline --profile {profile_name}` "
            "before launching the dashboard."
        )
        return

    _render_kpis(marts, filters)
    _render_trends(marts, filters)
    _render_comparisons(marts, filters)
    _render_recommendations(marts, filters)


def _render_kpis(marts: MartBundle, filters: FilterState) -> None:
    st.subheader("KPI summary")
    try:
        cards = executive_kpi_cards(marts.executive, filters.reporting_month)
    except KeyError:
        render_empty_state(
            f"No executive KPIs for reporting month {filters.reporting_month}."
        )
        return
    render_kpi_cards(cards, columns=5)


def _render_trends(marts: MartBundle, filters: FilterState) -> None:
    st.subheader("Trend analysis")
    trend = filter_month_range(
        marts.executive,
        start_month=filters.start_month,
        end_month=filters.end_month,
    )
    left, right = st.columns(2)
    with left:
        render_revenue_trend(trend)
    with right:
        render_subscriber_mix(trend)


def _render_comparisons(marts: MartBundle, filters: FilterState) -> None:
    st.subheader("Regional and segment comparison")
    left, right = st.columns(2)
    with left:
        regional = regional_revenue_slice(
            marts.regional,
            reporting_month=filters.reporting_month,
            regions=filters.regions or None,
        )
        render_regional_bar(regional)
    with right:
        segments = revenue_by_value_segment(
            marts.snapshot,
            reporting_month=filters.reporting_month,
        )
        render_segment_bar(segments)


def _render_recommendations(marts: MartBundle, filters: FilterState) -> None:
    recommendations = generate_recommendations(
        reporting_month=filters.reporting_month,
        executive_mart=marts.executive,
        revenue_mart=marts.revenue,
        subscriber_mart=marts.subscriber,
        churn_mart=marts.churn,
        recharge_mart=marts.recharge,
        regional_mart=marts.regional,
        campaign_mart=marts.campaign,
    )
    if filters.regions:
        recommendations = [
            rec
            for rec in recommendations
            if rec.supporting_filters.get("region") in filters.regions
            or "region" not in rec.supporting_filters
        ]
    top = recommendations[0] if recommendations else None
    render_insight_panel(top)
    if len(recommendations) > 1:
        with st.expander(f"Additional recommendations ({len(recommendations) - 1})"):
            for rec in recommendations[1:6]:
                st.markdown(
                    f"**{rec.priority} · {rec.module}** — {rec.finding}  \n"
                    f"_{rec.recommended_action}_"
                )
