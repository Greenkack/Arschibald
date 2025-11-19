/**
 * Export Formatting Utilities
 * 
 * Utilities for applying German number formatting to exports (PDF, Excel, CSV).
 * Ensures all exported data maintains German locale formatting.
 * 
 * Requirements: 14.3
 */

import { germanFormatter } from './germanNumberFormatter';

/**
 * Format data for CSV export
 * 
 * Converts numeric values to German formatted strings for CSV export
 */
export const formatDataForCSV = (
  data: any[],
  numericFields: string[],
  fieldTypes?: Record<string, 'number' | 'currency' | 'percent'>,
  currencySymbol: string = '€'
): any[] => {
  return data.map(row => {
    const formattedRow = { ...row };
    
    numericFields.forEach(field => {
      const value = row[field];
      if (value !== null && value !== undefined && typeof value === 'number') {
        const type = fieldTypes?.[field] || 'number';
        
        switch (type) {
          case 'currency':
            formattedRow[field] = germanFormatter.formatCurrency(value, currencySymbol);
            break;
          case 'percent':
            formattedRow[field] = germanFormatter.formatPercent(value, true);
            break;
          default:
            formattedRow[field] = germanFormatter.format(value);
        }
      }
    });
    
    return formattedRow;
  });
};

/**
 * Format data for Excel export
 * 
 * Prepares data with German formatting for Excel export
 */
export const formatDataForExcel = (
  data: any[],
  numericFields: string[],
  fieldTypes?: Record<string, 'number' | 'currency' | 'percent'>,
  currencySymbol: string = '€'
): any[] => {
  return data.map(row => {
    const formattedRow = { ...row };
    
    numericFields.forEach(field => {
      const value = row[field];
      if (value !== null && value !== undefined && typeof value === 'number') {
        const type = fieldTypes?.[field] || 'number';
        
        // For Excel, we can either format as string or provide the raw number
        // with formatting instructions. Here we format as string for consistency.
        switch (type) {
          case 'currency':
            formattedRow[field] = germanFormatter.formatCurrency(value, currencySymbol);
            break;
          case 'percent':
            formattedRow[field] = germanFormatter.formatPercent(value, true);
            break;
          default:
            formattedRow[field] = germanFormatter.format(value);
        }
      }
    });
    
    return formattedRow;
  });
};

/**
 * Format data for PDF export
 * 
 * Prepares data with German formatting for PDF generation
 */
export const formatDataForPDF = (
  data: any[],
  numericFields: string[],
  fieldTypes?: Record<string, 'number' | 'currency' | 'percent'>,
  currencySymbol: string = '€'
): any[] => {
  return data.map(row => {
    const formattedRow = { ...row };
    
    numericFields.forEach(field => {
      const value = row[field];
      if (value !== null && value !== undefined && typeof value === 'number') {
        const type = fieldTypes?.[field] || 'number';
        
        switch (type) {
          case 'currency':
            formattedRow[field] = germanFormatter.formatCurrency(value, currencySymbol);
            break;
          case 'percent':
            formattedRow[field] = germanFormatter.formatPercent(value, true);
            break;
          default:
            formattedRow[field] = germanFormatter.format(value);
        }
      }
    });
    
    return formattedRow;
  });
};

/**
 * Format calculation results for export
 * 
 * Formats all numeric calculation results with German formatting
 */
export const formatCalculationResults = (
  results: Record<string, any>,
  numericFields: string[],
  fieldTypes?: Record<string, 'number' | 'currency' | 'percent'>,
  currencySymbol: string = '€'
): Record<string, any> => {
  const formattedResults = { ...results };
  
  numericFields.forEach(field => {
    const value = results[field];
    if (value !== null && value !== undefined && typeof value === 'number') {
      const type = fieldTypes?.[field] || 'number';
      
      switch (type) {
        case 'currency':
          formattedResults[field] = germanFormatter.formatCurrency(value, currencySymbol);
          break;
        case 'percent':
          formattedResults[field] = germanFormatter.formatPercent(value, true);
          break;
        default:
          formattedResults[field] = germanFormatter.format(value);
      }
    }
  });
  
  return formattedResults;
};

/**
 * Create CSV string with German formatting
 * 
 * Generates a CSV string with properly formatted numbers
 */
