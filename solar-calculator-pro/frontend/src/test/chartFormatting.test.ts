/**
 * Chart Formatting Tests
 * 
 * Tests for German number formatting in charts and visualizations.
 * 
 * Requirements: 14.3
 * Task: 218 - Chart and Visualization Formatting
 */

import {
  formatChartAxis,
  formatChartAxisCurrency,
  formatChartAxisPercent,
  rechartsTooltipFormatter,
  rechartsCurrencyTooltipFormatter,
  rechartsPercentTooltipFormatter,
  rechartsAxisTickFormatter,
  rechartsCurrencyAxisTickFormatter,
  rechartsPercentAxisTickFormatter,
  rechartsLabelFormatter,
  chartJsTooltipCallback,
  chartJsCurrencyTooltipCallback,
  chartJsPercentTooltipCallback,
  chartJsAxisTickCallback,
  chartJsCurrencyAxisTickCallback,
  chartJsPercentAxisTickCallback,
  getPlotlyFormatConfig,
  getPlotlyHoverTemplate,
  getPlotlyCurrencyHoverTemplate,
  getPlotlyPercentHoverTemplate,
  formatChartData,
  createRechartsConfig,
  createChartJsConfig,
} from '../utils/chartFormatting';

describe('Chart Formatting - Basic Functions', () => {
  describe('formatChartAxis', () => {
    it('formats numbers with German locale', () => {
      expect(formatChartAxis(1234.56)).toBe('1.234,56');
      expect(formatChartAxis(1234567.89)).toBe('1.234.567,89');
      expect(formatChartAxis(0.5)).toBe('0,50');
    });

    it('formats with custom decimal places', () => {
      expect(formatChartAxis(1234.567, 3)).toBe('1.234,567');
      expect(formatChartAxis(1234.5, 1)).toBe('1.234,5');
    });

    it('handles zero and negative numbers', () => {
      expect(formatChartAxis(0)).toBe('0,00');
      expect(formatChartAxis(-1234.56)).toBe('-1.234,56');
    });
  });

  describe('formatChartAxisCurrency', () => {
    it('formats currency with German locale', () => {
      expect(formatChartAxisCurrency(1234.56, '€')).toBe('1.234,56 €');
      expect(formatChartAxisCurrency(15000, '€')).toBe('15.000,00 €');
    });

    it('handles different currency symbols', () => {
      expect(formatChartAxisCurrency(1234.56, '$')).toBe('1.234,56 $');
      expect(formatChartAxisCurrency(1234.56, 'CHF')).toBe('1.234,56 CHF');
    });

    it('handles zero and negative amounts', () => {
      expect(formatChartAxisCurrency(0, '€')).toBe('0,00 €');
      expect(formatChartAxisCurrency(-1234.56, '€')).toBe('-1.234,56 €');
    });
  });

  describe('formatChartAxisPercent', () => {
    it('formats percentages with German locale', () => {
      expect(formatChartAxisPercent(0.35, true)).toBe('35,00 %');
      expect(formatChartAxisPercent(0.1234, true)).toBe('12,34 %');
    });

    it('handles values already in percent', () => {
      expect(formatChartAxisPercent(35, false)).toBe('35,00 %');
      expect(formatChartAxisPercent(12.34, false)).toBe('12,34 %');
    });

    it('handles zero and negative percentages', () => {
      expect(formatChartAxisPercent(0, true)).toBe('0,00 %');
      expect(formatChartAxisPercent(-0.15, true)).toBe('-15,00 %');
    });
  });
});

