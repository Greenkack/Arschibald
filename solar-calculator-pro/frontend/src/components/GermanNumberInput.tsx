/**
 * GermanNumberInput Component
 * 
 * Custom input component for German number format with bidirectional conversion.
 * Displays numbers in German format (1.234,56) while maintaining numeric values internally.
 * 
 * Requirements: 14.3, 14.6, 14.9
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { InputText, InputTextProps } from 'primereact/inputtext';
import { germanFormatter } from '../utils/germanNumberFormatter';

export interface GermanNumberInputProps extends Omit<InputTextProps, 'value' | 'onChange'> {
  value: number;
  onChange: (value: number) => void;
  label?: string;
  min?: number;
  max?: number;
  decimalPlaces?: number;
  showError?: boolean;
  errorMessage?: string;
  onValidationError?: (error: string) => void;
  className?: string;
  disabled?: boolean;
  placeholder?: string;
}

export const GermanNumberInput: React.FC<GermanNumberInputProps> = ({
  value,
  onChange,
  label,
  min,
  max,
  decimalPlaces = 2,
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
        const formatted = germanFormatter.format(value, decimalPlaces);
        setDisplayValue(formatted);
        setError('');
      } catch (err) {
        setError('Ungültiger Wert');
      }
    }
  }, [value, decimalPlaces, isFocused]);

  // Handle input change
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value;
    setDisplayValue(input);

    // Clear error while typing
    setError('');

    // Try to parse and validate
    try {
      if (!input || input === '-') {
        // Allow empty or just minus sign while typing
        return;
      }

      if (germanFormatter.validate(input)) {
        const numericValue = germanFormatter.parse(input);

        // Validate range
        if (min !== undefined && numericValue < min) {
          const errorMsg = `Wert muss mindestens ${germanFormatter.format(min, decimalPlaces)} sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          return;
        }

        if (max !== undefined && numericValue > max) {
          const errorMsg = `Wert darf höchstens ${germanFormatter.format(max, decimalPlaces)} sein`;
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
      // User might still be typing
    }
  }, [min, max, decimalPlaces, onChange, onValidationError]);

  // Handle blur - reformat to ensure consistent display
  const handleBlur = useCallback(() => {
    setIsFocused(false);

    try {
      if (!displayValue || displayValue === '-') {
        // Empty or just minus - reset to current value
        const formatted = germanFormatter.format(value, decimalPlaces);
        setDisplayValue(formatted);
        setError('');
        return;
      }

      if (germanFormatter.validate(displayValue)) {
        const numericValue = germanFormatter.parse(displayValue);

        // Validate range
        if (min !== undefined && numericValue < min) {
          const errorMsg = `Wert muss mindestens ${germanFormatter.format(min, decimalPlaces)} sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          // Reset to min value
          onChange(min);
          setDisplayValue(germanFormatter.format(min, decimalPlaces));
          return;
        }

        if (max !== undefined && numericValue > max) {
          const errorMsg = `Wert darf höchstens ${germanFormatter.format(max, decimalPlaces)} sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
          // Reset to max value
          onChange(max);
          setDisplayValue(germanFormatter.format(max, decimalPlaces));
          return;
        }

        // Valid - reformat for consistency
        onChange(numericValue);
        setDisplayValue(germanFormatter.format(numericValue, decimalPlaces));
        setError('');
      } else {
        // Invalid format - reset to current value
        const errorMsg = 'Ungültiges Zahlenformat. Erwartetes Format: 1.234,56';
        setError(errorMsg);
        if (onValidationError) {
          onValidationError(errorMsg);
        }
        setDisplayValue(germanFormatter.format(value, decimalPlaces));
      }
    } catch (err) {
      // Error parsing - reset to current value
      const errorMsg = err instanceof Error ? err.message : 'Fehler beim Parsen der Zahl';
      setError(errorMsg);
      if (onValidationError) {
        onValidationError(errorMsg);
      }
      setDisplayValue(germanFormatter.format(value, decimalPlaces));
    }
  }, [displayValue, value, min, max, decimalPlaces, onChange, onValidationError]);

  // Handle focus
  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

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

    // Allow minus only at start
    if (char === '-' && currentValue.length === 0) {
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
  }, [displayValue]);

  const inputClassName = `german-number-input ${className} ${error ? 'p-invalid' : ''}`.trim();

  return (
    <div className="german-number-input-wrapper">
      {label && (
        <label htmlFor={inputProps.id} className="german-number-input-label">
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
        placeholder={placeholder || '0,00'}
        style={{ textAlign: 'right', ...inputProps.style }}
      />
      {showError && (error || errorMessage) && (
        <small className="p-error german-number-input-error">
          {errorMessage || error}
        </small>
      )}
    </div>
  );
};

export default GermanNumberInput;
