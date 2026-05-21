/**
 * PV + Heat Pump Integration Service
 * 
 * Frontend service for combined PV and heat pump calculations.
 * 
 * Requirements: funktionen.txt - "Integration PV + WP"
 * Task: 258. PV + Heat Pump Integration
 */

import api from './api';

// ==================== Interfaces ====================

export interface PVSystemData {
  system_power_kwp: number;
  annual_production_kwh: number;
  battery_capacity_kwh?: number;
  electricity_price_eur_kwh?: number;
  feed_in_tariff_eur_kwh?: number;
}

export interface HeatPumpData {
  heating_demand_kwh: number;
  hot_water_demand_kwh?: number;
  jaz?: number;
  electricity_consumption_kwh?: number;
}

export interface HouseholdData {
  annual_consumption_kwh: number;
  persons?: number;
}

export interface CombinedCalculationRequest {
  pv_system: PVSystemData;
  heat_pump: HeatPumpData;
  household: HouseholdData;
}

export interface SynergyResult {
  pv_to_heatpump_kwh: number;
  pv_to_heatpump_percent: number;
  heatpump_from_grid_kwh: number;
  heatpump_self_sufficiency_percent: number;
  synergy_savings_eur: number;
}

export interface MonthlyData {
  month: string;
  month_number: number;
  pv_production_kwh: number;
  household_demand_kwh: number;
  heatpump_demand_kwh: number;
  total_demand_kwh: number;
  self_consumption_kwh: number;
  grid_feed_in_kwh: number;
  grid_consumption_kwh: number;
  pv_to_heatpump_kwh: number;
}

export interface CombinedResult {
  total_electricity_demand_kwh: number;
  household_demand_kwh: number;
  heatpump_demand_kwh: number;
  pv_production_kwh: number;
  self_consumption_kwh: number;
  self_consumption_percent: number;
  grid_feed_in_kwh: number;
  grid_consumption_kwh: number;
  autarky_percent: number;
  autarky_without_hp_percent: number;
  synergy: SynergyResult;
  annual_savings_eur: number;
  pv_savings_eur: number;
  heatpump_savings_eur: number;
  combined_bonus_eur: number;
  monthly_data: MonthlyData[];
}

export interface SizingRecommendation {
  total_demand_kwh: number;
  household_demand_kwh: number;
  heatpump_demand_kwh: number;
  target_autarky_percent: number;
  recommended_pv_kwp: number;
  recommended_pv_production_kwh: number;
  recommended_battery_kwh: number;
  note: string;
}

// ==================== Service Class ====================

class PVHeatpumpIntegrationService {
  private baseUrl = '/api/v1/integration/pv-heatpump';

  async calculateCombined(request: CombinedCalculationRequest): Promise<CombinedResult> {
    const response = await api.post(`${this.baseUrl}/calculate`, request);
    return response.data;
  }

  async quickSynergy(
    pvProductionKwh: number,
    heatpumpConsumptionKwh: number,
    householdConsumptionKwh: number,
    batteryKwh: number = 0,
    electricityPrice: number = 0.30
  ): Promise<{
    total_demand_kwh: number;
    self_consumption_kwh: number;
    autarky_percent: number;
    pv_to_heatpump_kwh: number;
    heatpump_self_sufficiency_percent: number;
    synergy_savings_eur: number;
    recommendation: string;
  }> {
    const response = await api.get(`${this.baseUrl}/quick-synergy`, {
      params: {
        pv_production_kwh: pvProductionKwh,
        heatpump_consumption_kwh: heatpumpConsumptionKwh,
        household_consumption_kwh: householdConsumptionKwh,
        battery_kwh: batteryKwh,
        electricity_price: electricityPrice
      }
    });
    return response.data;
  }

  async getSizingRecommendation(
    heatingDemandKwh: number,
    householdConsumptionKwh: number,
    jaz: number = 4.0,
    targetAutarkyPercent: number = 50
  ): Promise<SizingRecommendation> {
    const response = await api.get(`${this.baseUrl}/sizing-recommendation`, {
      params: {
        heating_demand_kwh: heatingDemandKwh,
        household_consumption_kwh: householdConsumptionKwh,
        jaz,
        target_autarky_percent: targetAutarkyPercent
      }
    });
    return response.data;
  }

  // Utility methods
  formatEnergy(kwh: number): string {
    return new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 }).format(kwh) + ' kWh';
  }

  formatCurrency(eur: number): string {
    return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(eur);
  }

  formatPercent(value: number): string {
    return value.toFixed(1) + ' %';
  }

  async healthCheck(): Promise<{ status: string; service: string; timestamp: string }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }
}

export const pvHeatpumpIntegrationService = new PVHeatpumpIntegrationService();
export default pvHeatpumpIntegrationService;
