"""
Solar Calculator Service

This service wraps the legacy calculations.py module and provides
a clean API interface for solar system calculations.
"""

import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import hashlib
import json

# Add parent directory to path to import calculations module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.base_service import BaseService, HealthCheckResult, ServiceStatus
from backend.core.error_wrapper import handle_service_errors, ErrorContext
from backend.core.logging_decorator import log_service_call
from backend.models.solar_schemas import (
    SolarCalculationRequest,
    SolarCalculationResponse,
    SolarSystemSizing,
    EnergyProduction,
    SelfConsumption,
    EconomicAnalysis,
    EnvironmentalImpact,
    StorageAnalysis,
    MonthlyData
)


class SolarCalculatorService(BaseService):
    """
    Service wrapper for solar calculator functionality.
    
    Wraps the legacy calculations.py module and provides:
    - Input validation via Pydantic models
    - Caching for repeated calculations
    - Error handling and logging
    - Health checks
    """
    
    def __init__(self):
        super().__init__("solar_calculator")
        self._cache: Dict[str, tuple[SolarCalculationResponse, float]] = {}
        self._cache_ttl_seconds = 300  # 5 minutes cache TTL
        self._calculations_module = None
        
    def initialize(self) -> None:
        """Initialize the service and load legacy calculations module"""
        try:
            # Import the legacy calculations module
            import calculations
            self._calculations_module = calculations
            self._set_legacy_module(calculations)
            self._set_initialized(True)
            self.logger.info("Solar Calculator Service initialized successfully")
        except ImportError as e:
            self.logger.error(f"Failed to import calculations module: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Solar Calculator Service: {e}")
            raise
    
    def health_check(self) -> HealthCheckResult:
        """Perform health check on the service"""
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Service not initialized"
            )
        
        if self._calculations_module is None:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Calculations module not loaded"
            )
        
        # Check if key functions are available
        required_functions = ['perform_calculations', 'get_pvgis_data']
        missing_functions = []
        
        for func_name in required_functions:
            if not hasattr(self._calculations_module, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            return HealthCheckResult(
                status=ServiceStatus.DEGRADED,
                message=f"Missing functions: {', '.join(missing_functions)}",
                details={"missing_functions": missing_functions}
            )
        
        return HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="Service is healthy",
            details={
                "cache_size": len(self._cache),
                "cache_ttl_seconds": self._cache_ttl_seconds
            }
        )
    
    @log_service_call(service_name="solar_calculator", log_timing=True)
    @handle_service_errors(service_name="solar_calculator", error_message="Solar calculation failed")
    def calculate_solar_system(
        self,
        request: SolarCalculationRequest
    ) -> SolarCalculationResponse:
        """
        Calculate solar system performance and economics.
        
        Args:
            request: Solar calculation request with all parameters
            
        Returns:
            SolarCalculationResponse with complete calculation results
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If calculation fails
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        start_time = time.time()
        
        # Check cache first
        cache_key = self._generate_cache_key(request)
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            self.logger.info(f"Returning cached result for key: {cache_key[:16]}...")
            return cached_result
        
        # Prepare project data in the format expected by legacy calculations.py
        project_data = self._prepare_project_data(request)
        
        # Prepare texts dictionary (for error messages)
        texts = self._get_default_texts()
        
        # Errors list to collect warnings/errors
        errors_list: List[str] = []
        
        # Call legacy perform_calculations function
        try:
            calculation_results = self._calculations_module.perform_calculations(
                project_data=project_data,
                texts=texts,
                errors_list=errors_list,
                simulation_duration_user=request.simulation_period_years,
                electricity_price_increase_user=request.electricity_price_increase_annual_percent
            )
        except Exception as e:
            self.logger.error(f"Calculation failed: {e}")
            raise RuntimeError(f"Solar calculation failed: {str(e)}")
        
        # Transform legacy results to modern response model
        response = self._transform_results(
            calculation_results,
            request,
            errors_list,
            start_time
        )
        
        # Cache the result
        self._add_to_cache(cache_key, response)
        
        return response
    
    def _prepare_project_data(self, request: SolarCalculationRequest) -> Dict[str, Any]:
        """
        Prepare project data dictionary in legacy format.
        
        Args:
            request: Modern request model
            
        Returns:
            Dictionary in legacy calculations.py format
        """
        return {
            "customer_data": {
                "customer_name": request.customer_name or "",
                "customer_email": request.customer_email or ""
            },
            "project_details": {
                # Location
                "latitude": request.latitude,
                "longitude": request.longitude,
                "address": request.address or "",
                
                # Roof configuration
                "roof_area_m2": request.roof_area_m2,
                "roof_orientation": request.roof_orientation.value if hasattr(request.roof_orientation, 'value') else request.roof_orientation,
                "roof_inclination_deg": request.roof_inclination_deg,
                "roof_type": request.roof_type.value if request.roof_type and hasattr(request.roof_type, 'value') else (request.roof_type or ""),
                
                # Module configuration
                "selected_module_id": request.selected_module_id,
                "module_quantity": request.module_quantity,
                
                # Consumption
                "annual_consumption_kwh_yr": request.annual_consumption_kwh_yr,
                "consumption_heating_kwh_yr": request.consumption_heating_kwh_yr,
                "electricity_price_kwh": request.electricity_price_kwh,
                
                # Storage
                "include_storage": request.include_storage,
                "selected_storage_id": request.selected_storage_id,
                "selected_storage_capacity_kwh": request.selected_storage_capacity_kwh,
            },
            "economic_data": {
                "simulation_period_years": request.simulation_period_years,
                "electricity_price_increase_annual_percent": request.electricity_price_increase_annual_percent,
            }
        }
    
    def _get_default_texts(self) -> Dict[str, str]:
        """Get default text translations for error messages"""
        return {
            "warn_global_constants_fallback": "Warning: Using fallback for global constants.",
            "warn_pvgis_zero_coords": "PVGIS: Invalid default coordinates (0,0). Using manual calculation.",
            "pvgis_invalid_lat_lon_range": "PVGIS: Latitude or longitude out of valid range.",
            "error_geocoding_conversion_calc": "Error converting geocoding data for PVGIS.",
            "warn_pvgis_returned_zero_yield_fallback": "PVGIS returned 0 kWh yield. Using manual calculation.",
            "warn_pvgis_incomplete_data_fallback": "PVGIS response incomplete/invalid. Using manual calculation.",
            "warn_invalid_monthly_distribution": "Invalid monthly production distribution in constants, using uniform distribution.",
            "warn_invalid_monthly_consumption_distribution": "Invalid monthly consumption distribution, using uniform distribution.",
            "info_global_yield_adjustment_applied": "Global yield adjustment of {percent}% was applied."
        }
    
    def _transform_results(
        self,
        calc_results: Dict[str, Any],
        request: SolarCalculationRequest,
        errors_list: List[str],
        start_time: float
    ) -> SolarCalculationResponse:
        """
        Transform legacy calculation results to modern response model.
        
        Args:
            calc_results: Results from legacy calculations.py
            request: Original request
            errors_list: List of errors/warnings
            start_time: Calculation start time
            
        Returns:
            SolarCalculationResponse model
        """
        calculation_duration_ms = (time.time() - start_time) * 1000
        
        # Extract system sizing
        system_sizing = SolarSystemSizing(
            system_size_kwp=calc_results.get("anlage_kwp", 0.0),
            module_count=request.module_quantity,
            module_capacity_w=request.module_capacity_w or 0.0,
            specific_yield_kwh_kwp=calc_results.get("specific_annual_yield_kwh_per_kwp", 0.0)
        )
        
        # Extract energy production
        monthly_prod_list = calc_results.get("monthly_productions_sim", [0.0] * 12)
        if len(monthly_prod_list) != 12:
            monthly_prod_list = [0.0] * 12
        
        energy_production = EnergyProduction(
            annual_production_kwh=calc_results.get("annual_pv_production_kwh", 0.0),
            monthly_production_kwh=MonthlyData.from_list(monthly_prod_list),
            pvgis_data_used=calc_results.get("pvgis_data_used", False),
            pvgis_source=calc_results.get("pvgis_source", "Manual")
        )
        
        # Extract self-consumption data
        annual_self_consumption = calc_results.get("annual_self_consumption_kwh", 0.0)
        annual_production = calc_results.get("annual_pv_production_kwh", 1.0)  # Avoid division by zero
        annual_consumption = calc_results.get("total_consumption_kwh_yr", 1.0)
        
        self_consumption_rate = (annual_self_consumption / annual_production * 100) if annual_production > 0 else 0.0
        autarky_degree = (annual_self_consumption / annual_consumption * 100) if annual_consumption > 0 else 0.0
        
        self_consumption = SelfConsumption(
            annual_self_consumption_kwh=annual_self_consumption,
            self_consumption_rate_percent=self_consumption_rate,
            autarky_degree_percent=autarky_degree,
            annual_grid_feed_in_kwh=calc_results.get("annual_feed_in_kwh", 0.0),
            annual_grid_purchase_kwh=calc_results.get("annual_grid_purchase_kwh", 0.0)
        )
        
        # Extract economic analysis
        economic_analysis = EconomicAnalysis(
            total_investment_cost_net=calc_results.get("final_price_netto", 0.0),
            total_investment_cost_gross=calc_results.get("final_price_brutto", 0.0),
            annual_savings_year1=calc_results.get("annual_savings_year1", 0.0),
            payback_period_years=calc_results.get("payback_period_years", 0.0),
            total_savings_20years=calc_results.get("total_savings_20years", 0.0),
            total_savings_25years=calc_results.get("total_savings_25years", 0.0),
            net_present_value=calc_results.get("net_present_value", None),
            internal_rate_of_return_percent=calc_results.get("internal_rate_of_return_percent", None),
            annual_feed_in_revenue=calc_results.get("annual_feed_in_revenue", 0.0)
        )
        
        # Extract environmental impact
        environmental_impact = EnvironmentalImpact(
            annual_co2_savings_kg=calc_results.get("annual_co2_savings_kg", 0.0),
            total_co2_savings_25years_kg=calc_results.get("total_co2_savings_25years_kg", 0.0),
            equivalent_trees=int(calc_results.get("equivalent_trees", 0)),
            equivalent_car_km=calc_results.get("equivalent_car_km", 0.0),
            co2_payback_time_years=calc_results.get("co2_payback_time_years", None)
        )
        
        # Extract storage analysis if applicable
        storage_analysis = None
        if request.include_storage and request.selected_storage_capacity_kwh > 0:
            storage_analysis = StorageAnalysis(
                storage_capacity_kwh=request.selected_storage_capacity_kwh,
                storage_efficiency_percent=calc_results.get("storage_efficiency_percent", 90.0),
                annual_storage_cycles=calc_results.get("annual_storage_cycles", 250),
                additional_self_consumption_kwh=calc_results.get("additional_self_consumption_from_storage_kwh", 0.0),
                storage_contribution_to_autarky_percent=calc_results.get("storage_contribution_to_autarky_percent", 0.0)
            )
        
        # Separate warnings and errors
        warnings = [msg for msg in errors_list if "warn" in msg.lower() or "warnung" in msg.lower()]
        errors = [msg for msg in errors_list if msg not in warnings]
        
        return SolarCalculationResponse(
            calculation_timestamp=datetime.now(),
            calculation_duration_ms=calculation_duration_ms,
            system_sizing=system_sizing,
            energy_production=energy_production,
            self_consumption=self_consumption,
            economic_analysis=economic_analysis,
            environmental_impact=environmental_impact,
            storage_analysis=storage_analysis,
            warnings=warnings,
            errors=errors,
            metadata={
                "request_hash": self._generate_cache_key(request)[:16],
                "legacy_calculation_keys": list(calc_results.keys())[:20]  # First 20 keys for debugging
            }
        )
    
    def _generate_cache_key(self, request: SolarCalculationRequest) -> str:
        """
        Generate cache key from request parameters.
        
        Args:
            request: Calculation request
            
        Returns:
            MD5 hash of request parameters
        """
        # Create a normalized dict of request parameters
        cache_dict = {
            "lat": request.latitude,
            "lon": request.longitude,
            "orientation": request.roof_orientation.value if hasattr(request.roof_orientation, 'value') else request.roof_orientation,
            "inclination": request.roof_inclination_deg,
            "module_id": request.selected_module_id,
            "module_qty": request.module_quantity,
            "consumption": request.annual_consumption_kwh_yr,
            "heating": request.consumption_heating_kwh_yr,
            "storage": request.include_storage,
            "storage_cap": request.selected_storage_capacity_kwh if request.include_storage else 0,
            "sim_years": request.simulation_period_years,
            "price_increase": request.electricity_price_increase_annual_percent
        }
        
        # Create JSON string and hash it
        cache_str = json.dumps(cache_dict, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[SolarCalculationResponse]:
        """
        Get result from cache if available and not expired.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response or None
        """
        if cache_key not in self._cache:
            return None
        
        result, timestamp = self._cache[cache_key]
        
        # Check if cache entry is expired
        if time.time() - timestamp > self._cache_ttl_seconds:
            del self._cache[cache_key]
            return None
        
        return result
    
    def _add_to_cache(self, cache_key: str, result: SolarCalculationResponse) -> None:
        """
        Add result to cache.
        
        Args:
            cache_key: Cache key
            result: Calculation result
        """
        self._cache[cache_key] = (result, time.time())
        
        # Clean up old cache entries if cache is too large
        if len(self._cache) > 100:
            self._cleanup_cache()
    
    def _cleanup_cache(self) -> None:
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp > self._cache_ttl_seconds
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def clear_cache(self) -> int:
        """
        Clear all cached results.
        
        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        self.logger.info(f"Cleared {count} cache entries")
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "total_entries": len(self._cache),
            "cache_ttl_seconds": self._cache_ttl_seconds,
            "oldest_entry_age_seconds": min(
                (time.time() - timestamp for _, timestamp in self._cache.values()),
                default=0
            )
        }


# Global service instance
_solar_service_instance: Optional[SolarCalculatorService] = None


def get_solar_service() -> SolarCalculatorService:
    """
    Get or create the global Solar Calculator Service instance.
    
    Returns:
        SolarCalculatorService instance
    """
    global _solar_service_instance
    
    if _solar_service_instance is None:
        _solar_service_instance = SolarCalculatorService()
        _solar_service_instance.initialize()
    
    return _solar_service_instance
