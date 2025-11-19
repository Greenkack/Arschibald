# Global German Number Formatting - Quick Reference

## Setup (One Time)

```tsx
// In your App.tsx or main entry point
import { GlobalFormattingProvider } from './providers';

function App() {
  return (
    <GlobalFormattingProvider locale="de-DE" defaultDecimalPlaces={2}>
      <YourApp />
    </GlobalFormattingProvider>
  );
}
```

## Display Components

```tsx
import {
  FormattedNumber,
  FormattedCurrency,
  FormattedPercent,
  FormattedLabel,
  FormattedTableCell,
  FormattedCardValue,
} from './components';

// Number: 1.234,56
<FormattedNumber value={1234.56} />

// Currency: 15.000,00 €
<FormattedCurrency value={15000} symbol="€" />

// Percent: 18,00 %
<FormattedPercent value={0.18} multiplyBy100={true} />

// Label: System Size: 10,50
<FormattedLabel label="System Size" value={10.5} type="number" />

// Table Cell
<FormattedTableCell value={1234.56} type="currency" symbol="€" />

// Card Value
<FormattedCardValue
  title="Total Cost"
  value={18500}
  type="currency"
  symbol="€"
/>
```

## Input Components

```tsx
import {
  GermanNumberInput,
  GermanCurrencyInput,
  GermanPercentInput,
  GermanSlider,
} from './components';

<GermanNumberInput value={value} onChange={setValue} label="Amount" />
<GermanCurrencyInput value={value} onChange={setValue} label="Price" />
<GermanPercentInput value={value} onChange={setValue} label="Percent" />
<GermanSlider value={value} onChange={setValue} formatType="currency" />
```

## Direct Formatting

```tsx
import { useGlobalFormatting } from './providers';

const { formatNumber, formatCurrency, formatPercent } = useGlobalFormatting();

formatNumber(1234.56)        // → "1.234,56"
formatCurrency(15000, '€')   // → "15.000,00 €"
formatPercent(0.18, true)    // → "18,00 %"
```

## Charts

```tsx
import { createRechartsConfig } from './utils/chartFormatting';

const config = createRechartsConfig('currency', '€');

<LineChart data={data}>
  <YAxis tickFormatter={config.yAxis.tickFormatter} />
  <Tooltip formatter={config.tooltip.formatter} />
</LineChart>
```

## Tables

```tsx
import { createPrimeReactColumnConfig } from './utils/tableFormatting';

<DataTable value={data}>
  <Column {...createPrimeReactColumnConfig('price', 'Price', 'currency', '€')} />
  <Column {...createPrimeReactColumnConfig('quantity', 'Quantity', 'number')} />
</DataTable>
```

## Exports

```tsx
import { downloadFormattedCSV } from './utils/exportFormatting';

downloadFormattedCSV(
  data,
  ['name', 'price', 'quantity'],
  ['price', 'quantity'],
  'export.csv',
  { price: 'currency', quantity: 'number' },
  '€'
);
```

## Format Types

- `'number'` - Standard number: 1.234,56
- `'currency'` - Currency: 1.234,56 €
- `'percent'` - Percentage: 12,34 %

## Common Patterns

### Solar Calculator Results
```tsx
<FormattedCardValue title="System Size" value={10.5} type="number" subtitle="kWp" />
<FormattedCardValue title="Total Cost" value={18500} type="currency" symbol="€" />
<FormattedCardValue title="Efficiency" value={0.21} type="percent" />
```

### Price Matrix Table
```tsx
<DataTable value={products}>
  <Column field="name" header="Product" />
  <Column {...createPrimeReactColumnConfig('basePrice', 'Base Price', 'currency', '€')} />
  <Column {...createPrimeReactColumnConfig('discount', 'Discount', 'percent')} />
</DataTable>
```

### Heat Pump Display
```tsx
<FormattedLabel label="Heating Power" value={8.5} type="number" />
<FormattedLabel label="Annual Cost" value={1200} type="currency" symbol="€" />
<FormattedLabel label="COP" value={4.2} type="number" />
```

## Requirements

✅ **14.1** - German locale (de-DE) with dot (.) as thousand separator and comma (,) as decimal separator
✅ **14.2** - Exactly 2 decimal places for all decimal numbers
✅ **14.3** - Applied to all input fields, displays, calculations, charts, tables, and reports

## Full Documentation

See `GLOBAL_FORMATTING_GUIDE.md` for complete documentation.
