# Phase 8 — Streamlit Design System and Executive Overview

**Status:** Not started  
**Depends on:** [Phase 7](phase-07.md)  
**Next:** [Phase 9](phase-09.md)

---

## Objective

Establish the Streamlit presentation layer: design system, global filters, shared components, cached data loading, and the Executive Overview page. Pages display results only — they call analytics services.

## In Scope

- Shared layout, theme alignment (`.streamlit/config.toml`), typography/spacing helpers
- Global filters: reporting month, date range, region, segment, account type, product category
- Filter reset, data freshness indicator, no-data handling
- Reusable KPI cards, chart wrappers, finding/impact/action panels
- Consistent TZS formatting and comparison labels
- Executive Overview page with KPI summary, trends, regional/segment comparison, finding, impact, action
- `app/services/` data-loading wrappers (no KPI math)

## Out of Scope

- Remaining analytical pages (Phase 9)
- Portfolio packaging and screenshots (Phase 11)

## Page Contract (every page)

1. KPI summary  
2. Trend analysis  
3. Segment or regional comparison  
4. Key finding  
5. Business impact  
6. Recommended action  

Do not ship chart-only pages.

## Planned Modules

- `app/components/` (kpi_card, filters, insight_panel, charts)
- `app/services/data_loader.py`
- `app/pages/` Executive Overview entry
- Updates to `app.py` navigation/shell

## Acceptance Criteria

- [ ] `streamlit run app.py` loads Executive Overview against processed marts
- [ ] Filters propagate to service calls
- [ ] KPI values come from `src/analytics`, not page code
- [ ] Finding → Impact → Action visible on the page
- [ ] Empty/missing data states are handled cleanly
- [ ] Quality checks pass

## Verification Commands

```bash
streamlit run app.py
pytest
ruff check .
```

## Stop Rule

Stop after Phase 8. Build remaining pages only with approval (Phase 9), preferably one page at a time.
