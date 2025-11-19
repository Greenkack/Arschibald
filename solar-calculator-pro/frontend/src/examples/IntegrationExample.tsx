/**
 * Integration Example
 * 
 * Shows how to integrate global German number formatting into a real application.
 * This example demonstrates a complete Solar Calculator results page with:
 * - Formatted display components
 * - Charts with German formatting
 * - Tables with German formatting
 * - Export functionality with German formatting
 */

import React, { useState } from 'react';
import { GlobalFormattingProvider, useGlobalFormatting } from '../providers';
import {
  FormattedNumber,
  FormattedCurrency,
  FormattedPercent,
  FormattedCardValue,
} from '../components';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { createPrimeReactColumnConfig } from '../utils/tableFormatting';
import { createRechartsConfig } from '../utils/chartFormatting';
import { downloadFormattedCSV } from '../utils/exportFormatting';

/**
 * Solar Calculator Results Page
 */
const SolarCalculatorResultsContent: React.FC = () => {
  // Sample calculation results
  const results = {
    systemSize: 10.5,
    moduleCount: 30,
    totalCost: 18500,
    annualProduction: 12000,
    selfConsumption: 0.35,
    paybackPeriod: 12.5,
    savings25Years: 45000,
    co2Savings: 180000,
  };

  // Sample monthly production data
  const monthlyData = [
    { month: 'Jan', production: 650, consumption: 1200, savings: 195 },
    { month: 'Feb', production: 850, consumption: 1100, savings: 255 },
    { month: 'Mar', production: 1100, consumption: 1000, savings: 330 },
    { month: 'Apr', production: 1300, consumption: 900, savings: 390 },
    { month: 'Mai', production: 1450, consumption: 850, savings: 435 },
    { month: 'Jun', production: 1500, consumption: 800, savings: 450 },
    { month: 'Jul', production: 1550, consumption: 750, savings: 465 },
    { month: 'Aug', production: 1400, consumption: 800, savings: 420 },
    { month: 'Sep', production: 1200, consumption: 900, savings: 360 },
    { month: 'Okt', production: 900, consumption: 1000, savings: 270 },
    { month: 'Nov', production: 700, consumption: 1100, savings: 210 },
    { month: 'Dez', production: 600, consumption: 1200, savings: 180 },
  ];

  // Sample component comparison data
  const components = [
    { id: 1, component: 'Solar Modules', quantity: 30, unitPrice: 250, totalPrice: 7500 },
    { id: 2, component: 'Inverter', quantity: 1, unitPrice: 2500, totalPrice: 2500 },
    { id: 3, component: 'Mounting System', quantity: 1, unitPrice: 3000, totalPrice: 3000 },
    { id: 4, component: 'Installation', quantity: 1, unitPrice: 4000, totalPrice: 4000 },
    { id: 5, component: 'Other Components', quantity: 1, unitPrice: 1500, totalPrice: 1500 },
  ];

  // Chart configuration with German formatting
  const chartConfig = createRechartsConfig('number');

  // Handle CSV export
  const handleExportCSV = () => {
    downloadFormattedCSV(
      components,
      ['component', 'quantity', 'unitPrice', 'totalPrice'],
      ['quantity', 'unitPrice', 'totalPrice'],
      'solar-calculator-components.csv',
      { unitPrice: 'currency', totalPrice: 'currency', quantity: 'number' },
      '€'
    );
  };

  return (
    <div className="solar-calculator-results">
      <h1>Solar Calculator Results</h1>

      {/* Section 1: Key Metrics */}
      <section className="key-metrics">
        <h2>Key Metrics</h2>
        <div className="metrics-grid">
          <FormattedCardValue
            title="System Size"
            value={results.systemSize}
            type="number"
            subtitle="kWp"
          />
          
          <FormattedCardValue
            title="Module Count"
            value={results.moduleCount}
            type="number"
            subtitle="modules"
          />
          
          <FormattedCardValue
            title="Total Cost"
            value={results.totalCost}
            type="currency"
            symbol="€"
          />
          
          <FormattedCardValue
            title="Annual Production"
            value={results.annualProduction}
            type="number"
            subtitle="kWh/year"
          />
          
          <FormattedCardValue
            title="Self Consumption"
            value={results.selfConsumption}
            type="percent"
          />
          
          <FormattedCardValue
            title="Payback Period"
            value={results.paybackPeriod}
            type="number"
            subtitle="years"
          />
          
          <FormattedCardValue
            title="25-Year Savings"
            value={results.savings25Years}
            type="currency"
            symbol="€"
          />
          
          <FormattedCardValue
            title="CO₂ Savings"
            value={results.co2Savings}
            type="number"
            subtitle="kg CO₂"
          />
        </div>
      </section>

      {/* Section 2: Monthly Production Chart */}
      <section className="monthly-production">
        <h2>Monthly Production and Consumption</h2>
        <LineChart width={800} height={400} data={monthlyData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis tickFormatter={chartConfig.yAxis.tickFormatter} />
          <Tooltip formatter={chartConfig.tooltip.formatter} />
          <Legend />
          <Line type="monotone" dataKey="production" stroke="#8884d8" name="Production (kWh)" />
          <Line type="monotone" dataKey="consumption" stroke="#82ca9d" name="Consumption (kWh)" />
        </LineChart>
      </section>

      {/* Section 3: Component Breakdown Table */}
      <section className="component-breakdown">
        <h2>Component Breakdown</h2>
        <div className="table-actions">
          <button onClick={handleExportCSV} className="export-button">
            Export to CSV
          </button>
        </div>
        <DataTable value={components} showGridlines>
          <Column field="component" header="Component" />
          <Column {...createPrimeReactColumnConfig('quantity', 'Quantity', 'number')} />
          <Column {...createPrimeReactColumnConfig('unitPrice', 'Unit Price', 'currency', '€')} />
          <Column {...createPrimeReactColumnConfig('totalPrice', 'Total Price', 'currency', '€')} />
        </DataTable>
        
        <div className="table-summary">
          <strong>Total: </strong>
          <FormattedCurrency 
            value={components.reduce((sum, item) => sum + item.totalPrice, 0)} 
            symbol="€" 
          />
        </div>
      </section>

      {/* Section 4: Financial Summary */}
      <section className="financial-summary">
        <h2>Financial Summary</h2>
        <div className="summary-grid">
          <div className="summary-item">
            <span className="summary-label">Initial Investment:</span>
            <FormattedCurrency value={results.totalCost} symbol="€" />
          </div>
          <div className="summary-item">
            <span className="summary-label">Annual Savings:</span>
            <FormattedCurrency value={results.savings25Years / 25} symbol="€" />
          </div>
          <div className="summary-item">
            <span className="summary-label">Payback Period:</span>
            <FormattedNumber value={results.paybackPeriod} /> years
          </div>
          <div className="summary-item">
            <span className="summary-label">25-Year Return:</span>
            <FormattedPercent value={(results.savings25Years / results.totalCost) - 1} />
          </div>
        </div>
      </section>

      {/* Section 5: Environmental Impact */}
      <section className="environmental-impact">
        <h2>Environmental Impact</h2>
        <div className="impact-grid">
          <div className="impact-item">
            <span className="impact-label">CO₂ Savings (25 years):</span>
            <FormattedNumber value={results.co2Savings} /> kg
          </div>
          <div className="impact-item">
            <span className="impact-label">Equivalent Trees Planted:</span>
            <FormattedNumber value={results.co2Savings / 20} /> trees
          </div>
          <div className="impact-item">
            <span className="impact-label">Cars Off Road (1 year):</span>
            <FormattedNumber value={results.co2Savings / 25 / 4000} /> cars
          </div>
        </div>
      </section>
    </div>
  );
};

/**
 * Main Integration Example with Provider
 */
export const IntegrationExample: React.FC = () => {
  return (
    <GlobalFormattingProvider locale="de-DE" defaultDecimalPlaces={2}>
      <SolarCalculatorResultsContent />
    </GlobalFormattingProvider>
  );
};

export default IntegrationExample;
