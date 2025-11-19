# German Input Components - Quick Reference

## Import

```tsx
import {
  GermanNumberInput,
  GermanCurrencyInput,
  GermanPercentInput,
  GermanSlider
} from './components';
import './styles/germanInputComponents.css';
```

## GermanNumberInput

```tsx
<GermanNumberInput
  value={1234.56}
  onChange={(val) => setValue(val)}
  label="Betrag"
  min={0}
  max={10000}
  decimalPlaces={2}
  placeholder="Wert eingeben"
  disabled={false}
  showError={true}
  onValidationError={(error) => console.error(error)}
/>
```

**Display**: `1.234,56`  
**Stored**: `1234.56`

## GermanCurrencyInput

```tsx
<GermanCurrencyInput
  value={5000}
  onChange={(val) => setPrice(val)}
  label="Preis"
  currencySymbol="€"
  symbolPosition="suffix"
  min={0}
  max={100000}
/>
```

**Display**: `5.000,00 €`  
**Stored**: `5000`

## GermanPercentInput

```tsx
<GermanPercentInput
  value={0.15}
  onChange={(val) => setPercent(val)}
  label="Prozentsatz"
  multiplyBy100={true}
  min={0}
  max={100}
/>
```

**Display**: `15,00 %`  
**Stored**: `0.15`

## GermanSlider

```tsx
<GermanSlider
  value={50}
  onChange={(val) => setValue(val)}
  label="Wert"
  min={0}
  max={100}
  step={1}
  formatType="currency"
  currencySymbol="€"
  showValue={true}
  showMinMax={true}
/>
```

**Display**: `50,00 €`  
**Stored**: `50`

## Format Types

| Type | Example Display | Use Case |
|------|----------------|----------|
| `number` | `1.234,56` | General numbers |
| `currency` | `1.234,56 €` | Money values |
| `percent` | `15,00 %` | Percentages |

## Common Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `number` | required | Current value |
| `onChange` | `function` | required | Change handler |
| `label` | `string` | - | Input label |
| `min` | `number` | - | Minimum value |
| `max` | `number` | - | Maximum value |
| `disabled` | `boolean` | `false` | Disabled state |
| `showError` | `boolean` | `true` | Show errors |
| `onValidationError` | `function` | - | Error callback |

## Validation

```tsx
<GermanNumberInput
  value={value}
  onChange={setValue}
  min={0}
  max={10000}
  onValidationError={(error) => {
    // Handle validation error
    toast.error(error);
  }}
/>
```

## Bidirectional Conversion

```tsx
// User types: "1.234,56"
// onChange receives: 1234.56
// Display shows: "1.234,56"

// Value changes to: 5678.90
// Display updates to: "5.678,90"
```

## Keyboard Input

- ✅ Digits: `0-9`
- ✅ Decimal separator: `,`
- ✅ Thousand separator: `.`
- ✅ Minus sign: `-` (at start)
- ❌ All other characters blocked

## Error Messages

| Error | Message |
|-------|---------|
| Invalid format | "Ungültiges Zahlenformat. Erwartetes Format: 1.234,56" |
| Below minimum | "Wert muss mindestens {min} sein" |
| Above maximum | "Wert darf höchstens {max} sein" |

## Styling

```css
/* Custom styling */
.german-number-input {
  font-family: 'Courier New', monospace;
  text-align: right;
}

.german-number-input.p-invalid {
  border-color: var(--red-500);
}
```

## Requirements

- ✅ 14.3: German formatting
- ✅ 14.6: Bidirectional conversion
- ✅ 14.9: Validation

## Browser Support

- ✅ Chrome/Edge
- ✅ Firefox
- ✅ Safari
- ✅ Mobile

## Full Documentation

See `GERMAN_INPUT_COMPONENTS.md` for complete API reference.
