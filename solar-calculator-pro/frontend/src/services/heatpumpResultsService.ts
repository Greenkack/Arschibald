/**
 * Heat Pump Results Service
 * 
 * Frontend service for heat pump calculation results.
 * 
 * Requirements: funktionen.txt - "Ergebnisgrößen"
 * Task: 257. Heat Pump Calculation Results
 */

import api from './api';

// ==================== Enums ====================

export enum OldHeatingSystem {
  OIL = 'oil',
  GAS = 'gas',
  ELECTRIC = 'electric',
  COAL = 'coal',
  WOOD = 'wood',
  DISTRICT = 'district',
  LPG = 'lpg'
}

export enum HeatingSystemType {
  FLOOR_HEATING = 'floor_heating',
  RADIATORS_LOW = 'radiators_low',
  RADIATORS_HIGH = 'radiators_high',
  MIXED = 'mixed'
}

// ==================== Interfaces ====================

export interface CalculationRequest {
  heating_demand_kwh: number;
  hot_water_demand_kwh?: number;
  heat_pump_cop?: number;
  heating_system_type?: HeatingSystemType;
  old_heating_system?: OldHeatingSystem;
  old_system_efficiency?: number;
  electricity_price_eur_kwh?: number;
  old_fuel_price_eur_kwh?: number;
  heat_pump_price_eur?: number;
  installation_cost_eur?: number;
  subsidy_percent?: number;
  amortization_cheat_factor?: number;
}

export interface JAZRequest {
  cop_a7w35: number;
  cop_a2w35: number;
  cop_a_7w35?: number;
  heating_system_type?: HeatingSystemType;
  climate_zone?: string;
  hot_water_share_percent?: number;
}


export interface AmortizationResult {
  simple_payback_years: number;
  adjusted_payback_years: number;
  net_investment_eur: number;
  annual_savings_eur: number;
  total_savings_20_years_eur: number;
  roi_20_years_percent: number;
}

export interface HeatingCostComparison {
  old_system: {
    type: string;
    efficiency: number;
    annual_cost_eur: number;
    fuel_consumption_kwh: number;
    co2_emissions_kg: number;
  };
  new_system: {
    type: string;
    jaz: number;
    annual_cost_eur: number;
    electricity_consumption_kwh: number;
    co2_emissions_kg: number;
  };
  annual_savings_eur: number;
  savings_percent: number;
  co2_savings_kg: number;
}

export interface MonthlyBreakdown {
  month: string;
  month_number: number;
  heating_share_percent: number;
  electricity_kwh: number;
  electricity_cost_eur: number;
  old_system_cost_eur: number;
  savings_eur: number;
}

export interface CalculationResult {
  jaz: number;
  electricity_consumption_kwh: number;
  annual_electricity_cost_eur: number;
  old_heating_cost_eur: number;
  annual_savings_eur: number;
  savings_percent: number;
  co2_savings_kg: number;
  amortization: AmortizationResult;
  cost_comparison: HeatingCostComparison;
  monthly_breakdown: MonthlyBreakdown[];
}

export interface JAZResult {
  jaz: number;
  input_cops: {
    cop_a7w35: number;
    cop_a2w35: number;
    cop_a_7w35?: number;
  };
  factors: {
    flow_temperature_factor: number;
    climate_factor: number;
    hot_water_factor: number;
  };
  rating: string;
}

export interface FuelPrice {
  fuel: string;
  price_eur_kwh: number;
  label_de: string;
}

export interface CO2Factor {
  fuel: string;
  co2_kg_kwh: number;
  label_de: string;
}

// ==================== Service Class ====================

class HeatpumpResultsService {
  private baseUrl = '/api/v1/heatpump/results';

  // ==================== Main Calculations ====================

  async calculate(request: CalculationRequest): Promise<CalculationResult> {
    const response = await api.post(`${this.baseUrl}/calculate`, request);
    return response.data;
  }

  async calculateJAZ(request: JAZRequest): Promise<JAZResult> {
    const response = await api.post(`${this.baseUrl}/jaz`, request);
    return response.data;
  }

  // ==================== Quick Calculations ====================

  async getCostComparison(
    heatingDemandKwh: number,
    hotWaterDemandKwh: number = 0,
    jaz: number = 4.0,
    electricityPriceEurKwh: number = 0.30,
    oldSystem: OldHeatingSystem = OldHeatingSystem.GAS,
    oldEfficiency: number = 0.9
  ): Promise<{
    old_system: { type: string; annual_cost_eur: number; fuel_consumption_kwh: number };
    new_system: { type: string; annual_cost_eur: number; electricity_consumption_kwh: number };
    savings: { annual_eur: number; percent: number; monthly_eur: number };
  }> {
    const response = await api.get(`${this.baseUrl}/cost-comparison`, {
      params: {
        heating_demand_kwh: heatingDemandKwh,
        hot_water_demand_kwh: hotWaterDemandKwh,
        jaz,
        electricity_price_eur_kwh: electricityPriceEurKwh,
        old_system: oldSystem,
        old_efficiency: oldEfficiency
      }
    });
    return response.data;
  }

