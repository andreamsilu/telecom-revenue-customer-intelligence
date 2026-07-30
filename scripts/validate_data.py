"""CLI: validate raw prerequisites and processed ETL outputs.

Example:
    python -m scripts.validate_data --profile development
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from src.config import list_profiles, load_settings
from src.generator.io import read_frame
from src.utils.logging import configure_logging, get_logger
from src.validation.etl import validate_processed_layer
from src.validation.reference import ValidationReport

logger = get_logger(__name__)

REQUIRED_RAW = (
    "customers.parquet",
    "daily_usage.parquet",
    "recharges.parquet",
    "mobile_money_transactions.parquet",
    "campaign_responses.parquet",
    "customer_events.parquet",
)
REQUIRED_REFERENCE = (
    "calendar.csv",
    "regions.csv",
    "products.csv",
    "campaigns.csv",
)


def _validate_sources(raw: Path, reference: Path) -> ValidationReport:
    """Check that upstream raw/reference files exist."""
    report = ValidationReport("source_catalog")
    for name in REQUIRED_RAW:
        if not (raw / name).exists():
            report.errors.append(f"Missing raw dataset: {name}")
    for name in REQUIRED_REFERENCE:
        if not (reference / name).exists():
            report.errors.append(f"Missing reference dataset: {name}")
    snapshot = raw.parent / "processed" / "customer_monthly_snapshot.parquet"
    if not snapshot.exists():
        report.errors.append("Missing processed customer_monthly_snapshot.parquet")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    """Validate source data and processed outputs when available."""
    parser = argparse.ArgumentParser(
        description="Validate telecom platform datasets and ETL outputs."
    )
    parser.add_argument(
        "--profile",
        choices=list_profiles(),
        default="development",
        help="Configuration profile (default: development).",
    )
    args = parser.parse_args(argv)

    try:
        settings = load_settings(profile_name=args.profile)
        configure_logging(settings.logging_level, force=True)

        reports = [
            _validate_sources(settings.raw_data_path, settings.reference_data_path)
        ]

        # If marts already exist, validate them too.
        executive = settings.processed_data_path / "executive_kpi_mart.parquet"
        if executive.exists():
            customers = read_frame(settings.raw_data_path / "customers.parquet")
            snapshot = read_frame(
                settings.processed_data_path / "customer_monthly_snapshot.parquet"
            )
            reports.extend(
                validate_processed_layer(
                    settings.processed_data_path,
                    customers=customers,
                    snapshot=snapshot,
                )
            )
        else:
            logger.info(
                "Processed marts not found yet; source validation only. "
                "Run: python -m scripts.run_pipeline --profile %s",
                args.profile,
            )

        failed = False
        for report in reports:
            for warning in report.warnings:
                logger.warning("[%s] %s", report.dataset, warning)
            for error in report.errors:
                logger.error("[%s] %s", report.dataset, error)
                failed = True

        if failed:
            return 1
        logger.info("Data validation succeeded for profile '%s'.", args.profile)
        return 0
    except Exception:
        logger.exception("Data validation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
