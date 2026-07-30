"""Orchestration for usage and recharge dataset generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.settings import AppSettings
from src.generator.io import read_frame, write_parquet_batches
from src.generator.recharges import iter_recharge_batches
from src.generator.usage import iter_usage_batches
from src.utils.logging import get_logger
from src.utils.paths import ensure_directory

logger = get_logger(__name__)


def _require_frame(path: Path, label: str) -> pd.DataFrame:
    """Load a required upstream dataset or raise a helpful error."""
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {label} at {path}. Generate upstream Phase 2 datasets first."
        )
    return read_frame(path)


def generate_usage_dataset(settings: AppSettings) -> Path:
    """Generate and persist daily usage parquet using batched writes.

    Args:
        settings: Resolved application settings.

    Returns:
        Path to ``daily_usage.parquet``.
    """
    customers = _require_frame(
        settings.raw_data_path / "customers.parquet", "customers"
    )
    regions = _require_frame(settings.reference_data_path / "regions.csv", "regions")
    products = _require_frame(settings.reference_data_path / "products.csv", "products")

    raw_dir = ensure_directory(settings.raw_data_path)
    path = raw_dir / "daily_usage.parquet"
    written, rows = write_parquet_batches(
        iter_usage_batches(settings, customers, regions, products),
        path,
    )
    logger.info("Wrote daily_usage (%s rows) → %s", f"{rows:,}", written)
    return written


def generate_recharge_dataset(settings: AppSettings) -> Path:
    """Generate and persist recharges parquet using batched writes.

    Args:
        settings: Resolved application settings.

    Returns:
        Path to ``recharges.parquet``.
    """
    customers = _require_frame(
        settings.raw_data_path / "customers.parquet", "customers"
    )
    products = _require_frame(settings.reference_data_path / "products.csv", "products")

    raw_dir = ensure_directory(settings.raw_data_path)
    path = raw_dir / "recharges.parquet"
    written, rows = write_parquet_batches(
        iter_recharge_batches(settings, customers, products),
        path,
    )
    logger.info("Wrote recharges (%s rows) → %s", f"{rows:,}", written)
    return written
