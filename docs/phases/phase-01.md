# Phase 1 — Scaffolding, Configuration, and Documentation

**Status:** Complete  
**Depends on:** None  
**Next:** [Phase 2](phase-02.md)

---

## Objective

Create the business specification, architecture, configuration system, project scaffolding, quality tooling, and initial documentation. Do not generate subscriber or transaction datasets.

## In Scope

- Folder structure aligned to the architecture
- `pyproject.toml`, `requirements.txt`, `.gitignore`, `.env.example`
- Pydantic settings and three scale profiles
- Path utilities (repo-root based) and logging
- CLI health check
- Core documentation under `docs/`
- Initial README
- Unit tests for config, paths, and health check
- Ruff, pytest, and mypy wiring

## Out of Scope

- Synthetic customer or transaction generation
- ETL, analytics services, recommendation engine
- Streamlit analytical pages
- Final KPI calculations

## Deliverables

| Item | Location |
|------|----------|
| Project layout | `app/`, `src/`, `data/`, `tests/`, `scripts/`, `docs/` |
| Tooling | `pyproject.toml`, `.gitignore`, `.env.example`, `.streamlit/config.toml` |
| Config | `src/config/settings.py`, `src/config/profiles.py` |
| Utils | `src/utils/paths.py`, `src/utils/logging.py` |
| Health check | `scripts/health_check.py` |
| Docs | `docs/*.md`, `README.md` |
| Tests | `tests/unit/test_config.py`, `test_paths.py`, `test_health_check.py` |

## Profiles

| Profile | Subscribers | Period |
|---------|-------------|--------|
| development | 10,000 | 2024-01-01 → 2025-12-31 |
| demo | 25,000 | same |
| portfolio | 100,000 | same |

Default reporting month: December 2025.

## Acceptance Criteria

- [x] Configuration loads for all three profiles
- [x] Invalid subscriber count, date ranges, and reporting month fail validation
- [x] Period must contain exactly 24 complete months
- [x] Paths resolve relative to repository root
- [x] `python -m scripts.health_check --profile development` exits 0
- [x] `ruff check .`, `pytest`, and `mypy src` pass

## Verification Commands

```bash
python -m scripts.health_check --profile development
ruff format .
ruff check .
pytest
mypy src
```

## Stop Rule

Stop after Phase 1. Do not start Phase 2 without explicit approval.
