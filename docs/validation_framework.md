# Validation Framework

Validation runs after generation and after ETL. Critical failures abort pipelines when `validation_strictness=strict`.

## Check Categories

### Schema Checks

- Required columns present
- Expected dtypes
- Non-null constraints on keys and mandatory attributes

### Referential Integrity

- `customer_id` in facts exists in customers / `dim_customer`
- `region` / `region_id` resolve to regions dimension
- `product_id` and `campaign_id` resolve to dimensions
- Orphan rate must be zero for critical keys

### Range Checks

- Dates within configured period (or justified exception for lags)
- Non-negative amounts, minutes, counts, and fees
- Age and tenure within configured bounds
- Lifecycle inactivity days consistent with status

### Duplicate Checks

- Unique business keys (`customer_id`, `recharge_id`, `transaction_id`, etc.)
- One snapshot row per customer per reporting month

### Missing-Value Checks

- Critical fields have no unexpected nulls
- Optional fields documented and within tolerance

### Business-Rule Checks

- Revenue equals sum of components (within floating tolerance)
- Mobile money fees match configured fee bands
- Campaign response flags consistent (converted implies responded/contacted rules)
- Lifecycle status matches inactivity thresholds
- Prepaid share and segment distributions within plausible synthetic bands

### Trend Reasonableness Checks

- December activity elevated vs adjacent months (warning if violated)
- Data revenue generally non-decreasing across the two-year horizon (warning bands)
- Voice/SMS not exploding unrealistically
- Subscriber and revenue series free of impossible spikes (configurable thresholds)

## Severity

| Severity | Behaviour |
|----------|-----------|
| Critical | Fail pipeline in strict mode; block mart publication |
| Warning | Log and continue; surface in validation report |

Examples of **critical:** missing primary keys, orphan foreign keys, negative revenue, lifecycle contradictions.

Examples of **warning:** soft seasonality deviation, segment mix drift within tolerance.

## Outputs

Validation produces:

- structured logs
- optional export under `data/exports/`
- non-zero process exit code on critical failure

## Testing Expectation

Every business calculation and critical validation rule must have automated tests. KPI values must be reproducible under the same seed and profile.
