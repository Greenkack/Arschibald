# Product Management - Quick Reference Guide

## Overview
Complete product management system with CRUD operations, bulk import, and advanced features.

## Access
**URL:** `/products/manage`

## Key Features

### 1. Create Product
```typescript
// Open create dialog
<Button onClick={() => setShowCreateDialog(true)} />

// Form fields
- Category (required, dropdown)
- Model Name (required, text)
- Brand (optional, text)
- Price (optional, currency €)
- Description (optional, textarea)
- Image (optional, file upload)
- Specifications (optional, key-value pairs)
```

### 2. Edit Product
```typescript
// Click edit button on any product row
// Same form as create, pre-filled with existing data
```

### 3. Delete Product
```typescript
// Single delete: Click trash icon
// Bulk delete: Select multiple, click "Delete (n)" button
// Both show confirmation dialog
```

### 4. Bulk Import
```typescript
// Click "Bulk Import" button
// Upload Excel (.xlsx, .xls) or CSV file
// Preview and validate data
// Import valid rows

// Template format:
category | model_name | brand | price_euro | description
```

### 5. Search & Filter
```typescript
// Global search: Type in search box (searches all fields)
// Category filter: Select from dropdown
// Column filters: Use filter inputs in table headers
```

## Component Usage

### ProductForm
```typescript
import ProductForm from '@components/products/ProductForm';

<ProductForm
  product={existingProduct} // Optional, for edit mode
  categories={['Solar Module', 'Inverter', 'Battery']}
  onSubmit={async (data) => {
    await api.post('/products', data);
  }}
  onCancel={() => setShowDialog(false)}
  loading={false}
/>
```

### ProductBulkImport
```typescript
import ProductBulkImport from '@components/products/ProductBulkImport';

<ProductBulkImport
  onImport={async (products) => {
    await Promise.all(
      products.map(p => api.post('/products', p))
    );
  }}
  onCancel={() => setShowDialog(false)}
/>
```

## API Endpoints

```typescript
// List products
GET /products
Response: { products: Product[] }

// Get categories
GET /products/categories/list
Response: { categories: string[] }

// Create product
POST /products
Body: ProductFormData
Response: { product: Product }

// Update product
PUT /products/:id
Body: ProductFormData
Response: { product: Product }

// Delete product
DELETE /products/:id
Response: { success: boolean }

// Search products
POST /products/search
Body: { query: string, ...filters }
Response: { products: Product[] }
```

## Data Types

```typescript
interface Product {
  id: number;
  category: string;
  model_name: string;
  brand?: string;
  price_euro?: number;
  description?: string;
  specifications?: Record<string, any>;
  image_url?: string;
  company_id?: number;
  created_at?: string;
  updated_at?: string;
}

interface ProductFormData {
  id?: number;
  category: string;
  model_name: string;
  brand?: string;
  price_euro?: number;
  description?: string;
  specifications?: Record<string, any>;
  image_url?: string;
  company_id?: number;
}
```

## Validation Rules

### Required Fields:
- `category` - Must be selected from dropdown
- `model_name` - Must not be empty

### Optional Fields:
- `brand` - Any string
- `price_euro` - Must be positive number if provided
- `description` - Any text
- `specifications` - Key-value pairs
- `image_url` - Valid image file (JPG, PNG, GIF, max 5MB)

## Specifications Editor

```typescript
// Add specification
1. Enter key (e.g., "Power")
2. Enter value (e.g., "400W")
3. Click "Add" button

// Remove specification
Click X button next to specification

// Specifications are stored as JSON object:
{
  "Power": "400W",
  "Efficiency": "21.5%",
  "Dimensions": "1722x1134x30mm"
}
```

## Image Upload

```typescript
// Supported formats: JPG, PNG, GIF
// Maximum size: 5MB
// Preview shown before upload
// Image stored as URL in database
```

## Bulk Import Format

### Excel/CSV Template:
```
category,model_name,brand,price_euro,description
Solar Module,Example 400W,Brand A,250.00,High efficiency module
Inverter,Example 5kW,Brand B,1200.00,String inverter
Battery,Example 10kWh,Brand C,5000.00,Lithium battery
```

### Validation:
- ✅ Valid: All required fields present, price is positive
- ❌ Invalid: Missing category or model_name, negative price
- Rows with errors are highlighted and not imported

## Keyboard Shortcuts

- `Ctrl/Cmd + N` - New product (when focused)
- `Ctrl/Cmd + S` - Save form (when in form)
- `Esc` - Close dialog
- `Enter` - Submit form (when in form)

## Responsive Behavior

### Desktop (>1024px):
- Full toolbar with all buttons
- Side-by-side filters
- Wide table with all columns

### Tablet (768px-1024px):
- Stacked toolbar
- Full-width filters
- Scrollable table

### Mobile (<768px):
- Vertical toolbar
- Full-width buttons
- Simplified table view
- Touch-friendly controls

## Error Handling

### Network Errors:
- Toast notification shown
- Form remains open for retry
- Data preserved

### Validation Errors:
- Inline error messages
- Red border on invalid fields
- Submit button disabled until valid

### Bulk Import Errors:
- Row-by-row error display
- Invalid rows not imported
- Success/failure statistics shown

## Performance Tips

1. **Large Datasets**: Use pagination (20 rows default)
2. **Search**: Debounced for better performance
3. **Images**: Compressed before upload
4. **Bulk Import**: Process in batches of 100

## Common Tasks

### Add New Product:
1. Click "New Product"
2. Fill required fields (category, model name)
3. Add optional fields as needed
4. Upload image if available
5. Add specifications
6. Click "Create Product"

### Edit Product:
1. Find product in table
2. Click edit icon (pencil)
3. Modify fields
4. Click "Update Product"

### Import Products:
1. Click "Bulk Import"
2. Download template (optional)
3. Fill template with data
4. Upload file
5. Review validation
6. Click "Import X Products"

### Delete Products:
1. Select products (checkboxes)
2. Click "Delete (n)"
3. Confirm deletion

## Troubleshooting

### Image not uploading:
- Check file size (<5MB)
- Check file format (JPG, PNG, GIF)
- Check network connection

### Import failing:
- Verify template format
- Check required fields
- Validate price values
- Check file encoding (UTF-8)

### Search not working:
- Clear filters
- Check spelling
- Try different search terms

## Best Practices

1. **Always fill required fields** (marked with *)
2. **Use descriptive model names** for easy searching
3. **Add specifications** for better product details
4. **Upload images** for visual identification
5. **Use bulk import** for multiple products
6. **Regular backups** before bulk operations
7. **Test import** with small file first

## Support

For issues or questions:
1. Check this guide
2. Review error messages
3. Check browser console
4. Contact development team
