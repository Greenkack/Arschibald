# Solar Calculator Form - Implementation Guide

## Overview

The Solar Calculator Form is a comprehensive multi-step wizard for collecting all necessary data to calculate a solar system. It implements Task 31 from the migration plan with full German localization and validation.

## Features

### ✅ Multi-Step Wizard
- **5 Steps**: Customer & Location → Roof Configuration → Module Selection → Consumption → Storage & Options
- **Progress Indicator**: Visual steps component showing current progress
- **Navigation**: Back/Next buttons with validation
- **Step Validation**: Each step validates before allowing progression

### ✅ Step 1: Customer & Location
- **Customer Name**: Required text input
- **Customer Email**: Optional email input
- **Location Autocomplete**: 
  - Searches common German cities
  - Auto-fills coordinates (latitude/longitude)
  - Displays selected coordinates
  - Validates location selection

### ✅ Step 2: Roof Configuration
- **Roof Area**: German number input with m² suffix
- **Roof Type**: Dropdown with options (Satteldach, Flachdach, etc.)
- **Roof Orientation**: Dropdown with compass directions
- **Roof Inclination**: Number input with degree suffix (0-90°)
- **Info Message**: Shows optimal configuration tip

### ✅ Step 3: Module Selection
- **Visual Module Grid**: 
  - Cards with product images
  - Manufacturer and model name
  - Capacity (W) and price (€)
  - Click to select
  - Visual selection indicator
- **Module Quantity**: Number input with +/- buttons
- **System Size Display**: Automatically calculates kWp from selection

### ✅ Step 4: Consumption
- **Annual Household Consumption**: German number input (kWh/year)
- **Annual Heating Consumption**: Optional German number input
- **Electricity Price**: German currency input (€/kWh)
- **Price Increase**: Percentage input for annual increase
- **Info Message**: Shows typical household consumption range

### ✅ Step 5: Storage & Options
- **Storage Toggle**: Checkbox to include battery storage
- **Storage Selection**: Visual cards (only shown if enabled)
  - Manufacturer and model
  - Capacity (kWh) and price (€)
  - Click to select
- **Simulation Period**: Years input (1-50)
- **PVGIS Toggle**: Use PVGIS for yield calculation
- **Yield Adjustment**: Percentage adjustment (-50% to +50%)

## Validation

### Required Fields
- Customer Name
- Location (address + coordinates)
- Roof Area (> 0)
- Roof Inclination (0-90°)
- Module Selection
- Module Quantity (> 0)
- Annual Consumption (> 0)
- Electricity Price (> 0)
- Storage Selection (if storage enabled)

### Validation Messages
- German error messages
- Field-level validation
- Step-level validation
- Visual error indicators (red borders)

## German Number Formatting

All numeric inputs use German formatting:
- **Thousand Separator**: Dot (.)
- **Decimal Separator**: Comma (,)
- **Example**: 1.234,56

### Components Used
- `GermanNumberInput`: For general numbers
- `GermanCurrencyInput`: For currency values
- Standard `InputNumber`: For percentages and degrees

## Data Structure

```typescript
interface SolarFormData {
  // Customer
  customerName: string;
  customerEmail: string;
  
  // Location
  latitude: number | null;
  longitude: number | null;
  address: string;
  
  // Roof
  roofAreaM2: number | null;
  roofOrientation: string;
  roofInclinationDeg: number;
  roofType: string;
  
  // Modules
  selectedModuleId: number | null;
  moduleQuantity: number;
  moduleCapacityW: number | null;
  
  // Consumption
  annualConsumptionKwhYr: number;
  consumptionHeatingKwhYr: number;
  electricityPriceKwh: number;
  
  // Storage
  includeStorage: boolean;
  selectedStorageId: number | null;
  selectedStorageCapacityKwh: number;
  
  // Options
  simulationPeriodYears: number;
  electricityPriceIncreaseAnnualPercent: number;
  usePvgis: boolean;
  globalYieldAdjustmentPercent: number;
}
```

## API Integration

### Request Transformation
The form data is transformed to match the backend API schema:
- Snake_case conversion
- Field name mapping
- Type validation

