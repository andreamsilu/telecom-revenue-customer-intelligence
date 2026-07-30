# Phase 9 — Remaining Analytical Dashboard Pages

**Status:** Complete  
**Depends on:** [Phase 8](phase-08.md)  
**Next:** [Phase 10](phase-10.md)

---

## Objective

Build the remaining analytical Streamlit pages one page at a time, each satisfying the page contract and calling shared analytics/recommendation services.

## Pages to Build (in order)

1. Subscriber Analytics  
2. Revenue Analytics  
3. Churn and Retention  
4. Recharge Analytics  
5. Mobile Money Analytics  
6. Campaign Analytics  
7. Regional Performance  
8. Executive Recommendations  

Each page requires explicit approval before starting the next when requested by the project owner; otherwise complete Phase 9 as a sequenced delivery with a stop after the phase.

## In Scope

- One Streamlit page per module above
- Domain KPIs, trends, comparisons, and interpreted insights
- Campaign page must avoid unjustified causal uplift language
- Executive Recommendations page lists engine output with priority and department
- Reuse of shared components and filters

## Out of Scope

- Heavy performance optimization (Phase 10)
- Final portfolio README polish and screenshot pack (Phase 11)

## Acceptance Criteria (per page)

- [x] KPI summary present
- [x] Trend analysis present
- [x] Segment or regional comparison present
- [x] Finding, business impact, and recommended action present
- [x] No KPI calculations inside the page file
- [x] Tests for any new service helpers
- [x] Ruff/pytest still pass after each page (or after the phase batch)

## Verification Commands

```bash
streamlit run app.py
pytest
ruff check .
```

## Stop Rule

Stop after Phase 9 (or after each page if the owner requires per-page approval). Do not begin performance/deployment prep without approval.
