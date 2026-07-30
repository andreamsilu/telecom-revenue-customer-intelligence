You are acting as a senior Python data engineer, analytics engineer, BI developer, software architect, and telecom commercial analytics consultant.

You are responsible for helping me build a professional portfolio project named:

TELECOM REVENUE & CUSTOMER INTELLIGENCE PLATFORM

Subtitle:

A Python-Based Executive Decision Support Platform for Telecommunications Operators in Tanzania

The project must be built carefully, professionally, and phase by phase.

Do not build the entire project in one attempt.

Before every phase:

1. Inspect the existing repository.
2. Explain the implementation plan.
3. List all files that will be created or modified.
4. Identify assumptions and risks.
5. Implement only the requested phase.
6. Run tests and quality checks.
7. Explain how I can run and verify the completed work.
8. Summarize what was completed.
9. Stop and wait for my approval before starting the next phase.

Do not automatically proceed to another phase.

==================================================
1. PROJECT PURPOSE
==================================================

This is an end-to-end telecom analytics portfolio project.

It must simulate a telecommunications operator serving the Tanzanian market and transform synthetic operational data into executive-level business intelligence.

The platform should help management answer one central question:

How can a telecommunications operator grow revenue while improving customer retention, campaign effectiveness, and digital service adoption?

The project should demonstrate:

- Python analytics
- Pandas and NumPy
- synthetic data engineering
- data modelling
- ETL pipeline development
- data quality validation
- telecom revenue analytics
- customer lifecycle analytics
- churn and retention analytics
- recharge analytics
- mobile money analytics
- campaign performance analytics
- regional performance analytics
- KPI design
- executive reporting
- interactive data visualization
- Streamlit dashboard development
- Plotly visualizations
- deterministic executive recommendations
- automated testing
- professional GitHub documentation

All data must be synthetic.

The project must not claim to represent any real telecommunications operator.

Do not use the name, branding, subscriber numbers, market share, pricing, or confidential data of any real operator.

==================================================
2. CORE BUSINESS STORY
==================================================

The synthetic operator is experiencing subscriber growth, but total revenue is growing more slowly than expected.

Management wants to understand whether this is caused by:

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

The platform must investigate these issues and produce clear executive findings and recommendations.

Primary users:

- Chief Executive Officer
- Commercial Director
- Finance Director
- Marketing Manager
- Customer Experience Manager
- Mobile Money Manager
- Regional Sales Manager

==================================================
3. HISTORICAL TIMEFRAME
==================================================

Generate and analyse 24 complete months of data:

Start date:
2024-01-01

End date:
2025-12-31

Default reporting month:
December 2025

The dashboard must support:

- month-over-month comparison
- year-over-year comparison
- current period versus previous comparable period
- rolling 3-month average
- rolling 12-month values where useful
- year-to-date comparison
- custom reporting periods

KPI cards should show both the current value and an appropriate comparison.

Examples:

Total Revenue
TZS 48.2B
+6.4% month over month
+11.8% year over year

Churn Rate
4.8%
-0.6 percentage points month over month

Use percentage-point differences when comparing rates such as churn, conversion rate, response rate, and mobile money adoption.

==================================================
4. PROJECT SCALE
==================================================

Create three configurable profiles.

Development profile:

- 10,000 subscribers
- full 24-month timeframe
- smaller transaction volumes
- intended for frequent development and testing

Demo profile:

- approximately 25,000 subscribers
- optimized for local demonstration and Streamlit deployment

Portfolio profile:

- 100,000 subscribers
- full 24-month timeframe
- realistic large transaction volumes
- used for final screenshots and portfolio evidence

The system must allow these numbers to be changed through configuration.

Use deterministic random seeds so that repeated runs with the same configuration produce the same output.

Generation should be memory-conscious and support batching where necessary.

==================================================
5. TECHNOLOGY STACK
==================================================

Use:

- Python 3.11 or later
- Pandas
- NumPy
- PyArrow
- Plotly
- Streamlit
- Pydantic
- Pydantic Settings
- Faker where useful
- pytest
- pytest-cov
- Ruff
- mypy where practical
- python-dotenv
- pathlib
- standard Python logging

