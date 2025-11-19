/**
 * Table Formatting Utilities
 * 
 * Utilities for applying German number formatting to tables and data grids.
 * Supports PrimeReact DataTable, AG Grid, and other table libraries.
 * 
 * Requirements: 14.3
 */

import { germanFormatter } from './germanNumberFormatter';

/**
 * PrimeReact DataTable Body Template for Numbers
 * 
 * Usage:
 * <Column body={primeReactNumberBodyTemplate} />
 */
export const primeReactNumberBodyTemplate = (rowData: any, column: any): string => {
  const value = rowData[column.field];
  if (value === null || value === undefined) return '';
  return germanFormatter.format(value);
};

/**
 * PrimeReact DataTable Body Template for Currency
 */
export const primeReactCurrencyBodyTemplate = (symbol: string = '€') => {
  return (rowData: any, column: any): string => {
    const value = rowData[column.field];
    if (value === null || value === undefined) return '';
    return germanFormatter.formatCurrency(value, symbol);
  };
};

/**
 * PrimeReact DataTable Body Template for Percent
 */
export const primeReactPercentBodyTemplate = (rowData: any, column: any): string => {
  const value = rowData[column.field];
  if (value === null || value === undefined) return '';
  return germanFormatter.formatPercent(value, true);
};

/**
 * Create PrimeReact Column Configuration with German Formatting
 */
export const createPrimeReactColumnConfig = (
  field: string,
  header: string,
  type: 'number' | 'currency' | 'percent' = 'number',
  symbol: string = '€'
) => {
  const config: any = {
    field,
    header,
    sortable: true,
    style: { textAlign: 'right' },
  };

  switch (type) {
    case 'currency':
      config.body = primeReactCurrencyBodyTemplate(symbol);
      break;
    case 'percent':
      config.body = primeReactPercentBodyTemplate;
      break;
    default:
      config.body = primeReactNumberBodyTemplate;
  }

  return config;
};

/**
 * AG Grid Value Formatter for Numbers
 * 
 * Usage:
 * columnDefs: [
 *   { field: 'value', valueFormatter: agGridNumberFormatter }
 * ]
 */
export const agGridNumberFormatter = (params: any): string => {
  if (params.value === null || params.value === undefined) return '';
  return germanFormatter.format(params.value);
};

/**
 * AG Grid Value Formatter for Currency
 */
export const agGridCurrencyFormatter = (symbol: string = '€') => {
  return (params: any): string => {
    if (params.value === null || params.value === undefined) return '';
    return germanFormatter.formatCurrency(params.value, symbol);
  };
};

/**
 * AG Grid Value Formatter for Percent
 */
export const agGridPercentFormatter = (params: any): string => {
  if (params.value === null || params.value === undefined) return '';
  return germanFormatter.formatPercent(params.value, true);
};

/**
 * Create AG Grid Column Definition with German Formatting
 */
export const createAgGridColumnDef = (
  field: string,
  headerName: string,
  type: 'number' | 'currency' | 'percent' = 'number',
  symbol: string = '€'
) => {
  const columnDef: any = {
    field,
    headerName,
    sortable: true,
    filter: 'agNumberColumnFilter',
    cellStyle: { textAlign: 'right' },
  };

  switch (type) {
    case 'currency':
      columnDef.valueFormatter = agGridCurrencyFormatter(symbol);
      break;
    case 'percent':
      columnDef.valueFormatter = agGridPercentFormatter;
      break;
    default:
      columnDef.valueFormatter = agGridNumberFormatter;
  }

  return columnDef;
};

/**
 * Format table data for export
 * 
 * Converts numeric values in table data to German formatted strings
 */
export const formatTableDataForExport = (
  data: any[],
  numericFields: string[],
  fieldTypes?: Record<string, 'number' | 'currency' | 'percent'>,
  currencySymbol: string = '€'
): any[] => {
  return data.map(row => {
    const formattedRow = { ...row };
    
    numericFields.forEach(field => {
      const value = row[field];
      if (value !== null && value !== undefined) {
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
 * Format table cell value
 * 
 * Generic formatter for any table cell
 */
export const formatTableCell = (
  value: number,
  type: 'number' | 'currency' | 'percent' = 'number',
  symbol: string = '€',
  decimalPlaces?: number
): string => {
  if (value === null || value === undefined) return '';
  
  switch (type) {
    case 'currency':
      return germanFormatter.formatCurrency(value, symbol);
    case 'percent':
      return germanFormatter.formatPercent(value, true);
    default:
      return germanFormatter.format(value, decimalPlaces);
  }
};

/**
 * Create table column formatter function
 * 
 * Returns a formatter function for a specific column type
 */
export const createTableColumnFormatter = (
  type: 'number' | 'currency' | 'percent' = 'number',
  symbol: string = '€',
  decimalPlaces?: number
) => {
  return (value: number): string => {
    return formatTableCell(value, type, symbol, decimalPlaces);
  };
};

/**
 * Format table summary row
 * 
 * Formats numeric values in a summary/total row
 */
export const formatTableSummaryRow = (
  summaryData: Record<string, number>,
  fieldTypes: Record<string, 'number' | 'currency' | 'percent'>,
  currencySymbol: string = '€'
): Record<string, string> => {
  const formattedSummary: Record<string, string> = {};
  
  Object.entries(summaryData).forEach(([field, value]) => {
    const type = fieldTypes[field] || 'number';
    formattedSummary[field] = formatTableCell(value, type, currencySymbol);
  });
  
  return formattedSummary;
};

/**
 * React Table (TanStack Table) Cell Formatter
 * 
 * Usage:
 * columnHelper.accessor('value', {
 *   cell: reactTableNumberCell
 * })
 */
export const reactTableNumberCell = (info: any): string => {
  const value = info.getValue();
  if (value === null || value === undefined) return '';
  return germanFormatter.format(value);
};

/**
 * React Table Currency Cell Formatter
 */
export const reactTableCurrencyCell = (symbol: string = '€') => {
  return (info: any): string => {
    const value = info.getValue();
    if (value === null || value === undefined) return '';
    return germanFormatter.formatCurrency(value, symbol);
  };
};

/**
 * React Table Percent Cell Formatter
 */
export const reactTablePercentCell = (info: any): string => {
  const value = info.getValue();
  if (value === null || value === undefined) return '';
  return germanFormatter.formatPercent(value, true);
};

/**
 * Create React Table Column Definition with German Formatting
 */
export const createReactTableColumnDef = (
  accessorKey: string,
  header: string,
  type: 'number' | 'currency' | 'percent' = 'number',
  symbol: string = '€'
) => {
  const columnDef: any = {
    accessorKey,
    header,
    meta: {
      align: 'right',
    },
  };

  switch (type) {
    case 'currency':
      columnDef.cell = reactTableCurrencyCell(symbol);
      break;
    case 'percent':
      columnDef.cell = reactTablePercentCell;
      break;
    default:
      columnDef.cell = reactTableNumberCell;
  }

  return columnDef;
};
