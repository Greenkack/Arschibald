# Form Management System - Complete Guide

## Overview

The Form Management System provides a comprehensive solution for building forms in the Solar Calculator Pro application. It combines React Hook Form, Zod validation, reusable components, auto-save functionality, and error handling into a cohesive system.

## Table of Contents

1. [Core Features](#core-features)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Form Validation](#form-validation)
5. [Form Components](#form-components)
6. [Auto-Save](#auto-save)
7. [Error Handling](#error-handling)
8. [Advanced Usage](#advanced-usage)
9. [Best Practices](#best-practices)

## Core Features

- ✅ **React Hook Form Integration**: Performant form state management
- ✅ **Zod Schema Validation**: Type-safe validation with German error messages
- ✅ **Reusable Components**: 10+ pre-built form field components
- ✅ **Auto-Save**: Configurable automatic form saving
- ✅ **Error Handling**: Comprehensive error display and toast notifications
- ✅ **German Formatting**: Number formatting with German locale
- ✅ **TypeScript**: Full type safety throughout
- ✅ **Responsive**: Mobile-friendly design
- ✅ **Accessible**: ARIA labels and keyboard navigation

## Installation

All required dependencies are already installed:

```json
{
  "react-hook-form": "^7.49.2",
  "zod": "^3.22.4",
  "@hookform/resolvers": "^3.3.3"
}
```

## Quick Start

### 1. Define a Validation Schema

```typescript
import { z } from 'zod';
import { validators } from '../utils/formValidation';

const myFormSchema = z.object({
  name: validators.requiredString,
  email: validators.email,
  age: validators.positiveNumber,
});

type MyFormData = z.infer<typeof myFormSchema>;
```

### 2. Create a Form Component

```typescript
import { useForm } from '../hooks/useForm';
import { FormTextField, FormNumberField } from '../components/forms';
import { FormContainer } from '../components/forms';

function MyForm() {
  const { control, handleSubmit, formState } = useForm<MyFormData>({
    schema: myFormSchema,
    defaultValues: {
      name: '',
      email: '',
      age: 0,
    },
    onSubmitSuccess: (data) => {
      console.log('Form submitted:', data);
    },
  });

  return (
    <FormContainer
      onSubmit={handleSubmit}
      title="My Form"
      isSubmitting={formState.isSubmitting}
    >
      <FormTextField
        name="name"
        control={control}
        label="Name"
        required
      />
      
      <FormTextField
        name="email"
        control={control}
        label="E-Mail"
        required
      />
      
      <FormNumberField
        name="age"
        control={control}
        label="Alter"
        min={0}
        max={120}
        required
      />
    </FormContainer>
  );
}
```

## Form Validation

### Pre-defined Validators

The system includes common validators in `utils/formValidation.ts`:

```typescript
import { validators } from '../utils/formValidation';

// Available validators:
validators.email              // Email validation
validators.password           // Strong password (8+ chars, uppercase, number, special)
validators.url                // URL validation
validators.phone              // Phone number validation
validators.positiveNumber     // Number > 0
validators.nonNegativeNumber  // Number >= 0
validators.percentage         // Number 0-100
validators.requiredString     // Non-empty string
validators.optionalString     // Optional string
validators.date               // Date validation
```

### Pre-defined Schemas

Common form schemas are already defined:

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
  priceMatrixUploadSchema,
  userSettingsSchema,
} from '../utils/formValidation';
```

### Custom Validation

Create custom schemas for specific needs:

```typescript
const customSchema = z.object({
  username: z.string()
    .min(3, 'Mindestens 3 Zeichen')
    .max(20, 'Maximal 20 Zeichen')
    .regex(/^[a-zA-Z0-9_]+$/, 'Nur Buchstaben, Zahlen und Unterstriche'),
  
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwörter stimmen nicht überein',
  path: ['confirmPassword'],
});
```

## Form Components

### Available Components

1. **FormTextField** - Text input
2. **FormNumberField** - Number input with German formatting
3. **FormTextareaField** - Multi-line text
4. **FormDropdownField** - Single select dropdown
5. **FormMultiSelectField** - Multiple select
6. **FormDateField** - Date/time picker
7. **FormCheckboxField** - Checkbox
8. **FormRadioField** - Radio button group
9. **FormSliderField** - Slider
10. **FormPasswordField** - Password input with strength indicator

### Component Examples

#### Text Field

```typescript
<FormTextField
  name="firstName"
  control={control}
  label="Vorname"
  placeholder="Vorname eingeben"
  required
  helperText="Ihr offizieller Vorname"
/>
```

#### Number Field with German Formatting

```typescript
<FormNumberField
  name="price"
  control={control}
  label="Preis"
  mode="currency"
  currency="EUR"
  min={0}
  suffix=" €"
  showButtons
  required
/>
```

#### Dropdown

```typescript
<FormDropdownField
  name="category"
  control={control}
  label="Kategorie"
  options={[
    { label: 'Solar', value: 'solar' },
    { label: 'Wärmepumpe', value: 'heatpump' },
  ]}
  filter
  showClear
  required
/>
```

#### Date Field

```typescript
<FormDateField
  name="installationDate"
  control={control}
  label="Installationsdatum"
  showIcon
  dateFormat="dd.mm.yy"
  minDate={new Date()}
  required
/>
```

#### Checkbox

```typescript
<FormCheckboxField
  name="acceptTerms"
  control={control}
  label="Ich akzeptiere die Nutzungsbedingungen"
/>
```

#### Radio Group

```typescript
<FormRadioField
  name="paymentMethod"
  control={control}
  label="Zahlungsmethode"
  options={[
    { label: 'Rechnung', value: 'invoice' },
    { label: 'Kreditkarte', value: 'credit_card' },
    { label: 'PayPal', value: 'paypal' },
  ]}
  required
/>
```

#### Slider

```typescript
<FormSliderField
  name="brightness"
  control={control}
  label="Helligkeit"
  min={0}
  max={100}
  step={5}
/>
```

## Auto-Save

### Enable Auto-Save

```typescript
const { control, handleSubmit, isAutoSaving, lastSaved } = useForm({
  schema: mySchema,
  autoSave: true,
  autoSaveInterval: 5000, // Save every 5 seconds
  onAutoSave: async (data) => {
    // Save to API or localStorage
    await api.post('/save', data);
  },
});
```

### Display Auto-Save Status

```typescript
<FormContainer
  onSubmit={handleSubmit}
  isAutoSaving={isAutoSaving}
  lastSaved={lastSaved}
>
  {/* Form fields */}
</FormContainer>
```

### Manual Save

```typescript
const { manualSave } = useForm({
  // ... options
});

// Trigger manual save
<Button onClick={manualSave} label="Jetzt speichern" />
```

## Error Handling

### Automatic Error Display

Errors are automatically displayed below each field:

```typescript
<FormTextField
  name="email"
  control={control}
  label="E-Mail"
  required
/>
// If validation fails, error message appears automatically
```

### Toast Notifications

```typescript
const { control, handleSubmit } = useForm({
  schema: mySchema,
  showSuccessToast: true,
  showErrorToast: true,
  successMessage: 'Erfolgreich gespeichert!',
  errorMessage: 'Fehler beim Speichern',
  onSubmitSuccess: (data) => {
    // Success handler
  },
  onSubmitError: (error) => {
    // Error handler
  },
});
```

### Custom Error Handling

```typescript
import { useFormError, useHasError } from '../hooks/useForm';

const errorMessage = useFormError('email', formState.errors);
const hasError = useHasError('email', formState.errors);

if (hasError) {
  console.log('Error:', errorMessage);
}
```

## Advanced Usage

### Conditional Fields

```typescript
const { control, watch } = useForm({...});
const showBattery = watch('batteryStorage');

return (
  <>
    <FormCheckboxField
      name="batteryStorage"
      control={control}
      label="Batteriespeicher hinzufügen"
    />
    
    {showBattery && (
      <FormNumberField
        name="batteryCapacity"
        control={control}
        label="Speicherkapazität"
        suffix=" kWh"
      />
    )}
  </>
);
```

### Dynamic Field Arrays

```typescript
import { useFieldArray } from 'react-hook-form';

const { control } = useForm({...});
const { fields, append, remove } = useFieldArray({
  control,
  name: 'items',
});

return (
  <>
    {fields.map((field, index) => (
      <div key={field.id}>
        <FormTextField
          name={`items.${index}.name`}
          control={control}
          label={`Item ${index + 1}`}
        />
        <Button onClick={() => remove(index)} label="Entfernen" />
      </div>
    ))}
    <Button onClick={() => append({ name: '' })} label="Hinzufügen" />
  </>
);
```

### Form Reset

```typescript
const { reset } = useForm({...});

// Reset to default values
<Button onClick={() => reset()} label="Zurücksetzen" />

// Reset to specific values
<Button 
  onClick={() => reset({ name: 'New Name', email: 'new@email.com' })} 
  label="Neu laden"
/>
```

### Form Dirty State

```typescript
const { formState } = useForm({...});

if (formState.isDirty) {
  console.log('Form has unsaved changes');
}
```

## Best Practices

### 1. Always Define Schemas

```typescript
// ✅ Good
const schema = z.object({
  email: validators.email,
  age: validators.positiveNumber,
});

// ❌ Bad - No validation
const { control } = useForm({ defaultValues: {...} });
```

### 2. Use Type Inference

```typescript
// ✅ Good
type FormData = z.infer<typeof mySchema>;
const { control } = useForm<FormData>({...});

// ❌ Bad - Manual typing
interface FormData {
  email: string;
  age: number;
}
```

### 3. Provide Helper Text

```typescript
// ✅ Good
<FormNumberField
  name="roofArea"
  control={control}
  label="Dachfläche"
  helperText="Verfügbare Dachfläche in Quadratmetern"
/>

// ❌ Bad - No context
<FormNumberField name="roofArea" control={control} />
```

### 4. Use FormContainer

```typescript
// ✅ Good
<FormContainer onSubmit={handleSubmit} title="My Form">
  {/* Fields */}
</FormContainer>

// ❌ Bad - Manual form structure
<form onSubmit={handleSubmit}>
  {/* Fields */}
  <button type="submit">Submit</button>
</form>
```

### 5. Handle Loading States

```typescript
// ✅ Good
<FormContainer
  onSubmit={handleSubmit}
  isSubmitting={formState.isSubmitting}
>
  {/* Fields */}
</FormContainer>

// ❌ Bad - No loading indicator
<FormContainer onSubmit={handleSubmit}>
  {/* Fields */}
</FormContainer>
```

### 6. Use Auto-Save for Long Forms

```typescript
// ✅ Good for long forms
const { control } = useForm({
  autoSave: true,
  autoSaveInterval: 5000,
  onAutoSave: saveToAPI,
});

// ✅ Good for short forms
const { control } = useForm({
  autoSave: false,
});
```

### 7. Provide Clear Error Messages

```typescript
// ✅ Good
const schema = z.object({
  email: z.string()
    .min(1, 'E-Mail ist erforderlich')
    .email('Ungültige E-Mail-Adresse'),
});

// ❌ Bad - Generic errors
const schema = z.object({
  email: z.string().email(),
});
```

## Examples

See `src/examples/FormManagementDemo.tsx` for comprehensive examples including:

- Login form
- Solar calculator with auto-save
- Project creation form
- Customer management form

## API Reference

### useForm Hook

```typescript
interface UseFormOptions<TFieldValues> {
  schema?: ZodSchema;
  autoSave?: boolean;
  autoSaveInterval?: number;
  onAutoSave?: (data: TFieldValues) => Promise<void> | void;
  onSubmitSuccess?: (data: TFieldValues) => void;
  onSubmitError?: (error: Error) => void;
  showSuccessToast?: boolean;
  showErrorToast?: boolean;
  successMessage?: string;
  errorMessage?: string;
  defaultValues?: Partial<TFieldValues>;
  mode?: 'onBlur' | 'onChange' | 'onSubmit';
}
```

### FormContainer Props

```typescript
interface FormContainerProps {
  children: ReactNode;
  onSubmit: (e: React.FormEvent) => void;
  title?: string;
  description?: string;
  submitLabel?: string;
  cancelLabel?: string;
  onCancel?: () => void;
  isSubmitting?: boolean;
  isAutoSaving?: boolean;
  lastSaved?: Date | null;
  disabled?: boolean;
  showSubmitButton?: boolean;
  showCancelButton?: boolean;
  className?: string;
  actions?: ReactNode;
}
```

## Troubleshooting

### Form Not Validating

Ensure you've passed the schema to useForm:

```typescript
const { control } = useForm({
  schema: mySchema, // ← Don't forget this!
});
```

### Auto-Save Not Working

Check that you've provided the onAutoSave callback:

```typescript
const { control } = useForm({
  autoSave: true,
  onAutoSave: async (data) => {
    // ← Implement this
    await saveData(data);
  },
});
```

### TypeScript Errors

Ensure you're using type inference:

```typescript
type FormData = z.infer<typeof mySchema>;
const { control } = useForm<FormData>({...});
```

## Support

For issues or questions, refer to:
- React Hook Form docs: https://react-hook-form.com/
- Zod docs: https://zod.dev/
- PrimeReact docs: https://primereact.org/