Use CSV for small reference datasets when convenient.

Use Parquet for:

- large raw datasets
- transaction-level datasets
- processed analytical datasets
- data marts

PostgreSQL may be added later as an optional enhancement, but the first complete version must work locally using files.

Do not use:

- Excel
- AWS
- Power BI
- machine learning in version one
- unnecessary external APIs
- complex authentication
- real operator data
- notebooks as the main production pipeline

Notebooks may only be used for optional exploration.

All repeatable processing must be implemented in Python modules and scripts.

==================================================
6. CODE QUALITY RULES
==================================================

Use:

- type hints
- docstrings for public functions and classes
- clear variable and function names
- pathlib for filesystem paths
- standard logging rather than print statements in production modules
- modular reusable functions
- configuration-driven behaviour
- explicit validation
- helpful error messages
- deterministic random seeds
- unit tests
- integration tests
- reproducible commands

Avoid:

- giant scripts
- files larger than approximately 400 lines without a strong reason
- duplicated calculations
- raw transformation logic inside Streamlit page files
- silent exception handling
- hard-coded absolute paths
- unexplained magic numbers
- independent random fields with no business relationship
- unsupported business recommendations
- calculations duplicated across pages
- loading transaction-level datasets when aggregated marts are sufficient

The Streamlit layer should display results.

The `src` layer should calculate results.

==================================================
7. INITIAL PROJECT STRUCTURE
==================================================

Create or maintain this structure:

telecom-revenue-customer-intelligence/
├── .cursor/
│   └── rules/
│       └── project-rules.mdc
├── .streamlit/
│   └── config.toml
├── app/
│   ├── __init__.py
│   ├── pages/
│   ├── components/
│   ├── services/
│   └── assets/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── reference/
│   └── exports/
├── docs/
│   ├── business_requirements.md
│   ├── kpi_dictionary.md
│   ├── data_dictionary.md
│   ├── synthetic_data_rules.md
│   ├── churn_methodology.md
│   ├── architecture.md
│   └── validation_framework.md
├── notebooks/
├── scripts/
├── src/
│   ├── __init__.py
│   ├── analytics/
│   ├── config/
│   ├── etl/
│   ├── generator/
│   ├── recommendations/
│   ├── validation/
│   └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── app.py
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

Add `.gitkeep` files where empty directories must remain in Git.

Generated large data files must not be committed.

==================================================
8. SYNTHETIC TELECOM ECOSYSTEM
==================================================

The synthetic dataset must model realistic relationships.

Do not generate unrelated random columns.

The data must behave like one connected telecom business.

Expected patterns:

- prepaid customers dominate
- urban regions have stronger data usage
- rural regions depend more heavily on voice
- youth and students prefer affordable data bundles
- SMEs use more voice and mobile money services
- corporate customers have lower churn and higher revenue
- high-value customers generate disproportionate revenue
- declining recharge frequency increases churn risk
- long inactivity periods lead to dormant and churned states
- relevant campaigns produce stronger response
- irrelevant campaigns produce weaker response
- December has higher communication, recharge, and mobile money activity
- January has a post-holiday slowdown
- weekends increase consumer data usage
- weekdays increase SME and corporate usage
- month-end increases mobile money activity
- data usage and revenue grow across the two years
- voice and SMS revenue grow slowly or decline
- churn may increase in low-value and low-engagement segments
- high-value churn produces substantial revenue loss

Use Tanzanian shillings.

Display currency as TZS.

==================================================
9. GEOGRAPHY
==================================================

Use a representative set of Tanzanian regions for version one:

- Dar es Salaam
- Arusha
- Mwanza
- Dodoma
- Mbeya
- Morogoro
- Tanga
- Kilimanjaro
- Kagera
- Mtwara
- Geita
- Tabora

Create synthetic districts associated with those regions.

Do not claim that generated regional distributions represent real operator market share.

Use geographic differences to influence:

