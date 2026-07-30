"""Global filter state and sidebar controls."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import streamlit as st
from src.config.settings import AppSettings


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
    end = reporting
    return FilterState(
        reporting_month=reporting,
        start_month=start,
        end_month=end,
        regions=[],
        segments=[],
        account_types=[],
        product_categories=[],
    )


def render_global_filters(
    settings: AppSettings,
    *,
    available_months: list[str],
    regions: list[str],
    segments: list[str],
    account_types: list[str],
    product_categories: list[str],
) -> FilterState:
    """Render sidebar filters and return the active filter state."""
    defaults = default_filters(settings, available_months)
    if "filter_defaults" not in st.session_state:
        st.session_state["filter_defaults"] = defaults.as_dict()
        st.session_state["filters"] = defaults.as_dict()

    st.sidebar.markdown("### Filters")
    if st.sidebar.button("Reset filters", use_container_width=True):
        st.session_state["filters"] = dict(st.session_state["filter_defaults"])
        st.rerun()

    current = FilterState(**st.session_state["filters"])
    month_options = available_months or [defaults.reporting_month]
    reporting_idx = (
        month_options.index(current.reporting_month)
        if current.reporting_month in month_options
        else len(month_options) - 1
    )
    reporting_month = st.sidebar.selectbox(
        "Reporting month",
        options=month_options,
        index=reporting_idx,
    )
    if len(month_options) == 1:
        start_month = end_month = month_options[0]
        st.sidebar.caption(f"Trend range: {start_month}")
    else:
        start_default = (
            current.start_month
            if current.start_month in month_options
            else month_options[0]
        )
        end_default = (
            current.end_month
            if current.end_month in month_options
            else month_options[-1]
        )
        start_month, end_month = st.sidebar.select_slider(
            "Trend date range",
            options=month_options,
            value=(start_default, end_default),
        )
    selected_regions = st.sidebar.multiselect(
        "Region",
        options=regions,
        default=[r for r in current.regions if r in regions],
        help="Empty selection means all regions.",
    )
    selected_segments = st.sidebar.multiselect(
        "Customer segment",
        options=segments,
        default=[s for s in current.segments if s in segments],
    )
    selected_accounts = st.sidebar.multiselect(
        "Account type",
        options=account_types,
        default=[a for a in current.account_types if a in account_types],
    )
    selected_products = st.sidebar.multiselect(
        "Product category",
        options=product_categories,
        default=[p for p in current.product_categories if p in product_categories],
    )

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
