# Business Requirements

## Business Background

This portfolio project simulates a telecommunications operator serving the Tanzanian market. All data is synthetic. The platform does not represent any real operator, brand, subscriber base, market share, or pricing.

The synthetic operator is growing its subscriber base, but total revenue is growing more slowly than management expects. Leadership needs an executive decision-support platform that explains revenue movement, retention risk, regional performance, campaign effectiveness, and digital service adoption.

## Business Problem

Management needs to determine whether slower-than-expected revenue growth is driven by:

- declining ARPU
- changing product mix
- falling voice and SMS revenue
- insufficient data revenue growth
- customer churn
- regional underperformance
- reduced recharge frequency
- low mobile money adoption
- ineffective campaigns
- poor post-campaign retention
- loss of high-value customers

## Intended Users

| Role | Primary decisions supported |
|------|-----------------------------|
| Chief Executive Officer | Portfolio growth, retention, and profitability |
| Commercial Director | Product mix, ARPU, and segment performance |
| Finance Director | Revenue trends, contribution, and risk |
| Marketing Manager | Campaign ROI, conversion, and retention |
| Customer Experience Manager | Churn, dormancy, and reactivation |
| Mobile Money Manager | Adoption, usage, and fee revenue |
| Regional Sales Manager | Regional gaps and commercial actions |

## Business Questions

The platform must help answer:

1. Why is revenue changing?
2. Why are subscribers churning?
3. Which regions underperform?
4. Which campaigns succeed?
5. Which products drive growth?

Every metric display must include interpretation:

**Finding → Business Impact → Recommendation**

## Project Scope (Version 1)

In scope:

- Synthetic data generation for 24 months (2024-01-01 to 2025-12-31)
- Configurable profiles (development, demo, portfolio)
- Data quality validation
- ETL into dimensions, facts, and analytical marts
- Telecom KPI analytics in `src/`
- Deterministic executive recommendation engine
- Streamlit dashboards with Plotly charts
- Automated tests and professional documentation

Out of scope (Version 1):

- Machine learning models
- Real operator data or branding
- Excel, AWS, Power BI
- External APIs
- Complex authentication
- Notebooks as the production pipeline
- Causal campaign uplift claims without experimental design

## Expected Decisions Supported

- Prioritise retention actions for at-risk and high-value segments
- Rebalance product and regional commercial focus
- Improve recharge and mobile money engagement where adoption lags
- Stop, scale, or redesign campaigns based on ROI and retention
- Explain month-over-month and year-over-year revenue movement to executives

## Currency and Market Framing

- Currency: Tanzanian Shillings (TZS)
- Geography: representative Tanzanian regions for synthetic modelling only
- Historical period: January 2024 through December 2025
- Default reporting month: December 2025
