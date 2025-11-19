# Price Calculator Component - User Guide

## Overview

The Price Calculator component provides a comprehensive interface for calculating prices for PV systems with battery storage, extras, and services. It implements Task 38 of the Streamlit-to-Electron migration project.

## Features

### 1. Product Selection Interface
- **Module Count Input**: Number input with validation (1-200 modules)
- **Storage Model Selection**: Dropdown with battery storage options
- **Real-time Validation**: Immediate feedback on invalid inputs

### 2. Quantity Input with Validation
- Minimum: 1 module
- Maximum: 200 modules
- Increment/decrement buttons for easy adjustment
- Visual validation feedback

### 3. Options Selection

#### Extras & Accessories
- Leistungsoptimierer (Power Optimizers)
- Monitoring-System
- Wallbox 11kW (EV Charging Station)
- Überspannungsschutz (Surge Protection)
- Smart Meter

#### Services
- Installation & Inbetriebnahme (Installation & Commissioning)
- Detailplanung (Detailed Planning)
- Genehmigungsservice (Permit Service)
- Erweiterte Garantie (Extended Warranty)
- Wartungsvertrag (Maintenance Contract)

### 4. Real-time Price Calculation
- Automatic calculation on input change
- Debounced API calls for performance
- Loading indicators during calculation
- Error handling with user-friendly messages

### 5. Price Breakdown Display
- Detailed item list with quantities and prices
- Subtotal, discount, tax, and total
- German number formatting (1.234,56 €)
- Visual categorization (base, extras, services)
- Calculation metadata

## Usage

### Basic Usage

```tsx
import PriceCalculator from '../components/pricing/PriceCalculator';

function PriceMatrixPage() {
  return (
    <div>
      <PriceCalculator />
    </div>
  );
}
```

### Integration with PriceMatrix Page

The component is integrated into the PriceMatrix page as the "Berechnung" tab:

```tsx
<TabPanel header="🧮 Berechnung" leftIcon="pi pi-calculator">
  <PriceCalculator />
</TabPanel>
```

## API Integration

### Price Calculation Endpoint

```typescript
POST /api/v1/pricing/calculate
{
  "module_count": 20,
  "storage_model": "byd_10",
  "enable_fallback": true
}
```

**Response:**
```typescript
{
  "success": true,
  "price": 25000.00,
  "metadata": {
    "module_count": 20,
    "storage_model": "BYD Battery-Box Premium HVS 10.2",
    "matrix_id": 1,
    "calculation_time": 0.05
  }
}
```

## Component Structure

```
PriceCalculator/
├── Product Selection
│   ├── Module Count Input
│   └── Storage Model Dropdown
├── Extras Selection
│   └── Checkbox Grid
├── Services Selection
│   └── Checkbox Grid
├── Action Buttons
│   ├── Calculate Button
│   └── Reset Button
└── Price Breakdown
    ├── Items Table
    ├── Summary
    └── Metadata
```

## State Management

### Local State
- `moduleCount`: Number of PV modules
- `storageModel`: Selected battery storage model
- `selectedExtras`: Array of selected extra IDs
- `selectedServices`: Array of selected service IDs
- `calculating`: Loading state
- `result`: Calculation result
- `error`: Error message
- `validationErrors`: Field validation errors

### Effects
- Load storage options on mount
- Load extras on mount
- Load services on mount
- Calculate price on input change (debounced)

## Validation Rules

### Module Count
- Required field
- Minimum: 1
- Maximum: 200
- Must be a positive integer

### Storage Model
- Optional field
- Default: "kein Speicher" (no storage)

## Price Calculation Logic

1. **Base Price**: Retrieved from price matrix using INDEX/MATCH logic
   - Row: Module count (MATCH in column A)
   - Column: Storage model (MATCH in row 1)
   - Special handling for "kein Speicher" (last column)

2. **Extras Total**: Sum of selected extras prices

3. **Services Total**: Sum of selected services prices

4. **Subtotal**: Base + Extras + Services

5. **Discount**: Applied based on rules (currently 0)

6. **Tax**: 19% MwSt (German VAT)

7. **Total**: Subtotal - Discount + Tax

## German Number Formatting

