/**
 * User Profile Page
 * 
 * Display and edit user profile information
 */

import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Avatar } from 'primereact/avatar';
import { Divider } from 'primereact/divider';
import { Message } from 'primereact/message';
import { useAuth } from '@hooks/useAuth';
import './Profile.css';

interface ProfileFormData {
  username: string;
  email: string;
}

interface ProfileFormErrors {
  username?: string;
  email?: string;
}

const Profile: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [formData, setFormData] = useState<ProfileFormData>({
    username: user?.username || '',
    email: user?.email || '',
  });

  const [formErrors, setFormErrors] = useState<ProfileFormErrors>({});

  /**
   * Validate email format
   */
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  /**
   * Validate form field
   */
  const validateField = (name: keyof ProfileFormData, value: string): string | undefined => {
    switch (name) {
      case 'username':
        if (!value.trim()) {
          return 'Username is required';
        }
        if (value.length < 3) {
          return 'Username must be at least 3 characters';
        }
        break;
      case 'email':
        if (!value.trim()) {
          return 'Email is required';
        }
        if (!validateEmail(value)) {
          return 'Please enter a valid email address';
        }
        break;
    }
    return undefined;
  };

  /**
   * Validate entire form
   */
  const validateForm = (): boolean => {
    const errors: ProfileFormErrors = {};
    
    const usernameError = validateField('username', formData.username);
    if (usernameError) errors.username = usernameError;
    
    const emailError = validateField('email', formData.email);
    if (emailError) errors.email = emailError;

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle input change
   */
  const handleChange = (field: keyof ProfileFormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    // Clear error for this field
    const error = validateField(field, value);
    setFormErrors((prev) => ({
      ...prev,
      [field]: error,
    }));

    // Clear messages
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  /**
   * Handle edit button click
   */
  const handleEdit = () => {
    setIsEditing(true);
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  /**
   * Handle cancel button click
   */
  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      username: user?.username || '',
      email: user?.email || '',
    });
    setFormErrors({});
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  /**
   * Handle save button click
   */
  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    setIsSaving(true);
    setSuccessMessage(null);
    setErrorMessage(null);

    try {
      // TODO: Call API to update profile
      // await api.put('/auth/profile', formData);
      
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Refresh user data
      await refreshUser();

      setSuccessMessage('Profile updated successfully');
      setIsEditing(false);
    } catch (error: any) {
      setErrorMessage(error.message || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Get user initials for avatar
   */
  const getUserInitials = (): string => {
    if (!user?.username) return '?';
    return user.username.substring(0, 2).toUpperCase();
  };

  /**
   * Format date
   */
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (!user) {
    return (
      <div className="profile-container">
        <Card>
          <Message severity="warn" text="No user data available" />
        </Card>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <Card className="profile-card">
        <div className="profile-header">
          <Avatar
            label={getUserInitials()}
            size="xlarge"
            shape="circle"
            className="profile-avatar"
          />
          <div className="profile-header-info">
            <h2>{user.username}</h2>
            <p className="profile-role">{user.role}</p>
          </div>
        </div>

        <Divider />

        {/* Success/Error Messages */}
        {successMessage && (
          <Message severity="success" text={successMessage} className="profile-message" />
        )}
        {errorMessage && (
          <Message severity="error" text={errorMessage} className="profile-message" />
        )}

        {/* Profile Information */}
        <div className="profile-form">
          <div className="p-field">
            <label htmlFor="username" className="p-label">
              Username
            </label>
            <InputText
              id="username"
              value={formData.username}
              onChange={(e) => handleChange('username', e.target.value)}
              disabled={!isEditing || isSaving}
              className={formErrors.username ? 'p-invalid' : ''}
            />
            {formErrors.username && (
              <small className="p-error">{formErrors.username}</small>
            )}
          </div>

          <div className="p-field">
            <label htmlFor="email" className="p-label">
              Email
            </label>
            <InputText
              id="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              disabled={!isEditing || isSaving}
              className={formErrors.email ? 'p-invalid' : ''}
            />
            {formErrors.email && (
              <small className="p-error">{formErrors.email}</small>
            )}
          </div>

          <div className="p-field">
            <label className="p-label">Role</label>
            <InputText value={user.role} disabled />
          </div>

          <div className="p-field">
            <label className="p-label">Member Since</label>
            <InputText value={formatDate(user.created_at)} disabled />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="profile-actions">
          {!isEditing ? (
            <Button
              label="Edit Profile"
              icon="pi pi-pencil"
              onClick={handleEdit}
              className="p-button-primary"
            />
          ) : (
            <>
              <Button
                label="Cancel"
                icon="pi pi-times"
                onClick={handleCancel}
                className="p-button-secondary"
                disabled={isSaving}
              />
              <Button
                label={isSaving ? 'Saving...' : 'Save Changes'}
                icon={isSaving ? 'pi pi-spin pi-spinner' : 'pi pi-check'}
                onClick={handleSave}
                className="p-button-success"
                disabled={isSaving}
                loading={isSaving}
              />
            </>
          )}
        </div>
      </Card>
    </div>
  );
};

export default Profile;
