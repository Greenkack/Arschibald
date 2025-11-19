# Customer Management - Quick Reference

## Overview

The Customer Management system provides a complete interface for managing customer data in the CRM.

## Components

### CustomerList
**Location**: `src/components/crm/CustomerList.tsx`

**Purpose**: Display and manage list of customers

**Features**:
- Paginated data table
- Search functionality
- View, Edit, Delete actions
- Responsive design

**Props**:
```typescript
interface CustomerListProps {
  onCustomerSelect?: (customer: Customer) => void;
  onCustomerEdit?: (customer: Customer) => void;
  refreshTrigger?: number;
}
```

**Usage**:
```tsx
<CustomerList
  onCustomerSelect={handleViewCustomer}
  onCustomerEdit={handleEditCustomer}
  refreshTrigger={refreshTrigger}
/>
```

### CustomerForm
**Location**: `src/components/crm/CustomerForm.tsx`

**Purpose**: Create and edit customers

**Features**:
- Form validation
- Required field checking
- Email format validation
- Organized sections

**Props**:
```typescript
interface CustomerFormProps {
  customer?: Customer | null;  // For editing
  onSave?: (customer: Customer) => void;
  onCancel?: () => void;
}
```

**Usage**:
```tsx
// Create new customer
<CustomerForm
  onSave={handleSave}
  onCancel={handleCancel}
/>

// Edit existing customer
<CustomerForm
  customer={selectedCustomer}
  onSave={handleSave}
  onCancel={handleCancel}
/>
```

### CustomerDetail
**Location**: `src/components/crm/CustomerDetail.tsx`

**Purpose**: Display detailed customer information

**Features**:
- Comprehensive information display
- Clickable contact links
- Edit functionality
- Formatted dates

**Props**:
```typescript
interface CustomerDetailProps {
  customer: Customer;
  onEdit?: () => void;
  onClose?: () => void;
}
```

**Usage**:
```tsx
<CustomerDetail
  customer={selectedCustomer}
  onEdit={handleEdit}
  onClose={handleClose}
/>
```

## Customer Data Model

```typescript
interface Customer {
  id?: number;
  first_name: string;        // Required
  last_name: string;         // Required
  company_name?: string;
  email?: string;
  phone_mobile?: string;
  phone_landline?: string;
  street?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  notes?: string;
  created_at?: string;
}
```

## API Endpoints

### List Customers
```typescript
GET /api/v1/crm/customers
Query Parameters:
  - limit: number (default: 100)
  - offset: number (default: 0)
  - search: string (optional)
```

### Get Customer
```typescript
GET /api/v1/crm/customers/{id}
```

### Create Customer
```typescript
POST /api/v1/crm/customers
Body: Customer (without id)
```

### Update Customer
```typescript
PUT /api/v1/crm/customers/{id}
Body: Partial<Customer>
```

### Delete Customer
```typescript
DELETE /api/v1/crm/customers/{id}
```

## Common Patterns

### Creating a Customer
```tsx
const handleCreate = async (customerData: Customer) => {
  try {
    const response = await api.post('/crm/customers', customerData);
    // Handle success
  } catch (error) {
    // Handle error
  }
};
```

### Updating a Customer
```tsx
const handleUpdate = async (id: number, customerData: Partial<Customer>) => {
  try {
    const response = await api.put(`/crm/customers/${id}`, customerData);
    // Handle success
  } catch (error) {
    // Handle error
  }
};
```

### Searching Customers
```tsx
const searchCustomers = async (searchTerm: string) => {
  try {
    const response = await api.get('/crm/customers', {
      params: { search: searchTerm }
    });
    // Handle results
  } catch (error) {
    // Handle error
  }
};
```

### Deleting a Customer
```tsx
const handleDelete = async (id: number) => {
  confirmDialog({
    message: 'Are you sure you want to delete this customer?',
    accept: async () => {
      try {
        await api.delete(`/crm/customers/${id}`);
        // Handle success
      } catch (error) {
        // Handle error
      }
    }
  });
};
```

## Validation Rules

### Required Fields
- `first_name`: Must not be empty
- `last_name`: Must not be empty

### Email Validation
- Must match pattern: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`

### Error Display
Errors are displayed below the respective form fields in red text.

## Styling

All components use PrimeReact components and custom CSS:
- `CustomerList.css` - List styling
- `CustomerForm.css` - Form styling
- `CustomerDetail.css` - Detail view styling
- `CRM.css` - Page styling

## Responsive Design

All components are responsive and adapt to:
- Desktop (> 768px)
- Tablet (768px - 1024px)
- Mobile (< 768px)

## User Feedback

### Toast Notifications
Used for:
- Success messages (create, update, delete)
- Error messages
- Information messages

### Confirm Dialogs
Used for:
- Delete confirmation
- Destructive actions

### Loading States
Displayed during:
- API calls
- Form submission
- Data loading

## Best Practices

1. **Always validate on client and server**
   - Client validation for UX
   - Server validation for security

2. **Handle errors gracefully**
   - Display user-friendly messages
   - Log errors for debugging

3. **Provide feedback**
   - Show loading states
   - Confirm actions
   - Display results

4. **Keep forms simple**
   - Group related fields
   - Use clear labels
   - Provide help text

5. **Make it accessible**
   - Use semantic HTML
   - Provide keyboard navigation
   - Add ARIA labels

## Troubleshooting

### Customer list not loading
- Check API endpoint is accessible
- Verify authentication token
- Check network tab for errors

### Form validation not working
- Ensure all required fields are filled
- Check email format
- Verify validation rules

### Search not returning results
- Check search term
- Verify API parameters
- Check backend search implementation

### Delete not working
- Verify customer ID
- Check permissions
- Ensure confirmation dialog is accepted

## Performance Tips

1. **Pagination**
   - Use appropriate page sizes
   - Don't load all customers at once

2. **Search**
   - Debounce search input
   - Use server-side search

3. **Caching**
   - Cache customer list
   - Invalidate on changes

4. **Lazy Loading**
   - Load details on demand
   - Use virtual scrolling for large lists

## Security Considerations

1. **Input Validation**
   - Validate all inputs
   - Sanitize user data

2. **Authentication**
   - Require authentication
   - Check permissions

3. **Data Protection**
   - Don't expose sensitive data
   - Use HTTPS

4. **SQL Injection**
   - Use parameterized queries
   - Validate input types

## Future Enhancements

- Advanced filtering
- Bulk operations
- Import/Export
- Customer tags
- Activity timeline
- Revenue tracking
- Custom fields
- Duplicate detection
