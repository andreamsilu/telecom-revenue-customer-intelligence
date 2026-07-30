"""Executive Recommendations Streamlit page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.filters import FilterState
from app.components.insight_panel import render_insight_panel
from app.components.kpi_card import render_summary_cards
from app.pages._common import (
    load_page_marts,
    page_recommendations,
    render_base_composition,
)
from app.services.data_loader import FilterOptions


def render_executive_recommendations(
    filters: FilterState,
    options: FilterOptions,
    *,
    profile_name: str = "development",
) -> None:
    """List deterministic recommendations with priority and department."""
    marts = load_page_marts(
        options,
        filters,
        profile_name=profile_name,
        title="Executive Recommendations",
        subtitle="Priority Finding → Impact → Action queue for leadership.",
    )
    if marts is None:
        return

    render_base_composition(marts, filters)
    recommendations = page_recommendations(marts, filters)
    st.subheader("KPI summary")
    render_summary_cards(
        [
            (
                "Total recommendations",
                f"{len(recommendations):,}",
                "recommendation",
            ),
            (
                "Critical",
                str(sum(1 for r in recommendations if r.priority == "Critical")),
                "churn",
            ),
            (
                "High",
                str(sum(1 for r in recommendations if r.priority == "High")),
                "active",
            ),
            (
                "Departments",
                str(len({r.responsible_department for r in recommendations})),
                "subscribers",
            ),
        ],
        columns=4,
    )

    st.subheader("Priority queue")
    if not recommendations:
        from app.components.layout import render_empty_state

        render_empty_state(
            "No priority actions for this reporting month and filter scope."
        )
        return

    render_insight_panel(recommendations[0])

    st.subheader("All recommendations")
    rows = [
        {
            "Priority": r.priority,
            "Module": r.module,
            "Department": r.responsible_department,
            "Finding": r.finding,
            "Impact": r.business_impact,
            "Action": r.recommended_action,
            "Metric": r.metric_name,
            "Value": r.metric_value,
            "Benchmark": r.benchmark,
        }
        for r in recommendations
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    departments = sorted({r.responsible_department for r in recommendations})
    selected = st.multiselect("Department", departments, default=departments)
    for rec in recommendations:
        if rec.responsible_department not in selected:
            continue
        title = f"{rec.priority} · {rec.module} · {rec.responsible_department}"
        with st.expander(title):
            st.markdown(f"**Finding:** {rec.finding}")
            st.markdown(f"**Business impact:** {rec.business_impact}")
            st.markdown(f"**Recommended action:** {rec.recommended_action}")
            st.caption(
                f"{rec.metric_name}: {rec.metric_value:,.2f} · "
                f"Benchmark {rec.benchmark}"
            )
