"""
Heat Pump Sizing Service

This service provides comprehensive heat pump sizing calculations including:
- Heat load calculations (DIN EN 12831)
- Building insulation analysis
- Climate-based sizing
- Backup heating calculations
- Oversizing/undersizing warnings
- Seasonal performance predictions
"""

import sys
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import math
from dataclasses import dataclass

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.base_service import BaseService, HealthCheckResult, ServiceStatus
from backend.core.error_wrapper import handle_service_errors
from backend.core.logging_decorator import log_service_call


class BuildingType(str, Enum):
    """Building types"""
    SINGLE_FAMILY = "single_family"
    MULTI_FAMILY = "multi_family"
    APARTMENT = "apartment"
    COMMERCIAL = "commercial"


class InsulationStandard(str, Enum):
    """Insulation standards"""
    OLD_BUILDING = "old_building"  # Before 1977
    STANDARD = "standard"  # 1977-2002
    ENEV_2009 = "enev_2009"  # EnEV 2009
    ENEV_2014 = "enev_2014"  # EnEV 2014
    KFW_55 = "kfw_55"  # KfW 55
    KFW_40 = "kfw_40"  # KfW 40
    PASSIVE_HOUSE = "passive_house"  # Passive house


class ClimateZone(str, Enum):
    """Climate zones (Germany)"""
    ZONE_1 = "zone_1"  # Coastal (mild)
    ZONE_2 = "zone_2"  # Lowlands
    ZONE_3 = "zone_3"  # Central Germany
    ZONE_4 = "zone_4"  # Mountains (cold)


@dataclass
class HeatLoadCalculation:
    """Heat load calculation results (DIN EN 12831)"""
    design_heat_load_kw: float
    transmission_heat_loss_kw: float
    ventilation_heat_loss_kw: float
    heat_gain_kw: float
    safety_margin_kw: float
    total_heat_load_kw: float
    specific_heat_load_w_m2: float
    calculation_method: str
    design_outdoor_temp_c: float
    design_indoor_temp_c: float


@dataclass
class InsulationAnalysis:
    """Building insulation analysis"""
    u_value_walls_w_m2k: float
    u_value_roof_w_m2k: float
    u_value_floor_w_m2k: float
    u_value_windows_w_m2k: float
    average_u_value_w_m2k: float
    insulation_quality_score: float  # 0-100
    improvement_potential_percent: float
    recommended_improvements: List[str]
    annual_heat_loss_kwh: float


@dataclass
class ClimateSizing:
    """Climate-based sizing results"""
    climate_zone: ClimateZone
    design_outdoor_temp_c: float
    average_winter_temp_c: float
    heating_degree_days: float
    bivalent_point_c: float  # Temperature where backup heating starts
    recommended_capacity_kw: float
    capacity_at_bivalent_kw: float
    monovalent_limit_c: float  # Lowest temp for heat pump alone
    sizing_factor: float


@dataclass
class BackupHeating:
    """Backup heating calculations"""
    backup_required: bool
    backup_type: str  # "electric", "gas", "none"
    backup_capacity_kw: float
    backup_activation_temp_c: float
    annual_backup_hours: float
    annual_backup_energy_kwh: float
    backup_cost_eur_year: float
    backup_percentage: float  # % of total heating


@dataclass
class SizingWarnings:
    """Oversizing/undersizing warnings"""
    is_oversized: bool
    is_undersized: bool
    oversizing_percent: float
    undersizing_percent: float
    warnings: List[str]
    recommendations: List[str]
    optimal_size_range_kw: Tuple[float, float]
    efficiency_impact_percent: float


@dataclass
class SeasonalPrediction:
    """Seasonal performance predictions"""
    winter_capacity_kw: float
    spring_capacity_kw: float
    summer_capacity_kw: float
    autumn_capacity_kw: float
    winter_cop: float
    spring_cop: float
    summer_cop: float
    autumn_cop: float
    annual_scop: float
    monthly_performance: List[Dict[str, float]]  # 12 months
    capacity_degradation_percent: float


