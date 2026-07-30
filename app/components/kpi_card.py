"""Reusable KPI card rendering."""

from __future__ import annotations

import streamlit as st
from src.analytics.types import KpiResult

from app.components.formatting import format_comparison, format_kpi_value


def render_kpi_cards(kpis: list[KpiResult], *, columns: int = 5) -> None:
    """Render a responsive row of KPI metric cards."""
    if not kpis:
        st.warning("No KPI values available for the selected filters.")
        return
    cols = st.columns(min(columns, len(kpis)))
    for col, kpi in zip(cols, kpis, strict=False):
        with col:
            st.metric(
                label=kpi.name,
                value=format_kpi_value(kpi),
                delta=format_comparison(kpi),
                delta_color=_delta_color(kpi),
                help=f"Unit: {kpi.unit} · Period: {kpi.reporting_month}",
            )


def _delta_color(kpi: KpiResult) -> str:
    """Invert delta color for rates where a decrease is favourable."""
    lower_is_better = {"Churn Rate", "Failed Transaction Rate"}
    if kpi.name in lower_is_better:
        return "inverse"
    return "normal"
