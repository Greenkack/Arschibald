/**
 * GermanNumberInputModern Component
 * 
 * Custom input component for German number format with bidirectional conversion.
 * Displays numbers in German format (1.234,56) while maintaining numeric values internally.
 * Migrated from PrimeReact to shadcn/ui.
 * 
 * Requirements: 14.3, 14.6, 14.9
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { germanFormatter } from '../utils/germanNumberFormatter';
import { cn } from '@/lib/utils';

export interface GermanNumberInputModernProps {
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
  id?: string;
}

export const GermanNumberInputModern: React.FC<GermanNumberInputModernProps> = ({
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
  id,
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
    setError('');

    try {
      if (!input || input === '-') {
        return;
      }

      if (germanFormatter.validate(input)) {
        const numericValue = germanFormatter.parse(input);

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

        onChange(numericValue);
      }
    } catch (err) {
      // Invalid format - don't update parent yet
    }
  }, [min, max, decimalPlaces, onChange, onValidationError]);

  // Handle blur - reformat to ensure consistent display
  const handleBlur = useCallback(() => {
    setIsFocused(false);

    try {
      if (!displayValue || displayValue === '-') {
        const formatted = germanFormatter.format(value, decimalPlaces);
        setDisplayValue(formatted);
        setError('');
        return;
      }

      if (germanFormatter.validate(displayValue)) {
        const numericValue = germanFormatter.parse(displayValue);

        if (min !== undefined && numericValue < min) {
          const errorMsg = `Wert muss mindestens ${germanFormatter.format(min, decimalPlaces)} sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
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
          onChange(max);
          setDisplayValue(germanFormatter.format(max, decimalPlaces));
          return;
        }

        onChange(numericValue);
        setDisplayValue(germanFormatter.format(numericValue, decimalPlaces));
        setError('');
      } else {
        const errorMsg = 'Ungültiges Zahlenformat. Erwartetes Format: 1.234,56';
        setError(errorMsg);
        if (onValidationError) {
          onValidationError(errorMsg);
        }
        setDisplayValue(germanFormatter.format(value, decimalPlaces));
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Fehler beim Parsen der Zahl';
      setError(errorMsg);
      if (onValidationError) {
        onValidationError(errorMsg);
      }
      setDisplayValue(germanFormatter.format(value, decimalPlaces));
    }
  }, [displayValue, value, min, max, decimalPlaces, onChange, onValidationError]);

  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const handleKeyPress = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    const char = e.key;
    const currentValue = displayValue;

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

    if (char === '-' && currentValue.length === 0) {
      return;
    }

    if (/\d/.test(char)) {
      return;
    }

    if (char === ',' && !currentValue.includes(',')) {
      return;
    }

    if (char === '.') {
      return;
    }

    e.preventDefault();
  }, [displayValue]);

  return (
    <div className="space-y-2">
      {label && (
        <Label htmlFor={id} className="text-sm font-medium">
          {label}
        </Label>
      )}
      <Input
        id={id}
        ref={inputRef}
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        onFocus={handleFocus}
        onKeyDown={handleKeyPress}
        className={cn('text-right', className, { 'border-destructive': error })}
        disabled={disabled}
        placeholder={placeholder || '0,00'}
      />
      {showError && (error || errorMessage) && (
        <p className="text-sm text-destructive">
          {errorMessage || error}
        </p>
      )}
    </div>
  );
};

export default GermanNumberInputModern;
