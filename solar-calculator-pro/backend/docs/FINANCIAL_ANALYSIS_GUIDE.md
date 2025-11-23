# Solar Financial Analysis Service - Complete Guide

## Overview

The Solar Financial Analysis Service provides comprehensive financial calculations for solar PV projects, including:

- **ROI (Return on Investment)** calculations
- **NPV (Net Present Value)** analysis
- **IRR (Internal Rate of Return)** calculations
- **Payback Period** analysis (simple and discounted)
- **25-year Cash Flow** projections
- **Financing Options** comparison
- **Sensitivity Analysis** on key parameters
- **Tax Incentives** integration
- **Environmental Impact** calculations

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [API Reference](#api-reference)
4. [Financial Metrics Explained](#financial-metrics-explained)
5. [Financing Options](#financing-options)
6. [Tax Incentives](#tax-incentives)
7. [Sensitivity Analysis](#sensitivity-analysis)
8. [Best Practices](#best-practices)
9. [Examples](#examples)

## Quick Start

### Basic Analysis

```python
from models.financial_schemas import FinancialAnalysisRequest
from services.financial_analysis_service import FinancialAnalysisService

# Create service
service = FinancialAnalysisService()

# Create request
request = FinancialAnalysisRequest(
    system_size_kwp=10.5,
    total_system_cost=16999.00,
    annual_production_kwh=12000,
    current_electricity_price=0.35,
    electricity_price_increase=3.0,
    feed_in_tariff=0.08,
    annual_consumption_kwh=4000,
    self_consumption_rate=35.0,
    discount_rate=4.0,
    analysis_period_years=25
)

# Calculate analysis
result = service.calculate_comprehensive_analysis(request)

# Access results
print(f"NPV: €{result.npv_analysis.npv:,.2f}")
print(f"IRR: {result.irr_analysis.irr_percent:.2f}%")
print(f"Payback: {result.roi_analysis.simple_payback_years:.1f} years")
```

### API Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/financial-analysis/calculate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "system_size_kwp": 10.5,
    "total_system_cost": 16999.00,
    "annual_production_kwh": 12000,
    "current_electricity_price": 0.35,
    "electricity_price_increase": 3.0,
    "feed_in_tariff": 0.08,
    "annual_consumption_kwh": 4000,
    "self_consumption_rate": 35.0,
    "discount_rate": 4.0,
    "analysis_period_years": 25
  }'
```

## Core Concepts

### 1. Return on Investment (ROI)

ROI measures the profitability of the solar investment:

- **Simple ROI**: Total savings divided by initial investment
- **Payback Period**: Time required to recover the initial investment
- **Average Annual Return**: Average yearly profit as percentage of investment

### 2. Net Present Value (NPV)

NPV calculates the present value of all future cash flows:

- **Positive NPV**: Investment creates value
- **Negative NPV**: Investment destroys value
- **Benefit-Cost Ratio**: Ratio of present value of benefits to costs

### 3. Internal Rate of Return (IRR)

IRR is the discount rate that makes NPV equal to zero:

- **IRR > Discount Rate**: Good investment
- **IRR < Discount Rate**: Poor investment
- **Modified IRR (MIRR)**: More realistic version accounting for reinvestment rate

### 4. Cash Flow Projections

Yearly projections include:

- Energy production (with degradation)
- Electricity savings
- Feed-in revenue
- Maintenance and insurance costs
- Loan payments
- Tax benefits
- Net cash flow
- Cumulative cash flow

## API Reference

### POST /api/v1/financial-analysis/calculate

Calculate comprehensive financial analysis.

**Request Body:**

```json
{
  "system_size_kwp": 10.5,
  "total_system_cost": 16999.00,
  "annual_production_kwh": 12000,
  "current_electricity_price": 0.35,
  "electricity_price_increase": 3.0,
  "feed_in_tariff": 0.08,
  "annual_consumption_kwh": 4000,
  "self_consumption_rate": 35.0,
  "system_degradation": 0.5,
  "maintenance_cost_annual": 200.0,
  "maintenance_cost_increase": 2.0,
  "insurance_cost_annual": 150.0,
  "discount_rate": 4.0,
  "analysis_period_years": 25,
  "income_tax_rate": 30.0,
  "financing_options": [],
  "tax_incentives": []
}
```

**Response:**

```json
{
  "system_size_kwp": 10.5,
  "total_system_cost": 16999.00,
  "analysis_period_years": 25,
  "roi_analysis": {
    "simple_roi_percent": 285.5,
    "simple_payback_years": 8.7,
    "discounted_payback_years": 11.2,
    "total_lifetime_savings": 48532.50,
    "average_annual_return": 1941.30,
    "average_annual_return_percent": 11.4
  },
  "npv_analysis": {
    "npv": 25678.90,
    "npv_positive": true,
    "present_value_benefits": 42677.90,
    "present_value_costs": 16999.00,
    "benefit_cost_ratio": 2.51
  },
  "irr_analysis": {
    "irr_percent": 12.8,
    "irr_exceeds_discount_rate": true,
    "modified_irr_percent": 11.5
  },
  "yearly_cash_flows": [...],
  "financing_comparisons": [...],
  "sensitivity_analyses": [...],
  "investment_grade": "Excellent",
  "key_insights": [...]
}
```

### POST /api/v1/financial-analysis/quick-roi

Calculate quick ROI estimate without full analysis.

**Parameters:**
- `system_cost`: Total system cost in EUR
- `annual_savings`: Estimated annual savings in EUR
- `analysis_years`: Number of years for analysis (default: 25)

### POST /api/v1/financial-analysis/calculate-loan-payment

Calculate monthly loan payment.

**Parameters:**
- `loan_amount`: Loan amount in EUR
- `interest_rate`: Annual interest rate in %
- `term_years`: Loan term in years

### POST /api/v1/financial-analysis/compare-scenarios

Compare multiple financial scenarios (max 5).

**Request Body:** Array of `FinancialAnalysisRequest` objects

### GET /api/v1/financial-analysis/financing-templates

Get common financing option templates.

### GET /api/v1/financial-analysis/tax-incentive-templates

Get common tax incentive templates for Germany.

## Financial Metrics Explained

### Simple ROI

```
Simple ROI (%) = (Total Lifetime Savings / Initial Investment) × 100
```

**Example:**
- Initial Investment: €16,999
- Total Savings (25 years): €48,532
- Simple ROI: (48,532 / 16,999) × 100 = 285.5%

### Simple Payback Period

```
Payback Period = Initial Investment / Annual Savings
```

**Example:**
- Initial Investment: €16,999
- Average Annual Savings: €1,941
- Payback Period: 16,999 / 1,941 = 8.7 years

### Net Present Value (NPV)

```
NPV = Σ (Cash Flow_t / (1 + r)^t) - Initial Investment
```

Where:
- `Cash Flow_t` = Net cash flow in year t
- `r` = Discount rate
- `t` = Year number

**Example:**
- Initial Investment: €16,999
- Discount Rate: 4%
- Present Value of Benefits: €42,678
- NPV: 42,678 - 16,999 = €25,679

### Internal Rate of Return (IRR)

IRR is the discount rate where NPV = 0.

**Interpretation:**
- IRR > Discount Rate: Accept project
- IRR < Discount Rate: Reject project
- IRR = Discount Rate: Indifferent

**Example:**
- IRR: 12.8%
- Discount Rate: 4.0%
- Decision: Accept (IRR exceeds discount rate)

### Benefit-Cost Ratio

```
BCR = Present Value of Benefits / Present Value of Costs
```

**Interpretation:**
- BCR > 1: Benefits exceed costs
- BCR < 1: Costs exceed benefits
- BCR = 1: Break-even

**Example:**
- PV Benefits: €42,678
- PV Costs: €16,999
- BCR: 42,678 / 16,999 = 2.51

## Financing Options

### Cash Purchase

```python
FinancingOption(
    type=FinancingType.CASH,
    name="Cash Purchase",
    down_payment=16999.00,
    down_payment_percent=100.0,
    loan_amount=0.0,
    interest_rate=0.0,
    term_years=0
)
```

**Pros:**
- No interest payments
- Best NPV
- Immediate ownership

**Cons:**
- High upfront cost
- Opportunity cost of capital

### Loan Financing

```python
FinancingOption(
    type=FinancingType.LOAN,
    name="10-Year Loan",
    down_payment=3399.80,
    down_payment_percent=20.0,
    loan_amount=13599.20,
    interest_rate=5.0,
    term_years=10
)
```

**Pros:**
- Lower upfront cost
- Preserve liquidity
- Tax-deductible interest (in some cases)

**Cons:**
- Interest payments reduce returns
- Lower NPV than cash
- Longer payback period

### Loan Payment Calculation

```python
Monthly Payment = P × [r(1+r)^n] / [(1+r)^n - 1]
```

Where:
- `P` = Loan amount
- `r` = Monthly interest rate (annual rate / 12)
- `n` = Number of payments (years × 12)

**Example:**
- Loan Amount: €13,599.20
- Interest Rate: 5.0% annual (0.4167% monthly)
- Term: 10 years (120 months)
- Monthly Payment: €144.31

## Tax Incentives

### German Tax Incentives

#### 1. KfW Förderung 270

```python
TaxIncentive(
    type=TaxIncentiveType.GRANT,
    name="KfW Förderung 270",
    amount=1699.90,  # 10% of system cost
    year_received=1,
    description="KfW loan program for renewable energy"
)
```

**Details:**
- Low-interest loan program
- Typically 10-15% of system cost
- Received in year 1

#### 2. BAFA Förderung

```python
TaxIncentive(
    type=TaxIncentiveType.GRANT,
    name="BAFA Förderung",
    amount=2549.85,  # 15% of system cost
    year_received=1,
    description="Federal Office for Economic Affairs grant"
)
```

**Details:**
- Direct grant
- Typically 10-20% of system cost
- Received in year 1

#### 3. Degressive AfA (Accelerated Depreciation)

```python
TaxIncentive(
    type=TaxIncentiveType.DEPRECIATION,
    name="Degressive AfA",
    amount=3399.80,  # 20% of system cost
    year_received=1,
    description="Accelerated depreciation for tax purposes"
)
```

**Details:**
- Tax deduction
- Typically 20-30% of system cost
- Spread over multiple years

### Impact on Financial Metrics

Tax incentives improve:
- **NPV**: Increases by incentive amount (discounted)
- **IRR**: Increases due to higher early cash flows
- **Payback Period**: Decreases significantly
- **Investment Grade**: Often improves by one level

## Sensitivity Analysis

Sensitivity analysis shows how NPV changes with key parameters:

### Parameters Analyzed

1. **Electricity Price** (±30%)
2. **System Cost** (±20%)
3. **Self-Consumption Rate** (±50%)
4. **Discount Rate** (±50%)

### Interpretation

**Sensitivity Percentage:**
- High sensitivity (>1.0): NPV is very sensitive to this parameter
- Low sensitivity (<0.5): NPV is relatively insensitive

**Example:**
```
Parameter: electricity_price
Base Value: €0.35/kWh
Low Value: €0.20/kWh (-43%)
High Value: €0.50/kWh (+43%)
NPV @ Low: €12,345
NPV @ Base: €25,679
NPV @ High: €39,012
Sensitivity: 1.15 (NPV changes 1.15% for every 1% change in electricity price)
```

### Risk Assessment

- **High Sensitivity**: Focus on accurate forecasting
- **Low Sensitivity**: Less critical for decision-making

## Best Practices

### 1. Input Data Quality

- Use accurate system cost estimates
- Base electricity prices on recent bills
- Use realistic self-consumption rates (30-40% typical)
- Consider local feed-in tariffs

### 2. Conservative Assumptions

- Use conservative electricity price increases (2-3%)
- Account for system degradation (0.5% annually)
- Include maintenance costs (€150-300/year)
- Use appropriate discount rate (3-5%)

### 3. Scenario Analysis

Always analyze multiple scenarios:
- **Best Case**: High electricity prices, low system cost
- **Base Case**: Realistic assumptions
- **Worst Case**: Low electricity prices, high system cost

### 4. Financing Decisions

Consider:
- **Cash if available**: Best NPV
- **Loan if needed**: Preserve liquidity
- **Compare options**: Use financing comparison feature

### 5. Tax Incentives

- Research available incentives
- Include all applicable programs
- Verify eligibility requirements
- Consider timing of benefits

## Examples

### Example 1: Residential System

```python
request = FinancialAnalysisRequest(
    system_size_kwp=8.5,
    total_system_cost=14999.00,
    annual_production_kwh=9500,
    current_electricity_price=0.35,
    electricity_price_increase=3.0,
    feed_in_tariff=0.08,
    annual_consumption_kwh=3500,
    self_consumption_rate=40.0,
    discount_rate=4.0,
    analysis_period_years=25
)
```

**Expected Results:**
- NPV: €18,000-22,000
- IRR: 11-13%
- Payback: 9-11 years
- Investment Grade: Good

### Example 2: Commercial System

```python
request = FinancialAnalysisRequest(
    system_size_kwp=50.0,
    total_system_cost=75000.00,
    annual_production_kwh=55000,
    current_electricity_price=0.25,
    electricity_price_increase=2.5,
    feed_in_tariff=0.07,
    annual_consumption_kwh=40000,
    self_consumption_rate=70.0,
    discount_rate=5.0,
    analysis_period_years=20
)
```

**Expected Results:**
- NPV: €60,000-80,000
- IRR: 14-16%
- Payback: 7-9 years
- Investment Grade: Excellent

### Example 3: With Battery Storage

```python
request = FinancialAnalysisRequest(
    system_size_kwp=10.5,
    total_system_cost=22999.00,  # Includes battery
    annual_production_kwh=12000,
    current_electricity_price=0.35,
    electricity_price_increase=3.0,
    feed_in_tariff=0.08,
    annual_consumption_kwh=4000,
    self_consumption_rate=65.0,  # Higher with battery
    discount_rate=4.0,
    analysis_period_years=25
)
```

**Expected Results:**
- NPV: €25,000-30,000
- IRR: 10-12%
- Payback: 10-12 years
- Investment Grade: Good

## Troubleshooting

### Issue: Negative NPV

**Possible Causes:**
- System cost too high
- Electricity price too low
- Self-consumption rate too low
- Discount rate too high

**Solutions:**
- Negotiate better system price
- Increase self-consumption (add battery)
- Consider tax incentives
- Review discount rate assumptions

### Issue: Long Payback Period

**Possible Causes:**
- High system cost
- Low electricity savings
- Low self-consumption

**Solutions:**
- Reduce system size
- Increase self-consumption
- Consider financing options
- Add battery storage

### Issue: Low IRR

**Possible Causes:**
- Poor system economics
- High opportunity cost
- Unfavorable market conditions

**Solutions:**
- Improve system design
- Maximize self-consumption
- Utilize tax incentives
- Consider alternative investments

## Support

For questions or issues:
- Email: support@solar-calculator-pro.com
- Documentation: https://docs.solar-calculator-pro.com
- API Reference: https://api.solar-calculator-pro.com/docs

## Version History

- **v1.0.0** (2024-01-15): Initial release
  - ROI, NPV, IRR calculations
  - Cash flow projections
  - Financing comparisons
  - Sensitivity analysis
  - Tax incentives support
