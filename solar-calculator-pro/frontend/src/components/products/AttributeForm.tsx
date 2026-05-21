/**
 * AttributeForm Component - Task 51
 * Form for creating and editing product attributes
 */

import React, { useState, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { Checkbox } from 'primereact/checkbox';
import { Button } from 'primereact/button';
import { Chips } from 'primereact/chips';
import { ProductAttribute, AttributeGroup } from './ProductAttributeManager';

interface AttributeFormProps {
  attribute: ProductAttribute | null;
  groups: AttributeGroup[];
  onSubmit: (data: Partial<ProductAttribute>) => void;
  onCancel: () => void;
}

const AttributeForm: React.FC<AttributeFormProps> = ({
  attribute,
  groups,
  onSubmit,
  onCancel
}) => {
  const [formData, setFormData] = useState<Partial<ProductAttribute>>({
    name: '',
    label: '',
    type: 'text',
    required: false,
    default_value: null,
    options: [],
    validation_rules: {},
    group_id: undefined,
    description: '',
    unit: '',
    order: 0,
    is_custom: true
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (attribute) {
      setFormData(attribute);
    }
  }, [attribute]);

  const attributeTypes = [
    { label: 'Text', value: 'text' },
    { label: 'Number', value: 'number' },
    { label: 'Boolean', value: 'boolean' },
    { label: 'Select', value: 'select' },
    { label: 'Multi-Select', value: 'multiselect' },
    { label: 'Date', value: 'date' }
  ];

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      newErrors.name = 'Name is required';
    } else if (!/^[a-z_][a-z0-9_]*$/.test(formData.name)) {
      newErrors.name = 'Name must be lowercase with underscores only';
    }

    if (!formData.label?.trim()) {
      newErrors.label = 'Label is required';
    }

    if ((formData.type === 'select' || formData.type === 'multiselect') && 
        (!formData.options || formData.options.length === 0)) {
      newErrors.options = 'Options are required for select types';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="attribute-form">
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="name">Name *</label>
          <InputText
            id="name"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g., power_output"
            className={errors.name ? 'p-invalid' : ''}
          />
          {errors.name && <small className="p-error">{errors.name}</small>}
          <small>Lowercase with underscores only</small>
        </div>

        <div className="form-field">
          <label htmlFor="label">Label *</label>
          <InputText
            id="label"
            value={formData.label}
            onChange={(e) => handleChange('label', e.target.value)}
            placeholder="e.g., Power Output"
            className={errors.label ? 'p-invalid' : ''}
          />
          {errors.label && <small className="p-error">{errors.label}</small>}
        </div>

        <div className="form-field">
          <label htmlFor="type">Type *</label>
          <Dropdown
            id="type"
            value={formData.type}
            options={attributeTypes}
            onChange={(e) => handleChange('type', e.value)}
            placeholder="Select type"
          />
        </div>

        <div className="form-field">
          <label htmlFor="group">Group</label>
          <Dropdown
            id="group"
            value={formData.group_id}
            options={[
              { label: 'No Group', value: undefined },
              ...groups.map(g => ({ label: g.label, value: g.id }))
            ]}
            onChange={(e) => handleChange('group_id', e.value)}
            placeholder="Select group"
          />
        </div>

        <div className="form-field">
          <label htmlFor="unit">Unit</label>
          <InputText
            id="unit"
            value={formData.unit || ''}
            onChange={(e) => handleChange('unit', e.target.value)}
            placeholder="e.g., kW, %, °C"
          />
        </div>

        <div className="form-field">
          <label htmlFor="order">Display Order</label>
          <InputNumber
            id="order"
            value={formData.order}
            onValueChange={(e) => handleChange('order', e.value)}
            min={0}
          />
        </div>
      </div>

      <div className="form-field full-width">
        <label htmlFor="description">Description</label>
        <InputTextarea
          id="description"
          value={formData.description || ''}
          onChange={(e) => handleChange('description', e.target.value)}
          rows={3}
          placeholder="Describe this attribute..."
        />
      </div>

      {(formData.type === 'select' || formData.type === 'multiselect') && (
        <div className="form-field full-width">
          <label htmlFor="options">Options *</label>
          <Chips
            id="options"
            value={formData.options || []}
            onChange={(e) => handleChange('options', e.value)}
            placeholder="Type option and press Enter"
            className={errors.options ? 'p-invalid' : ''}
          />
          {errors.options && <small className="p-error">{errors.options}</small>}
          <small>Press Enter after each option</small>
        </div>
      )}

      <div className="form-field full-width">
        <div className="checkbox-group">
          <div className="checkbox-item">
            <Checkbox
              inputId="required"
              checked={formData.required}
              onChange={(e) => handleChange('required', e.checked)}
            />
            <label htmlFor="required">Required Field</label>
          </div>

          <div className="checkbox-item">
            <Checkbox
              inputId="is_custom"
              checked={formData.is_custom}
              onChange={(e) => handleChange('is_custom', e.checked)}
            />
            <label htmlFor="is_custom">Custom Attribute</label>
          </div>
        </div>
      </div>

      <div className="form-actions">
        <Button
          type="button"
          label="Cancel"
          icon="pi pi-times"
          className="p-button-text"
          onClick={onCancel}
        />
        <Button
          type="submit"
          label={attribute ? 'Update' : 'Create'}
          icon="pi pi-check"
          className="p-button-success"
        />
      </div>
    </form>
  );
};

export default AttributeForm;
