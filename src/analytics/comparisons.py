"""Comparison helpers for KPI services (percent vs percentage points)."""

from __future__ import annotations


def percent_change(current: float, previous: float | None) -> float | None:
    """Return percent change from previous to current.

    Args:
        current: Current period value.
        previous: Previous period value.

    Returns:
        Percent change, or None when previous is missing/zero.
    """
    if previous is None:
        return None
    if previous == 0:
        return None
    return ((current - previous) / previous) * 100.0


def percentage_point_change(
    current: float,
    previous: float | None,
) -> float | None:
    """Return percentage-point difference for rate metrics.

    Args:
        current: Current rate (already in percent units, e.g. 4.8 for 4.8%).
        previous: Previous rate in the same units.

    Returns:
        ``current - previous``, or None when previous is missing.
    """
    if previous is None:
        return None
    return current - previous


def absolute_change(current: float, previous: float | None) -> float | None:
    """Return absolute level change."""
    if previous is None:
        return None
    return current - previous


def safe_float(value: object, default: float = 0.0) -> float:
    """Coerce a mart cell to float with a default for nulls."""
    if value is None:
        return default
    try:
        if value != value:  # NaN check
            return default
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def period_snapshot(row: object, metric: str) -> dict[str, float | None]:
    """Extract MoM/YoY/rolling/YTD fields already present on a mart row.

    Args:
        row: Mapping-like mart row (Series or dict).
        metric: Base metric column name (e.g. ``total_revenue``).

    Returns:
        Dict with current, previous_month, prior_year, mom_pct, yoy_pct,
        rolling_3_month_average, and year_to_date_value.
    """
    getter = row.get if hasattr(row, "get") else lambda k, d=None: row[k]  # type: ignore[index]
    current = safe_float(getter(metric))
    previous = _nullable(getter(f"{metric}_previous_month_value"))
    prior_year = _nullable(getter(f"{metric}_prior_year_value"))
    return {
        "current": current,
        "previous_month": previous,
        "prior_year": prior_year,
        "mom_pct": percent_change(current, previous),
        "yoy_pct": percent_change(current, prior_year),
        "rolling_3_month_average": _nullable(
            getter(f"{metric}_rolling_3_month_average")
        ),
        "year_to_date_value": _nullable(getter(f"{metric}_year_to_date_value")),
    }


def _nullable(value: object) -> float | None:
    number = safe_float(value, default=float("nan"))
    return None if number != number else number
