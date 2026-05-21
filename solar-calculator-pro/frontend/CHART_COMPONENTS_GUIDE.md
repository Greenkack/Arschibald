# Chart Components Guide

Complete guide for using chart components in the Solar Calculator Pro application.

## Overview

The chart components provide reusable, German-formatted visualizations for energy production, cost analysis, consumption breakdown, and savings over time. All components support export functionality and are built with Recharts.

## Requirements

- **Requirement 7.4**: Chart components for data visualization

## Components

### 1. LineChart

Line chart component for visualizing trends over time, such as energy production.

#### Props

```typescript
interface LineChartProps {
  data: LineChartData[];              // Array of data points
  lines: Array<{                      // Line configurations
    dataKey: string;                  // Key in data object
    name: string;                     // Display name
    color: string;                    // Line color (hex)
    strokeWidth?: number;             // Line width (default: 2)
  }>;
  xAxisKey?: string;                  // X-axis data key (default: 'name')
  title?: string;                     // Chart title
  height?: number;                    // Chart height in pixels (default: 300)
  formatType?: 'number' | 'currency' | 'percent';  // Number format type
  currencySymbol?: string;            // Currency symbol (default: '€')
  showGrid?: boolean;                 // Show grid lines (default: true)
  showLegend?: boolean;               // Show legend (default: true)
  className?: string;                 // Additional CSS classes
}
```

#### Example

```tsx
import { LineChart } from '../components/charts';

const energyData = [
  { name: 'Jan', production: 2400, consumption: 2100 },
  { name: 'Feb', production: 3200, consumption: 2300 },
  // ... more data
];

<LineChart
  data={energyData}
  lines={[
    { dataKey: 'production', name: 'Produktion (kWh)', color: '#00C49F' },
    { dataKey: 'consumption', name: 'Verbrauch (kWh)', color: '#FF8042' },
  ]}
  title="Monatliche Energieproduktion"
  height={400}
  formatType="number"
/>
```

### 2. BarChart

Bar chart component for comparing values, such as cost analysis.

#### Props

```typescript
interface BarChartProps {
  data: BarChartData[];               // Array of data points
  bars: Array<{                       // Bar configurations
    dataKey: string;                  // Key in data object
    name: string;                     // Display name
    color: string;                    // Bar color (hex)
  }>;
  xAxisKey?: string;                  // X-axis data key (default: 'name')
  title?: string;                     // Chart title
  height?: number;                    // Chart height in pixels (default: 300)
  formatType?: 'number' | 'currency' | 'percent';  // Number format type
  currencySymbol?: string;            // Currency symbol (default: '€')
  showGrid?: boolean;                 // Show grid lines (default: true)
  showLegend?: boolean;               // Show legend (default: true)
  layout?: 'horizontal' | 'vertical'; // Bar orientation (default: 'horizontal')
  stacked?: boolean;                  // Stack bars (default: false)
  className?: string;                 // Additional CSS classes
}
```

#### Example

```tsx
import { BarChart } from '../components/charts';

const costData = [
  { name: 'PV-Module', cost: 12500 },
  { name: 'Wechselrichter', cost: 3200 },
  { name: 'Batteriespeicher', cost: 8500 },
];

<BarChart
  data={costData}
  bars={[
    { dataKey: 'cost', name: 'Kosten', color: '#0088FE' },
  ]}
  title="Kostenaufschlüsselung"
  height={400}
  formatType="currency"
  currencySymbol="€"
/>
```

### 3. PieChart

Pie chart component for showing proportions, such as consumption breakdown.

#### Props

```typescript
interface PieChartProps {
  data: PieChartData[];               // Array of data points
  title?: string;                     // Chart title
  height?: number;                    // Chart height in pixels (default: 300)
  formatType?: 'number' | 'currency' | 'percent';  // Number format type
  currencySymbol?: string;            // Currency symbol (default: '€')
  showLegend?: boolean;               // Show legend (default: true)
  showLabels?: boolean;               // Show labels on slices (default: true)
  innerRadius?: number;               // Inner radius for donut chart (default: 0)
  outerRadius?: number;               // Outer radius (default: 80)
  colors?: string[];                  // Custom color palette
  className?: string;                 // Additional CSS classes
}
```

