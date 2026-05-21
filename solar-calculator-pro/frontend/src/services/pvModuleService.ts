/**
 * PV Module Service
 * 
 * Frontend service for PV module selection and calculations
 */

import api from './api';

export interface PVModule {
  id: number;
  manufacturer: string;
  model: string;
  power_wp: number;
  efficiency: number;
  width_mm: number;
  height_mm: number;
  weight_kg: number;
  cell_type: string;
  warranty_years: number;
  price_net: number;
  price_gross: number;
  datasheet_url?: string;
  image_url?: string;
  is_active: boolean;
}

export interface SystemPowerResult {
  module: {
    id: number;
    manufacturer: string;
    model: string;
    power_wp: number;
    efficiency: number;
  };
  module_count: number;
  total_power_wp: number;
  total_power_kwp: number;
  module_area_m2: number;
  total_area_m2: number;
  total_weight_kg: number;
  price_net: number;
  price_gross: number;
  price_per_kwp_net: number;
}

export interface ModuleRecommendation {
  module: {
    id: number;
    manufacturer: string;
    model: string;
    power_wp: number;
    efficiency: number;
    cell_type: string;
  };
  recommended_count: number;
  max_count: number;
  total_kwp: number;
  total_price_gross: number;
  price_per_kwp: number;
  roof_utilization: number;
}

export interface ModuleComparison {
  modules: Array<{
    id: number;
    manufacturer: string;
    model: string;
    power_wp: number;
    efficiency: number;
    dimensions: string;
    weight_kg: number;
    cell_type: string;
    warranty_years: number;
    price_net: number;
    price_gross: number;
    price_per_wp: number;
  }>;
  best: {
    highest_power: number;
    highest_efficiency: number;
    lowest_price: number;
    best_value: number;
    longest_warranty: number;
    lightest: number;
  };
}

export interface YieldEstimation {
  system_kwp: number;
  location_factor: number;
  orientation_factor: number;
  first_year_yield_kwh: number;
  total_25_years_kwh: number;
  average_annual_kwh: number;
  yields_by_year: Array<{
    year: number;
    yield_kwh: number;
    degradation_percent: number;
  }>;
}

class PVModuleService {
  private baseUrl = '/api/v1/pv-modules';

  // ==================== Module Retrieval ====================

  async getAllModules(activeOnly: boolean = true): Promise<PVModule[]> {
    const response = await api.get(`${this.baseUrl}/`, {
      params: { active_only: activeOnly }
    });
    return response.data;
  }

  async getModule(moduleId: number): Promise<PVModule> {
    const response = await api.get(`${this.baseUrl}/${moduleId}`);
    return response.data;
  }

  async getManufacturers(): Promise<string[]> {
    const response = await api.get(`${this.baseUrl}/manufacturers`);
    return response.data;
  }

  async getModulesByManufacturer(manufacturer: string): Promise<PVModule[]> {
    const response = await api.get(`${this.baseUrl}/by-manufacturer/${encodeURIComponent(manufacturer)}`);
    return response.data;
  }

  // ==================== Calculations ====================

  async calculateSystemPower(moduleId: number, moduleCount: number): Promise<SystemPowerResult> {
    const response = await api.post(`${this.baseUrl}/calculate-system`, {
      module_id: moduleId,
      module_count: moduleCount
    });
    return response.data;
  }

  async recommendModules(roofAreaM2: number, targetKwp?: number): Promise<ModuleRecommendation[]> {
    const response = await api.post(`${this.baseUrl}/recommend`, {
      roof_area_m2: roofAreaM2,
      target_kwp: targetKwp
    });
    return response.data;
  }

  async compareModules(moduleIds: number[]): Promise<ModuleComparison> {
    const response = await api.get(`${this.baseUrl}/compare`, {
      params: { module_ids: moduleIds.join(',') }
    });
    return response.data;
  }

  async estimateYield(
    moduleId: number, 
    moduleCount: number,
    locationFactor: number = 1000,
    orientationFactor: number = 1.0
  ): Promise<YieldEstimation> {
    const response = await api.post(`${this.baseUrl}/estimate-yield`, {
      module_id: moduleId,
      module_count: moduleCount,
      location_factor: locationFactor,
      orientation_factor: orientationFactor
    });
    return response.data;
  }

  // ==================== Utility Methods ====================

  formatModuleName(module: PVModule): string {
    return `${module.manufacturer} ${module.model}`;
  }

  formatPower(powerWp: number): string {
    return `${powerWp} Wp`;
  }

  formatKwp(kwp: number): string {
    return `${kwp.toFixed(2)} kWp`;
  }

  formatPrice(price: number): string {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  }

  formatEfficiency(efficiency: number): string {
    return `${efficiency.toFixed(1)}%`;
  }

  formatDimensions(module: PVModule): string {
    return `${module.width_mm} × ${module.height_mm} mm`;
  }

  getModuleArea(module: PVModule): number {
    return (module.width_mm / 1000) * (module.height_mm / 1000);
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{ status: string; active_modules?: number }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }
}

export const pvModuleService = new PVModuleService();
export default pvModuleService;
