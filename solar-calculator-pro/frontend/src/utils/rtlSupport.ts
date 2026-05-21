/**
 * RTL (Right-to-Left) Support Utilities
 * Handles layout direction for RTL languages
 */

import { supportedLanguages, SupportedLanguage } from '../i18n/i18nConfig';

export class RTLSupport {
  /**
   * Check if a language is RTL
   */
  static isRTL(language: SupportedLanguage): boolean {
    return supportedLanguages[language]?.rtl || false;
  }

  /**
   * Apply RTL direction to document
   */
  static applyDirection(language: SupportedLanguage): void {
    const isRTL = this.isRTL(language);
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = language;

    // Update body class for additional styling
    if (isRTL) {
      document.body.classList.add('rtl');
      document.body.classList.remove('ltr');
    } else {
      document.body.classList.add('ltr');
      document.body.classList.remove('rtl');
    }
  }

  /**
   * Get text alignment based on direction
   */
  static getTextAlign(language: SupportedLanguage): 'left' | 'right' {
    return this.isRTL(language) ? 'right' : 'left';
  }

  /**
   * Get flex direction based on RTL
   */
  static getFlexDirection(
    language: SupportedLanguage,
    defaultDirection: 'row' | 'column' = 'row'
  ): string {
    if (defaultDirection === 'column') return 'column';
    return this.isRTL(language) ? 'row-reverse' : 'row';
  }

  /**
   * Get margin/padding direction
   */
  static getSpacingDirection(
    language: SupportedLanguage,
    side: 'left' | 'right'
  ): 'left' | 'right' {
    if (!this.isRTL(language)) return side;
    return side === 'left' ? 'right' : 'left';
  }

  /**
   * Get border radius for RTL
   */
  static getBorderRadius(
    language: SupportedLanguage,
    topLeft: number,
    topRight: number,
    bottomRight: number,
    bottomLeft: number
  ): string {
    if (!this.isRTL(language)) {
      return `${topLeft}px ${topRight}px ${bottomRight}px ${bottomLeft}px`;
    }
    return `${topRight}px ${topLeft}px ${bottomLeft}px ${bottomRight}px`;
  }

  /**
   * Get transform origin for RTL
   */
  static getTransformOrigin(
    language: SupportedLanguage,
    x: string = 'left',
    y: string = 'top'
  ): string {
    if (!this.isRTL(language)) return `${x} ${y}`;
    const rtlX = x === 'left' ? 'right' : x === 'right' ? 'left' : x;
    return `${rtlX} ${y}`;
  }

  /**
   * Get icon rotation for RTL (for directional icons)
   */
  static getIconRotation(language: SupportedLanguage): number {
    return this.isRTL(language) ? 180 : 0;
  }

  /**
   * Flip horizontal position for RTL
   */
  static flipHorizontal(language: SupportedLanguage, value: number): number {
    return this.isRTL(language) ? -value : value;
  }

  /**
   * Get CSS styles for RTL support
   */
  static getStyles(language: SupportedLanguage): React.CSSProperties {
    return {
      direction: this.isRTL(language) ? 'rtl' : 'ltr',
      textAlign: this.getTextAlign(language),
    };
  }

  /**
   * Get PrimeReact RTL configuration
   */
  static getPrimeReactConfig(language: SupportedLanguage) {
    return {
      rtl: this.isRTL(language),
    };
  }

  /**
   * Convert logical properties to physical for RTL
   */
  static convertLogicalProperty(
    language: SupportedLanguage,
    property: 'start' | 'end'
  ): 'left' | 'right' {
    const isRTL = this.isRTL(language);
    if (property === 'start') {
      return isRTL ? 'right' : 'left';
    }
    return isRTL ? 'left' : 'right';
  }

  /**
   * Get scroll direction multiplier for RTL
   */
  static getScrollMultiplier(language: SupportedLanguage): number {
    return this.isRTL(language) ? -1 : 1;
  }

  /**
   * Adjust chart configuration for RTL
   */
  static adjustChartConfig(language: SupportedLanguage, config: any): any {
    if (!this.isRTL(language)) return config;

    return {
      ...config,
      layout: {
        ...config.layout,
        padding: {
          left: config.layout?.padding?.right || 0,
          right: config.layout?.padding?.left || 0,
          top: config.layout?.padding?.top || 0,
          bottom: config.layout?.padding?.bottom || 0,
        },
      },
      legend: {
        ...config.legend,
        align: config.legend?.align === 'left' ? 'right' : 'left',
      },
    };
  }

  /**
   * Adjust table column order for RTL
   */
  static adjustTableColumns<T>(
    language: SupportedLanguage,
    columns: T[]
  ): T[] {
    return this.isRTL(language) ? [...columns].reverse() : columns;
  }
}

// Hook for React components
export const useRTL = () => {
  const { i18n } = require('react-i18next');
  const language = i18n.language as SupportedLanguage;

  return {
    isRTL: RTLSupport.isRTL(language),
    direction: RTLSupport.isRTL(language) ? 'rtl' : 'ltr',
    textAlign: RTLSupport.getTextAlign(language),
    getStyles: () => RTLSupport.getStyles(language),
    flipHorizontal: (value: number) => RTLSupport.flipHorizontal(language, value),
    getSpacingDirection: (side: 'left' | 'right') =>
      RTLSupport.getSpacingDirection(language, side),
  };
};

export default RTLSupport;
