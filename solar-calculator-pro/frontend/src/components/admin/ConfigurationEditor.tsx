/**
 * Configuration Editor Component
 * 
 * Form for creating and editing configurations with validation
 */

import React, { useState, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { Checkbox } from 'primereact/checkbox';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { Divider } from 'primereact/divider';
import { TabView, TabPanel } from 'primereact/tabview';
import { InputNumber } from 'primereact/inputnumber';
import { Editor } from 'primereact/editor';

interface Configuration {
  id?: number;
  key: string;
  value: string;
  value_type: string;
  description: string;
  category: string;
  namespace: string;
  parent_id?: number;
  validation_schema?: any;
  is_required: boolean;
  default_value?: string;
  is_encrypted: boolean;
  is_sensitive: boolean;
}

interface ConfigurationEditorProps {
  configuration: Configuration | null;
  onSave: (config: Configuration) => void;
  onCancel: () => void;
}

const ConfigurationEditor: React.FC<ConfigurationEditorProps> = ({
  configuration,
  onSave,
  onCancel
}) => {
  const [formData, setFormData] = useState<Configuration>({
    key: '',
    value: '',
    value_type: 'string',
    description: '',
    category: 'user',
    namespace: 'global',
    is_required: false,
    is_encrypted: false,
    is_sensitive: false
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [validationResult, setValidationResult] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  
  // Value type options
  const valueTypeOptions = [
    { label: 'String', value: 'string' },
    { label: 'Number', value: 'number' },
    { label: 'Boolean', value: 'boolean' },
    { label: 'JSON', value: 'json' },
    { label: 'Array', value: 'array' }
  ];
  
  // Category options
  const categoryOptions = [
    { label: 'System', value: 'system' },
    { label: 'User', value: 'user' },
    { label: 'Module', value: 'module' },
    { label: 'Feature', value: 'feature' }
  ];
  
  // Namespace options
  const namespaceOptions = [
    { label: 'Global', value: 'global' },
    { label: 'Solar', value: 'solar' },
    { label: 'Heat Pump', value: 'heatpump' },
    { label: 'PDF', value: 'pdf' },
    { label: 'CRM', value: 'crm' },
    { label: 'Pricing', value: 'pricing' },
    { label: 'Visualization', value: 'visualization' }
  ];
  
  // Load configuration data
  useEffect(() => {
    if (configuration) {
      setFormData(configuration);
    }
  }, [configuration]);
  
  // Handle field change
  const handleChange = (field: keyof Configuration, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };
  
  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.key.trim()) {
      newErrors.key = 'Key is required';
    } else if (!/^[a-zA-Z0-9._-]+$/.test(formData.key)) {
      newErrors.key = 'Key can only contain alphanumeric characters, dots, underscores, and hyphens';
    }
    
    if (!formData.namespace.trim()) {
      newErrors.namespace = 'Namespace is required';
    }
    
    if (!formData.category) {
      newErrors.category = 'Category is required';
    }
    
    // Validate value based on type
    if (formData.value) {
      try {
        switch (formData.value_type) {
          case 'number':
            if (isNaN(Number(formData.value))) {
              newErrors.value = 'Value must be a valid number';
            }
            break;
          case 'boolean':
            if (!['true', 'false', '1', '0', 'yes', 'no'].includes(formData.value.toLowerCase())) {
              newErrors.value = 'Value must be a valid boolean (true/false, yes/no, 1/0)';
            }
            break;
          case 'json':
          case 'array':
            try {
              JSON.parse(formData.value);
            } catch {
              newErrors.value = 'Value must be valid JSON';
            }
            break;
        }
      } catch (error) {
        newErrors.value = 'Invalid value format';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Handle save
  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }
    
    setSaving(true);
    try {
      const url = configuration
        ? `/api/v1/configurations/${configuration.id}`
        : '/api/v1/configurations';
      
      const method = configuration ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const savedConfig = await response.json();
        onSave(savedConfig);
      } else {
        const error = await response.json();
        setErrors({ general: error.detail || 'Failed to save configuration' });
      }
    } catch (error) {
      setErrors({ general: 'Network error occurred' });
    } finally {
      setSaving(false);
    }
  };
  
  // Validate value against schema
  const handleValidate = async () => {
    if (!formData.validation_schema || !formData.value) {
      return;
    }
    
    try {
      const response = await fetch('/api/v1/configurations/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          value: formData.value,
          validation_schema: formData.validation_schema
        })
      });
      
      const result = await response.json();
      setValidationResult(result);
    } catch (error) {
      setValidationResult({
        is_valid: false,
        errors: [{ message: 'Validation failed' }]
      });
    }
  };
  
  return (
    <div className="configuration-editor">
      {errors.general && (
        <Message severity="error" text={errors.general} className="mb-3 w-full" />
      )}
      
      <TabView>
        <TabPanel header="Basic Information">
          <div className="grid grid-cols-1 gap-4">
            {/* Key */}
            <div className="field">
              <label htmlFor="key" className="block font-semibold mb-2">
                Key <span className="text-red-500">*</span>
              </label>
              <InputText
                id="key"
                value={formData.key}
                onChange={(e) => handleChange('key', e.target.value)}
                className={`w-full ${errors.key ? 'p-invalid' : ''}`}
                placeholder="e.g., app.feature.enabled"
                disabled={!!configuration}
              />
              {errors.key && <small className="p-error">{errors.key}</small>}
              <small className="block mt-1 text-gray-600">
                Unique identifier for this configuration
              </small>
            </div>
            
            {/* Namespace */}
            <div className="field">
              <label htmlFor="namespace" className="block font-semibold mb-2">
                Namespace <span className="text-red-500">*</span>
              </label>
              <Dropdown
                id="namespace"
                value={formData.namespace}
                options={namespaceOptions}
                onChange={(e) => handleChange('namespace', e.value)}
                className={`w-full ${errors.namespace ? 'p-invalid' : ''}`}
                disabled={!!configuration}
              />
              {errors.namespace && <small className="p-error">{errors.namespace}</small>}
            </div>
            
            {/* Category */}
            <div className="field">
              <label htmlFor="category" className="block font-semibold mb-2">
                Category <span className="text-red-500">*</span>
              </label>
              <Dropdown
                id="category"
                value={formData.category}
                options={categoryOptions}
                onChange={(e) => handleChange('category', e.value)}
                className={`w-full ${errors.category ? 'p-invalid' : ''}`}
              />
              {errors.category && <small className="p-error">{errors.category}</small>}
            </div>
            
            {/* Description */}
            <div className="field">
              <label htmlFor="description" className="block font-semibold mb-2">
                Description
              </label>
              <InputTextarea
                id="description"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
                className="w-full"
                placeholder="Describe what this configuration controls..."
              />
            </div>
          </div>
        </TabPanel>
        
        <TabPanel header="Value Configuration">
          <div className="grid grid-cols-1 gap-4">
            {/* Value Type */}
            <div className="field">
              <label htmlFor="value_type" className="block font-semibold mb-2">
                Value Type
              </label>
              <Dropdown
                id="value_type"
                value={formData.value_type}
                options={valueTypeOptions}
                onChange={(e) => handleChange('value_type', e.value)}
                className="w-full"
              />
            </div>
            
            {/* Value */}
            <div className="field">
              <label htmlFor="value" className="block font-semibold mb-2">
                Value
              </label>
              {formData.value_type === 'json' || formData.value_type === 'array' ? (
                <InputTextarea
                  id="value"
                  value={formData.value}
                  onChange={(e) => handleChange('value', e.target.value)}
                  rows={8}
                  className={`w-full font-mono ${errors.value ? 'p-invalid' : ''}`}
                  placeholder={formData.value_type === 'json' ? '{"key": "value"}' : '["item1", "item2"]'}
                />
              ) : (
                <InputText
                  id="value"
                  value={formData.value}
                  onChange={(e) => handleChange('value', e.target.value)}
                  className={`w-full ${errors.value ? 'p-invalid' : ''}`}
                  placeholder={`Enter ${formData.value_type} value...`}
                />
              )}
              {errors.value && <small className="p-error">{errors.value}</small>}
            </div>
            
            {/* Default Value */}
            <div className="field">
              <label htmlFor="default_value" className="block font-semibold mb-2">
                Default Value
              </label>
              <InputText
                id="default_value"
                value={formData.default_value || ''}
                onChange={(e) => handleChange('default_value', e.target.value)}
                className="w-full"
                placeholder="Default value if not set..."
              />
            </div>
            
            {/* Validation Schema */}
            <div className="field">
              <label htmlFor="validation_schema" className="block font-semibold mb-2">
                Validation Schema (JSON Schema)
              </label>
              <InputTextarea
                id="validation_schema"
                value={formData.validation_schema ? JSON.stringify(formData.validation_schema, null, 2) : ''}
                onChange={(e) => {
                  try {
                    const schema = e.target.value ? JSON.parse(e.target.value) : null;
                    handleChange('validation_schema', schema);
                  } catch {
                    // Invalid JSON, keep as is
                  }
                }}
                rows={6}
                className="w-full font-mono"
                placeholder='{"type": "string", "minLength": 1}'
              />
              <div className="flex gap-2 mt-2">
                <Button
                  label="Validate Value"
                  icon="pi pi-check"
                  size="small"
                  onClick={handleValidate}
                  disabled={!formData.validation_schema || !formData.value}
                />
              </div>
              
              {validationResult && (
                <Message
                  severity={validationResult.is_valid ? 'success' : 'error'}
                  text={validationResult.is_valid ? 'Validation passed' : `Validation failed: ${validationResult.errors[0]?.message}`}
                  className="mt-2 w-full"
                />
              )}
            </div>
          </div>
        </TabPanel>
        
        <TabPanel header="Advanced Options">
          <div className="grid grid-cols-1 gap-4">
            {/* Checkboxes */}
            <div className="field-checkbox">
              <Checkbox
                inputId="is_required"
                checked={formData.is_required}
                onChange={(e) => handleChange('is_required', e.checked)}
              />
              <label htmlFor="is_required" className="ml-2">
                Required Configuration
              </label>
            </div>
            
            <div className="field-checkbox">
              <Checkbox
                inputId="is_encrypted"
                checked={formData.is_encrypted}
                onChange={(e) => handleChange('is_encrypted', e.checked)}
              />
              <label htmlFor="is_encrypted" className="ml-2">
                Encrypt Value
              </label>
            </div>
            
            <div className="field-checkbox">
              <Checkbox
                inputId="is_sensitive"
                checked={formData.is_sensitive}
                onChange={(e) => handleChange('is_sensitive', e.checked)}
              />
              <label htmlFor="is_sensitive" className="ml-2">
                Sensitive (Hide in UI)
              </label>
            </div>
            
            <Divider />
            
            {/* Parent Configuration */}
            <div className="field">
              <label htmlFor="parent_id" className="block font-semibold mb-2">
                Parent Configuration ID
              </label>
              <InputNumber
                id="parent_id"
                value={formData.parent_id || null}
                onValueChange={(e) => handleChange('parent_id', e.value)}
                className="w-full"
                placeholder="Optional parent configuration for inheritance"
              />
              <small className="block mt-1 text-gray-600">
                Inherit values from parent configuration
              </small>
            </div>
          </div>
        </TabPanel>
      </TabView>
      
      {/* Action Buttons */}
      <div className="flex justify-end gap-2 mt-4">
        <Button
          label="Cancel"
          icon="pi pi-times"
          severity="secondary"
          onClick={onCancel}
          disabled={saving}
        />
        <Button
          label={configuration ? 'Update' : 'Create'}
          icon="pi pi-check"
          severity="success"
          onClick={handleSave}
          loading={saving}
        />
      </div>
    </div>
  );
};

export default ConfigurationEditor;
