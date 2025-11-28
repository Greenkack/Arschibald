/**
 * Battery Storage Service
 * 
 * Frontend service for battery storage selection, sizing, and ROI analysis.
 * 
 * Requirements: funktionen.txt - "Batteriespeicher"
 * Task: 250. Battery Storage Configuration
 */

import api from './api';

// ==================== Interfaces ====================

export interface BatteryStorage {
  id: number;
  manufacturer: string;
  model_name: string;
  capacity_kwh: number;
  nominal_capacity_kwh: number;
  max_power_kw: number;
  efficiency_percent: number;
  cycle_life: number;
  warranty_years: number;
  warranty_cycles: number;
  depth_of_discharge: number;
  price_net: number;
  price_gross: number;
  price_per_kwh: number;
  weight_kg: number;
  dimensions: string | null;
  battery_type: string;
  features: string[];
  is_modular: boolean;
  min_modules: number;
  max_modules: number;
  compatible_inverters: string[];
  is_active: boolean;
}

export interface BatterySizingRequest {
  annual_consumption_kwh: number;
  pv_system_kwp: number;
  self_consumption_target?: number;
  autarky_target?: number;
  daily_consumption_kwh?: number;
}

export interface BatterySizingResult {
  recommended_capacity_kwh: number;
  capacity_range: {
    min_kwh: number;
    optimal_kwh: number;
    max_kwh: number;
  };
  expected_autarky: number;
  expected_self_consumption: number;
  daily_cycles: number;
  sizing_factors: {
    daily_consumption_kwh: number;
    daily_pv_production_kwh: number;
    surplus_energy_kwh: number;
    evening_consumption_kwh: number;
  };
}

export interface BatterySelectionRequest {
  required_capacity_kwh: number;
  preferred_manufacturer?: string;
  max_budget?: number;
  required_features?: string[];
  compatible_inverter?: string;
  is_modular_required?: boolean;
}

export interface BatterySelectionResult {
  selected_battery: BatteryStorage | null;
  selection_score: number;
  capacity_match: number;
  alternatives: BatteryStorage[];
  reasoning: string;
}

export interface BatteryROIRequest {
  battery_id: number;
  annual_consumption_kwh: number;
  pv_production_kwh: number;
  electricity_price?: number;
  feed_in_tariff?: number;
  electricity_price_increase?: number;
  analysis_years?: number;
}

export interface YearlyBreakdown {
  year: number;
  annual_savings_eur: number;
  cumulative_savings_eur: number;
  electricity_price_eur: number;
  degradation_percent: number;
}

export interface BatteryROIResult {
  payback_years: number;
  total_savings_eur: number;
  annual_savings_eur: number;
  roi_percent: number;
  npv_eur: number;
  yearly_breakdown: YearlyBreakdown[];
}

export interface BatteryComparison {
  batteries: BatteryStorage[];
  comparison: {
    capacity_range: { min: number; max: number };
    price_range: { min: number; max: number };
    price_per_kwh_range: { min: number; max: number };
    efficiency_range: { min: number; max: number };
    best_value: string;
    highest_efficiency: string;
    longest_warranty: string;
  };
}

// ==================== Service Class ====================

class BatteryStorageService {
  private baseUrl = '/api/v1/battery-storage';

  // ==================== Battery Retrieval ====================

  /**
   * Get all batteries with optional filters
   */
  async getAllBatteries(options?: {
    activeOnly?: boolean;
    includeNoStorage?: boolean;
    manufacturer?: string;
    minCapacity?: number;
    maxCapacity?: number;
    modularOnly?: boolean;
  }): Promise<BatteryStorage[]> {
    const params: Record<string, any> = {};
    if (options?.activeOnly !== undefined) params.active_only = options.activeOnly;
    if (options?.includeNoStorage !== undefined) params.include_no_storage = options.includeNoStorage;
    if (options?.manufacturer) params.manufacturer = options.manufacturer;
    if (options?.minCapacity !== undefined) params.min_capacity = options.minCapacity;
    if (options?.maxCapacity !== undefined) params.max_capacity = options.maxCapacity;
    if (options?.modularOnly !== undefined) params.modular_only = options.modularOnly;
    
    const response = await api.get(`${this.baseUrl}/`, { params });
    return response.data;
  }

  /**
   * Get battery by ID
   */
  async getBattery(batteryId: number): Promise<BatteryStorage> {
    const response = await api.get(`${this.baseUrl}/${batteryId}`);
    return response.data;
  }

  /**
   * Get list of all manufacturers
   */
  async getManufacturers(): Promise<string[]> {
    const response = await api.get(`${this.baseUrl}/manufacturers`);
    return response.data;
  }

  /**
   * Get "kein Speicher" (no storage) option
   */
  async getNoStorageOption(): Promise<BatteryStorage> {
    const response = await api.get(`${this.baseUrl}/no-storage`);
    return response.data;
  }

  // ==================== Sizing & Selection ====================

