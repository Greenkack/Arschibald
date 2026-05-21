/**
 * TemplateForm Component - Task 51
 * Form for creating and editing attribute templates
 */

import React, { useState, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Button } from 'primereact/button';
import { MultiSelect } from 'primereact/multiselect';
import { ProductAttribute, AttributeTemplate } from './ProductAttributeManager';

interface TemplateFormProps {
  template: AttributeTemplate | null;
  attributes: ProductAttribute[];
  onSubmit: (data: Partial<AttributeTemplate>) => void;
  onCancel: () => void;
}

const TemplateForm: React.FC<TemplateFormProps> = ({
  template,
  attributes,
  onSubmit,
  onCancel
}) => {
  const [formData, setFormData] = useState<Partial<AttributeTemplate>>({
    name: '',
    description: '',
    category: '',
    attributes: []
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (template) {
      setFormData(template);
    }
  }, [template]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.category?.trim()) {
      newErrors.category = 'Category is required';
    }

    if (!formData.attributes || formData.attributes.length === 0) {
      newErrors.attributes = 'At least one attribute is required';
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

  const attributeOptions = attributes.map(attr => ({
    label: `${attr.label} (${attr.type})`,
    value: attr.id
  }));

  return (
    <form onSubmit={handleSubmit} className="template-form">
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="name">Template Name *</label>
          <InputText
            id="name"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g., Solar Module Template"
            className={errors.name ? 'p-invalid' : ''}
          />
          {errors.name && <small className="p-error">{errors.name}</small>}
        </div>

        <div className="form-field">
          <label htmlFor="category">Category *</label>
          <InputText
            id="category"
            value={formData.category}
            onChange={(e) => handleChange('category', e.target.value)}
            placeholder="e.g., Solar Modules"
            className={errors.category ? 'p-invalid' : ''}
          />
          {errors.category && <small className="p-error">{errors.category}</small>}
        </div>
      </div>

      <div className="form-field full-width">
        <label htmlFor="description">Description</label>
        <InputTextarea
          id="description"
          value={formData.description || ''}
          onChange={(e) => handleChange('description', e.target.value)}
          rows={3}
          placeholder="Describe this template..."
        />
      </div>

      <div className="form-field full-width">
        <label htmlFor="attributes">Attributes *</label>
        <MultiSelect
          id="attributes"
          value={formData.attributes}
          options={attributeOptions}
          onChange={(e) => handleChange('attributes', e.value)}
          placeholder="Select attributes"
          display="chip"
          filter
          className={errors.attributes ? 'p-invalid' : ''}
        />
        {errors.attributes && <small className="p-error">{errors.attributes}</small>}
        <small>Select the attributes to include in this template</small>
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
          label={template ? 'Update' : 'Create'}
          icon="pi pi-check"
          className="p-button-success"
        />
      </div>
    </form>
  );
};

export default TemplateForm;
