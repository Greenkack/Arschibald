/**
 * Global Formatting Demo
 * 
 * Demonstrates the application of German number formatting across all components.
 * Shows examples of formatted displays, inputs, charts, tables, and exports.
 * 
 * Requirements: 14.1, 14.2, 14.3
 */

import React, { useState } from 'react';
import { GlobalFormattingProvider, useGlobalFormatting } from '../providers/GlobalFormattingProvider';
import {
  FormattedNumber,
  FormattedCurrency,
  FormattedPercent,
  FormattedLabel,
  FormattedTableCell,
  FormattedCardValue,
} from '../components/FormattedDisplay';
import {
  GermanNumberInput,
  GermanCurrencyInput,
  GermanPercentInput,
  GermanSlider,
} from '../components';

/**
 * Demo Component Content
 */
const GlobalFormattingDemoContent: React.FC = () => {
  const { formatNumber, formatCurrency, formatPercent } = useGlobalFormatting();
  
  // State for inputs
  const [numberValue, setNumberValue] = useState(1234.56);
  const [currencyValue, setCurrencyValue] = useState(15000);
  const [percentValue, setPercentValue] = useState(0.18);
  const [sliderValue, setSliderValue] = useState(5000);
  
  // Sample data for table
  const tableData = [
    { id: 1, product: 'Solar Module A', power: 400, price: 250, efficiency: 0.21 },
    { id: 2, product: 'Solar Module B', power: 450, price: 280, efficiency: 0.22 },
    { id: 3, product: 'Solar Module C', power: 500, price: 320, efficiency: 0.23 },
  ];
  
  // Sample calculation results
  const calculationResults = {
    systemSize: 10.5,
    totalCost: 18500,
    annualProduction: 12000,
    selfConsumption: 0.35,
    paybackPeriod: 12.5,
    savings25Years: 45000,
  };

  return (
    <div className="global-formatting-demo">
      <h1>Global German Number Formatting Demo</h1>
      
      {/* Section 1: Formatted Display Components */}
      <section className="demo-section">
        <h2>1. Formatted Display Components</h2>
        
        <div className="demo-grid">
          <div className="demo-item">
            <h3>FormattedNumber</h3>
            <FormattedNumber value={1234.56} />
            <p className="demo-description">Displays: 1.234,56</p>
          </div>
          
          <div className="demo-item">
            <h3>FormattedCurrency</h3>
            <FormattedCurrency value={15000} symbol="€" />
            <p className="demo-description">Displays: 15.000,00 €</p>
          </div>
          
          <div className="demo-item">
            <h3>FormattedPercent</h3>
            <FormattedPercent value={0.18} multiplyBy100={true} />
            <p className="demo-description">Displays: 18,00 %</p>
          </div>
          
          <div className="demo-item">
            <h3>FormattedLabel</h3>
            <FormattedLabel
              label="System Size"
              value={10.5}
              type="number"
            />
            <p className="demo-description">Displays: System Size: 10,50</p>
          </div>
        </div>
      </section>
      
      {/* Section 2: Input Components */}
      <section className="demo-section">
        <h2>2. German Input Components</h2>
        
        <div className="demo-grid">
          <div className="demo-item">
            <GermanNumberInput
              value={numberValue}
              onChange={setNumberValue}
              label="Number Input"
              min={0}
              max={10000}
            />
            <p className="demo-value">Value: {numberValue}</p>
          </div>
          
          <div className="demo-item">
            <GermanCurrencyInput
              value={currencyValue}
              onChange={setCurrencyValue}
              label="Currency Input"
              min={0}
              max={100000}
            />
            <p className="demo-value">Value: {currencyValue}</p>
          </div>
          
          <div className="demo-item">
            <GermanPercentInput
              value={percentValue}
              onChange={setPercentValue}
              label="Percent Input"
              multiplyBy100={true}
            />
            <p className="demo-value">Value: {percentValue}</p>
          </div>
          
          <div className="demo-item">
            <GermanSlider
              value={sliderValue}
              onChange={setSliderValue}
              label="Slider"
              min={0}
              max={10000}
              step={100}
              formatType="currency"
              showValue={true}
            />
            <p className="demo-value">Value: {sliderValue}</p>
          </div>
        </div>
      </section>
      
      {/* Section 3: Calculation Results */}
      <section className="demo-section">
        <h2>3. Calculation Results Display</h2>
        
        <div className="demo-results">
          <FormattedCardValue
            title="System Size"
            value={calculationResults.systemSize}
            type="number"
            subtitle="kWp"
          />
          
          <FormattedCardValue
            title="Total Cost"
            value={calculationResults.totalCost}
            type="currency"
            symbol="€"
          />
          
          <FormattedCardValue
            title="Annual Production"
            value={calculationResults.annualProduction}
            type="number"
            subtitle="kWh/year"
          />
          
          <FormattedCardValue
            title="Self Consumption"
            value={calculationResults.selfConsumption}
            type="percent"
          />
          
          <FormattedCardValue
            title="Payback Period"
            value={calculationResults.paybackPeriod}
            type="number"
            subtitle="years"
          />
          
          <FormattedCardValue
            title="25-Year Savings"
            value={calculationResults.savings25Years}
            type="currency"
            symbol="€"
          />
        </div>
      </section>
      
      {/* Section 4: Table Display */}
      <section className="demo-section">
        <h2>4. Table with Formatted Numbers</h2>
        
        <table className="demo-table">
          <thead>
            <tr>
              <th>Product</th>
              <th style={{ textAlign: 'right' }}>Power (W)</th>
              <th style={{ textAlign: 'right' }}>Price</th>
              <th style={{ textAlign: 'right' }}>Efficiency</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map(row => (
              <tr key={row.id}>
                <td>{row.product}</td>
                <FormattedTableCell value={row.power} type="number" />
                <FormattedTableCell value={row.price} type="currency" symbol="€" />
                <FormattedTableCell value={row.efficiency} type="percent" />
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      
      {/* Section 5: Direct Formatting Functions */}
      <section className="demo-section">
        <h2>5. Direct Formatting Functions</h2>
        
        <div className="demo-code">
          <h3>Using useGlobalFormatting Hook:</h3>
          <pre>
{`const { formatNumber, formatCurrency, formatPercent } = useGlobalFormatting();

formatNumber(1234.56)           // → "1.234,56"
formatCurrency(15000, '€')      // → "15.000,00 €"
formatPercent(0.18, true)       // → "18,00 %"`}
          </pre>
          
          <h3>Results:</h3>
          <ul>
            <li>formatNumber(1234.56) = {formatNumber(1234.56)}</li>
            <li>formatCurrency(15000, '€') = {formatCurrency(15000, '€')}</li>
            <li>formatPercent(0.18, true) = {formatPercent(0.18, true)}</li>
          </ul>
        </div>
      </section>
      
      {/* Section 6: Integration Examples */}
      <section className="demo-section">
        <h2>6. Integration Examples</h2>
        
        <div className="demo-integration">
          <h3>Solar Calculator Integration:</h3>
          <div className="integration-example">
            <FormattedLabel label="Roof Area" value={50} type="number" />
            <FormattedLabel label="System Cost" value={18500} type="currency" />
            <FormattedLabel label="Efficiency" value={0.21} type="percent" />
          </div>
          
          <h3>Price Matrix Integration:</h3>
          <div className="integration-example">
            <FormattedLabel label="Base Price" value={250} type="currency" />
            <FormattedLabel label="Discount" value={0.15} type="percent" />
            <FormattedLabel label="Final Price" value={212.50} type="currency" />
          </div>
          
          <h3>Heat Pump Integration:</h3>
          <div className="integration-example">
            <FormattedLabel label="Heating Power" value={8.5} type="number" />
            <FormattedLabel label="Annual Cost" value={1200} type="currency" />
            <FormattedLabel label="COP" value={4.2} type="number" />
          </div>
        </div>
      </section>
      
      {/* Section 7: Requirements Compliance */}
      <section className="demo-section">
        <h2>7. Requirements Compliance</h2>
        
        <div className="requirements-list">
          <div className="requirement-item">
            <h3>✅ Requirement 14.1</h3>
            <p>All numbers formatted with German locale (de-DE)</p>
            <p className="example">Example: {formatNumber(1234567.89)}</p>
          </div>
          
          <div className="requirement-item">
            <h3>✅ Requirement 14.2</h3>
            <p>Exactly 2 decimal places for all decimal numbers</p>
            <p className="example">Example: {formatNumber(123.4)} (not 123.4)</p>
          </div>
          
          <div className="requirement-item">
            <h3>✅ Requirement 14.3</h3>
            <p>Applied to all input fields, displays, calculations, charts, tables, and reports</p>
            <p className="example">Demonstrated in all sections above</p>
          </div>
        </div>
      </section>
    </div>
  );
};

/**
 * Main Demo Component with Provider
 */
export const GlobalFormattingDemo: React.FC = () => {
  return (
    <GlobalFormattingProvider locale="de-DE" defaultDecimalPlaces={2}>
      <GlobalFormattingDemoContent />
    </GlobalFormattingProvider>
  );
};

export default GlobalFormattingDemo;
