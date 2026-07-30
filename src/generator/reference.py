"""Orchestration for reference dataset generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.settings import AppSettings, OutputFormat
from src.generator.calendar import generate_calendar
from src.generator.customers import generate_customers
from src.generator.io import write_frame
from src.generator.products import generate_products
from src.generator.regions import generate_regions
from src.utils.logging import get_logger
from src.utils.paths import ensure_directory

logger = get_logger(__name__)


def generate_reference_datasets(
    settings: AppSettings,
) -> dict[str, Path]:
    """Generate and persist calendar, regions, and products reference data.

    Args:
        settings: Resolved application settings.

    Returns:
        Mapping of dataset name to written path.
    """
    reference_dir = ensure_directory(settings.reference_data_path)
    fmt = OutputFormat.CSV

    calendar = generate_calendar(settings)
    regions = generate_regions()
    products = generate_products(settings)

    paths = {
        "calendar": write_frame(calendar, reference_dir / "calendar.csv", fmt),
        "regions": write_frame(regions, reference_dir / "regions.csv", fmt),
        "products": write_frame(products, reference_dir / "products.csv", fmt),
    }
    for name, path in paths.items():
        logger.info("Wrote %s → %s", name, path)
    return paths


def generate_customer_dataset(
    settings: AppSettings,
    regions: pd.DataFrame | None = None,
) -> Path:
    """Generate and persist the customer master Parquet file.

    Args:
        settings: Resolved application settings.
        regions: Optional pre-loaded regions frame; loaded from disk if omitted.

    Returns:
        Path to the written customers dataset.
    """
    if regions is None:
        regions_path = settings.reference_data_path / "regions.csv"
        if not regions_path.exists():
            raise FileNotFoundError(
                f"Regions reference not found at {regions_path}. "
                "Run generate_reference_data first."
            )
        regions = pd.read_csv(regions_path)

    customers = generate_customers(settings, regions)
    raw_dir = ensure_directory(settings.raw_data_path)
    path = write_frame(
        customers,
        raw_dir / "customers.parquet",
        settings.raw_output_format,
    )
    logger.info("Wrote customers (%s rows) → %s", len(customers), path)
    return path