All prices are formatted using German locale:
- Thousand separator: `.` (dot)
- Decimal separator: `,` (comma)
- Currency symbol: `€`
- Example: `25.000,00 €`

## Styling

### CSS Classes
- `.price-calculator`: Main container
- `.calculator-card`: Card wrapper
- `.form-grid`: Product selection grid
- `.extras-grid`: Extras selection grid
- `.services-grid`: Services selection grid
- `.price-breakdown`: Breakdown display
- `.price-summary`: Summary section

### Responsive Design
- Desktop: Multi-column grids
- Tablet: 2-column grids
- Mobile: Single column layout

### Dark Mode
- Automatic color scheme adaptation
- Uses CSS custom properties

## Error Handling

### Validation Errors
- Displayed inline below input fields
- Red border on invalid inputs
- Clear error messages in German

### API Errors
- Displayed as Message component
- User-friendly error messages
- Fallback to generic error message

### Network Errors
- Automatic retry logic (via axios interceptors)
- Timeout handling
- Connection error messages

## Accessibility

- Semantic HTML structure
- ARIA labels on form controls
- Keyboard navigation support
- Focus management
- Screen reader friendly

## Performance Optimization

### Debouncing
- Real-time calculation debounced to 500ms
- Prevents excessive API calls

### Memoization
- `useCallback` for calculation function
- Prevents unnecessary re-renders

### Lazy Loading
- Options loaded on mount
- Cached for subsequent renders

## Testing

### Unit Tests
```typescript
describe('PriceCalculator', () => {
  it('validates module count input', () => {
    // Test validation logic
  });

  it('calculates price correctly', () => {
    // Test calculation logic
  });

  it('formats prices in German format', () => {
    // Test number formatting
  });
});
```

### Integration Tests
```typescript
describe('PriceCalculator Integration', () => {
  it('fetches and displays storage options', async () => {
    // Test API integration
  });

  it('calculates price via API', async () => {
    // Test end-to-end calculation
  });
});
```

## Future Enhancements

### Planned Features
1. **Discount Rules Engine**: Automatic discount calculation
2. **Bundle Pricing**: Special pricing for product bundles
3. **Customer-Specific Pricing**: Personalized pricing based on customer
4. **Price History**: Track price changes over time
5. **Export Functionality**: Export calculation as PDF/Excel
6. **Save Calculations**: Save and retrieve previous calculations
7. **Comparison Mode**: Compare multiple configurations
8. **Advanced Filters**: Filter extras and services by category

### API Enhancements
1. **Batch Calculation**: Calculate multiple configurations at once
2. **Price Optimization**: Suggest optimal configuration
3. **Availability Check**: Real-time product availability
4. **Lead Time**: Estimated delivery time

## Troubleshooting

### Common Issues

**Issue**: Price not calculating
- **Solution**: Check if active matrix is set in backend
- **Solution**: Verify module count is within valid range
- **Solution**: Check browser console for API errors

**Issue**: Storage options not loading
- **Solution**: Verify backend API is running
- **Solution**: Check network tab for failed requests
- **Solution**: Ensure CORS is configured correctly

**Issue**: German formatting not working
- **Solution**: Verify `germanNumberFormatter` utility is imported
- **Solution**: Check browser locale settings
- **Solution**: Clear browser cache

## Support

For issues or questions:
1. Check the console for error messages
2. Verify API endpoints are accessible
3. Review the backend logs
4. Contact the development team

## Related Components

- `MatrixUpload`: Upload price matrices
- `MatrixList`: Manage price matrices
- `MatrixPreview`: Preview matrix data
- `MatrixVersionHistory`: View matrix versions
- `GermanNumberInput`: German number formatting input
- `GermanCurrencyInput`: German currency input

## Requirements Validation

This component fulfills **Requirement 7.2** from the design document:

✅ Create product selection interface
✅ Build quantity input with validation
✅ Implement options selection (extras, services)
✅ Add real-time price calculation
✅ Display price breakdown

## Version History

- **v1.0.0** (2024-01-XX): Initial implementation
  - Product selection interface
  - Quantity input with validation
  - Extras and services selection
  - Real-time price calculation
  - Price breakdown display
  - German number formatting
  - Responsive design
  - Error handling
