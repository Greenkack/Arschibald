"""
Combined Heat Pump + PV System Integration Service.
Implements system optimization, self-consumption maximization, synergy calculations,
smart control strategies, combined financial analysis, and monitoring integration.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import math

from ..models.combined_system_schemas import (
    CombinedSystemRequest,
    CombinedSystemResponse,
    HourlyEnergyFlow,
    SynergyAnalysis,
    SmartControlSchedule,
    CombinedFinancialAnalysis,
    SystemMonitoringData,
    ControlStrategy,
    TimeOfUseProfile,
    OptimizationRequest,
    OptimizationResponse
)


class CombinedSystemService:
    """Service for combined heat pump + PV system analysis and optimization"""
    
    def __init__(self):
        self.co2_factor_grid = 0.485  # kg CO2 per kWh (German grid mix)
        self.co2_factor_pv = 0.05  # kg CO2 per kWh (PV lifecycle)
        self.discount_rate = 0.04  # 4% discount rate for NPV
        
    def analyze_combined_system(self, request: CombinedSystemRequest) -> CombinedSystemResponse:
        """
        Perform complete analysis of combined heat pump + PV system.
        
        Args:
            request: Combined system parameters
            
        Returns:
            Complete analysis with optimization, synergies, and financial metrics
        """
        # Generate hourly profiles
        hourly_flows = self._simulate_hourly_energy_flows(request)
        
        # Calculate synergies
        synergy = self._calculate_synergies(request, hourly_flows)
        
        # Generate smart control schedule
        control_schedule = self._generate_smart_control_schedule(request, hourly_flows)
        
        # Financial analysis
        financial = self._calculate_combined_financial_analysis(request, hourly_flows, synergy)
        
        # Performance metrics
        self_consumption_rate = self._calculate_self_consumption_rate(hourly_flows)
        grid_independence_rate = self._calculate_grid_independence_rate(hourly_flows)
        renewable_rate = self._calculate_renewable_energy_rate(request, hourly_flows)
        
        # Environmental impact
        co2_savings = self._calculate_co2_savings(request, hourly_flows)
        
        # Comparisons
        comparisons = self._generate_comparisons(request, financial)
        
        # Annual energy flow summary
        annual_flow = self._summarize_annual_energy_flow(hourly_flows)
        
        return CombinedSystemResponse(
            system_configuration=self._get_system_configuration(request),
            optimized_control_strategy=request.control_strategy,
            annual_energy_flow=annual_flow,
            hourly_energy_flows=hourly_flows[:24],  # First day as example
            synergy_analysis=synergy,
            smart_control_schedule=control_schedule,
            control_recommendations=self._generate_control_recommendations(request, synergy),
            financial_analysis=financial,
            self_consumption_rate=self_consumption_rate,
            grid_independence_rate=grid_independence_rate,
            renewable_energy_rate=renewable_rate,
            annual_co2_savings=co2_savings,
            equivalent_trees_planted=int(co2_savings / 22),  # 1 tree absorbs ~22kg CO2/year
            comparison_pv_only=comparisons['pv_only'],
            comparison_hp_only=comparisons['hp_only'],
            comparison_conventional=comparisons['conventional'],
            synergy_benefit=comparisons['synergy_benefit']
        )

    def _simulate_hourly_energy_flows(self, request: CombinedSystemRequest) -> List[HourlyEnergyFlow]:
        """Simulate hourly energy flows for a full year (8760 hours)"""
        flows = []
        
        # Generate typical daily PV production profile (bell curve)
        pv_daily_profile = self._generate_pv_production_profile()
        
        # Generate typical daily heat demand profile
        heat_demand_profile = self._generate_heat_demand_profile(request.building_insulation_quality)
        
        # Generate typical household consumption profile
        household_profile = self._generate_household_consumption_profile()
        
        # Battery state tracking
        battery_soc = request.battery_capacity * 0.5 if request.battery_capacity else 0
        
        for day in range(365):
            # Seasonal factors
            pv_seasonal_factor = self._get_pv_seasonal_factor(day)
            heat_seasonal_factor = self._get_heat_seasonal_factor(day)
            
            for hour in range(24):
                # PV production
                pv_production = (request.pv_annual_production / 365) * pv_daily_profile[hour] * pv_seasonal_factor
                
                # Heat pump consumption
                heat_demand_hour = (request.annual_heating_demand / 365) * heat_demand_profile[hour] * heat_seasonal_factor
                hp_consumption = heat_demand_hour / request.hp_cop if heat_demand_hour > 0 else 0
                
                # Household consumption (excluding heat pump)
                household_consumption = household_profile[hour] * 10  # Assume 10 kWh daily average
                
                # Total consumption
                total_consumption = hp_consumption + household_consumption
                
                # Energy flow optimization based on control strategy
                flow = self._optimize_energy_flow(
                    pv_production=pv_production,
                    hp_consumption=hp_consumption,
                    household_consumption=household_consumption,
                    battery_soc=battery_soc,
                    battery_capacity=request.battery_capacity or 0,
                    battery_efficiency=request.battery_efficiency or 0.95,
                    control_strategy=request.control_strategy,
                    hour=hour,
                    electricity_price=self._get_electricity_price(hour, request),
                    feed_in_tariff=request.feed_in_tariff
                )
                
                # Update battery SOC
                battery_soc = flow['battery_soc_end']
                
                flows.append(HourlyEnergyFlow(
                    hour=hour,
                    pv_production=pv_production,
                    hp_consumption=hp_consumption,
                    household_consumption=household_consumption,
                    battery_charge=flow['battery_charge'],
                    battery_discharge=flow['battery_discharge'],
                    grid_import=flow['grid_import'],
                    grid_export=flow['grid_export'],
                    self_consumption=flow['self_consumption'],
                    electricity_cost=flow['electricity_cost']
                ))
        
        return flows

    def _optimize_energy_flow(self, pv_production: float, hp_consumption: float,
                              household_consumption: float, battery_soc: float,
                              battery_capacity: float, battery_efficiency: float,
                              control_strategy: ControlStrategy, hour: int,
                              electricity_price: float, feed_in_tariff: float) -> Dict[str, float]:
        """
        Optimize energy flow based on control strategy.
        Implements smart control logic for self-consumption maximization.
        """
        total_consumption = hp_consumption + household_consumption
        
        # Initialize flow variables
        self_consumption = 0
        battery_charge = 0
        battery_discharge = 0
        grid_import = 0
        grid_export = 0
        
        # Available PV after direct consumption
        pv_available = pv_production
        consumption_remaining = total_consumption
        
        # Step 1: Direct self-consumption (highest priority)
        direct_use = min(pv_available, consumption_remaining)
        self_consumption += direct_use
        pv_available -= direct_use
        consumption_remaining -= direct_use
        
        # Step 2: Battery operations based on strategy
        if battery_capacity > 0:
            if control_strategy == ControlStrategy.SELF_CONSUMPTION:
                # Maximize self-consumption: charge battery with excess PV, discharge to cover consumption
                if pv_available > 0:
                    # Charge battery with excess PV
                    max_charge = min(pv_available, (battery_capacity - battery_soc) / battery_efficiency)
                    battery_charge = max_charge
                    pv_available -= max_charge
                    battery_soc += max_charge * battery_efficiency
                
                if consumption_remaining > 0 and battery_soc > 0:
                    # Discharge battery to cover remaining consumption
                    max_discharge = min(consumption_remaining, battery_soc * battery_efficiency)
                    battery_discharge = max_discharge
                    self_consumption += max_discharge
                    consumption_remaining -= max_discharge
                    battery_soc -= max_discharge / battery_efficiency
            
            elif control_strategy == ControlStrategy.COST_OPTIMIZATION:
                # Charge during low prices, discharge during high prices
                avg_price = 0.30  # Assume average price
                if electricity_price < avg_price and pv_available > 0:
                    # Charge battery
                    max_charge = min(pv_available, (battery_capacity - battery_soc) / battery_efficiency)
                    battery_charge = max_charge
                    pv_available -= max_charge
                    battery_soc += max_charge * battery_efficiency
                elif electricity_price > avg_price and consumption_remaining > 0 and battery_soc > 0:
                    # Discharge battery
                    max_discharge = min(consumption_remaining, battery_soc * battery_efficiency)
                    battery_discharge = max_discharge
                    self_consumption += max_discharge
                    consumption_remaining -= max_discharge
                    battery_soc -= max_discharge / battery_efficiency
        
        # Step 3: Grid interaction
        if consumption_remaining > 0:
            grid_import = consumption_remaining
        
        if pv_available > 0:
            grid_export = pv_available
        
        # Calculate electricity cost
        electricity_cost = (grid_import * electricity_price) - (grid_export * feed_in_tariff)
        
        return {
            'self_consumption': self_consumption,
            'battery_charge': battery_charge,
            'battery_discharge': battery_discharge,
            'grid_import': grid_import,
            'grid_export': grid_export,
            'electricity_cost': electricity_cost,
            'battery_soc_end': battery_soc
        }

    def _calculate_synergies(self, request: CombinedSystemRequest, 
                            flows: List[HourlyEnergyFlow]) -> SynergyAnalysis:
        """Calculate synergies between PV and heat pump systems"""
        # Calculate PV energy used by heat pump
        pv_to_hp_direct = 0
        pv_to_hp_via_battery = 0
        
        for flow in flows:
            # Direct PV to HP
            pv_for_hp = min(flow.pv_production, flow.hp_consumption)
            pv_to_hp_direct += pv_for_hp
            
            # PV to HP via battery (approximate)
            if flow.battery_discharge > 0 and flow.hp_consumption > 0:
                battery_to_hp = min(flow.battery_discharge, flow.hp_consumption)
                pv_to_hp_via_battery += battery_to_hp * 0.7  # Assume 70% of battery discharge is from PV
        
        total_pv_for_heating = pv_to_hp_direct + pv_to_hp_via_battery
        
        # Calculate heating cost reduction
        total_hp_consumption = sum(flow.hp_consumption for flow in flows)
        heating_cost_with_pv = (total_hp_consumption - total_pv_for_heating) * request.electricity_price
        heating_cost_without_pv = total_hp_consumption * request.electricity_price
        heating_cost_reduction = heating_cost_without_pv - heating_cost_with_pv
        heating_cost_reduction_percent = (heating_cost_reduction / heating_cost_without_pv * 100) if heating_cost_without_pv > 0 else 0
        
        # Effective COP improvement
        effective_cop = request.hp_cop * (1 + (total_pv_for_heating / total_hp_consumption) * 0.5) if total_hp_consumption > 0 else request.hp_cop
        cop_improvement = effective_cop - request.hp_cop
        
        # Grid independence for heating
        grid_independence_heating = (total_pv_for_heating / total_hp_consumption * 100) if total_hp_consumption > 0 else 0
        
        return SynergyAnalysis(
            pv_to_hp_direct=pv_to_hp_direct,
            pv_to_hp_via_battery=pv_to_hp_via_battery,
            total_pv_for_heating=total_pv_for_heating,
            heating_cost_reduction=heating_cost_reduction,
            heating_cost_reduction_percent=heating_cost_reduction_percent,
            cop_improvement=cop_improvement,
            grid_independence_heating=grid_independence_heating
        )
    
    def _generate_smart_control_schedule(self, request: CombinedSystemRequest,
                                        flows: List[HourlyEnergyFlow]) -> List[SmartControlSchedule]:
        """Generate smart control schedule for heat pump operation"""
        schedule = []
        
        # Analyze first week (168 hours) as example
        for hour in range(min(168, len(flows))):
            flow = flows[hour]
            hour_of_day = hour % 24
            
            # Determine operation mode based on PV production and electricity price
            if flow.pv_production > flow.hp_consumption:
                mode = "on"
                power_level = 1.0
                reason = "Abundant PV production - maximize heat pump operation"
            elif flow.pv_production > flow.hp_consumption * 0.5:
                mode = "modulated"
                power_level = 0.7
                reason = "Moderate PV production - modulated operation"
            elif self._get_electricity_price(hour_of_day, request) < request.electricity_price * 0.8:
                mode = "on"
                power_level = 0.8
                reason = "Low electricity price - favorable for operation"
            elif hour_of_day >= 22 or hour_of_day <= 6:
                mode = "modulated"
                power_level = 0.5
                reason = "Night hours - reduced operation"
            else:
                mode = "on"
                power_level = 0.6
                reason = "Standard operation"
            
            schedule.append(SmartControlSchedule(
                hour=hour_of_day,
                hp_operation_mode=mode,
                hp_power_level=power_level,
                reason=reason,
                expected_pv_production=flow.pv_production,
                expected_electricity_price=self._get_electricity_price(hour_of_day, request)
            ))
        
        return schedule[:24]  # Return first day

    def _calculate_combined_financial_analysis(self, request: CombinedSystemRequest,
                                               flows: List[HourlyEnergyFlow],
                                               synergy: SynergyAnalysis) -> CombinedFinancialAnalysis:
        """Calculate comprehensive financial analysis for combined system"""
        # Investment costs (estimates)
        pv_cost_per_kwp = 1200  # €/kWp
        hp_cost_base = 15000  # € base cost
        battery_cost_per_kwh = 800  # €/kWh
        installation_cost = 3000  # €
        
        pv_system_cost = request.pv_system_size * pv_cost_per_kwp
        heat_pump_cost = hp_cost_base
        battery_cost = (request.battery_capacity or 0) * battery_cost_per_kwh
        total_investment = pv_system_cost + heat_pump_cost + battery_cost + installation_cost
        
        # Annual costs and savings
        total_grid_import = sum(flow.grid_import for flow in flows)
        total_grid_export = sum(flow.grid_export for flow in flows)
        total_self_consumption = sum(flow.self_consumption for flow in flows)
        
        annual_electricity_cost_combined = (total_grid_import * request.electricity_price) - (total_grid_export * request.feed_in_tariff)
        
        # Baseline: conventional heating + grid electricity
        conventional_heating_cost = request.annual_heating_demand * 0.08  # €/kWh for gas/oil
        baseline_household_electricity = 3500  # kWh/year
        annual_electricity_cost_baseline = conventional_heating_cost + (baseline_household_electricity * request.electricity_price)
        
        annual_savings = annual_electricity_cost_baseline - annual_electricity_cost_combined
        
        # Heating specific
        total_hp_consumption = sum(flow.hp_consumption for flow in flows)
        annual_heating_cost_baseline = conventional_heating_cost
        annual_heating_cost_hp = total_hp_consumption * request.electricity_price - synergy.heating_cost_reduction
        annual_heating_savings = annual_heating_cost_baseline - annual_heating_cost_hp
        
        # PV economics
        annual_pv_self_consumption_value = total_self_consumption * request.electricity_price
        annual_pv_feed_in_revenue = total_grid_export * request.feed_in_tariff
        pv_self_consumption_rate = total_self_consumption / request.pv_annual_production if request.pv_annual_production > 0 else 0
        
        # ROI metrics
        simple_payback_years = total_investment / annual_savings if annual_savings > 0 else 999
        
        # NPV calculation (20 years)
        npv_20_years = self._calculate_npv(total_investment, annual_savings, 20, self.discount_rate)
        
        # IRR calculation
        irr = self._calculate_irr(total_investment, annual_savings, 20)
        
        # LCOE (Levelized Cost of Energy)
        total_energy_produced_20_years = request.pv_annual_production * 20 * 0.98  # 2% degradation
        lcoe = (total_investment + (annual_electricity_cost_combined * 20)) / total_energy_produced_20_years
        
        # Cumulative cash flow
        cumulative_cash_flow_10_years = (annual_savings * 10) - total_investment
        cumulative_cash_flow_20_years = (annual_savings * 20) - total_investment
        
        return CombinedFinancialAnalysis(
            total_investment=total_investment,
            pv_system_cost=pv_system_cost,
            heat_pump_cost=heat_pump_cost,
            battery_cost=battery_cost,
            installation_cost=installation_cost,
            annual_electricity_cost_baseline=annual_electricity_cost_baseline,
            annual_electricity_cost_combined=annual_electricity_cost_combined,
            annual_savings=annual_savings,
            annual_heating_cost_baseline=annual_heating_cost_baseline,
            annual_heating_cost_hp=annual_heating_cost_hp,
            annual_heating_savings=annual_heating_savings,
            annual_pv_self_consumption_value=annual_pv_self_consumption_value,
            annual_pv_feed_in_revenue=annual_pv_feed_in_revenue,
            pv_self_consumption_rate=pv_self_consumption_rate,
            simple_payback_years=simple_payback_years,
            npv_20_years=npv_20_years,
            irr=irr,
            lcoe=lcoe,
            cumulative_cash_flow_10_years=cumulative_cash_flow_10_years,
            cumulative_cash_flow_20_years=cumulative_cash_flow_20_years
        )

    # Helper methods for profiles and calculations
    
    def _generate_pv_production_profile(self) -> List[float]:
        """Generate normalized daily PV production profile (bell curve)"""
        profile = []
        for hour in range(24):
            if 6 <= hour <= 20:
                # Bell curve centered at noon
                x = (hour - 13) / 4
                value = math.exp(-x**2)
            else:
                value = 0
            profile.append(value)
        
        # Normalize to sum to 1
        total = sum(profile)
        return [v / total for v in profile]
    
    def _generate_heat_demand_profile(self, insulation_quality: str) -> List[float]:
        """Generate normalized daily heat demand profile"""
        # Higher demand in morning and evening
        base_profile = [
            0.06, 0.06, 0.05, 0.05, 0.05, 0.06,  # 0-5: night
            0.08, 0.09, 0.08, 0.06, 0.05, 0.04,  # 6-11: morning
            0.04, 0.04, 0.04, 0.04, 0.05, 0.06,  # 12-17: afternoon
            0.08, 0.09, 0.08, 0.07, 0.07, 0.06   # 18-23: evening
        ]
        
        # Adjust based on insulation quality
        quality_factors = {
            'poor': 1.5,
            'average': 1.2,
            'good': 1.0,
            'excellent': 0.8
        }
        factor = quality_factors.get(insulation_quality, 1.0)
        
        profile = [v * factor for v in base_profile]
        total = sum(profile)
        return [v / total for v in profile]
    
    def _generate_household_consumption_profile(self) -> List[float]:
        """Generate normalized daily household consumption profile"""
        profile = [
            0.02, 0.02, 0.02, 0.02, 0.02, 0.03,  # 0-5: night
            0.05, 0.06, 0.05, 0.04, 0.04, 0.04,  # 6-11: morning
            0.04, 0.04, 0.04, 0.04, 0.05, 0.06,  # 12-17: afternoon
            0.07, 0.08, 0.07, 0.06, 0.04, 0.03   # 18-23: evening
        ]
        total = sum(profile)
        return [v / total for v in profile]
    
    def _get_pv_seasonal_factor(self, day_of_year: int) -> float:
        """Get seasonal factor for PV production (higher in summer)"""
        # Sine wave with peak in summer (day 172 = June 21)
        return 0.5 + 0.5 * math.sin((day_of_year - 80) * 2 * math.pi / 365)
    
    def _get_heat_seasonal_factor(self, day_of_year: int) -> float:
        """Get seasonal factor for heating demand (higher in winter)"""
        # Inverse sine wave with peak in winter
        return 1.5 - 0.5 * math.sin((day_of_year - 80) * 2 * math.pi / 365)
    
    def _get_electricity_price(self, hour: int, request: CombinedSystemRequest) -> float:
        """Get electricity price for given hour"""
        if request.time_of_use_tariff:
            for tariff in request.time_of_use_tariff:
                if tariff.hour == hour:
                    return tariff.price_per_kwh
        return request.electricity_price
    
    def _calculate_self_consumption_rate(self, flows: List[HourlyEnergyFlow]) -> float:
        """Calculate overall self-consumption rate"""
        total_pv = sum(flow.pv_production for flow in flows)
        total_self_consumption = sum(flow.self_consumption for flow in flows)
        return total_self_consumption / total_pv if total_pv > 0 else 0
    
    def _calculate_grid_independence_rate(self, flows: List[HourlyEnergyFlow]) -> float:
        """Calculate grid independence rate"""
        total_consumption = sum(flow.hp_consumption + flow.household_consumption for flow in flows)
        total_grid_import = sum(flow.grid_import for flow in flows)
        return 1 - (total_grid_import / total_consumption) if total_consumption > 0 else 0
    
    def _calculate_renewable_energy_rate(self, request: CombinedSystemRequest, 
                                        flows: List[HourlyEnergyFlow]) -> float:
        """Calculate renewable energy rate"""
        total_consumption = sum(flow.hp_consumption + flow.household_consumption for flow in flows)
        total_renewable = sum(flow.self_consumption for flow in flows)
        return total_renewable / total_consumption if total_consumption > 0 else 0

    def _calculate_co2_savings(self, request: CombinedSystemRequest, 
                               flows: List[HourlyEnergyFlow]) -> float:
        """Calculate annual CO2 savings"""
        # CO2 from grid electricity avoided
        total_self_consumption = sum(flow.self_consumption for flow in flows)
        co2_avoided_grid = total_self_consumption * self.co2_factor_grid
        
        # CO2 from PV production
        co2_from_pv = request.pv_annual_production * self.co2_factor_pv
        
        # Net CO2 savings
        return co2_avoided_grid - co2_from_pv
    
    def _generate_comparisons(self, request: CombinedSystemRequest,
                             financial: CombinedFinancialAnalysis) -> Dict[str, Any]:
        """Generate comparisons with alternative scenarios"""
        # PV only (no heat pump)
        pv_only_investment = financial.pv_system_cost + financial.battery_cost + (financial.installation_cost * 0.6)
        pv_only_savings = financial.annual_pv_self_consumption_value + financial.annual_pv_feed_in_revenue
        
        # HP only (no PV)
        hp_only_investment = financial.heat_pump_cost + (financial.installation_cost * 0.4)
        hp_only_savings = financial.annual_heating_savings * 0.5  # Less savings without PV
        
        # Conventional (no PV, no HP)
        conventional_cost = financial.annual_electricity_cost_baseline
        
        # Synergy benefit
        combined_savings = financial.annual_savings
        separate_savings = pv_only_savings + hp_only_savings
        synergy_benefit = combined_savings - separate_savings
        
        return {
            'pv_only': {
                'investment': pv_only_investment,
                'annual_savings': pv_only_savings,
                'payback_years': pv_only_investment / pv_only_savings if pv_only_savings > 0 else 999
            },
            'hp_only': {
                'investment': hp_only_investment,
                'annual_savings': hp_only_savings,
                'payback_years': hp_only_investment / hp_only_savings if hp_only_savings > 0 else 999
            },
            'conventional': {
                'annual_cost': conventional_cost
            },
            'synergy_benefit': synergy_benefit
        }
    
    def _summarize_annual_energy_flow(self, flows: List[HourlyEnergyFlow]) -> Dict[str, float]:
        """Summarize annual energy flows"""
        return {
            'total_pv_production': sum(flow.pv_production for flow in flows),
            'total_hp_consumption': sum(flow.hp_consumption for flow in flows),
            'total_household_consumption': sum(flow.household_consumption for flow in flows),
            'total_self_consumption': sum(flow.self_consumption for flow in flows),
            'total_grid_import': sum(flow.grid_import for flow in flows),
            'total_grid_export': sum(flow.grid_export for flow in flows),
            'total_battery_charge': sum(flow.battery_charge for flow in flows),
            'total_battery_discharge': sum(flow.battery_discharge for flow in flows),
            'total_electricity_cost': sum(flow.electricity_cost for flow in flows)
        }
    
    def _generate_control_recommendations(self, request: CombinedSystemRequest,
                                         synergy: SynergyAnalysis) -> List[str]:
        """Generate control recommendations"""
        recommendations = []
        
        if synergy.grid_independence_heating < 50:
            recommendations.append("Consider increasing PV system size to improve heating independence")
        
        if request.battery_capacity is None or request.battery_capacity < 5:
            recommendations.append("Adding battery storage would significantly improve self-consumption")
        
        if synergy.pv_to_hp_direct < synergy.total_pv_for_heating * 0.5:
            recommendations.append("Optimize heat pump operation schedule to align with PV production")
        
        if request.control_strategy != ControlStrategy.SELF_CONSUMPTION:
            recommendations.append("Switch to self-consumption strategy for maximum PV utilization")
        
        recommendations.append("Enable smart control to automatically optimize heat pump operation")
        recommendations.append("Monitor system performance regularly and adjust settings as needed")
        
        return recommendations
    
    def _get_system_configuration(self, request: CombinedSystemRequest) -> Dict[str, Any]:
        """Get system configuration summary"""
        return {
            'pv_system_size_kwp': request.pv_system_size,
            'pv_annual_production_kwh': request.pv_annual_production,
            'pv_module_count': request.pv_module_count,
            'heat_pump_model': request.hp_model,
            'heat_pump_cop': request.hp_cop,
            'heat_pump_capacity_kw': request.hp_heating_capacity,
            'battery_capacity_kwh': request.battery_capacity,
            'annual_heating_demand_kwh': request.annual_heating_demand,
            'control_strategy': request.control_strategy.value,
            'location': request.location
        }

    def _calculate_npv(self, investment: float, annual_savings: float, 
                       years: int, discount_rate: float) -> float:
        """Calculate Net Present Value"""
        npv = -investment
        for year in range(1, years + 1):
            npv += annual_savings / ((1 + discount_rate) ** year)
        return npv
    
    def _calculate_irr(self, investment: float, annual_savings: float, years: int) -> float:
        """Calculate Internal Rate of Return (simplified)"""
        # Use Newton-Raphson method to find IRR
        irr_guess = 0.1  # Start with 10%
        tolerance = 0.0001
        max_iterations = 100
        
        for _ in range(max_iterations):
            npv = -investment
            npv_derivative = 0
            
            for year in range(1, years + 1):
                npv += annual_savings / ((1 + irr_guess) ** year)
                npv_derivative -= year * annual_savings / ((1 + irr_guess) ** (year + 1))
            
            if abs(npv) < tolerance:
                return irr_guess * 100  # Return as percentage
            
            irr_guess = irr_guess - npv / npv_derivative
            
            if irr_guess < -0.99:  # Prevent negative IRR below -99%
                irr_guess = -0.99
        
        return irr_guess * 100
    
    def optimize_system(self, request: OptimizationRequest) -> OptimizationResponse:
        """
        Optimize system operation for given time horizon.
        Uses predictive control to minimize costs or maximize self-consumption.
        """
        start_time = datetime.now()
        
        # This would integrate with weather forecasts and load predictions
        # For now, return a simplified optimization
        
        schedule = []
        for hour in range(24):
            schedule.append(SmartControlSchedule(
                hour=hour,
                hp_operation_mode="optimized",
                hp_power_level=0.8,
                reason="Optimized based on forecast",
                expected_pv_production=0,
                expected_electricity_price=0.30
            ))
        
        computation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return OptimizationResponse(
            optimized_schedule=schedule,
            expected_savings=500.0,
            expected_self_consumption_rate=0.75,
            optimization_quality=0.92,
            computation_time_ms=computation_time
        )
    
    def get_monitoring_data(self, system_id: int) -> SystemMonitoringData:
        """
        Get real-time monitoring data for combined system.
        This would integrate with actual monitoring hardware/APIs.
        """
        # Placeholder - would fetch from monitoring system
        return SystemMonitoringData(
            timestamp=datetime.now(),
            pv_current_power=4.5,
            pv_daily_production=25.3,
            pv_monthly_production=680.5,
            pv_annual_production=8250.0,
            hp_status="on",
            hp_current_power=2.1,
            hp_current_cop=3.8,
            hp_daily_consumption=12.5,
            hp_supply_temperature=45.0,
            hp_return_temperature=35.0,
            battery_soc=75.0,
            battery_power=1.2,
            grid_power=-2.4,  # Exporting
            grid_daily_import=5.2,
            grid_daily_export=8.7,
            self_consumption_rate_today=0.82,
            grid_independence_rate_today=0.78,
            cost_savings_today=12.50
        )