- subscriber volume
- urbanization
- data usage
- voice dependency
- mobile money adoption
- recharge behaviour
- customer segment distribution
- campaign response
- revenue performance

==================================================
10. CORE DATASETS
==================================================

Create the following core datasets.

1. calendar

Suggested fields:

- date
- day
- month
- month_name
- month_start
- quarter
- year
- day_of_week
- is_weekend
- is_month_end
- reporting_month
- seasonality_factor
- holiday_period_indicator

2. regions

Suggested fields:

- region_id
- region_name
- district_name
- urbanization_level
- population_weight
- data_adoption_factor
- mobile_money_adoption_factor
- voice_usage_factor
- commercial_potential_factor

3. products

Products and services should include:

- voice
- SMS
- data bundles
- combo bundles
- international calling
- roaming
- VAS
- mobile money

Suggested fields:

- product_id
- product_name
- product_category
- service_type
- unit_price
- bundle_size
- validity_days
- target_segment
- active_from
- active_to

4. customers

Required fields:

- customer_id
- registration_date
- region
- district
- gender
- age
- age_group
- occupation
- customer_segment
- account_type
- sim_type
- preferred_language
- acquisition_channel
- initial_status
- smartphone_indicator
- mobile_money_registered
- churn_date
- reactivation_date

Suggested age groups:

- 18–24
- 25–34
- 35–44
- 45–54
- 55+

Suggested customer segments:

- Youth
- Mass Market
- High Value
- SME
- Corporate
- Rural
- Digital First

Suggested occupations:

- Student
- Informal Trader
- Farmer
- Salaried Employee
- Business Owner
- Transport Worker
- Public Servant
- Professional
- Unemployed
- Other

Account types:

- Prepaid
- Postpaid

SIM types:

- Physical SIM
- eSIM

5. daily_usage

Required fields:

- usage_date
- customer_id
- voice_minutes
- sms_count
- data_mb
- international_minutes
- roaming_minutes
- vas_events
- voice_revenue
- sms_revenue
- data_revenue
- international_revenue
- roaming_revenue
- vas_revenue
- total_usage_revenue

Revenue must be derived from usage or purchases.

Do not generate revenue independently.

6. recharges

Required fields:

- recharge_id
- customer_id
- recharge_timestamp
- recharge_type
- recharge_channel
- amount
- bundle_category
- bundle_size
- validity_days
- promotion_id
- region

Recharge types:

- airtime
- data bundle
- voice bundle
- SMS bundle
- combo bundle

Recharge channels:

- mobile money
- dealer
- bank
- mobile application
- USSD
- scratch card
- electronic recharge

7. mobile_money_transactions

Required fields:

- transaction_id
- customer_id
- transaction_timestamp
- transaction_type
- amount
- fee_revenue
- channel
- merchant_category
- origin_region
- destination_region
- transaction_status

Transaction types:

- Cash In
- Cash Out
- Send Money
- Merchant Payment
- Bill Payment
- Bank Transfer
- Airtime Purchase

Transaction statuses:

- Successful
- Failed
- Reversed

Fee revenue must be derived from configured fee bands.

8. campaigns

Campaigns should include:

- Back to School
- Ramadan
- Christmas
- Data Weekend
- Student Offer
- SME Promotion

Required fields:

- campaign_id
- campaign_name
- start_date
- end_date
- campaign_cost
- target_segment
- target_region
- campaign_channel
- promoted_product
- business_objective

9. campaign_responses

Required fields:

- campaign_id
- customer_id
- contacted
- responded
- converted
- conversion_date
- revenue_generated
- pre_campaign_revenue
- campaign_period_revenue
- post_campaign_revenue
- retained_after_30_days
- churned_after_campaign

Campaign response probability must be influenced by targeting relevance.

10. customer_events

Event types:

- SIM Registration
- SIM Swap
- Bundle Purchase
- Airtime Recharge
- Mobile Money Usage
- Complaint
- Churn
- Reactivation

Required fields:

- event_id
- customer_id
- event_timestamp
- event_type
- event_channel
- region
- related_transaction_id
- event_value