### Example API Call
```typescript
const requestData = {
  customer_name: formData.customerName,
  customer_email: formData.customerEmail,
  latitude: formData.latitude,
  longitude: formData.longitude,
  // ... other fields
};

const response = await post('/solar/calculate', requestData);
```

## Usage

### Basic Usage
```tsx
import SolarCalculatorForm from './components/solar/SolarCalculatorForm';

function MyComponent() {
  const handleSubmit = (data: SolarFormData) => {
    console.log('Form submitted:', data);
    // Call API
  };

  return (
    <SolarCalculatorForm
      onSubmit={handleSubmit}
      loading={false}
    />
  );
}
```

### With Initial Data
```tsx
<SolarCalculatorForm
  onSubmit={handleSubmit}
  initialData={{
    customerName: 'Max Mustermann',
    roofAreaM2: 50,
    moduleQuantity: 20
  }}
  loading={false}
/>
```

### With Cancel Handler
```tsx
<SolarCalculatorForm
  onSubmit={handleSubmit}
  onCancel={() => console.log('Cancelled')}
  loading={false}
/>
```

## Styling

### CSS Classes
- `.solar-calculator-form`: Main container
- `.form-step`: Individual step container
- `.module-grid`: Module selection grid
- `.module-card`: Individual module card
- `.module-card.selected`: Selected module
- `.storage-list`: Storage selection list
- `.storage-card`: Individual storage card
- `.storage-card.selected`: Selected storage
- `.form-actions`: Button container

### Customization
Override CSS variables:
```css
.solar-calculator-form {
  --primary-color: #your-color;
  --primary-color-rgb: r, g, b;
}
```

## Responsive Design

### Breakpoints
- **Desktop**: > 768px - Full grid layout
- **Tablet**: 481px - 768px - Adjusted grid
- **Mobile**: ≤ 480px - Single column

### Mobile Optimizations
- Stacked form actions
- Smaller module cards
- Single column module grid
- Reduced font sizes
- Compact spacing

## Accessibility

### Features
- Semantic HTML
- Label associations
- Keyboard navigation
- Focus management
- Error announcements
- ARIA labels (via PrimeReact)

### Keyboard Support
- Tab: Navigate fields
- Enter: Submit/Next
- Escape: Cancel (if handler provided)
- Arrow keys: Navigate dropdowns

## Performance

### Optimizations
- Lazy loading of module/storage data
- Debounced location search
- Memoized calculations
- Conditional rendering
- CSS animations (GPU accelerated)

## Testing

### Unit Tests
```typescript
describe('SolarCalculatorForm', () => {
  it('renders all steps', () => {
    // Test step rendering
  });

  it('validates required fields', () => {
    // Test validation
  });

  it('submits correct data', () => {
    // Test submission
  });
});
```

### Integration Tests
- Test full form flow
- Test API integration
- Test error handling
- Test loading states

## Future Enhancements

### Planned Features
1. **Real-time Calculation**: Show estimates as user types
2. **Map Integration**: Visual location picker
3. **3D Roof Visualization**: Preview module placement
4. **Save Draft**: Save incomplete forms
5. **Templates**: Pre-filled templates for common scenarios
6. **Comparison Mode**: Compare multiple configurations
7. **PDF Export**: Export form data as PDF
8. **Weather Data**: Real-time weather integration

### API Enhancements
1. **Module Search**: Filter modules by criteria
2. **Storage Recommendations**: AI-powered suggestions
3. **Price Updates**: Real-time pricing
4. **Availability Check**: Stock availability

## Troubleshooting

### Common Issues

**Issue**: Location autocomplete not working
- **Solution**: Check location suggestions are loaded
- **Solution**: Verify search function is called

**Issue**: Module images not loading
- **Solution**: Check image URLs
- **Solution**: Verify fallback image exists

**Issue**: Validation not working
- **Solution**: Check validation logic in `validateStep`
- **Solution**: Verify error state updates

**Issue**: Form not submitting
- **Solution**: Check all required fields
- **Solution**: Verify API endpoint
- **Solution**: Check network tab for errors

## Support

For issues or questions:
1. Check this documentation
2. Review component code
3. Check browser console
4. Review API documentation
5. Contact development team

## Version History

- **v1.0.0** (2024-01-15): Initial implementation
  - Multi-step wizard
  - All 5 steps implemented
  - German localization
  - Validation
  - Responsive design
