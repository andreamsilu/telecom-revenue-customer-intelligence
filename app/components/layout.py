"""Shared page layout helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st


def inject_theme_css() -> None:
    """Apply theme helpers for main content and a polished sidebar."""
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.25rem; padding-bottom: 2rem; }
        h1 { letter-spacing: -0.02em; }
        div[data-testid="stMetricValue"] { font-size: 1.35rem; }
        div[data-testid="stMetricDelta"] { font-size: 0.85rem; }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #E8F0EC 0%, #F7F9F8 42%, #F7F9F8 100%);
            border-right: 1px solid #D5E3DB;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.25rem;
        }
        .trci-sidebar-brand {
            font-size: 0.95rem;
            font-weight: 700;
            color: #0B6E4F;
            letter-spacing: -0.01em;
            line-height: 1.35;
            margin-bottom: 0.15rem;
        }
        .trci-sidebar-meta {
            color: #4A5A52;
            font-size: 0.78rem;
            margin-bottom: 0.85rem;
        }
        .trci-sidebar-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #0B6E4F;
            margin: 0.35rem 0 0.35rem 0;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            background: rgba(255,255,255,0.55);
            border: 1px solid #D5E3DB;
            border-radius: 0.55rem;
            padding: 0.45rem 0.65rem;
            margin-bottom: 0.35rem;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            border-color: #0B6E4F;
            background: #FFFFFF;
        }
        section[data-testid="stSidebar"] hr {
            margin: 0.9rem 0;
            border-color: #D5E3DB;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand(*, project_name: str, profile: str) -> None:
    """Render branded sidebar header above navigation."""
    st.sidebar.markdown(
        f'<div class="trci-sidebar-brand">{project_name}</div>'
        f'<div class="trci-sidebar-meta">Profile <code>{profile}</code>'
        " · Synthetic Tanzania telecom data</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="trci-sidebar-label">Navigate</div>', unsafe_allow_html=True
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
