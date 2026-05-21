/**
 * Live Calculation Service
 * 
 * Frontend service for real-time PV system calculations.
 * 
 * Requirements: funktionen.txt - "Live-Berechnungen"
 * Task: 252. Live Calculation Engine
 */

import api from './api';

// ==================== Enums ====================

export type RoofOrientation = 
  | 'south' 
  | 'south_east' 
  | 'south_west' 
  | 'east' 
  | 'west' 
  | 'north' 
  | 'flat';

export type ConsumptionProfile = 
  | 'standard' 
  | 'home_office' 
  | 'evening' 
  | 'industrial';

// ==================== Interfaces ====================

export interface LiveCalculationRequest {
  module_count: number;
  module_power_wp?: number;
  location?: string;
  roof_orientation?: RoofOrientation;
  roof_angle?: number;
  annual_consumption_kwh?: number;
  consumption_profile?: ConsumptionProfile;
  battery_capacity_kwh?: number;
  battery_efficiency?: number;
  electricity_price?: number;
  feed_in_tariff?: number;
}

export interface LiveCalculationResult {
  // System Power
  system_power_kwp: number;
  module_count: number;
  module_power_wp: number;
  
  // Annual Yield
  annual_yield_kwh: number;
  specific_yield_kwh_kwp: number;
  yield_factor: number;
  
  // Self-Consumption & Autarky
  direct_consumption_kwh: number;
  direct_consumption_rate: number;
  self_consumption_kwh: number;
  self_consumption_rate: number;
  autarky_rate: number;
  
  // Storage
  storage_charge_kwh: number;
  storage_discharge_kwh: number;
  storage_cycles_per_year: number;
  storage_contribution_kwh: number;
  
  // Grid
  grid_feed_in_kwh: number;
  grid_purchase_kwh: number;
  
  // Financial
  annual_savings_eur: number;
  feed_in_revenue_eur: number;
  total_benefit_eur: number;
  
  // CO2
  co2_savings_kg: number;
}

export interface QuickCalculationRequest {
  module_count: number;
  module_power_wp?: number;
  annual_consumption_kwh?: number;
  battery_capacity_kwh?: number;
}

export interface MonthlyBreakdown {
  months: string[];
  production_kwh: number[];
  consumption_kwh: number[];
  self_consumption_kwh: number[];
  grid_feed_in_kwh: number[];
  grid_purchase_kwh: number[];
}

export interface SystemPowerResult {
  module_count: number;
  module_power_wp: number;
  system_power_kwp: number;
  system_power_wp: number;
}

export interface AnnualYieldResult {
  system_power_kwp: number;
  orientation: string;
  roof_angle: number;
  annual_yield_kwh: number;
  specific_yield_kwh_kwp: number;
  yield_factor: number;
  orientation_factor: number;
  angle_factor: number;
}

export interface SelfConsumptionResult {
  direct_consumption_kwh: number;
  direct_consumption_rate: number;
  self_consumption_kwh: number;
  self_consumption_rate: number;
  autarky_rate: number;
  storage_charge_kwh: number;
  storage_discharge_kwh: number;
  storage_cycles_per_year: number;
  storage_contribution_kwh: number;
  grid_feed_in_kwh: number;
  grid_purchase_kwh: number;
}

export interface AutarkyComparisonItem {
  battery_kwh: number;
  autarky_rate: number;
  self_consumption_rate: number;
  grid_purchase_kwh: number;
}

export interface AutarkyComparison {
  annual_yield_kwh: number;
  annual_consumption_kwh: number;
  comparison: AutarkyComparisonItem[];
}

// ==================== Service Class ====================

class LiveCalculationService {
  private baseUrl = '/api/v1/live-calculation';

  // ==================== Main Calculations ====================

  /**
   * Perform complete live calculation
   */
  async calculate(request: LiveCalculationRequest): Promise<LiveCalculationResult> {
    const response = await api.post(`${this.baseUrl}/calculate`, request);
    return response.data;
  }

  /**
   * Quick calculation with minimal inputs
   */
  async quickCalculate(request: QuickCalculationRequest): Promise<LiveCalculationResult> {
    const response = await api.post(`${this.baseUrl}/quick`, request);
    return response.data;
  }

  /**
   * Get monthly breakdown
   */
  async getMonthlyBreakdown(request: LiveCalculationRequest): Promise<MonthlyBreakdown> {
    const response = await api.post(`${this.baseUrl}/monthly-breakdown`, request);
    return response.data;
  }

  // ==================== Individual Calculations ====================

  /**
   * Calculate system power
   */
  async calculateSystemPower(moduleCount: number, modulePowerWp: number = 400): Promise<SystemPowerResult> {
    const response = await api.get(`${this.baseUrl}/system-power`, {
      params: { module_count: moduleCount, module_power_wp: modulePowerWp }
    });
    return response.data;
  }

