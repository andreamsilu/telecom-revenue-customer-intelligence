"""Executive Recommendations Streamlit page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.filters import FilterState
from app.components.insight_panel import render_insight_panel
from app.pages._common import load_page_marts, page_recommendations
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
        profile_name=profile_name,
        title="Executive Recommendations",
        subtitle="Metric-supported Finding → Impact → Action queue for leadership.",
    )
    if marts is None:
        return

    recommendations = page_recommendations(marts, filters)
    st.subheader("KPI summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total recommendations", len(recommendations))
    c2.metric(
        "Critical",
        sum(1 for r in recommendations if r.priority == "Critical"),
    )
    c3.metric("High", sum(1 for r in recommendations if r.priority == "High"))
    c4.metric(
        "Departments",
        len({r.responsible_department for r in recommendations}),
    )

    st.subheader("Priority queue")
    if not recommendations:
        st.info("No recommendations fired for this reporting month.")
        return

    render_insight_panel(recommendations[0])

    st.subheader("All recommendations")
    rows = [
        {
            "priority": r.priority,
            "module": r.module,
            "department": r.responsible_department,
            "finding": r.finding,
            "impact": r.business_impact,
            "action": r.recommended_action,
            "metric": r.metric_name,
            "value": r.metric_value,
            "benchmark": r.benchmark,
            "id": r.recommendation_id,
        }
        for r in recommendations
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    departments = sorted({r.responsible_department for r in recommendations})
    selected = st.multiselect("Filter by department", departments, default=departments)
    for rec in recommendations:
        if rec.responsible_department not in selected:
            continue
        with st.expander(f"{rec.priority} · {rec.module} · {rec.recommendation_id}"):
            st.markdown(f"**Finding:** {rec.finding}")
            st.markdown(f"**Business impact:** {rec.business_impact}")
            st.markdown(f"**Recommended action:** {rec.recommended_action}")
            st.caption(
                f"{rec.metric_name}={rec.metric_value} · benchmark={rec.benchmark} · "
                f"dept={rec.responsible_department}"
            )
