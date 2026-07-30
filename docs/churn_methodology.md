# Churn and Lifecycle Methodology

Lifecycle status is **derived from generated activity**, not assigned randomly.

## Qualifying Activity

Any of the following resets inactivity:

- voice usage
- SMS usage
- data usage
- airtime recharge
- bundle purchase
- mobile money transaction

## Lifecycle Definitions

| Status | Rule |
|--------|------|
| Active | Qualifying activity within the last 30 days |
| At Risk | 31–45 days inactive |
| Dormant | 46–59 days inactive |
| Churned | 60+ days inactive |
| Reactivated | Qualifying activity after a Churned classification |

Boundary tests must cover day 30, 31, 45, 46, 59, and 60.

## Monthly Snapshot

One row per customer per reporting month, including:

- lifecycle status
- last activity date and inactivity days
- monthly and rolling 3-month revenue
- usage, recharge, and mobile money measures
- newly registered / newly churned / newly reactivated flags
- tenure and value segment

## Monthly Churn Rate

```
churn_rate = newly_churned_in_month / active_customers_at_month_start * 100
```

- **Numerator:** Customers who newly became Churned during the month.
- **Denominator:** Active customers at the beginning of the month.
- Compare rates using **percentage points**, not relative percent, on KPI cards.

## Reactivation

A customer classified as Churned who later records qualifying activity becomes Reactivated. Reactivation rate denominators will be documented precisely when the analytics service is implemented (eligible churned pool in the lookback window).

## Synthetic Engagement Attrition

Because dense usage generation alone rarely reaches 60-day inactivity, the
lifecycle builder applies a **deterministic attrition mask** to a minority of
customers (about 14%), oversampling those with below-median recharge counts.
After their cutoff date, usage/recharge/mobile-money rows are ignored for
lifecycle and snapshot metrics so churn and reactivation can occur while
remaining reproducible under the configured seed.

## Value Segmentation

Value segments are assigned **within each reporting month** using the customer's
`rolling_3_month_revenue` and the month's distribution of positive rolling
revenues:

| Segment | Rule |
|---------|------|
| Low Value | revenue ≤ p50 (or ≤ 0) |
| Medium Value | p50 < revenue ≤ p75 |
| High Value | p75 < revenue ≤ p90 |
| Very High Value | revenue > p90 |

This is a portfolio segmentation device for synthetic analysis, not a real
operator ARPU tier definition.

High-value churn and revenue lost to churn are priority executive metrics.

## Limitations

- Inactivity-based churn is a behavioural proxy, not a contractual cancellation
- Multi-SIM reality is not modelled in Version 1
- Temporary travel/outage inactivity may look like churn risk
- Reactivation does not guarantee sustained retention
