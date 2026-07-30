# Phase 7 — Analytics Services and Recommendation Engine

**Status:** Not started  
**Depends on:** [Phase 6](phase-06.md)  
**Next:** [Phase 8](phase-08.md)

---

## Objective

Implement reusable analytics services that compute KPIs and comparisons in `src/`, plus a deterministic recommendation engine that emits Finding → Business Impact → Recommended Action with supporting metrics.

## In Scope

- Analytics modules for executive, revenue, subscriber, retention, recharge, mobile money, campaign, and regional KPIs
- MoM, YoY, rolling 3-month, YTD, and current vs previous helpers
- Percentage vs percentage-point comparison conventions
- Recommendation records with required fields (id, period, module, finding, metric, value, benchmark, impact, action, priority, department, filters)
- Rule examples from the implementation guide (ARPU down / subs up, high-value churn, negative campaign ROI, etc.)
- Unit tests for every business calculation
- No Streamlit KPI logic

## Out of Scope

- Streamlit design system and pages (Phases 8–9)
- Performance tuning for portfolio-scale files (Phase 10)

## Required Recommendation Fields

- `recommendation_id`
- `reporting_period`
- `module`
- `finding`
- `metric_name` / `metric_value` / `benchmark`
- `business_impact`
- `recommended_action`
- `priority` (Critical / High / Medium / Low)
- `responsible_department`
- `supporting_filters`

Recommendations must never be random or unsupported by metrics.

## Planned Modules

- `src/analytics/` service modules per domain
- `src/analytics/comparisons.py`
- `src/recommendations/engine.py`
- `src/recommendations/rules.py`
- Tests under `tests/unit/` for KPIs and rules

## Acceptance Criteria

- [ ] KPI functions are pure/reusable and covered by tests
- [ ] Same mart inputs → identical KPI outputs
- [ ] Rate comparisons use percentage points
- [ ] Every emitted recommendation includes required fields and a supporting KPI
- [ ] No business calculations live in `app/` pages
- [ ] Quality checks pass

## Verification Commands

```bash
pytest --cov=src
ruff check .
mypy src
```

## Stop Rule

Stop after Phase 7. Do not build Streamlit pages without approval.
