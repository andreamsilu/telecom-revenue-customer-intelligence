"""Plotly chart wrappers for Streamlit pages."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.components.formatting import format_tzs

_CHART_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#1A1F1C"},
    "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
}


def render_revenue_trend(frame: pd.DataFrame) -> None:
    """Line chart of monthly total revenue."""
    if frame.empty:
        st.warning("No trend data for the selected date range.")
        return
    fig = px.line(
        frame,
        x="reporting_month",
        y="total_revenue",
        markers=True,
        title="Total revenue trend",
        labels={"reporting_month": "Month", "total_revenue": "Revenue (TZS)"},
    )
    fig.update_layout(**_CHART_LAYOUT, hovermode="x unified")
    fig.update_traces(
        hovertemplate="%{x}<br>%{y:,.0f} TZS<extra></extra>",
        line_color="#0B6E4F",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_regional_bar(frame: pd.DataFrame) -> None:
    """Horizontal bar of regional revenue for the reporting month."""
    if frame.empty:
        st.warning("No regional data for the selected filters.")
        return
    ordered = frame.sort_values("total_revenue", ascending=True)
    fig = px.bar(
        ordered,
        x="total_revenue",
        y="region",
        orientation="h",
        title="Regional revenue comparison",
        labels={"total_revenue": "Revenue (TZS)", "region": "Region"},
        text=ordered["total_revenue"].map(lambda v: format_tzs(float(v))),
    )
    fig.update_layout(**_CHART_LAYOUT)
    fig.update_traces(marker_color="#0B6E4F", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def render_segment_bar(frame: pd.DataFrame) -> None:
    """Bar chart of revenue by value segment."""
    if frame.empty:
        st.warning("No segment breakdown for the selected filters.")
        return
    fig = px.bar(
        frame,
        x="value_segment",
        y="total_revenue",
        title="Revenue by value segment",
        labels={"value_segment": "Segment", "total_revenue": "Revenue (TZS)"},
    )
    fig.update_layout(**_CHART_LAYOUT)
    fig.update_traces(marker_color="#3D8B6E")
    st.plotly_chart(fig, use_container_width=True)


def render_subscriber_mix(frame: pd.DataFrame) -> None:
    """Simple subscriber vs ARPU dual-axis trend when columns exist."""
    if frame.empty or "arpu" not in frame.columns:
        return
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frame["reporting_month"],
            y=frame["total_subscribers"],
            name="Subscribers",
            mode="lines+markers",
            line={"color": "#0B6E4F"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=frame["reporting_month"],
            y=frame["arpu"],
            name="ARPU",
            mode="lines+markers",
            yaxis="y2",
            line={"color": "#C45C26"},
        )
    )
    fig.update_layout(
        **_CHART_LAYOUT,
        title="Subscribers vs ARPU",
        yaxis={"title": "Subscribers"},
        yaxis2={"title": "ARPU (TZS)", "overlaying": "y", "side": "right"},
        legend={"orientation": "h"},
    )
    st.plotly_chart(fig, use_container_width=True)