  async calculateAmortizationWithCheat(
    investmentEur: number,
    annualSavingsEur: number,
    subsidyPercent: number = 30,
    cheatFactor: number = 1.0
  ): Promise<{
    input: any;
    result: AmortizationResult;
    note?: string;
  }> {
    const response = await api.get(`${this.baseUrl}/amortization-cheat`, {
      params: {
        investment_eur: investmentEur,
        annual_savings_eur: annualSavingsEur,
        subsidy_percent: subsidyPercent,
        cheat_factor: cheatFactor
      }
    });
    return response.data;
  }

  async quickSavings(
    heatingDemandKwh: number,
    oldSystem: OldHeatingSystem = OldHeatingSystem.GAS,
    jaz: number = 4.0
  ): Promise<{
    heating_demand_kwh: number;
    old_system: string;
    jaz: number;
    old_annual_cost_eur: number;
    new_annual_cost_eur: number;
    annual_savings_eur: number;
    monthly_savings_eur: number;
  }> {
    const response = await api.get(`${this.baseUrl}/quick-savings`, {
      params: {
        heating_demand_kwh: heatingDemandKwh,
        old_system: oldSystem,
        jaz
      }
    });
    return response.data;
  }

  // ==================== Reference Data ====================

  async getFuelPrices(): Promise<{
    prices: FuelPrice[];
    electricity_price_eur_kwh: number;
    note: string;
  }> {
    const response = await api.get(`${this.baseUrl}/fuel-prices`);
    return response.data;
  }

  async getCO2Factors(): Promise<{
    factors: CO2Factor[];
    heat_pump_electricity_co2_kg_kwh: number;
    note: string;
  }> {
    const response = await api.get(`${this.baseUrl}/co2-factors`);
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
      minimumFractionDigits: 2
    }).format(amount);
  }

  formatEnergy(kwh: number): string {
    return new Intl.NumberFormat('de-DE', {
      maximumFractionDigits: 0
    }).format(kwh) + ' kWh';
  }

  formatCO2(kg: number): string {
    if (kg >= 1000) {
      return (kg / 1000).toFixed(1) + ' t CO₂';
    }
    return kg.toFixed(0) + ' kg CO₂';
  }

  formatPercent(value: number): string {
    return value.toFixed(1) + ' %';
  }

  formatYears(years: number): string {
    return years.toFixed(1) + ' Jahre';
  }

  getOldSystemLabel(system: OldHeatingSystem): string {
    const labels: Record<OldHeatingSystem, string> = {
      [OldHeatingSystem.OIL]: 'Heizöl',
      [OldHeatingSystem.GAS]: 'Erdgas',
      [OldHeatingSystem.ELECTRIC]: 'Strom (Direktheizung)',
      [OldHeatingSystem.COAL]: 'Kohle',
      [OldHeatingSystem.WOOD]: 'Holz/Pellets',
      [OldHeatingSystem.DISTRICT]: 'Fernwärme',
      [OldHeatingSystem.LPG]: 'Flüssiggas'
    };
    return labels[system] || system;
  }

  getHeatingSystemLabel(system: HeatingSystemType): string {
    const labels: Record<HeatingSystemType, string> = {
      [HeatingSystemType.FLOOR_HEATING]: 'Fußbodenheizung',
      [HeatingSystemType.RADIATORS_LOW]: 'Heizkörper (Niedertemperatur)',
      [HeatingSystemType.RADIATORS_HIGH]: 'Heizkörper (Hochtemperatur)',
      [HeatingSystemType.MIXED]: 'Gemischtes System'
    };
    return labels[system] || system;
  }

  getJAZRating(jaz: number): 'excellent' | 'good' | 'fair' | 'poor' {
    if (jaz >= 4.0) return 'excellent';
    if (jaz >= 3.5) return 'good';
    if (jaz >= 3.0) return 'fair';
    return 'poor';
  }

  getJAZRatingLabel(rating: string): string {
    const labels: Record<string, string> = {
      excellent: 'Sehr gut',
      good: 'Gut',
      fair: 'Befriedigend',
      poor: 'Ausreichend'
    };
    return labels[rating] || rating;
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{
    status: string;
    service: string;
    fuel_types: number;
    heating_systems: number;
    timestamp: string;
  }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }
}

export const heatpumpResultsService = new HeatpumpResultsService();
export default heatpumpResultsService;
