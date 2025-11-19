# Form Management - Quick Reference

## Basic Form Setup

```typescript
import { useForm } from '../hooks/useForm';
import { FormTextField, FormNumberField } from '../components/forms';
import { FormContainer } from '../components/forms';
import { z } from 'zod';

// 1. Define schema
const schema = z.object({
  name: z.string().min(1, 'Name erforderlich'),
  age: z.number().min(0, 'Alter muss positiv sein'),
});

type FormData = z.infer<typeof schema>;

// 2. Create form
function MyForm() {
  const { control, handleSubmit, formState } = useForm<FormData>({
    schema,
    defaultValues: { name: '', age: 0 },
    onSubmitSuccess: (data) => console.log(data),
  });

  return (
    <FormContainer onSubmit={handleSubmit} isSubmitting={formState.isSubmitting}>
      <FormTextField name="name" control={control} label="Name" required />
      <FormNumberField name="age" control={control} label="Alter" min={0} />
    </FormContainer>
  );
}
```

## Pre-defined Validators

```typescript
import { validators } from '../utils/formValidation';

validators.email              // Email
validators.password           // Strong password
validators.url                // URL
validators.phone              // Phone number
validators.positiveNumber     // Number > 0
validators.nonNegativeNumber  // Number >= 0
validators.percentage         // 0-100
validators.requiredString     // Non-empty string
validators.optionalString     // Optional string
validators.date               // Date
```

## Form Components

```typescript
// Text Input
<FormTextField name="field" control={control} label="Label" />

// Number Input (German formatting)
<FormNumberField name="field" control={control} label="Label" suffix=" €" />

// Textarea
<FormTextareaField name="field" control={control} label="Label" rows={4} />

// Dropdown
<FormDropdownField 
  name="field" 
  control={control} 
  options={[{ label: 'Option 1', value: '1' }]} 
/>

// Multi-Select
<FormMultiSelectField 
  name="field" 
  control={control} 
  options={[{ label: 'Option 1', value: '1' }]} 
/>

// Date Picker
<FormDateField name="field" control={control} dateFormat="dd.mm.yy" />

// Checkbox
<FormCheckboxField name="field" control={control} label="Accept" />

// Radio Group
<FormRadioField 
  name="field" 
  control={control} 
  options={[{ label: 'Yes', value: 'yes' }]} 
/>

// Slider
<FormSliderField name="field" control={control} min={0} max={100} />

// Password
<FormPasswordField name="field" control={control} feedback />
```

## Auto-Save

```typescript
const { control, isAutoSaving, lastSaved } = useForm({
  schema,
  autoSave: true,
  autoSaveInterval: 5000, // 5 seconds
  onAutoSave: async (data) => {
    await api.post('/save', data);
  },
});

<FormContainer 
  onSubmit={handleSubmit}
  isAutoSaving={isAutoSaving}
  lastSaved={lastSaved}
>
  {/* fields */}
</FormContainer>
```

## Error Handling

```typescript
const { control, handleSubmit } = useForm({
  schema,
  showSuccessToast: true,
  showErrorToast: true,
  successMessage: 'Gespeichert!',
  errorMessage: 'Fehler!',
  onSubmitSuccess: (data) => { /* success */ },
  onSubmitError: (error) => { /* error */ },
});
```

## Conditional Fields

```typescript
const { control, watch } = useForm({...});
const showField = watch('condition');

{showField && <FormTextField name="field" control={control} />}
```

## Form Reset

```typescript
const { reset } = useForm({...});

<Button onClick={() => reset()} label="Reset" />
```

## Pre-defined Schemas

```typescript
import {
  loginSchema,
  registerSchema,
  passwordChangeSchema,
  solarCalculatorSchema,
  heatPumpSchema,
  projectSchema,
  customerSchema,
  productSchema,
} from '../utils/formValidation';
```

## Common Patterns

### Login Form
```typescript
const { control, handleSubmit } = useForm<LoginFormData>({
  schema: loginSchema,
  defaultValues: { username: '', password: '', rememberMe: false },
});
```

### Form with Grid Layout
```typescript
<div className="form-grid">
  <FormTextField name="firstName" control={control} />
  <FormTextField name="lastName" control={control} />
</div>

/* CSS */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}
```

### Form with Sections
```typescript
<FormContainer onSubmit={handleSubmit}>
  <h3>Personal Info</h3>
  <FormTextField name="name" control={control} />
  
  <Divider />
  
  <h3>Contact Info</h3>
  <FormTextField name="email" control={control} />
</FormContainer>
```

## Tips

1. Always use `schema` for validation
2. Use `type FormData = z.infer<typeof schema>` for type safety
3. Provide `helperText` for complex fields
4. Use `FormContainer` for consistent styling
5. Enable `autoSave` for long forms
6. Show loading states with `isSubmitting`
7. Use German error messages
8. Test validation before implementing

## Demo

See `src/examples/FormManagementDemo.tsx` for complete examples.
