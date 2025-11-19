/**
 * UI Store
 * 
 * Manages global UI state using Zustand
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  // Sidebar
  sidebarCollapsed: boolean;
  sidebarVisible: boolean;
  
  // Theme
  theme: 'light' | 'dark' | 'auto';
  
  // Loading
  globalLoading: boolean;
  loadingMessage: string | null;
  
  // Notifications
  notifications: Notification[];
  
  // Actions
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setSidebarVisible: (visible: boolean) => void;
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  setGlobalLoading: (loading: boolean, message?: string) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: number;
}

/**
 * UI store
 */
export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      // Initial state
      sidebarCollapsed: false,
      sidebarVisible: true,
      theme: 'light',
      globalLoading: false,
      loadingMessage: null,
      notifications: [],

      // Actions
      toggleSidebar: () =>
        set((state) => ({
          sidebarCollapsed: !state.sidebarCollapsed,
        })),

      setSidebarCollapsed: (collapsed) =>
        set({ sidebarCollapsed: collapsed }),

      setSidebarVisible: (visible) =>
        set({ sidebarVisible: visible }),

      setTheme: (theme) =>
        set({ theme }),

      setGlobalLoading: (loading, message) =>
        set({
          globalLoading: loading,
          loadingMessage: message || null,
        }),

      addNotification: (notification) => {
        const id = `notification-${Date.now()}-${Math.random()}`;
        const newNotification: Notification = {
          ...notification,
          id,
          timestamp: Date.now(),
        };

        set((state) => ({
          notifications: [...state.notifications, newNotification],
        }));

        // Auto-remove after 5 seconds
        setTimeout(() => {
          get().removeNotification(id);
        }, 5000);
      },

      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),

      clearNotifications: () =>
        set({ notifications: [] }),
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
      }),
    }
  )
);
