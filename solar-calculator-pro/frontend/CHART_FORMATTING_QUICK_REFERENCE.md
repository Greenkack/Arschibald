# Chart Formatting Quick Reference

Quick reference for applying German number formatting to charts.

**Task:** 218 - Chart and Visualization Formatting  
**Requirements:** 14.3

## Quick Import

```typescript
import {
  // Recharts formatters
  rechartsAxisTickFormatter,
  rechartsTooltipFormatter,
  rechartsCurrencyAxisTickFormatter,
  rechartsCurrencyTooltipFormatter,
  rechartsPercentAxisTickFormatter,
  rechartsPercentTooltipFormatter,
  
  // Chart.js formatters
  chartJsAxisTickCallback,
  chartJsTooltipCallback,
  chartJsCurrencyAxisTickCallback,
  chartJsCurrencyTooltipCallback,
  chartJsPercentAxisTickCallback,
  chartJsPercentTooltipCallback,
  
  // Plotly formatters
  getPlotlyFormatConfig,
  getPlotlyHoverTemplate,
  getPlotlyCurrencyHoverTemplate,
  getPlotlyPercentHoverTemplate,
  
  // Helper functions
  createRechartsConfig,
  createChartJsConfig,
  formatChartData,
} from './utils/chartFormatting';

import { germanFormatter } from './utils/germanNumberFormatter';
```

## Recharts

### Line Chart

```typescript
<LineChart data={data}>
  <YAxis tickFormatter={rechartsAxisTickFormatter} />
  <Tooltip formatter={rechartsTooltipFormatter} />
</LineChart>
```

### Bar Chart (Currency)

```typescript
<BarChart data={data}>
  <YAxis tickFormatter={(v) => rechartsCurrencyAxisTickFormatter(v, '€')} />
  <Tooltip formatter={(v, n, p) => rechartsCurrencyTooltipFormatter(v, n, p, '€')} />
</BarChart>
```

### Pie Chart (Percent)

```typescript
<PieChart>
  <Pie
    label={(entry) => germanFormatter.formatPercent(entry.value * 100, false)}
  />
  <Tooltip formatter={rechartsPercentTooltipFormatter} />
</PieChart>
```

### Area Chart

```typescript
<AreaChart data={data}>
  <YAxis tickFormatter={(v) => rechartsCurrencyAxisTickFormatter(v, '€')} />
  <Tooltip formatter={(v, n, p) => rechartsCurrencyTooltipFormatter(v, n, p, '€')} />
</AreaChart>
```

### Using Config Helper

```typescript
const config = createRechartsConfig('currency', '€');

<LineChart data={data}>
  <YAxis tickFormatter={config.yAxis.tickFormatter} />
  <Tooltip formatter={config.tooltip.formatter} />
</LineChart>
```

## Chart.js

### Basic Chart

```typescript
const config = {
  options: {
    scales: {
      y: {
        ticks: {
          callback: chartJsAxisTickCallback,
        },
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: chartJsTooltipCallback,
        },
      },
    },
  },
};
```

### Currency Chart

```typescript
const config = {
  options: {
    scales: {
      y: {
        ticks: {
          callback: (v) => chartJsCurrencyAxisTickCallback(v, '€'),
        },
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (ctx) => chartJsCurrencyTooltipCallback(ctx, '€'),
        },
      },
    },
  },
};
```

### Using Config Helper

```typescript
const config = createChartJsConfig('currency', '€');

const chartConfig = {
  type: 'bar',
  data: { /* ... */ },
  options: {
    ...config,
  },
};
```

## Plotly

### Basic Chart

```typescript
const data = [{
  x: ['Jan', 'Feb', 'Mar'],
  y: [450.5, 620.75, 890.25],
  hovertemplate: getPlotlyHoverTemplate('Production'),
}];

const layout = {
  yaxis: {
    tickformat: ',.2f',
    separators: ',.',
  },
};

Plotly.newPlot('chart', data, layout, getPlotlyFormatConfig());
```

### Currency Chart

```typescript
const data = [{
  x: ['A', 'B', 'C'],
  y: [8500.50, 2300.75, 3200.25],
  hovertemplate: getPlotlyCurrencyHoverTemplate('Cost', '€'),
}];

const layout = {
  yaxis: {
    tickformat: ',.2f',
    ticksuffix: ' €',
    separators: ',.',
  },
};
```

## Direct Formatting

### Numbers

```typescript
germanFormatter.format(1234.56);           // "1.234,56"
formatChartAxis(1234.56);                  // "1.234,56"
```

### Currency

```typescript
germanFormatter.formatCurrency(1234.56, '€');  // "1.234,56 €"
formatChartAxisCurrency(1234.56, '€');         // "1.234,56 €"
```

### Percentages

```typescript
germanFormatter.formatPercent(35, false);      // "35,00 %"
formatChartAxisPercent(0.35);                  // "35,00 %"
```

## Data Formatting

```typescript
// Format array of numbers
formatChartData([1234.56, 2345.67], 'number');
// ["1.234,56", "2.345,67"]

// Format array of currency values
formatChartData([1000, 2000], 'currency', '€');
// ["1.000,00 €", "2.000,00 €"]

// Format array of percentages
formatChartData([0.15, 0.25], 'percent');
// ["15,00 %", "25,00 %"]
```

## Common Patterns

### Axis with Label

```typescript
<YAxis tickFormatter={rechartsAxisTickFormatter}>
  <Label 
    value="Production (kWh)" 
    angle={-90} 
    position="insideLeft" 
  />
</YAxis>
```

### Custom Legend

```typescript
<Legend 
  formatter={(value) => {
    const labels = {
      production: 'Production (kWh)',
      consumption: 'Consumption (kWh)',
    };
    return labels[value] || value;
  }}
/>
```

### Data Labels on Bars

```typescript
<Bar dataKey="value">
  <LabelList 
    dataKey="value" 
    position="top"
    formatter={(v) => germanFormatter.format(v)}
  />
</Bar>
```

### Responsive Container

```typescript
<ResponsiveContainer width="100%" height={400}>
  <LineChart data={data}>
    {/* Chart content */}
  </LineChart>
</ResponsiveContainer>
```

## Format Examples

| Input | Type | Output |
|-------|------|--------|
| 1234.56 | Number | 1.234,56 |
| 1234.56 | Currency (€) | 1.234,56 € |
| 0.35 | Percent | 35,00 % |
| 1234567.89 | Number | 1.234.567,89 |
| 15000 | Currency (€) | 15.000,00 € |
| 0.1234 | Percent | 12,34 % |

## Requirements Checklist

- ✅ Format axis labels in all charts
- ✅ Apply German formatting to chart tooltips
- ✅ Format legend values
- ✅ Apply formatting to data labels
- ✅ Format numbers in chart exports

## See Also

- [Complete Chart Formatting Guide](./CHART_FORMATTING_GUIDE.md)
- [Chart Formatting Demo](./src/examples/ChartFormattingDemo.tsx)
- [German Number Formatter](./src/utils/germanNumberFormatter.ts)
- [Chart Formatting Utilities](./src/utils/chartFormatting.ts)
