"""Orchestration for mobile money, campaigns, and campaign responses."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.settings import AppSettings, OutputFormat
from src.generator.campaign_responses import generate_campaign_responses
from src.generator.campaigns import generate_campaigns
from src.generator.io import read_frame, write_frame, write_parquet_batches
from src.generator.mobile_money import iter_mobile_money_batches
from src.utils.logging import get_logger
from src.utils.paths import ensure_directory

logger = get_logger(__name__)


def _require_frame(path: Path, label: str) -> pd.DataFrame:
    """Load a required upstream dataset or raise a helpful error."""
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {label} at {path}. Generate upstream datasets first."
        )
    return read_frame(path)


def generate_mobile_money_dataset(settings: AppSettings) -> Path:
    """Generate and persist mobile money transactions parquet."""
    customers = _require_frame(
        settings.raw_data_path / "customers.parquet", "customers"
    )
    regions = _require_frame(settings.reference_data_path / "regions.csv", "regions")
    raw_dir = ensure_directory(settings.raw_data_path)
    path = raw_dir / "mobile_money_transactions.parquet"
    written, rows = write_parquet_batches(
        iter_mobile_money_batches(settings, customers, regions),
        path,
    )
    logger.info("Wrote mobile_money_transactions (%s rows) → %s", f"{rows:,}", written)
    return written


def generate_campaign_datasets(settings: AppSettings) -> dict[str, Path]:
    """Generate campaign catalogue and campaign-response outcomes.

    Returns:
        Mapping with ``campaigns`` and ``campaign_responses`` paths.
    """
    customers = _require_frame(
        settings.raw_data_path / "customers.parquet", "customers"
    )
    products = _require_frame(settings.reference_data_path / "products.csv", "products")

    campaigns = generate_campaigns(settings)
    product_ids = set(products["product_id"].astype(str))
    missing_products = set(campaigns["promoted_product"].astype(str)) - product_ids
    if missing_products:
        raise ValueError(
            f"Campaign promoted_product values missing from products: "
            f"{sorted(missing_products)}"
        )

    reference_dir = ensure_directory(settings.reference_data_path)
    raw_dir = ensure_directory(settings.raw_data_path)

    campaigns_path = write_frame(
        campaigns,
        reference_dir / "campaigns.csv",
        OutputFormat.CSV,
    )
    responses = generate_campaign_responses(settings, customers, campaigns)
    responses_path = write_frame(
        responses,
        raw_dir / "campaign_responses.parquet",
        settings.raw_output_format,
    )
    logger.info("Wrote campaigns → %s", campaigns_path)
    logger.info(
        "Wrote campaign_responses (%s rows) → %s",
        f"{len(responses):,}",
        responses_path,
    )
    return {"campaigns": campaigns_path, "campaign_responses": responses_path}
