/**
 * Inverter Service
 * 
 * Frontend service for inverter selection, sizing, and compatibility checks.
 * 
 * Requirements: funktionen.txt - "Wechselrichter"
 */

import api from './api';

// ==================== Interfaces ====================

export interface Inverter {
  id: number;
  manufacturer: string;
  model_name: string;
  power_kw: number;
  efficiency_percent: number;
  max_dc_voltage: number;
  mppt_count: number;
  max_dc_current: number;
  price_net: number;
  price_gross: number;
  warranty_years: number;
  weight_kg: number;
  features: string[];
  is_hybrid: boolean;
  is_active: boolean;
}

export interface InverterSizingRequest {
  pv_power_kwp: number;
  module_voltage_vmp?: number;
  module_current_imp?: number;
  modules_per_string?: number;
  number_of_strings?: number;
}

export interface InverterSizingResult {
  required_power_kw: number;
  recommended_power_range: {
    min_kw: number;
    optimal_kw: number;
    max_kw: number;
  };
  dc_specifications: {
    string_voltage: number;
    required_max_voltage: number;
    total_current: number;
    required_max_current: number;
  };
  mppt_configuration: {
    recommended_mppt_count: number;
    strings_per_mppt: number;
    current_per_mppt: number;
  };
  sizing_ratio: {
    dc_ac_ratio: number;
    description: string;
  };
}

export interface InverterSelectionRequest {
  pv_power_kwp: number;
  system_voltage?: number;
  preferred_manufacturer?: string;
  required_features?: string[];
  is_hybrid_required?: boolean;
}

export interface InverterSelectionResult {
  selected_inverter: Inverter;
  selection_score: number;
  sizing_ratio: number;
  alternatives: Inverter[];
  reasoning: string;
}

export interface CompatibilityCheckRequest {
  inverter_id: number;
  pv_power_kwp: number;
  string_voltage: number;
  total_current: number;
  number_of_strings: number;
}

export interface CompatibilityCheck {
  check: string;
  status: 'OK' | 'FEHLER' | 'WARNUNG';
  details: string;
}

export interface CompatibilityResult {
  is_compatible: boolean;
  compatibility_score: number;
  checks: CompatibilityCheck[];
  inverter: Inverter;
}

export interface MultiInverterConfig {
  configuration_type: 'single' | 'multi';
  inverter_count: number;
  inverters: Inverter[];
  total_power_kw: number;
  sizing_ratio?: number;
  power_distribution?: Array<{
    inverter_index: number;
    assigned_kwp: number;
  }>;
  reasoning: string;
}

// ==================== Service Class ====================

class InverterService {
  private baseUrl = '/api/v1/inverters';

  // ==================== Inverter Retrieval ====================

  /**
   * Get all inverters with optional filters
   */
  async getAllInverters(options?: {
    activeOnly?: boolean;
    hybridOnly?: boolean;
    manufacturer?: string;
  }): Promise<Inverter[]> {
    const params: Record<string, any> = {};
    if (options?.activeOnly !== undefined) params.active_only = options.activeOnly;
    if (options?.hybridOnly !== undefined) params.hybrid_only = options.hybridOnly;
    if (options?.manufacturer) params.manufacturer = options.manufacturer;
    
    const response = await api.get(`${this.baseUrl}/`, { params });
    return response.data;
  }

  /**
   * Get inverter by ID
   */
  async getInverter(inverterId: number): Promise<Inverter> {
    const response = await api.get(`${this.baseUrl}/${inverterId}`);
    return response.data;
  }

  /**
   * Get list of all manufacturers
   */
  async getManufacturers(): Promise<string[]> {
    const response = await api.get(`${this.baseUrl}/manufacturers`);
    return response.data;
  }

  // ==================== Sizing & Selection ====================

  /**
   * Calculate inverter sizing requirements
   */
  async calculateSizing(request: InverterSizingRequest): Promise<InverterSizingResult> {
    const response = await api.post(`${this.baseUrl}/calculate-sizing`, request);
    return response.data;
  }

  /**
   * Select optimal inverter for PV system
   */
  async selectInverter(request: InverterSelectionRequest): Promise<InverterSelectionResult> {
    const response = await api.post(`${this.baseUrl}/select`, request);
    return response.data;
  }

  /**
   * Check inverter compatibility with PV system
   */
  async checkCompatibility(request: CompatibilityCheckRequest): Promise<CompatibilityResult> {
    const response = await api.post(`${this.baseUrl}/check-compatibility`, request);
    return response.data;
  }

  /**
   * Create multi-inverter configuration for large systems
   */
  async createMultiInverterConfig(
    pvPowerKwp: number,
    roofSections?: Array<{ orientation: string; area_m2: number }>
  ): Promise<MultiInverterConfig> {
    const response = await api.post(`${this.baseUrl}/multi-inverter`, {
      pv_power_kwp: pvPowerKwp,
      roof_sections: roofSections || []
    });
    return response.data;
  }

  // ==================== Utility Methods ====================

  /**
   * Format inverter name
   */
  formatInverterName(inverter: Inverter): string {
    return `${inverter.manufacturer} ${inverter.model_name}`;
  }

  /**
   * Format power
   */
  formatPower(powerKw: number): string {
    return `${powerKw.toFixed(1)} kW`;
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
   * Format efficiency
   */
  formatEfficiency(efficiency: number): string {
    return `${efficiency.toFixed(1)}%`;
  }

  /**
   * Calculate DC/AC ratio
   */
  calculateDcAcRatio(pvPowerKwp: number, inverterPowerKw: number): number {
    return pvPowerKwp / inverterPowerKw;
  }

  /**
   * Check if DC/AC ratio is optimal
   */
  isDcAcRatioOptimal(ratio: number): boolean {
    return ratio >= 0.8 && ratio <= 1.2;
  }

  /**
   * Get DC/AC ratio status
   */
  getDcAcRatioStatus(ratio: number): 'optimal' | 'warning' | 'error' {
    if (ratio >= 0.9 && ratio <= 1.1) return 'optimal';
    if (ratio >= 0.8 && ratio <= 1.2) return 'warning';
    return 'error';
  }

  /**
   * Get recommended inverter power range
   */
  getRecommendedPowerRange(pvPowerKwp: number): { min: number; optimal: number; max: number } {
    return {
      min: pvPowerKwp * 0.8,
      optimal: pvPowerKwp * 0.9,
      max: pvPowerKwp * 1.0
    };
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{ status: string; inverter_count: number; manufacturers: number }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }
}

// Export singleton instance
export const inverterService = new InverterService();
export default inverterService;
