"""Shared IO helpers for synthetic data generation."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from src.config.settings import OutputFormat


def write_frame(
    frame: pd.DataFrame,
    path: Path,
    output_format: OutputFormat,
) -> Path:
    """Write a DataFrame to CSV or Parquet and return the output path.

    Args:
        frame: Data to persist.
        path: Destination path including filename stem or full filename.
        output_format: On-disk format.

    Returns:
        Absolute path written.
    """
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    suffix = ".csv" if output_format == OutputFormat.CSV else ".parquet"
    if path.suffix.lower() not in {".csv", ".parquet"}:
        path = path.with_suffix(suffix)
    elif output_format == OutputFormat.CSV and path.suffix.lower() != ".csv":
        path = path.with_suffix(".csv")
    elif output_format == OutputFormat.PARQUET and path.suffix.lower() != ".parquet":
        path = path.with_suffix(".parquet")

    if output_format == OutputFormat.CSV:
        frame.to_csv(path, index=False)
    else:
        frame.to_parquet(path, index=False)

    return path


def write_parquet_batches(
    batches: Iterator[pd.DataFrame],
    path: Path,
) -> tuple[Path, int]:
    """Write successive DataFrame batches to a single Parquet file.

    Args:
        batches: Iterator of non-empty DataFrames with a shared schema.
        path: Destination parquet path.

    Returns:
        Tuple of (written path, total row count).
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    path = path.resolve()
    if path.suffix.lower() != ".parquet":
        path = path.with_suffix(".parquet")
    path.parent.mkdir(parents=True, exist_ok=True)

    writer: pq.ParquetWriter | None = None
    total_rows = 0
    try:
        for frame in batches:
            if frame.empty:
                continue
            table = pa.Table.from_pandas(frame, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(path, table.schema)
            writer.write_table(table)
            total_rows += len(frame)
    finally:
        if writer is not None:
            writer.close()

    if total_rows == 0:
        # Persist an empty file with an explicit empty frame for downstream checks.
        pd.DataFrame().to_parquet(path, index=False)

    return path, total_rows


def read_frame(path: Path) -> pd.DataFrame:
    """Read a CSV or Parquet file into a DataFrame."""
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported file format for {path}")
