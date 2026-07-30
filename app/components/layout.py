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

        .trci-kpi-card {
            background: #FFFFFF;
            border: 1px solid #D5E3DB;
            border-radius: 0.85rem;
            padding: 0.95rem 1rem 0.85rem;
            min-height: 8.25rem;
            box-shadow: 0 1px 2px rgba(26, 31, 28, 0.04);
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
            margin-bottom: 0.35rem;
        }
        .trci-kpi-card__head {
            display: flex;
            align-items: center;
            gap: 0.55rem;
        }
        .trci-kpi-card__icon {
            width: 2.1rem;
            height: 2.1rem;
            border-radius: 0.55rem;
            background: #E8F0EC;
            color: #0B6E4F;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .trci-kpi-card__icon svg {
            width: 1.15rem;
            height: 1.15rem;
            display: block;
        }
        .trci-kpi-card__label {
            color: #4A5A52;
            font-size: 0.82rem;
            font-weight: 600;
            line-height: 1.25;
        }
        .trci-kpi-card__value {
            color: #1A1F1C;
            font-size: 1.45rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.15;
        }
        .trci-kpi-card__delta {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            width: fit-content;
            border-radius: 999px;
            padding: 0.18rem 0.55rem;
            font-size: 0.78rem;
            font-weight: 600;
        }
        .trci-kpi-card__arrow {
            width: 0.85rem;
            height: 0.85rem;
            display: inline-flex;
        }
        .trci-kpi-card__arrow svg {
            width: 100%;
            height: 100%;
        }
        .trci-kpi-card__delta--up {
            background: #E4F5EC;
            color: #0B6E4F;
        }
        .trci-kpi-card__delta--down {
            background: #FCE8E6;
            color: #B42318;
        }
        .trci-kpi-card__delta--flat,
        .trci-kpi-card__delta--muted {
            background: #EEF2F0;
            color: #4A5A52;
        }

        .trci-insight-card {
            background: #FFFFFF;
            border: 1px solid #D5E3DB;
            border-radius: 0.9rem;
            padding: 1rem 1.1rem;
            box-shadow: 0 1px 2px rgba(26, 31, 28, 0.04);
            margin-bottom: 0.75rem;
        }
        .trci-insight-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            align-items: center;
            color: #4A5A52;
            font-size: 0.8rem;
            margin-bottom: 0.85rem;
        }
        .trci-insight-pill {
            background: #E8F0EC;
            color: #0B6E4F;
            border-radius: 999px;
            padding: 0.15rem 0.6rem;
            font-weight: 700;
        }
        .trci-insight-row {
            display: flex;
            gap: 0.7rem;
            margin-bottom: 0.75rem;
        }
        .trci-insight-icon {
            width: 2rem;
            height: 2rem;
            border-radius: 0.5rem;
            background: #E8F0EC;
            color: #0B6E4F;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .trci-insight-icon svg {
            width: 1.05rem;
            height: 1.05rem;
        }
        .trci-insight-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #0B6E4F;
            margin-bottom: 0.15rem;
        }
        .trci-insight-text {
            color: #1A1F1C;
            font-size: 0.95rem;
            line-height: 1.45;
        }
        .trci-insight-foot {
            color: #4A5A52;
            font-size: 0.78rem;
            border-top: 1px solid #E8F0EC;
            padding-top: 0.65rem;
            margin-top: 0.25rem;
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
