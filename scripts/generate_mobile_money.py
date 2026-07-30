"""CLI: generate mobile money transactions.

Example:
    python -m scripts.generate_mobile_money --profile development
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from src.config import list_profiles, load_settings
from src.generator.engagement import generate_mobile_money_dataset
from src.generator.io import read_frame
from src.utils.logging import configure_logging, get_logger
from src.validation.engagement import validate_mobile_money

logger = get_logger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate and validate mobile money transactions for a profile."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic mobile money transactions."
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
        path = generate_mobile_money_dataset(settings)
        frame = read_frame(path)
        customers = read_frame(settings.raw_data_path / "customers.parquet")
        report = validate_mobile_money(frame, customers)
        for warning in report.warnings:
            logger.warning("[%s] %s", report.dataset, warning)
        for error in report.errors:
            logger.error("[%s] %s", report.dataset, error)
        if not report.ok:
            return 1

        fee_total = float(frame["fee_revenue"].sum())
        logger.info(
            "Mobile money generation succeeded (%s rows). Fee revenue=%.2f TZS",
            f"{len(frame):,}",
            fee_total,
        )
        return 0
    except Exception:
        logger.exception("Mobile money generation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
