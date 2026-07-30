# Data Dictionary

Planned datasets for Version 1. Field lists may be refined during generation and ETL phases. Large datasets use Parquet; small reference datasets may use CSV.

Currency fields are in TZS. All data is synthetic.

---

## 1. calendar

| Field | Type | Description |
|-------|------|-------------|
| date | date | Calendar date |
| day | int | Day of month |
| month | int | Month number |
| month_name | str | Month name |
| month_start | date | First day of month |
| quarter | int | Calendar quarter |
| year | int | Calendar year |
| day_of_week | str/int | Weekday |
| is_weekend | bool | Weekend flag |
| is_month_end | bool | Month-end flag |
| reporting_month | date | Associated reporting month start |
| seasonality_factor | float | Synthetic seasonality weight |
| holiday_period_indicator | bool/str | Holiday / peak period marker |

## 2. regions

| Field | Type | Description |
|-------|------|-------------|
| region_id | str | Region/district surrogate key |
| region_name | str | Tanzanian region name |
| district_name | str | Synthetic district |
| urbanization_level | str | Urban / peri-urban / rural |
| population_weight | float | Relative subscriber weight |
| data_adoption_factor | float | Relative data usage intensity |
| mobile_money_adoption_factor | float | Relative MM adoption |
| voice_usage_factor | float | Relative voice intensity |
| commercial_potential_factor | float | Relative commercial potential |

## 3. products

Categories include voice, SMS, data bundles, combo bundles, international, roaming, VAS, mobile money.

| Field | Type | Description |
|-------|------|-------------|
| product_id | str | Product key |
| product_name | str | Display name |
| product_category | str | Category |
| service_type | str | Service family |
| unit_price | float | Price in TZS |
| bundle_size | float/null | Units (MB, minutes, SMS) |
| validity_days | int/null | Bundle validity |
| target_segment | str/null | Primary target segment |
| active_from | date | Availability start |
| active_to | date/null | Availability end |

## 4. customers

| Field | Type | Description |
|-------|------|-------------|
| customer_id | str | Customer key |
| registration_date | date | Acquisition date |
| region | str | Region name |
| district | str | District name |
| gender | str | Synthetic gender |
| age | int | Age |
| age_group | str | 18–24, 25–34, 35–44, 45–54, 55+ |
| occupation | str | Occupation category |
| customer_segment | str | Youth, Mass Market, High Value, SME, Corporate, Rural, Digital First |
| account_type | str | Prepaid / Postpaid |
| sim_type | str | Physical SIM / eSIM |
| preferred_language | str | Language preference |
| acquisition_channel | str | Acquisition channel |
| initial_status | str | Status at registration |
| smartphone_indicator | bool | Smartphone flag |
| mobile_money_registered | bool | MM registration flag |
| churn_date | date/null | First churn classification date |
| reactivation_date | date/null | Latest reactivation date |

## 5. daily_usage

Revenue fields are derived from usage or purchases — never independently random.

| Field | Type | Description |
|-------|------|-------------|
| usage_date | date | Usage date |
| customer_id | str | Customer key |
| voice_minutes | float | Voice minutes |
| sms_count | int | SMS count |
| data_mb | float | Data megabytes |
| international_minutes | float | International minutes |
| roaming_minutes | float | Roaming minutes |
| vas_events | int | VAS events |
| voice_revenue | float | Derived voice revenue |
| sms_revenue | float | Derived SMS revenue |
| data_revenue | float | Derived data revenue |
| international_revenue | float | Derived international revenue |
| roaming_revenue | float | Derived roaming revenue |
| vas_revenue | float | Derived VAS revenue |
| total_usage_revenue | float | Sum of usage revenues |

## 6. recharges

| Field | Type | Description |
|-------|------|-------------|
| recharge_id | str | Recharge key |
| customer_id | str | Customer key |
| recharge_timestamp | datetime | Event time |
| recharge_type | str | airtime, data/voice/SMS/combo bundle |
| recharge_channel | str | mobile money, dealer, bank, app, USSD, scratch card, electronic |
| amount | float | Amount TZS |
| bundle_category | str/null | Bundle category |
| bundle_size | float/null | Bundle size |
| validity_days | int/null | Validity |
| promotion_id | str/null | Linked promotion |
| region | str | Region |

