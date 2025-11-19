# German Input Components - Documentation

## Overview

Custom React input components with German number formatting for the Solar Calculator Pro application. These components provide bidirectional conversion between German format (1.234,56) and JavaScript numbers, with comprehensive validation and error handling.

## Requirements

- **14.3**: Apply German formatting to all input fields
- **14.6**: Implement bidirectional conversion
- **14.9**: Validate German-formatted number inputs

## Components

### 1. GermanNumberInput

Custom input component for numeric values with German formatting.

#### Features
- ✅ German number format (1.234,56)
- ✅ Bidirectional conversion (display ↔ calculation)
- ✅ Min/Max validation
- ✅ Customizable decimal places
- ✅ Error handling and display
- ✅ Keyboard input filtering
- ✅ Auto-formatting on blur

#### Props

```typescript
interface GermanNumberInputProps {
  value: number;                          // Current numeric value
  onChange: (value: number) => void;      // Change handler
  label?: string;                         // Input label
  min?: number;                           // Minimum value
  max?: number;                           // Maximum value
  decimalPlaces?: number;                 // Decimal places (default: 2)
  showError?: boolean;                    // Show error messages (default: true)
  errorMessage?: string;                  // Custom error message
  onValidationError?: (error: string) => void;  // Validation error callback
  className?: string;                     // Additional CSS classes
  disabled?: boolean;                     // Disabled state
  placeholder?: string;                   // Placeholder text
}
```

#### Usage

```tsx
import { GermanNumberInput } from './components';

function MyComponent() {
  const [value, setValue] = useState(1234.56);

  return (
    <GermanNumberInput
      value={value}
      onChange={setValue}
      label="Betrag"
      min={0}
      max={10000}
      decimalPlaces={2}
      placeholder="Wert eingeben"
    />
  );
}
```

#### Examples

```tsx
// Basic usage
<GermanNumberInput
  value={1234.56}
  onChange={setValue}
  label="Betrag"
/>
// Displays: 1.234,56

// With validation
<GermanNumberInput
  value={value}
  onChange={setValue}
  label="Betrag (0 - 10.000)"
  min={0}
  max={10000}
  onValidationError={(error) => console.error(error)}
/>

// Custom decimal places
<GermanNumberInput
  value={value}
  onChange={setValue}
  label="Präziser Wert"
  decimalPlaces={4}
/>
// Displays: 1.234,5678
```

---

### 2. GermanCurrencyInput

Custom input component for currency values with German formatting.

#### Features
- ✅ Currency symbol (customizable)
- ✅ Prefix or suffix position
- ✅ Always 2 decimal places
- ✅ Min/Max validation
- ✅ Auto-formatting on blur
- ✅ Focus behavior optimized for editing

#### Props

```typescript
interface GermanCurrencyInputProps {
  value: number;                          // Current numeric value
  onChange: (value: number) => void;      // Change handler
  label?: string;                         // Input label
  min?: number;                           // Minimum value (default: 0)
  max?: number;                           // Maximum value
  currencySymbol?: string;                // Currency symbol (default: "€")
  symbolPosition?: 'prefix' | 'suffix';   // Symbol position (default: "suffix")
  showError?: boolean;                    // Show error messages
  errorMessage?: string;                  // Custom error message
  onValidationError?: (error: string) => void;  // Validation error callback
  className?: string;                     // Additional CSS classes
  disabled?: boolean;                     // Disabled state
  placeholder?: string;                   // Placeholder text
}
```

#### Usage

```tsx
import { GermanCurrencyInput } from './components';

function MyComponent() {
  const [price, setPrice] = useState(5000);

  return (
    <GermanCurrencyInput
      value={price}
      onChange={setPrice}
      label="Preis"
      currencySymbol="€"
      symbolPosition="suffix"
      min={0}
      max={100000}
    />
  );
}
```

#### Examples

```tsx
// Euro (suffix)
<GermanCurrencyInput
  value={5000}
  onChange={setPrice}
  label="Preis"
  currencySymbol="€"
  symbolPosition="suffix"
/>
// Displays: 5.000,00 €

// Dollar (prefix)
<GermanCurrencyInput
  value={5000}
  onChange={setPrice}
  label="Price"
  currencySymbol="$"
  symbolPosition="prefix"
/>
// Displays: $ 5.000,00

// With validation
<GermanCurrencyInput
  value={price}
  onChange={setPrice}
  label="Preis"
  min={100}
  max={100000}
  onValidationError={(error) => alert(error)}
/>
```

