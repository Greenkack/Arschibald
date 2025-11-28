/**
 * Heat Pump Building Data Service
 * 
 * Frontend service for heat pump building data and heating load calculations.
 * 
 * Requirements: funktionen.txt - "Gebäude- und Heizungsdaten"
 * Task: 254. Heat Pump Building Data Integration
 */

import api from './api';

// ==================== Enums ====================

export enum InsulationStandard {
  POOR = 'poor',
  MODERATE = 'moderate',
  GOOD = 'good',
  EXCELLENT = 'excellent',
  PASSIVE_HOUSE = 'passive_house'
}

export enum HeatingSystemType {
  FLOOR_HEATING = 'floor_heating',
  RADIATORS_LOW = 'radiators_low',
  RADIATORS_HIGH = 'radiators_high',
  WALL_HEATING = 'wall_heating',
  CEILING_HEATING = 'ceiling_heating',
  MIXED = 'mixed'
}

export enum BuildingType {
  SINGLE_FAMILY = 'single_family',
  SEMI_DETACHED = 'semi_detached',
  ROW_HOUSE = 'row_house',
  APARTMENT = 'apartment',
  MULTI_FAMILY = 'multi_family',
  COMMERCIAL = 'commercial'
}

export enum OldHeatingSystem {
  OIL = 'oil',
  GAS = 'gas',
  ELECTRIC = 'electric',
  COAL = 'coal',
  WOOD = 'wood',
  DISTRICT = 'district',
  NONE = 'none'
}

// ==================== Interfaces ====================

export interface BuildingDataRequest {
  heated_area_m2: number;
  building_year?: number;
  building_type?: BuildingType;
  insulation_standard?: InsulationStandard;
  heating_system_type?: HeatingSystemType;
  old_heating_system?: OldHeatingSystem;
  number_of_floors?: number;
  number_of_residents?: number;
  hot_water_included?: boolean;
  location_climate_zone?: string;
}

export interface HeatingLoadResult {
  heating_load_kw: number;
  specific_heating_load_w_m2: number;
  annual_heating_demand_kwh: number;
  hot_water_demand_kwh: number;
  total_heat_demand_kwh: number;
  recommended_hp_power_kw: number;
  flow_temperature_c: number;
  calculation_details: {
    insulation_standard: string;
    building_type_factor: number;
    cop_factor: number;
    full_load_hours: number;
  };
}

export interface BuildingDataResponse {
  building_data: {
    heated_area_m2: number;
    building_year?: number;
    building_type: string;
    insulation_standard: string;
    heating_system_type: string;
    old_heating_system: string;
    number_of_floors: number;
    number_of_residents: number;
    hot_water_included: boolean;
  };
  heating_load: HeatingLoadResult;
  recommendations: string[];
  warnings: string[];
}

export interface InsulationInfo {
  standard: InsulationStandard;
  label_de: string;
  description_de: string;
  specific_heat_demand_kwh_m2: number;
  u_value_range: string;
  typical_building_years: string;
}

export interface HeatingSystemInfo {
  system_type: HeatingSystemType;
  label_de: string;
  description_de: string;
  flow_temperature_c: number;
  return_temperature_c: number;
  cop_factor: number;
  suitable_for_hp: boolean;
}

export interface BuildingTypeInfo {
  type: string;
  label_de: string;
  factor: number;
}

export interface OldHeatingSystemInfo {
  type: string;
  label_de: string;
  efficiency: number;
  co2_factor_kg_kwh: number;
}

export interface QuickCalculationResult {
  heated_area_m2: number;
  insulation_standard: string;
  heating_load_kw: number;
  annual_heating_demand_kwh: number;
  recommended_hp_power_kw: number;
  note: string;
}

// ==================== Service Class ====================

class HeatpumpBuildingService {
  private baseUrl = '/api/v1/heatpump/building';

  // ==================== Main Calculations ====================

  /**
   * Calculate heating load and demand from building data
   */
  async calculate(request: BuildingDataRequest): Promise<BuildingDataResponse> {
    const response = await api.post(`${this.baseUrl}/calculate`, request);
    return response.data;
  }

  /**
   * Quick calculation with minimal input
   */
  async quickCalculation(
    heatedAreaM2: number,
    buildingYear?: number,
    insulation?: InsulationStandard
  ): Promise<QuickCalculationResult> {
    const params: Record<string, any> = { heated_area_m2: heatedAreaM2 };
    if (buildingYear) params.building_year = buildingYear;
    if (insulation) params.insulation = insulation;
    
    const response = await api.get(`${this.baseUrl}/quick-calculation`, { params });
    return response.data;
  }

  // ==================== Reference Data ====================

