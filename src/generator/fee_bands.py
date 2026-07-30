"""Configurable mobile money fee bands (TZS)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeeBand:
    """Inclusive lower bound, exclusive upper bound fee schedule row."""

    min_amount: float
    max_amount: float | None
    fee: float


# Synthetic fee schedule — not a real operator tariff.
DEFAULT_FEE_BANDS: tuple[FeeBand, ...] = (
    FeeBand(0.0, 1_000.0, 50.0),
    FeeBand(1_000.0, 5_000.0, 100.0),
    FeeBand(5_000.0, 20_000.0, 250.0),
    FeeBand(20_000.0, 50_000.0, 500.0),
    FeeBand(50_000.0, 200_000.0, 1_000.0),
    FeeBand(200_000.0, None, 2_000.0),
)

# Airtime purchase via MM often uses a lower fixed fee.
AIRTIME_PURCHASE_FEE = 30.0


def fee_for_amount(
    amount: float,
    *,
    transaction_type: str,
    bands: tuple[FeeBand, ...] = DEFAULT_FEE_BANDS,
) -> float:
    """Return fee revenue for a successful mobile money transaction.

    Args:
        amount: Transaction amount in TZS.
        transaction_type: MM transaction type label.
        bands: Ordered fee bands.

    Returns:
        Fee in TZS derived from the configured schedule.
    """
    if amount < 0:
        raise ValueError(f"amount must be non-negative; got {amount}.")

    if transaction_type == "Airtime Purchase":
        return AIRTIME_PURCHASE_FEE

    for band in bands:
        upper_ok = band.max_amount is None or amount < band.max_amount
        if amount >= band.min_amount and upper_ok:
            return band.fee

    raise ValueError(f"No fee band matched amount={amount}.")
