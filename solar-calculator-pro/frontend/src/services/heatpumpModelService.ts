/**
 * Heat Pump Model Service
 * 
 * Frontend service for heat pump model selection and sizing.
 * 
 * Requirements: funktionen.txt - "Wärmepumpen-Auslegung"
 * Task: 255. Heat Pump Model Selection
 */

import api from './api';

// ==================== Enums ====================

export enum HeatPumpType {
  AIR_WATER = 'air_water',
  BRINE_WATER = 'brine_water',
  WATER_WATER = 'water_water',
  AIR_AIR = 'air_air'
}

export enum HeatPumpCategory {
  MONOBLOCK = 'monoblock',
  SPLIT = 'split',
  INDOOR = 'indoor',
  HYBRID = 'hybrid'
}

export enum EfficiencyClass {
  A_PLUS_PLUS_PLUS = 'A+++',
  A_PLUS_PLUS = 'A++',
  A_PLUS = 'A+',
  A = 'A',
  B = 'B'
}

// ==================== Interfaces ====================

export interface HeatPumpModel {
  id: string;
  manufacturer: string;
  model_name: string;
  heat_pump_type: HeatPumpType;
  category: HeatPumpCategory;
  heating_power_kw: number;
  cop_a7w35: number;
  cop_a2w35: number;
  cop_a_7w35?: number;
  jaz_estimate: number;
  max_flow_temp_c: number;
  noise_level_db?: number;
  refrigerant: string;
  efficiency_class: string;
  price_net_eur: number;
  price_gross_eur: number;
  warranty_years: number;
  dimensions?: { width: number; height: number; depth: number };
  weight_kg?: number;
  features: string[];
  datasheet_url?: string;
  image_url?: string;
}


export interface HeatPumpSizingRequest {
  heating_load_kw: number;
  hot_water_included?: boolean;
  preferred_type?: HeatPumpType;
  max_price_eur?: number;
  min_cop?: number;
  max_noise_db?: number;
  flow_temperature_c?: number;
}

export interface BufferStorageRecommendation {
  recommended: boolean;
  min_volume_liters: number;
  optimal_volume_liters: number;
  reason: string;
  hot_water_storage_liters?: number;
}

export interface HeatPumpSizingResult {
  heating_load_kw: number;
  recommended_power_kw: number;
  sizing_factor: number;
  recommended_models: HeatPumpModel[];
  buffer_storage_recommendation: BufferStorageRecommendation;
  notes: string[];
}

export interface HeatPumpTypeInfo {
  type: string;
  label_de: string;
  description_de: string;
  pros: string[];
  cons: string[];
  typical_cop: string;
  suitable_for: string[];
}

export interface HeatPumpCategoryInfo {
  category: string;
  label_de: string;
  description_de: string;
}

export interface BufferStorageCalculation {
  heating_buffer: {
    min_volume_liters: number;
    optimal_volume_liters: number;
    reason: string;
  };
  hot_water_storage: {
    recommended_liters: number;
    per_person_liters: number;
    reason: string;
  };
  combined_recommendation: {
    total_volume_liters: number;
    note: string;
  };
}

export interface HeatPumpComparison {
  models: HeatPumpModel[];
  comparison: {
    best_cop: number;
    lowest_price: number;
    quietest: number;
    highest_power: number;
  };
}

// ==================== Service Class ====================

class HeatpumpModelService {
  private baseUrl = '/api/v1/heatpump/models';

  // ==================== Model Queries ====================

  async getAllModels(params?: {
    heat_pump_type?: HeatPumpType;
    category?: HeatPumpCategory;
    min_power_kw?: number;
    max_power_kw?: number;
    manufacturer?: string;
    sort_by?: 'cop' | 'price' | 'power' | 'noise';
  }): Promise<HeatPumpModel[]> {
    const response = await api.get(this.baseUrl, { params });
    return response.data;
  }

  async getModelById(modelId: string): Promise<HeatPumpModel> {
    const response = await api.get(`${this.baseUrl}/${modelId}`);
    return response.data;
  }

  // ==================== Sizing ====================