  /**
   * Get all insulation standards
   */
  async getInsulationStandards(): Promise<InsulationInfo[]> {
    const response = await api.get(`${this.baseUrl}/insulation-standards`);
    return response.data;
  }

  /**
   * Get all heating system types
   */
  async getHeatingSystems(): Promise<HeatingSystemInfo[]> {
    const response = await api.get(`${this.baseUrl}/heating-systems`);
    return response.data;
  }

  /**
   * Get all building types
   */
  async getBuildingTypes(): Promise<{ building_types: BuildingTypeInfo[] }> {
    const response = await api.get(`${this.baseUrl}/building-types`);
    return response.data;
  }

  /**
   * Get all old heating system types
   */
  async getOldHeatingSystems(): Promise<{ old_heating_systems: OldHeatingSystemInfo[] }> {
    const response = await api.get(`${this.baseUrl}/old-heating-systems`);
    return response.data;
  }

  /**
   * Estimate insulation from building year
   */
  async estimateInsulation(buildingYear: number): Promise<{
    building_year: number;
    estimated_insulation: string;
    specific_heat_demand_kwh_m2: number;
    specific_heating_load_w_m2: number;
    note: string;
  }> {
    const response = await api.get(`${this.baseUrl}/estimate-insulation`, {
      params: { building_year: buildingYear }
    });
    return response.data;
  }

  // ==================== Utility Methods ====================

  /**
   * Get insulation standard label in German
   */
  getInsulationLabel(standard: InsulationStandard): string {
    const labels: Record<InsulationStandard, string> = {
      [InsulationStandard.POOR]: 'Unsaniert',
      [InsulationStandard.MODERATE]: 'Teilsaniert',
      [InsulationStandard.GOOD]: 'Gut gedämmt',
      [InsulationStandard.EXCELLENT]: 'Sehr gut gedämmt',
      [InsulationStandard.PASSIVE_HOUSE]: 'Passivhaus-Standard'
    };
    return labels[standard] || standard;
  }

  /**
   * Get heating system label in German
   */
  getHeatingSystemLabel(system: HeatingSystemType): string {
    const labels: Record<HeatingSystemType, string> = {
      [HeatingSystemType.FLOOR_HEATING]: 'Fußbodenheizung',
      [HeatingSystemType.RADIATORS_LOW]: 'Heizkörper (Niedertemperatur)',
      [HeatingSystemType.RADIATORS_HIGH]: 'Heizkörper (Hochtemperatur)',
      [HeatingSystemType.WALL_HEATING]: 'Wandheizung',
      [HeatingSystemType.CEILING_HEATING]: 'Deckenheizung',
      [HeatingSystemType.MIXED]: 'Gemischtes System'
    };
    return labels[system] || system;
  }

  /**
   * Get building type label in German
   */
  getBuildingTypeLabel(type: BuildingType): string {
    const labels: Record<BuildingType, string> = {
      [BuildingType.SINGLE_FAMILY]: 'Einfamilienhaus',
      [BuildingType.SEMI_DETACHED]: 'Doppelhaushälfte',
      [BuildingType.ROW_HOUSE]: 'Reihenhaus',
      [BuildingType.APARTMENT]: 'Wohnung',
      [BuildingType.MULTI_FAMILY]: 'Mehrfamilienhaus',
      [BuildingType.COMMERCIAL]: 'Gewerbe'
    };
    return labels[type] || type;
  }

  /**
   * Get old heating system label in German
   */
  getOldHeatingSystemLabel(system: OldHeatingSystem): string {
    const labels: Record<OldHeatingSystem, string> = {
      [OldHeatingSystem.OIL]: 'Ölheizung',
      [OldHeatingSystem.GAS]: 'Gasheizung',
      [OldHeatingSystem.ELECTRIC]: 'Elektroheizung',
      [OldHeatingSystem.COAL]: 'Kohleheizung',
      [OldHeatingSystem.WOOD]: 'Holzheizung',
      [OldHeatingSystem.DISTRICT]: 'Fernwärme',
      [OldHeatingSystem.NONE]: 'Keine/Neubau'
    };
    return labels[system] || system;
  }

  /**
   * Format heating load
   */
  formatHeatingLoad(loadKw: number): string {
    return `${loadKw.toFixed(1)} kW`;
  }

  /**
   * Format specific heating load
   */
  formatSpecificHeatingLoad(loadWM2: number): string {
    return `${loadWM2.toFixed(0)} W/m²`;
  }

  /**
   * Format energy demand
   */
  formatEnergyDemand(demandKwh: number): string {
    return new Intl.NumberFormat('de-DE', {
      maximumFractionDigits: 0
    }).format(demandKwh) + ' kWh/Jahr';
  }