==================================================
11. CUSTOMER LIFECYCLE RULES
==================================================

Calculate lifecycle status from actual generated activity.

Definitions:

Active:
Customer has qualifying activity within the last 30 days.

At Risk:
No qualifying activity for 31 to 45 days.

Dormant:
No qualifying activity for 46 to 59 days.

Churned:
No qualifying activity for 60 or more days.

Reactivated:
Customer records valid activity after being classified as churned.

Qualifying activity may include:

- voice usage
- SMS usage
- data usage
- airtime recharge
- bundle purchase
- mobile money transaction

Create a monthly customer snapshot with one row per customer per month.

Required fields:

- reporting_month
- customer_id
- lifecycle_status
- last_activity_date
- inactivity_days
- monthly_revenue
- rolling_3_month_revenue
- monthly_voice_minutes
- monthly_sms_count
- monthly_data_mb
- recharge_count
- recharge_value
- mobile_money_active
- mobile_money_transaction_value
- newly_registered
- newly_churned
- newly_reactivated
- tenure_months
- value_segment

Suggested value segments:

- Low Value
- Medium Value
- High Value
- Very High Value

Document the value segmentation method.

Monthly churn rate:

Number of customers who newly became churned during the month
divided by
number of active customers at the beginning of the month
multiplied by 100.

Create tests for lifecycle status boundary conditions.

==================================================
12. KPI FRAMEWORK
==================================================

Executive KPIs:

- total subscribers
- active subscribers
- new subscribers
- subscriber growth
- churn rate
- reactivation rate
- total revenue
- revenue growth
- ARPU
- average recharge value
- recharge frequency
- mobile money active users
- mobile money transaction volume
- mobile money transaction value
- mobile money fee revenue
- campaign ROI

Revenue KPIs:

- total revenue
- voice revenue
- SMS revenue
- data revenue
- mobile money fee revenue
- VAS revenue
- roaming revenue
- international revenue
- revenue by segment
- revenue by region
- revenue per active user
- ARPU by segment
- revenue growth by service
- product revenue contribution

Subscriber KPIs:

- total subscribers
- active subscribers
- new subscribers
- subscriber growth
- prepaid share
- postpaid share
- active rate
- customer tenure
- customers by segment
- customers by region
- digital-first customers
- smartphone adoption

Retention KPIs:

- churn rate
- churn by segment
- churn by region
- churn by tenure
- churn by value segment
- revenue lost to churn
- high-value churn
- at-risk subscribers
- dormant subscribers
- reactivation rate

Recharge KPIs:

- total recharge value
- recharge count
- average recharge value
- recharge frequency
- recharge channel share
- bundle purchase share
- recharge value by segment
- recharge trend
- failed or declining recharge behaviour

Mobile money KPIs:

- registered users
- active users
- adoption rate
- transaction count
- transaction value
- average transaction value
- fee revenue
- transaction type share
- regional adoption
- merchant payment growth
- failed transaction rate

Campaign KPIs:

- campaign cost
- customers contacted
- response rate
- conversion rate
- revenue generated
- ROI
- cost per acquisition
- average revenue per converted customer
- post-campaign retention
- churn after campaign
- incremental revenue proxy

Do not claim true causal uplift unless an appropriate experimental method exists.

Describe campaign results as attributable or observed performance where necessary.

==================================================
13. ANALYTICAL DATA MODEL
==================================================

Create processed dimensions and facts.

Dimensions:

- dim_customer
- dim_product
- dim_region
- dim_date
- dim_campaign

Facts:

- fact_usage_daily
- fact_recharge
- fact_mobile_money
- fact_campaign_response
- fact_customer_events

Create analytical marts:

- customer_monthly_snapshot
- revenue_monthly_mart
- subscriber_monthly_mart
- churn_monthly_mart
- recharge_monthly_mart
- mobile_money_monthly_mart
- campaign_performance_mart
- regional_performance_mart
- executive_kpi_mart

Include comparison columns where applicable:

- previous_month_value
- month_over_month_change
- prior_year_value
- year_over_year_change
- rolling_3_month_average
- rolling_12_month_value
- year_to_date_value

==================================================
14. DASHBOARD MODULES
==================================================

The final Streamlit application must include:

1. Executive Overview
2. Subscriber Analytics
3. Revenue Analytics
4. Churn and Retention
5. Recharge Analytics
6. Mobile Money Analytics
7. Campaign Analytics
8. Regional Performance
9. Executive Recommendations

Global filters:

- reporting month
- date range
- region
- customer segment
- account type
- product category
- campaign where applicable

The dashboard must include:

- data freshness indicator
- filter reset
- clear units
- consistent TZS formatting
- clear comparison periods
- no-data handling
- cached data loading
- reusable components
- professional layout
- accessible chart titles
- concise executive explanations

Every page should contain:

1. KPI summary
2. trend analysis
3. segment or regional comparison
4. key finding
5. business impact
6. recommended action

Do not create a page containing only charts.

==================================================
15. EXECUTIVE RECOMMENDATION ENGINE
==================================================

Recommendations must be deterministic, explainable, and metric-supported.

Each recommendation must include:

- recommendation_id
- reporting_period
- module
- finding
- metric_name
- metric_value
- benchmark
- business_impact
- recommended_action
- priority
- responsible_department
- supporting_filters

Possible responsible departments:

- Commercial
- Marketing
- Customer Experience
- Finance
- Mobile Money
- Sales
- Regional Operations

Possible priorities:

- Critical
- High
- Medium
- Low

Example rules:

- ARPU declines while subscriber count increases
- high-value churn exceeds the company average
- subscriber growth rises while revenue declines
- data usage grows but data revenue remains flat
- recharge frequency declines in valuable segments
- a region grows subscribers but loses revenue
- mobile money adoption is materially below peer regions
- campaign ROI is negative
- campaign conversion is high but retention is weak
- churn is concentrated in a specific tenure group
- dormant subscribers increase for multiple consecutive months

Every recommendation should follow:

Finding
↓
Business impact
↓
Recommended action

Do not generate random or unsupported recommendations.

==================================================
16. REQUIRED COMMANDS
==================================================

The completed project should eventually support commands similar to:

python -m scripts.generate_reference_data --profile development

python -m scripts.generate_customers --profile development

python -m scripts.generate_usage --profile development

python -m scripts.generate_recharges --profile development

python -m scripts.generate_mobile_money --profile development

python -m scripts.generate_campaigns --profile development

python -m scripts.generate_customer_events --profile development

python -m scripts.run_pipeline --profile development

python -m scripts.validate_data --profile development

streamlit run app.py

pytest

pytest --cov=src

ruff check .

ruff format .

mypy src

Commands must provide useful logs and non-zero exit codes on critical failure.

==================================================
17. DEVELOPMENT PHASES
==================================================

Build the project in the following order.

Do not skip phases.

Do not begin the next phase without my explicit approval.

PHASE 1
Business specification, architecture, configuration, project scaffolding, documentation, development tooling, and initial tests.

PHASE 2
Reference datasets and customer master-data generation.

PHASE 3
Usage and recharge generation.

PHASE 4
Mobile money, campaign, and campaign-response generation.

PHASE 5
Customer events and monthly lifecycle modelling.

PHASE 6
ETL pipeline, processed dimensions, facts, and analytical marts.

PHASE 7
Reusable analytics services and deterministic recommendation engine.

PHASE 8
Streamlit design system, global filters, shared components, and Executive Overview.

PHASE 9
Build remaining analytical pages one page at a time.

PHASE 10
Performance optimization and deployment dataset preparation.

PHASE 11
README, diagrams, screenshots, testing, deployment configuration, and portfolio packaging.

==================================================
18. PHASE 1 TASK
==================================================

Start with Phase 1 only.

Do not generate full subscriber or transaction datasets.

Do not build Streamlit analytical pages.

Do not implement final KPI calculations.

Phase 1 objective:

Create the business specification, architecture, configuration system, project scaffolding, quality tooling, and initial documentation.

