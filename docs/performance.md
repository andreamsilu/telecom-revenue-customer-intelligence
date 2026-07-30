# Performance and Deployment Notes

**Status:** Phase 10  

## Dashboard IO strategy

- Streamlit pages load **aggregated marts only** via `app/services/data_loader.py`.
- Transaction-level facts (`fact_usage_daily`, `fact_recharge`, etc.) are **not** read by the UI.
- Segment charts use `value_segment_monthly_mart` instead of the full customer snapshot.
- Mart loads are cached with `@st.cache_data(ttl=3600)`.

## Profiles

| Profile | Subscribers | Typical use |
|---------|-------------|-------------|
| `development` | 10,000 | Local iteration (default committed dashboard marts) |
| `demo` | 25,000 | Richer demos / screenshots |
| `portfolio` | 100,000 | Stress / scale storytelling |

## Regenerate commands

```bash
# Full synthetic rebuild (raw → events → ETL) — long-running for demo/portfolio
python -m scripts.generate_reference_data --profile demo
python -m scripts.generate_customers --profile demo
python -m scripts.generate_usage --profile demo
python -m scripts.generate_recharges --profile demo
python -m scripts.generate_mobile_money --profile demo
python -m scripts.generate_campaigns --profile demo
python -m scripts.generate_customer_events --profile demo
python -m scripts.run_pipeline --profile demo

# Export slim marts for packaging
python -m scripts.export_dashboard_marts --profile development
```

## Smoke timing (development, indicative)

Measured on a developer workstation; treat as order-of-magnitude:

| Step | Notes |
|------|--------|
| `python -m scripts.health_check --profile development` | Seconds |
| Dashboard cold start (`streamlit run app.py`) | Tens of seconds until first paint |
| First mart cache fill | Dominated by parquet read of ~0.5MB committed dashboard set |
| Subsequent page navigations | Sub-second when cache is warm |

## Streamlit Community Cloud

Committed allowlisted files under `data/processed/` keep the cloud app runnable without regenerating raw data. Prefer Python **3.12** in Advanced settings.
