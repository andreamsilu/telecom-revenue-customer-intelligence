"""Finding → Impact → Action insight panel."""

from __future__ import annotations

import html

import streamlit as st
from src.recommendations.models import Recommendation

_FINDING_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" '
    'stroke-width="1.75"/>'
    '<path fill="none" stroke="currentColor" stroke-width="1.75" '
    'stroke-linecap="round" d="M20 20l-3-3"/>'
    "</svg>"
)
_IMPACT_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="none" stroke="currentColor" stroke-width="1.75" '
    'stroke-linecap="round" stroke-linejoin="round" '
    'd="M13 2 4 14h7l-1 8 10-14h-7l1-6z"/>'
    "</svg>"
)
_ACTION_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="none" stroke="currentColor" stroke-width="1.75" '
    'stroke-linecap="round" stroke-linejoin="round" '
    'd="M5 12h14M13 6l6 6-6 6"/>'
    "</svg>"
)


def render_insight_panel(recommendation: Recommendation | None) -> None:
    """Render the executive finding, impact, and recommended action."""
    st.subheader("Executive insight")
    if recommendation is None:
        from app.components.layout import render_empty_state

        render_empty_state(
            "No priority insights for this reporting month and filter scope."
        )
        return

    finding = html.escape(recommendation.finding)
    impact = html.escape(recommendation.business_impact)
    action = html.escape(recommendation.recommended_action)
    priority = html.escape(recommendation.priority)
    department = html.escape(recommendation.responsible_department)
    module = html.escape(recommendation.module)
    metric = html.escape(
        f"{recommendation.metric_name}: {recommendation.metric_value:,.2f} "
        f"(benchmark: {recommendation.benchmark})"
    )
    filters = ""
    if recommendation.supporting_filters:
        filters = html.escape(
            "Filters: "
            + ", ".join(
                f"{k}={v}" for k, v in recommendation.supporting_filters.items()
            )
        )

    st.markdown(
        f"""
        <div class="trci-insight-card">
          <div class="trci-insight-meta">
            <span class="trci-insight-pill">{priority}</span>
            <span>{department}</span>
            <span>{module}</span>
          </div>
          <div class="trci-insight-row">
            <div class="trci-insight-icon">{_FINDING_ICON}</div>
            <div>
              <div class="trci-insight-label">Finding</div>
              <div class="trci-insight-text">{finding}</div>
            </div>
          </div>
          <div class="trci-insight-row">
            <div class="trci-insight-icon">{_IMPACT_ICON}</div>
            <div>
              <div class="trci-insight-label">Business impact</div>
              <div class="trci-insight-text">{impact}</div>
            </div>
          </div>
          <div class="trci-insight-row">
            <div class="trci-insight-icon">{_ACTION_ICON}</div>
            <div>
              <div class="trci-insight-label">Recommended action</div>
              <div class="trci-insight-text">{action}</div>
            </div>
          </div>
          <div class="trci-insight-foot">{metric}<br/>{filters}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
