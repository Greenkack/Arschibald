# Sales Pipeline - Quick Reference

## Quick Start

### 1. View Pipeline
```
Navigate to: CRM → Pipeline
```

### 2. Create Opportunity
```
Click "New Opportunity" → Fill form → Save
```

### 3. Move Opportunity
```
Drag opportunity card to different stage column
```

### 4. View Analytics
```
Navigate to: CRM → Pipeline → Analytics tab
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Stage** | Step in sales process (Lead, Qualified, Proposal, etc.) |
| **Opportunity** | Potential sale with estimated value |
| **Probability** | Likelihood of winning (0-100%) |
| **Weighted Value** | Estimated value × Probability |
| **Win Rate** | Percentage of opportunities won |
| **Sales Cycle** | Average time from creation to close |

## Common Actions

### Create Stage
```typescript
POST /api/v1/pipeline/stages
{
  "name": "Demo",
  "stage_type": "qualified",
  "order_index": 2,
  "probability": 30.0,
  "color": "#3B82F6"
}
```

### Create Opportunity
```typescript
POST /api/v1/pipeline/opportunities
{
  "name": "ABC Corp - Solar",
  "stage_id": 1,
  "estimated_value": 50000,
  "owner_id": 1,
  "expected_close_date": "2024-12-31"
}
```

### Move Stage
```typescript
POST /api/v1/pipeline/opportunities/{id}/change-stage
{
  "stage_id": 3,
  "reason": "Proposal accepted"
}
```

### Mark Won
```typescript
POST /api/v1/pipeline/opportunities/{id}/win
{
  "actual_value": 52000,
  "win_reason": "Best offer"
}
```

### Mark Lost
```typescript
POST /api/v1/pipeline/opportunities/{id}/lose
{
  "loss_reason": "Price too high",
  "competitor": "Competitor X"
}
```

## Analytics Queries

### Get Overview
```typescript
GET /api/v1/pipeline/analytics
?start_date=2024-01-01&end_date=2024-12-31
```

### Win/Loss Analysis
```typescript
GET /api/v1/pipeline/analytics/win-loss
?start_date=2024-01-01&end_date=2024-12-31
```

### Generate Forecast
```typescript
POST /api/v1/pipeline/forecast
{
  "period_start": "2024-12-01",
  "period_end": "2025-02-28"
}
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `N` | New opportunity |
| `F` | Focus search |
| `A` | View analytics |
| `R` | Refresh pipeline |
| `Esc` | Close dialog |

## Status Indicators

| Color | Meaning |
|-------|---------|
| 🔵 Blue | Lead/Qualified |
| 🟡 Yellow | Proposal |
| 🟠 Orange | Negotiation |
| 🟢 Green | Won |
| 🔴 Red | Lost |

## Filters

### By Stage
```
?stage_id=1
```

### By Owner
```
?owner_id=5
```

### By Status
```
?status=active
```

### By Date Range
```
?start_date=2024-01-01&end_date=2024-12-31
```

## Metrics Explained

### Total Value
Sum of all estimated values in pipeline

### Weighted Value
Sum of (estimated value × probability) for all opportunities

### Win Rate
```
Won / (Won + Lost) × 100
```

### Average Deal Size
```
Total Value / Number of Opportunities
```

### Sales Cycle
```
Average days from creation to close
```

## Best Practices

✅ **DO**
- Update opportunities regularly
- Set realistic close dates
- Document win/loss reasons
- Use consistent stage criteria
- Review pipeline weekly

❌ **DON'T**
- Leave stale opportunities
- Skip required fields
- Ignore stage time limits
- Forget to log activities
- Neglect analytics

## Troubleshooting

### Can't Move Opportunity
- Check required fields
- Verify permissions
- Ensure stage is active

### Analytics Not Showing
- Check date range
- Verify data exists
- Refresh page

### Forecast Inaccurate
- Set close dates
- Update probabilities
- Review historical data

## German Number Formatting

All currency values displayed in German format:
- **16.999,00 €** (not $16,999.00)
- **85,5%** (not 85.5%)
- **2 Dezimalstellen** (2 decimal places)

## Support

📧 Email: support@example.com
📞 Phone: +49 123 456789
📚 Docs: /docs/SALES_PIPELINE_GUIDE.md
