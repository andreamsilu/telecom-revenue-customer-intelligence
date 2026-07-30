"""Global filter state and top-of-page controls."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import pandas as pd
import streamlit as st
from src.config.settings import AppSettings

# Bump when default/filter shape changes so stale Streamlit sessions reset.
_FILTER_SCHEMA_VERSION = 3


@dataclass
class FilterState:
    """User-selected global dashboard filters."""

    reporting_month: str
    start_month: str
    end_month: str
    regions: list[str] = field(default_factory=list)
    segments: list[str] = field(default_factory=list)
    account_types: list[str] = field(default_factory=list)
    product_categories: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        """Serialize for session state / recommendation filters."""
        return asdict(self)


def default_filters(settings: AppSettings, available_months: list[str]) -> FilterState:
    """Build default filters from settings and available mart months."""
    reporting = settings.reporting_month.strftime("%Y-%m-%d")
    if available_months and reporting not in available_months:
        reporting = available_months[-1]
    start = (
        available_months[0]
        if available_months
        else settings.start_date.strftime("%Y-%m-01")
    )
    return FilterState(
        reporting_month=reporting,
        start_month=start,
        end_month=reporting,
        regions=[],
        segments=[],
        account_types=[],
        product_categories=[],
    )


def _month_label(month: str) -> str:
    return pd.Timestamp(month).strftime("%b %Y")


def render_global_filters(
    settings: AppSettings,
    *,
    available_months: list[str],
    regions: list[str],
    segments: list[str],
    account_types: list[str],
    product_categories: list[str],
) -> FilterState:
    """Render compact top-of-page filters and return active state."""
    defaults = default_filters(settings, available_months)
    month_options = available_months or [defaults.reporting_month]
    _ensure_session_filters(defaults)

    current = FilterState(**st.session_state["filters"])
    # Drop stale segment values after schema migration to value_segment.
    current.segments = [s for s in current.segments if s in segments]
    if current.reporting_month not in month_options:
        current.reporting_month = defaults.reporting_month
    if current.start_month not in month_options:
        current.start_month = month_options[0]
    if current.end_month not in month_options:
        current.end_month = defaults.reporting_month

    labels = {m: _month_label(m) for m in month_options}
    label_list = [labels[m] for m in month_options]
    value_by_label = {labels[m]: m for m in month_options}

    top_l, top_r = st.columns([6, 1])
    with top_l:
        st.markdown("### Filters")
    with top_r:
        if st.button("Reset filters", use_container_width=True):
            st.session_state["filters"] = dict(st.session_state["filter_defaults"])
            st.rerun()

    col_month, col_range = st.columns([1, 3])
    with col_month:
        reporting_label = st.selectbox(
            "Reporting month",
            options=label_list,
            index=label_list.index(labels[current.reporting_month]),
            help="KPI cards and comparisons use this month.",
        )
        reporting_month = value_by_label[reporting_label]

    with col_range:
        if len(month_options) == 1:
            start_month = end_month = month_options[0]
            st.caption(f"Trend range: {labels[start_month]}")
        else:
            end_default = (
                reporting_month
                if reporting_month != current.reporting_month
                else current.end_month
            )
            if end_default not in month_options:
                end_default = reporting_month
            start_default = current.start_month
            if start_default > end_default:
                start_default = month_options[0]
            start_label, end_label = st.select_slider(
                "Trend date range",
                options=label_list,
                value=(labels[start_default], labels[end_default]),
                help="Charts use this inclusive month range.",
            )
            start_month = value_by_label[start_label]
            end_month = value_by_label[end_label]

    with st.expander("Dimension filters (optional — empty means all)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            selected_regions = st.multiselect(
                "Region",
                options=regions,
                default=[r for r in current.regions if r in regions],
                help="Scopes regional charts and revenue/subscriber KPIs.",
            )
        with c2:
            selected_segments = st.multiselect(
                "Value segment",
                options=segments,
                default=[s for s in current.segments if s in segments],
                help="Filters value-segment charts and base composition.",
            )
        with c3:
            selected_accounts = st.multiselect(
                "Account type",
                options=account_types,
                default=[a for a in current.account_types if a in account_types],
                help="Applied to customer-base composition from dim_customer.",
            )
        with c4:
            selected_products = st.multiselect(
                "Product category",
                options=product_categories,
                default=[
                    p for p in current.product_categories if p in product_categories
                ],
                help="Filters campaign promoted products.",
            )

    st.divider()

    state = FilterState(
        reporting_month=str(reporting_month),
        start_month=str(start_month),
        end_month=str(end_month),
        regions=selected_regions,
        segments=selected_segments,
        account_types=selected_accounts,
        product_categories=selected_products,
    )
    st.session_state["filters"] = state.as_dict()
    return state


def _ensure_session_filters(defaults: FilterState) -> None:
    """Initialize or migrate session filter state."""
    if (
        st.session_state.get("filter_schema_version") != _FILTER_SCHEMA_VERSION
        or "filters" not in st.session_state
    ):
        st.session_state["filter_schema_version"] = _FILTER_SCHEMA_VERSION
        st.session_state["filter_defaults"] = defaults.as_dict()
        st.session_state["filters"] = defaults.as_dict()
