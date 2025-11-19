/**
 * Global Formatting Provider
 * 
 * Provides German number formatting context to the entire application.
 * Ensures all numbers are displayed with German locale formatting:
 * - Dot (.) as thousand separator
 * - Comma (,) as decimal separator
 * - Exactly 2 decimal places
 * 
 * Requirements: 14.1, 14.2, 14.3
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { germanFormatter } from '../utils/germanNumberFormatter';

interface FormattingContextType {
  // Format functions
  formatNumber: (value: number, decimalPlaces?: number) => string;
  formatCurrency: (value: number, symbol?: string, position?: 'prefix' | 'suffix') => string;
  formatPercent: (value: number, multiplyBy100?: boolean) => string;
  
  // Parse functions
  parseNumber: (value: string) => number;
  
  // Validation
  validateNumber: (value: string) => boolean;
  
  // Configuration
  locale: string;
  decimalSeparator: string;
  thousandSeparator: string;
  defaultDecimalPlaces: number;
}

const FormattingContext = createContext<FormattingContextType | undefined>(undefined);

interface GlobalFormattingProviderProps {
  children: ReactNode;
  locale?: string;
  defaultDecimalPlaces?: number;
}

/**
 * Global Formatting Provider Component
 * 
 * Wraps the entire application to provide consistent German number formatting.
 */
export const GlobalFormattingProvider: React.FC<GlobalFormattingProviderProps> = ({
  children,
  locale = 'de-DE',
  defaultDecimalPlaces = 2,
}) => {
  const contextValue: FormattingContextType = {
    // Format functions
    formatNumber: (value: number, decimalPlaces = defaultDecimalPlaces) => {
      return germanFormatter.format(value, decimalPlaces);
    },
    
    formatCurrency: (value: number, symbol = '€', position = 'suffix') => {
      return germanFormatter.formatCurrency(value, symbol, position);
    },
    
    formatPercent: (value: number, multiplyBy100 = true) => {
      return germanFormatter.formatPercent(value, multiplyBy100);
    },
    
    // Parse functions
    parseNumber: (value: string) => {
      return germanFormatter.parse(value);
    },
    
    // Validation
    validateNumber: (value: string) => {
      return germanFormatter.validate(value);
    },
    
    // Configuration
    locale,
    decimalSeparator: ',',
    thousandSeparator: '.',
    defaultDecimalPlaces,
  };

  return (
    <FormattingContext.Provider value={contextValue}>
      {children}
    </FormattingContext.Provider>
  );
};

/**
 * Hook to use global formatting context
 * 
 * @returns Formatting context with all formatting functions
 * @throws Error if used outside of GlobalFormattingProvider
 */
export const useGlobalFormatting = (): FormattingContextType => {
  const context = useContext(FormattingContext);
  
  if (!context) {
    throw new Error('useGlobalFormatting must be used within a GlobalFormattingProvider');
  }
  
  return context;
};

/**
 * HOC to inject formatting props into a component
 */
export function withGlobalFormatting<P extends object>(
  Component: React.ComponentType<P & { formatting: FormattingContextType }>
) {
  return (props: P) => {
    const formatting = useGlobalFormatting();
    return <Component {...props} formatting={formatting} />;
  };
}
