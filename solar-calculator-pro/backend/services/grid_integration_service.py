"""
Grid Integration Service
Comprehensive solar grid integration calculations and analysis
"""

import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from ..models.grid_schemas import (
    FeedInTariffRequest, FeedInTariffResponse,
    NetMeteringRequest, NetMeteringResponse,
    GridConnectionRequest, GridConnectionResponse,
    PowerQualityRequest, PowerQualityResponse,
    GridStabilityRequest, GridStabilityResponse,
    SmartGridRequest, SmartGridResponse,
    GridIntegrationAnalysisRequest, GridIntegrationAnalysisResponse,
    GridConnectionType, MeteringType, PowerQualityStandard
)

logger = logging.getLogger(__name__)


class GridIntegrationService:
    """Service for solar grid integration calculations"""
    
    def __init__(self):
        self.logger = logger
        
        # Standard values
        self.cable_resistivity = 0.0175  # Ohm*mm²/m for copper
        self.max_voltage_drop = 0.03  # 3% maximum voltage drop
        self.power_factor_min = 0.95
        self.thd_limit = 0.05  # 5% THD limit
        
    def calculate_feed_in_tariff(self, request: FeedInTariffRequest) -> FeedInTariffResponse:
        """
        Calculate feed-in tariff benefits over system lifetime
        
        Args:
            request: Feed-in tariff calculation parameters
            
        Returns:
            FeedInTariffResponse with detailed financial analysis
        """
        self.logger.info(f"Calculating feed-in tariff for {request.system_size_kwp} kWp system")
        
        # Calculate annual values
        annual_self_consumption_kwh = request.annual_production_kwh * request.self_consumption_rate
        annual_feed_in_kwh = request.annual_production_kwh * (1 - request.self_consumption_rate)
        
        annual_feed_in_revenue = annual_feed_in_kwh * request.feed_in_tariff_per_kwh
        annual_self_consumption_savings = annual_self_consumption_kwh * request.electricity_price_per_kwh
        total_annual_benefit = annual_feed_in_revenue + annual_self_consumption_savings
        
        # Calculate lifetime values with degradation
        lifetime_feed_in_revenue = 0
        lifetime_self_consumption_savings = 0
        
        for year in range(request.contract_duration_years):
            degradation_factor = (1 - request.degradation_rate) ** year
            year_production = request.annual_production_kwh * degradation_factor
            year_feed_in = year_production * (1 - request.self_consumption_rate)
            year_self_consumption = year_production * request.self_consumption_rate
            
            lifetime_feed_in_revenue += year_feed_in * request.feed_in_tariff_per_kwh
            lifetime_self_consumption_savings += year_self_consumption * request.electricity_price_per_kwh
        
        total_lifetime_benefit = lifetime_feed_in_revenue + lifetime_self_consumption_savings
        average_benefit_per_kwp = total_lifetime_benefit / request.system_size_kwp
        
        # Calculate payback period (simplified)
        system_cost = request.system_size_kwp * 1500  # Estimated €1500/kWp
        payback_period = system_cost / total_annual_benefit if total_annual_benefit > 0 else None
        
        return FeedInTariffResponse(
            annual_feed_in_kwh=round(annual_feed_in_kwh, 2),
            annual_feed_in_revenue=round(annual_feed_in_revenue, 2),
            annual_self_consumption_kwh=round(annual_self_consumption_kwh, 2),
            annual_self_consumption_savings=round(annual_self_consumption_savings, 2),
            total_annual_benefit=round(total_annual_benefit, 2),
            lifetime_feed_in_revenue=round(lifetime_feed_in_revenue, 2),
            lifetime_self_consumption_savings=round(lifetime_self_consumption_savings, 2),
            total_lifetime_benefit=round(total_lifetime_benefit, 2),
            average_benefit_per_kwp=round(average_benefit_per_kwp, 2),
            payback_period_years=round(payback_period, 1) if payback_period else None
        )
    
    def analyze_net_metering(self, request: NetMeteringRequest) -> NetMeteringResponse:
        """
        Analyze net metering benefits and monthly credit flow
        
        Args:
            request: Net metering analysis parameters
            
        Returns:
            NetMeteringResponse with monthly analysis
        """
        self.logger.info(f"Analyzing net metering for {request.system_size_kwp} kWp system")
        
        monthly_analysis = []
        cumulative_credits = 0
        annual_credits_earned = 0
        annual_credits_used = 0
        annual_net_export = 0
        annual_net_import = 0
        
        for month in range(12):
            production = request.monthly_production[month]
            consumption = request.monthly_consumption[month]
            
            net_energy = production - consumption
            
            if net_energy > 0:
                # Surplus - earn credits
                credits_earned = net_energy * request.net_metering_credit_per_kwh
                cumulative_credits += credits_earned
                annual_credits_earned += credits_earned
                annual_net_export += net_energy
                credits_used = 0
                grid_import = 0
            else:
                # Deficit - use credits or import from grid
                energy_needed = abs(net_energy)
                credits_available = cumulative_credits / request.net_metering_credit_per_kwh
                
                if credits_available >= energy_needed:
                    # Use credits
                    credits_used = energy_needed * request.net_metering_credit_per_kwh
                    cumulative_credits -= credits_used
                    annual_credits_used += credits_used
                    grid_import = 0
                else:
                    # Use all credits and import rest
                    credits_used = cumulative_credits
                    cumulative_credits = 0
                    annual_credits_used += credits_used
                    grid_import = energy_needed - credits_available
                    annual_net_import += grid_import
                
                credits_earned = 0
            
            # Check rollover limit
            if not request.rollover_allowed:
                cumulative_credits = 0
            elif month > 0 and month % request.max_rollover_months == 0:
                cumulative_credits = 0  # Reset after rollover period
            
            monthly_analysis.append({
                "month": month + 1,
                "production_kwh": round(production, 2),
                "consumption_kwh": round(consumption, 2),
                "net_energy_kwh": round(net_energy, 2),
                "credits_earned": round(credits_earned, 2),
                "credits_used": round(credits_used, 2),
                "cumulative_credits": round(cumulative_credits, 2),
                "grid_import_kwh": round(grid_import, 2)
            })
        
        # Calculate savings
        annual_net_savings = annual_credits_earned - (annual_net_import * request.electricity_price_per_kwh)
        
        # Calculate self-sufficiency and grid independence
        self_sufficiency_rate = (request.annual_production_kwh / request.annual_consumption_kwh) if request.annual_consumption_kwh > 0 else 0
        self_sufficiency_rate = min(self_sufficiency_rate, 1.0)
        
        grid_independence_rate = 1 - (annual_net_import / request.annual_consumption_kwh) if request.annual_consumption_kwh > 0 else 0
        grid_independence_rate = max(grid_independence_rate, 0)
        
        # Calculate optimal system size
        optimal_size = (request.annual_consumption_kwh / request.annual_production_kwh) * request.system_size_kwp
        
        return NetMeteringResponse(
            annual_net_export_kwh=round(annual_net_export, 2),
            annual_net_import_kwh=round(annual_net_import, 2),
            annual_credits_earned=round(annual_credits_earned, 2),
            annual_credits_used=round(annual_credits_used, 2),
            annual_net_savings=round(annual_net_savings, 2),
            monthly_analysis=monthly_analysis,
            self_sufficiency_rate=round(self_sufficiency_rate, 3),
            grid_independence_rate=round(grid_independence_rate, 3),
            optimal_system_size_kwp=round(optimal_size, 2)
        )
    
    def calculate_grid_connection_requirements(self, request: GridConnectionRequest) -> GridConnectionResponse:
        """
        Calculate grid connection requirements and costs
        
        Args:
            request: Grid connection parameters
            
        Returns:
            GridConnectionResponse with connection requirements
        """
        self.logger.info(f"Calculating grid connection for {request.system_size_kwp} kWp system")
        
        # Calculate required cable size based on current and distance
        max_current = (request.inverter_power_kw * 1000) / request.voltage_level
        
        if request.connection_type == GridConnectionType.THREE_PHASE:
            max_current = max_current / math.sqrt(3)
        
        # Cable sizing with voltage drop consideration
        required_cable_size = (2 * self.cable_resistivity * max_current * request.distance_to_grid_m) / (self.max_voltage_drop * request.voltage_level)
        
        # Round up to standard cable sizes
        standard_sizes = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]
        cable_size = next((size for size in standard_sizes if size >= required_cable_size), 240)
        
        # Calculate actual voltage drop
        voltage_drop = (2 * self.cable_resistivity * max_current * request.distance_to_grid_m) / cable_size
        voltage_drop_percent = (voltage_drop / request.voltage_level) * 100
        
        # Estimate connection cost
        base_cost = 500  # Base connection fee
        cable_cost = cable_size * request.distance_to_grid_m * 5  # €5 per mm² per meter
        installation_cost = request.distance_to_grid_m * 50  # €50 per meter installation
        equipment_cost = 1000 if request.system_size_kwp > 10 else 500
        
        total_cost = base_cost + cable_cost + installation_cost + equipment_cost
        
        # Determine protection devices
        protection_devices = [
            "AC Circuit Breaker",
            "Residual Current Device (RCD)",
            "Surge Protection Device (SPD)"
        ]
        
        if request.system_size_kwp > 10:
            protection_devices.extend([
                "Grid Monitoring Relay",
                "Anti-Islanding Protection"
            ])
        
        # Check grid capacity
        grid_capacity_sufficient = request.system_size_kwp < 30  # Simplified check
        
        # Additional requirements
        additional_requirements = []
        if request.system_size_kwp > 10:
            additional_requirements.append("Grid impact study required")
        if request.distance_to_grid_m > 100:
            additional_requirements.append("Transformer upgrade may be needed")
        if request.building_type == "commercial":
            additional_requirements.append("Commercial metering equipment required")
        
        # Estimate approval time
        approval_time = 30  # Base 30 days
        if request.system_size_kwp > 10:
            approval_time += 30
        if not grid_capacity_sufficient:
            approval_time += 60
        
        # Recommend connection type
        if request.system_size_kwp > 10:
            recommended_type = GridConnectionType.THREE_PHASE
        else:
            recommended_type = request.connection_type
        
        return GridConnectionResponse(
            connection_feasible=voltage_drop_percent <= 3.0,
            required_cable_size_mm2=round(cable_size, 1),
            estimated_connection_cost=round(total_cost, 2),
            voltage_drop_percent=round(voltage_drop_percent, 2),
            max_fault_current_a=round(max_current * 1.5, 2),
            required_protection_devices=protection_devices,
            grid_capacity_sufficient=grid_capacity_sufficient,
            additional_requirements=additional_requirements,
            estimated_approval_time_days=approval_time,
            connection_type_recommended=recommended_type
        )
    
    def analyze_power_quality(self, request: PowerQualityRequest) -> PowerQualityResponse:
        """
        Analyze power quality compliance
        
        Args:
            request: Power quality parameters
            
        Returns:
            PowerQualityResponse with compliance analysis
        """
        self.logger.info(f"Analyzing power quality for {request.system_size_kwp} kWp system")
        
        # Extract inverter specs
        rated_power = request.inverter_specs.get("rated_power_kw", request.system_size_kwp)
        efficiency = request.inverter_specs.get("efficiency", 0.97)
        power_factor = request.inverter_specs.get("power_factor", 0.99)
        
        # Voltage regulation (simplified)
        voltage_regulation = (request.system_size_kwp / 100) * 2  # 2% per 100kW
        voltage_regulation = min(voltage_regulation, 5.0)
        
        # Frequency deviation (typically very small for grid-tied inverters)
        frequency_deviation = 0.01  # ±0.01 Hz
        
        # Total Harmonic Distortion
        thd = request.inverter_specs.get("thd", 0.03)  # 3% typical
        
        # Individual harmonics (simplified)
        individual_harmonics = {
            "3rd": round(thd * 0.4, 4),
            "5th": round(thd * 0.3, 4),
            "7th": round(thd * 0.2, 4),
            "9th": round(thd * 0.1, 4)
        }
        
        # Flicker severity (simplified)
        flicker = request.system_size_kwp * 0.001  # Very low for PV
        
        # DC injection (must be < 0.5% of rated current)
        rated_current = (rated_power * 1000) / request.grid_voltage
        dc_injection = rated_current * 0.002 * 1000  # 0.2% in mA
        
        # Check compliance
        compliance_issues = []
        
        if voltage_regulation > 3.0:
            compliance_issues.append(f"Voltage regulation {voltage_regulation:.2f}% exceeds 3% limit")
        
        if abs(frequency_deviation) > 0.05:
            compliance_issues.append(f"Frequency deviation {frequency_deviation:.3f} Hz exceeds ±0.05 Hz limit")
        
        if power_factor < self.power_factor_min:
            compliance_issues.append(f"Power factor {power_factor:.3f} below {self.power_factor_min} minimum")
        
        if thd > self.thd_limit:
            compliance_issues.append(f"THD {thd*100:.2f}% exceeds {self.thd_limit*100}% limit")
        
        if dc_injection > 500:  # 500mA limit
            compliance_issues.append(f"DC injection {dc_injection:.1f} mA exceeds 500 mA limit")
        
        # Recommendations
        recommendations = []
        if voltage_regulation > 2.5:
            recommendations.append("Consider voltage regulation equipment")
        if power_factor < 0.98:
            recommendations.append("Enable reactive power compensation")
        if thd > 0.04:
            recommendations.append("Install harmonic filters")
        
        compliant = len(compliance_issues) == 0
        
        return PowerQualityResponse(
            compliant=compliant,
            voltage_regulation_percent=round(voltage_regulation, 2),
            frequency_deviation_hz=round(frequency_deviation, 3),
            power_factor=round(power_factor, 3),
            total_harmonic_distortion_percent=round(thd * 100, 2),
            individual_harmonics=individual_harmonics,
            flicker_severity=round(flicker, 4),
            dc_injection_ma=round(dc_injection, 2),
            compliance_issues=compliance_issues,
            recommendations=recommendations
        )
    
    def calculate_grid_stability(self, request: GridStabilityRequest) -> GridStabilityResponse:
        """
        Calculate grid stability metrics
        
        Args:
            request: Grid stability parameters
            
        Returns:
            GridStabilityResponse with stability analysis
        """
        self.logger.info(f"Calculating grid stability for {request.system_size_kwp} kWp system")
        
        # Short circuit ratio (grid strength indicator)
        pv_power_mva = request.system_size_kwp / 1000
        scr = request.grid_short_circuit_power_mva / pv_power_mva
        
        # Voltage stability margin (simplified)
        voltage_stability = min(scr / 20, 1.0)  # SCR > 20 is very stable
        
        # Frequency stability margin
        frequency_stability = 1.0 - (pv_power_mva / request.grid_short_circuit_power_mva)
        frequency_stability = max(frequency_stability, 0)
        
        # Reactive power capability (typically 60% of active power)
        reactive_power_kvar = request.system_size_kwp * 0.6
        
        # Overall stability index
        stability_index = (voltage_stability + frequency_stability) / 2
        
        # Grid support services
        grid_services = []
        if request.enable_reactive_power_support:
            grid_services.append("Reactive Power Support (Q/V control)")
        if request.enable_voltage_regulation:
            grid_services.append("Voltage Regulation")
        if scr > 10:
            grid_services.append("Frequency Response")
        if request.inverter_response_time_ms < 100:
            grid_services.append("Fast Fault Ride-Through")
        
        # Stability concerns
        concerns = []
        if scr < 3:
            concerns.append("Weak grid - SCR below 3")
        if voltage_stability < 0.5:
            concerns.append("Voltage stability margin low")
        if frequency_stability < 0.9:
            concerns.append("High penetration - frequency stability risk")
        
        # Recommended settings
        settings = {
            "power_factor_setpoint": 1.0 if scr > 10 else 0.95,
            "voltage_droop_percent": 3.0 if request.enable_voltage_regulation else 0,
            "frequency_droop_percent": 4.0 if scr > 10 else 0,
            "ramp_rate_limit_percent_per_min": 10.0 if scr < 5 else 20.0
        }
        
        return GridStabilityResponse(
            stability_index=round(stability_index, 3),
            short_circuit_ratio=round(scr, 2),
            voltage_stability_margin=round(voltage_stability, 3),
            frequency_stability_margin=round(frequency_stability, 3),
            reactive_power_capability_kvar=round(reactive_power_kvar, 2),
            grid_support_services=grid_services,
            stability_concerns=concerns,
            recommended_settings=settings
        )
    
    def analyze_smart_grid_integration(self, request: SmartGridRequest) -> SmartGridResponse:
        """
        Analyze smart grid integration potential
        
        Args:
            request: Smart grid parameters
            
        Returns:
            SmartGridResponse with integration analysis
        """
        self.logger.info(f"Analyzing smart grid integration for {request.system_size_kwp} kWp system")
        
        available_services = []
        revenue_streams = {}
        
        # Demand response
        if request.enable_demand_response:
            available_services.append("Demand Response")
            dr_capacity = request.system_size_kwp * 0.8  # 80% available for DR
            dr_revenue = dr_capacity * 50  # €50/kW/year
            revenue_streams["demand_response"] = dr_revenue
        else:
            dr_capacity = 0
        
        # Frequency regulation
        if request.enable_frequency_regulation and request.battery_capacity_kwh:
            available_services.append("Frequency Regulation")
            freq_revenue = request.battery_capacity_kwh * 100  # €100/kWh/year
            revenue_streams["frequency_regulation"] = freq_revenue
            freq_capable = True
        else:
            freq_capable = False
        
        # Voltage support
        if request.enable_voltage_support:
            available_services.append("Voltage Support")
            voltage_revenue = request.system_size_kwp * 30  # €30/kW/year
            revenue_streams["voltage_support"] = voltage_revenue
        
        # Time-of-use optimization
        if request.time_of_use_tariff and request.battery_capacity_kwh:
            available_services.append("Time-of-Use Optimization")
            tou_revenue = request.battery_capacity_kwh * 150  # €150/kWh/year
            revenue_streams["tou_optimization"] = tou_revenue
        
        # Peak shaving
        if request.battery_capacity_kwh:
            available_services.append("Peak Shaving")
            peak_revenue = request.battery_capacity_kwh * 80  # €80/kWh/year
            revenue_streams["peak_shaving"] = peak_revenue
        
        annual_revenue = sum(revenue_streams.values())
        
        # Integration cost
        base_cost = 2000  # Base smart grid controller
        battery_cost = request.battery_capacity_kwh * 500 if request.battery_capacity_kwh else 0
        communication_cost = 1000  # Communication equipment
        integration_cost = base_cost + battery_cost + communication_cost
        
        # Payback period
        payback = integration_cost / annual_revenue if annual_revenue > 0 else None
        
        # Recommended upgrades
        upgrades = []
        if not request.battery_capacity_kwh:
            upgrades.append("Add battery storage for enhanced services")
        if not request.enable_demand_response:
            upgrades.append("Enable demand response capability")
        if not request.time_of_use_tariff:
            upgrades.append("Switch to time-of-use tariff")
        
        smart_grid_ready = len(available_services) >= 3
        
        return SmartGridResponse(
            smart_grid_ready=smart_grid_ready,
            available_services=available_services,
            potential_revenue_streams=revenue_streams,
            annual_grid_services_revenue=round(annual_revenue, 2),
            demand_response_capacity_kw=round(dr_capacity, 2),
            frequency_regulation_capability=freq_capable,
            voltage_support_capability=request.enable_voltage_support,
            recommended_upgrades=upgrades,
            integration_cost=round(integration_cost, 2),
            payback_period_years=round(payback, 1) if payback else None
        )
    
    def comprehensive_grid_analysis(self, request: GridIntegrationAnalysisRequest) -> GridIntegrationAnalysisResponse:
        """
        Perform comprehensive grid integration analysis
        
        Args:
            request: Comprehensive analysis parameters
            
        Returns:
            GridIntegrationAnalysisResponse with complete analysis
        """
        self.logger.info(f"Performing comprehensive grid analysis for {request.system_size_kwp} kWp system")
        
        # Feed-in tariff analysis
        fit_request = FeedInTariffRequest(
            system_size_kwp=request.system_size_kwp,
            annual_production_kwh=request.annual_production_kwh,
            self_consumption_rate=request.annual_consumption_kwh / request.annual_production_kwh if request.annual_production_kwh > 0 else 0.3,
            feed_in_tariff_per_kwh=request.feed_in_tariff_per_kwh,
            electricity_price_per_kwh=request.electricity_price_per_kwh,
            contract_duration_years=20
        )
        feed_in_analysis = self.calculate_feed_in_tariff(fit_request)
        
        # Net metering analysis (if applicable)
        net_metering_analysis = None
        if request.metering_type == MeteringType.NET_METERING:
            # Generate monthly data (simplified)
            monthly_prod = [request.annual_production_kwh / 12] * 12
            monthly_cons = [request.annual_consumption_kwh / 12] * 12
            
            nm_request = NetMeteringRequest(
                system_size_kwp=request.system_size_kwp,
                annual_production_kwh=request.annual_production_kwh,
                annual_consumption_kwh=request.annual_consumption_kwh,
                electricity_price_per_kwh=request.electricity_price_per_kwh,
                net_metering_credit_per_kwh=request.electricity_price_per_kwh * 0.9,
                monthly_production=monthly_prod,
                monthly_consumption=monthly_cons
            )
            net_metering_analysis = self.analyze_net_metering(nm_request)
        
        # Grid connection requirements
        conn_request = GridConnectionRequest(
            system_size_kwp=request.system_size_kwp,
            connection_type=request.connection_type,
            voltage_level=request.grid_voltage,
            distance_to_grid_m=request.distance_to_grid_m,
            inverter_power_kw=request.system_size_kwp,
            location=request.location,
            building_type="residential"
        )
        connection_requirements = self.calculate_grid_connection_requirements(conn_request)
        
        # Power quality analysis
        pq_request = PowerQualityRequest(
            system_size_kwp=request.system_size_kwp,
            inverter_specs={"rated_power_kw": request.system_size_kwp, "efficiency": 0.97, "power_factor": 0.99},
            grid_voltage=request.grid_voltage,
            standard=PowerQualityStandard.VDE_AR_N_4105
        )
        power_quality = self.analyze_power_quality(pq_request)
        
        # Grid stability analysis
        gs_request = GridStabilityRequest(
            system_size_kwp=request.system_size_kwp,
            grid_short_circuit_power_mva=50.0,  # Typical value
            grid_impedance_ohm=0.1,
            inverter_response_time_ms=50
        )
        grid_stability = self.calculate_grid_stability(gs_request)
        
        # Smart grid potential (if enabled)
        smart_grid_potential = None
        if request.enable_smart_grid:
            sg_request = SmartGridRequest(
                system_size_kwp=request.system_size_kwp,
                battery_capacity_kwh=request.battery_capacity_kwh
            )
            smart_grid_potential = self.analyze_smart_grid_integration(sg_request)
        
        # Calculate total benefits
        total_annual = feed_in_analysis.total_annual_benefit
        if net_metering_analysis:
            total_annual = max(total_annual, net_metering_analysis.annual_net_savings)
        if smart_grid_potential:
            total_annual += smart_grid_potential.annual_grid_services_revenue
        
        total_lifetime = feed_in_analysis.total_lifetime_benefit
        if smart_grid_potential:
            total_lifetime += smart_grid_potential.annual_grid_services_revenue * 20
        
        # Recommended configuration
        recommended_config = {
            "connection_type": connection_requirements.connection_type_recommended.value,
            "metering_type": request.metering_type.value,
            "enable_smart_grid": request.enable_smart_grid,
            "cable_size_mm2": connection_requirements.required_cable_size_mm2,
            "protection_devices": connection_requirements.required_protection_devices
        }
        
        # Compliance status
        compliance_status = "Fully Compliant" if power_quality.compliant and connection_requirements.connection_feasible else "Requires Modifications"
        
        # Overall feasibility score (0-100)
        feasibility_score = 0
        if connection_requirements.connection_feasible:
            feasibility_score += 30
        if power_quality.compliant:
            feasibility_score += 30
        if grid_stability.stability_index > 0.7:
            feasibility_score += 20
        if connection_requirements.grid_capacity_sufficient:
            feasibility_score += 20
        
        return GridIntegrationAnalysisResponse(
            feed_in_analysis=feed_in_analysis,
            net_metering_analysis=net_metering_analysis,
            connection_requirements=connection_requirements,
            power_quality=power_quality,
            grid_stability=grid_stability,
            smart_grid_potential=smart_grid_potential,
            total_annual_benefit=round(total_annual, 2),
            total_lifetime_benefit=round(total_lifetime, 2),
            recommended_configuration=recommended_config,
            compliance_status=compliance_status,
            overall_feasibility_score=feasibility_score
        )
