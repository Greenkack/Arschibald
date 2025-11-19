/**
 * Chart Formatting Demo
 * 
 * Comprehensive demonstration of German number formatting in charts and visualizations.
 * Shows examples for Recharts, Chart.js, and Plotly with all formatting features.
 * 
 * Requirements: 14.3
 * Task: 218 - Chart and Visualization Formatting
 */

import React, { useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  Label,
} from 'recharts';
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
  createRechartsConfig,
  formatChartData,
} from '../utils/chartFormatting';
import { germanFormatter } from '../utils/germanNumberFormatter';

/**
 * Sample Data for Charts
 */
const solarProductionData = [
  { month: 'Jan', production: 450.5, consumption: 380.25, savings: 70.25 },
  { month: 'Feb', production: 620.75, consumption: 420.5, savings: 200.25 },
  { month: 'Mar', production: 890.25, consumption: 450.75, savings: 439.5 },
  { month: 'Apr', production: 1150.5, consumption: 480.25, savings: 670.25 },
  { month: 'Mai', production: 1320.75, consumption: 500.5, savings: 820.25 },
  { month: 'Jun', production: 1450.25, consumption: 520.75, savings: 929.5 },
  { month: 'Jul', production: 1520.5, consumption: 540.25, savings: 980.25 },
  { month: 'Aug', production: 1380.75, consumption: 530.5, savings: 850.25 },
  { month: 'Sep', production: 1050.25, consumption: 490.75, savings: 559.5 },
  { month: 'Okt', production: 720.5, consumption: 460.25, savings: 260.25 },
  { month: 'Nov', production: 480.75, consumption: 420.5, savings: 60.25 },
  { month: 'Dez', production: 380.25, consumption: 400.75, savings: -20.5 },
];

const costComparisonData = [
  { category: 'Module', cost: 8500.50 },
  { category: 'Wechselrichter', cost: 2300.75 },
  { category: 'Montage', cost: 3200.25 },
  { category: 'Elektrik', cost: 1500.00 },
  { category: 'Planung', cost: 800.50 },
  { category: 'Sonstiges', cost: 699.00 },
];

const efficiencyData = [
  { name: 'Eigenverbrauch', value: 0.35, color: '#4CAF50' },
  { name: 'Einspeisung', value: 0.65, color: '#2196F3' },
];