describe('Chart Formatting - Recharts', () => {
  describe('rechartsAxisTickFormatter', () => {
    it('formats axis tick values', () => {
      expect(rechartsAxisTickFormatter(1234.56)).toBe('1.234,56');
      expect(rechartsAxisTickFormatter(450.5)).toBe('450,50');
    });
  });

  describe('rechartsCurrencyAxisTickFormatter', () => {
    it('formats currency axis ticks', () => {
      expect(rechartsCurrencyAxisTickFormatter(1234.56, '€')).toBe('1.234,56 €');
      expect(rechartsCurrencyAxisTickFormatter(8500.50, '€')).toBe('8.500,50 €');
    });
  });

  describe('rechartsPercentAxisTickFormatter', () => {
    it('formats percent axis ticks', () => {
      expect(rechartsPercentAxisTickFormatter(0.35)).toBe('35,00 %');
      expect(rechartsPercentAxisTickFormatter(0.1234)).toBe('12,34 %');
    });
  });

  describe('rechartsTooltipFormatter', () => {
    it('formats tooltip values', () => {
      const [formattedValue, name] = rechartsTooltipFormatter(1234.56, 'Production', {});
      expect(formattedValue).toBe('1.234,56');
      expect(name).toBe('Production');
    });
  });

  describe('rechartsCurrencyTooltipFormatter', () => {
    it('formats currency tooltip values', () => {
      const [formattedValue, name] = rechartsCurrencyTooltipFormatter(
        1234.56,
        'Cost',
        {},
        '€'
      );
      expect(formattedValue).toBe('1.234,56 €');
      expect(name).toBe('Cost');
    });
  });

  describe('rechartsPercentTooltipFormatter', () => {
    it('formats percent tooltip values', () => {
      const [formattedValue, name] = rechartsPercentTooltipFormatter(0.35, 'Efficiency', {});
      expect(formattedValue).toBe('35,00 %');
      expect(name).toBe('Efficiency');
    });
  });

  describe('rechartsLabelFormatter', () => {
    it('formats label values', () => {
      expect(rechartsLabelFormatter(1234.56)).toBe('1.234,56');
    });
  });

  describe('createRechartsConfig', () => {
    it('creates number configuration', () => {
      const config = createRechartsConfig('number');
      expect(config).toHaveProperty('tooltip');
      expect(config).toHaveProperty('yAxis');
      expect(config.yAxis.tickFormatter(1234.56)).toBe('1.234,56');
    });

    it('creates currency configuration', () => {
      const config = createRechartsConfig('currency', '€');
      expect(config.yAxis.tickFormatter(1234.56)).toBe('1.234,56 €');
    });

    it('creates percent configuration', () => {
      const config = createRechartsConfig('percent');
      expect(config.yAxis.tickFormatter(0.35)).toBe('35,00 %');
    });
  });
});

describe('Chart Formatting - Chart.js', () => {
  describe('chartJsAxisTickCallback', () => {
    it('formats axis tick values', () => {
      expect(chartJsAxisTickCallback(1234.56)).toBe('1.234,56');
    });
  });

  describe('chartJsCurrencyAxisTickCallback', () => {
    it('formats currency axis ticks', () => {
      expect(chartJsCurrencyAxisTickCallback(1234.56, '€')).toBe('1.234,56 €');
    });
  });

  describe('chartJsPercentAxisTickCallback', () => {
    it('formats percent axis ticks', () => {
      expect(chartJsPercentAxisTickCallback(0.35)).toBe('35,00 %');
    });
  });

  describe('chartJsTooltipCallback', () => {
    it('formats tooltip values', () => {
      const tooltipItem = { parsed: { y: 1234.56 } };
      expect(chartJsTooltipCallback(tooltipItem)).toBe('1.234,56');
    });

    it('handles parsed value directly', () => {
      const tooltipItem = { parsed: 1234.56 };
      expect(chartJsTooltipCallback(tooltipItem)).toBe('1.234,56');
    });
  });

  describe('chartJsCurrencyTooltipCallback', () => {
    it('formats currency tooltip values', () => {
      const tooltipItem = { parsed: { y: 1234.56 } };
      expect(chartJsCurrencyTooltipCallback(tooltipItem, '€')).toBe('1.234,56 €');
    });
  });

  describe('chartJsPercentTooltipCallback', () => {
    it('formats percent tooltip values', () => {
      const tooltipItem = { parsed: { y: 0.35 } };
      expect(chartJsPercentTooltipCallback(tooltipItem)).toBe('35,00 %');
    });
  });

  describe('createChartJsConfig', () => {
    it('creates number configuration', () => {
      const config = createChartJsConfig('number');
      expect(config).toHaveProperty('plugins');
      expect(config).toHaveProperty('scales');
      expect(config.scales.y.ticks.callback(1234.56)).toBe('1.234,56');
    });

    it('creates currency configuration', () => {
      const config = createChartJsConfig('currency', '€');
      expect(config.scales.y.ticks.callback(1234.56)).toBe('1.234,56 €');
    });

    it('creates percent configuration', () => {
      const config = createChartJsConfig('percent');
      expect(config.scales.y.ticks.callback(0.35)).toBe('35,00 %');
    });
  });
});

describe('Chart Formatting - Plotly', () => {
  describe('getPlotlyFormatConfig', () => {
    it('returns correct format configuration', () => {
      const config = getPlotlyFormatConfig();
      expect(config.separators).toBe(',.');
      expect(config.locale).toBe('de-DE');
    });
  });

  describe('getPlotlyHoverTemplate', () => {
    it('creates hover template for numbers', () => {
      const template = getPlotlyHoverTemplate('Production');
      expect(template).toContain('Production');
      expect(template).toContain('%{y:,.2f}');
    });
  });

  describe('getPlotlyCurrencyHoverTemplate', () => {
    it('creates hover template for currency', () => {
      const template = getPlotlyCurrencyHoverTemplate('Cost', '€');
      expect(template).toContain('Cost');
      expect(template).toContain('€');
      expect(template).toContain('%{y:,.2f}');
    });
  });

  describe('getPlotlyPercentHoverTemplate', () => {
    it('creates hover template for percentages', () => {
      const template = getPlotlyPercentHoverTemplate('Efficiency');
      expect(template).toContain('Efficiency');
      expect(template).toContain('%');
      expect(template).toContain('%{y:,.2f}');
    });
  });
});

