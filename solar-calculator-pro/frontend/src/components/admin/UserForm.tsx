/**
 * User Form Component
 * 
 * Form for creating and editing users
 */

import React, { useState, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import { Password } from 'primereact/password';
import api from '../../services/api';
import './UserForm.css';

interface User {
  id?: number;
  username: string;
  email: string;
  password?: string;
  first_name: string;
  last_name: string;
  role: string;
  status: string;
  phone?: string;
  department?: string;
}

interface UserFormProps {
  visible: boolean;
  user: User | null;
  onHide: () => void;
  onSuccess: () => void;
}

const UserForm: React.FC<UserFormProps> = ({ visible, user, onHide, onSuccess }) => {
  const [formData, setFormData] = useState<User>({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'user',
    status: 'active',
    phone: '',
    department: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const toast = React.useRef<Toast>(null);

  const roles = [
    { label: 'Super Admin', value: 'super_admin' },
    { label: 'Admin', value: 'admin' },
    { label: 'Manager', value: 'manager' },
    { label: 'User', value: 'user' },
    { label: 'Viewer', value: 'viewer' }
  ];

  const statuses = [
    { label: 'Active', value: 'active' },
    { label: 'Inactive', value: 'inactive' },
    { label: 'Suspended', value: 'suspended' },
    { label: 'Pending', value: 'pending' }
  ];

  useEffect(() => {
    if (user) {
      setFormData({
        ...user,
        password: '' // Don't populate password for editing
      });
    } else {
      setFormData({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        role: 'user',
        status: 'active',
        phone: '',
        department: ''
      });
    }
    setErrors({});
  }, [user, visible]);

  const handleChange = (field: keyof User, value: any) => {
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

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!user && !formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password && formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) {
      return;
    }

    setLoading(true);
    try {
      if (user?.id) {
        // Update existing user
        const updateData: any = {
          email: formData.email,
          first_name: formData.first_name,
          last_name: formData.last_name,
          role: formData.role,
          status: formData.status,
          phone: formData.phone || null,
          department: formData.department || null
        };

        await api.put(`/api/v1/users/${user.id}`, updateData);
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'User updated successfully',
          life: 3000
        });
      } else {
        // Create new user
        await api.post('/api/v1/users/', formData);
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'User created successfully',
          life: 3000
        });
      }

      onSuccess();
      onHide();
    } catch (error: any) {
      const detail = error.response?.data?.detail || 'Failed to save user';
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: typeof detail === 'string' ? detail : JSON.stringify(detail),
        life: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  const footer = (
    <div className="form-footer">
      <Button
        label="Cancel"
        icon="pi pi-times"
        onClick={onHide}
        className="p-button-text"
        disabled={loading}
      />
      <Button
        label={user ? 'Update' : 'Create'}
        icon="pi pi-check"
        onClick={handleSubmit}
        loading={loading}
      />
    </div>
  );

  return (
    <>
      <Toast ref={toast} />
      <Dialog
        visible={visible}
        onHide={onHide}
        header={user ? 'Edit User' : 'Create New User'}
        footer={footer}
        className="user-form-dialog"
        style={{ width: '600px' }}
        modal
      >
        <div className="user-form">
          <div className="form-row">
            <div className="form-field">
              <label htmlFor="username">Username *</label>
              <InputText
                id="username"
                value={formData.username}
                onChange={(e) => handleChange('username', e.target.value)}
                disabled={!!user} // Can't change username when editing
                className={errors.username ? 'p-invalid' : ''}
              />
              {errors.username && <small className="p-error">{errors.username}</small>}
            </div>

            <div className="form-field">
              <label htmlFor="email">Email *</label>
              <InputText
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                className={errors.email ? 'p-invalid' : ''}
              />
              {errors.email && <small className="p-error">{errors.email}</small>}
            </div>
          </div>

          {!user && (
            <div className="form-field">
              <label htmlFor="password">Password *</label>
              <Password
                id="password"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                toggleMask
                feedback
                className={errors.password ? 'p-invalid' : ''}
              />
              {errors.password && <small className="p-error">{errors.password}</small>}
            </div>
          )}

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

          <div className="form-row">
            <div className="form-field">
              <label htmlFor="role">Role *</label>
              <Dropdown
                id="role"
                value={formData.role}
                options={roles}
                onChange={(e) => handleChange('role', e.value)}
              />
            </div>

            <div className="form-field">
              <label htmlFor="status">Status *</label>
              <Dropdown
                id="status"
                value={formData.status}
                options={statuses}
                onChange={(e) => handleChange('status', e.value)}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-field">
              <label htmlFor="phone">Phone</label>
              <InputText
                id="phone"
                value={formData.phone || ''}
                onChange={(e) => handleChange('phone', e.target.value)}
              />
            </div>

            <div className="form-field">
              <label htmlFor="department">Department</label>
              <InputText
                id="department"
                value={formData.department || ''}
                onChange={(e) => handleChange('department', e.target.value)}
              />
            </div>
          </div>
        </div>
      </Dialog>
    </>
  );
};

export default UserForm;
