"""Shared page layout helpers — production executive shell."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# Fictional operator brand for executive presentation.
OPERATOR_NAME = "UmojaTel"
PRODUCT_NAME = "Revenue & Customer Intelligence"
PRODUCT_SHORT = "RCI"

_THEME_PATH = Path(__file__).resolve().parent.parent / "assets" / "theme.css"
_THEME_CSS = _THEME_PATH.read_text(encoding="utf-8")


def inject_theme_css() -> None:
    """Apply production executive theme (main canvas + dark operator sidebar)."""
    st.markdown(f"<style>{_THEME_CSS}</style>", unsafe_allow_html=True)


def render_sidebar_brand(*, reporting_month: str | None = None) -> None:
    """Render operator-branded sidebar header."""
    period = (
        pd.Timestamp(reporting_month).strftime("%b %Y")
        if reporting_month
        else "Current period"
    )
    st.sidebar.markdown(
        f"""
        <div class="trci-sidebar-mark">
          <div class="trci-sidebar-logo">UT</div>
          <div>
            <div class="trci-sidebar-brand">{OPERATOR_NAME}</div>
            <div class="trci-sidebar-meta">{PRODUCT_SHORT} · {period}</div>
          </div>
        </div>
        <div class="trci-sidebar-label">Workspace</div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_footer() -> None:
    """Quiet production footer inside the sidebar."""
    st.sidebar.markdown(
        f'<div class="trci-sidebar-foot">{OPERATOR_NAME} {PRODUCT_SHORT}<br/>'
        "Confidential · Internal use only</div>",
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str, *, as_of: str | None = None) -> None:
    """Render an executive page hero."""
    status = ""
    if as_of:
        status = (
            f'<div class="trci-page-status">'
            f'<span class="trci-status-dot"></span>Data as of {as_of}</div>'
        )
    st.markdown(
        f"""
        <div class="trci-page-hero">
          <div>
            <div class="trci-page-kicker">{OPERATOR_NAME} · {PRODUCT_NAME}</div>
            <div class="trci-page-title">{title}</div>
            <div class="trci-page-sub">{subtitle}</div>
          </div>
          {status}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_data_freshness(paths: list[Path]) -> str | None:
    """Return a compact as-of stamp for the page hero (no noisy caption)."""
    existing = [path for path in paths if path.exists()]
    if not existing:
        return None
    newest = max(path.stat().st_mtime for path in existing)
    return datetime.fromtimestamp(newest).strftime("%d %b %Y %H:%M")


def render_empty_state(message: str) -> None:
    """Show a clean empty/missing-data message."""
    safe = message.replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(
        f'<div class="trci-empty">{safe}</div>',
        unsafe_allow_html=True,
    )


def render_section_label(label: str) -> None:
    """Render a production section eyebrow above Streamlit subheaders."""
    st.markdown(
        f'<div class="trci-section-label">{label}</div>',
        unsafe_allow_html=True,
    )


def render_app_footer() -> None:
    """Discreet legal footer for the main canvas."""
    st.markdown(
        f'<div class="trci-footer">{OPERATOR_NAME} {PRODUCT_NAME} · '
        "Internal executive decision support · Confidential</div>",
        unsafe_allow_html=True,
    )
