/**
 * GermanSlider Component
 * 
 * Custom slider component with German number formatting for display values.
 * Shows formatted values (1.234,56) while maintaining numeric values internally.
 * 
 * Requirements: 14.3, 14.6, 14.9
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Slider, SliderProps } from 'primereact/slider';
import { germanFormatter } from '../utils/germanNumberFormatter';

export interface GermanSliderProps extends Omit<SliderProps, 'value' | 'onChange'> {
  value: number | number[];
  onChange: (value: number | number[]) => void;
  label?: string;
  min?: number;
  max?: number;
  step?: number;
  decimalPlaces?: number;
  showValue?: boolean;
  showMinMax?: boolean;
  formatType?: 'number' | 'currency' | 'percent';
  currencySymbol?: string;
  className?: string;
  disabled?: boolean;
  range?: boolean;
}

export const GermanSlider: React.FC<GermanSliderProps> = ({
  value,
  onChange,
  label,
  min = 0,
  max = 100,
  step = 1,
  decimalPlaces = 2,
  showValue = true,
  showMinMax = true,
  formatType = 'number',
  currencySymbol = '€',
  className = '',
  disabled = false,
  range = false,
  ...sliderProps
}) => {
  const [isDragging, setIsDragging] = useState<boolean>(false);

  // Format value based on type
  const formatValue = useCallback((val: number): string => {
    switch (formatType) {
      case 'currency':
        return germanFormatter.formatCurrency(val, currencySymbol);
      case 'percent':
        return germanFormatter.formatPercent(val, false); // Don't multiply by 100
      case 'number':
      default:
        return germanFormatter.format(val, decimalPlaces);
    }
  }, [formatType, currencySymbol, decimalPlaces]);

  // Format display value(s)
  const displayValue = useMemo(() => {
    if (Array.isArray(value)) {
      return value.map(v => formatValue(v)).join(' - ');
    }
    return formatValue(value);
  }, [value, formatValue]);

  // Format min/max values
  const displayMin = useMemo(() => formatValue(min), [min, formatValue]);
  const displayMax = useMemo(() => formatValue(max), [max, formatValue]);

  // Handle slider change
  const handleChange = useCallback((e: { value: number | number[] }) => {
    onChange(e.value);
  }, [onChange]);

  // Handle slide start
  const handleSlideStart = useCallback(() => {
    setIsDragging(true);
  }, []);

  // Handle slide end
  const handleSlideEnd = useCallback(() => {
    setIsDragging(false);
  }, []);

  const sliderClassName = `german-slider ${className} ${isDragging ? 'dragging' : ''}`.trim();

  return (
    <div className="german-slider-wrapper">
      {label && (
        <div className="german-slider-header">
          <label className="german-slider-label">{label}</label>
          {showValue && (
            <span className="german-slider-value">{displayValue}</span>
          )}
        </div>
      )}
      
      <div className="german-slider-container">
        {showMinMax && (
          <span className="german-slider-min">{displayMin}</span>
        )}
        
        <Slider
          {...sliderProps}
          value={value}
          onChange={handleChange}
          onSlideStart={handleSlideStart}
          onSlideEnd={handleSlideEnd}
          min={min}
          max={max}
          step={step}
          className={sliderClassName}
          disabled={disabled}
          range={range}
        />
        
        {showMinMax && (
          <span className="german-slider-max">{displayMax}</span>
        )}
      </div>
      
      {!label && showValue && (
        <div className="german-slider-value-bottom">
          {displayValue}
        </div>
      )}
    </div>
  );
};

export default GermanSlider;
