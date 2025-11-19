/**
 * Solar Calculation Results Display
 * 
 * Comprehensive results display with:
 * - Results summary cards
 * - System size and module count display
 * - Production and savings charts
 * - Payback period visualization
 * - CO2 savings display
 * - German number formatting throughout
 */

import React from 'react';
import { Card } from 'primereact/card';
import { Divider } from 'primereact/divider';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { ProgressBar } from 'primereact/progressbar';
import { LineChart } from '../charts/LineChart';
import { BarChart } from '../charts/BarChart';
import { PieChart } from '../charts/PieChart';
import { AreaChart } from '../charts/AreaChart';
import { germanFormatter } from '../../utils/germanNumberFormatter';
import './SolarCalculationResults.css';

// Types
interface SolarCalculationResultsProps {
  results: SolarCalculationResponse;
  onEdit?: () => void;
  onSave?: () => void;
  onGeneratePDF?: () => void;
  onView3D?: () => void;
}

interface SolarCalculationResponse {
  calculation_id?: string;
  calculation_timestamp: string;
  system_sizing: {
    system_size_kwp: number;
    module_count: number;
    module_capacity_w: number;
    total_roof_area_required_m2?: number;
    specific_yield_kwh_kwp: number;
  };
  energy_production: {
    annual_production_kwh: number;
    monthly_production_kwh: MonthlyData;
    pvgis_data_used: boolean;
    pvgis_source: string;
  };
  self_consumption: {
    annual_self_consumption_kwh: number;
    self_consumption_rate_percent: number;
    autarky_degree_percent: number;
    annual_grid_feed_in_kwh: number;
    annual_grid_purchase_kwh: number;
    monthly_self_consumption_kwh?: MonthlyData;
  };
  economic_analysis: {
    total_investment_cost_net: number;
    total_investment_cost_gross: number;
    annual_savings_year1: number;
    payback_period_years: number;
    total_savings_20years: number;
    total_savings_25years: number;
    net_present_value?: number;
    internal_rate_of_return_percent?: number;
    annual_feed_in_revenue: number;
  };
  environmental_impact: {
    annual_co2_savings_kg: number;
    total_co2_savings_25years_kg: number;
    equivalent_trees: number;
    equivalent_car_km: number;
    co2_payback_time_years?: number;
  };
  storage_analysis?: {
    storage_capacity_kwh: number;
    storage_efficiency_percent: number;
    annual_storage_cycles: number;
    additional_self_consumption_kwh: number;
    storage_contribution_to_autarky_percent: number;
  };
  warnings: string[];
  errors: string[];
}

interface MonthlyData {
  january: number;
  february: number;
  march: number;
  april: number;
  may: number;
  june: number;
  july: number;
  august: number;
  september: number;
  october: number;
  november: number;
  december: number;
}

