"""ETL package for dimensions, facts, and analytical marts."""

from __future__ import annotations

from src.etl.pipeline import run_etl_pipeline

__all__ = ["run_etl_pipeline"]
