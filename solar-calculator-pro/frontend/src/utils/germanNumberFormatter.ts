/**
 * German Number Formatter Utility
 * 
 * TypeScript implementation of German number formatting for the frontend.
 * Provides bidirectional conversion between German format (1.234,56) and
 * standard JavaScript numbers.
 * 
 * Requirements: 14.1, 14.2, 14.3, 14.6, 14.9
 */

export interface GermanNumberFormatterOptions {
  decimalPlaces?: number;
  thousandSeparator?: string;
  decimalSeparator?: string;
}

export class GermanNumberFormatter {
  private readonly thousandSeparator: string;
  private readonly decimalSeparator: string;
  private readonly decimalPlaces: number;
  private readonly germanNumberPattern: RegExp;

  constructor(options: GermanNumberFormatterOptions = {}) {
    this.thousandSeparator = options.thousandSeparator || '.';
    this.decimalSeparator = options.decimalSeparator || ',';
    this.decimalPlaces = options.decimalPlaces ?? 2;
    
    // Regex pattern for German number validation
    this.germanNumberPattern = /^-?\d{1,3}(?:\.\d{3})*(?:,\d+)?$|^-?\d+(?:,\d+)?$/;
  }

  /**
   * Format a number to German format
   * @param value - Number to format
   * @param decimalPlaces - Override default decimal places
   * @returns Formatted string (e.g., "1.234,56")
   */
  format(value: number | string, decimalPlaces?: number): string {
    const places = decimalPlaces ?? this.decimalPlaces;
    
    // Parse if string
    let num: number;
    if (typeof value === 'string') {
      if (this.validate(value)) {
        num = this.parse(value);
      } else {
        num = parseFloat(value);
      }
    } else {
      num = value;
    }

    if (isNaN(num)) {
      throw new Error(`Cannot format invalid number: ${value}`);
    }

    // Handle negative numbers
    const isNegative = num < 0;
    num = Math.abs(num);

    // Round to specified decimal places
    const factor = Math.pow(10, places);
    num = Math.round(num * factor) / factor;

    // Split into integer and decimal parts
    const numStr = num.toFixed(places);
    const [integerPart, decimalPart] = numStr.split('.');

    // Add thousand separators
    const formattedInteger = this.addThousandSeparators(integerPart);

    // Combine parts
    let result = formattedInteger;
    if (places > 0 && decimalPart) {
      result += this.decimalSeparator + decimalPart;
    }

    // Add negative sign if needed
    return isNegative ? `-${result}` : result;
  }

  /**
   * Parse German-formatted number to JavaScript number
   * @param germanNumber - German-formatted string (e.g., "1.234,56")
   * @returns Parsed number
   */
  parse(germanNumber: string): number {
    if (typeof germanNumber !== 'string') {
      throw new Error(`Input must be a string, got ${typeof germanNumber}`);
    }

    const trimmed = germanNumber.trim();

    if (!this.validate(trimmed)) {
      throw new Error(
        `Invalid German number format: '${germanNumber}'. Expected format: 1.234,56`
      );
    }

    // Handle negative numbers
    const isNegative = trimmed.startsWith('-');
    let numberStr = isNegative ? trimmed.substring(1) : trimmed;

    // Remove thousand separators
    numberStr = numberStr.replace(new RegExp(`\\${this.thousandSeparator}`, 'g'), '');

    // Replace decimal separator with dot
    numberStr = numberStr.replace(this.decimalSeparator, '.');

    const result = parseFloat(numberStr);

    if (isNaN(result)) {
      throw new Error(`Cannot parse '${germanNumber}' to number`);
    }

    return isNegative ? -result : result;
  }

  /**
   * Format as currency
   * @param amount - Amount to format
   * @param currencySymbol - Currency symbol (default: "€")
   * @param symbolPosition - "prefix" or "suffix" (default: "suffix")
   * @returns Formatted currency string
   */
  formatCurrency(
    amount: number | string,
    currencySymbol: string = '€',
    symbolPosition: 'prefix' | 'suffix' = 'suffix'
  ): string {
    const formatted = this.format(amount, 2);
    
    if (symbolPosition === 'prefix') {
      return `${currencySymbol} ${formatted}`;
    }
    return `${formatted} ${currencySymbol}`;
  }

  /**
   * Format as percentage
   * @param value - Value to format (0.15 for 15% if multiplyBy100 is true)
   * @param multiplyBy100 - Whether to multiply by 100
   * @returns Formatted percentage string
   */
  formatPercent(value: number | string, multiplyBy100: boolean = true): string {
    let num: number;
    
    if (typeof value === 'string') {
      num = this.validate(value) ? this.parse(value) : parseFloat(value);
    } else {
      num = value;
    }

    if (isNaN(num)) {
      throw new Error(`Cannot format invalid number as percentage: ${value}`);
    }

    if (multiplyBy100) {
      num = num * 100;
    }

    const formatted = this.format(num, 2);
    return `${formatted} %`;
  }

  /**
   * Validate German number format
   * @param germanNumber - String to validate
   * @returns True if valid German format
   */
  validate(germanNumber: string): boolean {
    if (typeof germanNumber !== 'string') {
      return false;
    }

    const trimmed = germanNumber.trim();
    
    if (!trimmed) {
      return false;
    }

    return this.germanNumberPattern.test(trimmed);
  }

  /**
   * Add thousand separators to integer string
   * @param integerStr - Integer part as string
   * @returns String with thousand separators
   */
  private addThousandSeparators(integerStr: string): string {
    // Reverse the string
    const reversed = integerStr.split('').reverse().join('');
    
    // Add separator every 3 digits
    const parts: string[] = [];
    for (let i = 0; i < reversed.length; i += 3) {
      parts.push(reversed.substring(i, i + 3));
    }
    
    // Join with separator and reverse back
    return parts.join(this.thousandSeparator).split('').reverse().join('');
  }
}

// Singleton instance for convenience
export const germanFormatter = new GermanNumberFormatter();

// Convenience functions
export const formatGerman = (value: number | string, decimalPlaces?: number): string => {
  return germanFormatter.format(value, decimalPlaces);
};

export const parseGerman = (germanNumber: string): number => {
  return germanFormatter.parse(germanNumber);
};

export const formatCurrencyGerman = (
  amount: number | string,
  currencySymbol?: string
): string => {
  return germanFormatter.formatCurrency(amount, currencySymbol);
};

export const formatPercentGerman = (
  value: number | string,
  multiplyBy100?: boolean
): string => {
  return germanFormatter.formatPercent(value, multiplyBy100);
};

export const validateGerman = (germanNumber: string): boolean => {
  return germanFormatter.validate(germanNumber);
};