  /**
   * Calculate annual yield
   */
  async calculateAnnualYield(
    systemPowerKwp: number,
    orientation: RoofOrientation = 'south',
    roofAngle: number = 30
  ): Promise<AnnualYieldResult> {
    const response = await api.get(`${this.baseUrl}/annual-yield`, {
      params: { system_power_kwp: systemPowerKwp, orientation, roof_angle: roofAngle }
    });
    return response.data;
  }

  /**
   * Calculate self-consumption
   */
  async calculateSelfConsumption(
    annualYieldKwh: number,
    annualConsumptionKwh: number,
    batteryCapacityKwh: number = 0,
    consumptionProfile: ConsumptionProfile = 'standard'
  ): Promise<SelfConsumptionResult> {
    const response = await api.get(`${this.baseUrl}/self-consumption`, {
      params: {
        annual_yield_kwh: annualYieldKwh,
        annual_consumption_kwh: annualConsumptionKwh,
        battery_capacity_kwh: batteryCapacityKwh,
        consumption_profile: consumptionProfile
      }
    });
    return response.data;
  }

  /**
   * Compare autarky with different battery sizes
   */
  async compareAutarky(annualYieldKwh: number, annualConsumptionKwh: number): Promise<AutarkyComparison> {
    const response = await api.get(`${this.baseUrl}/autarky-comparison`, {
      params: { annual_yield_kwh: annualYieldKwh, annual_consumption_kwh: annualConsumptionKwh }
    });
    return response.data;
  }

  // ==================== Reference Data ====================

  /**
   * Get orientation factors
   */
  async getOrientationFactors(): Promise<Record<RoofOrientation, number>> {
    const response = await api.get(`${this.baseUrl}/orientation-factors`);
    return response.data;
  }

  /**
   * Get consumption profiles
   */
  async getConsumptionProfiles(): Promise<Record<ConsumptionProfile, { daytime_ratio: number; description: string }>> {
    const response = await api.get(`${this.baseUrl}/consumption-profiles`);
    return response.data;
  }

  // ==================== Utility Methods ====================

  /**
   * Format power (kWp)
   */
  formatPower(powerKwp: number): string {
    return `${powerKwp.toFixed(2)} kWp`;
  }

  /**
   * Format energy (kWh)
   */
  formatEnergy(energyKwh: number): string {
    return new Intl.NumberFormat('de-DE', {
      maximumFractionDigits: 0
    }).format(energyKwh) + ' kWh';
  }

  /**
   * Format percentage
   */
  formatPercent(value: number): string {
    return `${value.toFixed(1)}%`;
  }

  /**
   * Format currency
   */
  formatCurrency(value: number): string {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(value);
  }

  /**
   * Format CO2
   */
  formatCO2(kg: number): string {
    if (kg >= 1000) {
      return `${(kg / 1000).toFixed(1)} t`;
    }
    return `${kg.toFixed(0)} kg`;
  }

  /**
   * Get orientation label in German
   */
  getOrientationLabel(orientation: RoofOrientation): string {
    const labels: Record<RoofOrientation, string> = {
      south: 'Süd',
      south_east: 'Südost',
      south_west: 'Südwest',
      east: 'Ost',
      west: 'West',
      north: 'Nord',
      flat: 'Flach'
    };
    return labels[orientation];
  }

  /**
   * Get consumption profile label in German
   */
  getConsumptionProfileLabel(profile: ConsumptionProfile): string {
    const labels: Record<ConsumptionProfile, string> = {
      standard: 'Standard-Haushalt',
      home_office: 'Home Office',
      evening: 'Abendverbrauch',
      industrial: 'Gewerblich'
    };
    return labels[profile];
  }

  /**
   * Get autarky status
   */
  getAutarkyStatus(rate: number): 'low' | 'medium' | 'good' | 'excellent' {
    if (rate >= 70) return 'excellent';
    if (rate >= 50) return 'good';
    if (rate >= 30) return 'medium';
    return 'low';
  }

  /**
   * Get autarky status label
   */
  getAutarkyStatusLabel(status: 'low' | 'medium' | 'good' | 'excellent'): string {
    const labels = {
      low: 'Gering',
      medium: 'Mittel',
      good: 'Gut',
      excellent: 'Ausgezeichnet'
    };
    return labels[status];
  }

  /**
   * Calculate simple system power locally (for instant feedback)
   */
  calculateSystemPowerLocal(moduleCount: number, modulePowerWp: number): number {
    return (moduleCount * modulePowerWp) / 1000;
  }

  /**
   * Estimate annual yield locally (for instant feedback)
   */
  estimateAnnualYieldLocal(systemPowerKwp: number, orientationFactor: number = 1.0): number {
    const baseYield = 950; // kWh/kWp for Germany
    return systemPowerKwp * baseYield * orientationFactor;
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{
    status: string;
    base_specific_yield: number;
    orientations: number;
    consumption_profiles: number;
  }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }
}

// Export singleton instance
export const liveCalculationService = new LiveCalculationService();
export default liveCalculationService;
