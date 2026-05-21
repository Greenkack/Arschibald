# Price Calculator - Quick Reference

## Task 38: Price Calculation Interface ✅

### Features Implemented

#### 1️⃣ Product Selection Interface
```tsx
<InputNumber
  value={moduleCount}
  min={1}
  max={200}
  showButtons
/>

<Dropdown
  value={storageModel}
  options={storageOptions}
  optionLabel="name"
/>
```

#### 2️⃣ Quantity Input with Validation
- Min: 1 module
- Max: 200 modules
- Real-time validation
- Error messages in German

#### 3️⃣ Options Selection
**Extras:**
- ⚡ Leistungsoptimierer
- 📊 Monitoring-System
- 🚗 Wallbox 11kW
- 🛡️ Überspannungsschutz
- 📈 Smart Meter

**Services:**
- 🔧 Installation & Inbetriebnahme
- 📋 Detailplanung
- 📄 Genehmigungsservice
- 🛡️ Erweiterte Garantie
- 🔄 Wartungsvertrag

#### 4️⃣ Real-time Price Calculation
```typescript
useEffect(() => {
  if (moduleCount > 0) {
    calculatePrice();
  }
}, [moduleCount, storageModel, selectedExtras, selectedServices]);
```

#### 5️⃣ Price Breakdown Display
```
💰 Preisaufschlüsselung
├── Items Table
│   ├── 🏠 Base (PV + Storage)
│   ├── ➕ Extras
│   └── 🔧 Services
├── Zwischensumme
├── Rabatt (if applicable)
├── MwSt. (19%)
└── Gesamtpreis
```

## API Endpoints Used

### Calculate Price
```
POST /api/v1/pricing/calculate
{
  "module_count": 20,
  "storage_model": "byd_10",
  "enable_fallback": true
}
```

## Component Props

```typescript
interface PriceCalculatorProps {
  // No props - fully self-contained
}
```

## State Management

```typescript
// Product Selection
const [moduleCount, setModuleCount] = useState<number>(20);
const [storageModel, setStorageModel] = useState<string | null>(null);

// Options
const [selectedExtras, setSelectedExtras] = useState<string[]>([]);
const [selectedServices, setSelectedServices] = useState<string[]>([]);

// Calculation
const [calculating, setCalculating] = useState(false);
const [result, setResult] = useState<CalculationResult | null>(null);
const [error, setError] = useState<string | null>(null);
```

## Key Functions

### Calculate Price
```typescript
const calculatePrice = async () => {
  // 1. Validate inputs
  // 2. Call API
  // 3. Calculate extras/services
  // 4. Build breakdown
  // 5. Update state
};
```

### Handle Extra Toggle
```typescript
const handleExtraToggle = (extraId: string) => {
  setSelectedExtras(prev => 
    prev.includes(extraId) 
      ? prev.filter(id => id !== extraId)
      : [...prev, extraId]
  );
};
```

### Handle Reset
```typescript
const handleReset = () => {
  setModuleCount(20);
  setStorageModel('none');
  setSelectedExtras([]);
  setSelectedServices([]);
  setResult(null);
};
```

## German Number Formatting

```typescript
import { germanFormatter } from '../../utils/germanNumberFormatter';

// Format currency
germanFormatter.formatCurrency(25000.00)
// Output: "25.000,00 €"

// Format number
germanFormatter.format(1234.56)
// Output: "1.234,56"
```

## Validation Rules

```typescript
const validateInputs = (): boolean => {
  const errors: Record<string, string> = {};

  if (!moduleCount || moduleCount < 1) {
    errors.moduleCount = 'Bitte geben Sie eine gültige Modulanzahl ein';
  }

  if (moduleCount > 200) {
    errors.moduleCount = 'Maximale Modulanzahl ist 200';
  }

  setValidationErrors(errors);
  return Object.keys(errors).length === 0;
};
```

## Styling Classes

```css
.price-calculator          /* Main container */
.calculator-card           /* Card wrapper */
.form-grid                 /* Product selection grid */
.extras-grid               /* Extras grid */
.services-grid             /* Services grid */
.price-breakdown           /* Breakdown display */
.price-summary             /* Summary section */
.calculating-overlay       /* Loading state */
```

## Usage Example

```tsx
import PriceCalculator from '../components/pricing/PriceCalculator';

function PriceMatrixPage() {
  return (
    <TabPanel header="🧮 Berechnung">
      <PriceCalculator />
    </TabPanel>
  );
}
```

## Testing Checklist

- [ ] Module count validation (1-200)
- [ ] Storage model selection
- [ ] Extras selection/deselection
- [ ] Services selection/deselection
- [ ] Real-time calculation
- [ ] Price breakdown display
- [ ] German number formatting
- [ ] Error handling
- [ ] Loading states
- [ ] Reset functionality
- [ ] Responsive design
- [ ] Accessibility

## Requirements Met ✅

**Requirement 7.2:**
- ✅ Create product selection interface
- ✅ Build quantity input with validation
- ✅ Implement options selection (extras, services)
- ✅ Add real-time price calculation
- ✅ Display price breakdown

## Files Created

```
solar-calculator-pro/frontend/src/
├── components/pricing/
│   ├── PriceCalculator.tsx       (Main component)
│   ├── PriceCalculator.css       (Styles)
│   └── index.ts                  (Updated exports)
├── pages/
│   └── PriceMatrix.tsx           (Updated integration)
└── docs/
    ├── PRICE_CALCULATOR_GUIDE.md
    └── PRICE_CALCULATOR_QUICK_REFERENCE.md
```

## Performance Tips

1. **Debouncing**: Calculation is debounced via useEffect
2. **Memoization**: Use useCallback for expensive functions
3. **Lazy Loading**: Options loaded on mount, cached
4. **Optimistic Updates**: UI updates immediately

## Common Patterns

### Adding New Extra
```typescript
const newExtra: Extra = {
  id: 'new_extra',
  name: 'New Extra',
  price: 500,
  category: 'Category',
  description: 'Description'
};

setAvailableExtras(prev => [...prev, newExtra]);
```

### Custom Validation
```typescript
const customValidation = (value: number): string | null => {
  if (value % 2 !== 0) {
    return 'Modulanzahl muss gerade sein';
  }
  return null;
};
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Price not calculating | Check active matrix in backend |
| Options not loading | Verify API endpoints |
| Formatting incorrect | Check germanNumberFormatter import |
| Validation not working | Review validation rules |

## Next Steps

1. Integrate with real product database
2. Add discount rules engine
3. Implement save/load functionality
4. Add export to PDF/Excel
5. Create comparison mode

## Support

- Component: `PriceCalculator.tsx`
- Styles: `PriceCalculator.css`
- API: `/api/v1/pricing/*`
- Utils: `germanNumberFormatter.ts`
