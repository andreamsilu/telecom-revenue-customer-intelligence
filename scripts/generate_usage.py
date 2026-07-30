"""CLI: generate daily usage dataset.

Example:
    python -m scripts.generate_usage --profile development
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from src.config import list_profiles, load_settings
from src.generator.io import read_frame
from src.generator.transactions import generate_usage_dataset
from src.utils.logging import configure_logging, get_logger
from src.validation.transactions import (
    check_usage_seasonality,
    validate_daily_usage,
)

logger = get_logger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate and validate daily usage for a profile."""
    parser = argparse.ArgumentParser(description="Generate synthetic daily usage data.")
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
        path = generate_usage_dataset(settings)

        usage = read_frame(path)
        customers = read_frame(settings.raw_data_path / "customers.parquet")
        products = read_frame(settings.reference_data_path / "products.csv")
        report = validate_daily_usage(usage, customers, products)
        for warning in report.warnings:
            logger.warning("[%s] %s", report.dataset, warning)
        for error in report.errors:
            logger.error("[%s] %s", report.dataset, error)
        if not report.ok:
            return 1

        seasonality = check_usage_seasonality(usage)
        for message in seasonality.messages:
            logger.warning("[seasonality] %s", message)
        if not seasonality.ok and settings.validation_strictness.value == "strict":
            logger.error("Seasonality check failed under strict validation.")
            return 1

        logger.info(
            "Usage generation succeeded (%s rows). Dec data_mb mean=%.2f, Jan=%.2f",
            f"{len(usage):,}",
            seasonality.december_mean,
            seasonality.january_mean,
        )
        return 0
    except Exception:
        logger.exception("Usage generation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
