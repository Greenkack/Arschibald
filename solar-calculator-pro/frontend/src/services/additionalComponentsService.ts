/**
 * Additional Components Service
 * 
 * Frontend service for additional PV system components:
 * - Wallbox (EV charging stations)
 * - Energy Management System (EMS)
 * - Power Optimizers
 * - Emergency Power Systems (Notstrom)
 * - Animal Protection (Tierabwehr)
 * 
 * Requirements: funktionen.txt - "Zusatzkomponenten"
 * Task: 251. Additional Components (Wallbox, EMS, Optimizer)
 */

import api from './api';

// ==================== Enums ====================

export type ComponentCategory = 
  | 'wallbox' 
  | 'ems' 
  | 'optimizer' 
  | 'emergency_power' 
  | 'animal_protection';

export type WallboxPhase = '1-phase' | '3-phase';

// ==================== Interfaces ====================

export interface ComponentBase {
  id: number;
  category: ComponentCategory;
  manufacturer: string;
  model_name: string;
  description: string;
  price_net: number;
  price_gross: number;
  features: string[];
  is_active: boolean;
}

export interface WallboxComponent extends ComponentBase {
  category: 'wallbox';
  power_kw: number;
  phase: WallboxPhase;
  cable_length_m: number;
  has_cable: boolean;
  has_rfid: boolean;
  has_load_management: boolean;
  has_solar_charging: boolean;
  connector_type: string;
}

export interface EMSComponent extends ComponentBase {
  category: 'ems';
  max_devices: number;
  has_app: boolean;
  has_cloud: boolean;
  supported_inverters: string[];
  supported_batteries: string[];
}

export interface OptimizerComponent extends ComponentBase {
  category: 'optimizer';
  max_power_w: number;
  efficiency_percent: number;
  warranty_years: number;
  price_per_module: number;
}

export interface EmergencyPowerComponent extends ComponentBase {
  category: 'emergency_power';
  power_kw: number;
  switchover_time_ms: number;
  supported_inverters: string[];
}

export interface AnimalProtectionComponent extends ComponentBase {
  category: 'animal_protection';
  protection_type: string;
  coverage_area_m2: number;
}

export type AnyComponent = 
  | WallboxComponent 
  | EMSComponent 
  | OptimizerComponent 
  | EmergencyPowerComponent 
  | AnimalProtectionComponent;

export interface CategoryInfo {
  id: ComponentCategory;
  name: string;
  count: number;
}

export interface ComponentCostItem {
  component: AnyComponent;
  quantity: number;
  cost_net: number;
  cost_gross: number;
}

export interface ComponentCostCalculation {
  components: ComponentCostItem[];
  subtotal_net: number;
  subtotal_gross: number;
  installation_cost: number;
  total_net: number;
  total_gross: number;
}

export interface OptimizerCostResult {
  optimizer: OptimizerComponent;
  module_count: number;
  price_per_module: number;
  total_net: number;
  total_gross: number;
}

export interface ComponentRecommendations {
  wallbox: WallboxComponent | null;
  ems: EMSComponent | null;
  optimizer: OptimizerComponent | null;
  emergency_power: EmergencyPowerComponent | null;
  animal_protection: AnimalProtectionComponent | null;
}

export interface ComponentSelectionRequest {
  category?: ComponentCategory;
  pv_system_kwp?: number;
  module_count?: number;
  inverter_manufacturer?: string;
  battery_manufacturer?: string;
  max_budget?: number;
}

// ==================== Service Class ====================

class AdditionalComponentsService {
  private baseUrl = '/api/v1/additional-components';

  // ==================== General ====================

  /**
   * Get all components with optional filters
   */
  async getAllComponents(options?: {
    category?: ComponentCategory;
    manufacturer?: string;
    activeOnly?: boolean;
  }): Promise<AnyComponent[]> {
    const params: Record<string, any> = {};
    if (options?.category) params.category = options.category;
    if (options?.manufacturer) params.manufacturer = options.manufacturer;
    if (options?.activeOnly !== undefined) params.active_only = options.activeOnly;
    
    const response = await api.get(`${this.baseUrl}/`, { params });
    return response.data;
  }

  /**
   * Get all categories with counts
   */
  async getCategories(): Promise<{ categories: CategoryInfo[] }> {
    const response = await api.get(`${this.baseUrl}/categories`);
    return response.data;
  }

  /**
   * Get component by ID
   */
  async getComponent(componentId: number): Promise<AnyComponent> {
    const response = await api.get(`${this.baseUrl}/${componentId}`);
    return response.data;
  }

  /**
   * Get all manufacturers
   */
  async getManufacturers(category?: ComponentCategory): Promise<string[]> {
    const params = category ? { category } : {};
    const response = await api.get(`${this.baseUrl}/manufacturers`, { params });
    return response.data;
  }

  // ==================== Wallboxes ====================

