"""Shared helpers for analytical Streamlit pages."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import streamlit as st
from src.recommendations import generate_recommendations
from src.recommendations.models import Recommendation

from app.components.filters import FilterState
from app.components.insight_panel import render_insight_panel
from app.components.layout import (
    render_data_freshness,
    render_empty_state,
    render_page_header,
)
from app.services.data_loader import FilterOptions, MartBundle, load_mart_bundle


def load_page_marts(
    options: FilterOptions,
    *,
    profile_name: str,
    title: str,
    subtitle: str,
) -> MartBundle | None:
    """Render header/freshness and load marts, or show an empty state."""
    render_page_header(title, subtitle)
    render_data_freshness(list(options.mart_paths))
    try:
        return load_mart_bundle(profile_name)
    except FileNotFoundError as exc:
        render_empty_state(str(exc))
        return None


def page_recommendations(
    marts: MartBundle,
    filters: FilterState,
    *,
    module: str | None = None,
) -> list[Recommendation]:
    """Generate recommendations and optionally keep one module."""
    recommendations = generate_recommendations(
        reporting_month=filters.reporting_month,
        executive_mart=marts.executive,
        revenue_mart=marts.revenue,
        subscriber_mart=marts.subscriber,
        churn_mart=marts.churn,
        recharge_mart=marts.recharge,
        regional_mart=marts.regional,
        campaign_mart=marts.campaign,
    )
    if filters.regions:
        recommendations = [
            rec
            for rec in recommendations
            if rec.supporting_filters.get("region") in filters.regions
            or "region" not in rec.supporting_filters
        ]
    if module:
        modular = [rec for rec in recommendations if rec.module == module]
        if modular:
            return modular
    return recommendations


def render_top_insight(
    marts: MartBundle,
    filters: FilterState,
    *,
    module: str | None = None,
) -> None:
    """Show the top Finding → Impact → Action for the page."""
    recommendations = page_recommendations(marts, filters, module=module)
    render_insight_panel(recommendations[0] if recommendations else None)


def safe_kpi_section(
    label: str,
    builder: Callable[[], list],
) -> None:
    """Render a KPI section with KeyError protection."""
    st.subheader(label)
    try:
        cards = builder()
    except KeyError as exc:
        render_empty_state(f"KPI section unavailable: {exc}")
        return
    from app.components.kpi_card import render_kpi_cards

    render_kpi_cards(cards, columns=min(5, max(1, len(cards))))


def trend_frame(
    frame: pd.DataFrame,
    filters: FilterState,
) -> pd.DataFrame:
    """Filter a monthly mart to the selected trend range."""
    from src.analytics.breakdowns import filter_month_range

    return filter_month_range(
        frame,
        start_month=filters.start_month,
        end_month=filters.end_month,
    )
