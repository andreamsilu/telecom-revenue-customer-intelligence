"""Shared page layout helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st


def inject_theme_css() -> None:
    """Apply light spacing/typography helpers aligned to the Streamlit theme."""
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        h1 { letter-spacing: -0.02em; }
        div[data-testid="stMetricValue"] { font-size: 1.35rem; }
        div[data-testid="stMetricDelta"] { font-size: 0.85rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str) -> None:
    """Render a consistent page title block."""
    st.title(title)
    st.caption(subtitle)


def render_data_freshness(paths: list[Path]) -> None:
    """Show the newest processed-file modification time."""
    existing = [path for path in paths if path.exists()]
    if not existing:
        st.caption("Data freshness: no processed marts found")
        return
    newest = max(path.stat().st_mtime for path in existing)
    stamp = datetime.fromtimestamp(newest).strftime("%Y-%m-%d %H:%M")
    st.caption(f"Data freshness: processed marts updated {stamp}")


def render_empty_state(message: str) -> None:
    """Show a clean empty/missing-data message."""
    st.warning(message)
