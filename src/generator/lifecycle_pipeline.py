"""Orchestration for lifecycle snapshot and customer event generation."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from src.config.settings import AppSettings
from src.generator.customer_events import generate_customer_events
from src.generator.io import read_frame, write_frame, write_parquet_batches
from src.generator.snapshot import generate_customer_monthly_snapshot
from src.utils.logging import get_logger
from src.utils.paths import ensure_directory

logger = get_logger(__name__)


def _require(path: Path, label: str) -> pd.DataFrame:
    """Load a required upstream dataset."""
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {label} at {path}. Generate upstream phases first."
        )
    return read_frame(path)


def generate_lifecycle_datasets(settings: AppSettings) -> dict[str, Path]:
    """Generate monthly snapshot and customer events; persist to disk.

    Returns:
        Paths for ``customer_monthly_snapshot`` and ``customer_events``.
    """
    customers = _require(settings.raw_data_path / "customers.parquet", "customers")
    usage = _require(settings.raw_data_path / "daily_usage.parquet", "daily_usage")
    recharges = _require(settings.raw_data_path / "recharges.parquet", "recharges")
    mobile_money = _require(
        settings.raw_data_path / "mobile_money_transactions.parquet",
        "mobile_money_transactions",
    )

    snapshot = generate_customer_monthly_snapshot(
        settings, customers, usage, recharges, mobile_money
    )
    events = generate_customer_events(
        settings, customers, recharges, mobile_money, snapshot
    )

    processed_dir = ensure_directory(settings.processed_data_path)
    raw_dir = ensure_directory(settings.raw_data_path)

    # Snapshot is derived analytical grain → processed; events stay in raw.
    def _snapshot_batches() -> Iterator[pd.DataFrame]:
        yield snapshot

    snapshot_path, snap_rows = write_parquet_batches(
        _snapshot_batches(),
        processed_dir / "customer_monthly_snapshot.parquet",
    )
    events_path = write_frame(
        events,
        raw_dir / "customer_events.parquet",
        settings.raw_output_format,
    )
    logger.info(
        "Wrote customer_monthly_snapshot (%s rows) → %s",
        f"{snap_rows:,}",
        snapshot_path,
    )
    logger.info("Wrote customer_events (%s rows) → %s", f"{len(events):,}", events_path)
    return {
        "customer_monthly_snapshot": snapshot_path,
        "customer_events": events_path,
    }
