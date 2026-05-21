# Common UI Components - Quick Reference

## Import Statement

```tsx
import {
  FormInput,
  DataTable,
  Modal,
  SimpleModal,
  LoadingSpinner,
  InlineSpinner,
  SkeletonLoader,
  CardSkeleton,
  TableSkeleton,
  FormSkeleton,
  ListSkeleton,
  ToastNotification,
  useToast,
  ConfirmDialog,
  useConfirmDialog,
  StandaloneConfirmDialog,
} from '@/components/common';
```

## Quick Examples

### Form Input
```tsx
<FormInput
  name="email"
  label="Email"
  type="email"
  value={email}
  onChange={setEmail}
  required
/>
```

### Data Table
```tsx
<DataTable
  data={users}
  columns={[
    { field: 'name', header: 'Name', sortable: true },
    { field: 'email', header: 'Email', filterable: true },
  ]}
  paginator
/>
```

### Modal
```tsx
<SimpleModal
  visible={show}
  onHide={() => setShow(false)}
  title="Confirm"
  onConfirm={handleConfirm}
>
  Content here
</SimpleModal>
```

### Loading
```tsx
<LoadingSpinner size="medium" message="Loading..." />
<InlineSpinner />
<CardSkeleton />
```

### Toast
```tsx
const { toast, showSuccess, showError } = useToast();

<ToastNotification ref={toast} />
<Button onClick={() => showSuccess('Done!', 'Success')} />
```

### Confirm Dialog
```tsx
const { confirmDialog, confirmDelete } = useConfirmDialog();

<ConfirmDialog ref={confirmDialog} />
<Button onClick={() => confirmDelete('Item', handleDelete)} />
```

## Component Checklist

- ✅ FormInput - All input types (text, number, select, etc.)
- ✅ DataTable - Sorting, filtering, pagination
- ✅ Modal - Full control and simple variants
- ✅ LoadingSpinner - Inline and full-screen
- ✅ SkeletonLoader - Card, table, form, list variants
- ✅ ToastNotification - Success, error, warning, info
- ✅ ConfirmDialog - Custom and predefined confirmations

## Common Patterns

### Form with Validation
```tsx
<FormInput
  name="field"
  label="Field"
  value={value}
  onChange={setValue}
  error={error}
  required
/>
```

### Table with Actions
```tsx
<DataTable
  data={items}
  columns={[
    ...columns,
    {
      field: 'actions',
      header: 'Actions',
      body: (row) => (
        <Button icon="pi pi-trash" onClick={() => handleDelete(row.id)} />
      ),
    },
  ]}
/>
```

### Loading State
```tsx
{loading ? <CardSkeleton /> : <Card>{content}</Card>}
```

### User Feedback
```tsx
try {
  await action();
  showSuccess('Success!', 'Action completed');
} catch (error) {
  showError('Error!', error.message);
}
```

### Confirm Before Delete
```tsx
confirmDelete(itemName, async () => {
  await deleteItem();
  showSuccess('Deleted!');
});
```

## Props Summary

### FormInput
- `name`, `label`, `type`, `value`, `onChange`
- `required`, `disabled`, `error`, `helperText`
- `options` (for select/multiselect/radio)

### DataTable
- `data`, `columns`
- `paginator`, `rows`, `loading`
- `selectionMode`, `onRowClick`
- `globalFilterFields`

### Modal
- `visible`, `onHide`, `title`, `children`
- `footer`, `width`, `modal`

### LoadingSpinner
- `size`, `fullScreen`, `message`

### Toast
- `showSuccess(summary, detail)`
- `showError(summary, detail)`
- `showWarn(summary, detail)`
- `showInfo(summary, detail)`

### ConfirmDialog
- `confirm(options)`
- `confirmDelete(name, onConfirm)`
- `confirmSave(onConfirm)`
- `confirmDiscard(onConfirm)`

## File Locations

```
src/components/common/
├── FormInput.tsx
├── DataTable.tsx
├── Modal.tsx
├── LoadingSpinner.tsx
├── SkeletonLoader.tsx
├── ToastNotification.tsx
├── ConfirmDialog.tsx
└── index.ts

src/examples/
└── CommonComponentsDemo.tsx
```

## See Also

- Full Guide: `COMMON_COMPONENTS_GUIDE.md`
- Demo: `src/examples/CommonComponentsDemo.tsx`
- PrimeReact Docs: https://primereact.org/
