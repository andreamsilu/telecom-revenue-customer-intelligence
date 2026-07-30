# Phase 5 — Customer Events and Monthly Lifecycle Modelling

**Status:** Complete  
**Depends on:** [Phase 4](phase-04.md)  
**Next:** [Phase 6](phase-06.md)

---

## Objective

Build the customer event stream and monthly customer snapshots with lifecycle statuses derived strictly from qualifying activity. Encode churn, reactivation, and value-segment fields used by later analytics.

## In Scope

- Customer events (SIM Registration, SIM Swap, Bundle Purchase, Airtime Recharge, Mobile Money Usage, Complaint, Churn, Reactivation)
- Qualifying activity definition and last-activity calculation
- Lifecycle status: Active, At Risk, Dormant, Churned, Reactivated
- Monthly customer snapshot (one row per customer per month)
- Newly registered / newly churned / newly reactivated flags
- Value segment assignment method (documented)
- Boundary tests for inactivity day thresholds (30/31/45/46/59/60)
- Monthly churn rate building blocks for analytics

## Out of Scope

- Full ETL star schema and all analytical marts (Phase 6)
- Recommendation engine and Streamlit pages

## Expected Outputs

| Dataset | Typical path | Format |
|---------|--------------|--------|
| customer_events | `data/raw/customer_events.parquet` | Parquet |
| customer_monthly_snapshot | `data/raw/` or early processed path | Parquet |

## Lifecycle Rules

| Status | Inactivity |
|--------|------------|
| Active | ≤ 30 days |
| At Risk | 31–45 days |
| Dormant | 46–59 days |
| Churned | ≥ 60 days |
| Reactivated | Activity after churn |

Qualifying activity: voice, SMS, data, airtime recharge, bundle purchase, mobile money transaction.

Monthly churn rate:

```text
newly_churned_in_month / active_at_month_start * 100
```

## Planned Modules / Scripts

- `src/generator/customer_events.py`
- `src/generator/lifecycle.py`
- `scripts/generate_customer_events.py`
- Tests for boundary conditions and reactivation

## Acceptance Criteria

- [x] Events and monthly snapshots generate for `development`
- [x] Lifecycle status matches inactivity days at boundaries
- [x] Reactivation only occurs after a prior churn classification
- [x] Snapshot grain is one row per customer per month
- [x] Declining recharge frequency correlates with elevated churn risk (tested relationship)
- [x] Methodology remains consistent with `docs/churn_methodology.md`
- [x] Quality checks pass

## Verification Commands

```bash
python -m scripts.generate_customer_events --profile development
pytest
ruff check .
```

## Stop Rule

Stop after Phase 5. Do not implement the full ETL mart layer without approval.