---

### 3. GermanPercentInput

Custom input component for percentage values with German formatting.

#### Features
- ✅ Percent symbol automatically added
- ✅ Multiply by 100 optional
- ✅ Min/Max validation (0-100%)
- ✅ German formatting
- ✅ Focus behavior optimized

#### Props

```typescript
interface GermanPercentInputProps {
  value: number;                          // Current numeric value
  onChange: (value: number) => void;      // Change handler
  label?: string;                         // Input label
  min?: number;                           // Minimum value (default: 0)
  max?: number;                           // Maximum value (default: 100)
  multiplyBy100?: boolean;                // Multiply by 100 (default: true)
  showError?: boolean;                    // Show error messages
  errorMessage?: string;                  // Custom error message
  onValidationError?: (error: string) => void;  // Validation error callback
  className?: string;                     // Additional CSS classes
  disabled?: boolean;                     // Disabled state
  placeholder?: string;                   // Placeholder text
}
```

#### Usage

```tsx
import { GermanPercentInput } from './components';

function MyComponent() {
  const [percent, setPercent] = useState(0.15); // 15%

  return (
    <GermanPercentInput
      value={percent}
      onChange={setPercent}
      label="Prozentsatz"
      multiplyBy100={true}
      min={0}
      max={100}
    />
  );
}
```

#### Examples

```tsx
// Percentage (0-100%)
<GermanPercentInput
  value={0.15}
  onChange={setPercent}
  label="Prozentsatz"
  multiplyBy100={true}
/>
// Displays: 15,00 %
// Stores: 0.15

// Direct percentage (no multiplication)
<GermanPercentInput
  value={15}
  onChange={setPercent}
  label="Direkt als Prozent"
  multiplyBy100={false}
/>
// Displays: 15,00 %
// Stores: 15

// With range validation
<GermanPercentInput
  value={percent}
  onChange={setPercent}
  label="Begrenzter Bereich"
  min={0}
  max={50}
  multiplyBy100={true}
/>
```

---

### 4. GermanSlider

Custom slider component with German number formatting for display values.

#### Features
- ✅ German formatting for values
- ✅ Multiple format types (number, currency, percent)
- ✅ Min/Max display
- ✅ Value display
- ✅ Range slider support
- ✅ Customizable step size

#### Props

```typescript
interface GermanSliderProps {
  value: number | number[];               // Current value(s)
  onChange: (value: number | number[]) => void;  // Change handler
  label?: string;                         // Slider label
  min?: number;                           // Minimum value (default: 0)
  max?: number;                           // Maximum value (default: 100)
  step?: number;                          // Step size (default: 1)
  decimalPlaces?: number;                 // Decimal places (default: 2)
  showValue?: boolean;                    // Show current value (default: true)
  showMinMax?: boolean;                   // Show min/max labels (default: true)
  formatType?: 'number' | 'currency' | 'percent';  // Format type (default: 'number')
  currencySymbol?: string;                // Currency symbol (default: "€")
  className?: string;                     // Additional CSS classes
  disabled?: boolean;                     // Disabled state
  range?: boolean;                        // Range slider (default: false)
}
```

#### Usage

```tsx
import { GermanSlider } from './components';

function MyComponent() {
  const [value, setValue] = useState(50);

  return (
    <GermanSlider
      value={value}
      onChange={setValue}
      label="Wert"
      min={0}
      max={100}
      step={1}
      showValue={true}
      showMinMax={true}
      formatType="number"
    />
  );
}
```

#### Examples

```tsx
// Number slider
<GermanSlider
  value={50}
  onChange={setValue}
  label="Wert"
  min={0}
  max={100}
  formatType="number"
/>
// Displays: 50,00

// Currency slider
<GermanSlider
  value={5000}
  onChange={setValue}
  label="Preis"
  min={0}
  max={10000}
  step={100}
  formatType="currency"
  currencySymbol="€"
/>
// Displays: 5.000,00 €

// Percent slider
<GermanSlider
  value={15}
  onChange={setValue}
  label="Prozentsatz"
  min={0}
  max={100}
  step={5}
  formatType="percent"
/>
// Displays: 15,00 %

// Range slider
<GermanSlider
  value={[20, 80]}
  onChange={setValue}
  label="Bereich"
  min={0}
  max={100}
  formatType="number"
  range={true}
/>
// Displays: 20,00 - 80,00
```

---

