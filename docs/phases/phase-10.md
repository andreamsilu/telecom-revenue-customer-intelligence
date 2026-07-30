# Phase 10 — Performance Optimization and Deployment Datasets

**Status:** Not started  
**Depends on:** [Phase 9](phase-09.md)  
**Next:** [Phase 11](phase-11.md)

---

## Objective

Make local demo and portfolio profiles practical: optimize IO and caching, prefer marts over transaction scans in the UI, and prepare deployment-sized datasets for demonstration and screenshots.

## In Scope

- Profile-oriented generation/pipeline runs (`demo`, `portfolio` as needed)
- Streamlit caching strategy for marts
- Avoid loading transaction-level data when aggregated marts suffice
- Parquet partition/column pruning where beneficial
- Batch size and memory tuning for portfolio-scale generation
- Smoke timing notes for health check, pipeline, and dashboard cold start
- Optional export of slim demo extracts under `data/exports/`

## Out of Scope

- New analytical features unrelated to performance
- Final documentation packaging (Phase 11)

## Acceptance Criteria

- [ ] Executive Overview and key pages load from marts without full transaction scans
- [ ] `demo` profile pipeline completes successfully on a developer machine
- [ ] Documented commands to regenerate demo/portfolio artifacts
- [ ] No regression in KPI reproducibility
- [ ] Quality checks pass

## Verification Commands

```bash
python -m scripts.run_pipeline --profile demo
streamlit run app.py
pytest
ruff check .
```

## Stop Rule

Stop after Phase 10. Do not finalize portfolio packaging without approval.