  /**
   * Calculate optimal battery size
   */
  async calculateSizing(request: BatterySizingRequest): Promise<BatterySizingResult> {
    const response = await api.post(`${this.baseUrl}/calculate-sizing`, request);
    return response.data;
  }

  /**
   * Select optimal battery for requirements
   */
  async selectBattery(request: BatterySelectionRequest): Promise<BatterySelectionResult> {
    const response = await api.post(`${this.baseUrl}/select`, request);
    return response.data;
  }

  /**
   * Calculate ROI analysis for battery
   */
  async calculateROI(request: BatteryROIRequest): Promise<BatteryROIResult> {
    const response = await api.post(`${this.baseUrl}/calculate-roi`, request);
    return response.data;
  }

  /**
   * Compare multiple batteries
   */
  async compareBatteries(batteryIds: number[]): Promise<BatteryComparison> {
    const idsString = batteryIds.join(',');
    const response = await api.get(`${this.baseUrl}/compare/${idsString}`);
    return response.data;
  }

  /**
   * Get batteries compatible with inverter
   */
  async getCompatibleBatteries(inverterManufacturer: string): Promise<{
    inverter_manufacturer: string;
    compatible_batteries: BatteryStorage[];
    count: number;
  }> {
    const response = await api.get(`${this.baseUrl}/compatible/${inverterManufacturer}`);
    return response.data;
  }

  // ==================== Utility Methods ====================

  /**
   * Format battery name
   */
  formatBatteryName(battery: BatteryStorage): string {
    if (battery.id === 0) return 'Kein Speicher';
    return `${battery.manufacturer} ${battery.model_name}`;
  }

  /**
   * Format capacity
   */
  formatCapacity(capacityKwh: number): string {
    return `${capacityKwh.toFixed(1)} kWh`;
  }

  /**
   * Format price
   */
  formatPrice(price: number): string {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  }

  /**
   * Format price per kWh
   */
  formatPricePerKwh(pricePerKwh: number): string {
    return `${new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(pricePerKwh)}/kWh`;
  }

  /**
   * Format efficiency
   */
  formatEfficiency(efficiency: number): string {
    return `${efficiency.toFixed(1)}%`;
  }

  /**
   * Format cycle life
   */
  formatCycleLife(cycles: number): string {
    return `${cycles.toLocaleString('de-DE')} Zyklen`;
  }

  /**
   * Format warranty
   */
  formatWarranty(years: number, cycles?: number): string {
    if (cycles && cycles > 0) {
      return `${years} Jahre / ${cycles.toLocaleString('de-DE')} Zyklen`;
    }
    return `${years} Jahre`;
  }

  /**
   * Check if battery is "no storage" option
   */
  isNoStorage(battery: BatteryStorage): boolean {
    return battery.id === 0;
  }

  /**
   * Get battery category based on capacity
   */
  getBatteryCategory(capacityKwh: number): 'small' | 'medium' | 'large' | 'xlarge' {
    if (capacityKwh <= 5) return 'small';
    if (capacityKwh <= 10) return 'medium';
    if (capacityKwh <= 15) return 'large';
    return 'xlarge';
  }

  /**
   * Get category label in German
   */
  getCategoryLabel(category: 'small' | 'medium' | 'large' | 'xlarge'): string {
    const labels = {
      small: 'Klein (bis 5 kWh)',
      medium: 'Mittel (5-10 kWh)',
      large: 'Groß (10-15 kWh)',
      xlarge: 'Sehr groß (>15 kWh)'
    };
    return labels[category];
  }

  /**
   * Calculate estimated annual savings
   */
  calculateEstimatedSavings(
    capacityKwh: number,
    electricityPrice: number = 0.35,
    feedInTariff: number = 0.082,
    dailyCycles: number = 0.8
  ): number {
    const annualThroughput = capacityKwh * dailyCycles * 365 * 0.95; // 95% efficiency
    const savingsPerKwh = electricityPrice - feedInTariff;
    return annualThroughput * savingsPerKwh;
  }

  /**
   * Calculate simple payback period
   */
  calculateSimplePayback(
    batteryPrice: number,
    annualSavings: number
  ): number {
    if (annualSavings <= 0) return Infinity;
    return batteryPrice / annualSavings;
  }

  /**
   * Get ROI status
   */
  getROIStatus(paybackYears: number): 'excellent' | 'good' | 'moderate' | 'poor' {
    if (paybackYears <= 8) return 'excellent';
    if (paybackYears <= 12) return 'good';
    if (paybackYears <= 15) return 'moderate';
    return 'poor';
  }

  /**
   * Get ROI status label in German
   */
  getROIStatusLabel(status: 'excellent' | 'good' | 'moderate' | 'poor'): string {
    const labels = {
      excellent: 'Ausgezeichnet',
      good: 'Gut',
      moderate: 'Moderat',
      poor: 'Gering'
    };
    return labels[status];
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{
    status: string;
    battery_count: number;
    manufacturers: number;
    capacity_range: { min_kwh: number; max_kwh: number };
  }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }
}

// Export singleton instance
export const batteryStorageService = new BatteryStorageService();
export default batteryStorageService;
