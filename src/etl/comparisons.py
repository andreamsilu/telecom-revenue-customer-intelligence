"""Period comparison helpers for analytical marts."""

from __future__ import annotations

import pandas as pd


def add_monthly_comparisons(
    frame: pd.DataFrame,
    *,
    month_col: str,
    value_cols: list[str],
    partition_cols: list[str] | None = None,
) -> pd.DataFrame:
    """Add MoM, YoY, rolling, and YTD comparison columns for value metrics.

    Args:
        frame: Input mart frame.
        month_col: Month-start date column name.
        value_cols: Numeric columns to enrich.
        partition_cols: Optional group keys (e.g. region) for windowed calcs.

    Returns:
        Copy of ``frame`` with comparison columns appended.
    """
    if frame.empty:
        return frame.copy()

    out = frame.copy()
    out[month_col] = pd.to_datetime(out[month_col])
    sort_cols = [*(partition_cols or []), month_col]
    out = out.sort_values(sort_cols).reset_index(drop=True)

    group = out.groupby(partition_cols, dropna=False) if partition_cols else None

    for col in value_cols:
        if col not in out.columns:
            continue
        series = group[col] if group is not None else out[col]

        prev = series.shift(1) if group is None else group[col].shift(1)
        prior_year = series.shift(12) if group is None else group[col].shift(12)
        roll3 = (
            series.rolling(3, min_periods=1).mean()
            if group is None
            else group[col].transform(lambda s: s.rolling(3, min_periods=1).mean())
        )
        roll12 = (
            series.rolling(12, min_periods=1).sum()
            if group is None
            else group[col].transform(lambda s: s.rolling(12, min_periods=1).sum())
        )

        out[f"{col}_previous_month_value"] = prev
        out[f"{col}_month_over_month_change"] = out[col] - prev
        out[f"{col}_prior_year_value"] = prior_year
        out[f"{col}_year_over_year_change"] = out[col] - prior_year
        out[f"{col}_rolling_3_month_average"] = roll3
        out[f"{col}_rolling_12_month_value"] = roll12

        # Year-to-date within calendar year (and partition if present).
        year_col = f"__year_{col}"
        out[year_col] = out[month_col].dt.year
        if partition_cols:
            ytd = out.groupby([*partition_cols, year_col], dropna=False)[col].cumsum()
        else:
            ytd = out.groupby(year_col, dropna=False)[col].cumsum()
        out[f"{col}_year_to_date_value"] = ytd
        out = out.drop(columns=[year_col])

    out[month_col] = out[month_col].dt.strftime("%Y-%m-%d")
    return out
