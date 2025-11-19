# Price Matrix Management - Quick Reference

## Overview

Complete guide for managing price matrices in the Solar Calculator Pro application.

## Components

### MatrixList
**Location**: `src/components/pricing/MatrixList.tsx`

**Purpose**: Display and manage all price matrices

**Props**:
```typescript
interface MatrixListProps {
  onMatrixSelect?: (matrix: Matrix) => void;
  onMatrixActivate?: (matrix: Matrix) => void;
  onRefresh?: () => void;
}
```

**Usage**:
```tsx
<MatrixList
  onMatrixSelect={(matrix) => console.log('Selected:', matrix)}
  onMatrixActivate={(matrix) => console.log('Activated:', matrix)}
  onRefresh={() => console.log('Refreshed')}
/>
```

**Features**:
- Sortable data table
- Pagination (5, 10, 25, 50 rows)
- Status indicators (Active/Inactive)
- Action buttons (View, Activate, Export, Delete)
- Confirmation dialogs
- Toast notifications

### MatrixPreview
**Location**: `src/components/pricing/MatrixPreview.tsx`

**Purpose**: Display detailed matrix data

**Props**:
```typescript
interface MatrixPreviewProps {
  matrixId: number;
  onClose?: () => void;
}
```

**Usage**:
```tsx
<MatrixPreview
  matrixId={123}
  onClose={() => console.log('Closed')}
/>
```

**Features**:
- Full matrix data table
- Scrollable for large matrices
- German number formatting
- Metadata display
- Statistics overview
- Loading states

### MatrixVersionHistory
**Location**: `src/components/pricing/MatrixVersionHistory.tsx`

**Purpose**: Display version history

**Props**:
```typescript
interface MatrixVersionHistoryProps {
  matrixId?: number;
}
```

**Usage**:
```tsx
<MatrixVersionHistory matrixId={123} />
```

**Features**:
- Timeline visualization
- Version restore
- Version details dialog
- Active version highlighting
- New version badges

## API Endpoints

### List Matrices
```typescript
GET /pricing/matrix

Response:
{
  success: true,
  matrices: [
    {
      id: 1,
      name: "Matrix 2024",
      description: "Main pricing matrix",
      is_active: true,
      pricing_mode: "pauschal",
      include_accessories: true,
      include_misc: true,
      created_at: "2024-01-01T00:00:00",
      updated_at: "2024-01-01T00:00:00"
    }
  ],
  count: 1
}
```

### Get Matrix Data
```typescript
GET /pricing/matrix/{id}

Response:
{
  success: true,
  matrix: {
    meta: { ... },
    rows: [ ... ],
    columns: [ ... ],
    cells: { ... }
  }
}
```

### Activate Matrix
```typescript
PUT /pricing/matrix/{id}/activate

Response:
{
  success: true,
  message: "Matrix 1 ist jetzt aktiv"
}
```

### Delete Matrix
```typescript
DELETE /pricing/matrix/{id}

Response:
{
  success: true,
  message: "Matrix 1 wurde gelöscht"
}
```

### Export Matrix
```typescript
POST /pricing/matrix/export/csv
Body: {
  matrix_id: 1,
  delimiter: ";"
}

Response:
{
  success: true,
  csv_content: "ROW_LABEL;Col1;Col2\n10;1000.00;1500.00\n",
  matrix_id: 1
}
```

## Common Tasks

### 1. Display Matrix List
```tsx
import MatrixList from '../components/pricing/MatrixList';

function MyComponent() {
  return <MatrixList />;
}
```

### 2. Preview Selected Matrix
```tsx
import { useState } from 'react';
import MatrixList from '../components/pricing/MatrixList';
import MatrixPreview from '../components/pricing/MatrixPreview';

function MyComponent() {
  const [selectedMatrix, setSelectedMatrix] = useState(null);

  return (
    <>
      <MatrixList onMatrixSelect={setSelectedMatrix} />
      {selectedMatrix && (
        <MatrixPreview
          matrixId={selectedMatrix.id}
          onClose={() => setSelectedMatrix(null)}
        />
      )}
    </>
  );
}
```

### 3. Activate Matrix
```tsx
const handleActivate = async (matrix) => {
  try {
    const response = await api.put(`/pricing/matrix/${matrix.id}/activate`);
    if (response.data.success) {
      // Show success message
      toast.success(`Matrix "${matrix.name}" aktiviert`);
      // Refresh list
      loadMatrices();
    }
  } catch (error) {
    toast.error('Aktivierung fehlgeschlagen');
  }
};
```

### 4. Export Matrix
```tsx
const handleExport = async (matrix) => {
  try {
    const response = await api.post('/pricing/matrix/export/csv', {
      matrix_id: matrix.id,
      delimiter: ';'
    });
    
    if (response.data.success) {
      // Create download
      const blob = new Blob([response.data.csv_content], { 
        type: 'text/csv;charset=utf-8;' 
      });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `matrix_${matrix.name}.csv`);
      link.click();
    }
  } catch (error) {
    toast.error('Export fehlgeschlagen');
  }
};
```

