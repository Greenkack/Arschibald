# Chart Components Quick Reference

Quick reference for chart components in Solar Calculator Pro.

## Import

```tsx
import { LineChart, BarChart, PieChart, AreaChart } from '../components/charts';
import { exportChart, exportChartDataAsCSV } from '../utils/chartExport';
```

## Line Chart

```tsx
<LineChart
  data={[{ name: 'Jan', value: 100 }, ...]}
  lines={[
    { dataKey: 'value', name: 'Label', color: '#00C49F' }
  ]}
  formatType="number" // or "currency", "percent"
/>
```

## Bar Chart

```tsx
<BarChart
  data={[{ name: 'Item', cost: 1000 }, ...]}
  bars={[
    { dataKey: 'cost', name: 'Kosten', color: '#0088FE' }
  ]}
  formatType="currency"
  currencySymbol="€"
/>
```

## Pie Chart

```tsx
<PieChart
  data={[
    { name: 'Category', value: 100, color: '#00C49F' },
    ...
  ]}
  showLabels={true}
  formatType="number"
/>
```

## Area Chart

```tsx
<AreaChart
  data={[{ name: 'Year 1', savings: 1200 }, ...]}
  areas={[
    { dataKey: 'savings', name: 'Einsparungen', color: '#00C49F' }
  ]}
  formatType="currency"
/>
```

## Export Chart

```tsx
const chartRef = useRef<HTMLDivElement>(null);

<div ref={chartRef}>
  <LineChart data={data} lines={lines} />
</div>

<button onClick={() => exportChart(chartRef.current, {
  filename: 'chart',
  format: 'png' // or 'svg', 'pdf'
})}>
  Export
</button>
```

## Export Data

```tsx
// CSV
exportChartDataAsCSV(data, 'filename');

// JSON
exportChartDataAsJSON(data, 'filename');
```

## Format Types

- `number`: 1.234,56
- `currency`: 1.234,56 €
- `percent`: 12,34 %

## Common Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | Array | required | Chart data |
| `title` | string | - | Chart title |
| `height` | number | 300 | Chart height (px) |
| `formatType` | string | 'number' | Number format |
| `showGrid` | boolean | true | Show grid lines |
| `showLegend` | boolean | true | Show legend |
| `className` | string | '' | CSS classes |

## Color Palette

```tsx
const colors = [
  '#0088FE', // Blue
  '#00C49F', // Green
  '#FFBB28', // Yellow
  '#FF8042', // Orange
  '#8884D8', // Purple
  '#82CA9D', // Light Green
];
```

## Responsive Container

All charts are responsive by default. Set container width:

```tsx
<div style={{ width: '100%', maxWidth: '800px' }}>
  <LineChart data={data} lines={lines} />
</div>
```

## Requirements

**Requirement 7.4**: Chart components for data visualization with German formatting and export functionality.
