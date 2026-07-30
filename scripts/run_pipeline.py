"""CLI: run the ETL pipeline into processed dimensions, facts, and marts.

Example:
    python -m scripts.run_pipeline --profile development
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from src.config import list_profiles, load_settings
from src.etl.pipeline import run_etl_pipeline
from src.generator.io import read_frame
from src.utils.logging import configure_logging, get_logger
from src.validation.etl import validate_processed_layer

logger = get_logger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Execute ETL and validate processed outputs."""
    parser = argparse.ArgumentParser(
        description="Run ETL pipeline for dimensions, facts, and analytical marts."
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
        paths = run_etl_pipeline(settings)
        logger.info("ETL wrote %s datasets.", len(paths))

        customers = read_frame(settings.raw_data_path / "customers.parquet")
        snapshot = read_frame(
            settings.processed_data_path / "customer_monthly_snapshot.parquet"
        )
        reports = validate_processed_layer(
            settings.processed_data_path,
            customers=customers,
            snapshot=snapshot,
        )
        failed = False
        for report in reports:
            for warning in report.warnings:
                logger.warning("[%s] %s", report.dataset, warning)
            for error in report.errors:
                logger.error("[%s] %s", report.dataset, error)
                failed = True
        if failed and settings.validation_strictness.value == "strict":
            return 1

        logger.info("ETL pipeline succeeded for profile '%s'.", args.profile)
        return 0
    except Exception:
        logger.exception("ETL pipeline failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