export const createFormattedCSV = (
  data: any[],
  headers: string[],
  numericFields: string[],
  fieldTypes?: Record<string, 'number' | 'currency' | 'percent'>,
  currencySymbol: string = '€'
): string => {
  const formattedData = formatDataForCSV(data, numericFields, fieldTypes, currencySymbol);
  
  // Create CSV header
  const csvHeader = headers.join(';') + '\n';
  
  // Create CSV rows
  const csvRows = formattedData.map(row => {
    return headers.map(header => {
      const value = row[header];
      // Escape values that contain semicolons or quotes
      if (typeof value === 'string' && (value.includes(';') || value.includes('"'))) {
        return `"${value.replace(/"/g, '""')}"`;
      }
      return value;
    }).join(';');
  }).join('\n');
  
  return csvHeader + csvRows;
};

/**
 * Format report data
 * 
 * Formats all numeric values in a report for display or export
 */
export const formatReportData = (
  report: Record<string, any>,
  numericFields: string[],
  fieldTypes?: Record<string, 'number' | 'currency' | 'percent'>,
  currencySymbol: string = '€'
): Record<string, any> => {
  const formattedReport = { ...report };
  
  // Format top-level numeric fields
  numericFields.forEach(field => {
    if (field in formattedReport) {
      const value = formattedReport[field];
      if (value !== null && value !== undefined && typeof value === 'number') {
        const type = fieldTypes?.[field] || 'number';
        
        switch (type) {
          case 'currency':
            formattedReport[field] = germanFormatter.formatCurrency(value, currencySymbol);
            break;
          case 'percent':
            formattedReport[field] = germanFormatter.formatPercent(value, true);
            break;
          default:
            formattedReport[field] = germanFormatter.format(value);
        }
      }
    }
  });
  
  // Format nested arrays
  Object.keys(formattedReport).forEach(key => {
    if (Array.isArray(formattedReport[key])) {
      formattedReport[key] = formatDataForPDF(
        formattedReport[key],
        numericFields,
        fieldTypes,
        currencySymbol
      );
    }
  });
  
  return formattedReport;
};

/**
 * Format summary statistics
 * 
 * Formats summary statistics (totals, averages, etc.) with German formatting
 */
export const formatSummaryStatistics = (
  statistics: Record<string, number>,
  fieldTypes?: Record<string, 'number' | 'currency' | 'percent'>,
  currencySymbol: string = '€'
): Record<string, string> => {
  const formattedStatistics: Record<string, string> = {};
  
  Object.entries(statistics).forEach(([field, value]) => {
    const type = fieldTypes?.[field] || 'number';
    
    switch (type) {
      case 'currency':
        formattedStatistics[field] = germanFormatter.formatCurrency(value, currencySymbol);
        break;
      case 'percent':
        formattedStatistics[field] = germanFormatter.formatPercent(value, true);
        break;
      default:
        formattedStatistics[field] = germanFormatter.format(value);
    }
  });
  
  return formattedStatistics;
};

/**
 * Export configuration for different formats
 */
export interface ExportConfig {
  format: 'csv' | 'excel' | 'pdf' | 'json';
  numericFields: string[];
  fieldTypes?: Record<string, 'number' | 'currency' | 'percent'>;
  currencySymbol?: string;
  headers?: string[];
  filename?: string;
}

/**
 * Format data based on export configuration
 */
export const formatDataForExport = (
  data: any[],
  config: ExportConfig
): any[] => {
  const { format, numericFields, fieldTypes, currencySymbol = '€' } = config;
  
  switch (format) {
    case 'csv':
      return formatDataForCSV(data, numericFields, fieldTypes, currencySymbol);
    case 'excel':
      return formatDataForExcel(data, numericFields, fieldTypes, currencySymbol);
    case 'pdf':
      return formatDataForPDF(data, numericFields, fieldTypes, currencySymbol);
    case 'json':
      // For JSON, we might want to keep raw numbers or format them
      // Here we format them for consistency
      return formatDataForPDF(data, numericFields, fieldTypes, currencySymbol);
    default:
      return data;
  }
};

/**
 * Download formatted data as CSV
 */
export const downloadFormattedCSV = (
  data: any[],
  headers: string[],
  numericFields: string[],
  filename: string = 'export.csv',
  fieldTypes?: Record<string, 'number' | 'currency' | 'percent'>,
  currencySymbol: string = '€'
): void => {
  const csvContent = createFormattedCSV(data, headers, numericFields, fieldTypes, currencySymbol);
  
  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
