"""ETL pipeline orchestration for dimensions, facts, and marts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.settings import AppSettings, OutputFormat
from src.etl.dimensions import (
    build_dim_campaign,
    build_dim_customer,
    build_dim_date,
    build_dim_product,
    build_dim_region,
)
from src.etl.facts import (
    build_fact_campaign_response,
    build_fact_customer_events,
    build_fact_mobile_money,
    build_fact_recharge,
    build_fact_usage_daily,
)
from src.etl.marts import (
    build_churn_monthly_mart,
    build_mobile_money_monthly_mart,
    build_recharge_monthly_mart,
    build_revenue_monthly_mart,
    build_subscriber_monthly_mart,
)
from src.etl.marts_extra import (
    build_campaign_performance_mart,
    build_executive_kpi_mart,
    build_regional_performance_mart,
)
from src.generator.io import read_frame, write_frame
from src.utils.logging import get_logger
from src.utils.paths import ensure_directory

logger = get_logger(__name__)


def _require(path: Path, label: str) -> pd.DataFrame:
    """Load a required dataset or raise."""
    if not path.exists():
        raise FileNotFoundError(f"Missing {label} at {path}")
    return read_frame(path)


def run_etl_pipeline(settings: AppSettings) -> dict[str, Path]:
    """Run the full ETL from raw/reference into processed outputs.

    Returns:
        Mapping of dataset name to written path.
    """
    raw = settings.raw_data_path
    ref = settings.reference_data_path
    processed = ensure_directory(settings.processed_data_path)
    fmt = settings.processed_output_format

    calendar = _require(ref / "calendar.csv", "calendar")
    regions = _require(ref / "regions.csv", "regions")
    products = _require(ref / "products.csv", "products")
    campaigns = _require(ref / "campaigns.csv", "campaigns")
    customers = _require(raw / "customers.parquet", "customers")
    usage = _require(raw / "daily_usage.parquet", "daily_usage")
    recharges = _require(raw / "recharges.parquet", "recharges")
    mobile_money = _require(
        raw / "mobile_money_transactions.parquet", "mobile_money_transactions"
    )
    responses = _require(raw / "campaign_responses.parquet", "campaign_responses")
    events = _require(raw / "customer_events.parquet", "customer_events")
    snapshot = _require(
        processed / "customer_monthly_snapshot.parquet",
        "customer_monthly_snapshot",
    )

    outputs: dict[str, pd.DataFrame] = {
        "dim_date": build_dim_date(calendar),
        "dim_region": build_dim_region(regions),
        "dim_product": build_dim_product(products),
        "dim_campaign": build_dim_campaign(campaigns),
        "dim_customer": build_dim_customer(customers, snapshot),
        "fact_usage_daily": build_fact_usage_daily(usage),
        "fact_recharge": build_fact_recharge(recharges),
        "fact_mobile_money": build_fact_mobile_money(mobile_money),
        "fact_campaign_response": build_fact_campaign_response(responses),
        "fact_customer_events": build_fact_customer_events(events),
        "customer_monthly_snapshot": snapshot,
    }

    revenue_mart = build_revenue_monthly_mart(snapshot)
    subscriber_mart = build_subscriber_monthly_mart(snapshot)
    churn_mart = build_churn_monthly_mart(snapshot)
    recharge_mart = build_recharge_monthly_mart(recharges)
    mm_mart = build_mobile_money_monthly_mart(mobile_money)
    campaign_mart = build_campaign_performance_mart(campaigns, responses)
    regional_mart = build_regional_performance_mart(snapshot, customers)
    executive_mart = build_executive_kpi_mart(
        revenue_mart,
        subscriber_mart,
        churn_mart,
        recharge_mart,
        mm_mart,
    )

    outputs.update(
        {
            "revenue_monthly_mart": revenue_mart,
            "subscriber_monthly_mart": subscriber_mart,
            "churn_monthly_mart": churn_mart,
            "recharge_monthly_mart": recharge_mart,
            "mobile_money_monthly_mart": mm_mart,
            "campaign_performance_mart": campaign_mart,
            "regional_performance_mart": regional_mart,
            "executive_kpi_mart": executive_mart,
        }
    )

    paths: dict[str, Path] = {}
    for name, frame in outputs.items():
        suffix = ".parquet" if fmt == OutputFormat.PARQUET else ".csv"
        path = write_frame(frame, processed / f"{name}{suffix}", fmt)
        paths[name] = path
        logger.info("Wrote %s → %s", name, path)

    return paths