class HeatPumpSizingService(BaseService):
    """
    Heat Pump Sizing Service
    
    Provides comprehensive sizing calculations for heat pumps including:
    - Heat load calculations according to DIN EN 12831
    - Building insulation analysis
    - Climate-based sizing
    - Backup heating requirements
    - Oversizing/undersizing warnings
    - Seasonal performance predictions
    """
    
    def __init__(self):
        super().__init__("heatpump_sizing")
        self._sizing_cache: Dict[str, Any] = {}
        
        # U-value standards (W/m²K)
        self.u_value_standards = {
            InsulationStandard.OLD_BUILDING: {
                "walls": 1.4, "roof": 1.2, "floor": 1.0, "windows": 3.0
            },
            InsulationStandard.STANDARD: {
                "walls": 0.9, "roof": 0.8, "floor": 0.7, "windows": 2.0
            },
            InsulationStandard.ENEV_2009: {
                "walls": 0.35, "roof": 0.24, "floor": 0.35, "windows": 1.3
            },
            InsulationStandard.ENEV_2014: {
                "walls": 0.28, "roof": 0.20, "floor": 0.28, "windows": 1.1
            },
            InsulationStandard.KFW_55: {
                "walls": 0.20, "roof": 0.14, "floor": 0.20, "windows": 0.9
            },
            InsulationStandard.KFW_40: {
                "walls": 0.15, "roof": 0.12, "floor": 0.15, "windows": 0.8
            },
            InsulationStandard.PASSIVE_HOUSE: {
                "walls": 0.10, "roof": 0.10, "floor": 0.10, "windows": 0.6
            }
        }
        
        # Design outdoor temperatures for German climate zones (°C)
        self.design_temps = {
            ClimateZone.ZONE_1: -10,  # Coastal
            ClimateZone.ZONE_2: -12,  # Lowlands
            ClimateZone.ZONE_3: -14,  # Central
            ClimateZone.ZONE_4: -16   # Mountains
        }
        
        # Heating degree days for German climate zones
        self.heating_degree_days = {
            ClimateZone.ZONE_1: 3000,
            ClimateZone.ZONE_2: 3300,
            ClimateZone.ZONE_3: 3600,
            ClimateZone.ZONE_4: 4000
        }
        
    def initialize(self) -> None:
        """Initialize the sizing service"""
        try:
            self._set_initialized(True)
            self.logger.info("Heat Pump Sizing Service initialized successfully")
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
                "sizing_cache_size": len(self._sizing_cache)
            }
        )

    # ========== Heat Load Calculations ==========
    
    @log_service_call(service_name="heatpump_sizing", log_timing=True)
    @handle_service_errors(service_name="heatpump_sizing", error_message="Heat load calculation failed")
    def calculate_heat_load(
        self,
        building_area_m2: float,
        building_volume_m3: float,
        building_type: BuildingType,
        insulation_standard: InsulationStandard,
        climate_zone: ClimateZone,
        indoor_temp_c: float = 20.0,
        air_change_rate_h: float = 0.5,
        window_area_m2: Optional[float] = None
    ) -> HeatLoadCalculation:
        """
        Calculate heat load according to DIN EN 12831
        
        Args:
            building_area_m2: Heated building area
            building_volume_m3: Building volume
            building_type: Type of building
            insulation_standard: Insulation standard
            climate_zone: Climate zone
            indoor_temp_c: Design indoor temperature
            air_change_rate_h: Air changes per hour
            window_area_m2: Window area (optional, estimated if not provided)
            
        Returns:
            HeatLoadCalculation with detailed heat load analysis
        """
        # Get design outdoor temperature
        design_outdoor_temp_c = self.design_temps[climate_zone]
        temp_difference = indoor_temp_c - design_outdoor_temp_c
        
        # Get U-values for insulation standard
        u_values = self.u_value_standards[insulation_standard]
        
        # Estimate window area if not provided (typically 15-20% of floor area)
        if window_area_m2 is None:
            window_area_m2 = building_area_m2 * 0.17
        
        # Estimate surface areas
        # Assuming 2.5m ceiling height for area calculation
        wall_area_m2 = (building_volume_m3 / 2.5) * 0.6 - window_area_m2  # 60% of envelope is walls
        roof_area_m2 = building_area_m2
        floor_area_m2 = building_area_m2
        
        # Calculate transmission heat loss (Q_T)
        transmission_loss_walls = wall_area_m2 * u_values["walls"] * temp_difference
        transmission_loss_roof = roof_area_m2 * u_values["roof"] * temp_difference
        transmission_loss_floor = floor_area_m2 * u_values["floor"] * temp_difference * 0.5  # Ground contact factor
        transmission_loss_windows = window_area_m2 * u_values["windows"] * temp_difference
        
        transmission_heat_loss_kw = (
            transmission_loss_walls +
            transmission_loss_roof +
            transmission_loss_floor +
            transmission_loss_windows
        ) / 1000  # Convert W to kW
        
        # Calculate ventilation heat loss (Q_V)
        # Q_V = V * n * ρ * c * ΔT
        air_density = 1.2  # kg/m³
        specific_heat_capacity = 1005  # J/(kg·K)
        
        ventilation_heat_loss_w = (
            building_volume_m3 *
            air_change_rate_h *
            air_density *
            specific_heat_capacity *
            temp_difference
        ) / 3600  # Convert J/h to W
        
        ventilation_heat_loss_kw = ventilation_heat_loss_w / 1000
        
        # Calculate heat gains (internal and solar)
        # Internal gains: 5 W/m² (people, appliances, lighting)
        internal_gains_w = building_area_m2 * 5
        
        # Solar gains: depends on window area and orientation
        # Simplified: 100 W/m² window area during heating season
        solar_gains_w = window_area_m2 * 50  # Conservative estimate
        
        heat_gain_kw = (internal_gains_w + solar_gains_w) / 1000
        
        # Calculate design heat load
        design_heat_load_kw = transmission_heat_loss_kw + ventilation_heat_loss_kw - heat_gain_kw
        
        # Add safety margin (10-15%)
        safety_margin_percent = 0.12
        safety_margin_kw = design_heat_load_kw * safety_margin_percent
        
        total_heat_load_kw = design_heat_load_kw + safety_margin_kw
        
        # Calculate specific heat load
        specific_heat_load_w_m2 = (total_heat_load_kw * 1000) / building_area_m2
        
        return HeatLoadCalculation(
            design_heat_load_kw=design_heat_load_kw,
            transmission_heat_loss_kw=transmission_heat_loss_kw,
            ventilation_heat_loss_kw=ventilation_heat_loss_kw,
            heat_gain_kw=heat_gain_kw,
            safety_margin_kw=safety_margin_kw,
            total_heat_load_kw=total_heat_load_kw,
            specific_heat_load_w_m2=specific_heat_load_w_m2,
            calculation_method="DIN EN 12831",
            design_outdoor_temp_c=design_outdoor_temp_c,
            design_indoor_temp_c=indoor_temp_c
        )

    # ========== Building Insulation Analysis ==========
    
    @log_service_call(service_name="heatpump_sizing", log_timing=True)
    @handle_service_errors(service_name="heatpump_sizing", error_message="Insulation analysis failed")
    def analyze_insulation(
        self,
        building_area_m2: float,
        insulation_standard: InsulationStandard,
        climate_zone: ClimateZone,
        actual_u_values: Optional[Dict[str, float]] = None
    ) -> InsulationAnalysis:
        """
        Analyze building insulation quality
        
        Args:
            building_area_m2: Building area
            insulation_standard: Current insulation standard
            climate_zone: Climate zone
            actual_u_values: Actual measured U-values (optional)
            
        Returns:
            InsulationAnalysis with insulation quality assessment
        """
        # Get standard U-values
        standard_u_values = self.u_value_standards[insulation_standard]
        
        # Use actual U-values if provided, otherwise use standard
        u_values = actual_u_values if actual_u_values else standard_u_values
        
        # Calculate average U-value (weighted by typical surface areas)
        # Typical distribution: 40% walls, 25% roof, 20% floor, 15% windows
        average_u_value = (
            u_values.get("walls", standard_u_values["walls"]) * 0.40 +
            u_values.get("roof", standard_u_values["roof"]) * 0.25 +
            u_values.get("floor", standard_u_values["floor"]) * 0.20 +
            u_values.get("windows", standard_u_values["windows"]) * 0.15
        )
        
        # Calculate insulation quality score (0-100)
        # Best possible: Passive house (0.1 W/m²K average)
        # Worst: Old building (1.5 W/m²K average)
        best_u_value = 0.1
        worst_u_value = 1.5
        quality_score = max(0, min(100, 
            (worst_u_value - average_u_value) / (worst_u_value - best_u_value) * 100
        ))
        
        # Calculate improvement potential
        # Compare to KfW 55 standard
        target_u_values = self.u_value_standards[InsulationStandard.KFW_55]
        target_average = (
            target_u_values["walls"] * 0.40 +
            target_u_values["roof"] * 0.25 +
            target_u_values["floor"] * 0.20 +
            target_u_values["windows"] * 0.15
        )
        improvement_potential = max(0, (average_u_value - target_average) / average_u_value * 100)
        
        # Generate recommendations
        recommendations = []
        if u_values.get("windows", standard_u_values["windows"]) > 1.3:
            recommendations.append("Replace windows with modern triple-glazed windows (U ≤ 0.9 W/m²K)")
        if u_values.get("roof", standard_u_values["roof"]) > 0.24:
            recommendations.append("Improve roof insulation to at least 20 cm (U ≤ 0.20 W/m²K)")
        if u_values.get("walls", standard_u_values["walls"]) > 0.35:
            recommendations.append("Add external wall insulation (WDVS) 14-16 cm (U ≤ 0.24 W/m²K)")
        if u_values.get("floor", standard_u_values["floor"]) > 0.35:
            recommendations.append("Insulate basement ceiling or floor (U ≤ 0.25 W/m²K)")
        
        # Calculate annual heat loss
        heating_degree_days_value = self.heating_degree_days[climate_zone]
        # Annual heat loss = U-value * Area * HDD * 24h
        annual_heat_loss_kwh = average_u_value * building_area_m2 * heating_degree_days_value * 24 / 1000
        
        return InsulationAnalysis(
            u_value_walls_w_m2k=u_values.get("walls", standard_u_values["walls"]),
            u_value_roof_w_m2k=u_values.get("roof", standard_u_values["roof"]),
            u_value_floor_w_m2k=u_values.get("floor", standard_u_values["floor"]),
            u_value_windows_w_m2k=u_values.get("windows", standard_u_values["windows"]),
            average_u_value_w_m2k=average_u_value,
            insulation_quality_score=quality_score,
            improvement_potential_percent=improvement_potential,
            recommended_improvements=recommendations,
            annual_heat_loss_kwh=annual_heat_loss_kwh
        )

    # ========== Climate-Based Sizing ==========
    
    @log_service_call(service_name="heatpump_sizing", log_timing=True)
    @handle_service_errors(service_name="heatpump_sizing", error_message="Climate-based sizing failed")
    def calculate_climate_sizing(
        self,
        design_heat_load_kw: float,
        climate_zone: ClimateZone,
        bivalent_operation: bool = True,
        monovalent_limit_c: float = -7.0
    ) -> ClimateSizing:
        """
        Calculate climate-based heat pump sizing
        
        Args:
            design_heat_load_kw: Design heat load at design temperature
            climate_zone: Climate zone
            bivalent_operation: Whether to use bivalent operation (with backup)
            monovalent_limit_c: Lowest temperature for heat pump alone
            
        Returns:
            ClimateSizing with climate-based sizing recommendations
        """
        # Get climate data
        design_outdoor_temp_c = self.design_temps[climate_zone]
        heating_degree_days_value = self.heating_degree_days[climate_zone]
        
        # Calculate average winter temperature
        # Simplified: HDD / 200 days / 24 hours + base temp (15°C)
        average_winter_temp_c = 15 - (heating_degree_days_value / (200 * 24))
        
        # Determine bivalent point
        # Typically -5°C to -7°C for air source heat pumps
        if bivalent_operation:
            bivalent_point_c = -5.0
        else:
            bivalent_point_c = design_outdoor_temp_c
        
        # Calculate sizing factor
        # For bivalent operation: size for bivalent point, not design temperature
        # This prevents oversizing and improves efficiency
        if bivalent_operation:
            # Heat load at bivalent point (linear interpolation)
            # Assuming 20°C indoor temperature
            indoor_temp = 20.0
            heat_load_at_bivalent = design_heat_load_kw * (
                (indoor_temp - bivalent_point_c) / (indoor_temp - design_outdoor_temp_c)
            )
            sizing_factor = heat_load_at_bivalent / design_heat_load_kw
        else:
            # Monovalent operation: size for design temperature
            sizing_factor = 1.0
        
        # Calculate recommended capacity
        recommended_capacity_kw = design_heat_load_kw * sizing_factor
        
        # Calculate capacity at bivalent point
        capacity_at_bivalent_kw = recommended_capacity_kw
        
        return ClimateSizing(
            climate_zone=climate_zone,
            design_outdoor_temp_c=design_outdoor_temp_c,
            average_winter_temp_c=average_winter_temp_c,
            heating_degree_days=heating_degree_days_value,
            bivalent_point_c=bivalent_point_c,
            recommended_capacity_kw=recommended_capacity_kw,
            capacity_at_bivalent_kw=capacity_at_bivalent_kw,
            monovalent_limit_c=monovalent_limit_c,
            sizing_factor=sizing_factor
        )

    # ========== Backup Heating Calculations ==========
    
    @log_service_call(service_name="heatpump_sizing", log_timing=True)
    @handle_service_errors(service_name="heatpump_sizing", error_message="Backup heating calculation failed")
    def calculate_backup_heating(
        self,
        design_heat_load_kw: float,
        heat_pump_capacity_kw: float,
        climate_zone: ClimateZone,
        bivalent_point_c: float = -5.0,
        backup_type: str = "electric",
        electricity_price_eur_kwh: float = 0.30,
        gas_price_eur_kwh: float = 0.08
    ) -> BackupHeating:
        """
        Calculate backup heating requirements
        
        Args:
            design_heat_load_kw: Design heat load
            heat_pump_capacity_kw: Heat pump capacity
            climate_zone: Climate zone
            bivalent_point_c: Bivalent point temperature
            backup_type: Type of backup heating
            electricity_price_eur_kwh: Electricity price
            gas_price_eur_kwh: Gas price
            
        Returns:
            BackupHeating with backup heating analysis
        """
        design_outdoor_temp_c = self.design_temps[climate_zone]
        
        # Determine if backup is required
        backup_required = heat_pump_capacity_kw < design_heat_load_kw
        
        if not backup_required:
            return BackupHeating(
                backup_required=False,
                backup_type="none",
                backup_capacity_kw=0.0,
                backup_activation_temp_c=design_outdoor_temp_c,
                annual_backup_hours=0.0,
                annual_backup_energy_kwh=0.0,
                backup_cost_eur_year=0.0,
                backup_percentage=0.0
            )
        
        # Calculate backup capacity needed
        backup_capacity_kw = design_heat_load_kw - heat_pump_capacity_kw
        
        # Backup activates at bivalent point
        backup_activation_temp_c = bivalent_point_c
        
        # Estimate annual backup hours
        # Simplified: hours below bivalent point
        # Typical: 50-150 hours per year depending on climate
        if climate_zone == ClimateZone.ZONE_1:
            annual_backup_hours = 50
        elif climate_zone == ClimateZone.ZONE_2:
            annual_backup_hours = 80
        elif climate_zone == ClimateZone.ZONE_3:
            annual_backup_hours = 120
        else:  # ZONE_4
            annual_backup_hours = 150
        
        # Calculate annual backup energy
        # Average backup load during activation
        average_backup_load_kw = backup_capacity_kw * 0.7  # 70% average load
        annual_backup_energy_kwh = average_backup_load_kw * annual_backup_hours
        
        # Calculate backup cost
        if backup_type == "electric":
            backup_cost_eur_year = annual_backup_energy_kwh * electricity_price_eur_kwh
        elif backup_type == "gas":
            # Gas backup with 90% efficiency
            gas_consumption_kwh = annual_backup_energy_kwh / 0.90
            backup_cost_eur_year = gas_consumption_kwh * gas_price_eur_kwh
        else:
            backup_cost_eur_year = 0.0
        
        # Calculate backup percentage of total heating
        # Estimate total annual heating energy
        heating_degree_days_value = self.heating_degree_days[climate_zone]
        # Simplified annual heating energy estimation
        annual_heating_energy_kwh = design_heat_load_kw * heating_degree_days_value * 24 / (20 - design_outdoor_temp_c)
        backup_percentage = (annual_backup_energy_kwh / annual_heating_energy_kwh * 100) if annual_heating_energy_kwh > 0 else 0
        
        return BackupHeating(
            backup_required=True,
            backup_type=backup_type,
            backup_capacity_kw=backup_capacity_kw,
            backup_activation_temp_c=backup_activation_temp_c,
            annual_backup_hours=annual_backup_hours,
            annual_backup_energy_kwh=annual_backup_energy_kwh,
            backup_cost_eur_year=backup_cost_eur_year,
            backup_percentage=backup_percentage
        )

    # ========== Oversizing/Undersizing Warnings ==========
    
    @log_service_call(service_name="heatpump_sizing", log_timing=True)
    @handle_service_errors(service_name="heatpump_sizing", error_message="Sizing warning analysis failed")
    def analyze_sizing_warnings(
        self,
        design_heat_load_kw: float,
        heat_pump_capacity_kw: float,
        climate_zone: ClimateZone,
        bivalent_operation: bool = True
    ) -> SizingWarnings:
        """
        Analyze oversizing/undersizing and generate warnings
        
        Args:
            design_heat_load_kw: Design heat load
            heat_pump_capacity_kw: Selected heat pump capacity
            climate_zone: Climate zone
            bivalent_operation: Whether bivalent operation is used
            
        Returns:
            SizingWarnings with sizing analysis and recommendations
        """
        warnings = []
        recommendations = []
        
        # Calculate optimal size range
        if bivalent_operation:
            # For bivalent: 60-80% of design load
            optimal_min_kw = design_heat_load_kw * 0.60
            optimal_max_kw = design_heat_load_kw * 0.80
        else:
            # For monovalent: 100-110% of design load
            optimal_min_kw = design_heat_load_kw * 1.00
            optimal_max_kw = design_heat_load_kw * 1.10
        
        # Check for oversizing
        is_oversized = heat_pump_capacity_kw > optimal_max_kw
        oversizing_percent = max(0, (heat_pump_capacity_kw - optimal_max_kw) / optimal_max_kw * 100)
        
        if is_oversized:
            if oversizing_percent > 50:
                warnings.append(f"CRITICAL: Heat pump is severely oversized by {oversizing_percent:.0f}%")
                warnings.append("This will lead to frequent cycling, reduced efficiency, and increased wear")
                recommendations.append(f"Reduce capacity to {optimal_max_kw:.1f} kW or less")
            elif oversizing_percent > 20:
                warnings.append(f"WARNING: Heat pump is oversized by {oversizing_percent:.0f}%")
                warnings.append("This may reduce efficiency and increase cycling")
                recommendations.append(f"Consider reducing capacity to {optimal_max_kw:.1f} kW")
            else:
                warnings.append(f"NOTICE: Heat pump is slightly oversized by {oversizing_percent:.0f}%")
                recommendations.append("Acceptable, but consider inverter-controlled model for better modulation")
        
        # Check for undersizing
        is_undersized = heat_pump_capacity_kw < optimal_min_kw
        undersizing_percent = max(0, (optimal_min_kw - heat_pump_capacity_kw) / optimal_min_kw * 100)
        
        if is_undersized:
            if undersizing_percent > 30:
                warnings.append(f"CRITICAL: Heat pump is severely undersized by {undersizing_percent:.0f}%")
                warnings.append("Insufficient heating capacity, backup heating will run frequently")
                recommendations.append(f"Increase capacity to at least {optimal_min_kw:.1f} kW")
                if not bivalent_operation:
                    recommendations.append("Consider bivalent operation with backup heating")
            elif undersizing_percent > 15:
                warnings.append(f"WARNING: Heat pump is undersized by {undersizing_percent:.0f}%")
                warnings.append("May struggle to maintain comfort in extreme cold")
                recommendations.append(f"Consider increasing capacity to {optimal_min_kw:.1f} kW")
            else:
                warnings.append(f"NOTICE: Heat pump is slightly undersized by {undersizing_percent:.0f}%")
                recommendations.append("Ensure adequate backup heating is available")
        
        # Calculate efficiency impact
        if is_oversized:
            # Oversizing reduces efficiency due to cycling
            efficiency_impact_percent = -min(30, oversizing_percent * 0.5)
        elif is_undersized:
            # Undersizing increases backup heating usage
            efficiency_impact_percent = -min(20, undersizing_percent * 0.3)
        else:
            efficiency_impact_percent = 0.0
        
        # Add general recommendations
        if not warnings:
            recommendations.append("Heat pump is optimally sized for the application")
            recommendations.append("Ensure proper installation and commissioning for best performance")
        
        return SizingWarnings(
            is_oversized=is_oversized,
            is_undersized=is_undersized,
            oversizing_percent=oversizing_percent,
            undersizing_percent=undersizing_percent,
            warnings=warnings,
            recommendations=recommendations,
            optimal_size_range_kw=(optimal_min_kw, optimal_max_kw),
            efficiency_impact_percent=efficiency_impact_percent
        )

    # ========== Seasonal Performance Predictions ==========
    
    @log_service_call(service_name="heatpump_sizing", log_timing=True)
    @handle_service_errors(service_name="heatpump_sizing", error_message="Seasonal prediction failed")
    def predict_seasonal_performance(
        self,
        heat_pump_capacity_kw: float,
        climate_zone: ClimateZone,
        heat_pump_type: str = "air_source",  # "air_source", "ground_source"
        flow_temperature_c: float = 35.0
    ) -> SeasonalPrediction:
        """
        Predict seasonal heat pump performance
        
        Args:
            heat_pump_capacity_kw: Heat pump capacity
            climate_zone: Climate zone
            heat_pump_type: Type of heat pump
            flow_temperature_c: Flow temperature
            
        Returns:
            SeasonalPrediction with seasonal performance predictions
        """
        # Define seasonal average temperatures
        if climate_zone == ClimateZone.ZONE_1:
            seasonal_temps = {"winter": 2, "spring": 10, "summer": 18, "autumn": 9}
        elif climate_zone == ClimateZone.ZONE_2:
            seasonal_temps = {"winter": 0, "spring": 9, "summer": 17, "autumn": 8}
        elif climate_zone == ClimateZone.ZONE_3:
            seasonal_temps = {"winter": -2, "spring": 8, "summer": 16, "autumn": 7}
        else:  # ZONE_4
            seasonal_temps = {"winter": -4, "spring": 7, "summer": 15, "autumn": 6}
        
        # Calculate capacity at different temperatures
        # Air source: capacity decreases with lower outdoor temperature
        # Ground source: more stable
        
        if heat_pump_type == "air_source":
            # Capacity factor based on outdoor temperature
            # At -15°C: 70% capacity, at +7°C: 100% capacity, at +15°C: 110% capacity
            winter_capacity_factor = 0.70 + (seasonal_temps["winter"] + 15) * 0.015
            spring_capacity_factor = 0.70 + (seasonal_temps["spring"] + 15) * 0.015
            summer_capacity_factor = 0.70 + (seasonal_temps["summer"] + 15) * 0.015
            autumn_capacity_factor = 0.70 + (seasonal_temps["autumn"] + 15) * 0.015
        else:  # ground_source
            # Ground source is more stable (ground temp ~10°C year-round)
            winter_capacity_factor = 0.95
            spring_capacity_factor = 1.00
            summer_capacity_factor = 1.05
            autumn_capacity_factor = 1.00
        
        winter_capacity_kw = heat_pump_capacity_kw * winter_capacity_factor
        spring_capacity_kw = heat_pump_capacity_kw * spring_capacity_factor
        summer_capacity_kw = heat_pump_capacity_kw * summer_capacity_factor
        autumn_capacity_kw = heat_pump_capacity_kw * autumn_capacity_factor
        
        # Calculate COP for each season
        if heat_pump_type == "air_source":
            winter_cop = self._calculate_cop_air_source(seasonal_temps["winter"], flow_temperature_c)
            spring_cop = self._calculate_cop_air_source(seasonal_temps["spring"], flow_temperature_c)
            summer_cop = self._calculate_cop_air_source(seasonal_temps["summer"], flow_temperature_c)
            autumn_cop = self._calculate_cop_air_source(seasonal_temps["autumn"], flow_temperature_c)
        else:  # ground_source
            winter_cop = self._calculate_cop_ground_source(10.0, flow_temperature_c)
            spring_cop = self._calculate_cop_ground_source(10.0, flow_temperature_c)
            summer_cop = self._calculate_cop_ground_source(10.0, flow_temperature_c)
            autumn_cop = self._calculate_cop_ground_source(10.0, flow_temperature_c)
        
        # Calculate annual SCOP (weighted by heating demand)
        # Winter: 40%, Spring: 25%, Summer: 5%, Autumn: 30%
        annual_scop = (
            winter_cop * 0.40 +
            spring_cop * 0.25 +
            summer_cop * 0.05 +
            autumn_cop * 0.30
        )
        
        # Generate monthly performance
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
        
        monthly_performance = []
        for month, temp in enumerate(monthly_temps, 1):
            if heat_pump_type == "air_source":
                capacity_factor = 0.70 + (temp + 15) * 0.015
                cop = self._calculate_cop_air_source(temp, flow_temperature_c)
            else:
                capacity_factor = 0.95 + (month % 12) * 0.01  # Slight seasonal variation
                cop = self._calculate_cop_ground_source(10.0, flow_temperature_c)
            
            monthly_performance.append({
                "month": month,
                "outdoor_temp_c": temp,
                "capacity_kw": heat_pump_capacity_kw * capacity_factor,
                "cop": cop,
                "capacity_factor": capacity_factor
            })
        
        # Calculate capacity degradation
        # Difference between summer and winter capacity
        capacity_degradation_percent = (
            (summer_capacity_kw - winter_capacity_kw) / summer_capacity_kw * 100
        )
        
        return SeasonalPrediction(
            winter_capacity_kw=winter_capacity_kw,
            spring_capacity_kw=spring_capacity_kw,
            summer_capacity_kw=summer_capacity_kw,
            autumn_capacity_kw=autumn_capacity_kw,
            winter_cop=winter_cop,
            spring_cop=spring_cop,
            summer_cop=summer_cop,
            autumn_cop=autumn_cop,
            annual_scop=annual_scop,
            monthly_performance=monthly_performance,
            capacity_degradation_percent=capacity_degradation_percent
        )

    # ========== Helper Methods ==========
    
    def _calculate_cop_air_source(self, outdoor_temp_c: float, flow_temp_c: float) -> float:
        """Calculate COP for air source heat pump"""
        temp_diff = flow_temp_c - outdoor_temp_c
        base_cop = 4.0
        cop = base_cop * (1 - (temp_diff - 28) * 0.015)
        return max(2.0, min(5.0, cop))
    
    def _calculate_cop_ground_source(self, ground_temp_c: float, flow_temp_c: float) -> float:
        """Calculate COP for ground source heat pump"""
        temp_diff = flow_temp_c - ground_temp_c
        base_cop = 4.5
        cop = base_cop * (1 - (temp_diff - 25) * 0.012)
        return max(3.0, min(5.5, cop))


