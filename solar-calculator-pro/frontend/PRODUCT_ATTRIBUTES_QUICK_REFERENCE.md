# Product Attributes Management - Quick Reference

## Overview

The Product Attributes Management system allows you to define, organize, and manage custom attributes for products. This includes creating attribute definitions, grouping them logically, and creating reusable templates.

## Key Features

### 1. Attribute Definition Interface
- Create custom product attributes with various data types
- Define validation rules and default values
- Set display order and grouping
- Mark attributes as required or optional

### 2. Attribute Value Management
- Support for multiple data types:
  - Text: Free-form text input
  - Number: Numeric values with optional units
  - Boolean: Yes/No checkboxes
  - Select: Single-choice dropdown
  - Multi-Select: Multiple-choice selection
  - Date: Date picker

### 3. Attribute Groups
- Organize attributes into logical groups
- Control group display (collapsible, expanded by default)
- Set group order for consistent display
- Add descriptions for clarity

### 4. Custom Attributes
- Create custom attributes specific to your needs
- Distinguish between standard and custom attributes
- Full CRUD operations on custom attributes

### 5. Attribute Templates
- Create reusable attribute sets for product categories
- Apply templates to quickly configure new products
- Manage templates by category
- Update templates to affect all associated products

## Component Usage

### ProductAttributeManager

Main component for managing all attribute-related functionality.

```typescript
import { ProductAttributeManager } from '../components/products';

<ProductAttributeManager />
```

### Features:
- **Attributes Tab**: View and manage all product attributes
- **Groups Tab**: Create and organize attribute groups
- **Templates Tab**: Define reusable attribute templates

## API Endpoints

### Attributes

```typescript
// Get all attributes
GET /api/v1/products/attributes

// Create attribute
POST /api/v1/products/attributes
{
  "name": "power_output",
  "label": "Power Output",
  "type": "number",
  "required": true,
  "unit": "kW",
  "group_id": 1,
  "order": 1
}

// Update attribute
PUT /api/v1/products/attributes/{id}

// Delete attribute
DELETE /api/v1/products/attributes/{id}
```

### Attribute Groups

```typescript
// Get all groups
GET /api/v1/products/attribute-groups

// Create group
POST /api/v1/products/attribute-groups
{
  "name": "technical_specs",
  "label": "Technical Specifications",
  "description": "Technical specifications and performance data",
  "order": 1,
  "is_collapsible": true,
  "is_expanded_by_default": true
}

// Update group
PUT /api/v1/products/attribute-groups/{id}

// Delete group
DELETE /api/v1/products/attribute-groups/{id}
```

### Attribute Templates

```typescript
// Get all templates
GET /api/v1/products/attribute-templates

// Create template
POST /api/v1/products/attribute-templates
{
  "name": "Solar Module Template",
  "description": "Standard attributes for solar modules",
  "category": "Solar Modules",
  "attributes": [1, 2, 3, 4]
}

// Update template
PUT /api/v1/products/attribute-templates/{id}

// Delete template
DELETE /api/v1/products/attribute-templates/{id}
```

## Attribute Types

### Text
- Free-form text input
- Optional validation rules (min/max length, regex)

### Number
- Numeric input with optional unit
- Validation: min/max values, decimal places

### Boolean
- Checkbox for yes/no values
- Default value support

### Select
- Single-choice dropdown
- Requires options array
- Supports default value

### Multi-Select
- Multiple-choice selection
- Requires options array
- Returns array of selected values

### Date
- Date picker input
- ISO 8601 format
- Optional min/max date validation

## Best Practices

### Naming Conventions
- **Attribute Names**: Use lowercase with underscores (e.g., `power_output`)
- **Labels**: Use proper capitalization (e.g., "Power Output")
- **Groups**: Descriptive names that indicate content

### Organization
1. Group related attributes together
2. Use consistent ordering within groups
3. Mark truly required fields only
4. Provide clear descriptions

### Templates
1. Create templates for each product category
2. Include all common attributes
3. Keep templates focused and specific
4. Update templates when standards change

### Custom Attributes
1. Use custom attributes for unique requirements
2. Document custom attribute purposes
3. Consider if a custom attribute should become standard
4. Review and clean up unused custom attributes

## Common Workflows

### Creating a New Attribute

1. Navigate to Attributes tab
2. Click "New Attribute"
3. Fill in required fields:
   - Name (lowercase_with_underscores)
   - Label (Display Name)
   - Type (select from dropdown)
4. Optional: Assign to a group
5. Optional: Set unit, order, validation rules
6. Click "Create"

### Creating an Attribute Group

1. Navigate to Groups tab
2. Click "New Group"
3. Fill in:
   - Name (lowercase_with_underscores)
   - Label (Display Name)
   - Description
4. Set display options:
   - Collapsible
   - Expanded by default
5. Click "Create"

### Creating an Attribute Template

1. Navigate to Templates tab
2. Click "New Template"
3. Fill in:
   - Template Name
   - Category
   - Description
4. Select attributes to include
5. Click "Create"

### Applying a Template to Products

Templates can be applied when creating or editing products to quickly populate attribute fields with the template's defined attributes.

## Troubleshooting

### Attribute Not Showing
- Check if attribute is assigned to correct group
- Verify attribute order
- Ensure attribute is not hidden by filters

### Cannot Delete Attribute
- Check if attribute is used in templates
- Verify no products are using the attribute
- Check for dependencies

### Template Not Applying
- Verify template category matches product category
- Check that all template attributes exist
- Ensure template is not corrupted

## Related Components

- **ProductForm**: Uses attributes for product creation/editing
- **ProductManagement**: Main product management interface
- **ProductCatalog**: Displays products with their attributes

## Requirements Satisfied

This implementation satisfies **Requirement 7.1** from the specification:
- ✅ Attribute definition interface
- ✅ Attribute value management
- ✅ Attribute groups
- ✅ Custom attributes
- ✅ Attribute templates
