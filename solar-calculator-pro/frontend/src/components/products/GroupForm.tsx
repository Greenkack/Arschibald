/**
 * GroupForm Component - Task 51
 * Form for creating and editing attribute groups
 */

import React, { useState, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { InputNumber } from 'primereact/inputnumber';
import { Checkbox } from 'primereact/checkbox';
import { Button } from 'primereact/button';
import { AttributeGroup } from './ProductAttributeManager';

interface GroupFormProps {
  group: AttributeGroup | null;
  onSubmit: (data: Partial<AttributeGroup>) => void;
  onCancel: () => void;
}

const GroupForm: React.FC<GroupFormProps> = ({ group, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<Partial<AttributeGroup>>({
    name: '',
    label: '',
    description: '',
    order: 0,
    is_collapsible: true,
    is_expanded_by_default: true
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (group) {
      setFormData(group);
    }
  }, [group]);

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
    <form onSubmit={handleSubmit} className="group-form">
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="name">Name *</label>
          <InputText
            id="name"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g., technical_specs"
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
            placeholder="e.g., Technical Specifications"
            className={errors.label ? 'p-invalid' : ''}
          />
          {errors.label && <small className="p-error">{errors.label}</small>}
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
          placeholder="Describe this group..."
        />
      </div>

      <div className="form-field full-width">
        <div className="checkbox-group">
          <div className="checkbox-item">
            <Checkbox
              inputId="is_collapsible"
              checked={formData.is_collapsible}
              onChange={(e) => handleChange('is_collapsible', e.checked)}
            />
            <label htmlFor="is_collapsible">Collapsible</label>
          </div>

          <div className="checkbox-item">
            <Checkbox
              inputId="is_expanded_by_default"
              checked={formData.is_expanded_by_default}
              onChange={(e) => handleChange('is_expanded_by_default', e.checked)}
              disabled={!formData.is_collapsible}
            />
            <label htmlFor="is_expanded_by_default">Expanded by Default</label>
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
          label={group ? 'Update' : 'Create'}
          icon="pi pi-check"
          className="p-button-success"
        />
      </div>
    </form>
  );
};

export default GroupForm;
