/**
 * Line Chart Component
 * 
 * Reusable line chart component for energy production visualization
 * with German number formatting.
 * 
 * Requirements: 7.4
 */

import React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from 'recharts';
import {
  rechartsAxisTickFormatter,
  rechartsTooltipFormatter,
  rechartsCurrencyAxisTickFormatter,
  rechartsCurrencyTooltipFormatter,
} from '../../utils/chartFormatting';

export interface LineChartData {
  name: string;
  [key: string]: string | number;
}

export interface LineChartProps {
  data: LineChartData[];
  lines: Array<{
    dataKey: string;
    name: string;
    color: string;
    strokeWidth?: number;
  }>;
  xAxisKey?: string;
  title?: string;
  height?: number;
  formatType?: 'number' | 'currency' | 'percent';
  currencySymbol?: string;
  showGrid?: boolean;
  showLegend?: boolean;
  className?: string;
}

export const LineChart: React.FC<LineChartProps> = ({
  data,
  lines,
  xAxisKey = 'name',
  title,
  height = 300,
  formatType = 'number',
  currencySymbol = '€',
  showGrid = true,
  showLegend = true,
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
    <div className={`line-chart-container ${className}`}>
      {title && <h3 className="chart-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsLineChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          {showGrid && <CartesianGrid strokeDasharray="3 3" />}
          <XAxis dataKey={xAxisKey} />
          <YAxis tickFormatter={yAxisFormatter} />
          <Tooltip formatter={tooltipFormatter} />
          {showLegend && <Legend />}
          {lines.map((line) => (
            <Line
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              name={line.name}
              stroke={line.color}
              strokeWidth={line.strokeWidth || 2}
              activeDot={{ r: 8 }}
            />
          ))}
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LineChart;
