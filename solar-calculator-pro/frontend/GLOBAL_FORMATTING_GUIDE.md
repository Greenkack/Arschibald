# Global German Number Formatting Guide

## Overview

This guide describes the global German number formatting system that ensures all numbers throughout the application are displayed with German locale formatting:
- **Dot (.)** as thousand separator
- **Comma (,)** as decimal separator
- **Exactly 2 decimal places** for all decimal numbers

## Requirements Compliance

### ✅ Requirement 14.1
**THE Frontend Application SHALL format all numbers with German locale (de-DE) using dot (.) as thousand separator and comma (,) as decimal separator**

All formatting utilities use the German locale (de-DE) consistently.

### ✅ Requirement 14.2
**THE Frontend Application SHALL display exactly 2 decimal places for all decimal numbers throughout the application**

All formatters default to 2 decimal places (configurable where needed).

### ✅ Requirement 14.3
**THE Frontend Application SHALL apply German number formatting to all input fields, display fields, calculations, results, charts, tables, and reports**

Comprehensive utilities provided for all use cases.

---

## Table of Contents

1. [Global Formatting Provider](#global-formatting-provider)
2. [Formatted Display Components](#formatted-display-components)
3. [Input Components](#input-components)
4. [Chart Formatting](#chart-formatting)
5. [Table Formatting](#table-formatting)
6. [Export Formatting](#export-formatting)
7. [Integration Examples](#integration-examples)
8. [API Reference](#api-reference)

---

## Global Formatting Provider

### Setup

Wrap your entire application with the `GlobalFormattingProvider`:

```tsx
import { GlobalFormattingProvider } from './providers/GlobalFormattingProvider';

function App() {
  return (
    <GlobalFormattingProvider locale="de-DE" defaultDecimalPlaces={2}>
      <YourApp />
    </GlobalFormattingProvider>
  );
}
```

### Using the Hook

Access formatting functions anywhere in your app:

```tsx
import { useGlobalFormatting } from './providers/GlobalFormattingProvider';

function MyComponent() {
  const { formatNumber, formatCurrency, formatPercent } = useGlobalFormatting();
  
  return (
    <div>
      <p>{formatNumber(1234.56)}</p>        {/* 1.234,56 */}
      <p>{formatCurrency(15000, '€')}</p>   {/* 15.000,00 € */}
      <p>{formatPercent(0.18, true)}</p>    {/* 18,00 % */}
    </div>
  );
}
```

---

## Formatted Display Components

### FormattedNumber

Display a number with German formatting:

```tsx
import { FormattedNumber } from './components/FormattedDisplay';

<FormattedNumber value={1234.56} />
// Displays: 1.234,56

<FormattedNumber value={1234.56} decimalPlaces={3} />
// Displays: 1.234,560
```

### FormattedCurrency

Display a currency value:

```tsx
import { FormattedCurrency } from './components/FormattedDisplay';

<FormattedCurrency value={15000} symbol="€" />
// Displays: 15.000,00 €

<FormattedCurrency value={15000} symbol="$" position="prefix" />
// Displays: $ 15.000,00
```

### FormattedPercent

Display a percentage:

```tsx
import { FormattedPercent } from './components/FormattedDisplay';

<FormattedPercent value={0.18} multiplyBy100={true} />
// Displays: 18,00 %

<FormattedPercent value={18} multiplyBy100={false} />
// Displays: 18,00 %
```

### FormattedLabel

Display a label with a formatted value:

```tsx
import { FormattedLabel } from './components/FormattedDisplay';

<FormattedLabel label="System Size" value={10.5} type="number" />
// Displays: System Size: 10,50

<FormattedLabel label="Total Cost" value={18500} type="currency" symbol="€" />
// Displays: Total Cost: 18.500,00 €
```

### FormattedTableCell

Display a formatted value in a table cell:

```tsx
import { FormattedTableCell } from './components/FormattedDisplay';

<table>
  <tbody>
    <tr>
      <FormattedTableCell value={1234.56} type="number" />
      <FormattedTableCell value={15000} type="currency" symbol="€" />
      <FormattedTableCell value={0.18} type="percent" />
    </tr>
  </tbody>
</table>
```

### FormattedCardValue

Display a formatted value in a card layout:

```tsx
import { FormattedCardValue } from './components/FormattedDisplay';

<FormattedCardValue
  title="System Size"
  value={10.5}
  type="number"
  subtitle="kWp"
/>

<FormattedCardValue
  title="Total Cost"
  value={18500}
  type="currency"
  symbol="€"
/>
```

---

## Input Components

All input components from Task 216 are integrated:

### GermanNumberInput

```tsx
import { GermanNumberInput } from './components';

<GermanNumberInput
  value={value}
  onChange={setValue}
  label="Amount"
  min={0}
  max={10000}
  decimalPlaces={2}
/>
```

### GermanCurrencyInput

```tsx
import { GermanCurrencyInput } from './components';

<GermanCurrencyInput
  value={value}
  onChange={setValue}
  label="Price"
  currencySymbol="€"
/>
```

### GermanPercentInput

```tsx
import { GermanPercentInput } from './components';

<GermanPercentInput
  value={value}
  onChange={setValue}
  label="Percentage"
  multiplyBy100={true}
/>
```

### GermanSlider

```tsx
import { GermanSlider } from './components';

<GermanSlider
  value={value}
  onChange={setValue}
  label="Value"
  min={0}
  max={10000}
  formatType="currency"
  showValue={true}
/>
```

---

## Chart Formatting

### Recharts Integration

```tsx
import {
  rechartsTooltipFormatter,
  rechartsAxisTickFormatter,
  createRechartsConfig,
} from './utils/chartFormatting';

// Simple usage
<LineChart data={data}>
  <XAxis dataKey="name" />
  <YAxis tickFormatter={rechartsAxisTickFormatter} />
  <Tooltip formatter={rechartsTooltipFormatter} />
  <Line dataKey="value" />
</LineChart>

// With configuration
const config = createRechartsConfig('currency', '€');
<LineChart data={data}>
  <YAxis tickFormatter={config.yAxis.tickFormatter} />
  <Tooltip formatter={config.tooltip.formatter} />
</LineChart>
```

### Chart.js Integration

```tsx
import {
  chartJsTooltipCallback,
  chartJsAxisTickCallback,
  createChartJsConfig,
} from './utils/chartFormatting';

const config = createChartJsConfig('currency', '€');

const chartOptions = {
  plugins: {
    tooltip: {
      callbacks: config.plugins.tooltip.callbacks,
    },
  },
  scales: {
    y: {
      ticks: {
        callback: config.scales.y.ticks.callback,
      },
    },
  },
};
```

### Plotly Integration

```tsx
import {
  getPlotlyFormatConfig,
  getPlotlyHoverTemplate,
} from './utils/chartFormatting';

const plotlyConfig = getPlotlyFormatConfig();

const data = [{
  x: [1, 2, 3],
  y: [1000, 2000, 3000],
  hovertemplate: getPlotlyHoverTemplate('Value'),
}];

const layout = {
  ...plotlyConfig,
};
```

---

## Table Formatting

### PrimeReact DataTable

```tsx
import {
  primeReactNumberBodyTemplate,
  primeReactCurrencyBodyTemplate,
  createPrimeReactColumnConfig,
} from './utils/tableFormatting';

<DataTable value={data}>
  <Column field="name" header="Name" />
  <Column body={primeReactNumberBodyTemplate} field="value" header="Value" />
  <Column body={primeReactCurrencyBodyTemplate('€')} field="price" header="Price" />
</DataTable>

// Or use configuration
const columns = [
  createPrimeReactColumnConfig('value', 'Value', 'number'),
  createPrimeReactColumnConfig('price', 'Price', 'currency', '€'),
  createPrimeReactColumnConfig('efficiency', 'Efficiency', 'percent'),
];
```

### AG Grid

```tsx
import {
  agGridNumberFormatter,
  agGridCurrencyFormatter,
  createAgGridColumnDef,
} from './utils/tableFormatting';

const columnDefs = [
  { field: 'name', headerName: 'Name' },
  { field: 'value', headerName: 'Value', valueFormatter: agGridNumberFormatter },
  { field: 'price', headerName: 'Price', valueFormatter: agGridCurrencyFormatter('€') },
];

// Or use configuration
const columnDefs = [
  createAgGridColumnDef('value', 'Value', 'number'),
  createAgGridColumnDef('price', 'Price', 'currency', '€'),
];
```

### React Table (TanStack Table)

```tsx
import {
  reactTableNumberCell,
  reactTableCurrencyCell,
  createReactTableColumnDef,
} from './utils/tableFormatting';

const columns = [
  columnHelper.accessor('name', { header: 'Name' }),
  columnHelper.accessor('value', { header: 'Value', cell: reactTableNumberCell }),
  columnHelper.accessor('price', { header: 'Price', cell: reactTableCurrencyCell('€') }),
];

// Or use configuration
const columns = [
  createReactTableColumnDef('value', 'Value', 'number'),
  createReactTableColumnDef('price', 'Price', 'currency', '€'),
];
```

---

## Export Formatting

### CSV Export

```tsx
import {
  formatDataForCSV,
  downloadFormattedCSV,
} from './utils/exportFormatting';

const data = [
  { name: 'Product A', price: 1234.56, quantity: 10 },
  { name: 'Product B', price: 2345.67, quantity: 20 },
];

const numericFields = ['price', 'quantity'];
const fieldTypes = { price: 'currency', quantity: 'number' };

// Format data
const formattedData = formatDataForCSV(data, numericFields, fieldTypes, '€');

// Or download directly
downloadFormattedCSV(
  data,
  ['name', 'price', 'quantity'],
  numericFields,
  'export.csv',
  fieldTypes,
  '€'
);
```

### Excel Export

```tsx
import { formatDataForExcel } from './utils/exportFormatting';

const formattedData = formatDataForExcel(data, numericFields, fieldTypes, '€');
// Use with your Excel export library (e.g., xlsx)
```

### PDF Export

```tsx
import { formatDataForPDF } from './utils/exportFormatting';

const formattedData = formatDataForPDF(data, numericFields, fieldTypes, '€');
// Use with your PDF generation library
```

### Report Formatting

```tsx
import {
  formatReportData,
  formatSummaryStatistics,
} from './utils/exportFormatting';

const report = {
  title: 'Solar Calculator Report',
  systemSize: 10.5,
  totalCost: 18500,
  annualProduction: 12000,
};

const formattedReport = formatReportData(
  report,
  ['systemSize', 'totalCost', 'annualProduction'],
  { totalCost: 'currency', systemSize: 'number', annualProduction: 'number' },
  '€'
);
```

---

## Integration Examples

### Solar Calculator

```tsx
function SolarCalculatorResults({ results }) {
  return (
    <div className="results">
      <FormattedCardValue
        title="System Size"
        value={results.systemSize}
        type="number"
        subtitle="kWp"
      />
      
      <FormattedCardValue
        title="Total Cost"
        value={results.totalCost}
        type="currency"
        symbol="€"
      />
      
      <FormattedCardValue
        title="Annual Production"
        value={results.annualProduction}
        type="number"
        subtitle="kWh/year"
      />
      
      <FormattedCardValue
        title="Self Consumption"
        value={results.selfConsumption}
        type="percent"
      />
    </div>
  );
}
```

### Price Matrix

```tsx
function PriceMatrixTable({ products }) {
  return (
    <DataTable value={products}>
      <Column field="name" header="Product" />
      <Column
        field="basePrice"
        header="Base Price"
        body={primeReactCurrencyBodyTemplate('€')}
      />
      <Column
        field="discount"
        header="Discount"
        body={primeReactPercentBodyTemplate}
      />
      <Column
        field="finalPrice"
        header="Final Price"
        body={primeReactCurrencyBodyTemplate('€')}
      />
    </DataTable>
  );
}
```

### Heat Pump Calculator

```tsx
function HeatPumpResults({ results }) {
  const { formatNumber, formatCurrency } = useGlobalFormatting();
  
  return (
    <div className="results">
      <FormattedLabel
        label="Heating Power"
        value={results.heatingPower}
        type="number"
      />
      
      <FormattedLabel
        label="Annual Cost"
        value={results.annualCost}
        type="currency"
        symbol="€"
      />
      
      <FormattedLabel
        label="COP"
        value={results.cop}
        type="number"
      />
    </div>
  );
}
```

### Charts

```tsx
function ProductionChart({ data }) {
  const config = createRechartsConfig('number');
  
  return (
    <LineChart data={data}>
      <XAxis dataKey="month" />
      <YAxis tickFormatter={config.yAxis.tickFormatter} />
      <Tooltip formatter={config.tooltip.formatter} />
      <Line dataKey="production" stroke="#8884d8" />
    </LineChart>
  );
}
```

---

## API Reference

### GlobalFormattingProvider

**Props:**
- `locale?: string` - Locale to use (default: 'de-DE')
- `defaultDecimalPlaces?: number` - Default decimal places (default: 2)
- `children: ReactNode` - Child components

### useGlobalFormatting Hook

**Returns:**
```typescript
{
  formatNumber: (value: number, decimalPlaces?: number) => string;
  formatCurrency: (value: number, symbol?: string, position?: 'prefix' | 'suffix') => string;
  formatPercent: (value: number, multiplyBy100?: boolean) => string;
  parseNumber: (value: string) => number;
  validateNumber: (value: string) => boolean;
  locale: string;
  decimalSeparator: string;
  thousandSeparator: string;
  defaultDecimalPlaces: number;
}
```

### Formatted Display Components

All components accept:
- `value: number` - The number to format
- `className?: string` - Optional CSS class
- `style?: React.CSSProperties` - Optional inline styles

Type-specific props:
- `type?: 'number' | 'currency' | 'percent'` - Format type
- `symbol?: string` - Currency symbol (default: '€')
- `decimalPlaces?: number` - Number of decimal places
- `multiplyBy100?: boolean` - For percentages (default: true)

---

## Best Practices

### 1. Always Use the Provider

Wrap your entire app with `GlobalFormattingProvider` at the root level.

### 2. Use Formatted Components

Prefer using `FormattedNumber`, `FormattedCurrency`, etc. over manual formatting.

### 3. Consistent Decimal Places

Stick to 2 decimal places unless there's a specific reason to use more.

### 4. Chart Integration

Always use the provided chart formatters to ensure consistency.

### 5. Table Integration

Use the table formatting utilities for all numeric columns.

### 6. Export Formatting

Always format data before exporting to maintain consistency.

### 7. Input Components

Use the German input components for all numeric inputs.

---

## Testing

All formatting utilities are tested. See:
- `solar-calculator-pro/frontend/src/test/GermanNumberInput.test.tsx`
- Additional tests for each utility module

---

## Browser Support

- Chrome/Edge: ✅
- Firefox: ✅
- Safari: ✅
- Mobile Browsers: ✅

---

## Dependencies

- React 18+
- PrimeReact 10+ (for input components)
- TypeScript 5+

---

## Summary

The global German number formatting system provides:

✅ **Consistent formatting** across the entire application
✅ **Easy integration** with all UI components
✅ **Chart support** for Recharts, Chart.js, and Plotly
✅ **Table support** for PrimeReact, AG Grid, and React Table
✅ **Export support** for CSV, Excel, and PDF
✅ **Input components** with bidirectional conversion
✅ **Requirements compliance** (14.1, 14.2, 14.3)

All numbers are displayed with:
- Dot (.) as thousand separator
- Comma (,) as decimal separator
- Exactly 2 decimal places

🎉 **Ready for production use!**
