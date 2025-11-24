/**
 * Theme Presets - Predefined theme configurations
 */

import { ThemeSettings } from './themeEngine';

export const themePresets: Record<string, ThemeSettings> = {
  default: {
    mode: 'light',
    preset: 'default',
    colors: {
      primary: '#3B82F6',
      secondary: '#8B5CF6',
      accent: '#10B981',
      background: '#F9FAFB',
      surface: '#FFFFFF',
      text: '#111827',
      error: '#EF4444',
      warning: '#F59E0B',
      success: '#10B981',
      info: '#3B82F6',
    },
    typography: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      fontSize: 'medium',
      fontWeight: 'normal',
    },
  },

  dark: {
    mode: 'dark',
    preset: 'dark',
    colors: {
      primary: '#60A5FA',
      secondary: '#A78BFA',
      accent: '#34D399',
      background: '#111827',
      surface: '#1F2937',
      text: '#F9FAFB',
      error: '#F87171',
      warning: '#FBBF24',
      success: '#34D399',
      info: '#60A5FA',
    },
    typography: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      fontSize: 'medium',
      fontWeight: 'normal',
    },
  },

  ocean: {
    mode: 'light',
    preset: 'ocean',
    colors: {
      primary: '#0EA5E9',
      secondary: '#06B6D4',
      accent: '#14B8A6',
      background: '#F0F9FF',
      surface: '#FFFFFF',
      text: '#0C4A6E',
      error: '#DC2626',
      warning: '#F59E0B',
      success: '#14B8A6',
      info: '#0EA5E9',
    },
    typography: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      fontSize: 'medium',
      fontWeight: 'normal',
    },
  },

  forest: {
    mode: 'light',
    preset: 'forest',
    colors: {
      primary: '#059669',
      secondary: '#10B981',
      accent: '#84CC16',
      background: '#F0FDF4',
      surface: '#FFFFFF',
      text: '#064E3B',
      error: '#DC2626',
      warning: '#F59E0B',
      success: '#10B981',
      info: '#0EA5E9',
    },
    typography: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      fontSize: 'medium',
      fontWeight: 'normal',
    },
  },

  sunset: {
    mode: 'light',
    preset: 'sunset',
    colors: {
      primary: '#F97316',
      secondary: '#FB923C',
      accent: '#FBBF24',
      background: '#FFF7ED',
      surface: '#FFFFFF',
      text: '#7C2D12',
      error: '#DC2626',
      warning: '#F59E0B',
      success: '#10B981',
      info: '#3B82F6',
    },
    typography: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      fontSize: 'medium',
      fontWeight: 'normal',
    },
  },

  highContrast: {
    mode: 'light',
    preset: 'highContrast',
    colors: {
      primary: '#000000',
      secondary: '#1F2937',
      accent: '#4B5563',
      background: '#FFFFFF',
      surface: '#F9FAFB',
      text: '#000000',
      error: '#991B1B',
      warning: '#92400E',
      success: '#065F46',
      info: '#1E3A8A',
    },
    typography: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      fontSize: 'large',
      fontWeight: 'bold',
    },
  },
};

/**
 * Get theme preset by name
 */
export function getThemePreset(name: string): ThemeSettings {
  return themePresets[name] || themePresets.default;
}

/**
 * Get all available theme preset names
 */
export function getThemePresetNames(): string[] {
  return Object.keys(themePresets);
}

/**
 * Create custom theme from base preset
 */
export function createCustomTheme(
  basePreset: string,
  overrides: Partial<ThemeSettings>
): ThemeSettings {
  const base = getThemePreset(basePreset);
  return {
    ...base,
    ...overrides,
    preset: 'custom',
    colors: {
      ...base.colors,
      ...(overrides.colors || {}),
    },
    typography: {
      ...base.typography,
      ...(overrides.typography || {}),
    },
  };
}
