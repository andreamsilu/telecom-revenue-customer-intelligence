# Synthetic Data Rules

All data is synthetic. Distributions and relationships are designed to behave like one connected telecom business serving Tanzania. They do **not** represent any real operator.

## Design Principles

- Deterministic random seeds for reproducibility
- Configuration-driven scale (development / demo / portfolio)
- Revenue derived from usage or purchases — never independent random revenue
- Relationships between geography, segment, product, and behaviour
- No unrelated random columns

## Time and Seasonality

| Pattern | Behaviour |
|---------|-----------|
| December | Higher communication, recharge, and mobile money activity |
| January | Post-holiday slowdown |
| Weekends | Higher consumer data usage |
| Weekdays | Higher SME / corporate usage |
| Month-end | Higher mobile money activity |
| 2024–2025 trend | Data usage and revenue grow; voice/SMS grow slowly or decline |

## Geography

Representative regions (Version 1): Dar es Salaam, Arusha, Mwanza, Dodoma, Mbeya, Morogoro, Tanga, Kilimanjaro, Kagera, Mtwara, Geita, Tabora.

Urbanization influences:

- subscriber volume
- data vs voice mix
- mobile money adoption
- recharge behaviour
- segment mix
- campaign response
- revenue performance

Urban regions skew toward data; rural regions skew toward voice.

## Segment Behaviour

| Segment / trait | Expected behaviour |
|-----------------|--------------------|
| Prepaid majority | Dominates the base |
| Youth / students | Smaller affordable data bundles |
| SME | More voice and mobile money |
| Corporate | Lower churn, higher revenue |
| High value | Disproportionate revenue contribution |
| Digital First | Higher app/USSD digital channels |
| Rural | Higher voice dependency |

## Lifecycle and Churn Drivers

- Declining recharge frequency increases churn risk
- Long inactivity progresses Active → At Risk → Dormant → Churned
- Qualifying activity after churn produces Reactivated status
- High-value churn produces outsized revenue loss
- Low-engagement / low-value segments may show elevated churn

## Campaign Behaviour

- Relevant targeting → stronger response and conversion
- Irrelevant targeting → weaker response
- Observed campaign revenue is attributable, not causal uplift
- Post-campaign retention and churn-after-campaign are tracked

## Revenue Derivation

- Usage revenue from minutes, SMS, MB, and configured rates/products
- Bundle revenue from recharge/purchase events
- Mobile money fee revenue from configured fee bands
- Totals reconcile to component sums in validation

## Limitations

- Synthetic correlations are illustrative, not market estimates
- Regional weights are modelling devices, not real market shares
- No claim of national representativeness
- Version 1 excludes ML-based propensity or uplift models
