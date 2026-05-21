/**
 * Password Change Form Component
 * 
 * Allows users to change their password with validation
 */

import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { Password } from 'primereact/password';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { Divider } from 'primereact/divider';
import api from '@services/api';
import './PasswordChangeForm.css';

interface PasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

interface PasswordFormErrors {
  currentPassword?: string;
  newPassword?: string;
  confirmPassword?: string;
}

export const PasswordChangeForm: React.FC = () => {
  const [formData, setFormData] = useState<PasswordFormData>({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [formErrors, setFormErrors] = useState<PasswordFormErrors>({});
  const [touched, setTouched] = useState<Record<keyof PasswordFormData, boolean>>({
    currentPassword: false,
    newPassword: false,
    confirmPassword: false,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  /**
   * Password strength checker
   */
  const checkPasswordStrength = (password: string): {
    score: number;
    feedback: string[];
  } => {
    const feedback: string[] = [];
    let score = 0;

    if (password.length >= 8) {
      score += 1;
    } else {
      feedback.push('At least 8 characters');
    }

    if (/[a-z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('Include lowercase letters');
    }

    if (/[A-Z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('Include uppercase letters');
    }

    if (/[0-9]/.test(password)) {
      score += 1;
    } else {
      feedback.push('Include numbers');
    }

    if (/[^a-zA-Z0-9]/.test(password)) {
      score += 1;
    } else {
      feedback.push('Include special characters');
    }

    return { score, feedback };
  };

  /**
   * Validate form field
   */
  const validateField = (name: keyof PasswordFormData, value: string): string | undefined => {
    switch (name) {
      case 'currentPassword':
        if (!value) {
          return 'Current password is required';
        }
        break;
      case 'newPassword':
        if (!value) {
          return 'New password is required';
        }
        if (value.length < 8) {
          return 'Password must be at least 8 characters';
        }
        const strength = checkPasswordStrength(value);
        if (strength.score < 3) {
          return 'Password is too weak. ' + strength.feedback.join(', ');
        }
        if (value === formData.currentPassword) {
          return 'New password must be different from current password';
        }
        break;
      case 'confirmPassword':
        if (!value) {
          return 'Please confirm your new password';
        }
        if (value !== formData.newPassword) {
          return 'Passwords do not match';
        }
        break;
    }
    return undefined;
  };

  /**
   * Validate entire form
   */
  const validateForm = (): boolean => {
    const errors: PasswordFormErrors = {};
    
    Object.keys(formData).forEach((key) => {
      const field = key as keyof PasswordFormData;
      const error = validateField(field, formData[field]);
      if (error) {
        errors[field] = error;
      }
    });

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle input change
   */
  const handleChange = (field: keyof PasswordFormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    // Clear error for this field if touched
    if (touched[field]) {
      const error = validateField(field, value);
      setFormErrors((prev) => ({
        ...prev,
        [field]: error,
      }));
    }

    // Clear messages
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  /**
   * Handle input blur
   */
  const handleBlur = (field: keyof PasswordFormData) => {
    setTouched((prev) => ({
      ...prev,
      [field]: true,
    }));

    const error = validateField(field, formData[field]);
    setFormErrors((prev) => ({
      ...prev,
      [field]: error,
    }));
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({
      currentPassword: true,
      newPassword: true,
      confirmPassword: true,
    });

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setSuccessMessage(null);
    setErrorMessage(null);

    try {
      // Call API to change password
      await api.post('/auth/change-password', {
        current_password: formData.currentPassword,
        new_password: formData.newPassword,
      });

      setSuccessMessage('Password changed successfully');
      
      // Reset form
      setFormData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      setTouched({
        currentPassword: false,
        newPassword: false,
        confirmPassword: false,
      });
      setFormErrors({});
    } catch (error: any) {
      const message = error.response?.data?.error?.message || 'Failed to change password';
      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Get password strength indicator
   */
  const getPasswordStrengthIndicator = () => {
    if (!formData.newPassword) return null;

    const strength = checkPasswordStrength(formData.newPassword);
    const colors = ['#f44336', '#ff9800', '#ffc107', '#8bc34a', '#4caf50'];
    const labels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];

    return (
      <div className="password-strength">
        <div className="password-strength-bar">
          <div
            className="password-strength-fill"
            style={{
              width: `${(strength.score / 5) * 100}%`,
              backgroundColor: colors[strength.score],
            }}
          />
        </div>
        <small className="password-strength-label" style={{ color: colors[strength.score] }}>
          {labels[strength.score]}
        </small>
      </div>
    );
  };

  return (
    <Card className="password-change-card">
      <h3 className="password-change-title">
        <i className="pi pi-lock" style={{ marginRight: '0.5rem' }}></i>
        Change Password
      </h3>

      <Divider />

      <form onSubmit={handleSubmit} className="password-change-form">
        {/* Success/Error Messages */}
        {successMessage && (
          <Message severity="success" text={successMessage} className="form-message" />
        )}
        {errorMessage && (
          <Message severity="error" text={errorMessage} className="form-message" />
        )}

        {/* Current Password */}
        <div className="p-field">
          <label htmlFor="currentPassword" className="p-label">
            Current Password
          </label>
          <Password
            id="currentPassword"
            value={formData.currentPassword}
            onChange={(e) => handleChange('currentPassword', e.target.value)}
            onBlur={() => handleBlur('currentPassword')}
            className={formErrors.currentPassword && touched.currentPassword ? 'p-invalid' : ''}
            placeholder="Enter your current password"
            feedback={false}
            toggleMask
            disabled={isSubmitting}
          />
          {formErrors.currentPassword && touched.currentPassword && (
            <small className="p-error">{formErrors.currentPassword}</small>
          )}
        </div>

        {/* New Password */}
        <div className="p-field">
          <label htmlFor="newPassword" className="p-label">
            New Password
          </label>
          <Password
            id="newPassword"
            value={formData.newPassword}
            onChange={(e) => handleChange('newPassword', e.target.value)}
            onBlur={() => handleBlur('newPassword')}
            className={formErrors.newPassword && touched.newPassword ? 'p-invalid' : ''}
            placeholder="Enter your new password"
            feedback={false}
            toggleMask
            disabled={isSubmitting}
          />
          {getPasswordStrengthIndicator()}
          {formErrors.newPassword && touched.newPassword && (
            <small className="p-error">{formErrors.newPassword}</small>
          )}
        </div>

        {/* Confirm Password */}
        <div className="p-field">
          <label htmlFor="confirmPassword" className="p-label">
            Confirm New Password
          </label>
          <Password
            id="confirmPassword"
            value={formData.confirmPassword}
            onChange={(e) => handleChange('confirmPassword', e.target.value)}
            onBlur={() => handleBlur('confirmPassword')}
            className={formErrors.confirmPassword && touched.confirmPassword ? 'p-invalid' : ''}
            placeholder="Confirm your new password"
            feedback={false}
            toggleMask
            disabled={isSubmitting}
          />
          {formErrors.confirmPassword && touched.confirmPassword && (
            <small className="p-error">{formErrors.confirmPassword}</small>
          )}
        </div>

        {/* Submit Button */}
        <div className="password-change-actions">
          <Button
            type="submit"
            label={isSubmitting ? 'Changing Password...' : 'Change Password'}
            icon={isSubmitting ? 'pi pi-spin pi-spinner' : 'pi pi-check'}
            className="p-button-primary"
            disabled={isSubmitting}
            loading={isSubmitting}
          />
        </div>
      </form>
    </Card>
  );
};