## 7. mobile_money_transactions

| Field | Type | Description |
|-------|------|-------------|
| transaction_id | str | Transaction key |
| customer_id | str | Customer key |
| transaction_timestamp | datetime | Event time |
| transaction_type | str | Cash In/Out, Send Money, Merchant, Bill, Bank Transfer, Airtime |
| amount | float | Amount TZS |
| fee_revenue | float | Derived fee from bands |
| channel | str | Channel |
| merchant_category | str/null | Merchant category |
| origin_region | str | Origin region |
| destination_region | str/null | Destination region |
| transaction_status | str | Successful / Failed / Reversed |

## 8. campaigns

| Field | Type | Description |
|-------|------|-------------|
| campaign_id | str | Campaign key |
| campaign_name | str | Name (e.g., Back to School, Ramadan, Christmas) |
| start_date | date | Start |
| end_date | date | End |
| campaign_cost | float | Cost TZS |
| target_segment | str | Target segment |
| target_region | str/null | Target region |
| campaign_channel | str | Channel |
| promoted_product | str | Promoted product |
| business_objective | str | Objective |

## 9. campaign_responses

| Field | Type | Description |
|-------|------|-------------|
| campaign_id | str | Campaign key |
| customer_id | str | Customer key |
| contacted | bool | Contacted flag |
| responded | bool | Response flag |
| converted | bool | Conversion flag |
| conversion_date | date/null | Conversion date |
| revenue_generated | float | Attributed revenue |
| pre_campaign_revenue | float | Pre window revenue |
| campaign_period_revenue | float | During window revenue |
| post_campaign_revenue | float | Post window revenue |
| retained_after_30_days | bool | 30-day retention flag |
| churned_after_campaign | bool | Post-campaign churn flag |

## 10. customer_events

| Field | Type | Description |
|-------|------|-------------|
| event_id | str | Event key |
| customer_id | str | Customer key |
| event_timestamp | datetime | Event time |
| event_type | str | Registration, SIM Swap, Bundle, Recharge, MM, Complaint, Churn, Reactivation |
| event_channel | str | Channel |
| region | str | Region |
| related_transaction_id | str/null | Related transaction |
| event_value | float/null | Monetary or numeric value |

## 11. customer_monthly_snapshot

| Field | Type | Description |
|-------|------|-------------|
| reporting_month | date | Month start |
| customer_id | str | Customer key |
| lifecycle_status | str | Active / At Risk / Dormant / Churned / Reactivated |
| last_activity_date | date/null | Last qualifying activity |
| inactivity_days | int | Days since last activity |
| monthly_revenue | float | Month revenue |
| rolling_3_month_revenue | float | Rolling 3-month revenue |
| monthly_voice_minutes | float | Voice minutes |
| monthly_sms_count | int | SMS count |
| monthly_data_mb | float | Data MB |
| recharge_count | int | Recharges |
| recharge_value | float | Recharge value |
| mobile_money_active | bool | MM active in month |
| mobile_money_transaction_value | float | MM value |
| newly_registered | bool | New in month |
| newly_churned | bool | Newly churned |
| newly_reactivated | bool | Newly reactivated |
| tenure_months | int | Tenure |
| value_segment | str | Low / Medium / High / Very High Value |

## Processed analytical model

**Dimensions:** `dim_customer`, `dim_product`, `dim_region`, `dim_date`, `dim_campaign`

**Facts:** `fact_usage_daily`, `fact_recharge`, `fact_mobile_money`, `fact_campaign_response`, `fact_customer_events`

**Marts:** `customer_monthly_snapshot`, `revenue_monthly_mart`, `subscriber_monthly_mart`, `churn_monthly_mart`, `recharge_monthly_mart`, `mobile_money_monthly_mart`, `campaign_performance_mart`, `regional_performance_mart`, `executive_kpi_mart`

Comparison columns on marts where applicable: previous month, MoM change, prior year, YoY change, rolling 3/12 month, YTD.
