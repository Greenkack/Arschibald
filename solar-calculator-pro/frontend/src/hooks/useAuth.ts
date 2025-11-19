/**
 * useAuth Hook
 * 
 * Custom hook for authentication operations
 */

import { useCallback } from 'react';
import { useAuthStore } from '@store/authStore';
import { authService, LoginRequest } from '@services/auth';
import { useUIStore } from '@store/uiStore';

export const useAuth = () => {
  const { user, isAuthenticated, isLoading, error, setUser, setLoading, setError, logout: logoutStore } = useAuthStore();
  const { addNotification } = useUIStore();

  /**
   * Login user
   */
  const login = useCallback(async (credentials: LoginRequest) => {
    try {
      setLoading(true);
      setError(null);

      // Call auth service
      await authService.login(credentials);

      // Get user data
      const userData = await authService.getCurrentUser();
      setUser(userData);

      addNotification({
        type: 'success',
        title: 'Login Successful',
        message: `Welcome back, ${userData.username}!`,
      });

      return true;
    } catch (err: any) {
      const errorMessage = err.message || 'Login failed';
      setError(errorMessage);
      
      addNotification({
        type: 'error',
        title: 'Login Failed',
        message: errorMessage,
      });

      return false;
    } finally {
      setLoading(false);
    }
  }, [setUser, setLoading, setError, addNotification]);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      await authService.logout();
      logoutStore();

      addNotification({
        type: 'info',
        title: 'Logged Out',
        message: 'You have been logged out successfully.',
      });
    } catch (err: any) {
      console.error('Logout error:', err);
      // Still logout locally even if API call fails
      logoutStore();
    }
  }, [logoutStore, addNotification]);

  /**
   * Refresh user data
   */
  const refreshUser = useCallback(async () => {
    try {
      setLoading(true);
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (err: any) {
      console.error('Failed to refresh user:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [setUser, setLoading, setError]);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    refreshUser,
  };
};
