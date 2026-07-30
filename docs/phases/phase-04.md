# Phase 4 — Mobile Money, Campaigns, and Responses

**Status:** Not started  
**Depends on:** [Phase 3](phase-03.md)  
**Next:** [Phase 5](phase-05.md)

---

## Objective

Generate mobile money transactions, campaign master data, and campaign-response outcomes. Response probability must depend on targeting relevance. Fee revenue must come from configured fee bands.

## In Scope

- Mobile money transaction generation (Cash In/Out, Send Money, Merchant, Bill, Bank Transfer, Airtime)
- Fee revenue from configurable fee bands
- Campaign catalogue (e.g., Back to School, Ramadan, Christmas, Data Weekend, Student Offer, SME Promotion)
- Campaign responses with contact, response, conversion, revenue windows, 30-day retention, post-campaign churn flags
- SME / high mobile-money usage relationships
- Month-end mobile money uplift
- Validation and tests for fees, statuses, and targeting effects

## Out of Scope

- Customer event log and monthly lifecycle modelling
- ETL marts and Streamlit pages

## Expected Outputs

| Dataset | Typical path | Format |
|---------|--------------|--------|
| mobile_money_transactions | `data/raw/mobile_money_transactions.parquet` | Parquet |
| campaigns | `data/raw/campaigns.parquet` (or reference) | Parquet/CSV |
| campaign_responses | `data/raw/campaign_responses.parquet` | Parquet |

## Business Rules to Encode

- SMEs use more mobile money
- Regional MM adoption factors influence activity
- Relevant campaign targeting → higher response/conversion
- Irrelevant targeting → weaker response
- Campaign results are attributable/observed — not causal uplift claims
- Transaction statuses: Successful, Failed, Reversed

## Planned Modules / Scripts

- `src/generator/mobile_money.py`
- `src/generator/campaigns.py`
- `src/generator/campaign_responses.py`
- `src/generator/fee_bands.py`
- `scripts/generate_mobile_money.py`
- `scripts/generate_campaigns.py`

## Acceptance Criteria

- [ ] MM, campaigns, and responses generate for `development`
- [ ] Fees match configured bands for successful transactions
- [ ] Response rates differ materially for relevant vs irrelevant targeting (tested)
- [ ] Referential integrity to customers, regions, products/campaigns
- [ ] Deterministic reproducibility
- [ ] Quality checks pass

## Verification Commands

```bash
python -m scripts.generate_mobile_money --profile development
python -m scripts.generate_campaigns --profile development
pytest
ruff check .
```

## Stop Rule

Stop after Phase 4. Do not build lifecycle snapshots without approval.
