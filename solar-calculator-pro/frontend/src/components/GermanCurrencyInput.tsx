/**
 * GermanCurrencyInput Component
 * 
 * Custom input component for currency values in German format.
 * Displays currency with symbol and German number formatting (1.234,56 €).
 * 
 * Requirements: 14.3, 14.6, 14.9
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { InputText, InputTextProps } from 'primereact/inputtext';
import { germanFormatter } from '../utils/germanNumberFormatter';

export interface GermanCurrencyInputProps extends Omit<InputTextProps, 'value' | 'onChange'> {
  value: number;
  onChange: (value: number) => void;
  label?: string;
  min?: number;
  max?: number;
  currencySymbol?: string;
  symbolPosition?: 'prefix' | 'suffix';
  showError?: boolean;
  errorMessage?: string;
  onValidationError?: (error: string) => void;
  className?: string;
  disabled?: boolean;
  placeholder?: string;
}

export const GermanCurrencyInput: React.FC<GermanCurrencyInputProps> = ({
  value,
  onChange,
  label,
  min = 0,
  max,
  currencySymbol = '€',
  symbolPosition = 'suffix',
  showError = true,
  errorMessage,
  onValidationError,
  className = '',
  disabled = false,
  placeholder,
  ...inputProps
}) => {
  const [displayValue, setDisplayValue] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isFocused, setIsFocused] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize display value from prop value
  useEffect(() => {
    if (!isFocused) {
      try {
        const formatted = germanFormatter.formatCurrency(value, currencySymbol, symbolPosition);
        setDisplayValue(formatted);
        setError('');
      } catch (err) {
        setError('Ungültiger Betrag');
      }
    }
  }, [value, currencySymbol, symbolPosition, isFocused]);

  // Extract numeric part from currency string
  const extractNumericPart = useCallback((currencyString: string): string => {
    // Remove currency symbol and extra spaces
    let numeric = currencyString.trim();
    
    // Remove currency symbol
    numeric = numeric.replace(currencySymbol, '').trim();
    
    return numeric;
  }, [currencySymbol]);

  // Handle input change
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value;
    setDisplayValue(input);

    // Clear error while typing
    setError('');

    try {
      // Extract numeric part
      const numericPart = extractNumericPart(input);

      if (!numericPart || numericPart === '-') {
        // Allow empty or just minus sign while typing
        return;
      }

      if (germanFormatter.validate(numericPart)) {
        const numericValue = germanFormatter.parse(numericPart);

        // Validate range
        if (min !== undefined && numericValue < min) {
          const errorMsg = `Betrag muss mindestens ${germanFormatter.formatCurrency(min, currencySymbol, symbolPosition)} sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          return;
        }

        if (max !== undefined && numericValue > max) {
          const errorMsg = `Betrag darf höchstens ${germanFormatter.formatCurrency(max, currencySymbol, symbolPosition)} sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          return;
        }

        // Valid value - update parent
        onChange(numericValue);
      }
    } catch (err) {
      // Invalid format - don't update parent yet
    }
  }, [min, max, currencySymbol, symbolPosition, onChange, onValidationError, extractNumericPart]);

  // Handle blur - reformat to ensure consistent display
  const handleBlur = useCallback(() => {
    setIsFocused(false);

    try {
      const numericPart = extractNumericPart(displayValue);

      if (!numericPart || numericPart === '-') {
        // Empty or just minus - reset to current value
        const formatted = germanFormatter.formatCurrency(value, currencySymbol, symbolPosition);
        setDisplayValue(formatted);
        setError('');
        return;
      }

      if (germanFormatter.validate(numericPart)) {
        const numericValue = germanFormatter.parse(numericPart);

        // Validate range
        if (min !== undefined && numericValue < min) {
          const errorMsg = `Betrag muss mindestens ${germanFormatter.formatCurrency(min, currencySymbol, symbolPosition)} sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          // Reset to min value
          onChange(min);
          setDisplayValue(germanFormatter.formatCurrency(min, currencySymbol, symbolPosition));
          return;
        }

        if (max !== undefined && numericValue > max) {
          const errorMsg = `Betrag darf höchstens ${germanFormatter.formatCurrency(max, currencySymbol, symbolPosition)} sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          // Reset to max value
          onChange(max);
          setDisplayValue(germanFormatter.formatCurrency(max, currencySymbol, symbolPosition));
          return;
        }

        // Valid - reformat for consistency
        onChange(numericValue);
        setDisplayValue(germanFormatter.formatCurrency(numericValue, currencySymbol, symbolPosition));
        setError('');
      } else {
        // Invalid format - reset to current value
        const errorMsg = 'Ungültiges Währungsformat. Erwartetes Format: 1.234,56 €';
        setError(errorMsg);
        if (onValidationError) {
          onValidationError(errorMsg);
        }
        setDisplayValue(germanFormatter.formatCurrency(value, currencySymbol, symbolPosition));
      }
    } catch (err) {
      // Error parsing - reset to current value
      const errorMsg = err instanceof Error ? err.message : 'Fehler beim Parsen des Betrags';
      setError(errorMsg);
      if (onValidationError) {
        onValidationError(errorMsg);
      }
      setDisplayValue(germanFormatter.formatCurrency(value, currencySymbol, symbolPosition));
    }
  }, [displayValue, value, min, max, currencySymbol, symbolPosition, onChange, onValidationError, extractNumericPart]);

  // Handle focus
  const handleFocus = useCallback(() => {
    setIsFocused(true);
    
    // On focus, show just the numeric part for easier editing
    const numericPart = extractNumericPart(displayValue);
    setDisplayValue(numericPart);
  }, [displayValue, extractNumericPart]);

  // Handle key press - allow only valid characters
  const handleKeyPress = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    const char = e.key;
    const currentValue = displayValue;

    // Allow control keys
    if (
      char === 'Backspace' ||
      char === 'Delete' ||
      char === 'Tab' ||
      char === 'ArrowLeft' ||
      char === 'ArrowRight' ||
      char === 'Home' ||
      char === 'End'
    ) {
      return;
    }

    // Allow minus only at start (if min allows negative)
    if (char === '-' && currentValue.length === 0 && (min === undefined || min < 0)) {
      return;
    }

    // Allow digits
    if (/\d/.test(char)) {
      return;
    }

    // Allow decimal separator (comma) only once
    if (char === ',' && !currentValue.includes(',')) {
      return;
    }

    // Allow thousand separator (dot)
    if (char === '.') {
      return;
    }

    // Block all other characters
    e.preventDefault();
  }, [displayValue, min]);

  const inputClassName = `german-currency-input ${className} ${error ? 'p-invalid' : ''}`.trim();

  return (
    <div className="german-currency-input-wrapper">
      {label && (
        <label htmlFor={inputProps.id} className="german-currency-input-label">
          {label}
        </label>
      )}
      <InputText
        {...inputProps}
        ref={inputRef}
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        onFocus={handleFocus}
        onKeyDown={handleKeyPress}
        className={inputClassName}
        disabled={disabled}
        placeholder={placeholder || `0,00 ${currencySymbol}`}
        style={{ textAlign: 'right', ...inputProps.style }}
      />
      {showError && (error || errorMessage) && (
        <small className="p-error german-currency-input-error">
          {errorMessage || error}
        </small>
      )}
    </div>
  );
};

export default GermanCurrencyInput;
