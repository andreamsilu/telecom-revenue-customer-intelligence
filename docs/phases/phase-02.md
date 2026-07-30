# Phase 2 — Reference Data and Customer Master Generation

**Status:** Complete  
**Depends on:** [Phase 1](phase-01.md)  
**Next:** [Phase 3](phase-03.md)

---

## Objective

Generate deterministic reference datasets and the customer master file for a selected profile. Establish the synthetic geography, product catalogue, and subscriber base that all later transaction generators depend on.

## In Scope

- Calendar dimension/reference generation (24 months, seasonality flags)
- Regions and synthetic districts with urbanization and adoption factors
- Product catalogue (voice, SMS, data, combo, international, roaming, VAS, mobile money)
- Customer master generation with segments, occupations, account/SIM types
- CLI scripts for reference and customer generation
- Schema/basic validation for reference and customer outputs
- Unit and integration tests for distributions and referential readiness

## Out of Scope

- Daily usage, recharges, mobile money, campaigns
- Lifecycle snapshots and churn events
- ETL marts and Streamlit pages

## Expected Outputs

| Dataset | Typical path | Format |
|---------|--------------|--------|
| calendar | `data/reference/calendar.csv` or parquet | CSV/Parquet |
| regions | `data/reference/regions.csv` | CSV |
| products | `data/reference/products.csv` | CSV |
| customers | `data/raw/customers.parquet` | Parquet |

## Business Rules to Encode

- Prepaid customers dominate
- Urban regions: stronger data adoption
- Rural regions: higher voice dependency
- Segments: Youth, Mass Market, High Value, SME, Corporate, Rural, Digital First
- Age groups: 18–24, 25–34, 35–44, 45–54, 55+
- Registration dates spread across the historical window (with tenure realism)
- Deterministic seed → identical outputs for the same profile

## Planned Modules / Scripts

- `src/generator/calendar.py`
- `src/generator/regions.py`
- `src/generator/products.py`
- `src/generator/customers.py`
- `scripts/generate_reference_data.py`
- `scripts/generate_customers.py`
- Tests under `tests/unit/` and `tests/integration/`

## Acceptance Criteria

- [x] Reference datasets generate for `development` profile
- [x] Customer count matches profile `subscriber_count`
- [x] All region/district and product keys are valid
- [x] Segment, account type, and geography distributions are plausible and tested
- [x] Re-running with the same seed reproduces the same files
- [x] Generated large files remain gitignored
- [x] Quality checks pass

## Verification Commands

```bash
python -m scripts.generate_reference_data --profile development
python -m scripts.generate_customers --profile development
pytest
ruff check .
```

## Stop Rule

Stop after Phase 2. Do not generate usage or recharge data without approval.
