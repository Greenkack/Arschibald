/**
 * Theme Store - Zustand store for theme management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ThemeSettings, themeEngine } from '../theme/themeEngine';
import { getThemePreset, createCustomTheme } from '../theme/themePresets';

interface ThemeStore {
  theme: ThemeSettings;
  isCustomThemeCreatorOpen: boolean;
  
  // Actions
  setTheme: (theme: ThemeSettings) => void;
  setPreset: (presetName: string) => void;
  updateColors: (colors: Partial<ThemeSettings['colors']>) => void;
  updateTypography: (typography: Partial<ThemeSettings['typography']>) => void;
  setMode: (mode: 'light' | 'dark' | 'auto') => void;
  resetTheme: () => void;
  exportTheme: () => string;
  importTheme: (themeJson: string) => void;
  openCustomThemeCreator: () => void;
  closeCustomThemeCreator: () => void;
}

const defaultTheme = getThemePreset('default');

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      theme: defaultTheme,
      isCustomThemeCreatorOpen: false,

      setTheme: (theme) => {
        set({ theme });
        themeEngine.applyTheme(theme);
      },

      setPreset: (presetName) => {
        const theme = getThemePreset(presetName);
        get().setTheme(theme);
      },

      updateColors: (colors) => {
        const currentTheme = get().theme;
        const updatedTheme = {
          ...currentTheme,
          colors: {
            ...currentTheme.colors,
            ...colors,
          },
          preset: 'custom',
        };
        get().setTheme(updatedTheme);
      },

      updateTypography: (typography) => {
        const currentTheme = get().theme;
        const updatedTheme = {
          ...currentTheme,
          typography: {
            ...currentTheme.typography,
            ...typography,
          },
          preset: 'custom',
        };
        get().setTheme(updatedTheme);
      },

      setMode: (mode) => {
        const currentTheme = get().theme;
        const updatedTheme = {
          ...currentTheme,
          mode,
        };
        get().setTheme(updatedTheme);
      },

      resetTheme: () => {
        get().setTheme(defaultTheme);
      },

      exportTheme: () => {
        const theme = get().theme;
        return JSON.stringify(theme, null, 2);
      },

      importTheme: (themeJson) => {
        try {
          const theme = JSON.parse(themeJson) as ThemeSettings;
          get().setTheme(theme);
        } catch (error) {
          console.error('Failed to import theme:', error);
          throw new Error('Invalid theme format');
        }
      },

      openCustomThemeCreator: () => {
        set({ isCustomThemeCreatorOpen: true });
      },

      closeCustomThemeCreator: () => {
        set({ isCustomThemeCreatorOpen: false });
      },
    }),
    {
      name: 'theme-storage',
      partialize: (state) => ({ theme: state.theme }),
    }
  )
);

// Initialize theme on app start
export function initializeTheme(): void {
  const theme = useThemeStore.getState().theme;
  themeEngine.applyTheme(theme);
}
