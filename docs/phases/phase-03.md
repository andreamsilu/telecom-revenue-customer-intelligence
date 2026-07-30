# Phase 3 — Usage and Recharge Generation

**Status:** Complete  
**Depends on:** [Phase 2](phase-02.md)  
**Next:** [Phase 4](phase-04.md)

---

## Objective

Generate daily usage and recharge transaction datasets that reflect realistic telecom behaviour, with revenue derived from usage and purchases — never from independent random revenue columns.

## In Scope

- Daily usage generation (voice, SMS, data, international, roaming, VAS)
- Derived usage revenue components and totals
- Recharge events (airtime and bundles) across channels
- Seasonality (December peak, January slowdown, weekend/weekday patterns)
- Segment and geography behavioural differentials
- Memory-conscious batching
- Validation of ranges, non-negative amounts, and customer referential integrity
- Tests for revenue derivation and key behavioural relationships

## Out of Scope

- Mobile money and campaigns
- Customer events / monthly lifecycle snapshots
- ETL and dashboards

## Expected Outputs

| Dataset | Typical path | Format |
|---------|--------------|--------|
| daily_usage | `data/raw/daily_usage.parquet` | Parquet |
| recharges | `data/raw/recharges.parquet` | Parquet |

## Business Rules to Encode

- Urban → more mobile data; rural → more voice
- Students / youth → smaller data bundles
- Data revenue grows over the two-year horizon; voice grows slowly or declines
- Recharge frequency and amount vary by segment and value
- Revenue = f(usage or purchase, product rates) within tolerance
- Weekends boost consumer data; weekdays boost SME/corporate usage

## Planned Modules / Scripts

- `src/generator/usage.py`
- `src/generator/recharges.py`
- `src/generator/pricing.py` (or shared rate tables)
- `scripts/generate_usage.py`
- `scripts/generate_recharges.py`

## Acceptance Criteria

- [x] Usage and recharge files generate for `development`
- [x] Every `customer_id` exists in customers
- [x] No negative usage or revenue
- [x] Component revenues sum to `total_usage_revenue` within tolerance
- [x] Seasonality and urban/rural differentials are observable and tested
- [x] Deterministic seed reproducibility
- [x] Quality checks pass

## Verification Commands

```bash
python -m scripts.generate_usage --profile development
python -m scripts.generate_recharges --profile development
pytest
ruff check .
```

## Stop Rule

Stop after Phase 3. Do not start mobile money or campaign generation without approval.
