"""Copy slim dashboard marts into data/exports for demos and packaging."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from src.config import load_settings
from src.utils.logging import get_logger
from src.utils.paths import ensure_directory

logger = get_logger(__name__)

DASHBOARD_MARTS = (
    "executive_kpi_mart.parquet",
    "revenue_monthly_mart.parquet",
    "subscriber_monthly_mart.parquet",
    "churn_monthly_mart.parquet",
    "recharge_monthly_mart.parquet",
    "mobile_money_monthly_mart.parquet",
    "regional_performance_mart.parquet",
    "campaign_performance_mart.parquet",
    "value_segment_monthly_mart.parquet",
    "dim_customer.parquet",
    "dim_product.parquet",
    "dim_region.parquet",
)


def export_dashboard_marts(profile_name: str = "development") -> Path:
    """Export allowlisted marts to ``data/exports/dashboard``."""
    settings = load_settings(profile_name=profile_name)  # type: ignore[arg-type]
    source = Path(settings.processed_data_path)
    target = ensure_directory(Path(settings.export_path) / "dashboard")
    copied = 0
    for name in DASHBOARD_MARTS:
        src = source / name
        if not src.exists():
            logger.warning("Skipping missing mart %s", src)
            continue
        shutil.copy2(src, target / name)
        copied += 1
        logger.info("Exported %s", name)
    logger.info("Exported %s dashboard files to %s", copied, target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="development")
    args = parser.parse_args()
    export_dashboard_marts(args.profile)


if __name__ == "__main__":
    main()
