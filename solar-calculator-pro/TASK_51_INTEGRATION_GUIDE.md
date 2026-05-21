# Task 51: Product Attributes Management - Integration Guide

## Overview

This guide explains how to integrate the Product Attributes Management system into your application.

## Quick Start

### 1. Import the Component

```typescript
import { ProductAttributeManager } from './components/products';

// Use in your admin panel or product management page
<ProductAttributeManager />
```

### 2. Add to Admin Panel

If you have an admin panel with tabs, add the attribute manager:

```typescript
import { TabView, TabPanel } from 'primereact/tabview';
import { ProductAttributeManager } from './components/products';

<TabView>
  <TabPanel header="Products">
    {/* Existing product management */}
  </TabPanel>
  
  <TabPanel header="Attributes">
    <ProductAttributeManager />
  </TabPanel>
  
  <TabPanel header="Settings">
    {/* Other settings */}
  </TabPanel>
</TabView>
```

### 3. Add Route (Optional)

If you want a dedicated page for attribute management:

```typescript
// In your routes configuration
import { ProductAttributeManager } from './components/products';

{
  path: '/admin/attributes',
  element: <ProductAttributeManager />
}
```

## Integration with ProductForm

To use attributes in your product creation/editing form:

### Step 1: Fetch Attributes

```typescript
import { useEffect, useState } from 'react';
import api from '../services/api';

const [attributes, setAttributes] = useState([]);
const [groups, setGroups] = useState([]);

useEffect(() => {
  const loadAttributes = async () => {
    const attrResponse = await api.get('/products/attributes');
    setAttributes(attrResponse.data.attributes);
    
    const groupResponse = await api.get('/products/attribute-groups');
    setGroups(groupResponse.data.groups);
  };
  
  loadAttributes();
}, []);
```

### Step 2: Render Attributes by Group

```typescript
const renderAttributesByGroup = () => {
  return groups.map(group => {
    const groupAttributes = attributes.filter(
      attr => attr.group_id === group.id
    );
    
    if (groupAttributes.length === 0) return null;
    
    return (
      <Panel 
        key={group.id}
        header={group.label}
        toggleable={group.is_collapsible}
        collapsed={!group.is_expanded_by_default}
      >
        {groupAttributes.map(attr => renderAttribute(attr))}
      </Panel>
    );
  });
};
```

### Step 3: Render Individual Attributes

```typescript
const renderAttribute = (attr: ProductAttribute) => {
  switch (attr.type) {
    case 'text':
      return (
        <div className="form-field" key={attr.id}>
          <label htmlFor={attr.name}>
            {attr.label}
            {attr.required && ' *'}
            {attr.unit && ` (${attr.unit})`}
          </label>
          <InputText
            id={attr.name}
            value={formData[attr.name] || ''}
            onChange={(e) => handleChange(attr.name, e.target.value)}
            required={attr.required}
          />
        </div>
      );
      
    case 'number':
      return (
        <div className="form-field" key={attr.id}>
          <label htmlFor={attr.name}>
            {attr.label}
            {attr.required && ' *'}
            {attr.unit && ` (${attr.unit})`}
          </label>
          <InputNumber
            id={attr.name}
            value={formData[attr.name] || 0}
            onValueChange={(e) => handleChange(attr.name, e.value)}
            required={attr.required}
          />
        </div>
      );
      
    case 'boolean':
      return (
        <div className="form-field" key={attr.id}>
          <Checkbox
            inputId={attr.name}
            checked={formData[attr.name] || false}
            onChange={(e) => handleChange(attr.name, e.checked)}
          />
          <label htmlFor={attr.name}>{attr.label}</label>
        </div>
      );
      
    case 'select':
      return (
        <div className="form-field" key={attr.id}>
          <label htmlFor={attr.name}>
            {attr.label}
            {attr.required && ' *'}
          </label>
          <Dropdown
            id={attr.name}
            value={formData[attr.name]}
            options={attr.options?.map(opt => ({ label: opt, value: opt }))}
            onChange={(e) => handleChange(attr.name, e.value)}
            required={attr.required}
          />
        </div>
      );
      
    case 'multiselect':
      return (
        <div className="form-field" key={attr.id}>
          <label htmlFor={attr.name}>
            {attr.label}
            {attr.required && ' *'}
          </label>
          <MultiSelect
            id={attr.name}
            value={formData[attr.name] || []}
            options={attr.options?.map(opt => ({ label: opt, value: opt }))}
            onChange={(e) => handleChange(attr.name, e.value)}
            required={attr.required}
          />
        </div>
      );
      
    case 'date':
      return (
        <div className="form-field" key={attr.id}>
          <label htmlFor={attr.name}>
            {attr.label}
            {attr.required && ' *'}
          </label>
          <Calendar
            id={attr.name}
            value={formData[attr.name] ? new Date(formData[attr.name]) : null}
            onChange={(e) => handleChange(attr.name, e.value)}
            required={attr.required}
          />
        </div>
      );
      
    default:
      return null;
  }
};
```

