# Heat Pump Input Form - Quick Reference Guide

## Overview

The Heat Pump Input Form system provides a comprehensive interface for collecting building data, calculating heat loads, and selecting appropriate heat pump models.

## Component Usage

### HeatPumpInputForm

```tsx
import { HeatPumpInputForm } from '@components/heatpump/HeatPumpInputForm';

<HeatPumpInputForm
  onSubmit={(data) => {
    console.log('Building data:', data);
    // Process building data
  }}
  initialData={{
    heatedArea: 150,
    buildingType: 'Neubau Standard',
    // ... other fields
  }}
/>
```

**Props:**
- `onSubmit: (data: BuildingData) => void` - Callback when form is submitted
- `initialData?: Partial<BuildingData>` - Optional initial form values

**BuildingData Interface:**
```typescript
interface BuildingData {
  // Building Information
  heatedArea: number;
  buildingType: string;
  buildingYear: string;
  insulationQuality: string;
  location: string;
  climateZone: string;
  
  // Heating System
  currentHeatingSystem: string;
  hotWaterDemand: string;
  heatingSystemTemp: string;
  
  // Consumption
  oilConsumption: number;
  gasConsumption: number;
  woodConsumption: number;
  systemEfficiency: number;
  heatingHours: number;
  
  // Costs
  gasMonthlyC cost: number;
  oilPricePerTon: number;
  woodPricePerSter: number;
  
  // Advanced
  desiredTemperature: number;
  heatingDays: number;
  outsideTempDesign: number;
}
```

### HeatPumpModelSelection

```tsx
import { HeatPumpModelSelection } from '@components/heatpump/HeatPumpModelSelection';

<HeatPumpModelSelection
  requiredPower={12.5}
  onSelect={(model, power) => {
    console.log('Selected:', model.model, power);
    // Process selection
  }}
/>
```

**Props:**
- `requiredPower: number` - Required heating power in kW
- `onSelect: (model: HeatPumpModel, power: number) => void` - Callback when model is selected

**HeatPumpModel Interface:**
```typescript
interface HeatPumpModel {
  model: string;
  manufacturer: string;
  type: string;
  heating_power_kw: number[];
  scop: number;
  max_flow_temp: number;
  price_range: string;
  features: string[];
  refrigerant: string;
  rating: number;
  awards: string[];
}
```

## API Integration

### Calculate Heat Load

```typescript
const calculateHeatLoad = async (buildingData: BuildingData) => {
  const response = await api.post('/api/v1/heatpump/calculate-heat-load', buildingData);
  return response.data.heat_load_kw;
};
```

### Get Heat Pump Models

```typescript
const getHeatPumpModels = async (manufacturer: string, type: string) => {
  const response = await api.get('/api/v1/heatpump/models', {
    params: { manufacturer, type }
  });
  return response.data.models;
};
```

## Styling Customization

### Override Form Styles

```css
/* Custom styles for heat pump form */
.heat-pump-input-form .form-section {
  background: var(--custom-bg);
  border-radius: 12px;
}

.heat-pump-input-form .total-cost-display {
  background: linear-gradient(135deg, #your-color-1, #your-color-2);
}
```

### Theme Variables

```css
:root {
  --primary-color: #667eea;
  --surface-card: #ffffff;
  --text-color: #495057;
  --text-color-secondary: #6c757d;
}
```

## German Number Formatting

All numbers are formatted using German locale:

```typescript
// Currency
const formatted = value.toLocaleString('de-DE', {
  style: 'currency',
  currency: 'EUR'
});
// Output: "1.234,56 €"

// Number with decimals
const formatted = value.toLocaleString('de-DE', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});
// Output: "1.234,56"
```

## Validation Rules

### Building Area
- Min: 30 m²
- Max: 1000 m²
- Step: 10 m²

### System Efficiency
- Min: 40%
- Max: 105%
- Step: 1%

### Heating Hours
- Min: 1200 hours
- Max: 2600 hours
- Step: 100 hours

### Temperature
- Desired: 18-24°C
- Outside Design: -20 to -5°C

### Heating Days
- Min: 150 days
- Max: 300 days
- Step: 10 days

## Common Patterns

### Loading State

```tsx
const [loading, setLoading] = useState(false);

const handleSubmit = async (data: BuildingData) => {
  setLoading(true);
  try {
    const heatLoad = await calculateHeatLoad(data);
    // Process result
  } catch (error) {
    // Handle error
  } finally {
    setLoading(false);
  }
};
```

### Error Handling

```tsx
const [error, setError] = useState<string | null>(null);

try {
  // API call
} catch (err) {
  setError('Fehler beim Berechnen der Heizlast');
  console.error(err);
}
```

### Form Reset

```tsx
const resetForm = () => {
  setBuildingData(null);
  setCalculatedHeatLoad(0);
  setSelectedHeatPump(null);
  setActiveIndex(0);
};
```

## Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 768px) {
  /* Mobile styles */
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
  /* Tablet styles */
}

/* Desktop */
@media (min-width: 1025px) {
  /* Desktop styles */
}
```

## Accessibility

### Keyboard Navigation
- All form fields are keyboard accessible
- Tab order follows logical flow
- Enter key submits forms

### Screen Readers
- All inputs have proper labels
- ARIA labels for complex components
- Semantic HTML structure

### Color Contrast
- Meets WCAG AA standards
- High contrast mode support
- Color-blind friendly indicators

## Performance Tips

### Lazy Loading
```tsx
const HeatPumpInputForm = lazy(() => 
  import('@components/heatpump/HeatPumpInputForm')
);
```

### Memoization
```tsx
const memoizedCalculation = useMemo(() => 
  calculateHeatLoad(buildingData),
  [buildingData]
);
```

### Debouncing
```tsx
const debouncedSearch = useDebounce(searchTerm, 300);
```

## Testing

### Unit Test Example

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { HeatPumpInputForm } from './HeatPumpInputForm';

test('submits form with correct data', () => {
  const handleSubmit = jest.fn();
  render(<HeatPumpInputForm onSubmit={handleSubmit} />);
  
  fireEvent.change(screen.getByLabelText('Beheizte Wohnfläche'), {
    target: { value: '150' }
  });
  
  fireEvent.click(screen.getByText('Heizlast berechnen'));
  
  expect(handleSubmit).toHaveBeenCalledWith(
    expect.objectContaining({ heatedArea: 150 })
  );
});
```

## Troubleshooting

### Form Not Submitting
- Check all required fields are filled
- Verify validation rules are met
- Check console for errors

### Styles Not Applying
- Ensure CSS file is imported
- Check CSS specificity
- Verify theme variables are defined

### API Errors
- Check network tab for request details
- Verify API endpoint URLs
- Check authentication tokens

## Best Practices

1. **Always validate input** before sending to backend
2. **Use TypeScript types** for type safety
3. **Handle loading states** for better UX
4. **Provide error feedback** to users
5. **Test on multiple devices** for responsiveness
6. **Follow German locale** for all numbers and dates
7. **Use semantic HTML** for accessibility
8. **Optimize images** and assets
9. **Implement proper error boundaries**
10. **Document complex logic** with comments

## Resources

- [PrimeReact Documentation](https://primereact.org/)
- [React Hook Form](https://react-hook-form.com/)
- [German Number Formatting](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Last Updated:** 2025-01-19
**Version:** 1.0.0
