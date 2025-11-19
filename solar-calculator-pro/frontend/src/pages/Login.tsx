/**
 * Login Page
 * 
 * User authentication with form validation and remember me functionality
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Password } from 'primereact/password';
import { Button } from 'primereact/button';
import { Checkbox } from 'primereact/checkbox';
import { Message } from 'primereact/message';
import { useAuth } from '@hooks/useAuth';
import './Login.css';

interface LoginFormData {
  username: string;
  password: string;
  rememberMe: boolean;
}

interface LoginFormErrors {
  username?: string;
  password?: string;
}

const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading, error, isAuthenticated } = useAuth();

  const [formData, setFormData] = useState<LoginFormData>({
    username: '',
    password: '',
    rememberMe: false,
  });

  const [formErrors, setFormErrors] = useState<LoginFormErrors>({});
  const [touched, setTouched] = useState<{ username: boolean; password: boolean }>({
    username: false,
    password: false,
  });

  // Load remembered username on mount
  useEffect(() => {
    const rememberedUsername = localStorage.getItem('remembered_username');
    if (rememberedUsername) {
      setFormData((prev) => ({
        ...prev,
        username: rememberedUsername,
        rememberMe: true,
      }));
    }
  }, []);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = (location.state as any)?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  /**
   * Validate form field
   */
  const validateField = (name: keyof LoginFormData, value: string): string | undefined => {
    switch (name) {
      case 'username':
        if (!value.trim()) {
          return 'Username is required';
        }
        if (value.length < 3) {
          return 'Username must be at least 3 characters';
        }
        break;
      case 'password':
        if (!value) {
          return 'Password is required';
        }
        if (value.length < 6) {
          return 'Password must be at least 6 characters';
        }
        break;
    }
    return undefined;
  };

  /**
   * Validate entire form
   */
  const validateForm = (): boolean => {
    const errors: LoginFormErrors = {};
    
    const usernameError = validateField('username', formData.username);
    if (usernameError) errors.username = usernameError;
    
    const passwordError = validateField('password', formData.password);
    if (passwordError) errors.password = passwordError;

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle input change
   */
  const handleChange = (field: keyof LoginFormData, value: string | boolean) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    // Clear error for this field
    if (typeof value === 'string' && touched[field as 'username' | 'password']) {
      const error = validateField(field as 'username' | 'password', value);
      setFormErrors((prev) => ({
        ...prev,
        [field]: error,
      }));
    }
  };

  /**
   * Handle input blur
   */
  const handleBlur = (field: 'username' | 'password') => {
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
    setTouched({ username: true, password: true });

    // Validate form
    if (!validateForm()) {
      return;
    }

    // Handle remember me
    if (formData.rememberMe) {
      localStorage.setItem('remembered_username', formData.username);
    } else {
      localStorage.removeItem('remembered_username');
    }

    // Attempt login
    const success = await login({
      username: formData.username,
      password: formData.password,
    });

    if (success) {
      // Navigation is handled by useEffect
    }
  };

  /**
   * Handle Enter key press
   */
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit(e as any);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card-wrapper">
        <Card className="login-card">
          <div className="login-header">
            <i className="pi pi-sun" style={{ fontSize: '3rem', color: 'var(--primary-color)' }}></i>
            <h1>Solar Calculator Pro</h1>
            <p className="login-subtitle">Sign in to your account</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {/* Global error message */}
            {error && (
              <Message
                severity="error"
                text={error}
                className="login-error-message"
              />
            )}

            {/* Username field */}
            <div className="p-field">
              <label htmlFor="username" className="p-label">
                Username
              </label>
              <div className="p-inputgroup">
                <span className="p-inputgroup-addon">
                  <i className="pi pi-user"></i>
                </span>
                <InputText
                  id="username"
                  value={formData.username}
                  onChange={(e) => handleChange('username', e.target.value)}
                  onBlur={() => handleBlur('username')}
                  onKeyPress={handleKeyPress}
                  className={formErrors.username && touched.username ? 'p-invalid' : ''}
                  placeholder="Enter your username"
                  autoComplete="username"
                  disabled={isLoading}
                />
              </div>
              {formErrors.username && touched.username && (
                <small className="p-error">{formErrors.username}</small>
              )}
            </div>

            {/* Password field */}
            <div className="p-field">
              <label htmlFor="password" className="p-label">
                Password
              </label>
              <div className="p-inputgroup">
                <span className="p-inputgroup-addon">
                  <i className="pi pi-lock"></i>
                </span>
                <Password
                  id="password"
                  value={formData.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  onBlur={() => handleBlur('password')}
                  onKeyPress={handleKeyPress}
                  className={formErrors.password && touched.password ? 'p-invalid' : ''}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  feedback={false}
                  toggleMask
                  disabled={isLoading}
                />
              </div>
              {formErrors.password && touched.password && (
                <small className="p-error">{formErrors.password}</small>
              )}
            </div>

            {/* Remember me checkbox */}
            <div className="p-field-checkbox">
              <Checkbox
                inputId="rememberMe"
                checked={formData.rememberMe}
                onChange={(e) => handleChange('rememberMe', e.checked || false)}
                disabled={isLoading}
              />
              <label htmlFor="rememberMe" className="p-checkbox-label">
                Remember me
              </label>
            </div>

            {/* Submit button */}
            <Button
              type="submit"
              label={isLoading ? 'Signing in...' : 'Sign In'}
              icon={isLoading ? 'pi pi-spin pi-spinner' : 'pi pi-sign-in'}
              className="login-button"
              disabled={isLoading}
              loading={isLoading}
            />

            {/* Forgot password link */}
            <div className="login-footer">
              <a href="#" className="forgot-password-link">
                Forgot password?
              </a>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default Login;
