# Telecom Revenue & Customer Intelligence Platform

**A Python-Based Executive Decision Support Platform for Telecommunications Operators in Tanzania**

> **Disclaimer:** All data in this project is **synthetic**. This platform does not represent, imitate, or use confidential data from any real telecommunications operator.

---

## Executive Summary

This portfolio project simulates a Tanzanian telecom operator and turns synthetic operational data into executive-ready intelligence. It explains why revenue changes, where churn risk concentrates, which regions underperform, which campaigns work, and which products drive growth — always with **Finding → Business Impact → Recommendation**.

## Business Problem

The synthetic operator is growing subscribers, but revenue is growing more slowly than expected. Leadership needs to diagnose ARPU pressure, product mix shifts, churn, regional gaps, recharge behaviour, mobile money adoption, and campaign effectiveness.

## Planned Platform Modules

1. Executive Overview
2. Subscriber Analytics
3. Revenue Analytics
4. Churn and Retention
5. Recharge Analytics
6. Mobile Money Analytics
7. Campaign Analytics
8. Regional Performance
9. Executive Recommendations

## Technology Stack

Python 3.11+ · Pandas · NumPy · PyArrow · Pydantic · Faker · Plotly · Streamlit · pytest · Ruff · mypy

- CSV for small reference data
- Parquet for large datasets

## Project Structure

```text
telecom-revenue-customer-intelligence/
├── app/                 # Streamlit UI (display only)
├── data/
│   ├── raw/             # Generated raw datasets (not committed)
│   ├── processed/       # Analytical outputs (not committed)
│   ├── reference/       # Small reference datasets
│   └── exports/         # Reports / extracts
├── docs/                # Business and technical documentation
├── scripts/             # CLI entry points
├── src/                 # Business logic, generation, ETL, analytics
├── tests/               # Unit and integration tests
├── app.py               # Streamlit entry point
├── pyproject.toml
└── requirements.txt
```

## Development Profiles

| Profile | Subscribers | Period |
|---------|-------------|--------|
| `development` | 10,000 | Jan 2024 – Dec 2025 |
| `demo` | 25,000 | Jan 2024 – Dec 2025 |
| `portfolio` | 100,000 | Jan 2024 – Dec 2025 |

Default reporting month: **December 2025**.

## Current Status

**Phase 6 complete:** ETL pipeline producing dimensions, facts, and analytical marts with MoM/YoY/rolling/YTD comparisons.

Not yet implemented: analytics services, recommendation engine, or analytical Streamlit pages.

## Local Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Optional editable install:

```bash
pip install -e ".[dev]"
```

## Phase 1 Health Check

```bash
python -m scripts.health_check --profile development
```

Expected outcome: configuration loads, data directories resolve, package imports succeed, exit code `0`.

## Quality Commands

```bash
ruff format .
ruff check .
pytest
mypy src
```

## Documentation

- [Phase index](docs/phases/README.md) (Phases 1–11)
- [Business requirements](docs/business_requirements.md)
- [KPI dictionary](docs/kpi_dictionary.md)
- [Data dictionary](docs/data_dictionary.md)
- [Synthetic data rules](docs/synthetic_data_rules.md)
- [Churn methodology](docs/churn_methodology.md)
- [Architecture](docs/architecture.md)
- [Validation framework](docs/validation_framework.md)
- [Implementation guide](implementation.md)
# telecom-revenue-customer-intelligence