  async calculateSizing(request: HeatPumpSizingRequest): Promise<HeatPumpSizingResult> {
    const response = await api.post(`${this.baseUrl}/sizing`, request);
    return response.data;
  }

  // ==================== Reference Data ====================

  async getHeatPumpTypes(): Promise<{ types: HeatPumpTypeInfo[] }> {
    const response = await api.get(`${this.baseUrl}/types/list`);
    return response.data;
  }

  async getCategories(): Promise<{ categories: HeatPumpCategoryInfo[] }> {
    const response = await api.get(`${this.baseUrl}/categories/list`);
    return response.data;
  }

  async getManufacturers(): Promise<{ manufacturers: string[] }> {
    const response = await api.get(`${this.baseUrl}/manufacturers`);
    return response.data;
  }

  // ==================== Buffer Storage ====================

  async calculateBufferStorage(
    heatingPowerKw: number,
    hotWaterIncluded: boolean = true,
    numberOfResidents: number = 4
  ): Promise<BufferStorageCalculation> {
    const response = await api.get(`${this.baseUrl}/buffer-storage/calculate`, {
      params: {
        heating_power_kw: heatingPowerKw,
        hot_water_included: hotWaterIncluded,
        number_of_residents: numberOfResidents
      }
    });
    return response.data;
  }

  // ==================== Comparison ====================

  async compareModels(modelIds: string[]): Promise<HeatPumpComparison> {
    const response = await api.get(`${this.baseUrl}/compare`, {
      params: { model_ids: modelIds.join(',') }
    });
    return response.data;
  }

  // ==================== Utility Methods ====================

  getTypeLabel(type: HeatPumpType): string {
    const labels: Record<HeatPumpType, string> = {
      [HeatPumpType.AIR_WATER]: 'Luft/Wasser',
      [HeatPumpType.BRINE_WATER]: 'Sole/Wasser',
      [HeatPumpType.WATER_WATER]: 'Wasser/Wasser',
      [HeatPumpType.AIR_AIR]: 'Luft/Luft'
    };
    return labels[type] || type;
  }

  getCategoryLabel(category: HeatPumpCategory): string {
    const labels: Record<HeatPumpCategory, string> = {
      [HeatPumpCategory.MONOBLOCK]: 'Monoblock',
      [HeatPumpCategory.SPLIT]: 'Split-System',
      [HeatPumpCategory.INDOOR]: 'Innenaufstellung',
      [HeatPumpCategory.HYBRID]: 'Hybrid'
    };
    return labels[category] || category;
  }

  formatPower(powerKw: number): string {
    return `${powerKw.toFixed(1)} kW`;
  }

  formatCOP(cop: number): string {
    return cop.toFixed(2);
  }

  formatPrice(priceEur: number): string {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0
    }).format(priceEur);
  }

  formatNoise(noiseDb: number): string {
    return `${noiseDb.toFixed(0)} dB(A)`;
  }

  formatVolume(liters: number): string {
    return `${liters} Liter`;
  }

  getCOPRating(cop: number): 'poor' | 'fair' | 'good' | 'excellent' {
    if (cop >= 5.0) return 'excellent';
    if (cop >= 4.5) return 'good';
    if (cop >= 4.0) return 'fair';
    return 'poor';
  }

  getCOPRatingLabel(rating: string): string {
    const labels: Record<string, string> = {
      poor: 'Gering',
      fair: 'Mäßig',
      good: 'Gut',
      excellent: 'Ausgezeichnet'
    };
    return labels[rating] || rating;
  }

  getNoiseRating(noiseDb: number): 'quiet' | 'moderate' | 'loud' {
    if (noiseDb <= 50) return 'quiet';
    if (noiseDb <= 58) return 'moderate';
    return 'loud';
  }

  getNoiseRatingLabel(rating: string): string {
    const labels: Record<string, string> = {
      quiet: 'Leise',
      moderate: 'Moderat',
      loud: 'Laut'
    };
    return labels[rating] || rating;
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{
    status: string;
    service: string;
    total_models: number;
    manufacturers: number;
    timestamp: string;
  }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }
}

export const heatpumpModelService = new HeatpumpModelService();
export default heatpumpModelService;
