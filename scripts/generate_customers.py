"""CLI: generate synthetic customer master data.

Example:
    python -m scripts.generate_customers --profile development
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from src.config import list_profiles, load_settings
from src.generator import generate_customer_dataset
from src.generator.io import read_frame
from src.utils.logging import configure_logging, get_logger
from src.validation import validate_customers

logger = get_logger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Generate and validate the customer master for a profile."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic customer master data."
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

        regions_path = settings.reference_data_path / "regions.csv"
        if not regions_path.exists():
            raise FileNotFoundError(
                f"Missing {regions_path}. "
                "Run: python -m scripts.generate_reference_data "
                f"--profile {args.profile}"
            )

        regions = read_frame(regions_path)
        path = generate_customer_dataset(settings, regions=regions)
        customers = read_frame(path)
        report = validate_customers(
            customers,
            regions,
            expected_count=settings.subscriber_count,
        )
        for warning in report.warnings:
            logger.warning("[%s] %s", report.dataset, warning)
        for error in report.errors:
            logger.error("[%s] %s", report.dataset, error)
        if not report.ok:
            return 1

        prepaid_share = float((customers["account_type"] == "Prepaid").mean())
        logger.info("Prepaid share: %.1f%%", prepaid_share * 100)
        logger.info(
            "Customer generation succeeded for profile '%s' (%s rows).",
            args.profile,
            len(customers),
        )
        return 0
    except Exception:
        logger.exception("Customer generation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