## Using Templates

### Apply Template to Product Form

```typescript
const applyTemplate = async (templateId: number) => {
  try {
    // Get template
    const response = await api.get(`/products/attribute-templates/${templateId}`);
    const template = response.data.template;
    
    // Filter attributes to only those in template
    const templateAttributes = attributes.filter(
      attr => template.attributes.includes(attr.id)
    );
    
    // Initialize form with template attributes
    const initialValues = {};
    templateAttributes.forEach(attr => {
      initialValues[attr.name] = attr.default_value || null;
    });
    
    setFormData(prev => ({ ...prev, ...initialValues }));
  } catch (error) {
    console.error('Failed to apply template:', error);
  }
};
```

### Template Selector in Product Form

```typescript
<div className="form-field">
  <label>Apply Template</label>
  <Dropdown
    value={selectedTemplate}
    options={templates.map(t => ({ label: t.name, value: t.id }))}
    onChange={(e) => {
      setSelectedTemplate(e.value);
      applyTemplate(e.value);
    }}
    placeholder="Select a template"
  />
</div>
```

## Validation

### Validate Required Attributes

```typescript
const validateAttributes = () => {
  const errors = {};
  
  attributes.forEach(attr => {
    if (attr.required && !formData[attr.name]) {
      errors[attr.name] = `${attr.label} is required`;
    }
    
    // Type-specific validation
    if (attr.type === 'number' && formData[attr.name]) {
      if (attr.validation_rules?.min && formData[attr.name] < attr.validation_rules.min) {
        errors[attr.name] = `${attr.label} must be at least ${attr.validation_rules.min}`;
      }
      if (attr.validation_rules?.max && formData[attr.name] > attr.validation_rules.max) {
        errors[attr.name] = `${attr.label} must be at most ${attr.validation_rules.max}`;
      }
    }
  });
  
  return errors;
};
```

## Saving Product with Attributes

```typescript
const saveProduct = async () => {
  // Validate
  const errors = validateAttributes();
  if (Object.keys(errors).length > 0) {
    setValidationErrors(errors);
    return;
  }
  
  // Prepare data
  const productData = {
    // Standard fields
    category: formData.category,
    model_name: formData.model_name,
    brand: formData.brand,
    price_euro: formData.price_euro,
    
    // Custom attributes in specifications object
    specifications: {}
  };
  
  // Add all attribute values to specifications
  attributes.forEach(attr => {
    if (formData[attr.name] !== undefined && formData[attr.name] !== null) {
      productData.specifications[attr.name] = formData[attr.name];
    }
  });
  
  // Save
  try {
    await api.post('/products', productData);
    toast.success('Product created successfully');
  } catch (error) {
    toast.error('Failed to create product');
  }
};
```

## Displaying Attributes in Product View

### Grouped Display

```typescript
const ProductDetails: React.FC<{ product: Product }> = ({ product }) => {
  const [attributes, setAttributes] = useState([]);
  const [groups, setGroups] = useState([]);
  
  useEffect(() => {
    loadAttributes();
  }, []);
  
  const renderProductAttributes = () => {
    return groups.map(group => {
      const groupAttributes = attributes.filter(
        attr => attr.group_id === group.id
      );
      
      const hasValues = groupAttributes.some(
        attr => product.specifications?.[attr.name] !== undefined
      );
      
      if (!hasValues) return null;
      
      return (
        <Panel key={group.id} header={group.label}>
          <div className="attribute-grid">
            {groupAttributes.map(attr => {
              const value = product.specifications?.[attr.name];
              if (value === undefined || value === null) return null;
              
              return (
                <div key={attr.id} className="attribute-item">
                  <span className="attribute-label">{attr.label}:</span>
                  <span className="attribute-value">
                    {formatAttributeValue(attr, value)}
                  </span>
                </div>
              );
            })}
          </div>
        </Panel>
      );
    });
  };
  
  const formatAttributeValue = (attr: ProductAttribute, value: any) => {
    switch (attr.type) {
      case 'boolean':
        return value ? 'Yes' : 'No';
      case 'number':
        return attr.unit ? `${value} ${attr.unit}` : value;
      case 'date':
        return new Date(value).toLocaleDateString();
      case 'multiselect':
        return Array.isArray(value) ? value.join(', ') : value;
      default:
        return value;
    }
  };
  
  return (
    <div className="product-details">
      <h2>{product.model_name}</h2>
      {renderProductAttributes()}
    </div>
  );
};
```

