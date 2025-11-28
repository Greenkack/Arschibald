/**
 * Heat Pump Financing Service
 * 
 * Frontend service for heat pump financing calculations.
 * 
 * Requirements: funktionen.txt - "Optionale Finanzierung"
 * Task: 256. Heat Pump Financing Options
 */

import api from './api';

// ==================== Enums ====================

export enum FinancingType {
  ANNUITY = 'annuity',
  LINEAR = 'linear',
  BALLOON = 'balloon',
  LEASING = 'leasing'
}

export enum SubsidyProgram {
  BAFA = 'bafa',
  KFW = 'kfw',
  REGIONAL = 'regional',
  NONE = 'none'
}

// ==================== Interfaces ====================

export interface FinancingRequest {
  total_investment_eur: number;
  loan_amount_eur?: number;
  interest_rate_percent?: number;
  term_years?: number;
  financing_type?: FinancingType;
  down_payment_eur?: number;
  subsidy_program?: SubsidyProgram;
  subsidy_percent?: number;
}

export interface MonthlyPayment {
  month: number;
  payment_eur: number;
  principal_eur: number;
  interest_eur: number;
  remaining_balance_eur: number;
}

export interface FinancingResult {
  loan_amount_eur: number;
  monthly_payment_eur: number;
  total_payments_eur: number;
  total_interest_eur: number;
  effective_interest_rate_percent: number;
  subsidy_amount_eur: number;
  net_investment_eur: number;
  payment_schedule: MonthlyPayment[];
  summary: {
    total_investment: number;
    subsidy: number;
    down_payment: number;
    loan_amount: number;
    term_years: number;
    interest_rate: number;
    financing_type: string;
  };
}


export interface AmortizationRequest {
  annual_savings_eur: number;
  financing: FinancingRequest;
  energy_price_increase_percent?: number;
}

export interface YearlyCashflow {
  year: number;
  savings_eur: number;
  financing_cost_eur: number;
  net_cashflow_eur: number;
  cumulative_savings_eur: number;
  cumulative_costs_eur: number;
}

export interface AmortizationResult {
  payback_period_years: number;
  payback_period_with_financing_years: number;
  total_savings_20_years_eur: number;
  total_cost_20_years_eur: number;
  net_benefit_20_years_eur: number;
  roi_percent: number;
  yearly_cashflow: YearlyCashflow[];
}

export interface FinancingScenario {
  term_years: number;
  monthly_payment_eur: number;
  total_payments_eur: number;
  total_interest_eur: number;
  net_benefit_20y_eur: number;
  monthly_net_cashflow_eur: number;
}

export interface FinancingComparison {
  scenarios: FinancingScenario[];
  best_scenario: string;
  recommendation: string;
}

export interface SubsidyProgramInfo {
  program: string;
  name: string;
  description: string;
  base_rate_percent: number;
  oil_bonus_percent?: number;
  max_rate_percent?: number;
  max_amount_eur?: number;
  max_loan_eur?: number;
  interest_rate_percent?: number;
  requirements?: string[];
  note?: string;
}

export interface ROIImpact {
  without_financing: {
    payback_years: number;
    roi_20_years_percent: number;
    total_savings_20y_eur: number;
  };
  with_financing: {
    monthly_payment_eur: number;
    total_financing_cost_eur: number;
    subsidy_eur: number;
    roi_20_years_percent: number;
    net_benefit_20y_eur: number;
  };
  comparison: {
    roi_difference_percent: number;
    financing_recommended: boolean;
  };
}

// ==================== Service Class ====================

class HeatpumpFinancingService {
  private baseUrl = '/api/v1/heatpump/financing';

  // ==================== Main Calculations ====================

  async calculateFinancing(request: FinancingRequest): Promise<FinancingResult> {
    const response = await api.post(`${this.baseUrl}/calculate`, request);
    return response.data;
  }

  async calculateAmortization(request: AmortizationRequest): Promise<AmortizationResult> {
    const response = await api.post(`${this.baseUrl}/amortization`, request);
    return response.data;
  }

  async compareScenarios(
    totalInvestmentEur: number,
    annualSavingsEur: number,
    scenarios: string = '5,10,15,20'
  ): Promise<FinancingComparison> {
    const response = await api.post(`${this.baseUrl}/compare`, null, {
      params: {
        total_investment_eur: totalInvestmentEur,
        annual_savings_eur: annualSavingsEur,
        scenarios
      }
    });
    return response.data;
  }