  /**
   * Get all wallboxes with optional filters
   */
  async getWallboxes(options?: {
    phase?: WallboxPhase;
    minPower?: number;
    maxPower?: number;
    hasSolarCharging?: boolean;
  }): Promise<WallboxComponent[]> {
    const params: Record<string, any> = {};
    if (options?.phase) params.phase = options.phase;
    if (options?.minPower !== undefined) params.min_power = options.minPower;
    if (options?.maxPower !== undefined) params.max_power = options.maxPower;
    if (options?.hasSolarCharging !== undefined) params.has_solar_charging = options.hasSolarCharging;
    
    const response = await api.get(`${this.baseUrl}/wallboxes`, { params });
    return response.data;
  }

  // ==================== EMS ====================

  /**
   * Get all EMS systems
   */
  async getEMSSystems(inverterManufacturer?: string): Promise<EMSComponent[]> {
    const params = inverterManufacturer ? { inverter_manufacturer: inverterManufacturer } : {};
    const response = await api.get(`${this.baseUrl}/ems`, { params });
    return response.data;
  }

  // ==================== Optimizers ====================

  /**
   * Get all power optimizers
   */
  async getOptimizers(minPower?: number): Promise<OptimizerComponent[]> {
    const params = minPower !== undefined ? { min_power: minPower } : {};
    const response = await api.get(`${this.baseUrl}/optimizers`, { params });
    return response.data;
  }

  /**
   * Calculate optimizer cost for module count
   */
  async calculateOptimizerCost(optimizerId: number, moduleCount: number): Promise<OptimizerCostResult> {
    const response = await api.post(`${this.baseUrl}/calculate-optimizer-cost`, null, {
      params: { optimizer_id: optimizerId, module_count: moduleCount }
    });
    return response.data;
  }

  // ==================== Emergency Power ====================

  /**
   * Get all emergency power systems
   */
  async getEmergencyPowerSystems(inverterManufacturer?: string): Promise<EmergencyPowerComponent[]> {
    const params = inverterManufacturer ? { inverter_manufacturer: inverterManufacturer } : {};
    const response = await api.get(`${this.baseUrl}/emergency-power`, { params });
    return response.data;
  }

  // ==================== Animal Protection ====================

  /**
   * Get all animal protection options
   */
  async getAnimalProtection(protectionType?: string): Promise<AnimalProtectionComponent[]> {
    const params = protectionType ? { protection_type: protectionType } : {};
    const response = await api.get(`${this.baseUrl}/animal-protection`, { params });
    return response.data;
  }

  // ==================== Cost Calculation ====================

  /**
   * Calculate total cost for selected components
   */
  async calculateTotalCost(componentIds: number[], moduleCount: number = 0): Promise<ComponentCostCalculation> {
    const response = await api.post(`${this.baseUrl}/calculate-total-cost`, componentIds, {
      params: { module_count: moduleCount }
    });
    return response.data;
  }

  // ==================== Recommendations ====================

  /**
   * Get component recommendations based on system configuration
   */
  async getRecommendations(request: ComponentSelectionRequest): Promise<ComponentRecommendations> {
    const response = await api.post(`${this.baseUrl}/recommend`, request);
    return response.data;
  }

  // ==================== Utility Methods ====================

  /**
   * Format component name
   */
  formatComponentName(component: AnyComponent): string {
    return `${component.manufacturer} ${component.model_name}`;
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
   * Format power (kW)
   */
  formatPower(powerKw: number): string {
    return `${powerKw.toFixed(1)} kW`;
  }

  /**
   * Get category display name
   */
  getCategoryName(category: ComponentCategory): string {
    const names: Record<ComponentCategory, string> = {
      wallbox: 'Wallbox',
      ems: 'Energiemanagement (EMS)',
      optimizer: 'Leistungsoptimierer',
      emergency_power: 'Notstrom',
      animal_protection: 'Tierabwehr'
    };
    return names[category];
  }

  /**
   * Get category icon
   */
  getCategoryIcon(category: ComponentCategory): string {
    const icons: Record<ComponentCategory, string> = {
      wallbox: 'pi pi-car',
      ems: 'pi pi-chart-line',
      optimizer: 'pi pi-bolt',
      emergency_power: 'pi pi-shield',
      animal_protection: 'pi pi-heart'
    };
    return icons[category];
  }

  /**
   * Check if component is wallbox
   */
  isWallbox(component: AnyComponent): component is WallboxComponent {
    return component.category === 'wallbox';
  }

  /**
   * Check if component is EMS
   */
  isEMS(component: AnyComponent): component is EMSComponent {
    return component.category === 'ems';
  }

  /**
   * Check if component is optimizer
   */
  isOptimizer(component: AnyComponent): component is OptimizerComponent {
    return component.category === 'optimizer';
  }

  /**
   * Check if component is emergency power
   */
  isEmergencyPower(component: AnyComponent): component is EmergencyPowerComponent {
    return component.category === 'emergency_power';
  }

  /**
   * Check if component is animal protection
   */
  isAnimalProtection(component: AnyComponent): component is AnimalProtectionComponent {
    return component.category === 'animal_protection';
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{
    status: string;
    total_components: number;
    categories: Record<string, number>;
  }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }
}

// Export singleton instance
export const additionalComponentsService = new AdditionalComponentsService();
export default additionalComponentsService;