  /**
   * Format area
   */
  formatArea(areaM2: number): string {
    return `${areaM2.toFixed(0)} m²`;
  }

  /**
   * Format temperature
   */
  formatTemperature(tempC: number): string {
    return `${tempC.toFixed(0)} °C`;
  }

  /**
   * Get insulation quality rating
   */
  getInsulationQuality(standard: InsulationStandard): 'poor' | 'fair' | 'good' | 'excellent' {
    switch (standard) {
      case InsulationStandard.POOR:
        return 'poor';
      case InsulationStandard.MODERATE:
        return 'fair';
      case InsulationStandard.GOOD:
        return 'good';
      case InsulationStandard.EXCELLENT:
      case InsulationStandard.PASSIVE_HOUSE:
        return 'excellent';
      default:
        return 'fair';
    }
  }

  /**
   * Check if heating system is suitable for heat pump
   */
  isHeatingSystemSuitable(system: HeatingSystemType): boolean {
    return system !== HeatingSystemType.RADIATORS_HIGH;
  }

  /**
   * Get COP factor for heating system
   */
  getCopFactor(system: HeatingSystemType): number {
    const factors: Record<HeatingSystemType, number> = {
      [HeatingSystemType.FLOOR_HEATING]: 1.0,
      [HeatingSystemType.WALL_HEATING]: 1.0,
      [HeatingSystemType.CEILING_HEATING]: 0.95,
      [HeatingSystemType.RADIATORS_LOW]: 0.9,
      [HeatingSystemType.RADIATORS_HIGH]: 0.8,
      [HeatingSystemType.MIXED]: 0.9
    };
    return factors[system] || 0.9;
  }

  /**
   * Get flow temperature for heating system
   */
  getFlowTemperature(system: HeatingSystemType): number {
    const temps: Record<HeatingSystemType, number> = {
      [HeatingSystemType.FLOOR_HEATING]: 35,
      [HeatingSystemType.WALL_HEATING]: 35,
      [HeatingSystemType.CEILING_HEATING]: 35,
      [HeatingSystemType.RADIATORS_LOW]: 45,
      [HeatingSystemType.RADIATORS_HIGH]: 55,
      [HeatingSystemType.MIXED]: 45
    };
    return temps[system] || 45;
  }

  /**
   * Estimate insulation from building year (client-side)
   */
  estimateInsulationFromYear(buildingYear: number): InsulationStandard {
    if (buildingYear < 1978) return InsulationStandard.POOR;
    if (buildingYear < 1995) return InsulationStandard.MODERATE;
    if (buildingYear < 2009) return InsulationStandard.GOOD;
    return InsulationStandard.EXCELLENT;
  }

  /**
   * Calculate estimated heating load (client-side quick estimate)
   */
  estimateHeatingLoad(heatedAreaM2: number, insulation: InsulationStandard): number {
    const specificLoads: Record<InsulationStandard, number> = {
      [InsulationStandard.POOR]: 120,
      [InsulationStandard.MODERATE]: 80,
      [InsulationStandard.GOOD]: 50,
      [InsulationStandard.EXCELLENT]: 35,
      [InsulationStandard.PASSIVE_HOUSE]: 15
    };
    const specificLoad = specificLoads[insulation] || 80;
    return (heatedAreaM2 * specificLoad) / 1000;
  }

  /**
   * Calculate estimated annual heating demand (client-side quick estimate)
   */
  estimateAnnualDemand(heatedAreaM2: number, insulation: InsulationStandard): number {
    const specificDemands: Record<InsulationStandard, number> = {
      [InsulationStandard.POOR]: 200,
      [InsulationStandard.MODERATE]: 130,
      [InsulationStandard.GOOD]: 80,
      [InsulationStandard.EXCELLENT]: 50,
      [InsulationStandard.PASSIVE_HOUSE]: 15
    };
    const specificDemand = specificDemands[insulation] || 130;
    return heatedAreaM2 * specificDemand;
  }

  /**
   * Recommend heat pump power
   */
  recommendHeatPumpPower(heatingLoadKw: number, includeHotWater: boolean = true): number {
    const bufferFactor = includeHotWater ? 1.15 : 1.0;
    const recommended = heatingLoadKw * bufferFactor;
    
    const commonSizes = [3, 5, 7, 9, 11, 14, 17, 20, 25, 30];
    for (const size of commonSizes) {
      if (recommended <= size) return size;
    }
    return Math.ceil(recommended);
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{
    status: string;
    service: string;
    insulation_standards: number;
    heating_systems: number;
    building_types: number;
    timestamp: string;
  }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }
}

// Export singleton instance
export const heatpumpBuildingService = new HeatpumpBuildingService();
export default heatpumpBuildingService;
