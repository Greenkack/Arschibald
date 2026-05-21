"""
Heat Pump Advanced Service

This service provides advanced heat pump calculation features including:
- All heat pump calculation types (air-source, ground-source, water-source)
- COP (Coefficient of Performance) calculations
- Dynamic tariff optimization
- Heating cost comparison
- Seasonal performance analysis
- Combined PV + heat pump optimization
- Smart grid integration calculations
- Environmental impact analysis
"""

import sys
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import math
import numpy as np
from dataclasses import dataclass

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.base_service import BaseService, HealthCheckResult, ServiceStatus
from backend.core.error_wrapper import handle_service_errors
from backend.core.logging_decorator import log_service_call


class HeatPumpType(str, Enum):
    """Heat pump types"""
    AIR_SOURCE = "air_source"
    GROUND_SOURCE = "ground_source"
    WATER_SOURCE = "water_source"
    HYBRID = "hybrid"


class HeatingSystem(str, Enum):
    """Heating system types"""
    RADIATORS = "radiators"
    UNDERFLOOR = "underfloor"
    FAN_COIL = "fan_coil"
    MIXED = "mixed"


class TariffType(str, Enum):
    """Electricity tariff types"""
    FLAT_RATE = "flat_rate"
    TIME_OF_USE = "time_of_use"
    DYNAMIC = "dynamic"
    HEAT_PUMP_TARIFF = "heat_pump_tariff"


@dataclass
class COPCalculation:
    """Coefficient of Performance calculation results"""
    cop_heating: float
    cop_cooling: float
    scop_seasonal: float  # Seasonal COP
    outdoor_temp_c: float
    indoor_temp_c: float
    flow_temp_c: float
    return_temp_c: float
    efficiency_percent: float
    power_consumption_kw: float
    heating_output_kw: float


@dataclass
class DynamicTariffOptimization:
    """Dynamic tariff optimization results"""
    optimal_schedule: List[Dict[str, Any]]  # Hourly schedule for 24h
    annual_cost_eur: float
    cost_savings_percent: float
    peak_avoidance_hours: List[int]
    optimal_heating_hours: List[int]
    storage_utilization_percent: float
    grid_friendly_score: float


@dataclass
class HeatingCostComparison:
    """Heating cost comparison results"""
    heat_pump_annual_cost_eur: float
    gas_annual_cost_eur: float
    oil_annual_cost_eur: float
    electric_annual_cost_eur: float
    savings_vs_gas_eur: float
    savings_vs_oil_eur: float
    savings_vs_electric_eur: float
    payback_period_years: float
    roi_25years_eur: float


@dataclass
class SeasonalPerformance:
    """Seasonal performance analysis"""
    winter_cop: float
    spring_cop: float
    summer_cop: float
    autumn_cop: float
    annual_average_cop: float
    monthly_cop: List[float]  # 12 months
    monthly_consumption_kwh: List[float]  # 12 months
    monthly_heating_demand_kwh: List[float]  # 12 months
    efficiency_variation_percent: float


@dataclass
class PVHeatPumpOptimization:
    """Combined PV + Heat Pump optimization"""
    pv_system_size_kwp: float
    heat_pump_capacity_kw: float
    annual_pv_production_kwh: float
    annual_hp_consumption_kwh: float
    self_consumption_rate_percent: float
    autarky_rate_percent: float
    grid_import_kwh: float
    grid_export_kwh: float
    combined_savings_eur: float
    synergy_benefit_eur: float
    optimal_operation_schedule: List[Dict[str, Any]]


@dataclass
class SmartGridIntegration:
    """Smart grid integration analysis"""
    demand_response_potential_kw: float
    load_shifting_capacity_kwh: float
    grid_stabilization_score: float
    peak_shaving_contribution_kw: float
    renewable_integration_score: float
    flexibility_value_eur_year: float
    grid_services_revenue_eur_year: float


@dataclass
class EnvironmentalImpact:
    """Environmental impact analysis"""
    annual_co2_savings_kg: float
    co2_savings_vs_gas_kg: float
    co2_savings_vs_oil_kg: float
    renewable_energy_percent: float
    primary_energy_factor: float
    environmental_score: float
    carbon_footprint_reduction_percent: float
    equivalent_trees_planted: int
    # Enhanced environmental metrics
    lifetime_co2_savings_kg: float  # 25 years
    carbon_footprint_kg_year: float
    carbon_footprint_tracking: List[Dict[str, Any]]  # Yearly tracking
    sustainability_rating: str  # A+, A, B, C, D, E, F
    environmental_certifications: List[str]
    renewable_energy_contribution_kwh: float
    fossil_fuel_replacement_percent: float
    air_quality_improvement_score: float
    water_conservation_liters_year: float
    noise_pollution_reduction_db: float



