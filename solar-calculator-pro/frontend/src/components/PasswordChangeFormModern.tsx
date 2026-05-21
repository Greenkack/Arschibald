/**
 * Password Change Form Component (Modern - shadcn/ui)
 * 
 * Allows users to change their password with validation
 */

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { CheckCircle2, AlertCircle, Lock, Eye, EyeOff } from 'lucide-react';
import api from '@services/api';
import { cn } from '@/lib/utils';

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

export const PasswordChangeFormModern: React.FC = () => {
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

  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({
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
   * Toggle password visibility
   */
  const togglePasswordVisibility = (field: string) => {
    setShowPasswords((prev) => ({
      ...prev,
      [field]: !prev[field],
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
    const colors = [
      'bg-red-500',
      'bg-orange-500',
      'bg-yellow-500',
      'bg-lime-500',
      'bg-green-500',
    ];
    const labels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];

    return (
      <div className="space-y-1 mt-2">
        <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
          <div
            className={cn('h-full transition-all duration-300', colors[strength.score])}
            style={{ width: `${(strength.score / 5) * 100}%` }}
          />
        </div>
        <p className={cn('text-xs font-medium', {
          'text-red-600': strength.score <= 1,
          'text-orange-600': strength.score === 2,
          'text-yellow-600': strength.score === 3,
          'text-green-600': strength.score >= 4,
        })}>
          {labels[strength.score]}
        </p>
      </div>
    );
  };

  return (
    <Card className="max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lock className="h-5 w-5" />
          Change Password
        </CardTitle>
        <CardDescription>
          Update your password to keep your account secure
        </CardDescription>
      </CardHeader>

      <Separator />

      <CardContent className="pt-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Success/Error Messages */}
          {successMessage && (
            <Alert className="border-green-500 bg-green-50 dark:bg-green-950">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-700 dark:text-green-300">
                {successMessage}
              </AlertDescription>
            </Alert>
          )}
          {errorMessage && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          {/* Current Password */}
          <div className="space-y-2">
            <Label htmlFor="currentPassword">
              Current Password <span className="text-destructive">*</span>
            </Label>
            <div className="relative">
              <Input
                id="currentPassword"
                type={showPasswords.currentPassword ? 'text' : 'password'}
                value={formData.currentPassword}
                onChange={(e) => handleChange('currentPassword', e.target.value)}
                onBlur={() => handleBlur('currentPassword')}
                className={cn(
                  formErrors.currentPassword && touched.currentPassword && 'border-destructive'
                )}
                placeholder="Enter your current password"
                disabled={isSubmitting}
              />
              <button
                type="button"
                onClick={() => togglePasswordVisibility('currentPassword')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showPasswords.currentPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            {formErrors.currentPassword && touched.currentPassword && (
              <p className="text-sm text-destructive">{formErrors.currentPassword}</p>
            )}
          </div>

          {/* New Password */}
          <div className="space-y-2">
            <Label htmlFor="newPassword">
              New Password <span className="text-destructive">*</span>
            </Label>
            <div className="relative">
              <Input
                id="newPassword"
                type={showPasswords.newPassword ? 'text' : 'password'}
                value={formData.newPassword}
                onChange={(e) => handleChange('newPassword', e.target.value)}
                onBlur={() => handleBlur('newPassword')}
                className={cn(
                  formErrors.newPassword && touched.newPassword && 'border-destructive'
                )}
                placeholder="Enter your new password"
                disabled={isSubmitting}
              />
              <button
                type="button"
                onClick={() => togglePasswordVisibility('newPassword')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showPasswords.newPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            {getPasswordStrengthIndicator()}
            {formErrors.newPassword && touched.newPassword && (
              <p className="text-sm text-destructive">{formErrors.newPassword}</p>
            )}
          </div>

          {/* Confirm Password */}
          <div className="space-y-2">
            <Label htmlFor="confirmPassword">
              Confirm New Password <span className="text-destructive">*</span>
            </Label>
            <div className="relative">
              <Input
                id="confirmPassword"
                type={showPasswords.confirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => handleChange('confirmPassword', e.target.value)}
                onBlur={() => handleBlur('confirmPassword')}
                className={cn(
                  formErrors.confirmPassword && touched.confirmPassword && 'border-destructive'
                )}
                placeholder="Confirm your new password"
                disabled={isSubmitting}
              />
              <button
                type="button"
                onClick={() => togglePasswordVisibility('confirmPassword')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showPasswords.confirmPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            {formErrors.confirmPassword && touched.confirmPassword && (
              <p className="text-sm text-destructive">{formErrors.confirmPassword}</p>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={isSubmitting}
              className="gap-2"
            >
              {isSubmitting ? (
                <>
                  <span className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  Changing Password...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-4 w-4" />
                  Change Password
                </>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};
