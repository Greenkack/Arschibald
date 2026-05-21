# Chart and Visualization Formatting Guide

Complete guide for applying German number formatting to all charts and visualizations in the Solar Calculator Pro application.

**Requirements:** 14.3  
**Task:** 218 - Chart and Visualization Formatting

## Table of Contents

1. [Overview](#overview)
2. [Formatting Functions](#formatting-functions)
3. [Recharts Integration](#recharts-integration)
4. [Chart.js Integration](#chartjs-integration)
5. [Plotly Integration](#plotly-integration)
6. [Chart Export Formatting](#chart-export-formatting)
7. [Examples](#examples)
8. [Best Practices](#best-practices)

## Overview

All charts and visualizations in the application use German number formatting:
- **Decimal separator:** Comma (,)
- **Thousands separator:** Dot (.)
- **Decimal places:** Exactly 2
- **Format example:** 1.234,56

### Formatting Coverage

✅ **Axis Labels** - All X and Y axis labels  
✅ **Tooltips** - Interactive hover tooltips  
✅ **Legends** - Chart legends and keys  
✅ **Data Labels** - Labels on data points  
✅ **Exports** - PNG, SVG, PDF, and data exports

## Formatting Functions

### Basic Formatters

```typescript
import { germanFormatter } from './utils/germanNumberFormatter';

// Format number: 1234.56 → "1.234,56"
germanFormatter.format(1234.56);

// Format currency: 1234.56 → "1.234,56 €"
germanFormatter.formatCurrency(1234.56, '€');

// Format percent: 0.35 → "35,00 %"
germanFormatter.formatPercent(35, false);
```

### Chart-Specific Formatters

```typescript
import {
  formatChartAxis,
  formatChartAxisCurrency,
  formatChartAxisPercent,
} from './utils/chartFormatting';

// Format axis value
formatChartAxis(1234.56);           // "1.234,56"
formatChartAxisCurrency(1234.56);   // "1.234,56 €"
formatChartAxisPercent(0.35);       // "35,00 %"
```

## Recharts Integration

### Line Chart Example

```typescript
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import {
  rechartsAxisTickFormatter,
  rechartsTooltipFormatter,
} from './utils/chartFormatting';

<LineChart data={data}>
  <XAxis dataKey="month" />
  <YAxis tickFormatter={rechartsAxisTickFormatter} />
  <Tooltip formatter={rechartsTooltipFormatter} />
  <Legend />
  <Line dataKey="value" stroke="#8884d8" />
</LineChart>
```

### Bar Chart with Currency

```typescript
import {
  rechartsCurrencyAxisTickFormatter,
  rechartsCurrencyTooltipFormatter,
} from './utils/chartFormatting';

<BarChart data={data}>
  <YAxis tickFormatter={(v) => rechartsCurrencyAxisTickFormatter(v, '€')} />
  <Tooltip 
    formatter={(v, n, p) => rechartsCurrencyTooltipFormatter(v, n, p, '€')} 
  />
  <Bar dataKey="cost" fill="#8884d8" />
</BarChart>
```

### Pie Chart with Percentages

```typescript
import {
  rechartsPercentTooltipFormatter,
} from './utils/chartFormatting';

<PieChart>
  <Pie
    data={data}
    label={(entry) => germanFormatter.formatPercent(entry.value * 100, false)}
    dataKey="value"
  />
  <Tooltip formatter={rechartsPercentTooltipFormatter} />
</PieChart>
```

### Area Chart Example

```typescript
<AreaChart data={data}>
  <XAxis dataKey="year" />
  <YAxis tickFormatter={(v) => rechartsCurrencyAxisTickFormatter(v, '€')} />
  <Tooltip 
    formatter={(v, n, p) => rechartsCurrencyTooltipFormatter(v, n, p, '€')} 
  />
  <Area 
    type="monotone" 
    dataKey="savings" 
    stroke="#8884d8" 
    fill="#8884d8" 
  />
</AreaChart>
```

### Configuration Helper

```typescript
import { createRechartsConfig } from './utils/chartFormatting';

// Create pre-configured settings
const config = createRechartsConfig('currency', '€');

<LineChart data={data}>
  <YAxis tickFormatter={config.yAxis.tickFormatter} />
  <Tooltip formatter={config.tooltip.formatter} />
</LineChart>
```

## Chart.js Integration

### Basic Setup

```typescript
import {
  chartJsAxisTickCallback,
  chartJsTooltipCallback,
} from './utils/chartFormatting';

const chartConfig = {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
      label: 'Production',
      data: [450.5, 620.75, 890.25],
    }],
  },
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
import {
  chartJsCurrencyAxisTickCallback,
  chartJsCurrencyTooltipCallback,
} from './utils/chartFormatting';

const chartConfig = {
  options: {
    scales: {
      y: {
        ticks: {
          callback: (value) => chartJsCurrencyAxisTickCallback(value, '€'),
        },
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (context) => chartJsCurrencyTooltipCallback(context, '€'),
        },
      },
    },
  },
};
```

### Configuration Helper

```typescript
import { createChartJsConfig } from './utils/chartFormatting';

const config = createChartJsConfig('currency', '€');

const chartConfig = {
  type: 'bar',
  data: { /* ... */ },
  options: {
    ...config,
  },
};
```

## Plotly Integration

### Basic Configuration

```typescript
import {
  getPlotlyFormatConfig,
  getPlotlyHoverTemplate,
} from './utils/chartFormatting';

const plotlyConfig = getPlotlyFormatConfig();

const data = [{
  x: ['Jan', 'Feb', 'Mar'],
  y: [450.5, 620.75, 890.25],
  type: 'scatter',
  mode: 'lines+markers',
  hovertemplate: getPlotlyHoverTemplate('Production'),
}];

const layout = {
  yaxis: {
    tickformat: ',.2f',
    separators: ',.',
  },
};

Plotly.newPlot('chart', data, layout, plotlyConfig);
```

### Currency Chart

```typescript
import { getPlotlyCurrencyHoverTemplate } from './utils/chartFormatting';

const data = [{
  x: ['Module', 'Inverter', 'Installation'],
  y: [8500.50, 2300.75, 3200.25],
  type: 'bar',
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

### Percentage Chart

```typescript
import { getPlotlyPercentHoverTemplate } from './utils/chartFormatting';

const data = [{
  values: [35, 65],
  labels: ['Self-consumption', 'Feed-in'],
  type: 'pie',
  hovertemplate: getPlotlyPercentHoverTemplate('Share'),
}];
```

## Chart Export Formatting

### PNG/SVG Export

Formatting is automatically preserved when exporting to PNG or SVG:

```typescript
// Recharts - use recharts-to-png or similar
import { exportComponentAsPNG } from 'react-component-export-image';

const chartRef = useRef();

<LineChart ref={chartRef} data={data}>
  {/* Chart with formatted axes and tooltips */}
</LineChart>

<button onClick={() => exportComponentAsPNG(chartRef)}>
  Export as PNG
</button>
```

### PDF Export

```typescript
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

const exportChartToPDF = async (chartElement: HTMLElement) => {
  const canvas = await html2canvas(chartElement);
  const imgData = canvas.toDataURL('image/png');
  
  const pdf = new jsPDF();
  pdf.addImage(imgData, 'PNG', 10, 10, 190, 100);
  pdf.save('chart.pdf');
};
```

### Data Export (CSV/Excel)

```typescript
import { formatChartData } from './utils/chartFormatting';

// Format data array for export
const formattedData = formatChartData(
  [1234.56, 2345.67, 3456.78],
  'currency',
  '€'
);

// Export to CSV
const csvContent = data.map(row => 
  `${row.month},${germanFormatter.format(row.value)}`
).join('\n');

const blob = new Blob([csvContent], { type: 'text/csv' });
const url = URL.createObjectURL(blob);
```

## Examples

### Complete Solar Production Chart

```typescript
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  rechartsAxisTickFormatter,
  rechartsTooltipFormatter,
} from './utils/chartFormatting';

const SolarProductionChart: React.FC<{ data: any[] }> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis tickFormatter={rechartsAxisTickFormatter}>
          <Label 
            value="Production (kWh)" 
            angle={-90} 
            position="insideLeft" 
          />
        </YAxis>
        <Tooltip formatter={rechartsTooltipFormatter} />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="production" 
          stroke="#4CAF50" 
          strokeWidth={2}
        />
        <Line 
          type="monotone" 
          dataKey="consumption" 
          stroke="#FF9800" 
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

### Cost Breakdown Bar Chart

```typescript
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import {
  rechartsCurrencyAxisTickFormatter,
  rechartsCurrencyTooltipFormatter,
} from './utils/chartFormatting';

const CostBreakdownChart: React.FC<{ data: any[] }> = ({ data }) => {
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="category" />
        <YAxis tickFormatter={(v) => rechartsCurrencyAxisTickFormatter(v, '€')} />
        <Tooltip 
          formatter={(v, n, p) => rechartsCurrencyTooltipFormatter(v, n, p, '€')} 
        />
        <Bar dataKey="cost">
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};
```

### Efficiency Pie Chart

```typescript
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  rechartsPercentTooltipFormatter,
} from './utils/chartFormatting';
import { germanFormatter } from './utils/germanNumberFormatter';

const EfficiencyPieChart: React.FC<{ data: any[] }> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={true}
          label={(entry) => 
            `${entry.name}: ${germanFormatter.formatPercent(entry.value * 100, false)}`
          }
          outerRadius={120}
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip formatter={rechartsPercentTooltipFormatter} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
};
```

## Best Practices

### 1. Consistent Formatting

Always use the same formatting functions across all charts:

```typescript
// ✅ Good - Consistent
<YAxis tickFormatter={rechartsAxisTickFormatter} />
<Tooltip formatter={rechartsTooltipFormatter} />

// ❌ Bad - Inconsistent
<YAxis tickFormatter={(v) => v.toFixed(2)} />
<Tooltip formatter={(v) => `${v}`} />
```

### 2. Currency Symbol Placement

Place currency symbols after the number (German convention):

```typescript
// ✅ Good - German format
"1.234,56 €"

// ❌ Bad - English format
"€1,234.56"
```

### 3. Percentage Formatting

Use the `multiplyBy100` parameter correctly:

```typescript
// If value is already in percent (35)
germanFormatter.formatPercent(35, false);  // "35,00 %"

// If value is decimal (0.35)
germanFormatter.formatPercent(0.35 * 100, false);  // "35,00 %"
```

### 4. Axis Labels

Always add descriptive axis labels with units:

```typescript
<YAxis tickFormatter={rechartsAxisTickFormatter}>
  <Label 
    value="Production (kWh)" 
    angle={-90} 
    position="insideLeft" 
  />
</YAxis>
```

### 5. Tooltip Content

Provide context in tooltips:

```typescript
<Tooltip 
  formatter={rechartsTooltipFormatter}
  labelFormatter={(label) => `Month: ${label}`}
/>
```

### 6. Legend Formatting

Format legend labels for clarity:

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

### 7. Data Label Positioning

Position data labels to avoid overlap:

```typescript
<Bar dataKey="value">
  <LabelList 
    dataKey="value" 
    position="top"
    formatter={(value) => germanFormatter.format(value)}
  />
</Bar>
```

### 8. Responsive Design

Use ResponsiveContainer for all charts:

```typescript
<ResponsiveContainer width="100%" height={400}>
  <LineChart data={data}>
    {/* Chart content */}
  </LineChart>
</ResponsiveContainer>
```

### 9. Color Accessibility

Use accessible color combinations:

```typescript
const COLORS = {
  primary: '#4CAF50',    // Green - good contrast
  secondary: '#2196F3',  // Blue - good contrast
  warning: '#FF9800',    // Orange - good contrast
  error: '#F44336',      // Red - good contrast
};
```

### 10. Export Formatting

Ensure formatting is preserved in exports:

```typescript
// Before export, verify formatting
const verifyFormatting = (data: any[]) => {
  return data.map(item => ({
    ...item,
    formattedValue: germanFormatter.format(item.value),
  }));
};
```

## Testing

### Unit Tests

```typescript
import { germanFormatter } from './utils/germanNumberFormatter';

describe('Chart Formatting', () => {
  it('formats numbers correctly', () => {
    expect(germanFormatter.format(1234.56)).toBe('1.234,56');
  });

  it('formats currency correctly', () => {
    expect(germanFormatter.formatCurrency(1234.56, '€')).toBe('1.234,56 €');
  });

  it('formats percentages correctly', () => {
    expect(germanFormatter.formatPercent(35, false)).toBe('35,00 %');
  });
});
```

### Visual Testing

```typescript
// Test chart rendering with formatted values
import { render } from '@testing-library/react';
import { SolarProductionChart } from './SolarProductionChart';

test('renders chart with German formatting', () => {
  const data = [
    { month: 'Jan', production: 450.5 },
  ];

  const { container } = render(<SolarProductionChart data={data} />);
  
  // Check if formatted value appears in DOM
  expect(container.textContent).toContain('450,50');
});
```

## Troubleshooting

### Issue: Numbers not formatting

**Solution:** Ensure you're using the correct formatter:

```typescript
// Check import
import { rechartsAxisTickFormatter } from './utils/chartFormatting';

// Apply to axis
<YAxis tickFormatter={rechartsAxisTickFormatter} />
```

### Issue: Currency symbol in wrong position

**Solution:** Use German format (symbol after number):

```typescript
// Correct
germanFormatter.formatCurrency(1234.56, '€');  // "1.234,56 €"
```

### Issue: Tooltips showing wrong format

**Solution:** Use the correct tooltip formatter:

```typescript
<Tooltip formatter={rechartsTooltipFormatter} />
```

### Issue: Export loses formatting

**Solution:** Format data before export:

```typescript
const formattedData = data.map(row => ({
  ...row,
  value: germanFormatter.format(row.value),
}));
```

## Summary

✅ **All axis labels** formatted with German locale  
✅ **All tooltips** display German-formatted numbers  
✅ **All legends** show formatted values  
✅ **All data labels** use German formatting  
✅ **All exports** preserve German number format  

**Requirements 14.3 Compliance:** Complete ✓

For more examples, see `ChartFormattingDemo.tsx`.
