"""
Battery Storage Service

Implements battery sizing calculations, ROI analysis, discharge strategies,
grid independence calculations, lifecycle analysis, and monitoring integration.

Requirements: 1.3, 6.1
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import math
from pydantic import BaseModel


class BatterySpecs(BaseModel):
    """Battery specifications"""
    capacity_kwh: float
    usable_capacity_kwh: float
    max_charge_rate_kw: float
    max_discharge_rate_kw: float
    efficiency: float  # Round-trip efficiency (0-1)
    depth_of_discharge: float  # DoD (0-1)
    warranty_years: int
    warranty_cycles: int
    cost_per_kwh: float
    degradation_rate_per_year: float  # Annual capacity degradation


class BatterySizingRequest(BaseModel):
    """Request for battery sizing calculation"""
    daily_consumption_kwh: float
    pv_system_size_kwp: float
    annual_production_kwh: float
    self_consumption_rate: float
    grid_feed_in_tariff: float  # €/kWh
    electricity_price: float  # €/kWh
    backup_hours: Optional[int] = None  # Hours of backup power needed
    target_self_sufficiency: Optional[float] = None  # Target % (0-1)


class DischargeStrategy(BaseModel):
    """Battery discharge strategy configuration"""
    strategy_type: str  # 'peak_shaving', 'self_consumption', 'time_of_use', 'backup'
    peak_hours: Optional[List[int]] = None  # Hours of day (0-23)
    min_soc: float = 0.2  # Minimum state of charge (0-1)
    max_soc: float = 1.0  # Maximum state of charge (0-1)
    priority: str = 'self_consumption'  # 'self_consumption', 'grid_export', 'backup'


class BatteryStorageService:
    """Service for battery storage calculations and analysis"""
    
    def __init__(self):
        self.default_battery_specs = {
            'small': BatterySpecs(
                capacity_kwh=5.0,
                usable_capacity_kwh=4.5,
                max_charge_rate_kw=2.5,
                max_discharge_rate_kw=2.5,
                efficiency=0.95,
                depth_of_discharge=0.9,
                warranty_years=10,
                warranty_cycles=6000,
                cost_per_kwh=800.0,
                degradation_rate_per_year=0.02
            ),
            'medium': BatterySpecs(
                capacity_kwh=10.0,
                usable_capacity_kwh=9.0,
                max_charge_rate_kw=5.0,
                max_discharge_rate_kw=5.0,
                efficiency=0.95,
                depth_of_discharge=0.9,
                warranty_years=10,
                warranty_cycles=6000,
                cost_per_kwh=750.0,
                degradation_rate_per_year=0.02
            ),
            'large': BatterySpecs(
                capacity_kwh=15.0,
                usable_capacity_kwh=13.5,
                max_charge_rate_kw=7.5,
                max_discharge_rate_kw=7.5,
                efficiency=0.95,
                depth_of_discharge=0.9,
                warranty_years=10,
                warranty_cycles=6000,
                cost_per_kwh=700.0,
                degradation_rate_per_year=0.02
            )
        }
    
    def calculate_battery_sizing(
        self,
        request: BatterySizingRequest
    ) -> Dict[str, Any]:
        """
        Calculate optimal battery size based on consumption and production patterns
        
        Returns recommended battery size, expected performance, and cost analysis
        """
        # Calculate daily surplus and deficit
        daily_production = request.annual_production_kwh / 365
        daily_self_consumption = daily_production * request.self_consumption_rate
        daily_surplus = daily_production - daily_self_consumption
        daily_deficit = request.daily_consumption_kwh - daily_self_consumption
        
        # Determine battery size based on requirements
        if request.backup_hours:
            # Size for backup power
            backup_capacity = (request.daily_consumption_kwh / 24) * request.backup_hours
            recommended_size = backup_capacity / 0.9  # Account for DoD
        elif request.target_self_sufficiency:
            # Size for self-sufficiency target
            additional_storage_needed = daily_deficit * request.target_self_sufficiency
            recommended_size = additional_storage_needed / 0.9
        else:
            # Size based on daily surplus (store excess production)
            recommended_size = min(daily_surplus, daily_deficit) / 0.9
        
        # Select appropriate battery from specs
        battery_category = self._select_battery_category(recommended_size)
        battery_specs = self.default_battery_specs[battery_category]
        
        # Calculate performance metrics
        performance = self._calculate_battery_performance(
            battery_specs,
            request,
            daily_surplus,
            daily_deficit
        )
        
        return {
            'recommended_capacity_kwh': recommended_size,
            'selected_battery': battery_category,
            'battery_specs': battery_specs.dict(),
            'performance': performance,
            'sizing_rationale': {
                'daily_production_kwh': round(daily_production, 2),
                'daily_consumption_kwh': request.daily_consumption_kwh,
                'daily_surplus_kwh': round(daily_surplus, 2),
                'daily_deficit_kwh': round(daily_deficit, 2),
                'backup_hours': request.backup_hours,
                'target_self_sufficiency': request.target_self_sufficiency
            }
        }
    
    def calculate_battery_roi(
        self,
        battery_specs: BatterySpecs,
        request: BatterySizingRequest,
        analysis_years: int = 20
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive ROI analysis for battery storage
        
        Includes payback period, NPV, IRR, and lifetime savings
        """
        # Initial investment
        initial_cost = battery_specs.capacity_kwh * battery_specs.cost_per_kwh
        
        # Annual savings calculation
        daily_production = request.annual_production_kwh / 365
        daily_surplus = daily_production * (1 - request.self_consumption_rate)
        
        # Energy that can be stored and used instead of buying from grid
        daily_stored_energy = min(
            daily_surplus,
            battery_specs.usable_capacity_kwh
        ) * battery_specs.efficiency
        
        # Annual savings from self-consumption
        annual_grid_savings = daily_stored_energy * 365 * request.electricity_price
        
        # Annual savings from avoiding feed-in (if electricity price > feed-in tariff)
        price_difference = request.electricity_price - request.grid_feed_in_tariff
        annual_arbitrage_savings = daily_stored_energy * 365 * price_difference if price_difference > 0 else 0
        
        total_annual_savings = annual_grid_savings + annual_arbitrage_savings
        
        # Calculate year-by-year cash flow with degradation
        cash_flows = []
        cumulative_savings = 0
        payback_year = None
        
        for year in range(1, analysis_years + 1):
            # Apply degradation
            degradation_factor = (1 - battery_specs.degradation_rate_per_year) ** year
            year_savings = total_annual_savings * degradation_factor
            
            cumulative_savings += year_savings
            cash_flows.append({
                'year': year,
                'annual_savings': round(year_savings, 2),
                'cumulative_savings': round(cumulative_savings, 2),
                'capacity_remaining': round(degradation_factor * 100, 1)
            })
            
            # Determine payback year
            if payback_year is None and cumulative_savings >= initial_cost:
                payback_year = year
        
        # Calculate NPV (assuming 3% discount rate)
        discount_rate = 0.03
        npv = -initial_cost + sum(
            cf['annual_savings'] / ((1 + discount_rate) ** cf['year'])
            for cf in cash_flows
        )
        
        # Calculate simple payback period (more precise)
        simple_payback = initial_cost / total_annual_savings if total_annual_savings > 0 else float('inf')
        
        return {
            'initial_investment': round(initial_cost, 2),
            'annual_savings_year_1': round(total_annual_savings, 2),
            'lifetime_savings': round(cumulative_savings, 2),
            'simple_payback_years': round(simple_payback, 1),
            'payback_year': payback_year,
            'npv': round(npv, 2),
            'roi_percent': round((cumulative_savings - initial_cost) / initial_cost * 100, 1),
            'cash_flow_analysis': cash_flows,
            'savings_breakdown': {
                'grid_purchase_savings': round(annual_grid_savings, 2),
                'arbitrage_savings': round(annual_arbitrage_savings, 2),
                'total_annual': round(total_annual_savings, 2)
            }
        }
    
    def calculate_discharge_strategy(
        self,
        strategy: DischargeStrategy,
        battery_specs: BatterySpecs,
        hourly_production: List[float],
        hourly_consumption: List[float]
    ) -> Dict[str, Any]:
        """
        Simulate battery discharge strategy over 24-hour period
        
        Returns optimal charge/discharge schedule and performance metrics
        """
        schedule = []
        soc = 0.5  # Start at 50% state of charge
        total_charged = 0
        total_discharged = 0
        grid_import = 0
        grid_export = 0
        self_consumption = 0
        
        for hour in range(24):
            production = hourly_production[hour]
            consumption = hourly_consumption[hour]
            net_energy = production - consumption
            
            # Determine action based on strategy
            if strategy.strategy_type == 'self_consumption':
                action = self._self_consumption_strategy(
                    net_energy, soc, battery_specs, strategy
                )
            elif strategy.strategy_type == 'peak_shaving':
                action = self._peak_shaving_strategy(
                    hour, net_energy, soc, battery_specs, strategy
                )
            elif strategy.strategy_type == 'time_of_use':
                action = self._time_of_use_strategy(
                    hour, net_energy, soc, battery_specs, strategy
                )
            else:  # backup
                action = self._backup_strategy(
                    net_energy, soc, battery_specs, strategy
                )
            
            # Apply action and update SOC
            if action['type'] == 'charge':
                charge_amount = min(
                    action['amount'],
                    battery_specs.max_charge_rate_kw,
                    (strategy.max_soc - soc) * battery_specs.capacity_kwh
                )
                soc += charge_amount / battery_specs.capacity_kwh
                total_charged += charge_amount
                remaining_surplus = net_energy - charge_amount
                if remaining_surplus > 0:
                    grid_export += remaining_surplus
            elif action['type'] == 'discharge':
                discharge_amount = min(
                    action['amount'],
                    battery_specs.max_discharge_rate_kw,
                    (soc - strategy.min_soc) * battery_specs.capacity_kwh
                )
                soc -= discharge_amount / battery_specs.capacity_kwh
                total_discharged += discharge_amount
                remaining_deficit = abs(net_energy) - discharge_amount
                if remaining_deficit > 0:
                    grid_import += remaining_deficit
                self_consumption += discharge_amount
            else:  # idle
                if net_energy > 0:
                    grid_export += net_energy
                else:
                    grid_import += abs(net_energy)
            
            schedule.append({
                'hour': hour,
                'production_kw': round(production, 2),
                'consumption_kw': round(consumption, 2),
                'action': action['type'],
                'amount_kw': round(action.get('amount', 0), 2),
                'soc_percent': round(soc * 100, 1),
                'grid_import_kw': round(grid_import, 2) if net_energy < 0 else 0,
                'grid_export_kw': round(grid_export, 2) if net_energy > 0 else 0
            })
        
        # Calculate efficiency
        effective_discharged = total_discharged * battery_specs.efficiency
        round_trip_efficiency = (effective_discharged / total_charged * 100) if total_charged > 0 else 0
        
        return {
            'strategy_type': strategy.strategy_type,
            'schedule': schedule,
            'performance': {
                'total_charged_kwh': round(total_charged, 2),
                'total_discharged_kwh': round(total_discharged, 2),
                'effective_discharged_kwh': round(effective_discharged, 2),
                'round_trip_efficiency_percent': round(round_trip_efficiency, 1),
                'grid_import_kwh': round(grid_import, 2),
                'grid_export_kwh': round(grid_export, 2),
                'self_consumption_from_battery_kwh': round(self_consumption, 2),
                'final_soc_percent': round(soc * 100, 1)
            }
        }
    
    def calculate_grid_independence(
        self,
        battery_specs: BatterySpecs,
        request: BatterySizingRequest,
        monthly_production: List[float],
        monthly_consumption: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate grid independence metrics with battery storage
        
        Returns self-sufficiency rate, autarky level, and grid dependency
        """
        results = []
        annual_self_consumption = 0
        annual_grid_import = 0
        annual_battery_contribution = 0
        
        for month in range(12):
            production = monthly_production[month]
            consumption = monthly_consumption[month]
            
            # Direct self-consumption (without battery)
            direct_self_consumption = min(production, consumption)
            
            # Surplus that can be stored
            surplus = max(0, production - consumption)
            storable_energy = min(
                surplus,
                battery_specs.usable_capacity_kwh * 30  # Approximate monthly cycles
            ) * battery_specs.efficiency
            
            # Additional self-consumption from battery
            remaining_consumption = consumption - direct_self_consumption
            battery_contribution = min(storable_energy, remaining_consumption)
            
            # Grid import needed
            grid_import = max(0, consumption - direct_self_consumption - battery_contribution)
            
            # Calculate metrics
            total_self_consumption = direct_self_consumption + battery_contribution
            self_sufficiency = (total_self_consumption / consumption * 100) if consumption > 0 else 0
            
            annual_self_consumption += total_self_consumption
            annual_grid_import += grid_import
            annual_battery_contribution += battery_contribution
            
            results.append({
                'month': month + 1,
                'production_kwh': round(production, 2),
                'consumption_kwh': round(consumption, 2),
                'direct_self_consumption_kwh': round(direct_self_consumption, 2),
                'battery_contribution_kwh': round(battery_contribution, 2),
                'grid_import_kwh': round(grid_import, 2),
                'self_sufficiency_percent': round(self_sufficiency, 1)
            })
        
        # Annual metrics
        total_consumption = sum(monthly_consumption)
        annual_self_sufficiency = (annual_self_consumption / total_consumption * 100) if total_consumption > 0 else 0
        grid_dependency = (annual_grid_import / total_consumption * 100) if total_consumption > 0 else 0
        battery_impact = (annual_battery_contribution / total_consumption * 100) if total_consumption > 0 else 0
        
        # Without battery comparison
        without_battery_self_consumption = sum(min(p, c) for p, c in zip(monthly_production, monthly_consumption))
        without_battery_self_sufficiency = (without_battery_self_consumption / total_consumption * 100) if total_consumption > 0 else 0
        improvement = annual_self_sufficiency - without_battery_self_sufficiency
        
        return {
            'monthly_analysis': results,
            'annual_metrics': {
                'self_sufficiency_percent': round(annual_self_sufficiency, 1),
                'grid_dependency_percent': round(grid_dependency, 1),
                'battery_contribution_percent': round(battery_impact, 1),
                'total_self_consumption_kwh': round(annual_self_consumption, 2),
                'total_grid_import_kwh': round(annual_grid_import, 2),
                'total_battery_contribution_kwh': round(annual_battery_contribution, 2)
            },
            'comparison': {
                'without_battery_self_sufficiency_percent': round(without_battery_self_sufficiency, 1),
                'with_battery_self_sufficiency_percent': round(annual_self_sufficiency, 1),
                'improvement_percent': round(improvement, 1)
            }
        }
    
    def calculate_lifecycle_analysis(
        self,
        battery_specs: BatterySpecs,
        daily_cycles: float = 1.0,
        analysis_years: int = 20
    ) -> Dict[str, Any]:
        """
        Calculate battery lifecycle analysis including degradation and replacement
        
        Returns capacity over time, cycle life, and replacement schedule
        """
        # Calculate total cycles over lifetime
        cycles_per_year = daily_cycles * 365
        total_cycles = cycles_per_year * analysis_years
        
        # Determine replacement schedule
        replacements = []
        current_cycles = 0
        replacement_year = 0
        
        while current_cycles < total_cycles:
            current_cycles += battery_specs.warranty_cycles
            replacement_year = int(current_cycles / cycles_per_year)
            if replacement_year < analysis_years:
                replacements.append({
                    'year': replacement_year,
                    'cycles_completed': current_cycles,
                    'replacement_cost': round(battery_specs.capacity_kwh * battery_specs.cost_per_kwh, 2)
                })
        
        # Calculate capacity degradation over time
        capacity_timeline = []
        for year in range(analysis_years + 1):
            # Calendar degradation
            calendar_degradation = (1 - battery_specs.degradation_rate_per_year) ** year
            
            # Cycle degradation (simplified model)
            cycles_completed = year * cycles_per_year
            cycle_degradation = 1 - (cycles_completed / battery_specs.warranty_cycles) * 0.2  # 20% degradation at warranty cycles
            cycle_degradation = max(0.8, cycle_degradation)  # Minimum 80% capacity
            
            # Combined degradation (use worst case)
            total_degradation = min(calendar_degradation, cycle_degradation)
            remaining_capacity = battery_specs.capacity_kwh * total_degradation
            
            capacity_timeline.append({
                'year': year,
                'capacity_kwh': round(remaining_capacity, 2),
                'capacity_percent': round(total_degradation * 100, 1),
                'cycles_completed': int(cycles_completed),
                'usable_capacity_kwh': round(remaining_capacity * battery_specs.depth_of_discharge, 2)
            })
        
        # Calculate total cost of ownership
        initial_cost = battery_specs.capacity_kwh * battery_specs.cost_per_kwh
        replacement_costs = sum(r['replacement_cost'] for r in replacements)
        total_cost = initial_cost + replacement_costs
        
        # Estimate maintenance costs (1% of initial cost per year)
        annual_maintenance = initial_cost * 0.01
        total_maintenance = annual_maintenance * analysis_years
        
        return {
            'battery_specs': battery_specs.dict(),
            'lifecycle_parameters': {
                'daily_cycles': daily_cycles,
                'cycles_per_year': round(cycles_per_year, 0),
                'total_cycles': int(total_cycles),
                'warranty_cycles': battery_specs.warranty_cycles,
                'warranty_years': battery_specs.warranty_years
            },
            'capacity_timeline': capacity_timeline,
            'replacement_schedule': replacements,
            'cost_analysis': {
                'initial_cost': round(initial_cost, 2),
                'replacement_costs': round(replacement_costs, 2),
                'maintenance_costs': round(total_maintenance, 2),
                'total_cost_of_ownership': round(total_cost + total_maintenance, 2),
                'cost_per_year': round((total_cost + total_maintenance) / analysis_years, 2)
            },
            'end_of_life': {
                'final_capacity_percent': capacity_timeline[-1]['capacity_percent'],
                'total_cycles_completed': capacity_timeline[-1]['cycles_completed'],
                'years_of_service': analysis_years
            }
        }
    
    def get_monitoring_integration_config(
        self,
        battery_specs: BatterySpecs,
        monitoring_system: str = 'generic'
    ) -> Dict[str, Any]:
        """
        Generate monitoring integration configuration
        
        Returns API endpoints, data points, and alert thresholds
        """
        # Define monitoring data points
        data_points = {
            'real_time': [
                {'name': 'state_of_charge', 'unit': '%', 'update_interval_seconds': 5},
                {'name': 'power_flow', 'unit': 'kW', 'update_interval_seconds': 5},
                {'name': 'voltage', 'unit': 'V', 'update_interval_seconds': 10},
                {'name': 'current', 'unit': 'A', 'update_interval_seconds': 10},
                {'name': 'temperature', 'unit': '°C', 'update_interval_seconds': 30}
            ],
            'historical': [
                {'name': 'daily_cycles', 'unit': 'cycles', 'aggregation': 'sum'},
                {'name': 'energy_charged', 'unit': 'kWh', 'aggregation': 'sum'},
                {'name': 'energy_discharged', 'unit': 'kWh', 'aggregation': 'sum'},
                {'name': 'efficiency', 'unit': '%', 'aggregation': 'average'},
                {'name': 'capacity_remaining', 'unit': '%', 'aggregation': 'latest'}
            ],
            'lifecycle': [
                {'name': 'total_cycles', 'unit': 'cycles', 'aggregation': 'cumulative'},
                {'name': 'total_energy_throughput', 'unit': 'kWh', 'aggregation': 'cumulative'},
                {'name': 'capacity_degradation', 'unit': '%', 'aggregation': 'latest'},
                {'name': 'warranty_status', 'unit': '%', 'aggregation': 'calculated'}
            ]
        }
        
        # Define alert thresholds
        alert_thresholds = {
            'critical': [
                {'parameter': 'state_of_charge', 'condition': '<', 'value': 10, 'message': 'Battery critically low'},
                {'parameter': 'temperature', 'condition': '>', 'value': 50, 'message': 'Battery overheating'},
                {'parameter': 'voltage', 'condition': '<', 'value': battery_specs.capacity_kwh * 40, 'message': 'Low voltage detected'}
            ],
            'warning': [
                {'parameter': 'state_of_charge', 'condition': '<', 'value': 20, 'message': 'Battery low'},
                {'parameter': 'temperature', 'condition': '>', 'value': 40, 'message': 'Battery temperature elevated'},
                {'parameter': 'efficiency', 'condition': '<', 'value': 85, 'message': 'Battery efficiency degraded'},
                {'parameter': 'capacity_remaining', 'condition': '<', 'value': 80, 'message': 'Battery capacity degraded'}
            ],
            'info': [
                {'parameter': 'daily_cycles', 'condition': '>', 'value': 2, 'message': 'High battery usage'},
                {'parameter': 'total_cycles', 'condition': '>', 'value': battery_specs.warranty_cycles * 0.8, 'message': 'Approaching warranty cycle limit'}
            ]
        }
        
        # System-specific configuration
        system_configs = {
            'generic': {
                'api_endpoint': '/api/v1/battery/monitoring',
                'protocol': 'REST',
                'authentication': 'API_KEY',
                'data_format': 'JSON'
            },
            'tesla_powerwall': {
                'api_endpoint': 'https://powerwall.local/api',
                'protocol': 'REST',
                'authentication': 'TOKEN',
                'data_format': 'JSON'
            },
            'sonnen_battery': {
                'api_endpoint': 'https://sonnenbatterie.local:8080/api',
                'protocol': 'REST',
                'authentication': 'TOKEN',
                'data_format': 'JSON'
            },
            'lg_resu': {
                'api_endpoint': '/api/v1/battery/lg',
                'protocol': 'MODBUS_TCP',
                'authentication': 'NONE',
                'data_format': 'BINARY'
            }
        }
        
        return {
            'battery_specs': battery_specs.dict(),
            'monitoring_system': monitoring_system,
            'configuration': system_configs.get(monitoring_system, system_configs['generic']),
            'data_points': data_points,
            'alert_thresholds': alert_thresholds,
            'recommended_polling_intervals': {
                'real_time_data': '5 seconds',
                'historical_data': '15 minutes',
                'lifecycle_data': '1 day'
            },
            'integration_endpoints': {
                'get_status': '/api/v1/battery/status',
                'get_history': '/api/v1/battery/history',
                'get_lifecycle': '/api/v1/battery/lifecycle',
                'set_strategy': '/api/v1/battery/strategy',
                'get_alerts': '/api/v1/battery/alerts'
            }
        }
    
    # Helper methods
    
    def _select_battery_category(self, capacity_kwh: float) -> str:
        """Select appropriate battery category based on capacity"""
        if capacity_kwh <= 7:
            return 'small'
        elif capacity_kwh <= 12:
            return 'medium'
        else:
            return 'large'
    
    def _calculate_battery_performance(
        self,
        battery_specs: BatterySpecs,
        request: BatterySizingRequest,
        daily_surplus: float,
        daily_deficit: float
    ) -> Dict[str, Any]:
        """Calculate expected battery performance metrics"""
        # Energy that can be stored daily
        storable_energy = min(daily_surplus, battery_specs.usable_capacity_kwh)
        
        # Energy that can be used from battery
        usable_energy = storable_energy * battery_specs.efficiency
        
        # Additional self-consumption from battery
        additional_self_consumption = min(usable_energy, daily_deficit)
        
        # New self-consumption rate
        total_self_consumption = (request.annual_production_kwh / 365) * request.self_consumption_rate + additional_self_consumption
        new_self_consumption_rate = total_self_consumption / (request.annual_production_kwh / 365)
        
        # Cycles per day
        cycles_per_day = storable_energy / battery_specs.usable_capacity_kwh
        
        return {
            'storable_energy_per_day_kwh': round(storable_energy, 2),
            'usable_energy_per_day_kwh': round(usable_energy, 2),
            'additional_self_consumption_kwh': round(additional_self_consumption, 2),
            'new_self_consumption_rate_percent': round(new_self_consumption_rate * 100, 1),
            'improvement_percent': round((new_self_consumption_rate - request.self_consumption_rate) * 100, 1),
            'cycles_per_day': round(cycles_per_day, 2),
            'annual_cycles': round(cycles_per_day * 365, 0)
        }
    
    def _self_consumption_strategy(
        self,
        net_energy: float,
        soc: float,
        battery_specs: BatterySpecs,
        strategy: DischargeStrategy
    ) -> Dict[str, str]:
        """Self-consumption optimization strategy"""
        if net_energy > 0:  # Surplus - charge battery
            return {'type': 'charge', 'amount': net_energy}
        else:  # Deficit - discharge battery
            return {'type': 'discharge', 'amount': abs(net_energy)}
    
    def _peak_shaving_strategy(
        self,
        hour: int,
        net_energy: float,
        soc: float,
        battery_specs: BatterySpecs,
        strategy: DischargeStrategy
    ) -> Dict[str, str]:
        """Peak shaving strategy - discharge during peak hours"""
        is_peak_hour = hour in (strategy.peak_hours or [17, 18, 19, 20])
        
        if is_peak_hour and net_energy < 0:
            # Discharge during peak hours to reduce grid import
            return {'type': 'discharge', 'amount': abs(net_energy)}
        elif not is_peak_hour and net_energy > 0:
            # Charge during off-peak hours
            return {'type': 'charge', 'amount': net_energy}
        else:
            return {'type': 'idle', 'amount': 0}
    
    def _time_of_use_strategy(
        self,
        hour: int,
        net_energy: float,
        soc: float,
        battery_specs: BatterySpecs,
        strategy: DischargeStrategy
    ) -> Dict[str, str]:
        """Time-of-use optimization - charge when cheap, discharge when expensive"""
        # Assume peak hours have higher electricity prices
        is_peak_hour = hour in (strategy.peak_hours or [17, 18, 19, 20])
        
        if is_peak_hour:
            # Discharge during expensive hours
            if net_energy < 0:
                return {'type': 'discharge', 'amount': abs(net_energy)}
            else:
                return {'type': 'idle', 'amount': 0}
        else:
            # Charge during cheap hours
            if net_energy > 0:
                return {'type': 'charge', 'amount': net_energy}
            else:
                # Only discharge if necessary
                if soc > 0.8:  # High SOC, can discharge
                    return {'type': 'discharge', 'amount': abs(net_energy)}
                else:
                    return {'type': 'idle', 'amount': 0}
    
    def _backup_strategy(
        self,
        net_energy: float,
        soc: float,
        battery_specs: BatterySpecs,
        strategy: DischargeStrategy
    ) -> Dict[str, str]:
        """Backup strategy - maintain high SOC for emergency backup"""
        target_soc = 0.9  # Keep battery at 90% for backup
        
        if soc < target_soc and net_energy > 0:
            # Charge to maintain backup capacity
            return {'type': 'charge', 'amount': net_energy}
        elif soc > target_soc and net_energy < 0:
            # Only discharge if above target SOC
            return {'type': 'discharge', 'amount': abs(net_energy)}
        else:
            return {'type': 'idle', 'amount': 0}
