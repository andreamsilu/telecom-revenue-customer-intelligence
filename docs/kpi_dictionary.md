# KPI Dictionary

All KPIs are calculated in `src/analytics/` (not in Streamlit pages). Values use TZS where monetary. Rate comparisons use percentage-point differences.

Grain defaults to **reporting month** unless noted. Comparison methods include MoM, YoY, rolling 3-month average, YTD, and current vs previous period.

---

## Executive KPIs

### Total Subscribers

- **Definition:** Count of customers registered on or before the end of the reporting month and not permanently excluded.
- **Formula:** `COUNT(DISTINCT customer_id)` in the subscriber snapshot for the month.
- **Grain:** Monthly.
- **Comparison:** MoM %, YoY %.
- **Interpretation:** Rising base with flat revenue often signals ARPU pressure.
- **Limitations:** Does not alone indicate commercial health.

### Active Subscribers

- **Definition:** Customers with qualifying activity within the last 30 days of the reporting month-end.
- **Formula:** Count where `lifecycle_status = Active`.
- **Grain:** Monthly.
- **Comparison:** MoM %, YoY %.
- **Interpretation:** Active base drives near-term revenue.
- **Limitations:** Sensitive to definition of qualifying activity.

### New Subscribers

- **Definition:** Customers whose `registration_date` falls in the reporting month.
- **Formula:** Count of new registrations in month.
- **Grain:** Monthly.
- **Comparison:** MoM %, YoY %.
- **Interpretation:** Acquisition volume; evaluate with early churn.
- **Limitations:** Does not measure quality of acquisition.

### Subscriber Growth

- **Definition:** Net change in total subscribers versus prior period.
- **Formula:** `(subscribers_t - subscribers_t-1) / subscribers_t-1 * 100`.
- **Grain:** Monthly.
- **Comparison:** MoM pp/%, YoY.
- **Interpretation:** Growth without revenue growth indicates dilution.
- **Limitations:** Masks mix shifts between segments.

### Churn Rate

- **Definition:** Share of beginning-of-month active customers who newly churned in the month.
- **Formula:** `newly_churned / active_at_month_start * 100`.
- **Grain:** Monthly.
- **Comparison:** MoM percentage points, YoY percentage points.
- **Interpretation:** Rising churn destroys lifetime value, especially in high-value segments.
- **Limitations:** Depends on 60-day inactivity rule; not a contractual cancel event.

### Reactivation Rate

- **Definition:** Share of previously churned customers who record qualifying activity again.
- **Formula:** `newly_reactivated / churned_pool_eligible * 100` (exact denominator documented in churn methodology).
- **Grain:** Monthly.
- **Comparison:** MoM percentage points.
- **Interpretation:** Successful win-back reduces net base loss.
- **Limitations:** Reactivated customers may re-churn quickly.

### Total Revenue

- **Definition:** Sum of usage, bundle/recharge-attributed, VAS, international, roaming, and mobile money fee revenue for the period.
- **Formula:** Sum of component revenues in the revenue mart.
- **Grain:** Monthly.
- **Comparison:** MoM %, YoY %, rolling 3-month average.
- **Interpretation:** Primary commercial outcome metric.
- **Limitations:** Fee and usage allocation rules affect composition.

### Revenue Growth

- **Definition:** Period-over-period change in total revenue.
- **Formula:** `(revenue_t - revenue_t-1) / revenue_t-1 * 100`.
- **Grain:** Monthly.
- **Comparison:** MoM %, YoY %.
- **Interpretation:** Must be read with subscriber growth and ARPU.
- **Limitations:** Seasonality (e.g., December) can distort MoM reads.

### ARPU

- **Definition:** Average revenue per active user for the month.
- **Formula:** `total_revenue / active_subscribers`.
- **Grain:** Monthly.
- **Comparison:** MoM %, YoY %.
- **Interpretation:** Core profitability-per-user signal.
- **Limitations:** Sensitive to active definition and revenue scope.

### Average Recharge Value

- **Definition:** Mean monetary value per successful recharge event.
- **Formula:** `SUM(amount) / COUNT(recharges)`.
- **Grain:** Monthly.
- **Comparison:** MoM %, YoY %.
- **Interpretation:** Falling average may indicate downtrading to smaller bundles.
- **Limitations:** Mix of airtime vs bundles affects the average.

### Recharge Frequency

- **Definition:** Average successful recharges per active customer in the month.
- **Formula:** `recharge_count / active_subscribers`.
- **Grain:** Monthly.
- **Comparison:** MoM %, YoY %.
- **Interpretation:** Declining frequency is an early churn risk signal.
- **Limitations:** Prepaid-heavy bases show natural variability.

### Mobile Money Active Users

- **Definition:** Customers with at least one successful mobile money transaction in the month.
- **Formula:** Distinct `customer_id` with successful MM activity.
- **Grain:** Monthly.
- **Comparison:** MoM %, YoY %.
- **Interpretation:** Digital engagement and fee-revenue potential.
- **Limitations:** Registration alone does not imply activity.

### Mobile Money Transaction Volume / Value / Fee Revenue

- **Definition:** Count, sum of amounts, and derived fee revenue for successful transactions.
- **Formula:** Aggregations from mobile money fact; fees from configured bands.
- **Grain:** Monthly.
- **Comparison:** MoM %, YoY %.
- **Interpretation:** Adoption quality and monetisation of the wallet.
- **Limitations:** Failed/reversed transactions excluded from success metrics but tracked separately.

### Campaign ROI

- **Definition:** Observed return on campaign cost using attributed campaign revenue.
- **Formula:** `(revenue_generated - campaign_cost) / campaign_cost * 100`.
- **Grain:** Campaign / monthly roll-up.
- **Comparison:** Versus peer campaigns and historical average.
- **Interpretation:** Negative ROI warrants redesign or stop decisions.
- **Limitations:** Not true causal uplift without experimental design; treat as attributable/observed performance.

---

## Domain KPI Groups

Additional KPIs (documented fully as analytics modules are implemented):

- **Revenue:** voice, SMS, data, VAS, roaming, international, by segment/region, RPAU, product contribution.
- **Subscribers:** prepaid/postpaid share, active rate, tenure, segment/region mix, smartphone and digital-first share.
- **Retention:** churn by segment/region/tenure/value, revenue lost to churn, at-risk/dormant counts.
- **Recharge:** channel share, bundle share, declining recharge behaviour.
- **Mobile money:** adoption rate, type share, regional adoption, failed rate, merchant payment growth.
- **Campaign:** response rate, conversion, CPA, post-campaign retention, churn after campaign.

## Comparison Conventions

| Metric type | Preferred delta |
|-------------|-----------------|
| Levels (revenue, counts) | Percentage change |
| Rates (churn, conversion, adoption) | Percentage-point change |
| Currency | TZS with clear units (e.g., TZS millions/billions on executive cards) |
