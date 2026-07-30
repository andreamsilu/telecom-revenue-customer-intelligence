"""CLI: generate calendar, regions, and products reference datasets.

Example:
    python -m scripts.generate_reference_data --profile development
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from src.config import list_profiles, load_settings
from src.generator import generate_reference_datasets
from src.generator.io import read_frame
from src.utils.logging import configure_logging, get_logger
from src.validation import (
    validate_calendar,
    validate_products,
    validate_regions,
)

logger = get_logger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate and validate reference datasets for a profile."""
    parser = argparse.ArgumentParser(
        description="Generate calendar, regions, and products reference data."
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
        paths = generate_reference_datasets(settings)

        reports = [
            validate_calendar(read_frame(paths["calendar"])),
            validate_regions(read_frame(paths["regions"])),
            validate_products(read_frame(paths["products"])),
        ]
        for report in reports:
            for warning in report.warnings:
                logger.warning("[%s] %s", report.dataset, warning)
            for error in report.errors:
                logger.error("[%s] %s", report.dataset, error)
            if not report.ok:
                return 1

        logger.info(
            "Reference data generation succeeded for profile '%s'.",
            args.profile,
        )
        return 0
    except Exception:
        logger.exception("Reference data generation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