class HeatPumpAdvancedService(BaseService):
    """
    Advanced Heat Pump Service
    
    Provides comprehensive heat pump analysis including:
    - All heat pump calculation types
    - COP calculations
    - Dynamic tariff optimization
    - Heating cost comparison
    - Seasonal performance analysis
    - PV + heat pump optimization
    - Smart grid integration
    - Environmental impact analysis
    """
    
    def __init__(self):
        super().__init__("heatpump_advanced")
        self._cop_cache: Dict[str, COPCalculation] = {}
        self._tariff_cache: Dict[str, Any] = {}
        
    def initialize(self) -> None:
        """Initialize the advanced service"""
        try:
            self._set_initialized(True)
            self.logger.info("Heat Pump Advanced Service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            raise
    
    def health_check(self) -> HealthCheckResult:
        """Perform health check"""
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Service not initialized"
            )
        
        return HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="Service is healthy",
            details={
                "cop_cache_size": len(self._cop_cache),
                "tariff_cache_size": len(self._tariff_cache)
            }
        )

    # ========== Heat Pump Calculation Types ==========
    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="Air source heat pump calculation failed")
    def calculate_air_source_heat_pump(
        self,
        building_area_m2: float,
        insulation_quality: str,  # "poor", "average", "good", "excellent"
        outdoor_temp_c: float,
        indoor_temp_c: float,
        heating_system: HeatingSystem
    ) -> Dict[str, Any]:
        """
        Calculate air source heat pump performance
        
        Args:
            building_area_m2: Building area
            insulation_quality: Insulation quality level
            outdoor_temp_c: Outdoor temperature
            indoor_temp_c: Desired indoor temperature
            heating_system: Type of heating system
            
        Returns:
            Dictionary with air source heat pump calculation results
        """
        # Calculate heating demand
        heating_demand_kw = self._calculate_heating_demand(
            building_area_m2, insulation_quality, outdoor_temp_c, indoor_temp_c
        )
        
        # Calculate flow temperature based on heating system
        flow_temp_c = self._get_flow_temperature(heating_system, outdoor_temp_c)
        
        # Calculate COP for air source
        cop = self._calculate_air_source_cop(outdoor_temp_c, flow_temp_c)
        
        # Calculate power consumption
        power_consumption_kw = heating_demand_kw / cop
        
        # Calculate annual energy consumption
        annual_heating_hours = self._estimate_annual_heating_hours(outdoor_temp_c)
        annual_consumption_kwh = power_consumption_kw * annual_heating_hours
        
        return {
            "heat_pump_type": HeatPumpType.AIR_SOURCE,
            "heating_demand_kw": heating_demand_kw,
            "cop": cop,
            "power_consumption_kw": power_consumption_kw,
            "flow_temperature_c": flow_temp_c,
            "annual_consumption_kwh": annual_consumption_kwh,
            "annual_heating_hours": annual_heating_hours,
            "efficiency_percent": cop / 5.0 * 100  # Relative to theoretical max
        }

    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="Ground source heat pump calculation failed")
    def calculate_ground_source_heat_pump(
        self,
        building_area_m2: float,
        insulation_quality: str,
        ground_temp_c: float,
        indoor_temp_c: float,
        heating_system: HeatingSystem,
        collector_type: str = "horizontal"  # "horizontal" or "vertical"
    ) -> Dict[str, Any]:
        """
        Calculate ground source heat pump performance
        
        Args:
            building_area_m2: Building area
            insulation_quality: Insulation quality level
            ground_temp_c: Ground temperature (typically 8-12°C)
            indoor_temp_c: Desired indoor temperature
            heating_system: Type of heating system
            collector_type: Ground collector type
            
        Returns:
            Dictionary with ground source heat pump calculation results
        """
        # Calculate heating demand
        heating_demand_kw = self._calculate_heating_demand(
            building_area_m2, insulation_quality, 0.0, indoor_temp_c  # Use 0°C as reference
        )
        
        # Calculate flow temperature
        flow_temp_c = self._get_flow_temperature(heating_system, 0.0)
        
        # Calculate COP for ground source (higher than air source)
        cop = self._calculate_ground_source_cop(ground_temp_c, flow_temp_c)
        
        # Calculate power consumption
        power_consumption_kw = heating_demand_kw / cop
        
        # Calculate collector area needed
        collector_area_m2 = self._calculate_collector_area(
            heating_demand_kw, collector_type
        )
        
        # Calculate annual energy consumption
        annual_heating_hours = 2000  # More stable than air source
        annual_consumption_kwh = power_consumption_kw * annual_heating_hours
        
        return {
            "heat_pump_type": HeatPumpType.GROUND_SOURCE,
            "heating_demand_kw": heating_demand_kw,
            "cop": cop,
            "power_consumption_kw": power_consumption_kw,
            "flow_temperature_c": flow_temp_c,
            "annual_consumption_kwh": annual_consumption_kwh,
            "collector_type": collector_type,
            "collector_area_m2": collector_area_m2,
            "ground_temperature_c": ground_temp_c,
            "efficiency_percent": cop / 5.5 * 100
        }
    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="Water source heat pump calculation failed")
    def calculate_water_source_heat_pump(
        self,
        building_area_m2: float,
        insulation_quality: str,
        water_temp_c: float,
        indoor_temp_c: float,
        heating_system: HeatingSystem
    ) -> Dict[str, Any]:
        """
        Calculate water source heat pump performance
        
        Args:
            building_area_m2: Building area
            insulation_quality: Insulation quality level
            water_temp_c: Water source temperature
            indoor_temp_c: Desired indoor temperature
            heating_system: Type of heating system
            
        Returns:
            Dictionary with water source heat pump calculation results
        """
        # Calculate heating demand
        heating_demand_kw = self._calculate_heating_demand(
            building_area_m2, insulation_quality, 0.0, indoor_temp_c
        )
        
        # Calculate flow temperature
        flow_temp_c = self._get_flow_temperature(heating_system, 0.0)
        
        # Calculate COP for water source (similar to ground source)
        cop = self._calculate_water_source_cop(water_temp_c, flow_temp_c)
        
        # Calculate power consumption
        power_consumption_kw = heating_demand_kw / cop
        
        # Calculate annual energy consumption
        annual_heating_hours = 2000
        annual_consumption_kwh = power_consumption_kw * annual_heating_hours
        
        return {
            "heat_pump_type": HeatPumpType.WATER_SOURCE,
            "heating_demand_kw": heating_demand_kw,
            "cop": cop,
            "power_consumption_kw": power_consumption_kw,
            "flow_temperature_c": flow_temp_c,
            "annual_consumption_kwh": annual_consumption_kwh,
            "water_temperature_c": water_temp_c,
            "efficiency_percent": cop / 5.5 * 100
        }


    # ========== COP Calculations ==========
    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="COP calculation failed")
    def calculate_cop(
        self,
        heat_pump_type: HeatPumpType,
        outdoor_temp_c: float,
        indoor_temp_c: float,
        flow_temp_c: float,
        return_temp_c: float
    ) -> COPCalculation:
        """
        Calculate Coefficient of Performance
        
        Args:
            heat_pump_type: Type of heat pump
            outdoor_temp_c: Outdoor temperature
            indoor_temp_c: Indoor temperature
            flow_temp_c: Flow temperature
            return_temp_c: Return temperature
            
        Returns:
            COPCalculation with detailed COP analysis
        """
        # Calculate Carnot COP (theoretical maximum)
        t_hot_k = flow_temp_c + 273.15
        t_cold_k = outdoor_temp_c + 273.15
        carnot_cop = t_hot_k / (t_hot_k - t_cold_k)
        
        # Calculate actual COP based on heat pump type
        if heat_pump_type == HeatPumpType.AIR_SOURCE:
            cop_heating = self._calculate_air_source_cop(outdoor_temp_c, flow_temp_c)
        elif heat_pump_type == HeatPumpType.GROUND_SOURCE:
            cop_heating = self._calculate_ground_source_cop(outdoor_temp_c, flow_temp_c)
        elif heat_pump_type == HeatPumpType.WATER_SOURCE:
            cop_heating = self._calculate_water_source_cop(outdoor_temp_c, flow_temp_c)
        else:
            cop_heating = 3.5  # Default
        
        # Calculate cooling COP (if applicable)
        cop_cooling = cop_heating * 1.2  # Cooling is typically more efficient
        
        # Calculate seasonal COP (SCOP)
        scop_seasonal = cop_heating * 0.9  # Account for seasonal variations
        
        # Calculate efficiency relative to Carnot
        efficiency_percent = (cop_heating / carnot_cop) * 100
        
        # Estimate power consumption and heating output
        heating_output_kw = 10.0  # Example: 10 kW heating output
        power_consumption_kw = heating_output_kw / cop_heating
        
        return COPCalculation(
            cop_heating=cop_heating,
            cop_cooling=cop_cooling,
            scop_seasonal=scop_seasonal,
            outdoor_temp_c=outdoor_temp_c,
            indoor_temp_c=indoor_temp_c,
            flow_temp_c=flow_temp_c,
            return_temp_c=return_temp_c,
            efficiency_percent=efficiency_percent,
            power_consumption_kw=power_consumption_kw,
            heating_output_kw=heating_output_kw
        )
    
    # ========== Dynamic Tariff Optimization ==========
    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="Dynamic tariff optimization failed")
    def optimize_dynamic_tariff(
        self,
        annual_heating_demand_kwh: float,
        tariff_type: TariffType,
        hourly_tariffs_eur_kwh: List[float],  # 24 hours
        thermal_storage_capacity_kwh: float = 0.0,
        outdoor_temp_profile: Optional[List[float]] = None
    ) -> DynamicTariffOptimization:
        """
        Optimize heat pump operation for dynamic electricity tariffs
        
        Args:
            annual_heating_demand_kwh: Annual heating demand
            tariff_type: Type of electricity tariff
            hourly_tariffs_eur_kwh: Hourly tariff rates for 24 hours
            thermal_storage_capacity_kwh: Thermal storage capacity
            outdoor_temp_profile: Hourly outdoor temperature profile
            
        Returns:
            DynamicTariffOptimization with optimal operation schedule
        """
        if outdoor_temp_profile is None:
            outdoor_temp_profile = [5.0] * 24  # Default winter profile
        
        # Calculate hourly heating demand
        daily_demand_kwh = annual_heating_demand_kwh / 365
        hourly_demand_kwh = [daily_demand_kwh / 24] * 24
        
        # Find optimal heating hours (lowest tariff periods)
        tariff_hours = [(i, tariff) for i, tariff in enumerate(hourly_tariffs_eur_kwh)]
        sorted_hours = sorted(tariff_hours, key=lambda x: x[1])
        
        # Determine optimal heating schedule
        optimal_schedule = []
        peak_avoidance_hours = []
        optimal_heating_hours = []
        
        for hour in range(24):
            tariff = hourly_tariffs_eur_kwh[hour]
            demand = hourly_demand_kwh[hour]
            
            # Determine if this is a good hour to heat
            is_low_tariff = tariff < np.mean(hourly_tariffs_eur_kwh)
            is_peak_hour = tariff > np.percentile(hourly_tariffs_eur_kwh, 75)
            
            if is_peak_hour:
                peak_avoidance_hours.append(hour)
                # Use stored heat during peak hours
                heating_power_kw = 0.0 if thermal_storage_capacity_kwh > 0 else demand
            elif is_low_tariff:
                optimal_heating_hours.append(hour)
                # Heat more during low tariff hours
                heating_power_kw = demand * 1.5 if thermal_storage_capacity_kwh > 0 else demand
            else:
                heating_power_kw = demand
            
            optimal_schedule.append({
                "hour": hour,
                "tariff_eur_kwh": tariff,
                "heating_power_kw": heating_power_kw,
                "demand_kwh": demand,
                "is_optimal": is_low_tariff,
                "is_peak": is_peak_hour
            })
        
        # Calculate annual cost with optimization
        annual_cost_eur = sum(
            schedule["heating_power_kw"] * schedule["tariff_eur_kwh"]
            for schedule in optimal_schedule
        ) * 365
        
        # Calculate cost without optimization (flat operation)
        flat_cost_eur = daily_demand_kwh * np.mean(hourly_tariffs_eur_kwh) * 365
        cost_savings_percent = (flat_cost_eur - annual_cost_eur) / flat_cost_eur * 100
        
        # Calculate storage utilization
        storage_utilization_percent = min(100.0, thermal_storage_capacity_kwh / daily_demand_kwh * 100)
        
        # Calculate grid-friendly score
        grid_friendly_score = (
            len(optimal_heating_hours) / 24 * 50 +  # Spread of heating hours
            storage_utilization_percent * 0.3 +  # Storage usage
            cost_savings_percent * 0.2  # Cost optimization
        )
        
        return DynamicTariffOptimization(
            optimal_schedule=optimal_schedule,
            annual_cost_eur=annual_cost_eur,
            cost_savings_percent=cost_savings_percent,
            peak_avoidance_hours=peak_avoidance_hours,
            optimal_heating_hours=optimal_heating_hours,
            storage_utilization_percent=storage_utilization_percent,
            grid_friendly_score=min(100.0, grid_friendly_score)
        )


    # ========== Heating Cost Comparison ==========
    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="Heating cost comparison failed")
    def compare_heating_costs(
        self,
        annual_heating_demand_kwh: float,
        heat_pump_cop: float,
        electricity_price_eur_kwh: float,
        gas_price_eur_kwh: float,
        oil_price_eur_l: float,
        heat_pump_investment_eur: float
    ) -> HeatingCostComparison:
        """
        Compare heating costs across different systems
        
        Args:
            annual_heating_demand_kwh: Annual heating demand
            heat_pump_cop: Heat pump COP
            electricity_price_eur_kwh: Electricity price
            gas_price_eur_kwh: Gas price
            oil_price_eur_l: Oil price per liter
            heat_pump_investment_eur: Heat pump investment cost
            
        Returns:
            HeatingCostComparison with cost comparison
        """
        # Calculate heat pump annual cost
        hp_electricity_consumption_kwh = annual_heating_demand_kwh / heat_pump_cop
        heat_pump_annual_cost_eur = hp_electricity_consumption_kwh * electricity_price_eur_kwh
        
        # Calculate gas heating cost (90% efficiency)
        gas_consumption_kwh = annual_heating_demand_kwh / 0.90
        gas_annual_cost_eur = gas_consumption_kwh * gas_price_eur_kwh
        
        # Calculate oil heating cost (85% efficiency, 10 kWh per liter)
        oil_consumption_l = annual_heating_demand_kwh / 0.85 / 10.0
        oil_annual_cost_eur = oil_consumption_l * oil_price_eur_l
        
        # Calculate electric heating cost (100% efficiency)
        electric_annual_cost_eur = annual_heating_demand_kwh * electricity_price_eur_kwh
        
        # Calculate savings
        savings_vs_gas_eur = gas_annual_cost_eur - heat_pump_annual_cost_eur
        savings_vs_oil_eur = oil_annual_cost_eur - heat_pump_annual_cost_eur
        savings_vs_electric_eur = electric_annual_cost_eur - heat_pump_annual_cost_eur
        
        # Calculate payback period (vs gas)
        payback_period_years = heat_pump_investment_eur / savings_vs_gas_eur if savings_vs_gas_eur > 0 else 999
        
        # Calculate 25-year ROI
        roi_25years_eur = savings_vs_gas_eur * 25 - heat_pump_investment_eur
        
        return HeatingCostComparison(
            heat_pump_annual_cost_eur=heat_pump_annual_cost_eur,
            gas_annual_cost_eur=gas_annual_cost_eur,
            oil_annual_cost_eur=oil_annual_cost_eur,
            electric_annual_cost_eur=electric_annual_cost_eur,
            savings_vs_gas_eur=savings_vs_gas_eur,
            savings_vs_oil_eur=savings_vs_oil_eur,
            savings_vs_electric_eur=savings_vs_electric_eur,
            payback_period_years=payback_period_years,
            roi_25years_eur=roi_25years_eur
        )
    
    # ========== Seasonal Performance Analysis ==========
    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="Seasonal performance analysis failed")
    def analyze_seasonal_performance(
        self,
        heat_pump_type: HeatPumpType,
        latitude: float,
        building_area_m2: float,
        insulation_quality: str,
        heating_system: HeatingSystem
    ) -> SeasonalPerformance:
        """
        Analyze seasonal heat pump performance
        
        Args:
            heat_pump_type: Type of heat pump
            latitude: Location latitude
            building_area_m2: Building area
            insulation_quality: Insulation quality
            heating_system: Heating system type
            
        Returns:
            SeasonalPerformance with seasonal analysis
        """
        # Define seasonal average temperatures
        seasonal_temps = {
            "winter": -2.0 + (50 - abs(latitude)) * 0.3,
            "spring": 10.0 + (50 - abs(latitude)) * 0.2,
            "summer": 20.0 + (50 - abs(latitude)) * 0.1,
            "autumn": 8.0 + (50 - abs(latitude)) * 0.2
        }
        
        # Calculate monthly temperatures
        monthly_temps = [
            seasonal_temps["winter"],  # Jan
            seasonal_temps["winter"],  # Feb
            seasonal_temps["spring"],  # Mar
            seasonal_temps["spring"],  # Apr
            seasonal_temps["spring"],  # May
            seasonal_temps["summer"],  # Jun
            seasonal_temps["summer"],  # Jul
            seasonal_temps["summer"],  # Aug
            seasonal_temps["autumn"],  # Sep
            seasonal_temps["autumn"],  # Oct
            seasonal_temps["autumn"],  # Nov
            seasonal_temps["winter"]   # Dec
        ]
        
        # Calculate monthly COP and consumption
        monthly_cop = []
        monthly_consumption_kwh = []
        monthly_heating_demand_kwh = []
        
        for month, temp in enumerate(monthly_temps):
            # Calculate flow temperature
            flow_temp = self._get_flow_temperature(heating_system, temp)
            
            # Calculate COP for this month
            if heat_pump_type == HeatPumpType.AIR_SOURCE:
                cop = self._calculate_air_source_cop(temp, flow_temp)
            elif heat_pump_type == HeatPumpType.GROUND_SOURCE:
                cop = self._calculate_ground_source_cop(10.0, flow_temp)  # Stable ground temp
            else:
                cop = self._calculate_water_source_cop(10.0, flow_temp)
            
            monthly_cop.append(cop)
            
            # Calculate heating demand for this month
            if temp < 15:  # Heating needed
                heating_demand = self._calculate_heating_demand(
                    building_area_m2, insulation_quality, temp, 20.0
                )
                # Estimate hours of heating needed
                days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]
                heating_hours = days_in_month * 24 * max(0, (15 - temp) / 20)
                month_demand_kwh = heating_demand * heating_hours
            else:
                month_demand_kwh = 0.0
            
            monthly_heating_demand_kwh.append(month_demand_kwh)
            monthly_consumption_kwh.append(month_demand_kwh / cop if cop > 0 else 0)
        
        # Calculate seasonal averages
        winter_cop = np.mean([monthly_cop[i] for i in [0, 1, 11]])
        spring_cop = np.mean([monthly_cop[i] for i in [2, 3, 4]])
        summer_cop = np.mean([monthly_cop[i] for i in [5, 6, 7]])
        autumn_cop = np.mean([monthly_cop[i] for i in [8, 9, 10]])
        
        # Calculate annual average COP (weighted by heating demand)
        total_demand = sum(monthly_heating_demand_kwh)
        if total_demand > 0:
            annual_average_cop = sum(
                monthly_heating_demand_kwh[i] / monthly_consumption_kwh[i] 
                if monthly_consumption_kwh[i] > 0 else 0
                for i in range(12)
            ) / 12
        else:
            annual_average_cop = np.mean(monthly_cop)
        
        # Calculate efficiency variation
        efficiency_variation_percent = (max(monthly_cop) - min(monthly_cop)) / np.mean(monthly_cop) * 100
        
        return SeasonalPerformance(
            winter_cop=winter_cop,
            spring_cop=spring_cop,
            summer_cop=summer_cop,
            autumn_cop=autumn_cop,
            annual_average_cop=annual_average_cop,
            monthly_cop=monthly_cop,
            monthly_consumption_kwh=monthly_consumption_kwh,
            monthly_heating_demand_kwh=monthly_heating_demand_kwh,
            efficiency_variation_percent=efficiency_variation_percent
        )


    # ========== Combined PV + Heat Pump Optimization ==========
    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="PV + heat pump optimization failed")
    def optimize_pv_heatpump_combination(
        self,
        pv_system_size_kwp: float,
        annual_pv_production_kwh: float,
        heat_pump_capacity_kw: float,
        annual_hp_consumption_kwh: float,
        annual_household_consumption_kwh: float,
        electricity_price_eur_kwh: float,
        feed_in_tariff_eur_kwh: float
    ) -> PVHeatPumpOptimization:
        """
        Optimize combined PV + heat pump system
        
        Args:
            pv_system_size_kwp: PV system size
            annual_pv_production_kwh: Annual PV production
            heat_pump_capacity_kw: Heat pump capacity
            annual_hp_consumption_kwh: Annual heat pump consumption
            annual_household_consumption_kwh: Annual household consumption
            electricity_price_eur_kwh: Electricity price
            feed_in_tariff_eur_kwh: Feed-in tariff
            
        Returns:
            PVHeatPumpOptimization with optimization results
        """
        # Calculate total consumption
        total_consumption_kwh = annual_hp_consumption_kwh + annual_household_consumption_kwh
        
        # Estimate self-consumption (simplified model)
        # Assume 30% direct self-consumption, 20% additional with heat pump load shifting
        base_self_consumption_rate = 0.30
        hp_load_shifting_bonus = 0.20
        self_consumption_rate = min(0.90, base_self_consumption_rate + hp_load_shifting_bonus)
        
        self_consumption_kwh = min(annual_pv_production_kwh, total_consumption_kwh) * self_consumption_rate
        
        # Calculate grid import/export
        grid_import_kwh = max(0, total_consumption_kwh - self_consumption_kwh)
        grid_export_kwh = max(0, annual_pv_production_kwh - self_consumption_kwh)
        
        # Calculate autarky rate
        autarky_rate_percent = (self_consumption_kwh / total_consumption_kwh * 100) if total_consumption_kwh > 0 else 0
        
        # Calculate savings
        # Savings from self-consumed PV
        pv_self_consumption_savings = self_consumption_kwh * electricity_price_eur_kwh
        # Revenue from grid feed-in
        feed_in_revenue = grid_export_kwh * feed_in_tariff_eur_kwh
        # Cost of grid import
        grid_import_cost = grid_import_kwh * electricity_price_eur_kwh
        
        # Combined savings (vs. no PV)
        without_pv_cost = total_consumption_kwh * electricity_price_eur_kwh
        with_pv_cost = grid_import_cost - feed_in_revenue
        combined_savings_eur = without_pv_cost - with_pv_cost
        
        # Calculate synergy benefit (additional savings from load shifting)
        base_self_consumption_savings = annual_pv_production_kwh * base_self_consumption_rate * electricity_price_eur_kwh
        synergy_benefit_eur = pv_self_consumption_savings - base_self_consumption_savings
        
        # Generate optimal operation schedule (simplified 24h profile)
        optimal_schedule = []
        for hour in range(24):
            # PV production profile (bell curve)
            pv_production_factor = max(0, math.sin((hour - 6) * math.pi / 12))
            hourly_pv_kwh = annual_pv_production_kwh / 365 / 24 * pv_production_factor * 3
            
            # Heat pump consumption (shift to PV production hours)
            if 10 <= hour <= 16:  # Peak PV hours
                hp_consumption_factor = 1.5
            elif 6 <= hour <= 9 or 17 <= hour <= 20:
                hp_consumption_factor = 0.8
            else:
                hp_consumption_factor = 0.3
            
            hourly_hp_kwh = annual_hp_consumption_kwh / 365 / 24 * hp_consumption_factor
            
            optimal_schedule.append({
                "hour": hour,
                "pv_production_kwh": hourly_pv_kwh,
                "hp_consumption_kwh": hourly_hp_kwh,
                "self_consumption_kwh": min(hourly_pv_kwh, hourly_hp_kwh),
                "grid_import_kwh": max(0, hourly_hp_kwh - hourly_pv_kwh),
                "grid_export_kwh": max(0, hourly_pv_kwh - hourly_hp_kwh)
            })
        
        return PVHeatPumpOptimization(
            pv_system_size_kwp=pv_system_size_kwp,
            heat_pump_capacity_kw=heat_pump_capacity_kw,
            annual_pv_production_kwh=annual_pv_production_kwh,
            annual_hp_consumption_kwh=annual_hp_consumption_kwh,
            self_consumption_rate_percent=self_consumption_rate * 100,
            autarky_rate_percent=autarky_rate_percent,
            grid_import_kwh=grid_import_kwh,
            grid_export_kwh=grid_export_kwh,
            combined_savings_eur=combined_savings_eur,
            synergy_benefit_eur=synergy_benefit_eur,
            optimal_operation_schedule=optimal_schedule
        )
    
    # ========== Smart Grid Integration ==========
    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="Smart grid integration analysis failed")
    def analyze_smart_grid_integration(
        self,
        heat_pump_capacity_kw: float,
        thermal_storage_capacity_kwh: float,
        annual_consumption_kwh: float,
        grid_signal_response_time_min: float = 15.0
    ) -> SmartGridIntegration:
        """
        Analyze smart grid integration potential
        
        Args:
            heat_pump_capacity_kw: Heat pump capacity
            thermal_storage_capacity_kwh: Thermal storage capacity
            annual_consumption_kwh: Annual consumption
            grid_signal_response_time_min: Response time to grid signals
            
        Returns:
            SmartGridIntegration with grid integration analysis
        """
        # Calculate demand response potential
        # Heat pump can be turned off for short periods using thermal storage
        demand_response_potential_kw = heat_pump_capacity_kw * 0.8  # 80% of capacity
        
        # Calculate load shifting capacity
        # Based on thermal storage
        load_shifting_capacity_kwh = thermal_storage_capacity_kwh * 0.7  # 70% usable
        
        # Calculate grid stabilization score
        # Based on flexibility and response time
        response_score = max(0, 100 - grid_signal_response_time_min * 2)
        flexibility_score = min(100, load_shifting_capacity_kwh / (annual_consumption_kwh / 365) * 100)
        grid_stabilization_score = (response_score + flexibility_score) / 2
        
        # Calculate peak shaving contribution
        # Heat pump can reduce peak load by shifting consumption
        peak_shaving_contribution_kw = heat_pump_capacity_kw * 0.6
        
        # Calculate renewable integration score
        # Heat pump can absorb excess renewable energy
        renewable_integration_score = min(100, thermal_storage_capacity_kwh / heat_pump_capacity_kw * 10)
        
        # Estimate flexibility value (revenue from grid services)
        # Based on demand response and load shifting
        flexibility_value_eur_year = (
            demand_response_potential_kw * 50 +  # €50 per kW DR capacity
            load_shifting_capacity_kwh * 20  # €20 per kWh shifting capacity
        )
        
        # Estimate grid services revenue
        # From frequency regulation, peak shaving, etc.
        grid_services_revenue_eur_year = flexibility_value_eur_year * 0.3
        
        return SmartGridIntegration(
            demand_response_potential_kw=demand_response_potential_kw,
            load_shifting_capacity_kwh=load_shifting_capacity_kwh,
            grid_stabilization_score=grid_stabilization_score,
            peak_shaving_contribution_kw=peak_shaving_contribution_kw,
            renewable_integration_score=renewable_integration_score,
            flexibility_value_eur_year=flexibility_value_eur_year,
            grid_services_revenue_eur_year=grid_services_revenue_eur_year
        )


    # ========== Environmental Impact Analysis ==========
    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="Environmental impact analysis failed")
    def analyze_environmental_impact(
        self,
        annual_heating_demand_kwh: float,
        heat_pump_cop: float,
        electricity_co2_g_kwh: float = 400.0,  # Grid electricity CO2 intensity
        gas_co2_g_kwh: float = 200.0,
        oil_co2_g_kwh: float = 266.0,
        renewable_energy_percent: float = 0.0,
        lifetime_years: int = 25,
        building_area_m2: float = 150.0,
        heat_pump_type: HeatPumpType = HeatPumpType.AIR_SOURCE
    ) -> EnvironmentalImpact:
        """
        Comprehensive environmental impact analysis of heat pump
        
        Args:
            annual_heating_demand_kwh: Annual heating demand
            heat_pump_cop: Heat pump COP
            electricity_co2_g_kwh: CO2 intensity of grid electricity
            gas_co2_g_kwh: CO2 intensity of gas
            oil_co2_g_kwh: CO2 intensity of oil
            renewable_energy_percent: Percentage of renewable energy in grid
            lifetime_years: System lifetime for analysis
            building_area_m2: Building area for calculations
            heat_pump_type: Type of heat pump
            
        Returns:
            EnvironmentalImpact with comprehensive environmental analysis
        """
        # Calculate heat pump electricity consumption
        hp_electricity_kwh = annual_heating_demand_kwh / heat_pump_cop
        
        # Calculate CO2 emissions for heat pump
        # Adjust for renewable energy
        effective_co2_g_kwh = electricity_co2_g_kwh * (1 - renewable_energy_percent / 100)
        hp_co2_kg = hp_electricity_kwh * effective_co2_g_kwh / 1000
        
        # Calculate CO2 emissions for gas heating (90% efficiency)
        gas_consumption_kwh = annual_heating_demand_kwh / 0.90
        gas_co2_kg = gas_consumption_kwh * gas_co2_g_kwh / 1000
        
        # Calculate CO2 emissions for oil heating (85% efficiency)
        oil_consumption_kwh = annual_heating_demand_kwh / 0.85
        oil_co2_kg = oil_consumption_kwh * oil_co2_g_kwh / 1000
        
        # Calculate savings
        co2_savings_vs_gas_kg = gas_co2_kg - hp_co2_kg
        co2_savings_vs_oil_kg = oil_co2_kg - hp_co2_kg
        annual_co2_savings_kg = max(co2_savings_vs_gas_kg, co2_savings_vs_oil_kg)
        
        # Calculate lifetime CO2 savings (25 years)
        # Account for grid decarbonization (assume 2% improvement per year)
        lifetime_co2_savings_kg = 0.0
        for year in range(lifetime_years):
            year_grid_co2 = electricity_co2_g_kwh * (0.98 ** year)
            year_effective_co2 = year_grid_co2 * (1 - renewable_energy_percent / 100)
            year_hp_co2 = hp_electricity_kwh * year_effective_co2 / 1000
            year_gas_co2 = gas_consumption_kwh * gas_co2_g_kwh / 1000
            lifetime_co2_savings_kg += (year_gas_co2 - year_hp_co2)
        
        # Calculate carbon footprint per year
        carbon_footprint_kg_year = hp_co2_kg
        
        # Create carbon footprint tracking (yearly)
        carbon_footprint_tracking = []
        cumulative_savings = 0.0
        for year in range(1, min(lifetime_years + 1, 26)):
            year_grid_co2 = electricity_co2_g_kwh * (0.98 ** (year - 1))
            year_effective_co2 = year_grid_co2 * (1 - renewable_energy_percent / 100)
            year_hp_co2 = hp_electricity_kwh * year_effective_co2 / 1000
            year_gas_co2 = gas_consumption_kwh * gas_co2_g_kwh / 1000
            year_savings = year_gas_co2 - year_hp_co2
            cumulative_savings += year_savings
            
            carbon_footprint_tracking.append({
                "year": year,
                "hp_emissions_kg": round(year_hp_co2, 2),
                "gas_emissions_kg": round(year_gas_co2, 2),
                "annual_savings_kg": round(year_savings, 2),
                "cumulative_savings_kg": round(cumulative_savings, 2),
                "grid_co2_intensity_g_kwh": round(year_grid_co2, 2)
            })
        
        # Calculate primary energy factor
        # Heat pump: electricity * 1.8 (primary energy factor) / COP
        # Gas: direct consumption * 1.1
        hp_primary_energy = hp_electricity_kwh * 1.8
        gas_primary_energy = gas_consumption_kwh * 1.1
        primary_energy_factor = hp_primary_energy / gas_primary_energy if gas_primary_energy > 0 else 1.0
        
        # Calculate environmental score (0-100)
        # Based on CO2 savings, renewable energy, and efficiency
        co2_reduction_score = min(100, co2_savings_vs_gas_kg / gas_co2_kg * 100) if gas_co2_kg > 0 else 0
        renewable_score = renewable_energy_percent
        efficiency_score = min(100, heat_pump_cop / 5.0 * 100)
        environmental_score = (
            co2_reduction_score * 0.5 + 
            renewable_score * 0.3 + 
            efficiency_score * 0.2
        )
        
        # Calculate carbon footprint reduction
        carbon_footprint_reduction_percent = (co2_savings_vs_gas_kg / gas_co2_kg * 100) if gas_co2_kg > 0 else 0
        
        # Calculate equivalent trees planted
        # One tree absorbs ~20 kg CO2 per year
        equivalent_trees_planted = int(annual_co2_savings_kg / 20)
        
        # Determine sustainability rating (A+ to F)
        sustainability_rating = self._calculate_sustainability_rating(
            environmental_score, 
            carbon_footprint_reduction_percent,
            renewable_energy_percent
        )
        
        # Determine environmental certifications
        environmental_certifications = self._determine_certifications(
            heat_pump_cop,
            renewable_energy_percent,
            carbon_footprint_reduction_percent,
            heat_pump_type
        )
        
        # Calculate renewable energy contribution
        renewable_energy_contribution_kwh = hp_electricity_kwh * renewable_energy_percent / 100
        
        # Calculate fossil fuel replacement
        fossil_fuel_replacement_percent = (gas_consumption_kwh / (gas_consumption_kwh + hp_electricity_kwh) * 100) if (gas_consumption_kwh + hp_electricity_kwh) > 0 else 0
        
        # Calculate air quality improvement score
        # Based on reduction of local combustion emissions
        air_quality_improvement_score = self._calculate_air_quality_score(
            co2_savings_vs_gas_kg,
            building_area_m2
        )
        
        # Calculate water conservation (heat pumps use less water than conventional systems)
        # Gas boilers use water for combustion and condensation
        water_conservation_liters_year = annual_heating_demand_kwh * 0.5  # Approximate
        
        # Calculate noise pollution reduction
        # Modern heat pumps are quieter than old heating systems
        noise_pollution_reduction_db = self._calculate_noise_reduction(heat_pump_type)
        
        return EnvironmentalImpact(
            annual_co2_savings_kg=annual_co2_savings_kg,
            co2_savings_vs_gas_kg=co2_savings_vs_gas_kg,
            co2_savings_vs_oil_kg=co2_savings_vs_oil_kg,
            renewable_energy_percent=renewable_energy_percent,
            primary_energy_factor=primary_energy_factor,
            environmental_score=environmental_score,
            carbon_footprint_reduction_percent=carbon_footprint_reduction_percent,
            equivalent_trees_planted=equivalent_trees_planted,
            lifetime_co2_savings_kg=lifetime_co2_savings_kg,
            carbon_footprint_kg_year=carbon_footprint_kg_year,
            carbon_footprint_tracking=carbon_footprint_tracking,
            sustainability_rating=sustainability_rating,
            environmental_certifications=environmental_certifications,
            renewable_energy_contribution_kwh=renewable_energy_contribution_kwh,
            fossil_fuel_replacement_percent=fossil_fuel_replacement_percent,
            air_quality_improvement_score=air_quality_improvement_score,
            water_conservation_liters_year=water_conservation_liters_year,
            noise_pollution_reduction_db=noise_pollution_reduction_db
        )
    
    def _calculate_sustainability_rating(
        self,
        environmental_score: float,
        carbon_reduction_percent: float,
        renewable_percent: float
    ) -> str:
        """Calculate sustainability rating (A+ to F)"""
        # Weighted score
        total_score = (
            environmental_score * 0.5 +
            carbon_reduction_percent * 0.3 +
            renewable_percent * 0.2
        )
        
        if total_score >= 90:
            return "A+"
        elif total_score >= 80:
            return "A"
        elif total_score >= 70:
            return "B"
        elif total_score >= 60:
            return "C"
        elif total_score >= 50:
            return "D"
        elif total_score >= 40:
            return "E"
        else:
            return "F"
    
    def _determine_certifications(
        self,
        cop: float,
        renewable_percent: float,
        carbon_reduction_percent: float,
        heat_pump_type: HeatPumpType
    ) -> List[str]:
        """Determine applicable environmental certifications"""
        certifications = []
        
        # Energy efficiency certifications
        if cop >= 4.5:
            certifications.append("Energy Star Certified")
            certifications.append("EU Energy Label A+++")
        elif cop >= 4.0:
            certifications.append("EU Energy Label A++")
        elif cop >= 3.5:
            certifications.append("EU Energy Label A+")
        
        # Renewable energy certifications
        if renewable_percent >= 80:
            certifications.append("100% Renewable Ready")
        elif renewable_percent >= 50:
            certifications.append("Renewable Energy Compatible")
        
        # Carbon reduction certifications
        if carbon_reduction_percent >= 70:
            certifications.append("Carbon Neutral Certified")
        elif carbon_reduction_percent >= 50:
            certifications.append("Low Carbon Technology")
        
        # Heat pump specific certifications
        if heat_pump_type == HeatPumpType.GROUND_SOURCE:
            certifications.append("Geothermal Certified")
        
        # Environmental management
        certifications.append("ISO 14001 Compatible")
        
        # Refrigerant certifications
        certifications.append("F-Gas Compliant")
        certifications.append("Low GWP Refrigerant")
        
        return certifications
    
    def _calculate_air_quality_score(
        self,
        co2_savings_kg: float,
        building_area_m2: float
    ) -> float:
        """Calculate air quality improvement score (0-100)"""
        # Air quality improves by eliminating local combustion
        # Score based on CO2 savings per m2
        co2_per_m2 = co2_savings_kg / building_area_m2 if building_area_m2 > 0 else 0
        
        # Normalize to 0-100 scale
        # Assume 50 kg CO2/m2/year is excellent
        score = min(100, co2_per_m2 / 50 * 100)
        
        return score
    
    def _calculate_noise_reduction(self, heat_pump_type: HeatPumpType) -> float:
        """Calculate noise pollution reduction in dB"""
        # Compared to old oil/gas boilers
        if heat_pump_type == HeatPumpType.GROUND_SOURCE:
            return 15.0  # Very quiet, indoor unit only
        elif heat_pump_type == HeatPumpType.WATER_SOURCE:
            return 12.0  # Quiet, indoor unit only
        elif heat_pump_type == HeatPumpType.AIR_SOURCE:
            return 8.0  # Outdoor unit, but modern and quiet
        else:
            return 10.0  # Default
    
    @log_service_call(service_name="heatpump_advanced", log_timing=True)
    @handle_service_errors(service_name="heatpump_advanced", error_message="Sustainability report generation failed")
    def generate_sustainability_report(
        self,
        environmental_impact: EnvironmentalImpact,
        system_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive sustainability report
        
        Args:
            environmental_impact: Environmental impact analysis results
            system_details: Heat pump system details
            
        Returns:
            Dictionary with sustainability report
        """
        report = {
            "executive_summary": {
                "sustainability_rating": environmental_impact.sustainability_rating,
                "environmental_score": round(environmental_impact.environmental_score, 1),
                "annual_co2_savings_tons": round(environmental_impact.annual_co2_savings_kg / 1000, 2),
                "lifetime_co2_savings_tons": round(environmental_impact.lifetime_co2_savings_kg / 1000, 2),
                "equivalent_trees": environmental_impact.equivalent_trees_planted
            },
            "carbon_footprint": {
                "annual_footprint_kg": round(environmental_impact.carbon_footprint_kg_year, 2),
                "reduction_vs_gas_percent": round(environmental_impact.carbon_footprint_reduction_percent, 1),
                "tracking": environmental_impact.carbon_footprint_tracking
            },
            "renewable_energy": {
                "grid_renewable_percent": environmental_impact.renewable_energy_percent,
                "renewable_contribution_kwh": round(environmental_impact.renewable_energy_contribution_kwh, 0),
                "fossil_fuel_replacement_percent": round(environmental_impact.fossil_fuel_replacement_percent, 1)
            },
            "environmental_benefits": {
                "air_quality_score": round(environmental_impact.air_quality_improvement_score, 1),
                "water_conservation_liters": round(environmental_impact.water_conservation_liters_year, 0),
                "noise_reduction_db": environmental_impact.noise_pollution_reduction_db,
                "primary_energy_factor": round(environmental_impact.primary_energy_factor, 2)
            },
            "certifications": environmental_impact.environmental_certifications,
            "system_details": system_details,
            "recommendations": self._generate_recommendations(environmental_impact)
        }
        
        return report
    
    def _generate_recommendations(self, impact: EnvironmentalImpact) -> List[str]:
        """Generate recommendations for improving environmental performance"""
        recommendations = []
        
        if impact.renewable_energy_percent < 50:
            recommendations.append(
                "Consider switching to a green electricity tariff to increase renewable energy usage"
            )
        
        if impact.environmental_score < 70:
            recommendations.append(
                "Improve building insulation to reduce heating demand and environmental impact"
            )
        
        if impact.carbon_footprint_reduction_percent < 50:
            recommendations.append(
                "Consider combining with solar PV system for maximum carbon reduction"
            )
        
        if impact.sustainability_rating in ["D", "E", "F"]:
            recommendations.append(
                "Upgrade to a more efficient heat pump model to improve sustainability rating"
            )
        
        recommendations.append(
            "Regular maintenance ensures optimal efficiency and environmental performance"
        )
        
        recommendations.append(
            "Monitor and optimize operation schedule to maximize renewable energy usage"
        )
        
        return recommendations
    
    # ========== Helper Methods ==========
    
    def _calculate_heating_demand(
        self,
        building_area_m2: float,
        insulation_quality: str,
        outdoor_temp_c: float,
        indoor_temp_c: float
    ) -> float:
        """Calculate heating demand in kW"""
        # Heat loss coefficient based on insulation quality
        u_values = {
            "poor": 1.5,      # W/m²K
            "average": 1.0,
            "good": 0.6,
            "excellent": 0.3
        }
        u_value = u_values.get(insulation_quality, 1.0)
        
        # Calculate heat loss
        temp_difference = indoor_temp_c - outdoor_temp_c
        heat_loss_w = building_area_m2 * u_value * temp_difference
        
        return heat_loss_w / 1000  # Convert to kW
    
    def _get_flow_temperature(self, heating_system: HeatingSystem, outdoor_temp_c: float) -> float:
        """Get flow temperature based on heating system"""
        if heating_system == HeatingSystem.UNDERFLOOR:
            # Underfloor heating: 35-45°C
            return 35 + max(0, (10 - outdoor_temp_c) * 0.5)
        elif heating_system == HeatingSystem.FAN_COIL:
            # Fan coil: 40-50°C
            return 40 + max(0, (10 - outdoor_temp_c) * 0.6)
        elif heating_system == HeatingSystem.RADIATORS:
            # Radiators: 50-70°C
            return 50 + max(0, (10 - outdoor_temp_c) * 1.0)
        else:  # MIXED
            return 45 + max(0, (10 - outdoor_temp_c) * 0.7)
    
    def _calculate_air_source_cop(self, outdoor_temp_c: float, flow_temp_c: float) -> float:
        """Calculate COP for air source heat pump"""
        # Simplified COP calculation based on temperature difference
        temp_diff = flow_temp_c - outdoor_temp_c
        
        # Base COP at standard conditions (A7/W35)
        base_cop = 4.0
        
        # Adjust for temperature difference
        # COP decreases with larger temperature difference
        cop = base_cop * (1 - (temp_diff - 28) * 0.015)
        
        return max(2.0, min(5.0, cop))
    
    def _calculate_ground_source_cop(self, ground_temp_c: float, flow_temp_c: float) -> float:
        """Calculate COP for ground source heat pump"""
        # Ground source is more stable and efficient
        temp_diff = flow_temp_c - ground_temp_c
        
        base_cop = 4.5
        cop = base_cop * (1 - (temp_diff - 25) * 0.012)
        
        return max(3.0, min(5.5, cop))
    
    def _calculate_water_source_cop(self, water_temp_c: float, flow_temp_c: float) -> float:
        """Calculate COP for water source heat pump"""
        # Similar to ground source
        return self._calculate_ground_source_cop(water_temp_c, flow_temp_c)
    
    def _calculate_collector_area(self, heating_demand_kw: float, collector_type: str) -> float:
        """Calculate ground collector area needed"""
        if collector_type == "horizontal":
            # Horizontal collectors: 25-35 W/m²
            return heating_demand_kw * 1000 / 30
        else:  # vertical
            # Vertical collectors: 50-60 W/m (per meter depth)
            return heating_demand_kw * 1000 / 55
    
    def _estimate_annual_heating_hours(self, outdoor_temp_c: float) -> float:
        """Estimate annual heating hours based on climate"""
        # Simplified estimation
        if outdoor_temp_c < 0:
            return 2500
        elif outdoor_temp_c < 5:
            return 2200
        elif outdoor_temp_c < 10:
            return 1800
        else:
            return 1500


# Example usage
if __name__ == "__main__":
    service = HeatPumpAdvancedService()
    service.initialize()
    
    # Test air source heat pump calculation
    result = service.calculate_air_source_heat_pump(
        building_area_m2=150.0,
        insulation_quality="good",
        outdoor_temp_c=5.0,
        indoor_temp_c=20.0,
        heating_system=HeatingSystem.UNDERFLOOR
    )
    print("Air Source Heat Pump Result:")
    print(f"  Heating Demand: {result['heating_demand_kw']:.2f} kW")
    print(f"  COP: {result['cop']:.2f}")
    print(f"  Annual Consumption: {result['annual_consumption_kwh']:.0f} kWh")
    
    # Test COP calculation
    cop_result = service.calculate_cop(
        heat_pump_type=HeatPumpType.AIR_SOURCE,
        outdoor_temp_c=5.0,
        indoor_temp_c=20.0,
        flow_temp_c=40.0,
        return_temp_c=35.0
    )
    print(f"\nCOP Calculation:")
    print(f"  COP Heating: {cop_result.cop_heating:.2f}")
    print(f"  SCOP Seasonal: {cop_result.scop_seasonal:.2f}")
    print(f"  Efficiency: {cop_result.efficiency_percent:.1f}%")
