# Solar Financial Analysis - Quick Reference

## API Endpoints

### Calculate Comprehensive Analysis
```
POST /api/v1/financial-analysis/calculate
```

### Quick ROI Estimate
```
POST /api/v1/financial-analysis/quick-roi
```

### Calculate Loan Payment
```
POST /api/v1/financial-analysis/calculate-loan-payment
```

### Compare Scenarios
```
POST /api/v1/financial-analysis/compare-scenarios
```

### Get Financing Templates
```
GET /api/v1/financial-analysis/financing-templates
```

### Get Tax Incentive Templates
```
GET /api/v1/financial-analysis/tax-incentive-templates
```

## Key Metrics

| Metric | Formula | Good Value |
|--------|---------|------------|
| Simple ROI | (Total Savings / Investment) × 100 | > 200% |
| Payback Period | Investment / Annual Savings | < 10 years |
| NPV | Σ(CF_t / (1+r)^t) - Investment | > €10,000 |
| IRR | NPV = 0 | > 10% |
| BCR | PV Benefits / PV Costs | > 1.5 |

## Investment Grades

| Grade | NPV | IRR | Payback |
|-------|-----|-----|---------|
| Excellent | > €20,000 | > 15% | < 8 years |
| Good | > €10,000 | > 10% | < 12 years |
| Fair | > €0 | > 5% | < 15 years |
| Poor | < €0 | < 5% | > 15 years |

## Typical Values (Germany)

| Parameter | Typical Range |
|-----------|---------------|
| System Cost | €1,400-1,800/kWp |
| Electricity Price | €0.30-0.40/kWh |
| Feed-in Tariff | €0.07-0.09/kWh |
| Self-Consumption | 30-40% (without battery) |
| Self-Consumption | 60-80% (with battery) |
| System Degradation | 0.4-0.6% per year |
| Maintenance Cost | €150-300 per year |
| Discount Rate | 3-5% |

## Financing Options

### Cash Purchase
- **Down Payment**: 100%
- **Interest Rate**: 0%
- **Best NPV**: Yes
- **Liquidity Impact**: High

### 5-Year Loan
- **Down Payment**: 20%
- **Interest Rate**: 4-5%
- **Monthly Payment**: ~€250-300 (for €15k system)
- **Total Interest**: ~€1,500-2,000

### 10-Year Loan
- **Down Payment**: 20%
- **Interest Rate**: 5-6%
- **Monthly Payment**: ~€140-160 (for €15k system)
- **Total Interest**: ~€3,000-4,000

### Zero-Down Loan
- **Down Payment**: 0%
- **Interest Rate**: 6-7%
- **Monthly Payment**: ~€180-200 (for €15k system)
- **Total Interest**: ~€5,000-7,000

## German Tax Incentives

### KfW Förderung 270
- **Type**: Low-interest loan
- **Amount**: 10-15% of system cost
- **Timing**: Year 1
- **Eligibility**: Most residential systems

### BAFA Förderung
- **Type**: Direct grant
- **Amount**: 10-20% of system cost
- **Timing**: Year 1
- **Eligibility**: Specific programs

### Degressive AfA
- **Type**: Tax deduction
- **Amount**: 20-30% of system cost
- **Timing**: Years 1-5
- **Eligibility**: Business/commercial

## Sensitivity Analysis

### High Sensitivity Parameters
1. **Electricity Price** (1.15)
   - Most important factor
   - Monitor market trends
   
2. **Self-Consumption Rate** (0.95)
   - Consider battery storage
   - Optimize usage patterns

### Medium Sensitivity Parameters
3. **System Cost** (0.75)
   - Negotiate pricing
   - Compare quotes

4. **Discount Rate** (0.65)
   - Use appropriate rate
   - Consider risk

## Quick Decision Matrix

| Scenario | NPV | IRR | Payback | Decision |
|----------|-----|-----|---------|----------|
| High electricity price, low cost | > €25k | > 15% | < 8 yrs | **Strong Buy** |
| Average conditions | €15-25k | 10-15% | 8-12 yrs | **Buy** |
| Low electricity price, high cost | €5-15k | 5-10% | 12-15 yrs | **Consider** |
| Very unfavorable | < €5k | < 5% | > 15 yrs | **Avoid** |

## Common Pitfalls

❌ **Don't:**
- Overestimate self-consumption
- Ignore maintenance costs
- Use unrealistic electricity price increases
- Forget system degradation
- Ignore financing costs

✅ **Do:**
- Use conservative assumptions
- Include all costs
- Consider multiple scenarios
- Account for tax incentives
- Compare financing options

## Calculation Checklist

- [ ] System size and cost verified
- [ ] Production estimate realistic
- [ ] Current electricity price from recent bill
- [ ] Self-consumption rate appropriate
- [ ] Maintenance costs included
- [ ] Insurance costs included
- [ ] Discount rate appropriate
- [ ] Tax incentives researched
- [ ] Financing options compared
- [ ] Sensitivity analysis reviewed

## Example Results

### Typical Residential System (10 kWp)

```
System Cost: €16,999
Annual Production: 12,000 kWh
Self-Consumption: 35%

Results:
├─ NPV: €25,679
├─ IRR: 12.8%
├─ Payback: 8.7 years
├─ Lifetime Savings: €48,532
└─ Grade: Excellent
```

### With Battery Storage (10 kWp + 10 kWh)

```
System Cost: €22,999
Annual Production: 12,000 kWh
Self-Consumption: 65%

Results:
├─ NPV: €28,456
├─ IRR: 11.2%
├─ Payback: 10.3 years
├─ Lifetime Savings: €52,890
└─ Grade: Good
```

## Performance Benchmarks

| System Size | Typical NPV | Typical IRR | Typical Payback |
|-------------|-------------|-------------|-----------------|
| 5 kWp | €8,000-12,000 | 10-12% | 10-12 years |
| 10 kWp | €20,000-30,000 | 11-13% | 8-10 years |
| 15 kWp | €30,000-45,000 | 12-14% | 7-9 years |
| 20 kWp | €40,000-60,000 | 13-15% | 6-8 years |

## Support Resources

- **Full Guide**: FINANCIAL_ANALYSIS_GUIDE.md
- **API Docs**: /api/v1/docs
- **Demo Script**: demo_financial_analysis.py
- **Tests**: tests/test_financial_analysis_service.py

## Version

**Current Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Status**: Production Ready
