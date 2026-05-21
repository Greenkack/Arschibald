# Solar Calculation Results - Quick Reference

## Component Usage

### Basic Usage

```typescript
import SolarCalculationResults from '../components/solar/SolarCalculationResults';

<SolarCalculationResults
  results={calculationData}
  onEdit={() => handleEdit()}
  onSave={() => handleSave()}
  onGeneratePDF={() => handlePDF()}
  onView3D={() => handle3D()}
/>
```

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `results` | `SolarCalculationResponse` | Yes | Calculation results data |
| `onEdit` | `() => void` | No | Edit calculation callback |
| `onSave` | `() => void` | No | Save project callback |
| `onGeneratePDF` | `() => void` | No | Generate PDF callback |
| `onView3D` | `() => void` | No | View 3D model callback |

## Summary Cards

### 1. System Size Card (⚡)
- System size in kWp
- Module count
- Module capacity
- Required roof area

### 2. Annual Production Card (☀️)
- Annual production in kWh
- Specific yield (kWh/kWp)
- Data source indicator (PVGIS/Manual)

### 3. Self-Consumption Card (🏠)
- Self-consumption rate (%)
- Autarky degree (%)
- Self-consumption amount (kWh)
- Grid feed-in amount (kWh)

### 4. Annual Savings Card (💰)
- Annual savings (€)
- Feed-in revenue (€)
- 25-year total savings (€)

### 5. Payback Period Card (📈)
- Payback period (years)
- Investment cost (gross)
- Investment cost (net)

### 6. CO2 Savings Card (🌱)
- Annual CO2 savings (tons)
- 25-year total (tons)
- Equivalent trees
- Equivalent car kilometers

## Charts

### 1. Monthly Production Bar Chart
```typescript
// Shows monthly production distribution
// X-axis: Months (Jan-Dez)
// Y-axis: Production (kWh)
// Color: Orange (#f59e0b)
```

### 2. Energy Distribution Pie Chart
```typescript
// Shows self-consumption vs grid feed-in
// Segments:
//   - Eigenverbrauch (green)
//   - Netzeinspeisung (blue)
```

### 3. Payback Period Line Chart
```typescript
// Shows investment vs cumulative savings
// X-axis: Years
// Y-axis: Amount (€)
// Lines:
//   - Investment (red)
//   - Cumulative Savings (green)
```

### 4. Cumulative Savings Area Chart
```typescript
// Shows 25-year savings projection
// X-axis: Years (1-25)
// Y-axis: Cumulative Savings (€)
// Color: Blue (#3b82f6)
```

## Storage Analysis (Optional)

Displayed when `results.storage_analysis` is present:

- Storage capacity (kWh)
- Storage efficiency (%)
- Annual storage cycles
- Additional self-consumption (kWh)
- Contribution to autarky (%)

## Detailed Metrics

### System Data
- System size (kWp)
- Module count
- Module capacity (W)
- Specific yield (kWh/kWp)

### Energy Production
- Annual production (kWh)
- Self-consumption (kWh)
- Grid feed-in (kWh)
- Grid purchase (kWh)

### Economic Analysis
- Investment (net/gross) (€)
- Annual savings (€)
- Payback period (years)
- NPV (€) - if available
- IRR (%) - if available

### Environmental Impact
- Annual CO2 savings (kg)
- 25-year CO2 savings (tons)
- Equivalent trees
- Equivalent car km
- CO2 payback time (years) - if available

## Autarky Progress Bar

Visual representation of energy independence:
- Progress bar showing autarky degree
- Descriptive text explaining the percentage
- Storage contribution (if battery included)

## German Number Formatting

All numbers are formatted using German locale:

```typescript
// Numbers
1234.56 → "1.234,56"

// Currency
1234.56 → "1.234,56 €"

// Percentages
12.34 → "12,34%"
```

## Responsive Breakpoints

```css
/* Desktop */
@media (min-width: 1200px) {
  /* 3-column cards, 2-column charts */
}

/* Tablet */
@media (max-width: 1200px) {
  /* 2-column cards, 1-column charts */
}

/* Mobile */
@media (max-width: 768px) {
  /* 1-column layout */
}

/* Small Mobile */
@media (max-width: 480px) {
  /* Compact layout */
}
```

## Styling Classes

### Main Container
```css
.solar-calculation-results
```

### Header
```css
.results-header
.results-title
.results-timestamp
.results-actions
```

### Cards
```css
.summary-cards
.summary-card
.system-size-card
.production-card
.self-consumption-card
.savings-card
.payback-card
.co2-card
```

### Charts
```css
.charts-section
.chart-card
.chart-card.full-width
```

