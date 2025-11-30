/**
 * GermanCurrencyInputModern Component
 * 
 * Custom input component for currency values in German format.
 * Displays currency with symbol and German number formatting (1.234,56 €).
 * Migrated from PrimeReact to shadcn/ui.
 * 
 * Requirements: 14.3, 14.6, 14.9
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { germanFormatter } from '../utils/germanNumberFormatter';
import { cn } from '@/lib/utils';

export interface GermanCurrencyInputModernProps {
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
  id?: string;
}

export const GermanCurrencyInputModern: React.FC<GermanCurrencyInputModernProps> = ({
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
  id,
}) => {
  const [displayValue, setDisplayValue] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isFocused, setIsFocused] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement>(null);

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

  const extractNumericPart = useCallback((currencyString: string): string => {
    let numeric = currencyString.trim();
    numeric = numeric.replace(currencySymbol, '').trim();
    return numeric;
  }, [currencySymbol]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value;
    setDisplayValue(input);
    setError('');

    try {
      const numericPart = extractNumericPart(input);

      if (!numericPart || numericPart === '-') {
        return;
      }

      if (germanFormatter.validate(numericPart)) {
        const numericValue = germanFormatter.parse(numericPart);

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

        onChange(numericValue);
      }
    } catch (err) {
      // Invalid format
    }
  }, [min, max, currencySymbol, symbolPosition, onChange, onValidationError, extractNumericPart]);

  const handleBlur = useCallback(() => {
    setIsFocused(false);

    try {
      const numericPart = extractNumericPart(displayValue);

      if (!numericPart || numericPart === '-') {
        const formatted = germanFormatter.formatCurrency(value, currencySymbol, symbolPosition);
        setDisplayValue(formatted);
        setError('');
        return;
      }

      if (germanFormatter.validate(numericPart)) {
        const numericValue = germanFormatter.parse(numericPart);

        if (min !== undefined && numericValue < min) {
          const errorMsg = `Betrag muss mindestens ${germanFormatter.formatCurrency(min, currencySymbol, symbolPosition)} sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
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
          onChange(max);
          setDisplayValue(germanFormatter.formatCurrency(max, currencySymbol, symbolPosition));
          return;
        }

        onChange(numericValue);
        setDisplayValue(germanFormatter.formatCurrency(numericValue, currencySymbol, symbolPosition));
        setError('');
      } else {
        const errorMsg = 'Ungültiges Währungsformat. Erwartetes Format: 1.234,56 €';
        setError(errorMsg);
        if (onValidationError) {
          onValidationError(errorMsg);
        }
        setDisplayValue(germanFormatter.formatCurrency(value, currencySymbol, symbolPosition));
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Fehler beim Parsen des Betrags';
      setError(errorMsg);
      if (onValidationError) {
        onValidationError(errorMsg);
      }
      setDisplayValue(germanFormatter.formatCurrency(value, currencySymbol, symbolPosition));
    }
  }, [displayValue, value, min, max, currencySymbol, symbolPosition, onChange, onValidationError, extractNumericPart]);

  const handleFocus = useCallback(() => {
    setIsFocused(true);
    const numericPart = extractNumericPart(displayValue);
    setDisplayValue(numericPart);
  }, [displayValue, extractNumericPart]);

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

    if (char === '-' && currentValue.length === 0 && (min === undefined || min < 0)) {
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
  }, [displayValue, min]);

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
        placeholder={placeholder || `0,00 ${currencySymbol}`}
      />
      {showError && (error || errorMessage) && (
        <p className="text-sm text-destructive">
          {errorMessage || error}
        </p>
      )}
    </div>
  );
};

export default GermanCurrencyInputModern;
