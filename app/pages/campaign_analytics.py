"""Campaign Analytics Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.breakdowns import revenue_by_value_segment
from src.analytics.campaign_regional import campaign_kpi_summary

from app.components.charts import render_campaign_roi_bar, render_segment_bar
from app.components.filters import FilterState
from app.pages._common import load_page_marts, render_top_insight, safe_kpi_section
from app.services.data_loader import FilterOptions


def render_campaign_analytics(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render campaign portfolio KPIs and attributed performance views."""
    marts = load_page_marts(
        options,
        profile_name=profile_name,
        title="Campaign Analytics",
        subtitle="Attributed campaign outcomes — descriptive, not causal uplift.",
    )
    if marts is None:
        return

    safe_kpi_section(
        "KPI summary",
        lambda: campaign_kpi_summary(marts.campaign),
    )

    st.subheader("Trend analysis")
    st.caption(
        "Campaigns are event-based rather than monthly. The chart below compares "
        "attributed ROI across campaigns in the portfolio."
    )
    render_campaign_roi_bar(marts.campaign)

    st.subheader("Segment comparison")
    left, right = st.columns(2)
    with left:
        display = marts.campaign[
            [
                "campaign_id",
                "campaign_name",
                "customers_contacted",
                "conversions",
                "conversion_rate",
                "revenue_generated",
                "campaign_cost",
                "roi",
                "retained_after_30_days",
            ]
        ].copy()
        display["conversion_rate"] = display["conversion_rate"] * 100.0
        display["roi"] = display["roi"] * 100.0
        st.dataframe(display, use_container_width=True, hide_index=True)
    with right:
        render_segment_bar(
            revenue_by_value_segment(
                marts.segment, reporting_month=filters.reporting_month
            )
        )

    render_top_insight(marts, filters, module="Campaign Analytics")
