# Common UI Components Guide

This guide provides comprehensive documentation for all common UI components in the Solar Calculator Pro application.

## Table of Contents

1. [Form Input Components](#form-input-components)
2. [Data Table Component](#data-table-component)
3. [Modal Components](#modal-components)
4. [Loading Components](#loading-components)
5. [Skeleton Loaders](#skeleton-loaders)
6. [Toast Notifications](#toast-notifications)
7. [Confirmation Dialogs](#confirmation-dialogs)

---

## Form Input Components

The `FormInput` component is a versatile form input that supports multiple input types with consistent styling and validation.

### Basic Usage

```tsx
import { FormInput } from '@/components/common';

<FormInput
  name="email"
  label="Email Address"
  type="email"
  value={email}
  onChange={(value) => setEmail(value)}
  placeholder="Enter your email"
  required
  error={emailError}
  helperText="We'll never share your email"
/>
```

### Supported Input Types

- **text**: Standard text input
- **number**: Numeric input with min/max support
- **email**: Email input with validation
- **password**: Password input (masked)
- **select**: Dropdown selection
- **multiselect**: Multiple selection dropdown
- **textarea**: Multi-line text input
- **date**: Date picker
- **checkbox**: Single checkbox
- **radio**: Radio button group

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| name | string | required | Input name |
| label | string | - | Label text |
| type | string | 'text' | Input type |
| value | any | required | Input value |
| onChange | function | required | Change handler |
| placeholder | string | - | Placeholder text |
| required | boolean | false | Required field |
| disabled | boolean | false | Disabled state |
| error | string | - | Error message |
| helperText | string | - | Helper text |
| options | array | [] | Options for select/multiselect/radio |
| min | number | - | Min value for number input |
| max | number | - | Max value for number input |
| rows | number | 3 | Rows for textarea |

### Examples

#### Text Input
```tsx
<FormInput
  name="name"
  label="Full Name"
  type="text"
  value={name}
  onChange={setName}
  required
/>
```

#### Number Input
```tsx
<FormInput
  name="age"
  label="Age"
  type="number"
  value={age}
  onChange={setAge}
  min={0}
  max={120}
/>
```

#### Select Dropdown
```tsx
<FormInput
  name="country"
  label="Country"
  type="select"
  value={country}
  onChange={setCountry}
  options={[
    { label: 'Germany', value: 'de' },
    { label: 'Austria', value: 'at' },
  ]}
/>
```

#### Multi-Select
```tsx
<FormInput
  name="interests"
  label="Interests"
  type="multiselect"
  value={interests}
  onChange={setInterests}
  options={interestOptions}
/>
```

#### Checkbox
```tsx
<FormInput
  name="newsletter"
  label="Subscribe to newsletter"
  type="checkbox"
  value={newsletter}
  onChange={setNewsletter}
/>
```

#### Radio Buttons
```tsx
<FormInput
  name="gender"
  label="Gender"
  type="radio"
  value={gender}
  onChange={setGender}
  options={[
    { label: 'Male', value: 'male' },
    { label: 'Female', value: 'female' },
  ]}
/>
```

---

## Data Table Component

The `DataTable` component provides a feature-rich table with sorting, filtering, and pagination.

### Basic Usage

```tsx
import { DataTable } from '@/components/common';
import type { DataTableColumn } from '@/components/common';

const columns: DataTableColumn[] = [
  { field: 'id', header: 'ID', sortable: true },
  { field: 'name', header: 'Name', sortable: true, filterable: true },
  { field: 'email', header: 'Email', sortable: true, filterable: true },
];

<DataTable
  data={users}
  columns={columns}
  paginator
  rows={10}
  globalFilterFields={['name', 'email']}
/>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| data | array | required | Table data |
| columns | array | required | Column definitions |
| loading | boolean | false | Loading state |
| paginator | boolean | true | Enable pagination |
| rows | number | 10 | Rows per page |
| rowsPerPageOptions | array | [5,10,25,50] | Page size options |
| selectionMode | string | null | 'single' or 'multiple' |
| selection | any | - | Selected rows |
| onSelectionChange | function | - | Selection change handler |
| onRowClick | function | - | Row click handler |
| globalFilterFields | array | - | Fields for global search |
| showGridlines | boolean | true | Show grid lines |
| stripedRows | boolean | true | Striped rows |

### Column Definition

```tsx
interface DataTableColumn {
  field: string;           // Data field name
  header: string;          // Column header
  sortable?: boolean;      // Enable sorting
  filterable?: boolean;    // Enable filtering
  body?: (rowData) => ReactNode;  // Custom cell renderer
  style?: CSSProperties;   // Column style
}
```

### Custom Cell Rendering

```tsx
const columns: DataTableColumn[] = [
  {
    field: 'status',
    header: 'Status',
    body: (rowData) => (
      <span className={`badge ${rowData.status.toLowerCase()}`}>
        {rowData.status}
      </span>
    ),
  },
];
```

---

## Modal Components

Two modal components are available: `Modal` (full control) and `SimpleModal` (predefined buttons).

### Modal (Full Control)

```tsx
import { Modal } from '@/components/common';

<Modal
  visible={showModal}
  onHide={() => setShowModal(false)}
  title="Custom Modal"
  width="600px"
  footer={
    <div>
      <Button label="Cancel" onClick={() => setShowModal(false)} />
      <Button label="Save" onClick={handleSave} />
    </div>
  }
>
  <p>Modal content goes here</p>
</Modal>
```

### SimpleModal (Predefined Buttons)

```tsx
import { SimpleModal } from '@/components/common';

<SimpleModal
  visible={showModal}
  onHide={() => setShowModal(false)}
  title="Confirm Action"
  onConfirm={handleConfirm}
  confirmLabel="OK"
  cancelLabel="Cancel"
>
  <p>Are you sure?</p>
</SimpleModal>
```

### Props

#### Modal Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| visible | boolean | required | Visibility state |
| onHide | function | required | Close handler |
| title | string | - | Modal title |
| children | ReactNode | required | Modal content |
| footer | ReactNode | - | Custom footer |
| width | string | '50vw' | Modal width |
| modal | boolean | true | Modal overlay |
| closable | boolean | true | Show close button |
| maximizable | boolean | false | Show maximize button |

#### SimpleModal Additional Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| onConfirm | function | - | Confirm handler |
| onCancel | function | - | Cancel handler |
| confirmLabel | string | 'OK' | Confirm button label |
| cancelLabel | string | 'Cancel' | Cancel button label |
| confirmSeverity | string | 'success' | Button severity |
| showCancel | boolean | true | Show cancel button |
| showConfirm | boolean | true | Show confirm button |

---

## Loading Components

### LoadingSpinner

Display a loading spinner with optional message.

```tsx
import { LoadingSpinner } from '@/components/common';

// Inline spinner
<LoadingSpinner size="medium" message="Loading data..." />

// Full-screen spinner
<LoadingSpinner size="large" fullScreen message="Please wait..." />
```

### InlineSpinner

Small spinner for buttons and inline use.

```tsx
import { InlineSpinner } from '@/components/common';

<Button label="Loading" icon={<InlineSpinner />} disabled />
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| size | string | 'medium' | 'small', 'medium', 'large' |
| fullScreen | boolean | false | Full-screen overlay |
| message | string | - | Loading message |

---

## Skeleton Loaders

Skeleton loaders provide placeholder content while data is loading.

### Basic Skeleton

```tsx
import { SkeletonLoader } from '@/components/common';

<SkeletonLoader type="text" width="100%" />
<SkeletonLoader type="rectangle" width="200px" height="100px" />
<SkeletonLoader type="circle" width="50px" height="50px" />
```

### Specialized Skeletons

#### Card Skeleton
```tsx
import { CardSkeleton } from '@/components/common';

<CardSkeleton />
```

#### Table Skeleton
```tsx
import { TableSkeleton } from '@/components/common';

<TableSkeleton rows={5} columns={4} />
```

#### Form Skeleton
```tsx
import { FormSkeleton } from '@/components/common';

<FormSkeleton fields={4} />
```

#### List Skeleton
```tsx
import { ListSkeleton } from '@/components/common';

<ListSkeleton items={5} />
```

---

## Toast Notifications

Toast notifications provide non-intrusive feedback to users.

### Using the Hook

```tsx
import { ToastNotification, useToast } from '@/components/common';

function MyComponent() {
  const { toast, showSuccess, showError, showWarn, showInfo } = useToast();

  return (
    <>
      <ToastNotification ref={toast} />
      
      <Button 
        label="Success" 
        onClick={() => showSuccess('Success!', 'Operation completed')} 
      />
      <Button 
        label="Error" 
        onClick={() => showError('Error!', 'Something went wrong')} 
      />
      <Button 
        label="Warning" 
        onClick={() => showWarn('Warning!', 'Please be careful')} 
      />
      <Button 
        label="Info" 
        onClick={() => showInfo('Info', 'Just so you know')} 
      />
    </>
  );
}
```

### Toast Methods

- `showSuccess(summary, detail)` - Success message (green)
- `showError(summary, detail)` - Error message (red)
- `showWarn(summary, detail)` - Warning message (yellow)
- `showInfo(summary, detail)` - Info message (blue)
- `show(message)` - Custom message
- `clear()` - Clear all toasts

---

## Confirmation Dialogs

Confirmation dialogs ask users to confirm actions before proceeding.

### Using the Hook

```tsx
import { ConfirmDialog, useConfirmDialog } from '@/components/common';

function MyComponent() {
  const { confirmDialog, confirm, confirmDelete, confirmSave, confirmDiscard } = useConfirmDialog();

  return (
    <>
      <ConfirmDialog ref={confirmDialog} />
      
      {/* Custom confirmation */}
      <Button 
        label="Delete" 
        onClick={() => confirm({
          message: 'Are you sure?',
          header: 'Confirmation',
          onAccept: handleDelete,
        })} 
      />
      
      {/* Predefined delete confirmation */}
      <Button 
        label="Delete Item" 
        onClick={() => confirmDelete('Item Name', handleDelete)} 
      />
      
      {/* Predefined save confirmation */}
      <Button 
        label="Save" 
        onClick={() => confirmSave(handleSave)} 
      />
      
      {/* Predefined discard confirmation */}
      <Button 
        label="Discard" 
        onClick={() => confirmDiscard(handleDiscard)} 
      />
    </>
  );
}
```

### Confirmation Methods

- `confirm(options)` - Custom confirmation
- `confirmDelete(itemName, onConfirm)` - Delete confirmation
- `confirmSave(onConfirm, onReject)` - Save confirmation
- `confirmDiscard(onConfirm, onReject)` - Discard changes confirmation

### Standalone Confirmation Dialog

```tsx
import { StandaloneConfirmDialog } from '@/components/common';

<StandaloneConfirmDialog
  visible={showConfirm}
  onHide={() => setShowConfirm(false)}
  message="Are you sure you want to proceed?"
  header="Confirmation"
  onConfirm={handleConfirm}
  severity="warning"
/>
```

---

## Best Practices

### Form Validation

Always provide clear error messages and helper text:

```tsx
<FormInput
  name="email"
  label="Email"
  type="email"
  value={email}
  onChange={setEmail}
  error={emailError}
  helperText="We'll never share your email"
  required
/>
```

### Loading States

Use appropriate loading indicators:

```tsx
// For full-page loading
{isLoading && <LoadingSpinner fullScreen message="Loading..." />}

// For component loading
{isLoading ? <CardSkeleton /> : <Card>{content}</Card>}

// For button loading
<Button 
  label="Save" 
  icon={isSaving ? <InlineSpinner /> : 'pi pi-check'} 
  disabled={isSaving}
/>
```

### User Feedback

Always provide feedback for user actions:

```tsx
const handleSave = async () => {
  try {
    await saveData();
    showSuccess('Saved!', 'Your changes have been saved');
  } catch (error) {
    showError('Error!', 'Failed to save changes');
  }
};
```

### Destructive Actions

Always confirm destructive actions:

```tsx
const handleDelete = () => {
  confirmDelete('Project Name', async () => {
    await deleteProject();
    showSuccess('Deleted!', 'Project has been deleted');
  });
};
```

---

## Accessibility

All components follow accessibility best practices:

- Proper ARIA labels
- Keyboard navigation support
- Focus management
- Screen reader compatibility
- Color contrast compliance

---

## Styling

All components use CSS variables for theming:

```css
--text-color
--surface-card
--surface-section
--surface-border
--surface-hover
--primary-color
```

You can customize these in your theme configuration.

---

## Examples

See `src/examples/CommonComponentsDemo.tsx` for a comprehensive demo of all components.

To run the demo:

```bash
npm run dev
```

Then navigate to the demo page in your application.
