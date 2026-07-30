"""Cached data-loading wrappers for Streamlit (no KPI calculations)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st
from src.analytics.loaders import load_mart, processed_path
from src.config import load_settings
from src.config.settings import AppSettings
from src.generator.io import read_frame


@dataclass(frozen=True)
class MartBundle:
    """Processed marts required by the Executive Overview."""

    executive: pd.DataFrame
    revenue: pd.DataFrame
    subscriber: pd.DataFrame
    churn: pd.DataFrame
    recharge: pd.DataFrame
    mobile_money: pd.DataFrame
    regional: pd.DataFrame
    campaign: pd.DataFrame
    segment: pd.DataFrame


@dataclass(frozen=True)
class FilterOptions:
    """Distinct filter values sourced from dimensions / marts."""

    months: list[str]
    regions: list[str]
    segments: list[str]
    account_types: list[str]
    product_categories: list[str]
    mart_paths: tuple[Path, ...]


@st.cache_data(show_spinner="Loading processed marts…")
def load_mart_bundle(profile_name: str = "development") -> MartBundle:
    """Load analytical marts once per Streamlit session/cache key."""
    settings = _settings(profile_name)
    return MartBundle(
        executive=load_mart(settings, "executive_kpi_mart"),
        revenue=load_mart(settings, "revenue_monthly_mart"),
        subscriber=load_mart(settings, "subscriber_monthly_mart"),
        churn=load_mart(settings, "churn_monthly_mart"),
        recharge=load_mart(settings, "recharge_monthly_mart"),
        mobile_money=load_mart(settings, "mobile_money_monthly_mart"),
        regional=load_mart(settings, "regional_performance_mart"),
        campaign=load_mart(settings, "campaign_performance_mart"),
        segment=load_mart(settings, "value_segment_monthly_mart"),
    )


@st.cache_data(show_spinner=False)
def load_filter_options(profile_name: str = "development") -> FilterOptions:
    """Load distinct values for global sidebar filters."""
    settings = _settings(profile_name)
    executive = load_mart(settings, "executive_kpi_mart")
    months = sorted(executive["reporting_month"].astype(str).unique().tolist())
    regions = _distinct_from_dim(settings, "dim_customer", "region")
    segments = _distinct_from_dim(settings, "dim_customer", "customer_segment")
    accounts = _distinct_from_dim(settings, "dim_customer", "account_type")
    products = _distinct_from_dim(settings, "dim_product", "product_category")
    paths = tuple(
        processed_path(settings, name)
        for name in (
            "executive_kpi_mart",
            "revenue_monthly_mart",
            "regional_performance_mart",
            "campaign_performance_mart",
            "value_segment_monthly_mart",
        )
    )
    return FilterOptions(
        months=months,
        regions=regions,
        segments=segments,
        account_types=accounts,
        product_categories=products,
        mart_paths=paths,
    )


def marts_available(profile_name: str = "development") -> bool:
    """Return True when the executive mart exists on disk."""
    settings = _settings(profile_name)
    return processed_path(settings, "executive_kpi_mart").exists()


def _settings(profile_name: str) -> AppSettings:
    return load_settings(profile_name=profile_name)  # type: ignore[arg-type]


def _distinct_from_dim(settings: AppSettings, name: str, column: str) -> list[str]:
    path = processed_path(settings, name)
    if not path.exists():
        return []
    frame = read_frame(path)
    if column not in frame.columns:
        return []
    return sorted(frame[column].dropna().astype(str).unique().tolist())
