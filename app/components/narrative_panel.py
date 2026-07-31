"""Executive month-story and insight-first storytelling panels."""

from __future__ import annotations

import html

import streamlit as st
from src.analytics.narrative import MonthStory


def render_month_story(story: MonthStory) -> None:
    """Render What changed this month — headline, movements, drivers, close."""
    st.markdown(
        f"""
        <div class="trci-story-card">
          <div class="trci-story-kicker">What changed this month</div>
          <div class="trci-story-headline">{html.escape(story.headline)}</div>
          <div class="trci-story-grid">
            <div>
              <div class="trci-story-label">KPI movements</div>
              <ul class="trci-story-list">
                {"".join(f"<li>{html.escape(item)}</li>" for item in story.movements)}
              </ul>
            </div>
            <div>
              <div class="trci-story-label">Metric-backed drivers</div>
              {_drivers_html(story)}
            </div>
          </div>
          <div class="trci-story-close">{html.escape(story.closing)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if story.priority_action:
        st.caption(f"Lead action: {story.priority_action}")


def render_evidence_label(text: str = "Supporting evidence") -> None:
    """Section eyebrow before charts that prove the story."""
    st.markdown(
        f'<div class="trci-section-label">{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def _drivers_html(story: MonthStory) -> str:
    if not story.drivers:
        return (
            '<p class="trci-story-muted">No priority drivers fired under '
            "current recommendation rules.</p>"
        )
    items = "".join(f"<li>{html.escape(item)}</li>" for item in story.drivers)
    return f'<ul class="trci-story-list">{items}</ul>'
