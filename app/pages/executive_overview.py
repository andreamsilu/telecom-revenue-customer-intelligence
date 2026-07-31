"""Executive Overview Streamlit page — story first, then evidence."""

from __future__ import annotations

import streamlit as st
from src.analytics.executive import executive_kpi_cards
from src.analytics.filter_views import (
    regional_month_slice,
    scoped_revenue_kpis,
    scoped_revenue_trend,
    segment_month_slice,
)
from src.analytics.narrative import build_month_story

from app.components.charts import (
    render_regional_bar,
    render_revenue_trend,
    render_segment_bar,
    render_subscriber_mix,
)
from app.components.filters import FilterState
from app.components.insight_panel import render_insight_panel
from app.components.kpi_card import render_kpi_cards
from app.components.narrative_panel import render_evidence_label, render_month_story
from app.pages._common import (
    load_page_marts,
    page_recommendations,
    render_base_composition,
    to_selection,
)
from app.services.data_loader import FilterOptions


def render_executive_overview(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render story → insight → KPIs → evidence charts."""
    marts = load_page_marts(
        options,
        filters,
        profile_name=profile_name,
        title="Executive Overview",
        subtitle=("Month-in-review story, priority actions, then supporting evidence."),
    )
    if marts is None:
        return

    selection = to_selection(filters)
    render_base_composition(marts, filters)
    recommendations = page_recommendations(marts, filters)

    story = build_month_story(
        marts.executive,
        filters.reporting_month,
        recommendations,
    )
    render_month_story(story)
    render_insight_panel(recommendations[0] if recommendations else None)

    st.subheader("KPI summary")
    try:
        national = executive_kpi_cards(marts.executive, filters.reporting_month)
        cards = scoped_revenue_kpis(
            national_cards=national,
            regional_mart=marts.regional,
            selection=selection,
        )
    except KeyError:
        st.warning(f"No executive KPIs for {filters.reporting_month}.")
        return
    render_kpi_cards(cards, columns=min(5, len(cards)))

    render_evidence_label("Supporting evidence — trends")
    st.subheader("Trend analysis")
    trend = scoped_revenue_trend(
        national_mart=marts.executive,
        regional_mart=marts.regional,
        selection=selection,
    )
    left, right = st.columns(2)
    with left:
        render_revenue_trend(trend)
    with right:
        render_subscriber_mix(trend)

    render_evidence_label("Supporting evidence — comparisons")
    st.subheader("Regional and segment comparison")
    c1, c2 = st.columns(2)
    with c1:
        render_regional_bar(regional_month_slice(marts.regional, selection))
    with c2:
        render_segment_bar(segment_month_slice(marts.segment, selection))

    _render_additional_recommendations(recommendations)


def _render_additional_recommendations(recommendations: list) -> None:
    """Show remaining recommendations after the lead story."""
    if len(recommendations) <= 1:
        return
    with st.expander(f"Additional recommendations ({len(recommendations) - 1})"):
        for rec in recommendations[1:6]:
            st.markdown(
                f"**{rec.priority} · {rec.module}** — {rec.finding}  \n"
                f"_{rec.recommended_action}_"
            )
