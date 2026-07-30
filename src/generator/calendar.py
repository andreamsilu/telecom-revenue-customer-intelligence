"""Calendar reference dataset generation."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from src.config.settings import AppSettings

_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

_DAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


def _seasonality_factor(month: int, is_month_end: bool) -> float:
    """Return a synthetic activity weight for the calendar day."""
    base = {
        1: 0.88,  # post-holiday slowdown
        2: 0.95,
        3: 1.00,
        4: 1.02,
        5: 1.00,
        6: 1.03,
        7: 1.05,
        8: 1.04,
        9: 1.06,  # back-to-school period
        10: 1.05,
        11: 1.08,
        12: 1.22,  # December peak
    }[month]
    if is_month_end:
        return round(base * 1.04, 4)
    return base


def _holiday_period_indicator(month: int, day: int) -> str:
    """Return a coarse holiday / peak period label."""
    if month == 12 and day >= 15:
        return "year_end_peak"
    if month == 1 and day <= 10:
        return "post_holiday"
    if month == 9 and day <= 15:
        return "back_to_school"
    if month in {3, 4}:  # approximate Ramadan window placeholder
        return "ramadan_window"
    return "none"


def generate_calendar(settings: AppSettings) -> pd.DataFrame:
    """Build a daily calendar covering the configured historical period.

    Args:
        settings: Validated application settings.

    Returns:
        Calendar DataFrame with seasonality and holiday markers.
    """
    rows: list[dict[str, object]] = []
    current = settings.start_date
    while current <= settings.end_date:
        month_start = current.replace(day=1)
        next_month = date(
            current.year + (1 if current.month == 12 else 0),
            1 if current.month == 12 else current.month + 1,
            1,
        )
        is_month_end = current == (next_month - timedelta(days=1))
        weekday = current.weekday()
        rows.append(
            {
                "date": current.isoformat(),
                "day": current.day,
                "month": current.month,
                "month_name": _MONTH_NAMES[current.month - 1],
                "month_start": month_start.isoformat(),
                "quarter": (current.month - 1) // 3 + 1,
                "year": current.year,
                "day_of_week": _DAY_NAMES[weekday],
                "is_weekend": weekday >= 5,
                "is_month_end": is_month_end,
                "reporting_month": month_start.isoformat(),
                "seasonality_factor": _seasonality_factor(current.month, is_month_end),
                "holiday_period_indicator": _holiday_period_indicator(
                    current.month, current.day
                ),
            }
        )
        current += timedelta(days=1)

    frame = pd.DataFrame(rows)
    expected_days = (settings.end_date - settings.start_date).days + 1
    if len(frame) != expected_days:
        raise ValueError(
            f"Calendar length {len(frame)} does not match expected "
            f"{expected_days} days."
        )
    return frame
