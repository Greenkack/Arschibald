/**
 * Customer Form Component
 * 
 * Form for creating and editing customers
 */

import React, { useState, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './CustomerForm.css';

interface Customer {
  id?: number;
  first_name: string;
  last_name: string;
  company_name?: string;
  email?: string;
  phone_mobile?: string;
  phone_landline?: string;
  street?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  notes?: string;
}

interface CustomerFormProps {
  customer?: Customer | null;
  onSave?: (customer: Customer) => void;
  onCancel?: () => void;
}

const CustomerForm: React.FC<CustomerFormProps> = ({
  customer,
  onSave,
  onCancel
}) => {
  const [formData, setFormData] = useState<Customer>({
    first_name: '',
    last_name: '',
    company_name: '',
    email: '',
    phone_mobile: '',
    phone_landline: '',
    street: '',
    city: '',
    postal_code: '',
    country: 'Deutschland',
    notes: ''
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const toast = React.useRef<Toast>(null);

  // Load customer data if editing
  useEffect(() => {
    if (customer) {
      setFormData({
        ...customer,
        company_name: customer.company_name || '',
        email: customer.email || '',
        phone_mobile: customer.phone_mobile || '',
        phone_landline: customer.phone_landline || '',
        street: customer.street || '',
        city: customer.city || '',
        postal_code: customer.postal_code || '',
        country: customer.country || 'Deutschland',
        notes: customer.notes || ''
      });
    }
  }, [customer]);

  // Handle input change
  const handleChange = (field: keyof Customer, value: string) => {
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

    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required';
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      let response;
      if (customer?.id) {
        // Update existing customer
        response = await api.put(`/crm/customers/${customer.id}`, formData);
      } else {
        // Create new customer
        response = await api.post('/crm/customers', formData);
      }

      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: customer?.id ? 'Customer updated successfully' : 'Customer created successfully',
        life: 3000
      });

      if (onSave) {
        onSave(response.data);
      }
    } catch (error: any) {
      console.error('Error saving customer:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.error?.message || 'Failed to save customer',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="customer-form">
      <Toast ref={toast} />
      
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {/* Personal Information */}
          <div className="form-section">
            <h3>Personal Information</h3>
            
            <div className="form-row">
              <div className="form-field">
                <label htmlFor="first_name">First Name *</label>
                <InputText
                  id="first_name"
                  value={formData.first_name}
                  onChange={(e) => handleChange('first_name', e.target.value)}
                  className={errors.first_name ? 'p-invalid' : ''}
                />
                {errors.first_name && <small className="p-error">{errors.first_name}</small>}
              </div>

              <div className="form-field">
                <label htmlFor="last_name">Last Name *</label>
                <InputText
                  id="last_name"
                  value={formData.last_name}
                  onChange={(e) => handleChange('last_name', e.target.value)}
                  className={errors.last_name ? 'p-invalid' : ''}
                />
                {errors.last_name && <small className="p-error">{errors.last_name}</small>}
              </div>
            </div>

            <div className="form-field">
              <label htmlFor="company_name">Company Name</label>
              <InputText
                id="company_name"
                value={formData.company_name}
                onChange={(e) => handleChange('company_name', e.target.value)}
              />
            </div>
          </div>

          {/* Contact Information */}
          <div className="form-section">
            <h3>Contact Information</h3>
            
            <div className="form-field">
              <label htmlFor="email">Email</label>
              <InputText
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                className={errors.email ? 'p-invalid' : ''}
              />
              {errors.email && <small className="p-error">{errors.email}</small>}
            </div>

            <div className="form-row">
              <div className="form-field">
                <label htmlFor="phone_mobile">Mobile Phone</label>
                <InputText
                  id="phone_mobile"
                  value={formData.phone_mobile}
                  onChange={(e) => handleChange('phone_mobile', e.target.value)}
                />
              </div>

              <div className="form-field">
                <label htmlFor="phone_landline">Landline Phone</label>
                <InputText
                  id="phone_landline"
                  value={formData.phone_landline}
                  onChange={(e) => handleChange('phone_landline', e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Address Information */}
          <div className="form-section">
            <h3>Address</h3>
            
            <div className="form-field">
              <label htmlFor="street">Street</label>
              <InputText
                id="street"
                value={formData.street}
                onChange={(e) => handleChange('street', e.target.value)}
              />
            </div>

            <div className="form-row">
              <div className="form-field">
                <label htmlFor="postal_code">Postal Code</label>
                <InputText
                  id="postal_code"
                  value={formData.postal_code}
                  onChange={(e) => handleChange('postal_code', e.target.value)}
                />
              </div>

              <div className="form-field">
                <label htmlFor="city">City</label>
                <InputText
                  id="city"
                  value={formData.city}
                  onChange={(e) => handleChange('city', e.target.value)}
                />
              </div>
            </div>

            <div className="form-field">
              <label htmlFor="country">Country</label>
              <InputText
                id="country"
                value={formData.country}
                onChange={(e) => handleChange('country', e.target.value)}
              />
            </div>
          </div>

          {/* Notes */}
          <div className="form-section">
            <h3>Notes</h3>
            
            <div className="form-field">
              <label htmlFor="notes">Additional Notes</label>
              <InputTextarea
                id="notes"
                value={formData.notes}
                onChange={(e) => handleChange('notes', e.target.value)}
                rows={4}
                autoResize
              />
            </div>
          </div>
        </div>

        {/* Form Actions */}
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
            label={customer?.id ? 'Update Customer' : 'Create Customer'}
            icon="pi pi-check"
            loading={loading}
          />
        </div>
      </form>
    </div>
  );
};

export default CustomerForm;
