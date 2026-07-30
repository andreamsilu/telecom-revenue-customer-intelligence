"""Finding → Impact → Action insight panel."""

from __future__ import annotations

import streamlit as st
from src.recommendations.models import Recommendation


def render_insight_panel(recommendation: Recommendation | None) -> None:
    """Render the executive finding, impact, and recommended action."""
    st.subheader("Executive insight")
    if recommendation is None:
        st.info(
            "No metric-supported recommendations fired for this reporting month "
            "under the current rules."
        )
        return

    left, right = st.columns([2, 1])
    with left:
        st.markdown(f"**Finding**  \n{recommendation.finding}")
        st.markdown(f"**Business impact**  \n{recommendation.business_impact}")
        st.markdown(f"**Recommended action**  \n{recommendation.recommended_action}")
    with right:
        st.markdown(f"**Priority:** {recommendation.priority}")
        st.markdown(f"**Department:** {recommendation.responsible_department}")
        st.markdown(f"**Module:** {recommendation.module}")
        st.caption(
            f"{recommendation.metric_name}: {recommendation.metric_value:,.2f} "
            f"(benchmark: {recommendation.benchmark})"
        )
        if recommendation.supporting_filters:
            st.caption(
                "Filters: "
                + ", ".join(
                    f"{k}={v}" for k, v in recommendation.supporting_filters.items()
                )
            )
