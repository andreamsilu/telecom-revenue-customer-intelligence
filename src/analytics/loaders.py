"""Load processed analytical marts for analytics services."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.settings import AppSettings
from src.generator.io import read_frame


def processed_path(settings: AppSettings, name: str) -> Path:
    """Return the parquet path for a processed dataset stem."""
    return settings.processed_data_path / f"{name}.parquet"


def load_mart(settings: AppSettings, name: str) -> pd.DataFrame:
    """Load a processed mart by name."""
    path = processed_path(settings, name)
    if not path.exists():
        raise FileNotFoundError(
            f"Missing mart {name} at {path}. Run the ETL pipeline first."
        )
    return read_frame(path)


def row_for_month(frame: pd.DataFrame, reporting_month: str) -> pd.Series:
    """Return the unique row for a reporting month.

    Raises:
        KeyError: If the month is absent or duplicated.
    """
    month = pd.Timestamp(reporting_month).strftime("%Y-%m-%d")
    matched = frame[frame["reporting_month"].astype(str) == month]
    if matched.empty:
        raise KeyError(f"reporting_month {month} not found in mart.")
    if len(matched) > 1:
        raise KeyError(f"reporting_month {month} is not unique in mart.")
    return matched.iloc[0]