## Backend Integration

### Database Schema (Example)

```sql
-- Attributes table
CREATE TABLE product_attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    type TEXT NOT NULL,
    required BOOLEAN DEFAULT 0,
    default_value TEXT,
    options TEXT,  -- JSON array
    validation_rules TEXT,  -- JSON object
    group_id INTEGER,
    description TEXT,
    unit TEXT,
    "order" INTEGER DEFAULT 0,
    is_custom BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES attribute_groups(id)
);

-- Attribute groups table
CREATE TABLE attribute_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    description TEXT,
    "order" INTEGER DEFAULT 0,
    is_collapsible BOOLEAN DEFAULT 1,
    is_expanded_by_default BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attribute templates table
CREATE TABLE attribute_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    attributes TEXT NOT NULL,  -- JSON array of attribute IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Service Implementation

Replace the mock methods in `product_service.py` with actual database queries:

```python
def get_all_attributes(self) -> List[Dict[str, Any]]:
    """Get all product attributes"""
    query = """
        SELECT a.*, g.label as group_name
        FROM product_attributes a
        LEFT JOIN attribute_groups g ON a.group_id = g.id
        ORDER BY a.order, a.label
    """
    results = self.db.execute(query).fetchall()
    return [dict(row) for row in results]

def create_attribute(self, attribute_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new product attribute"""
    query = """
        INSERT INTO product_attributes 
        (name, label, type, required, default_value, options, 
         validation_rules, group_id, description, unit, "order", is_custom)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor = self.db.execute(query, (
        attribute_data['name'],
        attribute_data['label'],
        attribute_data['type'],
        attribute_data.get('required', False),
        attribute_data.get('default_value'),
        json.dumps(attribute_data.get('options', [])),
        json.dumps(attribute_data.get('validation_rules', {})),
        attribute_data.get('group_id'),
        attribute_data.get('description'),
        attribute_data.get('unit'),
        attribute_data.get('order', 0),
        attribute_data.get('is_custom', True)
    ))
    self.db.commit()
    
    return self.get_attribute_by_id(cursor.lastrowid)
```

## Testing

### Unit Tests

```typescript
// AttributeForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import AttributeForm from './AttributeForm';

describe('AttributeForm', () => {
  it('validates required fields', () => {
    const onSubmit = jest.fn();
    render(<AttributeForm attribute={null} groups={[]} onSubmit={onSubmit} onCancel={() => {}} />);
    
    fireEvent.click(screen.getByText('Create'));
    
    expect(screen.getByText('Name is required')).toBeInTheDocument();
    expect(screen.getByText('Label is required')).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });
  
  it('validates name format', () => {
    const onSubmit = jest.fn();
    render(<AttributeForm attribute={null} groups={[]} onSubmit={onSubmit} onCancel={() => {}} />);
    
    const nameInput = screen.getByLabelText('Name *');
    fireEvent.change(nameInput, { target: { value: 'Invalid Name' } });
    fireEvent.click(screen.getByText('Create'));
    
    expect(screen.getByText('Name must be lowercase with underscores only')).toBeInTheDocument();
  });
});
```

### Integration Tests

```typescript
// ProductAttributeManager.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import ProductAttributeManager from './ProductAttributeManager';
import api from '../../services/api';

jest.mock('../../services/api');

describe('ProductAttributeManager', () => {
  it('loads and displays attributes', async () => {
    (api.get as jest.Mock).mockResolvedValue({
      data: {
        attributes: [
          { id: 1, name: 'power_output', label: 'Power Output', type: 'number' }
        ]
      }
    });
    
    render(<ProductAttributeManager />);
    
    await waitFor(() => {
      expect(screen.getByText('Power Output')).toBeInTheDocument();
    });
  });
});
```

## Troubleshooting

### Attributes Not Showing
- Check API endpoint is accessible
- Verify data format matches interface
- Check browser console for errors

### Form Validation Issues
- Ensure validation rules are properly defined
- Check attribute type matches validation
- Verify required fields are marked correctly

### Template Not Applying
- Verify template attributes exist
- Check attribute IDs match
- Ensure category matches product category

## Support

For issues or questions:
1. Check the PRODUCT_ATTRIBUTES_QUICK_REFERENCE.md
2. Review the TASK_51_COMPLETE.md for technical details
3. Check the TASK_51_VISUAL_SUMMARY.md for UI flows

## Next Steps

1. Implement database persistence
2. Add attribute value validation rules editor
3. Create attribute usage analytics
4. Add bulk operations
5. Implement import/export functionality
