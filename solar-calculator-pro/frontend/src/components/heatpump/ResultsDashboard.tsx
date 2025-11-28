/**
 * Heat Pump Results Dashboard Component
 * 
 * Displays heat pump calculation results including JAZ, costs, and savings.
 * 
 * Requirements: funktionen.txt - "Ergebnisgrößen"
 * Task: 257. Heat Pump Calculation Results
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  heatpumpResultsService,
  CalculationRequest,
  CalculationResult,
  OldHeatingSystem,
  HeatingSystemType
} from '../../services/heatpumpResultsService';
import './ResultsDashboard.css';

// ==================== Interfaces ====================

interface ResultsDashboardProps {
  heatingDemandKwh: number;
  hotWaterDemandKwh?: number;
  heatPumpCop?: number;
  heatingSystemType?: HeatingSystemType;
  oldHeatingSystem?: OldHeatingSystem;
  heatPumpPriceEur?: number;
  installationCostEur?: number;
  subsidyPercent?: number;
  electricityPriceEurKwh?: number;
  showCheatFactor?: boolean;
  onResultsChange?: (result: CalculationResult) => void;
}

// ==================== Component ====================

const ResultsDashboard: React.FC<ResultsDashboardProps> = ({
  heatingDemandKwh,
  hotWaterDemandKwh = 0,
  heatPumpCop = 4.0,
  heatingSystemType = HeatingSystemType.FLOOR_HEATING,
  oldHeatingSystem = OldHeatingSystem.GAS,
  heatPumpPriceEur = 15000,
  installationCostEur = 5000,
  subsidyPercent = 30,
  electricityPriceEurKwh = 0.30,
  showCheatFactor = false,
  onResultsChange
}) => {
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cheatFactor, setCheatFactor] = useState(1.0);
  const [activeTab, setActiveTab] = useState<'overview' | 'comparison' | 'monthly'>('overview');

  // Calculate results
  const calculateResults = useCallback(async () => {
    if (heatingDemandKwh <= 0) return;

    setLoading(true);
    setError(null);

    try {
      const request: CalculationRequest = {
        heating_demand_kwh: heatingDemandKwh,
        hot_water_demand_kwh: hotWaterDemandKwh,
        heat_pump_cop: heatPumpCop,
        heating_system_type: heatingSystemType,
        old_heating_system: oldHeatingSystem,
        electricity_price_eur_kwh: electricityPriceEurKwh,
        heat_pump_price_eur: heatPumpPriceEur,
        installation_cost_eur: installationCostEur,
        subsidy_percent: subsidyPercent,
        amortization_cheat_factor: cheatFactor
      };

      const calcResult = await heatpumpResultsService.calculate(request);
      setResult(calcResult);
      onResultsChange?.(calcResult);
    } catch (err: any) {
      setError(err.message || 'Berechnung fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  }, [
    heatingDemandKwh, hotWaterDemandKwh, heatPumpCop, heatingSystemType,
    oldHeatingSystem, electricityPriceEurKwh, heatPumpPriceEur,
    installationCostEur, subsidyPercent, cheatFactor, onResultsChange
  ]);

  useEffect(() => {
    const timer = setTimeout(calculateResults, 300);
    return () => clearTimeout(timer);
  }, [calculateResults]);

  if (loading) {
    return <div className="results-dashboard loading">Berechne Ergebnisse...</div>;
  }

  if (error) {
    return (
      <div className="results-dashboard error">
        <span>❌</span> {error}
      </div>
    );
  }

  if (!result) {
    return <div className="results-dashboard empty">Keine Ergebnisse verfügbar</div>;
  }

  return (
    <div className="results-dashboard">
      <div className="dashboard-header">
        <h3>📊 Berechnungsergebnisse</h3>
        {showCheatFactor && (
          <div className="cheat-factor-control">
            <label>Demo-Faktor:</label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={cheatFactor}
              onChange={(e) => setCheatFactor(parseFloat(e.target.value))}
            />
            <span>{cheatFactor.toFixed(1)}x</span>
          </div>
        )}
      </div>

      {/* Key Metrics */}
      <div className="key-metrics">
        <div className="metric-card primary">
          <span className="metric-icon">⚡</span>
          <div className="metric-content">
            <span className="metric-label">Jahresarbeitszahl (JAZ)</span>
            <span className="metric-value">{result.jaz.toFixed(2)}</span>
          </div>
        </div>

        <div className="metric-card success">
          <span className="metric-icon">💰</span>
          <div className="metric-content">
            <span className="metric-label">Jährliche Ersparnis</span>
            <span className="metric-value">
              {heatpumpResultsService.formatCurrency(result.annual_savings_eur)}
            </span>
            <span className="metric-detail">{result.savings_percent.toFixed(0)}% weniger</span>
          </div>
        </div>

        <div className="metric-card">
          <span className="metric-icon">🌱</span>
          <div className="metric-content">
            <span className="metric-label">CO₂-Einsparung</span>
            <span className="metric-value">
              {heatpumpResultsService.formatCO2(result.co2_savings_kg)}
            </span>
            <span className="metric-detail">pro Jahr</span>
          </div>
        </div>

        <div className="metric-card highlight">
          <span className="metric-icon">⏱️</span>
          <div className="metric-content">
            <span className="metric-label">Amortisation</span>
            <span className="metric-value">
              {result.amortization.adjusted_payback_years.toFixed(1)} Jahre
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Übersicht
        </button>
        <button
          className={activeTab === 'comparison' ? 'active' : ''}
          onClick={() => setActiveTab('comparison')}
        >
          Kostenvergleich
        </button>
        <button
          className={activeTab === 'monthly' ? 'active' : ''}
          onClick={() => setActiveTab('monthly')}
        >
          Monatlich
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="overview-grid">
              <div className="overview-section">
                <h4>Stromverbrauch Wärmepumpe</h4>
                <div className="overview-item">
                  <span>Jahresverbrauch</span>
                  <span>{heatpumpResultsService.formatEnergy(result.electricity_consumption_kwh)}</span>
                </div>
                <div className="overview-item">
                  <span>Stromkosten/Jahr</span>
                  <span>{heatpumpResultsService.formatCurrency(result.annual_electricity_cost_eur)}</span>
                </div>
              </div>

              <div className="overview-section">
                <h4>Amortisation</h4>
                <div className="overview-item">
                  <span>Nettoinvestition</span>
                  <span>{heatpumpResultsService.formatCurrency(result.amortization.net_investment_eur)}</span>
                </div>
                <div className="overview-item">
                  <span>Einsparung (20 Jahre)</span>
                  <span>{heatpumpResultsService.formatCurrency(result.amortization.total_savings_20_years_eur)}</span>
                </div>
                <div className="overview-item highlight">
                  <span>ROI (20 Jahre)</span>
                  <span>{result.amortization.roi_20_years_percent.toFixed(0)}%</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'comparison' && (
          <div className="comparison-tab">
            <div className="comparison-grid">
              <div className="comparison-card old">
                <h4>🔥 Altes System ({heatpumpResultsService.getOldSystemLabel(oldHeatingSystem)})</h4>
                <div className="comparison-item">
                  <span>Jahreskosten</span>
                  <span className="cost">{heatpumpResultsService.formatCurrency(result.cost_comparison.old_system.annual_cost_eur)}</span>
                </div>
                <div className="comparison-item">
                  <span>Verbrauch</span>
                  <span>{heatpumpResultsService.formatEnergy(result.cost_comparison.old_system.fuel_consumption_kwh)}</span>
                </div>
                <div className="comparison-item">
                  <span>CO₂-Emissionen</span>
                  <span>{heatpumpResultsService.formatCO2(result.cost_comparison.old_system.co2_emissions_kg)}</span>
                </div>
              </div>

              <div className="comparison-arrow">→</div>

              <div className="comparison-card new">
                <h4>❄️ Wärmepumpe (JAZ {result.jaz.toFixed(1)})</h4>
                <div className="comparison-item">
                  <span>Jahreskosten</span>
                  <span className="cost">{heatpumpResultsService.formatCurrency(result.cost_comparison.new_system.annual_cost_eur)}</span>
                </div>
                <div className="comparison-item">
                  <span>Stromverbrauch</span>
                  <span>{heatpumpResultsService.formatEnergy(result.cost_comparison.new_system.electricity_consumption_kwh)}</span>
                </div>
                <div className="comparison-item">
                  <span>CO₂-Emissionen</span>
                  <span>{heatpumpResultsService.formatCO2(result.cost_comparison.new_system.co2_emissions_kg)}</span>
                </div>
              </div>
            </div>

            <div className="savings-summary">
              <div className="savings-item">
                <span>Jährliche Ersparnis</span>
                <span className="savings-value">{heatpumpResultsService.formatCurrency(result.cost_comparison.annual_savings_eur)}</span>
              </div>
              <div className="savings-item">
                <span>Einsparung</span>
                <span className="savings-value">{result.cost_comparison.savings_percent.toFixed(0)}%</span>
              </div>
              <div className="savings-item">
                <span>CO₂-Reduktion</span>
                <span className="savings-value">{heatpumpResultsService.formatCO2(result.cost_comparison.co2_savings_kg)}</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'monthly' && (
          <div className="monthly-tab">
            <table className="monthly-table">
              <thead>
                <tr>
                  <th>Monat</th>
                  <th>Heizanteil</th>
                  <th>Strom (kWh)</th>
                  <th>WP-Kosten</th>
                  <th>Alt-Kosten</th>
                  <th>Ersparnis</th>
                </tr>
              </thead>
              <tbody>
                {result.monthly_breakdown.map((month) => (
                  <tr key={month.month_number}>
                    <td>{month.month}</td>
                    <td>{month.heating_share_percent}%</td>
                    <td>{month.electricity_kwh.toFixed(0)}</td>
                    <td>{heatpumpResultsService.formatCurrencyDetailed(month.electricity_cost_eur)}</td>
                    <td>{heatpumpResultsService.formatCurrencyDetailed(month.old_system_cost_eur)}</td>
                    <td className={month.savings_eur >= 0 ? 'positive' : 'negative'}>
                      {heatpumpResultsService.formatCurrencyDetailed(month.savings_eur)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsDashboard;
