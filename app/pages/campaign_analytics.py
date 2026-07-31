"""Campaign Analytics Streamlit page."""

from __future__ import annotations

import streamlit as st
from src.analytics.campaign_regional import campaign_kpi_summary
from src.analytics.filter_views import apply_campaign_filters, segment_month_slice

from app.components.charts import render_campaign_roi_bar, render_segment_bar
from app.components.filters import FilterState
from app.components.narrative_panel import render_evidence_label
from app.pages._common import (
    load_page_marts,
    render_base_composition,
    render_top_insight,
    safe_kpi_section,
    to_selection,
)
from app.services.data_loader import FilterOptions


def render_campaign_analytics(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """Render insight first, then attributed campaign evidence."""
    marts = load_page_marts(
        options,
        filters,
        profile_name=profile_name,
        title="Campaign Analytics",
        subtitle="Attributed campaign outcomes — descriptive, not causal uplift.",
    )
    if marts is None:
        return

    selection = to_selection(filters)
    render_base_composition(marts, filters)
    campaigns = apply_campaign_filters(marts.campaign, selection)
    if campaigns.empty:
        st.warning("No campaigns match the current dimension filters.")
        campaigns = marts.campaign.iloc[0:0]

    render_top_insight(marts, filters, module="Campaign Analytics")
    safe_kpi_section(
        "KPI summary",
        lambda: campaign_kpi_summary(campaigns),
    )

    render_evidence_label()
    st.subheader("Trend analysis")
    st.caption(
        "Campaigns are event-based rather than monthly. ROI below is descriptive "
        "attribution for campaigns matching the active filters."
    )
    render_campaign_roi_bar(campaigns)

    st.subheader("Segment comparison")
    left, right = st.columns(2)
    with left:
        if campaigns.empty:
            st.info("No campaign rows to display.")
        else:
            display = campaigns[
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
        render_segment_bar(segment_month_slice(marts.segment, selection))