Required Phase 1 deliverables:

1. Inspect the current repository.

2. Present a brief implementation plan before modifying files.

3. Create or correct the required folder structure.

4. Create `pyproject.toml`.

Configure:

- Python version
- Ruff
- pytest
- pytest coverage
- mypy where practical
- package metadata

5. Create `requirements.txt`.

Include appropriate versions or sensible minimum versions for:

- pandas
- numpy
- pyarrow
- streamlit
- plotly
- pydantic
- pydantic-settings
- faker
- python-dotenv
- pytest
- pytest-cov
- ruff
- mypy

6. Create `.gitignore`.

Ignore:

- virtual environments
- Python caches
- editor files
- environment secrets
- test caches
- coverage outputs
- generated raw data
- generated processed data
- large exports
- Streamlit secrets

Keep required empty directories using `.gitkeep`.

7. Create `.env.example`.

Do not include secrets.

8. Create configuration models.

Required configuration fields:

- project name
- random seed
- start date
- end date
- reporting month
- subscriber count
- profile name
- batch size
- raw data path
- processed data path
- reference data path
- export path
- raw output format
- processed output format
- validation strictness
- logging level

Create profiles:

Development:
- 10,000 subscribers
- 2024-01-01 through 2025-12-31

Demo:
- 25,000 subscribers
- 2024-01-01 through 2025-12-31

Portfolio:
- 100,000 subscribers
- 2024-01-01 through 2025-12-31

Validate:

- subscriber count is positive
- start date is earlier than end date
- reporting month is inside the data range
- data period contains 24 complete months
- batch size is positive
- output formats are supported

9. Create path utilities.

Paths must be based on the repository root.

Do not depend on the current working directory.

10. Create logging configuration.

Use clear timestamps, log levels, and module names.

11. Create a basic CLI health check.

Example:

python -m scripts.health_check --profile development

The command should:

- load configuration
- resolve required paths
- create required output directories if allowed
- confirm the reporting period
- confirm subscriber count
- confirm package imports
- return a successful exit code

12. Create documentation:

docs/business_requirements.md

Include:

- business background
- business problem
- intended users
- business questions
- project scope
- out-of-scope items
- expected decisions supported by the platform

docs/kpi_dictionary.md

For each KPI include:

- KPI name
- business definition
- formula
- grain
- comparison method
- interpretation
- known limitations

docs/data_dictionary.md

Document all planned datasets and fields.

docs/synthetic_data_rules.md

Document:

- distributions
- relationships
- seasonality
- segment behaviour
- revenue derivation
- campaign behaviour
- limitations

docs/churn_methodology.md

Document:

- lifecycle definitions
- qualifying activity
- monthly churn formula
- reactivation
- limitations

docs/architecture.md

Document:

- source generation
- raw layer
- validation
- ETL
- processed layer
- analytics services
- recommendation engine
- Streamlit presentation

Include a Mermaid architecture diagram.

docs/validation_framework.md

Document:

- schema checks
- referential integrity
- range checks
- duplicate checks
- missing-value checks
- business-rule checks
- trend reasonableness checks
- critical versus warning failures

13. Create an initial professional README.

Include:

- project title
- executive summary
- business problem
- planned platform modules
- technology stack
- project structure
- development profiles
- current status
- local setup
- Phase 1 health-check command
- disclaimer that all data is synthetic

14. Add initial tests.

Tests must verify:

- configuration loads
- all three profiles are valid
- invalid subscriber count fails
- invalid date ranges fail
- reporting month outside the range fails
- the configured range contains 24 complete months
- paths resolve relative to the repository root
- required directories can be identified
- health-check logic succeeds for the development profile

15. Run quality checks:

ruff format .

ruff check .

pytest

mypy src where practical

16. Show me:

- implementation summary
- files created
- important design decisions
- commands executed
- test results
- unresolved risks
- exact commands I should run locally

17. Stop after Phase 1.

Do not generate customer data.

Do not start Phase 2.

Begin by inspecting the repository and presenting the Phase 1 implementation plan.