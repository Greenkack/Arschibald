/**
 * Chart Formatting Utilities
 * 
 * Utilities for applying German number formatting to charts and graphs.
 * Supports Recharts, Chart.js, and other charting libraries.
 * 
 * Requirements: 14.3
 */

import { germanFormatter } from './germanNumberFormatter';

/**
 * Format number for chart axis
 */
export const formatChartAxis = (value: number, decimalPlaces: number = 2): string => {
  return germanFormatter.format(value, decimalPlaces);
};

/**
 * Format currency for chart axis
 */
export const formatChartAxisCurrency = (value: number, symbol: string = '€'): string => {
  return germanFormatter.formatCurrency(value, symbol);
};

/**
 * Format percent for chart axis
 */
export const formatChartAxisPercent = (value: number, multiplyBy100: boolean = true): string => {
  return germanFormatter.formatPercent(value, multiplyBy100);
};

/**
 * Recharts Tooltip Formatter
 * 
 * Usage:
 * <Tooltip formatter={rechartsTooltipFormatter} />
 */
export const rechartsTooltipFormatter = (
  value: number,
  name: string,
  props: any
): [string, string] => {
  const formattedValue = germanFormatter.format(value);
  return [formattedValue, name];
};

/**
 * Recharts Currency Tooltip Formatter
 */
export const rechartsCurrencyTooltipFormatter = (
  value: number,
  name: string,
  props: any,
  symbol: string = '€'
): [string, string] => {
  const formattedValue = germanFormatter.formatCurrency(value, symbol);
  return [formattedValue, name];
};

/**
 * Recharts Percent Tooltip Formatter
 */
export const rechartsPercentTooltipFormatter = (
  value: number,
  name: string,
  props: any
): [string, string] => {
  const formattedValue = germanFormatter.formatPercent(value, true);
  return [formattedValue, name];
};

/**
 * Recharts Axis Tick Formatter
 * 
 * Usage:
 * <XAxis tickFormatter={rechartsAxisTickFormatter} />
 */
export const rechartsAxisTickFormatter = (value: number): string => {
  return germanFormatter.format(value);
};

/**
 * Recharts Currency Axis Tick Formatter
 */
export const rechartsCurrencyAxisTickFormatter = (value: number, symbol: string = '€'): string => {
  return germanFormatter.formatCurrency(value, symbol);
};

/**
 * Recharts Percent Axis Tick Formatter
 */
export const rechartsPercentAxisTickFormatter = (value: number): string => {
  return germanFormatter.formatPercent(value, true);
};

/**
 * Recharts Label Formatter
 * 
 * Usage:
 * <Label formatter={rechartsLabelFormatter} />
 */
export const rechartsLabelFormatter = (value: number): string => {
  return germanFormatter.format(value);
};

/**
 * Chart.js Tooltip Callback
 * 
 * Usage:
 * tooltips: {
 *   callbacks: {
 *     label: chartJsTooltipCallback
 *   }
 * }
 */
export const chartJsTooltipCallback = (tooltipItem: any): string => {
  const value = tooltipItem.parsed.y || tooltipItem.parsed;
  return germanFormatter.format(value);
};

/**
 * Chart.js Currency Tooltip Callback
 */
export const chartJsCurrencyTooltipCallback = (tooltipItem: any, symbol: string = '€'): string => {
  const value = tooltipItem.parsed.y || tooltipItem.parsed;
  return germanFormatter.formatCurrency(value, symbol);
};

/**
 * Chart.js Percent Tooltip Callback
 */
export const chartJsPercentTooltipCallback = (tooltipItem: any): string => {
  const value = tooltipItem.parsed.y || tooltipItem.parsed;
  return germanFormatter.formatPercent(value, true);
};

/**
 * Chart.js Axis Tick Callback
 * 
 * Usage:
 * scales: {
 *   y: {
 *     ticks: {
 *       callback: chartJsAxisTickCallback
 *     }
 *   }
 * }
 */
export const chartJsAxisTickCallback = (value: number): string => {
  return germanFormatter.format(value);
};

