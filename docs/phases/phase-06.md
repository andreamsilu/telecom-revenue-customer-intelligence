# Phase 6 — ETL, Dimensions, Facts, and Analytical Marts

**Status:** Complete  
**Depends on:** [Phase 5](phase-05.md)  
**Next:** [Phase 7](phase-07.md)

---

## Objective

Transform raw synthetic datasets into a processed analytical model: dimensions, facts, and monthly marts with comparison columns. Include validation gates between raw and processed layers.

## In Scope

- Dimension tables: `dim_customer`, `dim_product`, `dim_region`, `dim_date`, `dim_campaign`
- Fact tables: `fact_usage_daily`, `fact_recharge`, `fact_mobile_money`, `fact_campaign_response`, `fact_customer_events`
- Analytical marts listed below
- Comparison columns: previous month, MoM, prior year, YoY, rolling 3/12 month, YTD
- Pipeline CLI (`run_pipeline`, `validate_data`)
- Critical vs warning validation reporting
- Tests for grain, keys, and reconciliation

## Out of Scope

- Analytics service APIs and recommendation rules (Phase 7)
- Streamlit UI

## Expected Marts

- `customer_monthly_snapshot`
- `revenue_monthly_mart`
- `subscriber_monthly_mart`
- `churn_monthly_mart`
- `recharge_monthly_mart`
- `mobile_money_monthly_mart`
- `campaign_performance_mart`
- `regional_performance_mart`
- `executive_kpi_mart`

Outputs under `data/processed/` (Parquet).

## Planned Modules / Scripts

- `src/etl/dimensions.py`
- `src/etl/facts.py`
- `src/etl/marts.py`
- `src/etl/pipeline.py`
- `src/validation/` rule modules
- `scripts/run_pipeline.py`
- `scripts/validate_data.py`

## Acceptance Criteria

- [x] Pipeline runs end-to-end for `development`
- [x] Dimensions and facts have documented grains and unique keys
- [x] Marts include required comparison columns where applicable
- [x] Revenue and subscriber reconciliations pass within tolerance
- [x] Critical validation failures yield non-zero exit codes in strict mode
- [x] Quality checks pass

## Verification Commands

```bash
python -m scripts.validate_data --profile development
python -m scripts.run_pipeline --profile development
pytest
ruff check .
```

## Stop Rule

Stop after Phase 6. Do not implement analytics services or recommendations without approval.