# Example usage
if __name__ == "__main__":
    service = HeatPumpSizingService()
    service.initialize()
    
    # Test heat load calculation
    heat_load = service.calculate_heat_load(
        building_area_m2=150.0,
        building_volume_m3=375.0,
        building_type=BuildingType.SINGLE_FAMILY,
        insulation_standard=InsulationStandard.ENEV_2009,
        climate_zone=ClimateZone.ZONE_2
    )
    print("Heat Load Calculation:")
    print(f"  Total Heat Load: {heat_load.total_heat_load_kw:.2f} kW")
    print(f"  Specific Heat Load: {heat_load.specific_heat_load_w_m2:.1f} W/m²")
    
    # Test insulation analysis
    insulation = service.analyze_insulation(
        building_area_m2=150.0,
        insulation_standard=InsulationStandard.ENEV_2009,
        climate_zone=ClimateZone.ZONE_2
    )
    print(f"\nInsulation Analysis:")
    print(f"  Quality Score: {insulation.insulation_quality_score:.1f}/100")
    print(f"  Improvement Potential: {insulation.improvement_potential_percent:.1f}%")
    
    # Test climate sizing
    climate_sizing = service.calculate_climate_sizing(
        design_heat_load_kw=heat_load.total_heat_load_kw,
        climate_zone=ClimateZone.ZONE_2,
        bivalent_operation=True
    )
    print(f"\nClimate Sizing:")
    print(f"  Recommended Capacity: {climate_sizing.recommended_capacity_kw:.2f} kW")
    print(f"  Bivalent Point: {climate_sizing.bivalent_point_c}°C")
    
    # Test sizing warnings
    warnings = service.analyze_sizing_warnings(
        design_heat_load_kw=heat_load.total_heat_load_kw,
        heat_pump_capacity_kw=8.0,
        climate_zone=ClimateZone.ZONE_2,
        bivalent_operation=True
    )
    print(f"\nSizing Warnings:")
    for warning in warnings.warnings:
        print(f"  - {warning}")
    for rec in warnings.recommendations:
        print(f"  → {rec}")
