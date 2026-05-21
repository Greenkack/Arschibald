# Solar Calculator Form - Quick Reference

## Import

```tsx
import SolarCalculatorForm from './components/solar/SolarCalculatorForm';
```

## Basic Usage

```tsx
<SolarCalculatorForm
  onSubmit={(data) => console.log(data)}
  loading={false}
/>
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `onSubmit` | `(data: SolarFormData) => void` | Yes | Called when form is submitted |
| `onCancel` | `() => void` | No | Called when cancel is clicked |
| `initialData` | `Partial<SolarFormData>` | No | Pre-fill form data |
| `loading` | `boolean` | No | Show loading state |

## Form Steps

1. **Kunde & Standort** - Customer info and location
2. **Dachkonfiguration** - Roof configuration
3. **Modulauswahl** - Module selection with images
4. **Verbrauch** - Consumption data
5. **Speicher & Optionen** - Storage and options

## Required Fields

- Customer Name
- Location (address + coordinates)
- Roof Area (> 0 m²)
- Roof Inclination (0-90°)
- Module Selection
- Module Quantity (> 0)
- Annual Consumption (> 0 kWh)
- Electricity Price (> 0 €/kWh)

## German Number Format

- Thousand separator: `.` (dot)
- Decimal separator: `,` (comma)
- Example: `1.234,56`

## API Request Format

```typescript
{
  customer_name: string,
  customer_email: string,
  latitude: number,
  longitude: number,
  address: string,
  roof_area_m2: number,
  roof_orientation: string,
  roof_inclination_deg: number,
  roof_type: string,
  selected_module_id: number,
  module_quantity: number,
  module_capacity_w: number,
  annual_consumption_kwh_yr: number,
  consumption_heating_kwh_yr: number,
  electricity_price_kwh: number,
  include_storage: boolean,
  selected_storage_id: number | null,
  selected_storage_capacity_kwh: number,
  simulation_period_years: number,
  electricity_price_increase_annual_percent: number,
  use_pvgis: boolean,
  global_yield_adjustment_percent: number
}
```

## Validation Errors

Errors are displayed:
- Below each field (red text)
- Red border on invalid fields
- Prevents step progression

## Styling

Main CSS classes:
- `.solar-calculator-form`
- `.form-step`
- `.module-grid`
- `.module-card`
- `.storage-list`
- `.form-actions`

## Responsive Breakpoints

- Desktop: > 768px
- Tablet: 481-768px
- Mobile: ≤ 480px

## Example: Full Integration

```tsx
import React, { useState } from 'react';
import SolarCalculatorForm from './components/solar/SolarCalculatorForm';
import { useApi } from './hooks/useApi';

function SolarCalculator() {
  const { post } = useApi();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (data) => {
    setLoading(true);
    try {
      const response = await post('/solar/calculate', {
        customer_name: data.customerName,
        // ... transform other fields
      });
      setResult(response.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {!result ? (
        <SolarCalculatorForm
          onSubmit={handleSubmit}
          loading={loading}
        />
      ) : (
        <div>Results: {JSON.stringify(result)}</div>
      )}
    </div>
  );
}
```

## Common Customizations

### Pre-fill Data
```tsx
<SolarCalculatorForm
  initialData={{
    customerName: 'Max Mustermann',
    roofAreaM2: 50,
    moduleQuantity: 20
  }}
  onSubmit={handleSubmit}
/>
```

### Add Cancel Handler
```tsx
<SolarCalculatorForm
  onSubmit={handleSubmit}
  onCancel={() => router.push('/dashboard')}
/>
```

### Custom Styling
```css
.solar-calculator-form {
  --primary-color: #your-color;
}

.module-card {
  border-radius: 12px;
}
```

## Keyboard Shortcuts

- **Tab**: Navigate fields
- **Enter**: Next step / Submit
- **Escape**: Cancel (if handler provided)
- **Arrow Keys**: Navigate dropdowns

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Location not working | Check `locationSuggestions` array |
| Images not loading | Verify image URLs and fallback |
| Validation failing | Check `validateStep` function |
| Form not submitting | Verify all required fields |

## Performance Tips

1. Use `React.memo` for module/storage cards
2. Debounce location search
3. Lazy load images
4. Memoize calculations
5. Use virtual scrolling for large lists

## Accessibility

- All inputs have labels
- Keyboard navigable
- Screen reader friendly
- Focus management
- Error announcements

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

- PrimeReact 10+
- React 18+
- TypeScript 5+

## Files

- `SolarCalculatorForm.tsx` - Main component
- `SolarCalculatorForm.css` - Styles
- `index.ts` - Export

## Related Components

- `GermanNumberInput` - Number formatting
- `GermanCurrencyInput` - Currency formatting
- `GermanPercentInput` - Percentage formatting
- `GermanSlider` - Slider with German format
