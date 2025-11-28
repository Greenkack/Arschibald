/**
 * Financing Calculator Component
 * 
 * Component for heat pump financing calculations.
 * 
 * Requirements: funktionen.txt - "Optionale Finanzierung"
 * Task: 256. Heat Pump Financing Options
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  heatpumpFinancingService,
  FinancingRequest,
  FinancingResult,
  AmortizationResult,
  FinancingType,
  SubsidyProgram
} from '../../services/heatpumpFinancingService';
import './FinancingCalculator.css';

// ==================== Interfaces ====================

interface FinancingCalculatorProps {
  totalInvestmentEur: number;
  annualSavingsEur?: number;
  onFinancingChange?: (result: FinancingResult) => void;
  onAmortizationChange?: (result: AmortizationResult) => void;
  showAmortization?: boolean;
}

// ==================== Component ====================

const FinancingCalculator: React.FC<FinancingCalculatorProps> = ({
  totalInvestmentEur,
  annualSavingsEur = 0,
  onFinancingChange,
  onAmortizationChange,
  showAmortization = true
}) => {
  // Form state
  const [interestRate, setInterestRate] = useState(4.5);
  const [termYears, setTermYears] = useState(15);
  const [downPayment, setDownPayment] = useState(0);
  const [subsidyProgram, setSubsidyProgram] = useState<SubsidyProgram>(SubsidyProgram.BAFA);
  const [customSubsidyRate, setCustomSubsidyRate] = useState<number | null>(null);
  const [financingType, setFinancingType] = useState<FinancingType>(FinancingType.ANNUITY);
  const [energyPriceIncrease, setEnergyPriceIncrease] = useState(3.0);

  // Results
  const [financingResult, setFinancingResult] = useState<FinancingResult | null>(null);
  const [amortizationResult, setAmortizationResult] = useState<AmortizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Calculate financing
  const calculateFinancing = useCallback(async () => {
    if (totalInvestmentEur <= 0) return;

    setLoading(true);
    setError(null);

    try {
      const request: FinancingRequest = {
        total_investment_eur: totalInvestmentEur,
        interest_rate_percent: interestRate,
        term_years: termYears,
        down_payment_eur: downPayment,
        subsidy_program: subsidyProgram,
        subsidy_percent: customSubsidyRate ?? undefined,
        financing_type: financingType
      };

      const result = await heatpumpFinancingService.calculateFinancing(request);
      setFinancingResult(result);
      onFinancingChange?.(result);

      // Calculate amortization if savings provided
      if (showAmortization && annualSavingsEur > 0) {
        const amortization = await heatpumpFinancingService.calculateAmortization({
          annual_savings_eur: annualSavingsEur,
          financing: request,
          energy_price_increase_percent: energyPriceIncrease
        });
        setAmortizationResult(amortization);
        onAmortizationChange?.(amortization);
      }
    } catch (err: any) {
      setError(err.message || 'Berechnung fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  }, [
    totalInvestmentEur, interestRate, termYears, downPayment,
    subsidyProgram, customSubsidyRate, financingType,
    annualSavingsEur, energyPriceIncrease, showAmortization,
    onFinancingChange, onAmortizationChange
  ]);

  // Auto-calculate on changes
  useEffect(() => {
    const timer = setTimeout(calculateFinancing, 500);
    return () => clearTimeout(timer);
  }, [calculateFinancing]);

  // Get subsidy rate
  const getSubsidyRate = (): number => {
    if (customSubsidyRate !== null) return customSubsidyRate;
    const rates: Record<SubsidyProgram, number> = {
      [SubsidyProgram.BAFA]: 30,
      [SubsidyProgram.KFW]: 25,
      [SubsidyProgram.REGIONAL]: 15,
      [SubsidyProgram.NONE]: 0
    };
    return rates[subsidyProgram];
  };

  return (
    <div className="financing-calculator">
      <div className="calculator-header">
        <h3>💰 Finanzierungsrechner</h3>
        <p className="calculator-description">
          Berechnen Sie die Finanzierung für Ihre Wärmepumpe
        </p>
      </div>

      {/* Investment Summary */}
      <div className="investment-summary">
        <div className="summary-item">
          <span className="label">Gesamtinvestition</span>
          <span className="value">{heatpumpFinancingService.formatCurrency(totalInvestmentEur)}</span>
        </div>
        {annualSavingsEur > 0 && (
          <div className="summary-item">
            <span className="label">Jährliche Einsparung</span>
            <span className="value highlight">{heatpumpFinancingService.formatCurrency(annualSavingsEur)}</span>
          </div>
        )}
      </div>

      {/* Form */}
      <div className="form-grid">
        {/* Subsidy Program */}
        <div className="form-group">
          <label>Förderprogramm</label>
          <select
            value={subsidyProgram}
            onChange={(e) => {
              setSubsidyProgram(e.target.value as SubsidyProgram);
              setCustomSubsidyRate(null);
            }}
          >
            <option value={SubsidyProgram.BAFA}>BAFA (30%)</option>
            <option value={SubsidyProgram.KFW}>KfW (25%)</option>
            <option value={SubsidyProgram.REGIONAL}>Regional (15%)</option>
            <option value={SubsidyProgram.NONE}>Keine Förderung</option>
          </select>
        </div>

        {/* Custom Subsidy Rate */}
        <div className="form-group">
          <label>Fördersatz (%)</label>
          <input
            type="number"
            value={customSubsidyRate ?? getSubsidyRate()}
            onChange={(e) => setCustomSubsidyRate(parseFloat(e.target.value) || 0)}
            min={0}
            max={70}
            step={5}
          />
        </div>

        {/* Down Payment */}
        <div className="form-group">
          <label>Anzahlung (€)</label>
          <input
            type="number"
            value={downPayment}
            onChange={(e) => setDownPayment(parseFloat(e.target.value) || 0)}
            min={0}
            max={totalInvestmentEur}
            step={1000}
          />
        </div>

        {/* Interest Rate */}
        <div className="form-group">
          <label>Zinssatz (%)</label>
          <input
            type="number"
            value={interestRate}
            onChange={(e) => setInterestRate(parseFloat(e.target.value) || 0)}
            min={0}
            max={20}
            step={0.1}
          />
        </div>

        {/* Term */}
        <div className="form-group">
          <label>Laufzeit (Jahre)</label>
          <input
            type="number"
            value={termYears}
            onChange={(e) => setTermYears(parseInt(e.target.value) || 1)}
            min={1}
            max={30}
          />
        </div>

        {/* Financing Type */}
        <div className="form-group">
          <label>Darlehensart</label>
          <select
            value={financingType}
            onChange={(e) => setFinancingType(e.target.value as FinancingType)}
          >
            <option value={FinancingType.ANNUITY}>Annuitätendarlehen</option>
            <option value={FinancingType.LINEAR}>Lineares Darlehen</option>
          </select>
        </div>

        {showAmortization && annualSavingsEur > 0 && (
          <div className="form-group">
            <label>Energiepreissteigerung (%/Jahr)</label>
            <input
              type="number"
              value={energyPriceIncrease}
              onChange={(e) => setEnergyPriceIncrease(parseFloat(e.target.value) || 0)}
              min={0}
              max={20}
              step={0.5}
            />
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="error-message">
          <span>❌</span> {error}
        </div>
      )}

      {/* Results */}
      {financingResult && (
        <div className="results-section">
          <h4>📊 Finanzierungsergebnis</h4>
          
          <div className="results-grid">
            <div className="result-card primary">
              <span className="result-label">Monatliche Rate</span>
              <span className="result-value">
                {heatpumpFinancingService.formatCurrencyDetailed(financingResult.monthly_payment_eur)}
              </span>
            </div>

            <div className="result-card">
              <span className="result-label">Förderung</span>
              <span className="result-value highlight">
                {heatpumpFinancingService.formatCurrency(financingResult.subsidy_amount_eur)}
              </span>
            </div>

            <div className="result-card">
              <span className="result-label">Darlehensbetrag</span>
              <span className="result-value">
                {heatpumpFinancingService.formatCurrency(financingResult.loan_amount_eur)}
              </span>
            </div>

            <div className="result-card">
              <span className="result-label">Gesamtzinsen</span>
              <span className="result-value">
                {heatpumpFinancingService.formatCurrency(financingResult.total_interest_eur)}
              </span>
            </div>

            <div className="result-card">
              <span className="result-label">Gesamtkosten</span>
              <span className="result-value">
                {heatpumpFinancingService.formatCurrency(financingResult.total_payments_eur)}
              </span>
            </div>

            <div className="result-card">
              <span className="result-label">Effektivzins</span>
              <span className="result-value">
                {heatpumpFinancingService.formatPercent(financingResult.effective_interest_rate_percent)}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Amortization Results */}
      {amortizationResult && showAmortization && (
        <div className="amortization-section">
          <h4>📈 Amortisation mit Finanzierung</h4>
          
          <div className="amortization-grid">
            <div className="amort-card">
              <span className="amort-label">Amortisation (ohne Finanzierung)</span>
              <span className="amort-value">
                {amortizationResult.payback_period_years.toFixed(1)} Jahre
              </span>
            </div>

            <div className="amort-card highlight">
              <span className="amort-label">Amortisation (mit Finanzierung)</span>
              <span className="amort-value">
                {amortizationResult.payback_period_with_financing_years} Jahre
              </span>
            </div>

            <div className="amort-card">
              <span className="amort-label">Einsparung (20 Jahre)</span>
              <span className="amort-value">
                {heatpumpFinancingService.formatCurrency(amortizationResult.total_savings_20_years_eur)}
              </span>
            </div>

            <div className="amort-card success">
              <span className="amort-label">Nettogewinn (20 Jahre)</span>
              <span className="amort-value">
                {heatpumpFinancingService.formatCurrency(amortizationResult.net_benefit_20_years_eur)}
              </span>
            </div>

            <div className="amort-card">
              <span className="amort-label">ROI (20 Jahre)</span>
              <span className="amort-value">
                {amortizationResult.roi_percent.toFixed(1)} %
              </span>
            </div>
          </div>
        </div>
      )}

      {loading && <div className="loading-overlay">Berechne...</div>}
    </div>
  );
};

export default FinancingCalculator;