describe('Chart Formatting - Data Formatting', () => {
  describe('formatChartData', () => {
    it('formats number arrays', () => {
      const data = [1234.56, 2345.67, 3456.78];
      const formatted = formatChartData(data, 'number');
      expect(formatted).toEqual(['1.234,56', '2.345,67', '3.456,78']);
    });

    it('formats currency arrays', () => {
      const data = [1000, 2000, 3000];
      const formatted = formatChartData(data, 'currency', '€');
      expect(formatted).toEqual(['1.000,00 €', '2.000,00 €', '3.000,00 €']);
    });

    it('formats percent arrays', () => {
      const data = [0.15, 0.25, 0.35];
      const formatted = formatChartData(data, 'percent');
      expect(formatted).toEqual(['15,00 %', '25,00 %', '35,00 %']);
    });

    it('handles empty arrays', () => {
      const formatted = formatChartData([], 'number');
      expect(formatted).toEqual([]);
    });

    it('handles single value arrays', () => {
      const formatted = formatChartData([1234.56], 'number');
      expect(formatted).toEqual(['1.234,56']);
    });
  });
});

describe('Chart Formatting - Edge Cases', () => {
  it('handles very large numbers', () => {
    expect(formatChartAxis(1234567890.12)).toBe('1.234.567.890,12');
  });

  it('handles very small numbers', () => {
    expect(formatChartAxis(0.01)).toBe('0,01');
    expect(formatChartAxis(0.001)).toBe('0,00');
  });

  it('handles scientific notation', () => {
    expect(formatChartAxis(1.23e6)).toBe('1.230.000,00');
  });

  it('handles infinity', () => {
    const result = formatChartAxis(Infinity);
    expect(result).toBeTruthy(); // Should not throw
  });

  it('handles NaN', () => {
    const result = formatChartAxis(NaN);
    expect(result).toBeTruthy(); // Should not throw
  });
});

describe('Chart Formatting - Requirements Compliance', () => {
  it('✅ formats axis labels in all charts', () => {
    // Test axis formatters
    expect(rechartsAxisTickFormatter(1234.56)).toBe('1.234,56');
    expect(chartJsAxisTickCallback(1234.56)).toBe('1.234,56');
  });

  it('✅ applies German formatting to chart tooltips', () => {
    // Test tooltip formatters
    const [value] = rechartsTooltipFormatter(1234.56, 'Test', {});
    expect(value).toBe('1.234,56');
    
    const tooltipItem = { parsed: { y: 1234.56 } };
    expect(chartJsTooltipCallback(tooltipItem)).toBe('1.234,56');
  });

  it('✅ formats legend values', () => {
    // Test legend formatter
    expect(rechartsLabelFormatter(1234.56)).toBe('1.234,56');
  });

  it('✅ applies formatting to data labels', () => {
    // Test label formatters
    expect(rechartsLabelFormatter(1234.56)).toBe('1.234,56');
  });

  it('✅ formats numbers in chart exports', () => {
    // Test data formatting for export
    const data = [1234.56, 2345.67];
    const formatted = formatChartData(data, 'number');
    expect(formatted).toEqual(['1.234,56', '2.345,67']);
  });
});

describe('Chart Formatting - Integration', () => {
  it('works with Recharts configuration', () => {
    const config = createRechartsConfig('currency', '€');
    
    // Test axis formatter
    const axisValue = config.yAxis.tickFormatter(1234.56);
    expect(axisValue).toBe('1.234,56 €');
    
    // Test tooltip formatter
    const [tooltipValue] = config.tooltip.formatter(1234.56, 'Cost', {});
    expect(tooltipValue).toBe('1.234,56 €');
  });

  it('works with Chart.js configuration', () => {
    const config = createChartJsConfig('currency', '€');
    
    // Test axis callback
    const axisValue = config.scales.y.ticks.callback(1234.56);
    expect(axisValue).toBe('1.234,56 €');
    
    // Test tooltip callback
    const tooltipItem = { parsed: { y: 1234.56 } };
    const tooltipValue = config.plugins.tooltip.callbacks.label(tooltipItem);
    expect(tooltipValue).toBe('1.234,56 €');
  });

  it('works with Plotly configuration', () => {
    const config = getPlotlyFormatConfig();
    expect(config.separators).toBe(',.');
    expect(config.locale).toBe('de-DE');
    
    const template = getPlotlyCurrencyHoverTemplate('Cost', '€');
    expect(template).toContain('Cost');
    expect(template).toContain('€');
  });
});