#### Example

```tsx
import { PieChart } from '../components/charts';

const consumptionData = [
  { name: 'Eigenverbrauch', value: 6500, color: '#00C49F' },
  { name: 'Netzeinspeisung', value: 4200, color: '#0088FE' },
  { name: 'Netzbezug', value: 1800, color: '#FFBB28' },
];

<PieChart
  data={consumptionData}
  title="Energieverbrauch"
  height={400}
  formatType="number"
  showLabels={true}
/>
```

### 4. AreaChart

Area chart component for showing cumulative values over time, such as savings.

#### Props

```typescript
interface AreaChartProps {
  data: AreaChartData[];              // Array of data points
  areas: Array<{                      // Area configurations
    dataKey: string;                  // Key in data object
    name: string;                     // Display name
    color: string;                    // Area color (hex)
    fillOpacity?: number;             // Fill opacity (default: 0.6)
  }>;
  xAxisKey?: string;                  // X-axis data key (default: 'name')
  title?: string;                     // Chart title
  height?: number;                    // Chart height in pixels (default: 300)
  formatType?: 'number' | 'currency' | 'percent';  // Number format type
  currencySymbol?: string;            // Currency symbol (default: '€')
  showGrid?: boolean;                 // Show grid lines (default: true)
  showLegend?: boolean;               // Show legend (default: true)
  stacked?: boolean;                  // Stack areas (default: false)
  className?: string;                 // Additional CSS classes
}
```

#### Example

```tsx
import { AreaChart } from '../components/charts';

const savingsData = [
  { name: 'Jahr 1', savings: 1200, cumulative: 1200 },
  { name: 'Jahr 2', savings: 1250, cumulative: 2450 },
  { name: 'Jahr 3', savings: 1300, cumulative: 3750 },
];

<AreaChart
  data={savingsData}
  areas={[
    { dataKey: 'savings', name: 'Jährlich', color: '#00C49F' },
    { dataKey: 'cumulative', name: 'Kumuliert', color: '#0088FE' },
  ]}
  title="Einsparungen über Zeit"
  height={400}
  formatType="currency"
  currencySymbol="€"
/>
```

## Export Functionality

All charts can be exported to various formats using the export utilities.

### Export Chart as Image/PDF

```tsx
import { useRef } from 'react';
import { exportChart } from '../utils/chartExport';

const MyComponent = () => {
  const chartRef = useRef<HTMLDivElement>(null);

  const handleExport = async () => {
    if (!chartRef.current) return;
    
    await exportChart(chartRef.current, {
      filename: 'my-chart',
      format: 'png', // 'png', 'svg', or 'pdf'
      quality: 1.0,
      backgroundColor: '#ffffff',
    });
  };

  return (
    <div>
      <button onClick={handleExport}>Export Chart</button>
      <div ref={chartRef}>
        <LineChart data={data} lines={lines} />
      </div>
    </div>
  );
};
```

### Export Chart Data

```tsx
import { exportChartDataAsCSV, exportChartDataAsJSON } from '../utils/chartExport';

// Export as CSV
exportChartDataAsCSV(data, 'chart-data');

// Export as JSON
exportChartDataAsJSON(data, 'chart-data');
```

## German Number Formatting

All charts automatically use German number formatting:
- Thousands separator: `.` (dot)
- Decimal separator: `,` (comma)
- Currency format: `1.234,56 €`
- Percent format: `12,34 %`

The formatting is applied to:
- Y-axis labels
- Tooltip values
- Legend values
- Data labels

## Styling

### Custom Colors

```tsx
// Define custom color palette
const customColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'];

<PieChart
  data={data}
  colors={customColors}
/>
```

### Custom CSS

```tsx
<LineChart
  data={data}
  lines={lines}
  className="my-custom-chart"
/>
```

