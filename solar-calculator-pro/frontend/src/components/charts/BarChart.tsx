/**
 * Bar Chart Component
 * 
 * Reusable bar chart component for cost analysis visualization
 * with German number formatting.
 * 
 * Requirements: 7.4
 */

import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import {
  rechartsAxisTickFormatter,
  rechartsTooltipFormatter,
  rechartsCurrencyAxisTickFormatter,
  rechartsCurrencyTooltipFormatter,
} from '../../utils/chartFormatting';

export interface BarChartData {
  name: string;
  [key: string]: string | number;
}

export interface BarChartProps {
  data: BarChartData[];
  bars: Array<{
    dataKey: string;
    name: string;
    color: string;
  }>;
  xAxisKey?: string;
  title?: string;
  height?: number;
  formatType?: 'number' | 'currency' | 'percent';
  currencySymbol?: string;
  showGrid?: boolean;
  showLegend?: boolean;
  layout?: 'horizontal' | 'vertical';
  stacked?: boolean;
  className?: string;
}

export const BarChart: React.FC<BarChartProps> = ({
  data,
  bars,
  xAxisKey = 'name',
  title,
  height = 300,
  formatType = 'number',
  currencySymbol = '€',
  showGrid = true,
  showLegend = true,
  layout = 'horizontal',
  stacked = false,
  className = '',
}) => {
  // Select appropriate formatters based on type
  const yAxisFormatter = formatType === 'currency'
    ? (value: number) => rechartsCurrencyAxisTickFormatter(value, currencySymbol)
    : rechartsAxisTickFormatter;

  const tooltipFormatter = formatType === 'currency'
    ? (value: number, name: string, props: any) => 
        rechartsCurrencyTooltipFormatter(value, name, props, currencySymbol)
    : rechartsTooltipFormatter;

  return (
    <div className={`bar-chart-container ${className}`}>
      {title && <h3 className="chart-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsBarChart
          data={data}
          layout={layout}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          {showGrid && <CartesianGrid strokeDasharray="3 3" />}
          {layout === 'horizontal' ? (
            <>
              <XAxis dataKey={xAxisKey} />
              <YAxis tickFormatter={yAxisFormatter} />
            </>
          ) : (
            <>
              <XAxis type="number" tickFormatter={yAxisFormatter} />
              <YAxis type="category" dataKey={xAxisKey} />
            </>
          )}
          <Tooltip formatter={tooltipFormatter} />
          {showLegend && <Legend />}
          {bars.map((bar) => (
            <Bar
              key={bar.dataKey}
              dataKey={bar.dataKey}
              name={bar.name}
              fill={bar.color}
              stackId={stacked ? 'stack' : undefined}
            />
          ))}
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BarChart;
