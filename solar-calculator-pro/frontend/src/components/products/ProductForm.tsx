/**
 * ProductForm Component - Task 50
 * 
 * Form for creating and editing products with:
 * - All product fields
 * - Validation
 * - Image upload
 * - Specifications editor
 */

import React, { useState, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { InputNumber } from 'primereact/inputnumber';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { FileUpload, FileUploadHandlerEvent } from 'primereact/fileupload';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import { Divider } from 'primereact/divider';
import './ProductForm.css';

export interface ProductFormData {
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

interface ProductFormProps {
  product?: ProductFormData;
  categories: string[];
  onSubmit: (data: ProductFormData) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}

const ProductForm: React.FC<ProductFormProps> = ({
  product,
  categories,
  onSubmit,
  onCancel,
  loading = false
}) => {
  const [formData, setFormData] = useState<ProductFormData>({
    category: '',
    model_name: '',
    brand: '',
    price_euro: 0,
    description: '',
    specifications: {},
    image_url: '',
    company_id: undefined
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [specKey, setSpecKey] = useState<string>('');
  const [specValue, setSpecValue] = useState<string>('');

  useEffect(() => {
    if (product) {
      setFormData(product);
      if (product.image_url) {
        setImagePreview(product.image_url);
      }
    }
  }, [product]);

  const handleChange = (field: keyof ProductFormData, value: any) => {
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

  const handleImageSelect = (event: FileUploadHandlerEvent) => {
    const file = event.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAddSpecification = () => {
    if (specKey && specValue) {
      setFormData(prev => ({
        ...prev,
        specifications: {
          ...prev.specifications,
          [specKey]: specValue
        }
      }));
      setSpecKey('');
      setSpecValue('');
    }
  };

  const handleRemoveSpecification = (key: string) => {
    setFormData(prev => {
      const newSpecs = { ...prev.specifications };
      delete newSpecs[key];
      return { ...prev, specifications: newSpecs };
    });
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.category) {
      newErrors.category = 'Category is required';
    }

    if (!formData.model_name || formData.model_name.trim() === '') {
      newErrors.model_name = 'Model name is required';
    }

    if (formData.price_euro !== undefined && formData.price_euro < 0) {
      newErrors.price_euro = 'Price must be positive';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  const isEditMode = !!product?.id;

  return (
    <form onSubmit={handleSubmit} className="product-form">
      <div className="form-header">
        <h2>{isEditMode ? 'Edit Product' : 'Create New Product'}</h2>
      </div>

      <Panel header="Basic Information" className="form-section">
        <div className="p-fluid">
          <div className="field">
            <label htmlFor="category">Category *</label>
            <Dropdown
              id="category"
              value={formData.category}
              options={categories.map(cat => ({ label: cat, value: cat }))}
              onChange={(e) => handleChange('category', e.value)}
              placeholder="Select a category"
              disabled={loading}
              className={errors.category ? 'p-invalid' : ''}
            />
            {errors.category && <small className="p-error">{errors.category}</small>}
          </div>

          <div className="field">
            <label htmlFor="model_name">Model Name *</label>
            <InputText
              id="model_name"
              value={formData.model_name}
              onChange={(e) => handleChange('model_name', e.target.value)}
              placeholder="Enter model name"
              disabled={loading}
              className={errors.model_name ? 'p-invalid' : ''}
            />
            {errors.model_name && <small className="p-error">{errors.model_name}</small>}
          </div>

          <div className="field">
            <label htmlFor="brand">Brand</label>
            <InputText
              id="brand"
              value={formData.brand || ''}
              onChange={(e) => handleChange('brand', e.target.value)}
              placeholder="Enter brand name"
              disabled={loading}
            />
          </div>

          <div className="field">
            <label htmlFor="price_euro">Price (€)</label>
            <InputNumber
              id="price_euro"
              value={formData.price_euro}
              onValueChange={(e) => handleChange('price_euro', e.value)}
              mode="currency"
              currency="EUR"
              locale="de-DE"
              disabled={loading}
              className={errors.price_euro ? 'p-invalid' : ''}
            />
            {errors.price_euro && <small className="p-error">{errors.price_euro}</small>}
          </div>

          <div className="field">
            <label htmlFor="description">Description</label>
            <InputTextarea
              id="description"
              value={formData.description || ''}
              onChange={(e) => handleChange('description', e.target.value)}
              rows={4}
              placeholder="Enter product description"
              disabled={loading}
            />
          </div>
        </div>
      </Panel>

      <Panel header="Product Image" className="form-section">
        <div className="image-upload-section">
          {imagePreview && (
            <div className="image-preview">
              <img src={imagePreview} alt="Product preview" />
            </div>
          )}
          
          <FileUpload
            mode="basic"
            name="image"
            accept="image/*"
            maxFileSize={5000000}
            customUpload
            uploadHandler={handleImageSelect}
            auto
            chooseLabel="Choose Image"
            disabled={loading}
          />
          
          <Message 
            severity="info" 
            text="Maximum file size: 5MB. Supported formats: JPG, PNG, GIF" 
          />
        </div>
      </Panel>

      <Panel header="Specifications" className="form-section">
        <div className="specifications-editor">
          <div className="spec-input-row">
            <div className="field">
              <InputText
                value={specKey}
                onChange={(e) => setSpecKey(e.target.value)}
                placeholder="Specification name (e.g., Power)"
                disabled={loading}
              />
            </div>
            <div className="field">
              <InputText
                value={specValue}
                onChange={(e) => setSpecValue(e.target.value)}
                placeholder="Value (e.g., 400W)"
                disabled={loading}
              />
            </div>
            <Button
              type="button"
              icon="pi pi-plus"
              label="Add"
              onClick={handleAddSpecification}
              disabled={!specKey || !specValue || loading}
            />
          </div>

          {formData.specifications && Object.keys(formData.specifications).length > 0 && (
            <div className="specifications-list">
              <Divider />
              <h4>Current Specifications</h4>
              {Object.entries(formData.specifications).map(([key, value]) => (
                <div key={key} className="spec-item">
                  <span className="spec-key">{key}:</span>
                  <span className="spec-value">{String(value)}</span>
                  <Button
                    type="button"
                    icon="pi pi-times"
                    className="p-button-rounded p-button-text p-button-danger"
                    onClick={() => handleRemoveSpecification(key)}
                    disabled={loading}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </Panel>

      <div className="form-actions">
        <Button
          type="button"
          label="Cancel"
          icon="pi pi-times"
          className="p-button-secondary"
          onClick={onCancel}
          disabled={loading}
        />
        <Button
          type="submit"
          label={isEditMode ? 'Update Product' : 'Create Product'}
          icon="pi pi-check"
          loading={loading}
        />
      </div>
    </form>
  );
};

export default ProductForm;