## Utility Functions

### GermanNumberFormatter

Core utility class for German number formatting.

```typescript
import { germanFormatter } from './utils/germanNumberFormatter';

// Format number
const formatted = germanFormatter.format(1234.56);
// Returns: "1.234,56"

// Parse German number
const number = germanFormatter.parse("1.234,56");
// Returns: 1234.56

// Format currency
const currency = germanFormatter.formatCurrency(1234.56, "€", "suffix");
// Returns: "1.234,56 €"

// Format percent
const percent = germanFormatter.formatPercent(0.15, true);
// Returns: "15,00 %"

// Validate format
const isValid = germanFormatter.validate("1.234,56");
// Returns: true
```

### Convenience Functions

```typescript
import {
  formatGerman,
  parseGerman,
  formatCurrencyGerman,
  formatPercentGerman,
  validateGerman
} from './utils/germanNumberFormatter';

// Quick formatting
const formatted = formatGerman(1234.56);
// Returns: "1.234,56"

// Quick parsing
const number = parseGerman("1.234,56");
// Returns: 1234.56

// Quick currency formatting
const currency = formatCurrencyGerman(1234.56, "€");
// Returns: "1.234,56 €"

// Quick percent formatting
const percent = formatPercentGerman(0.15);
// Returns: "15,00 %"

// Quick validation
const isValid = validateGerman("1.234,56");
// Returns: true
```

---

## Styling

Import the CSS file to apply default styles:

```tsx
import './styles/germanInputComponents.css';
```

### Custom Styling

All components support custom CSS classes:

```tsx
<GermanNumberInput
  value={value}
  onChange={setValue}
  className="my-custom-class"
/>
```

### CSS Variables

The components use CSS variables for theming:

```css
:root {
  --text-color: #333;
  --text-color-secondary: #666;
  --primary-color: #007bff;
  --red-500: #dc3545;
  --surface-100: #f8f9fa;
}
```

---

## Validation and Error Handling

All input components support validation and error handling:

```tsx
<GermanNumberInput
  value={value}
  onChange={setValue}
  min={0}
  max={10000}
  showError={true}
  errorMessage="Custom error message"
  onValidationError={(error) => {
    console.error('Validation error:', error);
    // Handle error (e.g., show toast notification)
  }}
/>
```

### Validation Rules

1. **Format Validation**: Checks if input matches German number format
2. **Range Validation**: Checks if value is within min/max bounds
3. **Type Validation**: Ensures input can be parsed to a number

### Error Messages

- Invalid format: "Ungültiges Zahlenformat. Erwartetes Format: 1.234,56"
- Below minimum: "Wert muss mindestens {min} sein"
- Above maximum: "Wert darf höchstens {max} sein"

---

## Bidirectional Conversion

All components implement bidirectional conversion:

1. **Display → Calculation**: User types "1.234,56" → Stored as 1234.56
2. **Calculation → Display**: Value 1234.56 → Displayed as "1.234,56"

### Example

```tsx
const [value, setValue] = useState(1234.56);

<GermanNumberInput
  value={value}  // 1234.56
  onChange={setValue}
/>
// Displays: "1.234,56"

// User types: "5.678,90"
// onChange called with: 5678.90
// Displays: "5.678,90"
```

---

## Testing

Comprehensive tests are included:

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

### Test Coverage

- ✅ Rendering tests
- ✅ User input tests
- ✅ Validation tests
- ✅ Blur behavior tests
- ✅ Bidirectional conversion tests
- ✅ Disabled state tests
- ✅ Keyboard input tests
- ✅ Requirements compliance tests

---

## Requirements Compliance

### Requirement 14.3: Apply German formatting to input fields

✅ All components display numbers in German format (1.234,56)
- Dot (.) as thousand separator
- Comma (,) as decimal separator
- Exactly 2 decimal places (configurable)

### Requirement 14.6: Implement bidirectional conversion

✅ All components support bidirectional conversion
- German format → Number (parsing)
- Number → German format (formatting)
- Round-trip conversion maintains accuracy

### Requirement 14.9: Validate German-formatted number inputs

✅ All components include comprehensive validation
- Format validation (regex-based)
- Range validation (min/max)
- Error handling and display
- Validation callbacks

---

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Full support

---

## Dependencies

- React 18+
- PrimeReact 10+
- TypeScript 5+

---

## License

Part of the Solar Calculator Pro application.

---

## Support

For issues or questions, please contact the development team.
