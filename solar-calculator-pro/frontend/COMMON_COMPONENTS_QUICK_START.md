# Common UI Components - Quick Start Guide

Get started with the common UI components in 5 minutes!

## Installation

Components are already installed and ready to use. No additional setup required.

## Basic Setup

### 1. Add Global Components to Your App

Add these to your main App component or layout:

```tsx
// src/App.tsx
import { ToastNotification, ConfirmDialog, useToast, useConfirmDialog } from '@/components/common';

function App() {
  const { toast } = useToast();
  const { confirmDialog } = useConfirmDialog();

  return (
    <>
      {/* Global components */}
      <ToastNotification ref={toast} />
      <ConfirmDialog ref={confirmDialog} />
      
      {/* Your app content */}
      <YourRoutes />
    </>
  );
}
```

### 2. Use Components in Your Pages

```tsx
import { FormInput, DataTable, LoadingSpinner } from '@/components/common';

function MyPage() {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  return (
    <div>
      <FormInput
        name="name"
        label="Name"
        value={name}
        onChange={setName}
      />
      
      {loading && <LoadingSpinner />}
    </div>
  );
}
```

## Common Patterns

### Form with Validation

```tsx
const [formData, setFormData] = useState({ email: '', age: 0 });
const [errors, setErrors] = useState({});

<FormInput
  name="email"
  label="Email"
  type="email"
  value={formData.email}
  onChange={(value) => setFormData({ ...formData, email: value })}
  error={errors.email}
  required
/>
```

### Data Table with Actions

```tsx
const columns = [
  { field: 'name', header: 'Name', sortable: true },
  { field: 'email', header: 'Email', filterable: true },
  {
    field: 'actions',
    header: 'Actions',
    body: (row) => (
      <Button icon="pi pi-trash" onClick={() => handleDelete(row.id)} />
    ),
  },
];

<DataTable data={users} columns={columns} paginator />
```

### User Feedback

```tsx
const { showSuccess, showError } = useToast();

const handleSave = async () => {
  try {
    await saveData();
    showSuccess('Saved!', 'Data saved successfully');
  } catch (error) {
    showError('Error!', error.message);
  }
};
```

### Confirm Before Action

```tsx
const { confirmDelete } = useConfirmDialog();

const handleDelete = () => {
  confirmDelete('User', async () => {
    await deleteUser();
    showSuccess('Deleted!');
  });
};
```

### Loading States

```tsx
// Full-screen loading
{isLoading && <LoadingSpinner fullScreen message="Loading..." />}

// Component loading
{isLoading ? <CardSkeleton /> : <Card>{content}</Card>}

// Button loading
<Button 
  label="Save" 
  icon={isSaving ? <InlineSpinner /> : 'pi pi-check'} 
  disabled={isSaving}
/>
```

## Component Cheat Sheet

| Component | Use Case | Import |
|-----------|----------|--------|
| FormInput | All form inputs | `import { FormInput } from '@/components/common'` |
| DataTable | Tables with sorting/filtering | `import { DataTable } from '@/components/common'` |
| Modal | Dialogs and popups | `import { Modal, SimpleModal } from '@/components/common'` |
| LoadingSpinner | Loading indicators | `import { LoadingSpinner } from '@/components/common'` |
| SkeletonLoader | Placeholder content | `import { CardSkeleton, TableSkeleton } from '@/components/common'` |
| ToastNotification | User feedback | `import { useToast } from '@/components/common'` |
| ConfirmDialog | Confirm actions | `import { useConfirmDialog } from '@/components/common'` |

## Input Types

FormInput supports these types:
- `text`, `email`, `password` - Text inputs
- `number` - Numeric input
- `select` - Dropdown
- `multiselect` - Multiple selection
- `textarea` - Multi-line text
- `date` - Date picker
- `checkbox` - Single checkbox
- `radio` - Radio button group

## Toast Severities

- `showSuccess()` - Green, success message
- `showError()` - Red, error message
- `showWarn()` - Yellow, warning message
- `showInfo()` - Blue, info message

## Confirmation Types

- `confirm()` - Custom confirmation
- `confirmDelete()` - Delete confirmation
- `confirmSave()` - Save confirmation
- `confirmDiscard()` - Discard changes confirmation

## Demo

Run the interactive demo:

```bash
npm run dev
```

Then navigate to the demo page to see all components in action.

## Documentation

- **Full Guide**: `COMMON_COMPONENTS_GUIDE.md`
- **Quick Reference**: `COMMON_COMPONENTS_QUICK_REFERENCE.md`
- **Demo Code**: `src/examples/CommonComponentsDemo.tsx`

## Need Help?

1. Check the comprehensive guide
2. Look at the demo code
3. Review the TypeScript definitions
4. Check PrimeReact docs: https://primereact.org/

## Tips

✅ Always use TypeScript for better IntelliSense
✅ Add error handling to all async operations
✅ Provide user feedback for all actions
✅ Use loading states for better UX
✅ Confirm destructive actions
✅ Keep forms simple and clear
✅ Use skeleton loaders for perceived performance

---

**You're ready to go!** Start building amazing UIs with these components.
