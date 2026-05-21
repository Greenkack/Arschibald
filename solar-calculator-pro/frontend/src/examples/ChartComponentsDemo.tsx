/**
 * Chart Components Demo
 * 
 * Demonstrates usage of all chart components with German number formatting
 * and export functionality.
 * 
 * Requirements: 7.4
 */

import React, { useRef } from 'react';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { LineChart, BarChart, PieChart, AreaChart } from '../components/charts';
import {
  exportChart,
  exportChartDataAsCSV,
  exportChartDataAsJSON,
} from '../utils/chartExport';
import './ChartComponentsDemo.css';

// Sample data for energy production (Line Chart)
const energyProductionData = [
  { name: 'Jan', production: 2400, consumption: 2100 },
  { name: 'Feb', production: 3200, consumption: 2300 },
  { name: 'Mar', production: 4100, consumption: 2500 },
  { name: 'Apr', production: 5300, consumption: 2400 },
  { name: 'Mai', production: 6200, consumption: 2600 },
  { name: 'Jun', production: 6800, consumption: 2800 },
  { name: 'Jul', production: 7100, consumption: 3000 },
  { name: 'Aug', production: 6500, consumption: 2900 },
  { name: 'Sep', production: 5200, consumption: 2700 },
  { name: 'Okt', production: 3800, consumption: 2500 },
  { name: 'Nov', production: 2600, consumption: 2300 },
  { name: 'Dez', production: 2100, consumption: 2200 },
];

// Sample data for cost analysis (Bar Chart)
const costAnalysisData = [
  { name: 'PV-Module', cost: 12500 },
  { name: 'Wechselrichter', cost: 3200 },
  { name: 'Batteriespeicher', cost: 8500 },
  { name: 'Montagesystem', cost: 2800 },
  { name: 'Installation', cost: 4500 },
  { name: 'Genehmigungen', cost: 800 },
];

// Sample data for consumption breakdown (Pie Chart)
const consumptionBreakdownData = [
  { name: 'Eigenverbrauch', value: 6500, color: '#00C49F' },
  { name: 'Netzeinspeisung', value: 4200, color: '#0088FE' },
  { name: 'Netzbezug', value: 1800, color: '#FFBB28' },
];

// Sample data for savings over time (Area Chart)
const savingsOverTimeData = [
  { name: 'Jahr 1', savings: 1200, cumulative: 1200 },
  { name: 'Jahr 2', savings: 1250, cumulative: 2450 },
  { name: 'Jahr 3', savings: 1300, cumulative: 3750 },
  { name: 'Jahr 4', savings: 1350, cumulative: 5100 },
  { name: 'Jahr 5', savings: 1400, cumulative: 6500 },
  { name: 'Jahr 6', savings: 1450, cumulative: 7950 },
  { name: 'Jahr 7', savings: 1500, cumulative: 9450 },
  { name: 'Jahr 8', savings: 1550, cumulative: 11000 },
  { name: 'Jahr 9', savings: 1600, cumulative: 12600 },
  { name: 'Jahr 10', savings: 1650, cumulative: 14250 },
];

