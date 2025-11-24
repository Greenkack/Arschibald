/**
 * Theme Engine - Core theme management system
 * Handles theme application, CSS variable generation, and PrimeReact integration
 */

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  error: string;
  warning: string;
  success: string;
  info: string;
}

export interface ThemeTypography {
  fontFamily: string;
  fontSize: 'small' | 'medium' | 'large' | 'xlarge';
  fontWeight: 'light' | 'normal' | 'medium' | 'bold';
}

export interface ThemeSettings {
  mode: 'light' | 'dark' | 'auto';
  preset: string;
  colors: ThemeColors;
  typography: ThemeTypography;
}

export class ThemeEngine {
  private currentTheme: ThemeSettings | null = null;

  /**
   * Apply theme to the application
   */
  applyTheme(theme: ThemeSettings): void {
    this.currentTheme = theme;

    // Generate and apply CSS variables
    const cssVars = this.generateCSSVariables(theme);
    this.applyCSSVariables(cssVars);

    // Update PrimeReact theme
    this.updatePrimeReactTheme(theme);

    // Apply mode-specific styles
    this.applyModeStyles(theme.mode);
  }

  /**
   * Generate CSS variables from theme settings
   */
  private generateCSSVariables(theme: ThemeSettings): Record<string, string> {
    return {
      // Colors
      '--color-primary': theme.colors.primary,
      '--color-secondary': theme.colors.secondary,
      '--color-accent': theme.colors.accent,
      '--color-background': theme.colors.background,
      '--color-surface': theme.colors.surface,
      '--color-text': theme.colors.text,
      '--color-error': theme.colors.error,
      '--color-warning': theme.colors.warning,
      '--color-success': theme.colors.success,
      '--color-info': theme.colors.info,

      // Typography
      '--font-family': theme.typography.fontFamily,
      '--font-size-base': this.getFontSize(theme.typography.fontSize),
      '--font-weight': this.getFontWeight(theme.typography.fontWeight),
    };
  }

  /**
   * Apply CSS variables to document root
   */
  private applyCSSVariables(vars: Record<string, string>): void {
    Object.entries(vars).forEach(([key, value]) => {
      document.documentElement.style.setProperty(key, value);
    });
  }

  /**
   * Update PrimeReact theme variables
   */
  private updatePrimeReactTheme(theme: ThemeSettings): void {
    const primeVars = {
      '--primary-color': theme.colors.primary,
      '--surface-ground': theme.colors.background,
      '--surface-card': theme.colors.surface,
      '--text-color': theme.colors.text,
      '--text-color-secondary': this.adjustOpacity(theme.colors.text, 0.7),
      '--surface-border': this.adjustOpacity(theme.colors.text, 0.2),
    };

    Object.entries(primeVars).forEach(([key, value]) => {
      document.documentElement.style.setProperty(key, value);
    });
  }

  /**
   * Apply mode-specific styles (light/dark/auto)
   */
  private applyModeStyles(mode: 'light' | 'dark' | 'auto'): void {
    const body = document.body;
    body.classList.remove('theme-light', 'theme-dark');

    if (mode === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      body.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
    } else {
      body.classList.add(`theme-${mode}`);
    }
  }

  /**
   * Get font size value
   */
  private getFontSize(size: ThemeTypography['fontSize']): string {
    const sizes = {
      small: '14px',
      medium: '16px',
      large: '18px',
      xlarge: '20px',
    };
    return sizes[size];
  }

  /**
   * Get font weight value
   */
  private getFontWeight(weight: ThemeTypography['fontWeight']): string {
    const weights = {
      light: '300',
      normal: '400',
      medium: '500',
      bold: '700',
    };
    return weights[weight];
  }

  /**
   * Adjust color opacity
   */
  private adjustOpacity(color: string, opacity: number): string {
    // Simple implementation - can be enhanced with color parsing library
    if (color.startsWith('#')) {
      const r = parseInt(color.slice(1, 3), 16);
      const g = parseInt(color.slice(3, 5), 16);
      const b = parseInt(color.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    }
    return color;
  }

  /**
   * Get current theme
   */
  getCurrentTheme(): ThemeSettings | null {
    return this.currentTheme;
  }
}

export const themeEngine = new ThemeEngine();