```css
.my-custom-chart {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
}

.my-custom-chart .chart-title {
  color: #333;
  font-size: 1.5rem;
}
```

## Responsive Design

All charts are responsive by default using `ResponsiveContainer` from Recharts. They will automatically adjust to their container's width.

```tsx
<div style={{ width: '100%', maxWidth: '800px' }}>
  <LineChart data={data} lines={lines} height={400} />
</div>
```

## Best Practices

### 1. Data Preparation

Ensure data is in the correct format:

```tsx
// Good
const data = [
  { name: 'Jan', value: 100 },
  { name: 'Feb', value: 200 },
];

// Bad - missing required fields
const data = [
  { value: 100 },
  { value: 200 },
];
```

### 2. Color Selection

Use accessible color combinations:

```tsx
// Good - high contrast
const colors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

// Avoid - low contrast
const colors = ['#EEEEEE', '#F0F0F0', '#F5F5F5'];
```

### 3. Performance

For large datasets, consider:
- Limiting data points displayed
- Using data aggregation
- Implementing pagination or filtering

```tsx
// Limit to last 12 months
const recentData = allData.slice(-12);

<LineChart data={recentData} lines={lines} />
```

### 4. Accessibility

- Always provide meaningful titles
- Use descriptive names for data series
- Ensure sufficient color contrast
- Consider providing data tables as alternatives

```tsx
<LineChart
  data={data}
  lines={[
    { dataKey: 'production', name: 'Energieproduktion in kWh', color: '#00C49F' },
  ]}
  title="Monatliche Energieproduktion 2024"
/>
```

## Common Use Cases

### Energy Production Dashboard

```tsx
<div className="dashboard">
  <LineChart
    data={monthlyData}
    lines={[
      { dataKey: 'production', name: 'Produktion', color: '#00C49F' },
      { dataKey: 'consumption', name: 'Verbrauch', color: '#FF8042' },
    ]}
    title="Energiebilanz"
    formatType="number"
  />
  
  <PieChart
    data={distributionData}
    title="Energieverteilung"
    formatType="percent"
  />
</div>
```

### Cost Analysis

```tsx
<BarChart
  data={costBreakdown}
  bars={[
    { dataKey: 'cost', name: 'Kosten', color: '#0088FE' },
  ]}
  title="Investitionskosten"
  formatType="currency"
  layout="horizontal"
/>
```

### ROI Visualization

```tsx
<AreaChart
  data={roiData}
  areas={[
    { dataKey: 'investment', name: 'Investition', color: '#FF8042' },
    { dataKey: 'savings', name: 'Einsparungen', color: '#00C49F' },
  ]}
  title="Return on Investment"
  formatType="currency"
  stacked={false}
/>
```

## Troubleshooting

### Chart Not Rendering

1. Check that data is not empty
2. Verify data structure matches expected format
3. Ensure container has defined dimensions

```tsx
// Add container dimensions
<div style={{ width: '100%', height: '400px' }}>
  <LineChart data={data} lines={lines} />
</div>
```

### Export Not Working

1. Ensure chart ref is properly attached
2. Check browser console for errors
3. Verify export dependencies are installed

```bash
npm install html2canvas jspdf
```

### Formatting Issues

1. Verify `formatType` prop is set correctly
2. Check `currencySymbol` for currency formatting
3. Ensure data values are numbers, not strings

```tsx
// Convert strings to numbers if needed
const data = rawData.map(item => ({
  ...item,
  value: parseFloat(item.value),
}));
```

## Dependencies

- `recharts`: ^2.10.3
- `html2canvas`: ^1.4.1
- `jspdf`: ^2.5.1

## Related Documentation

- [German Number Formatting Guide](./GERMAN_INPUT_QUICK_REFERENCE.md)
- [Chart Formatting Utilities](../src/utils/chartFormatting.ts)
- [Export Utilities](../src/utils/chartExport.ts)

## Support

For issues or questions:
1. Check the demo file: `src/examples/ChartComponentsDemo.tsx`
2. Review the component source code
3. Consult the Recharts documentation: https://recharts.org/