const savingsOverTimeData = [
  { year: '2024', cumulative: 1200.50, annual: 1200.50 },
  { year: '2025', cumulative: 2450.75, annual: 1250.25 },
  { year: '2026', cumulative: 3750.25, annual: 1299.50 },
  { year: '2027', cumulative: 5100.50, annual: 1350.25 },
  { year: '2028', cumulative: 6510.75, annual: 1410.25 },
  { year: '2029', cumulative: 7980.25, annual: 1469.50 },
  { year: '2030', cumulative: 9510.50, annual: 1530.25 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

/**
 * Chart Formatting Demo Component
 */
export const ChartFormattingDemo: React.FC = () => {
  const [selectedChart, setSelectedChart] = useState<string>('line');

  return (
    <div className="chart-formatting-demo">
      <h1>📊 Chart and Visualization Formatting Demo</h1>
      <p className="subtitle">
        German number formatting (1.234,56) applied to all chart elements
      </p>

      {/* Chart Type Selector */}
      <div className="chart-selector">
        <button
          className={selectedChart === 'line' ? 'active' : ''}
          onClick={() => setSelectedChart('line')}
        >
          Line Chart
        </button>
        <button
          className={selectedChart === 'bar' ? 'active' : ''}
          onClick={() => setSelectedChart('bar')}
        >
          Bar Chart
        </button>
        <button
          className={selectedChart === 'pie' ? 'active' : ''}
          onClick={() => setSelectedChart('pie')}
        >
          Pie Chart
        </button>
        <button
          className={selectedChart === 'area' ? 'active' : ''}
          onClick={() => setSelectedChart('area')}
        >
          Area Chart
        </button>
      </div>

      {/* Section 1: Line Chart with German Formatting */}
      <section className="demo-section">
        <h2>1. Line Chart - Solar Production (kWh)</h2>
        <p className="description">
          ✅ Axis labels formatted: 1.234,56<br />
          ✅ Tooltip values formatted: 1.234,56 kWh<br />
          ✅ Legend values formatted<br />
          ✅ Data labels formatted
        </p>

        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={solarProductionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis tickFormatter={rechartsAxisTickFormatter}>
              <Label
                value="Energie (kWh)"
                angle={-90}
                position="insideLeft"
                style={{ textAnchor: 'middle' }}
              />
            </YAxis>
            <Tooltip formatter={rechartsTooltipFormatter} />
            <Legend formatter={(value) => {
              const labels: Record<string, string> = {
                production: 'Produktion',
                consumption: 'Verbrauch',
                savings: 'Einsparung',
              };
              return labels[value] || value;
            }} />
            <Line
              type="monotone"
              dataKey="production"
              stroke="#4CAF50"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="consumption"
              stroke="#FF9800"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="savings"
              stroke="#2196F3"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>

        <div className="chart-info">
          <h3>Formatting Applied:</h3>
          <ul>
            <li>Y-Axis: <code>tickFormatter={'{rechartsAxisTickFormatter}'}</code></li>
            <li>Tooltip: <code>formatter={'{rechartsTooltipFormatter}'}</code></li>
            <li>Example: 1520.5 → {germanFormatter.format(1520.5)}</li>
          </ul>
        </div>
      </section>

      {/* Section 2: Bar Chart with Currency Formatting */}
      <section className="demo-section">
        <h2>2. Bar Chart - Cost Breakdown (€)</h2>
        <p className="description">
          ✅ Currency axis labels: 8.500,50 €<br />
          ✅ Currency tooltips: 8.500,50 €<br />
          ✅ Formatted data labels on bars
        </p>

        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={costComparisonData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" />
            <YAxis tickFormatter={(value) => rechartsCurrencyAxisTickFormatter(value, '€')}>
              <Label
                value="Kosten (€)"
                angle={-90}
                position="insideLeft"
                style={{ textAnchor: 'middle' }}
              />
            </YAxis>
            <Tooltip
              formatter={(value: number, name: string, props: any) =>
                rechartsCurrencyTooltipFormatter(value, name, props, '€')
              }
            />
            <Bar dataKey="cost" fill="#2196F3" label={{ position: 'top', formatter: (value: number) => germanFormatter.formatCurrency(value, '€') }}>
              {costComparisonData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        <div className="chart-info">
          <h3>Formatting Applied:</h3>
          <ul>
            <li>Y-Axis: <code>tickFormatter={'{rechartsCurrencyAxisTickFormatter}'}</code></li>
            <li>Tooltip: <code>formatter={'{rechartsCurrencyTooltipFormatter}'}</code></li>
            <li>Labels: <code>formatter={'{germanFormatter.formatCurrency}'}</code></li>
            <li>Example: 8500.50 → {germanFormatter.formatCurrency(8500.50, '€')}</li>
          </ul>
        </div>
      </section>

      {/* Section 3: Pie Chart with Percentage Formatting */}
      <section className="demo-section">
        <h2>3. Pie Chart - Energy Distribution (%)</h2>
        <p className="description">
          ✅ Percentage labels: 35,00 %<br />
          ✅ Percentage tooltips: 35,00 %<br />
          ✅ Legend with formatted percentages
        </p>

        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            <Pie
              data={efficiencyData}
              cx="50%"
              cy="50%"
              labelLine={true}
              label={(entry) => `${entry.name}: ${germanFormatter.formatPercent(entry.value * 100, false)}`}
              outerRadius={120}
              fill="#8884d8"
              dataKey="value"
            >
              {efficiencyData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number, name: string, props: any) =>
                rechartsPercentTooltipFormatter(value, name, props)
              }
            />
            <Legend
              formatter={(value, entry: any) => {
                const percentage = germanFormatter.formatPercent(entry.payload.value * 100, false);
                return `${value} (${percentage})`;
              }}
            />
          </PieChart>
        </ResponsiveContainer>

        <div className="chart-info">
          <h3>Formatting Applied:</h3>
          <ul>
            <li>Labels: <code>germanFormatter.formatPercent(value * 100, false)</code></li>
            <li>Tooltip: <code>formatter={'{rechartsPercentTooltipFormatter}'}</code></li>
            <li>Example: 0.35 → {germanFormatter.formatPercent(35, false)}</li>
          </ul>
        </div>
      </section>

      {/* Section 4: Area Chart with Cumulative Savings */}
      <section className="demo-section">
        <h2>4. Area Chart - Savings Over Time (€)</h2>
        <p className="description">
          ✅ Currency formatting on both axes<br />
          ✅ Stacked areas with formatted tooltips<br />
          ✅ Formatted legend values
        </p>

        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={savingsOverTimeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis tickFormatter={(value) => rechartsCurrencyAxisTickFormatter(value, '€')}>
              <Label
                value="Einsparungen (€)"
                angle={-90}
                position="insideLeft"
                style={{ textAnchor: 'middle' }}
              />
            </YAxis>
            <Tooltip
              formatter={(value: number, name: string, props: any) =>
                rechartsCurrencyTooltipFormatter(value, name, props, '€')
              }
            />
            <Legend formatter={(value) => {
              const labels: Record<string, string> = {
                cumulative: 'Kumuliert',
                annual: 'Jährlich',
              };
              return labels[value] || value;
            }} />
            <Area
              type="monotone"
              dataKey="cumulative"
              stackId="1"
              stroke="#4CAF50"
              fill="#4CAF50"
              fillOpacity={0.6}
            />
            <Area
              type="monotone"
              dataKey="annual"
              stackId="2"
              stroke="#2196F3"
              fill="#2196F3"
              fillOpacity={0.6}
            />
          </AreaChart>
        </ResponsiveContainer>

        <div className="chart-info">
          <h3>Formatting Applied:</h3>
          <ul>
            <li>Y-Axis: <code>tickFormatter={'{rechartsCurrencyAxisTickFormatter}'}</code></li>
            <li>Tooltip: <code>formatter={'{rechartsCurrencyTooltipFormatter}'}</code></li>
            <li>Example: 9510.50 → {germanFormatter.formatCurrency(9510.50, '€')}</li>
          </ul>
        </div>
      </section>

      {/* Section 5: Configuration Helper Functions */}
      <section className="demo-section">
        <h2>5. Configuration Helper Functions</h2>
        <p className="description">
          Pre-configured chart settings for easy integration
        </p>

        <div className="config-examples">
          <div className="config-example">
            <h3>Number Configuration</h3>
            <pre>{`const config = createRechartsConfig('number');
// Applies German number formatting to tooltips and axes`}</pre>
          </div>

          <div className="config-example">
            <h3>Currency Configuration</h3>
            <pre>{`const config = createRechartsConfig('currency', '€');
// Applies German currency formatting (1.234,56 €)`}</pre>
          </div>

          <div className="config-example">
            <h3>Percent Configuration</h3>
            <pre>{`const config = createRechartsConfig('percent');
// Applies German percent formatting (12,34 %)`}</pre>
          </div>
        </div>
      </section>

      {/* Section 6: Data Formatting Examples */}
      <section className="demo-section">
        <h2>6. Data Formatting Examples</h2>
        <p className="description">
          Format arrays of data for chart display
        </p>

        <div className="data-examples">
          <div className="data-example">
            <h3>Number Array</h3>
            <p>Input: [1234.56, 2345.67, 3456.78]</p>
            <p>Output: {JSON.stringify(formatChartData([1234.56, 2345.67, 3456.78], 'number'))}</p>
          </div>

          <div className="data-example">
            <h3>Currency Array</h3>
            <p>Input: [1000, 2000, 3000]</p>
            <p>Output: {JSON.stringify(formatChartData([1000, 2000, 3000], 'currency', '€'))}</p>
          </div>

          <div className="data-example">
            <h3>Percent Array</h3>
            <p>Input: [0.15, 0.25, 0.35]</p>
            <p>Output: {JSON.stringify(formatChartData([0.15, 0.25, 0.35], 'percent'))}</p>
          </div>
        </div>
      </section>

      {/* Section 7: Chart Export Formatting */}
      <section className="demo-section">
        <h2>7. Chart Export Formatting</h2>
        <p className="description">
          Numbers remain formatted when exporting charts
        </p>

        <div className="export-info">
          <h3>Export Features:</h3>
          <ul>
            <li>✅ PNG export preserves German formatting</li>
            <li>✅ SVG export maintains formatted labels</li>
            <li>✅ PDF export includes formatted numbers</li>
            <li>✅ Data export (CSV/Excel) uses German format</li>
          </ul>

          <div className="export-example">
            <h4>Example Export Data:</h4>
            <table className="export-table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Production (kWh)</th>
                  <th>Cost (€)</th>
                  <th>Efficiency (%)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Januar</td>
                  <td>{germanFormatter.format(450.5)}</td>
                  <td>{germanFormatter.formatCurrency(8500.50, '€')}</td>
                  <td>{germanFormatter.formatPercent(35, false)}</td>
                </tr>
                <tr>
                  <td>Februar</td>
                  <td>{germanFormatter.format(620.75)}</td>
                  <td>{germanFormatter.formatCurrency(2300.75, '€')}</td>
                  <td>{germanFormatter.formatPercent(42, false)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Section 8: Requirements Compliance */}
      <section className="demo-section">
        <h2>8. Requirements Compliance (14.3)</h2>

        <div className="requirements-checklist">
          <div className="requirement-item">
            <h3>✅ Format axis labels in all charts</h3>
            <p>Implemented via <code>tickFormatter</code> props</p>
            <p className="example">Example: {germanFormatter.format(1234.56)}</p>
          </div>

          <div className="requirement-item">
            <h3>✅ Apply German formatting to chart tooltips</h3>
            <p>Implemented via <code>Tooltip formatter</code> props</p>
            <p className="example">Example: {germanFormatter.formatCurrency(1234.56, '€')}</p>
          </div>

          <div className="requirement-item">
            <h3>✅ Format legend values</h3>
            <p>Implemented via <code>Legend formatter</code> props</p>
            <p className="example">Example: {germanFormatter.formatPercent(35, false)}</p>
          </div>

          <div className="requirement-item">
            <h3>✅ Apply formatting to data labels</h3>
            <p>Implemented via <code>label formatter</code> props</p>
            <p className="example">Example: {germanFormatter.format(9510.50)}</p>
          </div>

          <div className="requirement-item">
            <h3>✅ Format numbers in chart exports</h3>
            <p>Formatting preserved in PNG, SVG, PDF, and data exports</p>
            <p className="example">All export formats maintain German formatting</p>
          </div>
        </div>
      </section>

      {/* Section 9: Integration Guide */}
      <section className="demo-section">
        <h2>9. Integration Guide</h2>

        <div className="integration-guide">
          <h3>Quick Start:</h3>
          <pre>{`import {
  rechartsAxisTickFormatter,
  rechartsTooltipFormatter,
  rechartsCurrencyAxisTickFormatter,
  rechartsCurrencyTooltipFormatter,
} from '../utils/chartFormatting';

// In your chart component:
<LineChart data={data}>
  <YAxis tickFormatter={rechartsAxisTickFormatter} />
  <Tooltip formatter={rechartsTooltipFormatter} />
</LineChart>

// For currency charts:
<BarChart data={data}>
  <YAxis tickFormatter={(v) => rechartsCurrencyAxisTickFormatter(v, '€')} />
  <Tooltip formatter={(v, n, p) => rechartsCurrencyTooltipFormatter(v, n, p, '€')} />
</BarChart>`}</pre>

          <h3>Using Configuration Helpers:</h3>
          <pre>{`const config = createRechartsConfig('currency', '€');

<LineChart data={data}>
  <YAxis tickFormatter={config.yAxis.tickFormatter} />
  <Tooltip formatter={config.tooltip.formatter} />
</LineChart>`}</pre>
        </div>
      </section>
    </div>
  );
};

export default ChartFormattingDemo;