  // ==================== Quick Calculations ====================

  async quickCalculation(
    investmentEur: number,
    termYears: number = 15,
    interestRatePercent: number = 4.5,
    subsidyPercent: number = 30
  ): Promise<{
    investment_eur: number;
    subsidy_eur: number;
    loan_amount_eur: number;
    monthly_payment_eur: number;
    total_payments_eur: number;
    total_interest_eur: number;
    term_years: number;
    interest_rate_percent: number;
  }> {
    const response = await api.get(`${this.baseUrl}/quick-calculation`, {
      params: {
        investment_eur: investmentEur,
        term_years: termYears,
        interest_rate_percent: interestRatePercent,
        subsidy_percent: subsidyPercent
      }
    });
    return response.data;
  }

  async calculateROIImpact(
    investmentEur: number,
    annualSavingsEur: number,
    interestRatePercent: number = 4.5,
    termYears: number = 15,
    subsidyPercent: number = 30
  ): Promise<ROIImpact> {
    const response = await api.get(`${this.baseUrl}/roi-impact`, {
      params: {
        investment_eur: investmentEur,
        annual_savings_eur: annualSavingsEur,
        interest_rate_percent: interestRatePercent,
        term_years: termYears,
        subsidy_percent: subsidyPercent
      }
    });
    return response.data;
  }

  // ==================== Reference Data ====================

  async getSubsidyPrograms(): Promise<{
    programs: SubsidyProgramInfo[];
    combination_note: string;
  }> {
    const response = await api.get(`${this.baseUrl}/subsidies`);
    return response.data;
  }

  // ==================== Utility Methods ====================

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0
    }).format(amount);
  }

  formatCurrencyDetailed(amount: number): string {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  }

  formatPercent(value: number): string {
    return `${value.toFixed(1)} %`;
  }

  formatYears(years: number): string {
    return `${years} ${years === 1 ? 'Jahr' : 'Jahre'}`;
  }

  getFinancingTypeLabel(type: FinancingType): string {
    const labels: Record<FinancingType, string> = {
      [FinancingType.ANNUITY]: 'Annuitätendarlehen',
      [FinancingType.LINEAR]: 'Lineares Darlehen',
      [FinancingType.BALLOON]: 'Ballonfinanzierung',
      [FinancingType.LEASING]: 'Leasing'
    };
    return labels[type] || type;
  }

  getSubsidyProgramLabel(program: SubsidyProgram): string {
    const labels: Record<SubsidyProgram, string> = {
      [SubsidyProgram.BAFA]: 'BAFA Förderung',
      [SubsidyProgram.KFW]: 'KfW Förderung',
      [SubsidyProgram.REGIONAL]: 'Regionale Förderung',
      [SubsidyProgram.NONE]: 'Keine Förderung'
    };
    return labels[program] || program;
  }

  // Client-side calculations
  calculateMonthlyPayment(
    principal: number,
    annualRatePercent: number,
    termYears: number
  ): number {
    if (annualRatePercent === 0) {
      return principal / (termYears * 12);
    }
    
    const monthlyRate = annualRatePercent / 100 / 12;
    const numPayments = termYears * 12;
    
    const payment = principal * (monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
                   (Math.pow(1 + monthlyRate, numPayments) - 1);
    
    return Math.round(payment * 100) / 100;
  }

  calculateSubsidy(investment: number, program: SubsidyProgram): number {
    const rates: Record<SubsidyProgram, number> = {
      [SubsidyProgram.BAFA]: 30,
      [SubsidyProgram.KFW]: 25,
      [SubsidyProgram.REGIONAL]: 15,
      [SubsidyProgram.NONE]: 0
    };
    return investment * (rates[program] || 0) / 100;
  }

  calculatePaybackPeriod(investment: number, annualSavings: number): number {
    if (annualSavings <= 0) return Infinity;
    return investment / annualSavings;
  }

  calculateROI(investment: number, totalSavings: number): number {
    if (investment <= 0) return 0;
    return ((totalSavings - investment) / investment) * 100;
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{
    status: string;
    service: string;
    subsidy_programs: number;
    financing_types: number;
    timestamp: string;
  }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }
}

export const heatpumpFinancingService = new HeatpumpFinancingService();
export default heatpumpFinancingService;
