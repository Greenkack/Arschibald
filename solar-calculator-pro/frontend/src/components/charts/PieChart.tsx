/**
 * Pie Chart Component
 * 
 * Reusable pie chart component for consumption breakdown visualization
 * with German number formatting.
 * 
 * Requirements: 7.4
 */

import React from 'react';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  rechartsTooltipFormatter,
  rechartsCurrencyTooltipFormatter,
  rechartsPercentTooltipFormatter,
} from '../../utils/chartFormatting';

export interface PieChartData {
  name: string;
  value: number;
  color?: string;
}

export interface PieChartProps {
  data: PieChartData[];
  title?: string;
  height?: number;
  formatType?: 'number' | 'currency' | 'percent';
  currencySymbol?: string;
  showLegend?: boolean;
  showLabels?: boolean;
  innerRadius?: number;
  outerRadius?: number;
  colors?: string[];
  className?: string;
}

const DEFAULT_COLORS = [
  '#0088FE',
  '#00C49F',
  '#FFBB28',
  '#FF8042',
  '#8884D8',
  '#82CA9D',
  '#FFC658',
  '#FF6B9D',
];

export const PieChart: React.FC<PieChartProps> = ({
  data,
  title,
  height = 300,
  formatType = 'number',
  currencySymbol = '€',
  showLegend = true,
  showLabels = true,
  innerRadius = 0,
  outerRadius = 80,
  colors = DEFAULT_COLORS,
  className = '',
}) => {
  // Select appropriate formatter based on type
  const tooltipFormatter = 
    formatType === 'currency'
      ? (value: number, name: string, props: any) => 
          rechartsCurrencyTooltipFormatter(value, name, props, currencySymbol)
      : formatType === 'percent'
      ? rechartsPercentTooltipFormatter
      : rechartsTooltipFormatter;

  // Render custom label
  const renderLabel = (entry: any) => {
    if (!showLabels) return null;
    
    const percent = ((entry.value / entry.payload.total) * 100).toFixed(1);
    return `${entry.name}: ${percent}%`;
  };

  // Calculate total for percentage calculation
  const total = data.reduce((sum, entry) => sum + entry.value, 0);
  const dataWithTotal = data.map(entry => ({ ...entry, total }));

  return (
    <div className={`pie-chart-container ${className}`}>
      {title && <h3 className="chart-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsPieChart>
          <Pie
            data={dataWithTotal}
            cx="50%"
            cy="50%"
            labelLine={showLabels}
            label={showLabels ? renderLabel : false}
            innerRadius={innerRadius}
            outerRadius={outerRadius}
            fill="#8884d8"
            dataKey="value"
          >
            {dataWithTotal.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color || colors[index % colors.length]}
              />
            ))}
          </Pie>
          <Tooltip formatter={tooltipFormatter} />
          {showLegend && <Legend />}
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PieChart;