export const ChartComponentsDemo: React.FC = () => {
  const lineChartRef = useRef<HTMLDivElement>(null);
  const barChartRef = useRef<HTMLDivElement>(null);
  const pieChartRef = useRef<HTMLDivElement>(null);
  const areaChartRef = useRef<HTMLDivElement>(null);

  const [exportFormat, setExportFormat] = React.useState<'png' | 'svg' | 'pdf'>('png');

  const exportFormats = [
    { label: 'PNG', value: 'png' },
    { label: 'SVG', value: 'svg' },
    { label: 'PDF', value: 'pdf' },
  ];

  const handleExportChart = async (chartRef: React.RefObject<HTMLDivElement>, chartName: string) => {
    if (!chartRef.current) return;

    try {
      await exportChart(chartRef.current, {
        filename: chartName,
        format: exportFormat,
      });
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export fehlgeschlagen. Bitte versuchen Sie es erneut.');
    }
  };

  const handleExportData = (data: any[], chartName: string, format: 'csv' | 'json') => {
    try {
      if (format === 'csv') {
        exportChartDataAsCSV(data, chartName);
      } else {
        exportChartDataAsJSON(data, chartName);
      }
    } catch (error) {
      console.error('Data export failed:', error);
      alert('Datenexport fehlgeschlagen. Bitte versuchen Sie es erneut.');
    }
  };

  return (
    <div className="chart-components-demo">
      <h1>Chart Components Demo</h1>
      <p className="demo-description">
        Demonstration aller Chart-Komponenten mit deutscher Zahlenformatierung und Export-Funktionalität.
      </p>

      <div className="export-controls">
        <label>Export-Format:</label>
        <Dropdown
          value={exportFormat}
          options={exportFormats}
          onChange={(e) => setExportFormat(e.value)}
          placeholder="Format wählen"
        />
      </div>

      {/* Line Chart Demo */}
      <div className="chart-section">
        <div className="chart-header">
          <h2>Line Chart - Energieproduktion</h2>
          <div className="chart-actions">
            <Button
              label="Chart exportieren"
              icon="pi pi-download"
              onClick={() => handleExportChart(lineChartRef, 'energieproduktion')}
              className="p-button-sm"
            />
            <Button
              label="Daten als CSV"
              icon="pi pi-file"
              onClick={() => handleExportData(energyProductionData, 'energieproduktion', 'csv')}
              className="p-button-sm p-button-secondary"
            />
            <Button
              label="Daten als JSON"
              icon="pi pi-file-o"
              onClick={() => handleExportData(energyProductionData, 'energieproduktion', 'json')}
              className="p-button-sm p-button-secondary"
            />
          </div>
        </div>
        <div ref={lineChartRef}>
          <LineChart
            data={energyProductionData}
            lines={[
              { dataKey: 'production', name: 'Produktion (kWh)', color: '#00C49F' },
              { dataKey: 'consumption', name: 'Verbrauch (kWh)', color: '#FF8042' },
            ]}
            title="Monatliche Energieproduktion und -verbrauch"
            height={400}
            formatType="number"
          />
        </div>
      </div>

      {/* Bar Chart Demo */}
      <div className="chart-section">
        <div className="chart-header">
          <h2>Bar Chart - Kostenanalyse</h2>
          <div className="chart-actions">
            <Button
              label="Chart exportieren"
              icon="pi pi-download"
              onClick={() => handleExportChart(barChartRef, 'kostenanalyse')}
              className="p-button-sm"
            />
            <Button
              label="Daten als CSV"
              icon="pi pi-file"
              onClick={() => handleExportData(costAnalysisData, 'kostenanalyse', 'csv')}
              className="p-button-sm p-button-secondary"
            />
          </div>
        </div>
        <div ref={barChartRef}>
          <BarChart
            data={costAnalysisData}
            bars={[
              { dataKey: 'cost', name: 'Kosten', color: '#0088FE' },
            ]}
            title="Kostenaufschlüsselung der PV-Anlage"
            height={400}
            formatType="currency"
            currencySymbol="€"
          />
        </div>
      </div>

      {/* Pie Chart Demo */}
      <div className="chart-section">
        <div className="chart-header">
          <h2>Pie Chart - Verbrauchsaufteilung</h2>
          <div className="chart-actions">
            <Button
              label="Chart exportieren"
              icon="pi pi-download"
              onClick={() => handleExportChart(pieChartRef, 'verbrauchsaufteilung')}
              className="p-button-sm"
            />
            <Button
              label="Daten als CSV"
              icon="pi pi-file"
              onClick={() => handleExportData(consumptionBreakdownData, 'verbrauchsaufteilung', 'csv')}
              className="p-button-sm p-button-secondary"
            />
          </div>
        </div>
        <div ref={pieChartRef}>
          <PieChart
            data={consumptionBreakdownData}
            title="Energieverbrauch und -verteilung"
            height={400}
            formatType="number"
            showLabels={true}
          />
        </div>
      </div>

      {/* Area Chart Demo */}
      <div className="chart-section">
        <div className="chart-header">
          <h2>Area Chart - Einsparungen über Zeit</h2>
          <div className="chart-actions">
            <Button
              label="Chart exportieren"
              icon="pi pi-download"
              onClick={() => handleExportChart(areaChartRef, 'einsparungen')}
              className="p-button-sm"
            />
            <Button
              label="Daten als CSV"
              icon="pi pi-file"
              onClick={() => handleExportData(savingsOverTimeData, 'einsparungen', 'csv')}
              className="p-button-sm p-button-secondary"
            />
          </div>
        </div>
        <div ref={areaChartRef}>
          <AreaChart
            data={savingsOverTimeData}
            areas={[
              { dataKey: 'savings', name: 'Jährliche Einsparung', color: '#00C49F' },
              { dataKey: 'cumulative', name: 'Kumulierte Einsparung', color: '#0088FE' },
            ]}
            title="Einsparungen über 10 Jahre"
            height={400}
            formatType="currency"
            currencySymbol="€"
          />
        </div>
      </div>

      {/* Usage Examples */}
      <div className="usage-examples">
        <h2>Verwendungsbeispiele</h2>
        
        <div className="code-example">
          <h3>Line Chart</h3>
          <pre>{`<LineChart
  data={energyProductionData}
  lines={[
    { dataKey: 'production', name: 'Produktion (kWh)', color: '#00C49F' },
    { dataKey: 'consumption', name: 'Verbrauch (kWh)', color: '#FF8042' },
  ]}
  title="Monatliche Energieproduktion"
  formatType="number"
/>`}</pre>
        </div>

        <div className="code-example">
          <h3>Bar Chart mit Währungsformatierung</h3>
          <pre>{`<BarChart
  data={costAnalysisData}
  bars={[{ dataKey: 'cost', name: 'Kosten', color: '#0088FE' }]}
  title="Kostenaufschlüsselung"
  formatType="currency"
  currencySymbol="€"
/>`}</pre>
        </div>

        <div className="code-example">
          <h3>Pie Chart</h3>
          <pre>{`<PieChart
  data={consumptionBreakdownData}
  title="Energieverbrauch"
  formatType="number"
  showLabels={true}
/>`}</pre>
        </div>

        <div className="code-example">
          <h3>Area Chart</h3>
          <pre>{`<AreaChart
  data={savingsOverTimeData}
  areas={[
    { dataKey: 'savings', name: 'Jährlich', color: '#00C49F' },
    { dataKey: 'cumulative', name: 'Kumuliert', color: '#0088FE' },
  ]}
  formatType="currency"
/>`}</pre>
        </div>
      </div>
    </div>
  );
};

export default ChartComponentsDemo;
