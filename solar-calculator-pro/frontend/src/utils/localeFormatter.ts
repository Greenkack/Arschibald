/**
 * Locale-Specific Formatting Utilities
 * Handles number, currency, date, and unit formatting based on locale
 */

import { supportedLanguages, SupportedLanguage } from '../i18n/i18nConfig';

export class LocaleFormatter {
  private locale: string;

  constructor(locale: string = 'de-DE') {
    this.locale = locale;
  }

  /**
   * Set the current locale
   */
  setLocale(locale: string) {
    this.locale = locale;
  }

  /**
   * Format number according to locale
   */
  formatNumber(value: number, options?: Intl.NumberFormatOptions): string {
    return new Intl.NumberFormat(this.locale, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      ...options,
    }).format(value);
  }

  /**
   * Format currency according to locale
   */
  formatCurrency(
    value: number,
    currency: string = 'EUR',
    options?: Intl.NumberFormatOptions
  ): string {
    return new Intl.NumberFormat(this.locale, {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      ...options,
    }).format(value);
  }

  /**
   * Format percentage according to locale
   */
  formatPercent(value: number, decimals: number = 1): string {
    return new Intl.NumberFormat(this.locale, {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value / 100);
  }

  /**
   * Format date according to locale
   */
  formatDate(
    date: Date | string,
    options?: Intl.DateTimeFormatOptions
  ): string {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(this.locale, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      ...options,
    }).format(dateObj);
  }

  /**
   * Format time according to locale
   */
  formatTime(
    date: Date | string,
    options?: Intl.DateTimeFormatOptions
  ): string {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(this.locale, {
      hour: '2-digit',
      minute: '2-digit',
      ...options,
    }).format(dateObj);
  }

  /**
   * Format datetime according to locale
   */
  formatDateTime(
    date: Date | string,
    options?: Intl.DateTimeFormatOptions
  ): string {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(this.locale, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      ...options,
    }).format(dateObj);
  }

  /**
   * Format relative time (e.g., "2 days ago")
   */
  formatRelativeTime(date: Date | string): string {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diffMs = now.getTime() - dateObj.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    const diffWeek = Math.floor(diffDay / 7);
    const diffMonth = Math.floor(diffDay / 30);
    const diffYear = Math.floor(diffDay / 365);

    const rtf = new Intl.RelativeTimeFormat(this.locale, { numeric: 'auto' });

    if (diffYear > 0) return rtf.format(-diffYear, 'year');
    if (diffMonth > 0) return rtf.format(-diffMonth, 'month');
    if (diffWeek > 0) return rtf.format(-diffWeek, 'week');
    if (diffDay > 0) return rtf.format(-diffDay, 'day');
    if (diffHour > 0) return rtf.format(-diffHour, 'hour');
    if (diffMin > 0) return rtf.format(-diffMin, 'minute');
    return rtf.format(-diffSec, 'second');
  }

  /**
   * Format file size
   */
  formatFileSize(bytes: number): string {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${this.formatNumber(size, { maximumFractionDigits: 1 })} ${units[unitIndex]}`;
  }

  /**
   * Format energy units (kWh, kWp)
   */
  formatEnergy(value: number, unit: 'kWh' | 'kWp' | 'MWh' | 'MWp'): string {
    return `${this.formatNumber(value)} ${unit}`;
  }

  /**
   * Format area (m²)
   */
  formatArea(value: number): string {
    return `${this.formatNumber(value)} m²`;
  }

  /**
   * Format angle (degrees)
   */
  formatAngle(value: number): string {
    return `${this.formatNumber(value, { maximumFractionDigits: 0 })}°`;
  }

  /**
   * Format weight (kg, tons)
   */
  formatWeight(value: number, unit: 'kg' | 't' = 'kg'): string {
    return `${this.formatNumber(value)} ${unit}`;
  }

  /**
   * Format duration (years, months, days)
   */
  formatDuration(value: number, unit: 'years' | 'months' | 'days'): string {
    const unitMap = {
      de: { years: 'Jahre', months: 'Monate', days: 'Tage' },
      en: { years: 'years', months: 'months', days: 'days' },
    };

    const lang = this.locale.startsWith('de') ? 'de' : 'en';
    return `${this.formatNumber(value, { maximumFractionDigits: 1 })} ${unitMap[lang][unit]}`;
  }

  /**
   * Parse locale-formatted number to standard number
   */
  parseNumber(value: string): number {
    // Remove thousand separators and replace decimal separator
    if (this.locale.startsWith('de')) {
      // German: 1.234,56 -> 1234.56
      return parseFloat(value.replace(/\./g, '').replace(',', '.'));
    }
    // English: 1,234.56 -> 1234.56
    return parseFloat(value.replace(/,/g, ''));
  }

  /**
   * Get decimal separator for current locale
   */
  getDecimalSeparator(): string {
    return this.locale.startsWith('de') ? ',' : '.';
  }

  /**
   * Get thousand separator for current locale
   */
  getThousandSeparator(): string {
    return this.locale.startsWith('de') ? '.' : ',';
  }

  /**
   * Format list according to locale
   */
  formatList(items: string[], type: 'conjunction' | 'disjunction' = 'conjunction'): string {
    return new Intl.ListFormat(this.locale, { type }).format(items);
  }

  /**
   * Format plural according to locale
   */
  formatPlural(count: number, singular: string, plural: string): string {
    const rules = new Intl.PluralRules(this.locale);
    const rule = rules.select(count);
    return rule === 'one' ? singular : plural;
  }
}

// Create singleton instance
export const localeFormatter = new LocaleFormatter();

// Hook for React components
export const useLocaleFormatter = () => {
  const { i18n } = require('react-i18next');
  const formatter = new LocaleFormatter(i18n.language);
  return formatter;
};
