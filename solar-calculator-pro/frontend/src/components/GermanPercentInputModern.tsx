/**
 * GermanPercentInputModern Component
 * 
 * Custom input component for percentage values in German format.
 * Displays percentages with German number formatting (15,00 %).
 * Migrated from PrimeReact to shadcn/ui.
 * 
 * Requirements: 14.3, 14.6, 14.9
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { germanFormatter } from '../utils/germanNumberFormatter';
import { cn } from '@/lib/utils';

export interface GermanPercentInputModernProps {
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
  id?: string;
}

export const GermanPercentInputModern: React.FC<GermanPercentInputModernProps> = ({
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
  id,
}) => {
  const [displayValue, setDisplayValue] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isFocused, setIsFocused] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement>(null);

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

  const extractNumericPart = useCallback((percentString: string): string => {
    let numeric = percentString.trim();
    numeric = numeric.replace('%', '').trim();
    return numeric;
  }, []);

  const getActualValue = useCallback((numericValue: number): number => {
    return multiplyBy100 ? numericValue : numericValue * 100;
  }, [multiplyBy100]);

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
        const parsedValue = germanFormatter.parse(numericPart);
        const actualValue = getActualValue(parsedValue);

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

        const valueToStore = multiplyBy100 ? parsedValue / 100 : parsedValue;
        onChange(valueToStore);
      }
    } catch (err) {
      // Invalid format
    }
  }, [min, max, multiplyBy100, onChange, onValidationError, extractNumericPart, getActualValue]);

  const handleBlur = useCallback(() => {
    setIsFocused(false);

    try {
      const numericPart = extractNumericPart(displayValue);

      if (!numericPart || numericPart === '-') {
        const formatted = germanFormatter.formatPercent(value, multiplyBy100);
        setDisplayValue(formatted);
        setError('');
        return;
      }

      if (germanFormatter.validate(numericPart)) {
        const parsedValue = germanFormatter.parse(numericPart);
        const actualValue = getActualValue(parsedValue);

        if (min !== undefined && actualValue < min) {
          const errorMsg = `Prozentsatz muss mindestens ${germanFormatter.format(min, 2)} % sein`;
          setError(errorMsg);
          if (onValidationError) {
            onValidationError(errorMsg);
          }
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
          const maxValue = multiplyBy100 ? max / 100 : max;
          onChange(maxValue);
          setDisplayValue(germanFormatter.formatPercent(maxValue, multiplyBy100));
          return;
        }

        const valueToStore = multiplyBy100 ? parsedValue / 100 : parsedValue;
        onChange(valueToStore);
        setDisplayValue(germanFormatter.formatPercent(valueToStore, multiplyBy100));
        setError('');
      } else {
        const errorMsg = 'Ungültiges Prozentformat. Erwartetes Format: 15,00 %';
        setError(errorMsg);
        if (onValidationError) {
          onValidationError(errorMsg);
        }
        setDisplayValue(germanFormatter.formatPercent(value, multiplyBy100));
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Fehler beim Parsen des Prozentsatzes';
      setError(errorMsg);
      if (onValidationError) {
        onValidationError(errorMsg);
      }
      setDisplayValue(germanFormatter.formatPercent(value, multiplyBy100));
    }
  }, [displayValue, value, min, max, multiplyBy100, onChange, onValidationError, extractNumericPart, getActualValue]);

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
        placeholder={placeholder || '0,00 %'}
      />
      {showError && (error || errorMessage) && (
        <p className="text-sm text-destructive">
          {errorMessage || error}
        </p>
      )}
    </div>
  );
};

export default GermanPercentInputModern;
