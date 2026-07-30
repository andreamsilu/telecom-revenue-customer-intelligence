"""Build processed dimension tables from reference and raw sources."""

from __future__ import annotations

import pandas as pd

from src.utils.logging import get_logger

logger = get_logger(__name__)


def build_dim_date(calendar: pd.DataFrame) -> pd.DataFrame:
    """Build date dimension from the calendar reference."""
    frame = calendar.copy()
    frame["date_key"] = pd.to_datetime(frame["date"]).dt.strftime("%Y%m%d").astype(int)
    frame["date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
    ordered = [
        "date_key",
        "date",
        "day",
        "month",
        "month_name",
        "month_start",
        "quarter",
        "year",
        "day_of_week",
        "is_weekend",
        "is_month_end",
        "reporting_month",
        "seasonality_factor",
        "holiday_period_indicator",
    ]
    dim = frame[ordered].drop_duplicates(subset=["date_key"])
    if dim["date_key"].duplicated().any():
        raise ValueError("dim_date has duplicate date_key values.")
    logger.info("Built dim_date (%s rows)", f"{len(dim):,}")
    return dim


def build_dim_region(regions: pd.DataFrame) -> pd.DataFrame:
    """Build region dimension."""
    dim = regions.copy()
    if dim["region_id"].duplicated().any():
        raise ValueError("dim_region has duplicate region_id values.")
    logger.info("Built dim_region (%s rows)", f"{len(dim):,}")
    return dim


def build_dim_product(products: pd.DataFrame) -> pd.DataFrame:
    """Build product dimension."""
    dim = products.copy()
    if dim["product_id"].duplicated().any():
        raise ValueError("dim_product has duplicate product_id values.")
    logger.info("Built dim_product (%s rows)", f"{len(dim):,}")
    return dim


def build_dim_campaign(campaigns: pd.DataFrame) -> pd.DataFrame:
    """Build campaign dimension."""
    dim = campaigns.copy()
    if dim["campaign_id"].duplicated().any():
        raise ValueError("dim_campaign has duplicate campaign_id values.")
    logger.info("Built dim_campaign (%s rows)", f"{len(dim):,}")
    return dim


def build_dim_customer(
    customers: pd.DataFrame,
    snapshot: pd.DataFrame,
) -> pd.DataFrame:
    """Build customer dimension with latest lifecycle attributes from snapshot."""
    latest = (
        snapshot.sort_values("reporting_month")
        .groupby("customer_id", as_index=False)
        .tail(1)[
            [
                "customer_id",
                "lifecycle_status",
                "value_segment",
                "tenure_months",
                "inactivity_days",
            ]
        ]
    )
    dim = customers.merge(latest, on="customer_id", how="left")
    if dim["customer_id"].duplicated().any():
        raise ValueError("dim_customer has duplicate customer_id values.")
    logger.info("Built dim_customer (%s rows)", f"{len(dim):,}")
    return dim