const SolarCalculationResults: React.FC<SolarCalculationResultsProps> = ({
  results,
  onEdit,
  onSave,
  onGeneratePDF,
  onView3D
}) => {
  // Convert monthly data to array
  const monthlyProductionToArray = (data: MonthlyData): number[] => {
    return [
      data.january, data.february, data.march, data.april,
      data.may, data.june, data.july, data.august,
      data.september, data.october, data.november, data.december
    ];
  };

  const monthNames = [
    'Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',
    'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'
  ];

  // Generate cumulative savings data for 25 years
  const generateCumulativeSavings = (): { year: number; savings: number }[] => {
    const data: { year: number; savings: number }[] = [];
    const annualSavings = results.economic_analysis.annual_savings_year1;
    let cumulative = 0;

    for (let year = 1; year <= 25; year++) {
      // Simple model: assume constant savings (could be enhanced with price increase)
      cumulative += annualSavings;
      data.push({ year, savings: cumulative });
    }

    return data;
  };

  // Generate payback visualization data
  const generatePaybackData = (): { year: number; investment: number; savings: number }[] => {
    const data: { year: number; investment: number; savings: number }[] = [];
    const investment = results.economic_analysis.total_investment_cost_gross;
    const annualSavings = results.economic_analysis.annual_savings_year1;
    let cumulativeSavings = 0;

    for (let year = 0; year <= Math.ceil(results.economic_analysis.payback_period_years) + 2; year++) {
      if (year > 0) {
        cumulativeSavings += annualSavings;
      }
      data.push({
        year,
        investment,
        savings: cumulativeSavings
      });
    }

    return data;
  };

  // Energy distribution for pie chart
  const getEnergyDistribution = () => {
    return [
      {
        name: 'Eigenverbrauch',
        value: results.self_consumption.annual_self_consumption_kwh,
        color: '#10b981'
      },
      {
        name: 'Netzeinspeisung',
        value: results.self_consumption.annual_grid_feed_in_kwh,
        color: '#3b82f6'
      }
    ];
  };

  // Monthly production chart data
  const getMonthlyProductionData = () => {
    const production = monthlyProductionToArray(results.energy_production.monthly_production_kwh);
    return monthNames.map((month, index) => ({
      month,
      production: production[index]
    }));
  };

  return (
    <div className="solar-calculation-results">
      {/* Header with Actions */}
      <div className="results-header">
        <div className="results-title">
          <h2>☀️ Berechnungsergebnisse</h2>
          <p className="results-timestamp">
            Berechnet am: {new Date(results.calculation_timestamp).toLocaleString('de-DE')}
          </p>
        </div>
        <div className="results-actions">
          {onEdit && (
            <Button
              label="Bearbeiten"
              icon="pi pi-pencil"
              onClick={onEdit}
              className="p-button-secondary"
            />
          )}
          {onSave && (
            <Button
              label="Speichern"
              icon="pi pi-save"
              onClick={onSave}
              className="p-button-success"
            />
          )}
          {onGeneratePDF && (
            <Button
              label="PDF erstellen"
              icon="pi pi-file-pdf"
              onClick={onGeneratePDF}
              className="p-button-help"
            />
          )}
          {onView3D && (
            <Button
              label="3D Ansicht"
              icon="pi pi-box"
              onClick={onView3D}
            />
          )}
        </div>
      </div>

      {/* Warnings and Errors */}
      {results.warnings.length > 0 && (
        <Card className="warnings-card">
          <h4>⚠️ Hinweise</h4>
          <ul>
            {results.warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </Card>
      )}

      {results.errors.length > 0 && (
        <Card className="errors-card">
          <h4>❌ Fehler</h4>
          <ul>
            {results.errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </Card>
      )}

      {/* Summary Cards */}
      <div className="summary-cards">
        {/* System Size Card */}
        <Card className="summary-card system-size-card">
          <div className="card-icon">⚡</div>
          <div className="card-content">
            <h3>Anlagengröße</h3>
            <div className="card-value">
              {germanFormatter.format(results.system_sizing.system_size_kwp)} kWp
            </div>
            <div className="card-details">
              <p>{results.system_sizing.module_count} Module</p>
              <p>{results.system_sizing.module_capacity_w}W je Modul</p>
              {results.system_sizing.total_roof_area_required_m2 && (
                <p>Benötigte Fläche: {germanFormatter.format(results.system_sizing.total_roof_area_required_m2)} m²</p>
              )}
            </div>
          </div>
        </Card>

        {/* Annual Production Card */}
        <Card className="summary-card production-card">
          <div className="card-icon">☀️</div>
          <div className="card-content">
            <h3>Jahresertrag</h3>
            <div className="card-value">
              {germanFormatter.format(results.energy_production.annual_production_kwh)} kWh
            </div>
            <div className="card-details">
              <p>Spezifischer Ertrag: {germanFormatter.format(results.system_sizing.specific_yield_kwh_kwp)} kWh/kWp</p>
              <Tag
                value={results.energy_production.pvgis_data_used ? 'PVGIS Daten' : 'Manuelle Eingabe'}
                severity={results.energy_production.pvgis_data_used ? 'success' : 'info'}
              />
            </div>
          </div>
        </Card>

        {/* Self-Consumption Card */}
        <Card className="summary-card self-consumption-card">
          <div className="card-icon">🏠</div>
          <div className="card-content">
            <h3>Eigenverbrauch</h3>
            <div className="card-value">
              {germanFormatter.format(results.self_consumption.self_consumption_rate_percent)} %
            </div>
            <div className="card-details">
              <p>Autarkiegrad: {germanFormatter.format(results.self_consumption.autarky_degree_percent)}%</p>
              <p>Eigenverbrauch: {germanFormatter.format(results.self_consumption.annual_self_consumption_kwh)} kWh</p>
              <p>Netzeinspeisung: {germanFormatter.format(results.self_consumption.annual_grid_feed_in_kwh)} kWh</p>
            </div>
          </div>
        </Card>

        {/* Annual Savings Card */}
        <Card className="summary-card savings-card">
          <div className="card-icon">💰</div>
          <div className="card-content">
            <h3>Jährliche Ersparnis</h3>
            <div className="card-value">
              {germanFormatter.formatCurrency(results.economic_analysis.annual_savings_year1)}
            </div>
            <div className="card-details">
              <p>Einspeisevergütung: {germanFormatter.formatCurrency(results.economic_analysis.annual_feed_in_revenue)}</p>
              <p>Ersparnis 25 Jahre: {germanFormatter.formatCurrency(results.economic_analysis.total_savings_25years)}</p>
            </div>
          </div>
        </Card>

        {/* Payback Period Card */}
        <Card className="summary-card payback-card">
          <div className="card-icon">📈</div>
          <div className="card-content">
            <h3>Amortisationszeit</h3>
            <div className="card-value">
              {germanFormatter.format(results.economic_analysis.payback_period_years)} Jahre
            </div>
            <div className="card-details">
              <p>Investition (brutto): {germanFormatter.formatCurrency(results.economic_analysis.total_investment_cost_gross)}</p>
              <p>Investition (netto): {germanFormatter.formatCurrency(results.economic_analysis.total_investment_cost_net)}</p>
            </div>
          </div>
        </Card>

        {/* CO2 Savings Card */}
        <Card className="summary-card co2-card">
          <div className="card-icon">🌱</div>
          <div className="card-content">
            <h3>CO₂-Einsparung</h3>
            <div className="card-value">
              {germanFormatter.format(results.environmental_impact.annual_co2_savings_kg / 1000)} t/Jahr
            </div>
            <div className="card-details">
              <p>25 Jahre: {germanFormatter.format(results.environmental_impact.total_co2_savings_25years_kg / 1000)} t</p>
              <p>≈ {results.environmental_impact.equivalent_trees} Bäume</p>
              <p>≈ {germanFormatter.format(results.environmental_impact.equivalent_car_km)} km Autofahrt</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Storage Analysis (if included) */}
      {results.storage_analysis && (
        <Card className="storage-analysis-card">
          <h3>🔋 Batteriespeicher-Analyse</h3>
          <Divider />
          <div className="storage-details">
            <div className="storage-metric">
              <label>Speicherkapazität:</label>
              <span>{germanFormatter.format(results.storage_analysis.storage_capacity_kwh)} kWh</span>
            </div>
            <div className="storage-metric">
              <label>Wirkungsgrad:</label>
              <span>{germanFormatter.format(results.storage_analysis.storage_efficiency_percent)}%</span>
            </div>
            <div className="storage-metric">
              <label>Jährliche Zyklen:</label>
              <span>{results.storage_analysis.annual_storage_cycles}</span>
            </div>
            <div className="storage-metric">
              <label>Zusätzlicher Eigenverbrauch:</label>
              <span>{germanFormatter.format(results.storage_analysis.additional_self_consumption_kwh)} kWh</span>
            </div>
            <div className="storage-metric">
              <label>Beitrag zur Autarkie:</label>
              <span>{germanFormatter.format(results.storage_analysis.storage_contribution_to_autarky_percent)}%</span>
            </div>
          </div>
        </Card>
      )}

      {/* Charts Section */}
      <div className="charts-section">
        {/* Monthly Production Chart */}
        <Card className="chart-card">
          <h3>📊 Monatliche Stromproduktion</h3>
          <Divider />
          <BarChart
            data={getMonthlyProductionData()}
            xKey="month"
            yKey="production"
            xLabel="Monat"
            yLabel="Produktion (kWh)"
            color="#f59e0b"
            height={300}
          />
        </Card>

        {/* Energy Distribution Chart */}
        <Card className="chart-card">
          <h3>🥧 Energieverteilung</h3>
          <Divider />
          <PieChart
            data={getEnergyDistribution()}
            height={300}
          />
        </Card>

        {/* Payback Period Visualization */}
        <Card className="chart-card full-width">
          <h3>💵 Amortisationsverlauf</h3>
          <Divider />
          <LineChart
            data={generatePaybackData()}
            lines={[
              { key: 'investment', name: 'Investition', color: '#ef4444' },
              { key: 'savings', name: 'Kumulierte Ersparnis', color: '#10b981' }
            ]}
            xKey="year"
            xLabel="Jahr"
            yLabel="Betrag (€)"
            height={350}
          />
          <div className="payback-info">
            <p>
              Die Anlage amortisiert sich nach{' '}
              <strong>{germanFormatter.format(results.economic_analysis.payback_period_years)} Jahren</strong>.
              Ab diesem Zeitpunkt übersteigen die kumulierten Einsparungen die Investitionskosten.
            </p>
          </div>
        </Card>

        {/* Cumulative Savings Over 25 Years */}
        <Card className="chart-card full-width">
          <h3>📈 Kumulierte Ersparnis über 25 Jahre</h3>
          <Divider />
          <AreaChart
            data={generateCumulativeSavings()}
            xKey="year"
            yKey="savings"
            xLabel="Jahr"
            yLabel="Kumulierte Ersparnis (€)"
            color="#3b82f6"
            height={350}
          />
          <div className="savings-summary">
            <div className="savings-item">
              <label>Ersparnis nach 20 Jahren:</label>
              <span className="savings-value">
                {germanFormatter.formatCurrency(results.economic_analysis.total_savings_20years)}
              </span>
            </div>
            <div className="savings-item">
              <label>Ersparnis nach 25 Jahren:</label>
              <span className="savings-value highlight">
                {germanFormatter.formatCurrency(results.economic_analysis.total_savings_25years)}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Detailed Metrics */}
      <Card className="detailed-metrics-card">
        <h3>📋 Detaillierte Kennzahlen</h3>
        <Divider />
        
        <div className="metrics-grid">
          <div className="metric-section">
            <h4>Systemdaten</h4>
            <div className="metric-row">
              <label>Anlagengröße:</label>
              <span>{germanFormatter.format(results.system_sizing.system_size_kwp)} kWp</span>
            </div>
            <div className="metric-row">
              <label>Modulanzahl:</label>
              <span>{results.system_sizing.module_count} Stück</span>
            </div>
            <div className="metric-row">
              <label>Modulleistung:</label>
              <span>{results.system_sizing.module_capacity_w} W</span>
            </div>
            <div className="metric-row">
              <label>Spezifischer Ertrag:</label>
              <span>{germanFormatter.format(results.system_sizing.specific_yield_kwh_kwp)} kWh/kWp</span>
            </div>
          </div>

          <div className="metric-section">
            <h4>Energieproduktion</h4>
            <div className="metric-row">
              <label>Jahresproduktion:</label>
              <span>{germanFormatter.format(results.energy_production.annual_production_kwh)} kWh</span>
            </div>
            <div className="metric-row">
              <label>Eigenverbrauch:</label>
              <span>{germanFormatter.format(results.self_consumption.annual_self_consumption_kwh)} kWh</span>
            </div>
            <div className="metric-row">
              <label>Netzeinspeisung:</label>
              <span>{germanFormatter.format(results.self_consumption.annual_grid_feed_in_kwh)} kWh</span>
            </div>
            <div className="metric-row">
              <label>Netzbezug:</label>
              <span>{germanFormatter.format(results.self_consumption.annual_grid_purchase_kwh)} kWh</span>
            </div>
          </div>

          <div className="metric-section">
            <h4>Wirtschaftlichkeit</h4>
            <div className="metric-row">
              <label>Investition (netto):</label>
              <span>{germanFormatter.formatCurrency(results.economic_analysis.total_investment_cost_net)}</span>
            </div>
            <div className="metric-row">
              <label>Investition (brutto):</label>
              <span>{germanFormatter.formatCurrency(results.economic_analysis.total_investment_cost_gross)}</span>
            </div>
            <div className="metric-row">
              <label>Jährliche Ersparnis:</label>
              <span>{germanFormatter.formatCurrency(results.economic_analysis.annual_savings_year1)}</span>
            </div>
            <div className="metric-row">
              <label>Amortisationszeit:</label>
              <span>{germanFormatter.format(results.economic_analysis.payback_period_years)} Jahre</span>
            </div>
            {results.economic_analysis.net_present_value && (
              <div className="metric-row">
                <label>Kapitalwert (NPV):</label>
                <span>{germanFormatter.formatCurrency(results.economic_analysis.net_present_value)}</span>
              </div>
            )}
            {results.economic_analysis.internal_rate_of_return_percent && (
              <div className="metric-row">
                <label>Interner Zinsfuß (IRR):</label>
                <span>{germanFormatter.format(results.economic_analysis.internal_rate_of_return_percent)}%</span>
              </div>
            )}
          </div>

          <div className="metric-section">
            <h4>Umweltbilanz</h4>
            <div className="metric-row">
              <label>CO₂-Einsparung/Jahr:</label>
              <span>{germanFormatter.format(results.environmental_impact.annual_co2_savings_kg)} kg</span>
            </div>
            <div className="metric-row">
              <label>CO₂-Einsparung 25 Jahre:</label>
              <span>{germanFormatter.format(results.environmental_impact.total_co2_savings_25years_kg / 1000)} t</span>
            </div>
            <div className="metric-row">
              <label>Entspricht Bäumen:</label>
              <span>{results.environmental_impact.equivalent_trees} Bäume</span>
            </div>
            <div className="metric-row">
              <label>Entspricht Autofahrt:</label>
              <span>{germanFormatter.format(results.environmental_impact.equivalent_car_km)} km</span>
            </div>
            {results.environmental_impact.co2_payback_time_years && (
              <div className="metric-row">
                <label>CO₂-Amortisation:</label>
                <span>{germanFormatter.format(results.environmental_impact.co2_payback_time_years)} Jahre</span>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Autarky Progress Bar */}
      <Card className="autarky-card">
        <h3>🎯 Autarkiegrad</h3>
        <Divider />
        <div className="autarky-visualization">
          <ProgressBar
            value={results.self_consumption.autarky_degree_percent}
            displayValueTemplate={(value) => `${germanFormatter.format(value)}%`}
            className="autarky-progress"
          />
          <p className="autarky-description">
            Sie decken <strong>{germanFormatter.format(results.self_consumption.autarky_degree_percent)}%</strong> Ihres
            Strombedarfs mit Ihrer eigenen PV-Anlage.
            {results.storage_analysis && (
              <> Der Batteriespeicher trägt zusätzlich{' '}
                <strong>{germanFormatter.format(results.storage_analysis.storage_contribution_to_autarky_percent)}%</strong> zur
                Autarkie bei.
              </>
            )}
          </p>
        </div>
      </Card>
    </div>
  );
};

export default SolarCalculationResults;
