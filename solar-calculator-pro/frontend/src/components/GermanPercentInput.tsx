/**
 * GermanPercentInput Component
 * 
 * Custom input component for percentage values in German format.
 * Displays percentages with German number formatting (15,00 %).
 * 
 * Requirements: 14.3, 14.6, 14.9
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { InputText, InputTextProps } from 'primereact/inputtext';
import { germanFormatter } from '../utils/germanNumberFormatter';

export interface GermanPercentInputProps extends Omit<InputTextProps, 'value' | 'onChange'> {
  value: number;
  onChange: (value: number) => void;
  label?: string;
  min?: number;
  max?: number;
  multiplyBy100?: boolean;
  showError?: boolean;
  errorMessage?: string;
  onValidationError?: (error: string) => void;
  className?: string;
  disabled?: boolean;
  placeholder?: string;
}

export const GermanPercentInput: React.FC<GermanPercentInputProps> = ({
  value,
  onChange,
  label,
  min = 0,
  max = 100,
  multiplyBy100 = true,
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
        const formatted = germanFormatter.formatPercent(value, multiplyBy100);
        setDisplayValue(formatted);
        setError('');
      } catch (err) {
        setError('Ungültiger Prozentsatz');
      }
    }
  }, [value, multiplyBy100, isFocused]);

  // Extract numeric part from percent string
  const extractNumericPart = useCallback((percentString: string): string => {
    // Remove percent symbol and extra spaces
    let numeric = percentString.trim();
    
    // Remove percent symbol
    numeric = numeric.replace('%', '').trim();
    
    return numeric;
  }, []);

  // Get actual value for validation (considering multiplyBy100)
  const getActualValue = useCallback((numericValue: number): number => {
    return multiplyBy100 ? numericValue : numericValue * 100;
  }, [multiplyBy100]);

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
        const parsedValue = germanFormatter.parse(numericPart);
        const actualValue = getActualValue(parsedValue);

        // Validate range (always in percent 0-100)
        if (min !== undefined && actualValue < min) {
          const errorMsg = `Prozentsatz muss mindestens ${germanFormatter.format(min, 2)} % sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          return;
        }

        if (max !== undefined && actualValue > max) {
          const errorMsg = `Prozentsatz darf höchstens ${germanFormatter.format(max, 2)} % sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          return;
        }

        // Valid value - update parent with the value in the expected format
        const valueToStore = multiplyBy100 ? parsedValue / 100 : parsedValue;
        onChange(valueToStore);
      }
    } catch (err) {
      // Invalid format - don't update parent yet
    }
  }, [min, max, multiplyBy100, onChange, onValidationError, extractNumericPart, getActualValue]);

  // Handle blur - reformat to ensure consistent display
  const handleBlur = useCallback(() => {
    setIsFocused(false);

    try {
      const numericPart = extractNumericPart(displayValue);

      if (!numericPart || numericPart === '-') {
        // Empty or just minus - reset to current value
        const formatted = germanFormatter.formatPercent(value, multiplyBy100);
        setDisplayValue(formatted);
        setError('');
        return;
      }

      if (germanFormatter.validate(numericPart)) {
        const parsedValue = germanFormatter.parse(numericPart);
        const actualValue = getActualValue(parsedValue);

        // Validate range
        if (min !== undefined && actualValue < min) {
          const errorMsg = `Prozentsatz muss mindestens ${germanFormatter.format(min, 2)} % sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          // Reset to min value
          const minValue = multiplyBy100 ? min / 100 : min;
          onChange(minValue);
          setDisplayValue(germanFormatter.formatPercent(minValue, multiplyBy100));
          return;
        }

        if (max !== undefined && actualValue > max) {
          const errorMsg = `Prozentsatz darf höchstens ${germanFormatter.format(max, 2)} % sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          // Reset to max value
          const maxValue = multiplyBy100 ? max / 100 : max;
          onChange(maxValue);
          setDisplayValue(germanFormatter.formatPercent(maxValue, multiplyBy100));
          return;
        }

        // Valid - reformat for consistency
        const valueToStore = multiplyBy100 ? parsedValue / 100 : parsedValue;
        onChange(valueToStore);
        setDisplayValue(germanFormatter.formatPercent(valueToStore, multiplyBy100));
        setError('');
      } else {
        // Invalid format - reset to current value
        const errorMsg = 'Ungültiges Prozentformat. Erwartetes Format: 15,00 %';
        setError(errorMsg);
        if (onValidationError) {
          onValidationError(errorMsg);
        }
        setDisplayValue(germanFormatter.formatPercent(value, multiplyBy100));
      }
    } catch (err) {
      // Error parsing - reset to current value
      const errorMsg = err instanceof Error ? err.message : 'Fehler beim Parsen des Prozentsatzes';
      setError(errorMsg);
      if (onValidationError) {
        onValidationError(errorMsg);
      }
      setDisplayValue(germanFormatter.formatPercent(value, multiplyBy100));
    }
  }, [displayValue, value, min, max, multiplyBy100, onChange, onValidationError, extractNumericPart, getActualValue]);

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

  const inputClassName = `german-percent-input ${className} ${error ? 'p-invalid' : ''}`.trim();

  return (
    <div className="german-percent-input-wrapper">
      {label && (
        <label htmlFor={inputProps.id} className="german-percent-input-label">
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
        placeholder={placeholder || '0,00 %'}
        style={{ textAlign: 'right', ...inputProps.style }}
      />
      {showError && (error || errorMessage) && (
        <small className="p-error german-percent-input-error">
          {errorMessage || error}
        </small>
      )}
    </div>
  );
};

export default GermanPercentInput;
