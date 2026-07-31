"""Reusable KPI card rendering with SVG icons (no emojis)."""

from __future__ import annotations

import html
import re

import streamlit as st
from src.analytics.types import KpiResult

from app.components.formatting import format_comparison, format_kpi_value

# Inline SVG icons — stroke-based, monochrome (colored via CSS currentColor).
_ICONS: dict[str, str] = {
    "revenue": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M4 19V9m5 10V5m5 14v-8m5 8V11"/>'
        "</svg>"
    ),
    "arpu": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M4 19V5m0 14h16M8 15l3-4 3 2 4-6"/>'
        "</svg>"
    ),
    "subscribers": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="3" fill="none" stroke="currentColor" '
        'stroke-width="1.75"/>'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>'
        "</svg>"
    ),
    "active": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 '
        '10 10z"/>'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l4 2"/>'
        "</svg>"
    ),
    "churn": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M16 17l5-5-5-5M21 12H9M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>'
        "</svg>"
    ),
    "recharge": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M13 2 4 14h7l-1 8 10-14h-7l1-6z"/>'
        "</svg>"
    ),
    "mobile_money": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<rect x="6" y="2" width="12" height="20" rx="2" fill="none" '
        'stroke="currentColor" stroke-width="1.75"/>'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" d="M10 18h4"/>'
        "</svg>"
    ),
    "campaign": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M11 5.08A8 8 0 1 0 18.92 13H13a2 2 0 0 1-2-2V5.08z"/>'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M15 2.46A8 8 0 0 1 21.54 9H17a2 2 0 0 1-2-2V2.46z"/>'
        "</svg>"
    ),
    "region": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M12 21s7-4.5 7-11a7 7 0 1 0-14 0c0 6.5 7 11 7 11z"/>'
        '<circle cx="12" cy="10" r="2.5" fill="none" stroke="currentColor" '
        'stroke-width="1.75"/>'
        "</svg>"
    ),
    "recommendation": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5V15h8v-1.5A6 6 0 0 0 12 3z"/>'
        "</svg>"
    ),
    "default": (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'd="M4 19h16M6 16V9m6 7V5m6 11v-4"/>'
        "</svg>"
    ),
}

_NAME_ICON_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"churn|failed transaction", re.I), "churn"),
    (re.compile(r"arpu|average recharge", re.I), "arpu"),
    (re.compile(r"revenue|roi|fee|attributed", re.I), "revenue"),
    (re.compile(r"active|activity|frequency", re.I), "active"),
    (re.compile(r"subscriber|customer|user|base", re.I), "subscribers"),
    (re.compile(r"recharge|top-?up", re.I), "recharge"),
    (re.compile(r"mobile money|wallet", re.I), "mobile_money"),
    (re.compile(r"campaign|conversion|portfolio", re.I), "campaign"),
    (re.compile(r"region|scope", re.I), "region"),
    (re.compile(r"recommend|critical|priority|department", re.I), "recommendation"),
]


def render_kpi_cards(kpis: list[KpiResult], *, columns: int = 5) -> None:
    """Render a responsive row of styled KPI cards with SVG icons."""
    if not kpis:
        st.warning("No KPI values available for the selected filters.")
        return
    cols = st.columns(min(columns, len(kpis)))
    for col, kpi in zip(cols, kpis, strict=False):
        with col:
            st.markdown(_card_html(kpi), unsafe_allow_html=True)


def render_summary_cards(
    items: list[tuple[str, str, str]],
    *,
    columns: int = 4,
) -> None:
    """Render simple labeled summary cards (label, value, icon_key)."""
    if not items:
        return
    cols = st.columns(min(columns, len(items)))
    for col, (label, value, icon_key) in zip(cols, items, strict=False):
        with col:
            st.markdown(
                _summary_card_html(label, value, icon_key),
                unsafe_allow_html=True,
            )


def _card_html(kpi: KpiResult) -> str:
    icon = _ICONS[_icon_key_for_name(kpi.name)]
    value = html.escape(format_kpi_value(kpi))
    label = html.escape(kpi.name)
    comparison = format_comparison(kpi)
    tone = _comparison_tone(kpi)
    arrow = _arrow_svg(tone)
    delta = html.escape(comparison)
    tip = html.escape(f"Unit: {kpi.unit} · Period: {kpi.reporting_month}")
    return f"""
    <div class="trci-kpi-card" title="{tip}">
      <div class="trci-kpi-card__head">
        <div class="trci-kpi-card__icon">{icon}</div>
        <div class="trci-kpi-card__label">{label}</div>
      </div>
      <div class="trci-kpi-card__value">{value}</div>
      <div class="trci-kpi-card__delta trci-kpi-card__delta--{tone}">
        <span class="trci-kpi-card__arrow">{arrow}</span>
        <span>{delta}</span>
      </div>
    </div>
    """


def _summary_card_html(label: str, value: str, icon_key: str) -> str:
    icon = _ICONS.get(icon_key, _ICONS["default"])
    return f"""
    <div class="trci-kpi-card">
      <div class="trci-kpi-card__head">
        <div class="trci-kpi-card__icon">{icon}</div>
        <div class="trci-kpi-card__label">{html.escape(label)}</div>
      </div>
      <div class="trci-kpi-card__value">{html.escape(value)}</div>
    </div>
    """


def _icon_key_for_name(name: str) -> str:
    for pattern, key in _NAME_ICON_RULES:
        if pattern.search(name):
            return key
    return "default"


def _comparison_tone(kpi: KpiResult) -> str:
    """Return css tone: up / down / flat / muted."""
    if kpi.comparison_value is None:
        return "muted"
    value = kpi.comparison_value
    if abs(value) < 1e-12:
        return "flat"
    lower_is_better = kpi.name in {"Churn Rate", "Failed Transaction Rate"}
    improving = value < 0 if lower_is_better else value > 0
    return "up" if improving else "down"


def _arrow_svg(tone: str) -> str:
    if tone == "up":
        path = "M12 19V5M6 11l6-6 6 6"
    elif tone == "down":
        path = "M12 5v14M6 13l6 6 6-6"
    else:
        path = "M5 12h14"
    return (
        '<svg viewBox="0 0 24 24" aria-hidden="true">'
        f'<path fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" d="{path}"/>'
        "</svg>"
    )