/**
 * Chart.js Currency Axis Tick Callback
 */
export const chartJsCurrencyAxisTickCallback = (value: number, symbol: string = '€'): string => {
  return germanFormatter.formatCurrency(value, symbol);
};

/**
 * Chart.js Percent Axis Tick Callback
 */
export const chartJsPercentAxisTickCallback = (value: number): string => {
  return germanFormatter.formatPercent(value, true);
};

/**
 * Plotly Format Configuration
 * 
 * Returns Plotly-compatible format configuration for German locale
 */
export const getPlotlyFormatConfig = () => {
  return {
    separators: ',.',  // decimal separator, thousands separator
    locale: 'de-DE',
  };
};

/**
 * Plotly Hover Template for Numbers
 * 
 * Usage:
 * hovertemplate: getPlotlyHoverTemplate('Wert')
 */
export const getPlotlyHoverTemplate = (label: string): string => {
  return `${label}: %{y:,.2f}<extra></extra>`;
};

/**
 * Plotly Hover Template for Currency
 */
export const getPlotlyCurrencyHoverTemplate = (label: string, symbol: string = '€'): string => {
  return `${label}: %{y:,.2f} ${symbol}<extra></extra>`;
};

/**
 * Plotly Hover Template for Percent
 */
export const getPlotlyPercentHoverTemplate = (label: string): string => {
  return `${label}: %{y:,.2f} %<extra></extra>`;
};

/**
 * Format data for chart display
 * 
 * Converts an array of numbers to formatted strings
 */
export const formatChartData = (
  data: number[],
  type: 'number' | 'currency' | 'percent' = 'number',
  symbol: string = '€'
): string[] => {
  return data.map(value => {
    switch (type) {
      case 'currency':
        return germanFormatter.formatCurrency(value, symbol);
      case 'percent':
        return germanFormatter.formatPercent(value, true);
      default:
        return germanFormatter.format(value);
    }
  });
};

/**
 * Create Recharts configuration with German formatting
 */
export const createRechartsConfig = (type: 'number' | 'currency' | 'percent' = 'number', symbol: string = '€') => {
  const config: any = {
    tooltip: {},
    xAxis: {},
    yAxis: {},
  };

  switch (type) {
    case 'currency':
      config.tooltip.formatter = (value: number, name: string, props: any) =>
        rechartsCurrencyTooltipFormatter(value, name, props, symbol);
      config.yAxis.tickFormatter = (value: number) => rechartsCurrencyAxisTickFormatter(value, symbol);
      break;
    case 'percent':
      config.tooltip.formatter = rechartsPercentTooltipFormatter;
      config.yAxis.tickFormatter = rechartsPercentAxisTickFormatter;
      break;
    default:
      config.tooltip.formatter = rechartsTooltipFormatter;
      config.yAxis.tickFormatter = rechartsAxisTickFormatter;
  }

  return config;
};

/**
 * Create Chart.js configuration with German formatting
 */
export const createChartJsConfig = (type: 'number' | 'currency' | 'percent' = 'number', symbol: string = '€') => {
  const config: any = {
    plugins: {
      tooltip: {
        callbacks: {},
      },
    },
    scales: {
      y: {
        ticks: {
          callback: null,
        },
      },
    },
  };

  switch (type) {
    case 'currency':
      config.plugins.tooltip.callbacks.label = (tooltipItem: any) =>
        chartJsCurrencyTooltipCallback(tooltipItem, symbol);
      config.scales.y.ticks.callback = (value: number) => chartJsCurrencyAxisTickCallback(value, symbol);
      break;
    case 'percent':
      config.plugins.tooltip.callbacks.label = chartJsPercentTooltipCallback;
      config.scales.y.ticks.callback = chartJsPercentAxisTickCallback;
      break;
    default:
      config.plugins.tooltip.callbacks.label = chartJsTooltipCallback;
      config.scales.y.ticks.callback = chartJsAxisTickCallback;
  }

  return config;
};
