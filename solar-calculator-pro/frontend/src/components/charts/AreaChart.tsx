/**
 * Area Chart Component
 * 
 * Reusable area chart component for savings over time visualization
 * with German number formatting.
 * 
 * Requirements: 7.4
 */

import React from 'react';
import {
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  rechartsAxisTickFormatter,
  rechartsTooltipFormatter,
  rechartsCurrencyAxisTickFormatter,
  rechartsCurrencyTooltipFormatter,
} from '../../utils/chartFormatting';

export interface AreaChartData {
  name: string;
  [key: string]: string | number;
}

export interface AreaChartProps {
  data: AreaChartData[];
  areas: Array<{
    dataKey: string;
    name: string;
    color: string;
    fillOpacity?: number;
  }>;
  xAxisKey?: string;
  title?: string;
  height?: number;
  formatType?: 'number' | 'currency' | 'percent';
  currencySymbol?: string;
  showGrid?: boolean;
  showLegend?: boolean;
  stacked?: boolean;
  className?: string;
}

export const AreaChart: React.FC<AreaChartProps> = ({
  data,
  areas,
  xAxisKey = 'name',
  title,
  height = 300,
  formatType = 'number',
  currencySymbol = '€',
  showGrid = true,
  showLegend = true,
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
    <div className={`area-chart-container ${className}`}>
      {title && <h3 className="chart-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsAreaChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          {showGrid && <CartesianGrid strokeDasharray="3 3" />}
          <XAxis dataKey={xAxisKey} />
          <YAxis tickFormatter={yAxisFormatter} />
          <Tooltip formatter={tooltipFormatter} />
          {showLegend && <Legend />}
          {areas.map((area) => (
            <Area
              key={area.dataKey}
              type="monotone"
              dataKey={area.dataKey}
              name={area.name}
              stroke={area.color}
              fill={area.color}
              fillOpacity={area.fillOpacity || 0.6}
              stackId={stacked ? 'stack' : undefined}
            />
          ))}
        </RechartsAreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AreaChart;