### Metrics
```css
.detailed-metrics-card
.metrics-grid
.metric-section
.metric-row
```

### Autarky
```css
.autarky-card
.autarky-visualization
.autarky-progress
.autarky-description
```

## Action Handlers

### Edit Calculation
```typescript
const handleEdit = () => {
  // Return to form with current data
  setShowForm(true);
};
```

### Save Project
```typescript
const handleSave = async () => {
  // Save calculation as project
  await api.post('/api/v1/projects', {
    name: 'Project Name',
    calculation: results
  });
};
```

### Generate PDF
```typescript
const handleGeneratePDF = async () => {
  // Generate PDF report
  await api.post('/api/v1/pdf/generate', {
    calculation_id: results.calculation_id
  });
};
```

### View 3D Model
```typescript
const handleView3D = () => {
  // Navigate to 3D visualization
  navigate('/3d-view', { state: { results } });
};
```

## Data Transformations

### Monthly Data to Array
```typescript
const monthlyProductionToArray = (data: MonthlyData): number[] => {
  return [
    data.january, data.february, data.march, data.april,
    data.may, data.june, data.july, data.august,
    data.september, data.october, data.november, data.december
  ];
};
```

### Energy Distribution
```typescript
const getEnergyDistribution = () => {
  return [
    {
      name: 'Eigenverbrauch',
      value: results.self_consumption.annual_self_consumption_kwh,
      color: '#10b981'
    },
    {
      name: 'Netzeinspeisung',
      value: results.self_consumption.annual_grid_feed_in_kwh,
      color: '#3b82f6'
    }
  ];
};
```

### Payback Data
```typescript
const generatePaybackData = () => {
  const data = [];
  const investment = results.economic_analysis.total_investment_cost_gross;
  const annualSavings = results.economic_analysis.annual_savings_year1;
  let cumulativeSavings = 0;

  for (let year = 0; year <= Math.ceil(results.economic_analysis.payback_period_years) + 2; year++) {
    if (year > 0) {
      cumulativeSavings += annualSavings;
    }
    data.push({ year, investment, savings: cumulativeSavings });
  }

  return data;
};
```

### Cumulative Savings
```typescript
const generateCumulativeSavings = () => {
  const data = [];
  const annualSavings = results.economic_analysis.annual_savings_year1;
  let cumulative = 0;

  for (let year = 1; year <= 25; year++) {
    cumulative += annualSavings;
    data.push({ year, savings: cumulative });
  }

  return data;
};
```

## Error Handling

### Warnings Display
```typescript
{results.warnings.length > 0 && (
  <Card className="warnings-card">
    <h4>⚠️ Hinweise</h4>
    <ul>
      {results.warnings.map((warning, index) => (
        <li key={index}>{warning}</li>
      ))}
    </ul>
  </Card>
)}
```

### Errors Display
```typescript
{results.errors.length > 0 && (
  <Card className="errors-card">
    <h4>❌ Fehler</h4>
    <ul>
      {results.errors.map((error, index) => (
        <li key={index}>{error}</li>
      ))}
    </ul>
  </Card>
)}
```

## Customization

### Color Scheme
```css
/* Primary colors */
--system-size-color: #f59e0b;
--production-color: #f59e0b;
--self-consumption-color: #10b981;
--savings-color: #10b981;
--payback-color: #3b82f6;
--co2-color: #10b981;
```

### Card Hover Effect
```css
.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}
```

### Chart Height
```typescript
<BarChart height={300} />
<LineChart height={350} />
<AreaChart height={350} />
```

## Best Practices

1. **Always validate data**: Check for null/undefined values
2. **Use German formatting**: Apply to all numeric displays
3. **Provide fallbacks**: Handle missing optional fields
4. **Optimize performance**: Memoize expensive calculations
5. **Test responsiveness**: Verify on multiple screen sizes
6. **Accessibility**: Ensure keyboard navigation works
7. **Error handling**: Display meaningful error messages
8. **Loading states**: Show loading indicators during API calls

## Common Issues

### Issue: Charts not rendering
**Solution**: Ensure chart data is properly formatted and not empty

### Issue: German formatting not working
**Solution**: Import and use `germanFormatter` utility

### Issue: Layout breaking on mobile
**Solution**: Check responsive breakpoints and grid settings

### Issue: Action buttons not working
**Solution**: Verify callback props are passed correctly

## Resources

- [PrimeReact Documentation](https://primereact.org/)
- [Recharts Documentation](https://recharts.org/)
- [German Number Formatting](../utils/germanNumberFormatter.ts)
- [API Documentation](../../backend/docs/API_DOCUMENTATION.md)

---

**Last Updated**: 2024
**Component Version**: 1.0.0
