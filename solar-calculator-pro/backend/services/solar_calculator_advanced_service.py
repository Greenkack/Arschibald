"""
Solar Calculator Advanced Service

This service provides advanced solar calculation features including:
- Multiple calculation variants (standard, premium, custom)
- Module placement optimization algorithms
- Shading analysis
- Weather data integration
- Energy production forecasting
- Battery storage calculations
- Grid feed-in calculations
- ROI and NPV calculations
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


class CalculationVariant(str, Enum):
    """Calculation variant types"""
    STANDARD = "standard"
    PREMIUM = "premium"
    CUSTOM = "custom"


class ShadingLevel(str, Enum):
    """Shading level categories"""
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    HEAVY = "heavy"


@dataclass
class ModulePlacement:
    """Module placement configuration"""
    row: int
    column: int
    x_position: float
    y_position: float
    z_position: float
    orientation: float  # degrees
    tilt: float  # degrees
    shading_factor: float  # 0.0 to 1.0
    efficiency_factor: float  # 0.0 to 1.0


@dataclass
class WeatherData:
    """Weather data for location"""
    latitude: float
    longitude: float
    annual_irradiation_kwh_m2: float
    monthly_irradiation: List[float]  # 12 months
    average_temperature_c: float
    monthly_temperatures: List[float]  # 12 months
    sunshine_hours_annual: float
    cloud_cover_percent: float


@dataclass
class ShadingAnalysisResult:
    """Shading analysis results"""
    overall_shading_level: ShadingLevel
    annual_shading_loss_percent: float
    monthly_shading_factors: List[float]  # 12 months
    hourly_shading_profile: List[List[float]]  # 365 days x 24 hours
    obstacles: List[Dict[str, Any]]
    recommendations: List[str]


@dataclass
class BatteryStorageAnalysis:
    """Battery storage analysis results"""
    optimal_capacity_kwh: float
    actual_capacity_kwh: float
    daily_cycles: float
    annual_cycles: float
    efficiency_percent: float
    depth_of_discharge_percent: float
    expected_lifetime_years: float
    self_consumption_increase_percent: float
    autarky_increase_percent: float
    roi_years: float
    cost_benefit_ratio: float


@dataclass
class GridFeedInAnalysis:
    """Grid feed-in analysis results"""
    annual_feed_in_kwh: float
    monthly_feed_in_kwh: List[float]
    feed_in_tariff_eur_kwh: float
    annual_feed_in_revenue_eur: float
    grid_connection_capacity_kw: float
    peak_feed_in_power_kw: float
    curtailment_losses_kwh: float
    grid_stability_score: float


@dataclass
class ROIAnalysis:
    """Return on Investment analysis"""
    initial_investment_eur: float
    annual_savings_eur: float
    annual_revenue_eur: float
    payback_period_years: float
    net_present_value_eur: float
    internal_rate_of_return_percent: float
    profitability_index: float
    break_even_year: int
    cumulative_cash_flow_25years: List[float]


class SolarCalculatorAdvancedService(BaseService):
    """
    Advanced Solar Calculator Service
    
    Provides comprehensive solar system analysis including:
    - Advanced calculation variants
    - Module placement optimization
    - Shading analysis
    - Weather integration
    - Production forecasting
    - Battery storage optimization
    - Grid feed-in analysis
    - Financial analysis (ROI, NPV, IRR)
    """
    
    def __init__(self):
        super().__init__("solar_calculator_advanced")
        self._weather_cache: Dict[str, WeatherData] = {}
        self._optimization_cache: Dict[str, Any] = {}
        
    def initialize(self) -> None:
        """Initialize the advanced service"""
        try:
            self._set_initialized(True)
            self.logger.info("Solar Calculator Advanced Service initialized successfully")
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
                "weather_cache_size": len(self._weather_cache),
                "optimization_cache_size": len(self._optimization_cache)
            }
        )

    # ========== Calculation Variants ==========
    
    @log_service_call(service_name="solar_calculator_advanced", log_timing=True)
    @handle_service_errors(service_name="solar_calculator_advanced", error_message="Standard calculation failed")
    def calculate_standard(
        self,
        roof_area_m2: float,
        latitude: float,
        longitude: float,
        orientation: float,
        tilt: float,
        module_power_w: float,
        annual_consumption_kwh: float
    ) -> Dict[str, Any]:
        """
        Standard calculation variant - basic solar system sizing
        
        Args:
            roof_area_m2: Available roof area
            latitude: Location latitude
            longitude: Location longitude
            orientation: Roof orientation (0=South, 90=West, -90=East, 180=North)
            tilt: Roof tilt angle in degrees
            module_power_w: Module power in watts
            annual_consumption_kwh: Annual electricity consumption
            
        Returns:
            Dictionary with standard calculation results
        """
        # Get weather data
        weather = self._get_weather_data(latitude, longitude)
        
        # Calculate optimal system size
        module_area_m2 = 1.7  # Standard module area
        max_modules = int(roof_area_m2 / module_area_m2 * 0.85)  # 85% utilization
        system_size_kwp = max_modules * module_power_w / 1000
        
        # Calculate annual production
        orientation_factor = self._calculate_orientation_factor(orientation)
        tilt_factor = self._calculate_tilt_factor(tilt, latitude)
        annual_production_kwh = (
            system_size_kwp * 
            weather.annual_irradiation_kwh_m2 * 
            orientation_factor * 
            tilt_factor * 
            0.85  # System efficiency
        )
        
        # Calculate self-consumption
        self_consumption_rate = self._estimate_self_consumption_rate(
            annual_production_kwh, 
            annual_consumption_kwh
        )
        annual_self_consumption_kwh = annual_production_kwh * self_consumption_rate
        
        return {
            "variant": CalculationVariant.STANDARD,
            "system_size_kwp": system_size_kwp,
            "module_count": max_modules,
            "annual_production_kwh": annual_production_kwh,
            "annual_self_consumption_kwh": annual_self_consumption_kwh,
            "self_consumption_rate_percent": self_consumption_rate * 100,
            "specific_yield_kwh_kwp": annual_production_kwh / system_size_kwp if system_size_kwp > 0 else 0
        }
    
    @log_service_call(service_name="solar_calculator_advanced", log_timing=True)
    @handle_service_errors(service_name="solar_calculator_advanced", error_message="Premium calculation failed")
    def calculate_premium(
        self,
        roof_area_m2: float,
        latitude: float,
        longitude: float,
        orientation: float,
        tilt: float,
        module_power_w: float,
        annual_consumption_kwh: float,
        include_shading_analysis: bool = True,
        include_battery: bool = True,
        battery_capacity_kwh: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Premium calculation variant - includes shading analysis and battery optimization
        
        Args:
            roof_area_m2: Available roof area
            latitude: Location latitude
            longitude: Location longitude
            orientation: Roof orientation
            tilt: Roof tilt angle
            module_power_w: Module power
            annual_consumption_kwh: Annual consumption
            include_shading_analysis: Whether to perform shading analysis
            include_battery: Whether to include battery storage
            battery_capacity_kwh: Battery capacity (auto-optimized if None)
            
        Returns:
            Dictionary with premium calculation results
        """
        # Start with standard calculation
        standard_result = self.calculate_standard(
            roof_area_m2, latitude, longitude, orientation, tilt,
            module_power_w, annual_consumption_kwh
        )
        
        # Add shading analysis
        shading_result = None
        if include_shading_analysis:
            shading_result = self.analyze_shading(
                latitude, longitude, orientation, tilt,
                roof_area_m2, []  # No obstacles for basic analysis
            )
            # Adjust production based on shading
            standard_result["annual_production_kwh"] *= (1 - shading_result.annual_shading_loss_percent / 100)
        
        # Add battery optimization
        battery_result = None
        if include_battery:
            if battery_capacity_kwh is None:
                # Auto-optimize battery size
                battery_capacity_kwh = self._optimize_battery_size(
                    standard_result["annual_production_kwh"],
                    annual_consumption_kwh
                )
            
            battery_result = self.analyze_battery_storage(
                standard_result["annual_production_kwh"],
                annual_consumption_kwh,
                battery_capacity_kwh
            )
            
            # Update self-consumption with battery
            standard_result["annual_self_consumption_kwh"] += battery_result.self_consumption_increase_percent / 100 * standard_result["annual_production_kwh"]
            standard_result["self_consumption_rate_percent"] = (
                standard_result["annual_self_consumption_kwh"] / standard_result["annual_production_kwh"] * 100
            )
        
        return {
            **standard_result,
            "variant": CalculationVariant.PREMIUM,
            "shading_analysis": shading_result,
            "battery_analysis": battery_result
        }

    @log_service_call(service_name="solar_calculator_advanced", log_timing=True)
    @handle_service_errors(service_name="solar_calculator_advanced", error_message="Custom calculation failed")
    def calculate_custom(
        self,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Custom calculation variant - fully customizable parameters
        
        Args:
            parameters: Dictionary with custom calculation parameters
            
        Returns:
            Dictionary with custom calculation results
        """
        # Extract parameters with defaults
        roof_area_m2 = parameters.get("roof_area_m2", 50.0)
        latitude = parameters.get("latitude", 51.0)
        longitude = parameters.get("longitude", 10.0)
        orientation = parameters.get("orientation", 0.0)
        tilt = parameters.get("tilt", 30.0)
        module_power_w = parameters.get("module_power_w", 400.0)
        annual_consumption_kwh = parameters.get("annual_consumption_kwh", 4000.0)
        
        # Custom factors
        system_efficiency = parameters.get("system_efficiency", 0.85)
        degradation_rate = parameters.get("degradation_rate_percent", 0.5)
        temperature_coefficient = parameters.get("temperature_coefficient", -0.4)
        
        # Get weather data
        weather = self._get_weather_data(latitude, longitude)
        
        # Calculate with custom parameters
        module_area_m2 = parameters.get("module_area_m2", 1.7)
        utilization_factor = parameters.get("utilization_factor", 0.85)
        max_modules = int(roof_area_m2 / module_area_m2 * utilization_factor)
        system_size_kwp = max_modules * module_power_w / 1000
        
        # Calculate production with custom factors
        orientation_factor = self._calculate_orientation_factor(orientation)
        tilt_factor = self._calculate_tilt_factor(tilt, latitude)
        temperature_loss = self._calculate_temperature_loss(
            weather.average_temperature_c,
            temperature_coefficient
        )
        
        annual_production_kwh = (
            system_size_kwp * 
            weather.annual_irradiation_kwh_m2 * 
            orientation_factor * 
            tilt_factor * 
            system_efficiency *
            (1 - temperature_loss)
        )
        
        # Calculate 25-year production with degradation
        production_25years = []
        for year in range(25):
            year_production = annual_production_kwh * (1 - degradation_rate / 100) ** year
            production_25years.append(year_production)
        
        return {
            "variant": CalculationVariant.CUSTOM,
            "system_size_kwp": system_size_kwp,
            "module_count": max_modules,
            "annual_production_kwh": annual_production_kwh,
            "production_25years": production_25years,
            "custom_parameters": {
                "system_efficiency": system_efficiency,
                "degradation_rate_percent": degradation_rate,
                "temperature_coefficient": temperature_coefficient,
                "temperature_loss_percent": temperature_loss * 100
            }
        }
    
    # ========== Module Placement Optimization ==========
    
    @log_service_call(service_name="solar_calculator_advanced", log_timing=True)
    @handle_service_errors(service_name="solar_calculator_advanced", error_message="Module placement optimization failed")
    def optimize_module_placement(
        self,
        roof_area_m2: float,
        roof_length_m: float,
        roof_width_m: float,
        module_length_m: float,
        module_width_m: float,
        orientation: float,
        tilt: float,
        obstacles: List[Dict[str, Any]] = None
    ) -> List[ModulePlacement]:
        """
        Optimize module placement on roof
        
        Args:
            roof_area_m2: Total roof area
            roof_length_m: Roof length
            roof_width_m: Roof width
            module_length_m: Module length
            module_width_m: Module width
            orientation: Roof orientation
            tilt: Roof tilt
            obstacles: List of obstacles (chimneys, vents, etc.)
            
        Returns:
            List of optimized module placements
        """
        if obstacles is None:
            obstacles = []
        
        placements = []
        
        # Calculate spacing requirements
        row_spacing_m = 0.02  # 2cm between modules
        col_spacing_m = 0.02
        edge_clearance_m = 0.3  # 30cm from roof edges
        
        # Try portrait orientation first
        modules_per_row_portrait = int((roof_width_m - 2 * edge_clearance_m) / (module_width_m + col_spacing_m))
        modules_per_col_portrait = int((roof_length_m - 2 * edge_clearance_m) / (module_length_m + row_spacing_m))
        total_portrait = modules_per_row_portrait * modules_per_col_portrait
        
        # Try landscape orientation
        modules_per_row_landscape = int((roof_width_m - 2 * edge_clearance_m) / (module_length_m + col_spacing_m))
        modules_per_col_landscape = int((roof_length_m - 2 * edge_clearance_m) / (module_width_m + row_spacing_m))
        total_landscape = modules_per_row_landscape * modules_per_col_landscape
        
        # Choose orientation with more modules
        if total_portrait >= total_landscape:
            modules_per_row = modules_per_row_portrait
            modules_per_col = modules_per_col_portrait
            module_l = module_length_m
            module_w = module_width_m
            is_portrait = True
        else:
            modules_per_row = modules_per_row_landscape
            modules_per_col = modules_per_col_landscape
            module_l = module_width_m
            module_w = module_length_m
            is_portrait = False
        
        # Generate placements
        for row in range(modules_per_col):
            for col in range(modules_per_row):
                x = edge_clearance_m + col * (module_w + col_spacing_m) + module_w / 2
                y = edge_clearance_m + row * (module_l + row_spacing_m) + module_l / 2
                z = 0.0  # On roof surface
                
                # Check for obstacles
                if self._check_obstacle_collision(x, y, module_w, module_l, obstacles):
                    continue
                
                # Calculate shading factor for this position
                shading_factor = self._calculate_position_shading(
                    x, y, row, col, modules_per_row, modules_per_col, obstacles
                )
                
                # Calculate efficiency factor based on position
                efficiency_factor = self._calculate_position_efficiency(
                    row, col, modules_per_row, modules_per_col
                )
                
                placement = ModulePlacement(
                    row=row,
                    column=col,
                    x_position=x,
                    y_position=y,
                    z_position=z,
                    orientation=orientation,
                    tilt=tilt,
                    shading_factor=shading_factor,
                    efficiency_factor=efficiency_factor
                )
                placements.append(placement)
        
        self.logger.info(f"Optimized placement: {len(placements)} modules ({'portrait' if is_portrait else 'landscape'})")
        
        return placements

    # ========== Shading Analysis ==========
    
    @log_service_call(service_name="solar_calculator_advanced", log_timing=True)
    @handle_service_errors(service_name="solar_calculator_advanced", error_message="Shading analysis failed")
    def analyze_shading(
        self,
        latitude: float,
        longitude: float,
        orientation: float,
        tilt: float,
        roof_area_m2: float,
        obstacles: List[Dict[str, Any]]
    ) -> ShadingAnalysisResult:
        """
        Analyze shading impact on solar production
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            orientation: Roof orientation
            tilt: Roof tilt
            roof_area_m2: Roof area
            obstacles: List of obstacles with height, distance, azimuth
            
        Returns:
            ShadingAnalysisResult with detailed shading analysis
        """
        # Calculate sun path for location
        sun_positions = self._calculate_sun_path(latitude, longitude)
        
        # Initialize hourly shading profile (365 days x 24 hours)
        hourly_shading = [[0.0 for _ in range(24)] for _ in range(365)]
        
        # Calculate shading for each hour of the year
        for day in range(365):
            for hour in range(24):
                sun_altitude, sun_azimuth = sun_positions[day][hour]
                
                if sun_altitude <= 0:
                    # Sun below horizon
                    hourly_shading[day][hour] = 1.0  # Fully shaded
                    continue
                
                # Check each obstacle
                shading_factor = 0.0
                for obstacle in obstacles:
                    obstacle_shading = self._calculate_obstacle_shading(
                        sun_altitude, sun_azimuth,
                        obstacle.get("height_m", 0),
                        obstacle.get("distance_m", 0),
                        obstacle.get("azimuth_deg", 0),
                        obstacle.get("width_m", 0)
                    )
                    shading_factor = max(shading_factor, obstacle_shading)
                
                hourly_shading[day][hour] = shading_factor
        
        # Calculate monthly shading factors
        monthly_shading = []
        for month in range(12):
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]
            start_day = sum([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][:month])
            
            month_shading_sum = 0.0
            month_hours = 0
            
            for day in range(start_day, start_day + days_in_month):
                for hour in range(6, 20):  # Daylight hours
                    month_shading_sum += hourly_shading[day][hour]
                    month_hours += 1
            
            monthly_shading.append(month_shading_sum / month_hours if month_hours > 0 else 0.0)
        
        # Calculate annual shading loss
        annual_shading_loss = sum(monthly_shading) / 12 * 100
        
        # Determine overall shading level
        if annual_shading_loss < 5:
            shading_level = ShadingLevel.NONE
        elif annual_shading_loss < 15:
            shading_level = ShadingLevel.MINIMAL
        elif annual_shading_loss < 30:
            shading_level = ShadingLevel.MODERATE
        else:
            shading_level = ShadingLevel.HEAVY
        
        # Generate recommendations
        recommendations = self._generate_shading_recommendations(
            shading_level, annual_shading_loss, obstacles
        )
        
        return ShadingAnalysisResult(
            overall_shading_level=shading_level,
            annual_shading_loss_percent=annual_shading_loss,
            monthly_shading_factors=monthly_shading,
            hourly_shading_profile=hourly_shading,
            obstacles=obstacles,
            recommendations=recommendations
        )
    
    # ========== Weather Data Integration ==========
    
    def _get_weather_data(self, latitude: float, longitude: float) -> WeatherData:
        """
        Get weather data for location (with caching)
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            WeatherData object
        """
        cache_key = f"{latitude:.2f}_{longitude:.2f}"
        
        if cache_key in self._weather_cache:
            return self._weather_cache[cache_key]
        
        # Fetch weather data (simplified - in production would call PVGIS or similar API)
        # For now, use estimated values based on latitude
        annual_irradiation = self._estimate_irradiation(latitude)
        monthly_irradiation = self._estimate_monthly_irradiation(latitude)
        avg_temperature = self._estimate_temperature(latitude)
        monthly_temperatures = self._estimate_monthly_temperatures(latitude)
        
        weather = WeatherData(
            latitude=latitude,
            longitude=longitude,
            annual_irradiation_kwh_m2=annual_irradiation,
            monthly_irradiation=monthly_irradiation,
            average_temperature_c=avg_temperature,
            monthly_temperatures=monthly_temperatures,
            sunshine_hours_annual=1800 + (50 - abs(latitude)) * 20,
            cloud_cover_percent=50 - (50 - abs(latitude)) * 0.5
        )
        
        self._weather_cache[cache_key] = weather
        return weather

    # ========== Energy Production Forecasting ==========
    
    @log_service_call(service_name="solar_calculator_advanced", log_timing=True)
    @handle_service_errors(service_name="solar_calculator_advanced", error_message="Production forecasting failed")
    def forecast_energy_production(
        self,
        system_size_kwp: float,
        latitude: float,
        longitude: float,
        orientation: float,
        tilt: float,
        years: int = 25,
        degradation_rate_percent: float = 0.5
    ) -> Dict[str, Any]:
        """
        Forecast energy production over multiple years
        
        Args:
            system_size_kwp: System size in kWp
            latitude: Location latitude
            longitude: Location longitude
            orientation: System orientation
            tilt: System tilt
            years: Number of years to forecast
            degradation_rate_percent: Annual degradation rate
            
        Returns:
            Dictionary with production forecast
        """
        weather = self._get_weather_data(latitude, longitude)
        
        # Calculate first year production
        orientation_factor = self._calculate_orientation_factor(orientation)
        tilt_factor = self._calculate_tilt_factor(tilt, latitude)
        
        year1_production = (
            system_size_kwp * 
            weather.annual_irradiation_kwh_m2 * 
            orientation_factor * 
            tilt_factor * 
            0.85
        )
        
        # Forecast for each year with degradation
        annual_forecast = []
        monthly_forecast = []
        
        for year in range(years):
            degradation_factor = (1 - degradation_rate_percent / 100) ** year
            year_production = year1_production * degradation_factor
            annual_forecast.append(year_production)
            
            # Monthly breakdown
            year_monthly = []
            for month in range(12):
                month_factor = weather.monthly_irradiation[month] / sum(weather.monthly_irradiation)
                month_production = year_production * month_factor
                year_monthly.append(month_production)
            monthly_forecast.append(year_monthly)
        
        # Calculate totals
        total_production = sum(annual_forecast)
        average_annual = total_production / years
        
        return {
            "years": years,
            "annual_forecast_kwh": annual_forecast,
            "monthly_forecast_kwh": monthly_forecast,
            "total_production_kwh": total_production,
            "average_annual_kwh": average_annual,
            "degradation_rate_percent": degradation_rate_percent,
            "first_year_production_kwh": year1_production,
            "last_year_production_kwh": annual_forecast[-1]
        }
    
    # ========== Battery Storage Calculations ==========
    
    @log_service_call(service_name="solar_calculator_advanced", log_timing=True)
    @handle_service_errors(service_name="solar_calculator_advanced", error_message="Battery storage analysis failed")
    def analyze_battery_storage(
        self,
        annual_production_kwh: float,
        annual_consumption_kwh: float,
        battery_capacity_kwh: float,
        battery_efficiency_percent: float = 90.0,
        depth_of_discharge_percent: float = 90.0
    ) -> BatteryStorageAnalysis:
        """
        Analyze battery storage system
        
        Args:
            annual_production_kwh: Annual PV production
            annual_consumption_kwh: Annual consumption
            battery_capacity_kwh: Battery capacity
            battery_efficiency_percent: Round-trip efficiency
            depth_of_discharge_percent: Maximum depth of discharge
            
        Returns:
            BatteryStorageAnalysis with detailed battery analysis
        """
        # Calculate usable capacity
        usable_capacity_kwh = battery_capacity_kwh * depth_of_discharge_percent / 100
        
        # Estimate daily production and consumption patterns
        daily_production_kwh = annual_production_kwh / 365
        daily_consumption_kwh = annual_consumption_kwh / 365
        
        # Simulate daily battery operation
        daily_cycles = self._simulate_battery_cycles(
            daily_production_kwh,
            daily_consumption_kwh,
            usable_capacity_kwh,
            battery_efficiency_percent
        )
        
        annual_cycles = daily_cycles * 365
        
        # Calculate self-consumption increase
        without_battery_self_consumption = min(daily_production_kwh, daily_consumption_kwh)
        with_battery_self_consumption = self._calculate_battery_self_consumption(
            daily_production_kwh,
            daily_consumption_kwh,
            usable_capacity_kwh,
            battery_efficiency_percent
        )
        
        self_consumption_increase = (
            (with_battery_self_consumption - without_battery_self_consumption) / 
            daily_production_kwh * 100
        )
        
        # Calculate autarky increase
        autarky_increase = (
            with_battery_self_consumption / daily_consumption_kwh * 100 -
            without_battery_self_consumption / daily_consumption_kwh * 100
        )
        
        # Estimate lifetime based on cycles
        expected_lifetime_years = 6000 / annual_cycles if annual_cycles > 0 else 15
        
        # Calculate ROI (simplified)
        battery_cost_eur = battery_capacity_kwh * 800  # €800 per kWh
        annual_savings_eur = (
            self_consumption_increase / 100 * 
            annual_production_kwh * 
            0.30  # €0.30 per kWh electricity price
        )
        roi_years = battery_cost_eur / annual_savings_eur if annual_savings_eur > 0 else 999
        
        # Cost-benefit ratio
        total_savings_lifetime = annual_savings_eur * expected_lifetime_years
        cost_benefit_ratio = total_savings_lifetime / battery_cost_eur if battery_cost_eur > 0 else 0
        
        # Optimize capacity if needed
        optimal_capacity = self._optimize_battery_size(
            annual_production_kwh,
            annual_consumption_kwh
        )
        
        return BatteryStorageAnalysis(
            optimal_capacity_kwh=optimal_capacity,
            actual_capacity_kwh=battery_capacity_kwh,
            daily_cycles=daily_cycles,
            annual_cycles=annual_cycles,
            efficiency_percent=battery_efficiency_percent,
            depth_of_discharge_percent=depth_of_discharge_percent,
            expected_lifetime_years=expected_lifetime_years,
            self_consumption_increase_percent=self_consumption_increase,
            autarky_increase_percent=autarky_increase,
            roi_years=roi_years,
            cost_benefit_ratio=cost_benefit_ratio
        )

    # ========== Grid Feed-In Calculations ==========
    
    @log_service_call(service_name="solar_calculator_advanced", log_timing=True)
    @handle_service_errors(service_name="solar_calculator_advanced", error_message="Grid feed-in analysis failed")
    def analyze_grid_feed_in(
        self,
        annual_production_kwh: float,
        annual_consumption_kwh: float,
        annual_self_consumption_kwh: float,
        system_size_kwp: float,
        feed_in_tariff_eur_kwh: float = 0.082,
        grid_connection_capacity_kw: Optional[float] = None
    ) -> GridFeedInAnalysis:
        """
        Analyze grid feed-in characteristics
        
        Args:
            annual_production_kwh: Annual PV production
            annual_consumption_kwh: Annual consumption
            annual_self_consumption_kwh: Annual self-consumption
            system_size_kwp: System size
            feed_in_tariff_eur_kwh: Feed-in tariff
            grid_connection_capacity_kw: Grid connection capacity limit
            
        Returns:
            GridFeedInAnalysis with detailed feed-in analysis
        """
        # Calculate annual feed-in
        annual_feed_in_kwh = annual_production_kwh - annual_self_consumption_kwh
        
        # Calculate monthly feed-in (simplified distribution)
        monthly_feed_in = []
        monthly_distribution = [0.04, 0.06, 0.08, 0.10, 0.12, 0.13, 
                               0.13, 0.12, 0.10, 0.07, 0.04, 0.03]
        for factor in monthly_distribution:
            monthly_feed_in.append(annual_feed_in_kwh * factor)
        
        # Calculate revenue
        annual_revenue = annual_feed_in_kwh * feed_in_tariff_eur_kwh
        
        # Determine grid connection capacity
        if grid_connection_capacity_kw is None:
            grid_connection_capacity_kw = system_size_kwp * 0.7  # 70% rule in Germany
        
        # Calculate peak feed-in power (assume 80% of system size at peak)
        peak_feed_in_power_kw = system_size_kwp * 0.8
        
        # Calculate curtailment losses if peak exceeds grid capacity
        curtailment_losses_kwh = 0.0
        if peak_feed_in_power_kw > grid_connection_capacity_kw:
            # Estimate curtailment (simplified)
            excess_capacity = peak_feed_in_power_kw - grid_connection_capacity_kw
            curtailment_hours = 500  # Estimated hours per year at peak
            curtailment_losses_kwh = excess_capacity * curtailment_hours
        
        # Calculate grid stability score (0-100)
        # Based on feed-in variability and grid capacity utilization
        capacity_utilization = peak_feed_in_power_kw / grid_connection_capacity_kw if grid_connection_capacity_kw > 0 else 1.0
        grid_stability_score = max(0, 100 - capacity_utilization * 50)
        
        return GridFeedInAnalysis(
            annual_feed_in_kwh=annual_feed_in_kwh,
            monthly_feed_in_kwh=monthly_feed_in,
            feed_in_tariff_eur_kwh=feed_in_tariff_eur_kwh,
            annual_feed_in_revenue_eur=annual_revenue,
            grid_connection_capacity_kw=grid_connection_capacity_kw,
            peak_feed_in_power_kw=peak_feed_in_power_kw,
            curtailment_losses_kwh=curtailment_losses_kwh,
            grid_stability_score=grid_stability_score
        )
    
    # ========== ROI and NPV Calculations ==========
    
    @log_service_call(service_name="solar_calculator_advanced", log_timing=True)
    @handle_service_errors(service_name="solar_calculator_advanced", error_message="ROI analysis failed")
    def calculate_roi_npv(
        self,
        initial_investment_eur: float,
        annual_production_kwh: float,
        annual_self_consumption_kwh: float,
        annual_feed_in_kwh: float,
        electricity_price_eur_kwh: float = 0.30,
        feed_in_tariff_eur_kwh: float = 0.082,
        electricity_price_increase_percent: float = 3.0,
        discount_rate_percent: float = 4.0,
        years: int = 25,
        degradation_rate_percent: float = 0.5,
        maintenance_cost_annual_eur: float = 200.0
    ) -> ROIAnalysis:
        """
        Calculate Return on Investment and Net Present Value
        
        Args:
            initial_investment_eur: Initial system cost
            annual_production_kwh: Annual production
            annual_self_consumption_kwh: Annual self-consumption
            annual_feed_in_kwh: Annual feed-in
            electricity_price_eur_kwh: Current electricity price
            feed_in_tariff_eur_kwh: Feed-in tariff
            electricity_price_increase_percent: Annual price increase
            discount_rate_percent: Discount rate for NPV
            years: Analysis period
            degradation_rate_percent: Annual degradation
            maintenance_cost_annual_eur: Annual maintenance cost
            
        Returns:
            ROIAnalysis with comprehensive financial analysis
        """
        cumulative_cash_flow = []
        annual_savings = []
        annual_revenue = []
        
        cumulative = -initial_investment_eur
        break_even_year = None
        
        for year in range(years):
            # Apply degradation
            degradation_factor = (1 - degradation_rate_percent / 100) ** year
            year_production = annual_production_kwh * degradation_factor
            year_self_consumption = annual_self_consumption_kwh * degradation_factor
            year_feed_in = annual_feed_in_kwh * degradation_factor
            
            # Apply electricity price increase
            price_factor = (1 + electricity_price_increase_percent / 100) ** year
            year_electricity_price = electricity_price_eur_kwh * price_factor
            
            # Calculate savings and revenue
            savings = year_self_consumption * year_electricity_price
            revenue = year_feed_in * feed_in_tariff_eur_kwh
            total_benefit = savings + revenue - maintenance_cost_annual_eur
            
            annual_savings.append(savings)
            annual_revenue.append(revenue)
            
            # Update cumulative cash flow
            cumulative += total_benefit
            cumulative_cash_flow.append(cumulative)
            
            # Check for break-even
            if break_even_year is None and cumulative >= 0:
                break_even_year = year + 1
        
        # Calculate NPV
        npv = -initial_investment_eur
        for year in range(years):
            discount_factor = 1 / (1 + discount_rate_percent / 100) ** (year + 1)
            npv += (annual_savings[year] + annual_revenue[year] - maintenance_cost_annual_eur) * discount_factor
        
        # Calculate IRR (simplified Newton-Raphson method)
        irr = self._calculate_irr(
            initial_investment_eur,
            annual_savings,
            annual_revenue,
            maintenance_cost_annual_eur,
            years
        )
        
        # Calculate payback period
        payback_period = break_even_year if break_even_year else years
        
        # Calculate profitability index
        present_value_benefits = sum([
            (annual_savings[year] + annual_revenue[year] - maintenance_cost_annual_eur) / 
            (1 + discount_rate_percent / 100) ** (year + 1)
            for year in range(years)
        ])
        profitability_index = present_value_benefits / initial_investment_eur if initial_investment_eur > 0 else 0
        
        return ROIAnalysis(
            initial_investment_eur=initial_investment_eur,
            annual_savings_eur=annual_savings[0],
            annual_revenue_eur=annual_revenue[0],
            payback_period_years=payback_period,
            net_present_value_eur=npv,
            internal_rate_of_return_percent=irr,
            profitability_index=profitability_index,
            break_even_year=break_even_year or years,
            cumulative_cash_flow_25years=cumulative_cash_flow
        )

    # ========== Helper Methods ==========
    
    def _calculate_orientation_factor(self, orientation: float) -> float:
        """Calculate orientation factor (1.0 = South, 0.0 = North)"""
        # orientation: 0=South, 90=West, -90=East, 180=North
        orientation_rad = math.radians(abs(orientation))
        return math.cos(orientation_rad)
    
    def _calculate_tilt_factor(self, tilt: float, latitude: float) -> float:
        """Calculate tilt factor based on optimal tilt for latitude"""
        optimal_tilt = abs(latitude)
        tilt_difference = abs(tilt - optimal_tilt)
        # Maximum efficiency at optimal tilt, decreases with difference
        return 1.0 - (tilt_difference / 90) * 0.15
    
    def _calculate_temperature_loss(self, avg_temp_c: float, temp_coefficient: float) -> float:
        """Calculate temperature-related efficiency loss"""
        # Standard test conditions: 25°C
        temp_difference = avg_temp_c - 25
        return abs(temp_coefficient / 100 * temp_difference)
    
    def _estimate_self_consumption_rate(
        self, 
        annual_production_kwh: float, 
        annual_consumption_kwh: float
    ) -> float:
        """Estimate self-consumption rate without battery"""
        if annual_production_kwh == 0:
            return 0.0
        
        # Simplified model based on production/consumption ratio
        ratio = annual_production_kwh / annual_consumption_kwh if annual_consumption_kwh > 0 else 1.0
        
        if ratio <= 0.3:
            return 0.95
        elif ratio <= 0.5:
            return 0.80
        elif ratio <= 0.7:
            return 0.65
        elif ratio <= 1.0:
            return 0.50
        elif ratio <= 1.5:
            return 0.35
        else:
            return 0.25
    
    def _optimize_battery_size(
        self,
        annual_production_kwh: float,
        annual_consumption_kwh: float
    ) -> float:
        """Optimize battery size for maximum benefit"""
        daily_production = annual_production_kwh / 365
        daily_consumption = annual_consumption_kwh / 365
        
        # Optimal battery size is typically 0.5-1.0 times daily consumption
        # or 1.0-1.5 times daily production surplus
        optimal_size = min(
            daily_consumption * 0.7,
            max(0, daily_production - daily_consumption * 0.3) * 1.2
        )
        
        # Round to nearest 0.5 kWh
        return round(optimal_size * 2) / 2
    
    def _simulate_battery_cycles(
        self,
        daily_production_kwh: float,
        daily_consumption_kwh: float,
        usable_capacity_kwh: float,
        efficiency_percent: float
    ) -> float:
        """Simulate daily battery charge/discharge cycles"""
        # Simplified simulation
        # Assume production peaks at midday, consumption is relatively constant
        
        # Morning: discharge to cover consumption
        morning_discharge = min(usable_capacity_kwh, daily_consumption_kwh * 0.3)
        
        # Midday: charge from excess production
        excess_production = max(0, daily_production_kwh - daily_consumption_kwh * 0.4)
        midday_charge = min(usable_capacity_kwh, excess_production)
        
        # Evening: discharge to cover consumption
        evening_discharge = min(usable_capacity_kwh, daily_consumption_kwh * 0.3)
        
        # Calculate effective cycles
        total_throughput = (morning_discharge + midday_charge + evening_discharge) / 3
        cycles = total_throughput / usable_capacity_kwh if usable_capacity_kwh > 0 else 0
        
        return min(cycles, 1.5)  # Cap at 1.5 cycles per day
    
    def _calculate_battery_self_consumption(
        self,
        daily_production_kwh: float,
        daily_consumption_kwh: float,
        usable_capacity_kwh: float,
        efficiency_percent: float
    ) -> float:
        """Calculate self-consumption with battery"""
        # Without battery
        base_self_consumption = min(daily_production_kwh, daily_consumption_kwh)
        
        # Additional self-consumption from battery
        excess_production = max(0, daily_production_kwh - base_self_consumption)
        stored_energy = min(excess_production, usable_capacity_kwh) * efficiency_percent / 100
        additional_consumption = min(stored_energy, daily_consumption_kwh - base_self_consumption)
        
        return base_self_consumption + additional_consumption
    
    def _check_obstacle_collision(
        self,
        x: float,
        y: float,
        width: float,
        length: float,
        obstacles: List[Dict[str, Any]]
    ) -> bool:
        """Check if module position collides with obstacles"""
        for obstacle in obstacles:
            obs_x = obstacle.get("x", 0)
            obs_y = obstacle.get("y", 0)
            obs_width = obstacle.get("width", 0)
            obs_length = obstacle.get("length", 0)
            
            # Simple rectangle collision detection
            if (abs(x - obs_x) < (width + obs_width) / 2 and
                abs(y - obs_y) < (length + obs_length) / 2):
                return True
        
        return False
    
    def _calculate_position_shading(
        self,
        x: float,
        y: float,
        row: int,
        col: int,
        total_rows: int,
        total_cols: int,
        obstacles: List[Dict[str, Any]]
    ) -> float:
        """Calculate shading factor for module position"""
        # Simplified shading calculation
        # Modules in front rows have less shading
        row_factor = row / total_rows if total_rows > 0 else 0
        shading = row_factor * 0.05  # Up to 5% shading for back rows
        
        # Add obstacle shading
        for obstacle in obstacles:
            distance = math.sqrt((x - obstacle.get("x", 0))**2 + (y - obstacle.get("y", 0))**2)
            if distance < 5:  # Within 5m of obstacle
                shading += 0.1 * (1 - distance / 5)
        
        return min(shading, 0.3)  # Cap at 30% shading
    
    def _calculate_position_efficiency(
        self,
        row: int,
        col: int,
        total_rows: int,
        total_cols: int
    ) -> float:
        """Calculate efficiency factor for module position"""
        # Edge modules may have slightly lower efficiency due to wind/temperature
        edge_penalty = 0.0
        if row == 0 or row == total_rows - 1 or col == 0 or col == total_cols - 1:
            edge_penalty = 0.02
        
        return 1.0 - edge_penalty

    def _calculate_sun_path(
        self,
        latitude: float,
        longitude: float
    ) -> List[List[Tuple[float, float]]]:
        """
        Calculate sun position for each hour of the year
        
        Returns:
            List of 365 days, each with 24 hours of (altitude, azimuth) tuples
        """
        sun_positions = []
        
        for day in range(365):
            day_positions = []
            
            # Calculate solar declination for this day
            declination = 23.45 * math.sin(math.radians(360 * (284 + day) / 365))
            
            for hour in range(24):
                # Calculate hour angle
                hour_angle = 15 * (hour - 12)
                
                # Calculate solar altitude
                lat_rad = math.radians(latitude)
                dec_rad = math.radians(declination)
                ha_rad = math.radians(hour_angle)
                
                sin_altitude = (
                    math.sin(lat_rad) * math.sin(dec_rad) +
                    math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
                )
                altitude = math.degrees(math.asin(max(-1, min(1, sin_altitude))))
                
                # Calculate solar azimuth
                cos_azimuth = (
                    (math.sin(dec_rad) - math.sin(lat_rad) * math.sin(math.radians(altitude))) /
                    (math.cos(lat_rad) * math.cos(math.radians(altitude)))
                ) if altitude > 0 else 0
                
                azimuth = math.degrees(math.acos(max(-1, min(1, cos_azimuth))))
                if hour_angle > 0:
                    azimuth = 360 - azimuth
                
                day_positions.append((altitude, azimuth))
            
            sun_positions.append(day_positions)
        
        return sun_positions
    
    def _calculate_obstacle_shading(
        self,
        sun_altitude: float,
        sun_azimuth: float,
        obstacle_height_m: float,
        obstacle_distance_m: float,
        obstacle_azimuth_deg: float,
        obstacle_width_m: float
    ) -> float:
        """Calculate shading factor from a single obstacle"""
        if sun_altitude <= 0:
            return 1.0
        
        # Calculate obstacle angle
        obstacle_angle = math.degrees(math.atan(obstacle_height_m / obstacle_distance_m)) if obstacle_distance_m > 0 else 90
        
        # Check if sun is behind obstacle
        azimuth_diff = abs(sun_azimuth - obstacle_azimuth_deg)
        if azimuth_diff > 90:
            return 0.0  # Sun not blocked by this obstacle
        
        # Calculate shading based on sun altitude vs obstacle angle
        if sun_altitude < obstacle_angle:
            # Sun is blocked
            # Calculate partial shading based on obstacle width and distance
            angular_width = math.degrees(math.atan(obstacle_width_m / obstacle_distance_m)) if obstacle_distance_m > 0 else 180
            shading_factor = min(1.0, angular_width / 30)  # Normalize to 30 degrees
            return shading_factor
        
        return 0.0
    
    def _generate_shading_recommendations(
        self,
        shading_level: ShadingLevel,
        annual_loss_percent: float,
        obstacles: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on shading analysis"""
        recommendations = []
        
        if shading_level == ShadingLevel.NONE:
            recommendations.append("Excellent location with minimal shading")
            recommendations.append("No special measures required")
        
        elif shading_level == ShadingLevel.MINIMAL:
            recommendations.append(f"Minor shading detected ({annual_loss_percent:.1f}% annual loss)")
            recommendations.append("Consider power optimizers for affected modules")
            recommendations.append("Regular tree trimming may help reduce shading")
        
        elif shading_level == ShadingLevel.MODERATE:
            recommendations.append(f"Moderate shading detected ({annual_loss_percent:.1f}% annual loss)")
            recommendations.append("Power optimizers or microinverters strongly recommended")
            recommendations.append("Consider removing or trimming nearby obstacles")
            recommendations.append("Evaluate alternative module placement")
        
        else:  # HEAVY
            recommendations.append(f"Significant shading detected ({annual_loss_percent:.1f}% annual loss)")
            recommendations.append("Microinverters essential for this installation")
            recommendations.append("Consider alternative roof surfaces")
            recommendations.append("Evaluate ground-mounted system as alternative")
            recommendations.append("Professional shading analysis recommended")
        
        # Obstacle-specific recommendations
        if len(obstacles) > 0:
            recommendations.append(f"Detected {len(obstacles)} obstacle(s) affecting system")
        
        return recommendations
    
    def _estimate_irradiation(self, latitude: float) -> float:
        """Estimate annual irradiation based on latitude"""
        # Simplified model: higher irradiation near equator
        base_irradiation = 1200  # kWh/m²/year at equator
        latitude_factor = 1 - abs(latitude) / 180
        return base_irradiation * (0.7 + 0.3 * latitude_factor)
    
    def _estimate_monthly_irradiation(self, latitude: float) -> List[float]:
        """Estimate monthly irradiation distribution"""
        annual = self._estimate_irradiation(latitude)
        
        # Northern hemisphere distribution (adjust for southern hemisphere)
        if latitude >= 0:
            distribution = [0.05, 0.06, 0.08, 0.10, 0.11, 0.12,
                          0.12, 0.11, 0.09, 0.07, 0.05, 0.04]
        else:
            distribution = [0.12, 0.11, 0.09, 0.07, 0.05, 0.04,
                          0.05, 0.06, 0.08, 0.10, 0.11, 0.12]
        
        return [annual * factor for factor in distribution]
    
    def _estimate_temperature(self, latitude: float) -> float:
        """Estimate average annual temperature"""
        # Simplified model
        return 25 - abs(latitude) * 0.5
    
    def _estimate_monthly_temperatures(self, latitude: float) -> List[float]:
        """Estimate monthly temperature distribution"""
        avg_temp = self._estimate_temperature(latitude)
        
        # Temperature variation (higher at higher latitudes)
        variation = abs(latitude) * 0.3
        
        if latitude >= 0:
            # Northern hemisphere
            monthly = [
                avg_temp - variation,  # Jan
                avg_temp - variation * 0.8,  # Feb
                avg_temp - variation * 0.4,  # Mar
                avg_temp,  # Apr
                avg_temp + variation * 0.4,  # May
                avg_temp + variation * 0.8,  # Jun
                avg_temp + variation,  # Jul
                avg_temp + variation * 0.8,  # Aug
                avg_temp + variation * 0.4,  # Sep
                avg_temp,  # Oct
                avg_temp - variation * 0.4,  # Nov
                avg_temp - variation * 0.8,  # Dec
            ]
        else:
            # Southern hemisphere (reversed)
            monthly = [
                avg_temp + variation,  # Jan
                avg_temp + variation * 0.8,  # Feb
                avg_temp + variation * 0.4,  # Mar
                avg_temp,  # Apr
                avg_temp - variation * 0.4,  # May
                avg_temp - variation * 0.8,  # Jun
                avg_temp - variation,  # Jul
                avg_temp - variation * 0.8,  # Aug
                avg_temp - variation * 0.4,  # Sep
                avg_temp,  # Oct
                avg_temp + variation * 0.4,  # Nov
                avg_temp + variation * 0.8,  # Dec
            ]
        
        return monthly
    
    def _calculate_irr(
        self,
        initial_investment: float,
        annual_savings: List[float],
        annual_revenue: List[float],
        annual_costs: float,
        years: int
    ) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson method"""
        # Initial guess
        irr = 0.1  # 10%
        
        # Newton-Raphson iteration
        for _ in range(100):
            npv = -initial_investment
            npv_derivative = 0
            
            for year in range(years):
                cash_flow = annual_savings[year] + annual_revenue[year] - annual_costs
                discount_factor = (1 + irr) ** (year + 1)
                npv += cash_flow / discount_factor
                npv_derivative -= (year + 1) * cash_flow / ((1 + irr) ** (year + 2))
            
            if abs(npv) < 0.01:  # Converged
                break
            
            if npv_derivative == 0:
                break
            
            irr = irr - npv / npv_derivative
            
            # Bounds check
            if irr < -0.99:
                irr = -0.99
            elif irr > 10:
                irr = 10
        
        return irr * 100  # Return as percentage


# Global service instance
_advanced_service_instance: Optional[SolarCalculatorAdvancedService] = None


def get_advanced_solar_service() -> SolarCalculatorAdvancedService:
    """
    Get or create the global Advanced Solar Calculator Service instance.
    
    Returns:
        SolarCalculatorAdvancedService instance
    """
    global _advanced_service_instance
    
    if _advanced_service_instance is None:
        _advanced_service_instance = SolarCalculatorAdvancedService()
        _advanced_service_instance.initialize()
    
    return _advanced_service_instance
