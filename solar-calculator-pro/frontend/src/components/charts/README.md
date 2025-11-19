# Chart Components

Reusable chart components for Solar Calculator Pro with German number formatting and export functionality.

## Components

### LineChart
Energy production and trend visualization.

```tsx
import { LineChart } from './charts';

<LineChart
  data={data}
  lines={[
    { dataKey: 'value', name: 'Label', color: '#00C49F' }
  ]}
/>
```

### BarChart
Cost analysis and comparison visualization.

```tsx
import { BarChart } from './charts';

<BarChart
  data={data}
  bars={[
    { dataKey: 'cost', name: 'Kosten', color: '#0088FE' }
  ]}
  formatType="currency"
/>
```

### PieChart
Consumption breakdown and proportion visualization.

```tsx
import { PieChart } from './charts';

<PieChart
  data={[
    { name: 'Category', value: 100, color: '#00C49F' }
  ]}
/>
```

### AreaChart
Savings over time and cumulative visualization.

```tsx
import { AreaChart } from './charts';

<AreaChart
  data={data}
  areas={[
    { dataKey: 'savings', name: 'Einsparungen', color: '#00C49F' }
  ]}
  formatType="currency"
/>
```

## Features

- ✅ German number formatting (1.234,56)
- ✅ Currency formatting (1.234,56 €)
- ✅ Percent formatting (12,34 %)
- ✅ Responsive design
- ✅ Customizable colors
- ✅ Grid and legend controls
- ✅ Multiple data series
- ✅ TypeScript support

## Export

All charts can be exported using the export utilities:

```tsx
import { exportChart } from '../../utils/chartExport';

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

## Documentation

- **Full Guide**: `/frontend/CHART_COMPONENTS_GUIDE.md`
- **Quick Reference**: `/frontend/CHART_COMPONENTS_QUICK_REFERENCE.md`
- **Demo**: `/frontend/src/examples/ChartComponentsDemo.tsx`

## Requirements

**Requirement 7.4**: Chart components for data visualization