### 5. Delete Matrix
```tsx
const handleDelete = async (matrix) => {
  if (confirm(`Matrix "${matrix.name}" wirklich löschen?`)) {
    try {
      const response = await api.delete(`/pricing/matrix/${matrix.id}`);
      if (response.data.success) {
        toast.success('Matrix gelöscht');
        loadMatrices();
      }
    } catch (error) {
      toast.error('Löschen fehlgeschlagen');
    }
  }
};
```

## Styling

### Custom Styles
All components use CSS modules for styling:
- `MatrixList.css` - List view styles
- `MatrixPreview.css` - Preview styles
- `MatrixVersionHistory.css` - History styles

### Theme Variables
Components use PrimeReact theme variables:
```css
var(--surface-card)
var(--surface-border)
var(--text-color)
var(--text-color-secondary)
var(--primary-color)
var(--green-500)
var(--blue-500)
```

### Responsive Breakpoints
```css
@media (max-width: 768px) {
  /* Mobile styles */
}
```

## Error Handling

### Toast Notifications
```tsx
import { Toast } from 'primereact/toast';

const toastRef = useRef<Toast>(null);

// Success
toastRef.current?.show({
  severity: 'success',
  summary: 'Erfolg',
  detail: 'Operation erfolgreich',
  life: 3000
});

// Error
toastRef.current?.show({
  severity: 'error',
  summary: 'Fehler',
  detail: 'Operation fehlgeschlagen',
  life: 3000
});
```

### Confirmation Dialogs
```tsx
import { confirmDialog } from 'primereact/confirmdialog';

confirmDialog({
  message: 'Wirklich löschen?',
  header: 'Bestätigung',
  icon: 'pi pi-exclamation-triangle',
  acceptLabel: 'Ja',
  rejectLabel: 'Nein',
  accept: () => {
    // Perform action
  }
});
```

## Best Practices

### 1. Always Handle Loading States
```tsx
const [loading, setLoading] = useState(false);

const loadData = async () => {
  setLoading(true);
  try {
    // Load data
  } finally {
    setLoading(false);
  }
};
```

### 2. Use Proper Error Messages
```tsx
catch (error: any) {
  const message = error.response?.data?.error || 'Unbekannter Fehler';
  toast.error(message);
}
```

### 3. Refresh After Mutations
```tsx
const handleActivate = async (matrix) => {
  await api.put(`/pricing/matrix/${matrix.id}/activate`);
  await loadMatrices(); // Refresh list
};
```

### 4. Format Numbers Properly
```tsx
const formatGermanNumber = (value: number): string => {
  return new Intl.NumberFormat('de-DE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};
```

### 5. Use TypeScript Interfaces
```tsx
interface Matrix {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  // ... other fields
}
```

## Troubleshooting

### Matrix Not Loading
- Check API endpoint is accessible
- Verify authentication token
- Check network tab for errors
- Ensure backend service is running

### Export Not Working
- Verify CSV content is valid
- Check browser download settings
- Ensure proper MIME type
- Check for CORS issues

### Preview Not Displaying
- Verify matrix ID is valid
- Check matrix has data
- Ensure API returns correct format
- Check for JavaScript errors

### Activation Fails
- Verify matrix exists
- Check user permissions
- Ensure matrix is not already active
- Check for database constraints

## Performance Tips

### 1. Use Pagination
```tsx
<DataTable
  value={data}
  paginator
  rows={10}
  rowsPerPageOptions={[5, 10, 25, 50]}
/>
```

### 2. Implement Virtual Scrolling
For very large matrices, consider virtual scrolling:
```tsx
<DataTable
  value={data}
  scrollable
  scrollHeight="500px"
  virtualScrollerOptions={{ itemSize: 46 }}
/>
```

### 3. Debounce Refresh
```tsx
const debouncedRefresh = useMemo(
  () => debounce(loadMatrices, 300),
  []
);
```

### 4. Cache Matrix Data
```tsx
const [cache, setCache] = useState<Map<number, MatrixData>>(new Map());

const loadMatrix = async (id: number) => {
  if (cache.has(id)) {
    return cache.get(id);
  }
  const data = await api.get(`/pricing/matrix/${id}`);
  setCache(new Map(cache.set(id, data)));
  return data;
};
```

## Related Documentation

- [Price Matrix Upload Guide](./PRICE_MATRIX_UPLOAD_GUIDE.md)
- [API Documentation](../../backend/docs/API_DOCUMENTATION.md)
- [PrimeReact DataTable](https://primereact.org/datatable/)
- [PrimeReact Timeline](https://primereact.org/timeline/)

## Support

For issues or questions:
1. Check this documentation
2. Review component source code
3. Check browser console for errors
4. Verify API responses
5. Contact development team
