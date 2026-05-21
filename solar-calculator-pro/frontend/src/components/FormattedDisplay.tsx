/**
 * Formatted Display Components
 * 
 * Components for displaying formatted numbers throughout the application.
 * All numbers are displayed with German locale formatting.
 * 
 * Requirements: 14.1, 14.2, 14.3
 */

import React from 'react';
import { useGlobalFormatting } from '../providers/GlobalFormattingProvider';

interface FormattedNumberProps {
  value: number;
  decimalPlaces?: number;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Formatted Number Display
 * 
 * Displays a number with German formatting (1.234,56)
 */
export const FormattedNumber: React.FC<FormattedNumberProps> = ({
  value,
  decimalPlaces,
  className,
  style,
}) => {
  const { formatNumber } = useGlobalFormatting();
  
  return (
    <span className={className} style={style}>
      {formatNumber(value, decimalPlaces)}
    </span>
  );
};

interface FormattedCurrencyProps {
  value: number;
  symbol?: string;
  position?: 'prefix' | 'suffix';
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Formatted Currency Display
 * 
 * Displays a currency value with German formatting (1.234,56 €)
 */
export const FormattedCurrency: React.FC<FormattedCurrencyProps> = ({
  value,
  symbol = '€',
  position = 'suffix',
  className,
  style,
}) => {
  const { formatCurrency } = useGlobalFormatting();
  
  return (
    <span className={className} style={style}>
      {formatCurrency(value, symbol, position)}
    </span>
  );
};

interface FormattedPercentProps {
  value: number;
  multiplyBy100?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Formatted Percent Display
 * 
 * Displays a percentage with German formatting (15,00 %)
 */
export const FormattedPercent: React.FC<FormattedPercentProps> = ({
  value,
  multiplyBy100 = true,
  className,
  style,
}) => {
  const { formatPercent } = useGlobalFormatting();
  
  return (
    <span className={className} style={style}>
      {formatPercent(value, multiplyBy100)}
    </span>
  );
};

interface FormattedLabelProps {
  label: string;
  value: number;
  type?: 'number' | 'currency' | 'percent';
  symbol?: string;
  decimalPlaces?: number;
  className?: string;
  labelClassName?: string;
  valueClassName?: string;
}

/**
 * Formatted Label with Value
 * 
 * Displays a label with a formatted value
 */
export const FormattedLabel: React.FC<FormattedLabelProps> = ({
  label,
  value,
  type = 'number',
  symbol = '€',
  decimalPlaces,
  className,
  labelClassName,
  valueClassName,
}) => {
  const { formatNumber, formatCurrency, formatPercent } = useGlobalFormatting();
  
  const getFormattedValue = () => {
    switch (type) {
      case 'currency':
        return formatCurrency(value, symbol);
      case 'percent':
        return formatPercent(value, true);
      default:
        return formatNumber(value, decimalPlaces);
    }
  };
  
  return (
    <div className={className}>
      <span className={labelClassName}>{label}: </span>
      <span className={valueClassName}>{getFormattedValue()}</span>
    </div>
  );
};

interface FormattedTableCellProps {
  value: number;
  type?: 'number' | 'currency' | 'percent';
  symbol?: string;
  decimalPlaces?: number;
  align?: 'left' | 'center' | 'right';
  className?: string;
}

/**
 * Formatted Table Cell
 * 
 * Displays a formatted number in a table cell
 */
export const FormattedTableCell: React.FC<FormattedTableCellProps> = ({
  value,
  type = 'number',
  symbol = '€',
  decimalPlaces,
  align = 'right',
  className,
}) => {
  const { formatNumber, formatCurrency, formatPercent } = useGlobalFormatting();
  
  const getFormattedValue = () => {
    switch (type) {
      case 'currency':
        return formatCurrency(value, symbol);
      case 'percent':
        return formatPercent(value, true);
      default:
        return formatNumber(value, decimalPlaces);
    }
  };
  
  return (
    <td className={className} style={{ textAlign: align }}>
      {getFormattedValue()}
    </td>
  );
};

interface FormattedCardValueProps {
  title: string;
  value: number;
  type?: 'number' | 'currency' | 'percent';
  symbol?: string;
  decimalPlaces?: number;
  subtitle?: string;
  icon?: React.ReactNode;
  className?: string;
}

/**
 * Formatted Card Value
 * 
 * Displays a formatted value in a card layout
 */
export const FormattedCardValue: React.FC<FormattedCardValueProps> = ({
  title,
  value,
  type = 'number',
  symbol = '€',
  decimalPlaces,
  subtitle,
  icon,
  className,
}) => {
  const { formatNumber, formatCurrency, formatPercent } = useGlobalFormatting();
  
  const getFormattedValue = () => {
    switch (type) {
      case 'currency':
        return formatCurrency(value, symbol);
      case 'percent':
        return formatPercent(value, true);
      default:
        return formatNumber(value, decimalPlaces);
    }
  };
  
  return (
    <div className={`formatted-card-value ${className || ''}`}>
      {icon && <div className="formatted-card-icon">{icon}</div>}
      <div className="formatted-card-content">
        <div className="formatted-card-title">{title}</div>
        <div className="formatted-card-value-text">{getFormattedValue()}</div>
        {subtitle && <div className="formatted-card-subtitle">{subtitle}</div>}
      </div>
    </div>
  );
};
