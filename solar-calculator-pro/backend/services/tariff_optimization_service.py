"""
Dynamic Tariff Optimization Service for Heat Pumps
"""

import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, time, timedelta
from ..models.tariff_schemas import (
    TariffStructure, TariffType, HeatingSchedule, OptimizationRequest,
    OptimizedSchedule, OptimizationResult, TariffComparison, DemandResponseEvent,
    RealTimeTariffData
)


class TariffOptimizationService:
    """Service for optimizing heat pump operation based on dynamic tariffs"""
    
    def __init__(self):
        self.hours_per_day = 24
        self.days_per_year = 365
    
    def optimize_schedule(self, request: OptimizationRequest) -> OptimizationResult:
        """
        Optimize heating schedule based on tariff structure
        
        Args:
            request: Optimization request with tariff and heating parameters
            
        Returns:
            OptimizationResult with optimized schedule and savings
        """
        # Calculate original cost
        original_cost = self._calculate_original_cost(request)
        
        # Generate optimized schedule
        optimized_schedule = self._generate_optimized_schedule(request)
        
        # Calculate optimized cost
        optimized_cost = sum(slot.cost for slot in optimized_schedule)
        
        # Calculate annual costs
        daily_original = original_cost
        daily_optimized = optimized_cost
        annual_original = daily_original * self.days_per_year
        annual_optimized = daily_optimized * self.days_per_year
        
        # Calculate savings
        savings = annual_original - annual_optimized
        savings_percent = (savings / annual_original * 100) if annual_original > 0 else 0
        
        # Calculate peak load reduction
        peak_reduction = self._calculate_peak_reduction(
            request.current_schedule, optimized_schedule
        )
        
        # Calculate comfort score
        comfort_score = self._calculate_comfort_score(
            request.current_schedule, optimized_schedule, request.comfort_priority
        )
        
        return OptimizationResult(
            original_cost=annual_original,
            optimized_cost=annual_optimized,
            savings=savings,
            savings_percent=savings_percent,
            optimized_schedule=optimized_schedule,
            peak_load_reduction=peak_reduction,
            comfort_score=comfort_score
        )
    
    def _calculate_original_cost(self, request: OptimizationRequest) -> float:
        """Calculate cost with original schedule"""
        total_cost = 0.0
        
        for schedule_item in request.current_schedule:
            # Get tariff rate for this hour
            rate = self._get_tariff_rate(
                request.tariff_structure, schedule_item.hour
            )
            
            # Estimate consumption for this hour
            consumption = self._estimate_hourly_consumption(
                request.annual_heating_demand,
                schedule_item.target_temperature,
                request.heat_pump_cop
            )
            
            total_cost += consumption * rate
        
        return total_cost
    
    def _generate_optimized_schedule(
        self, request: OptimizationRequest
    ) -> List[OptimizedSchedule]:
        """Generate optimized heating schedule"""
        optimized = []
        
        # Get hourly tariff rates
        hourly_rates = [
            self._get_tariff_rate(request.tariff_structure, hour)
            for hour in range(self.hours_per_day)
        ]
        
        # Sort hours by tariff rate (cheapest first)
        sorted_hours = sorted(
            range(self.hours_per_day), key=lambda h: hourly_rates[h]
        )
        
        # Create schedule prioritizing cheap hours
        for hour in range(self.hours_per_day):
            # Find original schedule for this hour
            original = next(
                (s for s in request.current_schedule if s.hour == hour),
                None
            )
            
            if original:
                # Determine if we should shift this heating period
                should_shift = (
                    original.flexible and
                    hourly_rates[hour] > np.median(hourly_rates) and
                    request.comfort_priority < 0.8
                )
                
                if should_shift:
                    # Find cheaper alternative hour
                    shifted_hour = self._find_alternative_hour(
                        hour, sorted_hours, hourly_rates, request
                    )
                    target_temp = original.target_temperature
                    shifted_from = hour
                    actual_hour = shifted_hour
                else:
                    target_temp = original.target_temperature
                    shifted_from = None
                    actual_hour = hour
                
                # Calculate consumption and cost
                consumption = self._estimate_hourly_consumption(
                    request.annual_heating_demand,
                    target_temp,
                    request.heat_pump_cop
                )
                
                rate = hourly_rates[actual_hour]
                cost = consumption * rate
                
                optimized.append(OptimizedSchedule(
                    hour=actual_hour,
                    target_temperature=target_temp,
                    estimated_consumption=consumption,
                    tariff_rate=rate,
                    cost=cost,
                    shifted_from=shifted_from
                ))
        
        return sorted(optimized, key=lambda x: x.hour)
    
    def _get_tariff_rate(self, tariff: TariffStructure, hour: int) -> float:
        """Get tariff rate for specific hour"""
        if tariff.type == TariffType.FLAT_RATE:
            return tariff.base_rate
        
        # For time-of-use tariffs, find matching period
        hour_time = time(hour=hour)
        
        for period in tariff.periods:
            if self._is_time_in_period(hour_time, period.start_time, period.end_time):
                return period.rate
        
        return tariff.base_rate
    
    def _is_time_in_period(self, check_time: time, start: time, end: time) -> bool:
        """Check if time falls within period"""
        if start <= end:
            return start <= check_time < end
        else:  # Period crosses midnight
            return check_time >= start or check_time < end
    
    def _estimate_hourly_consumption(
        self, annual_demand: float, target_temp: float, cop: float
    ) -> float:
        """Estimate hourly consumption based on target temperature"""
        # Base hourly consumption
        base_hourly = annual_demand / (self.hours_per_day * self.days_per_year)
        
        # Adjust for temperature (higher temp = more consumption)
        temp_factor = 1.0 + (target_temp - 20.0) * 0.05
        
        # Adjust for COP
        electrical_consumption = (base_hourly * temp_factor) / cop
        
        return max(0, electrical_consumption)
    
    def _find_alternative_hour(
        self, original_hour: int, sorted_hours: List[int],
        hourly_rates: List[float], request: OptimizationRequest
    ) -> int:
        """Find alternative cheaper hour for heating"""
        # Look for hours within ±3 hours window (thermal mass allows shifting)
        window = 3
        candidates = [
            h for h in sorted_hours
            if abs(h - original_hour) <= window and hourly_rates[h] < hourly_rates[original_hour]
        ]
        
        return candidates[0] if candidates else original_hour
    
    def _calculate_peak_reduction(
        self, original: List[HeatingSchedule], optimized: List[OptimizedSchedule]
    ) -> float:
        """Calculate peak load reduction"""
        # Find peak consumption in original schedule
        original_peak = max(
            self._estimate_hourly_consumption(1000, s.target_temperature, 3.0)
            for s in original
        )
        
        # Find peak consumption in optimized schedule
        optimized_peak = max(s.estimated_consumption for s in optimized)
        
        return max(0, original_peak - optimized_peak)
    
    def _calculate_comfort_score(
        self, original: List[HeatingSchedule], optimized: List[OptimizedSchedule],
        comfort_priority: float
    ) -> float:
        """Calculate comfort score (0-1)"""
        # Count how many hours were shifted
        shifted_count = sum(1 for s in optimized if s.shifted_from is not None)
        total_count = len(optimized)
        
        # Calculate score based on shifts and comfort priority
        shift_penalty = shifted_count / total_count if total_count > 0 else 0
        comfort_score = 1.0 - (shift_penalty * (1.0 - comfort_priority))
        
        return max(0.0, min(1.0, comfort_score))
    
    def compare_tariffs(
        self, tariffs: List[TariffStructure], heating_profile: Dict
    ) -> List[TariffComparison]:
        """Compare different tariff options"""
        comparisons = []
        
        for tariff in tariffs:
            # Calculate annual cost for this tariff
            annual_cost = self._calculate_tariff_cost(tariff, heating_profile)
            
            # Find baseline (flat rate) for comparison
            baseline_cost = self._calculate_baseline_cost(heating_profile)
            
            # Calculate potential savings
            savings = baseline_cost - annual_cost
            
            # Determine pros and cons
            pros, cons = self._analyze_tariff(tariff)
            
            comparisons.append(TariffComparison(
                tariff_name=tariff.name,
                tariff_type=tariff.type,
                annual_cost=annual_cost,
                potential_savings=savings,
                recommended=savings > 0 and tariff.type == TariffType.TIME_OF_USE,
                pros=pros,
                cons=cons
            ))
        
        return sorted(comparisons, key=lambda x: x.annual_cost)
    
    def _calculate_tariff_cost(
        self, tariff: TariffStructure, heating_profile: Dict
    ) -> float:
        """Calculate annual cost for specific tariff"""
        daily_cost = 0.0
        
        for hour in range(self.hours_per_day):
            rate = self._get_tariff_rate(tariff, hour)
            consumption = heating_profile.get(hour, 0)
            daily_cost += consumption * rate
        
        return daily_cost * self.days_per_year
    
    def _calculate_baseline_cost(self, heating_profile: Dict) -> float:
        """Calculate baseline cost with flat rate"""
        total_consumption = sum(heating_profile.values())
        avg_rate = 0.30  # EUR/kWh baseline
        return total_consumption * avg_rate * self.days_per_year
    
    def _analyze_tariff(self, tariff: TariffStructure) -> Tuple[List[str], List[str]]:
        """Analyze tariff pros and cons"""
        pros = []
        cons = []
        
        if tariff.type == TariffType.TIME_OF_USE:
            pros.append("Predictable rates with clear peak/off-peak periods")
            pros.append("Good savings potential with flexible heating schedule")
            cons.append("Requires schedule adjustment")
        
        elif tariff.type == TariffType.DYNAMIC:
            pros.append("Maximum savings potential")
            pros.append("Rewards flexible consumption")
            cons.append("Rates can vary significantly")
            cons.append("Requires active monitoring")
        
        elif tariff.type == TariffType.FLAT_RATE:
            pros.append("Simple and predictable")
            pros.append("No schedule optimization needed")
            cons.append("No savings from load shifting")
        
        return pros, cons
    
    def process_demand_response(
        self, event: DemandResponseEvent, current_schedule: List[HeatingSchedule]
    ) -> Dict:
        """Process demand response event and adjust schedule"""
        # Calculate current load during event period
        event_hours = self._get_event_hours(event)
        current_load = sum(
            self._estimate_hourly_consumption(1000, s.target_temperature, 3.0)
            for s in current_schedule if s.hour in event_hours
        )
        
        # Calculate required reduction
        reduction_needed = event.required_reduction
        
        # Determine if we can participate
        can_participate = current_load >= reduction_needed
        
        # Generate adjusted schedule
        adjusted_schedule = []
        if can_participate:
            for schedule_item in current_schedule:
                if schedule_item.hour in event_hours and schedule_item.flexible:
                    # Reduce temperature during event
                    adjusted_schedule.append({
                        'hour': schedule_item.hour,
                        'target_temperature': schedule_item.target_temperature - 2.0,
                        'reduced': True
                    })
                else:
                    adjusted_schedule.append({
                        'hour': schedule_item.hour,
                        'target_temperature': schedule_item.target_temperature,
                        'reduced': False
                    })
        
        # Calculate incentive earnings
        duration_hours = len(event_hours)
        incentive_earnings = reduction_needed * duration_hours * event.incentive_rate
        
        return {
            'can_participate': can_participate,
            'current_load': current_load,
            'reduction_achieved': reduction_needed if can_participate else 0,
            'adjusted_schedule': adjusted_schedule,
            'incentive_earnings': incentive_earnings if can_participate else 0,
            'recommendation': 'participate' if can_participate else 'skip'
        }
    
    def _get_event_hours(self, event: DemandResponseEvent) -> List[int]:
        """Get list of hours covered by event"""
        hours = []
        current = event.start_time
        while current < event.end_time:
            hours.append(current.hour)
            current += timedelta(hours=1)
        return hours
    
    def monitor_real_time_tariff(
        self, tariff_data: RealTimeTariffData, current_schedule: List[HeatingSchedule]
    ) -> Dict:
        """Monitor real-time tariff and provide recommendations"""
        current_rate = tariff_data.current_rate
        avg_forecast = np.mean(tariff_data.forecast_next_24_hours)
        
        # Determine if current rate is favorable
        is_cheap = current_rate < avg_forecast * 0.8
        is_expensive = current_rate > avg_forecast * 1.2
        
        # Generate recommendation
        if is_cheap:
            recommendation = "Increase heating now - rates are favorable"
            action = "increase_temperature"
        elif is_expensive:
            recommendation = "Reduce heating now - rates are high"
            action = "reduce_temperature"
        else:
            recommendation = "Maintain current schedule"
            action = "maintain"
        
        # Find optimal hours in next 24 hours
        optimal_hours = self._find_optimal_hours(tariff_data.forecast_next_24_hours)
        
        return {
            'current_rate': current_rate,
            'average_forecast': avg_forecast,
            'is_favorable': is_cheap,
            'recommendation': recommendation,
            'action': action,
            'optimal_hours_next_24h': optimal_hours,
            'grid_load_level': tariff_data.grid_load_level,
            'savings_opportunity': abs(current_rate - avg_forecast) * 10  # EUR per 10 kWh
        }
    
    def _find_optimal_hours(self, forecast: List[float]) -> List[int]:
        """Find optimal hours for heating based on forecast"""
        # Get indices of cheapest 8 hours
        sorted_indices = sorted(range(len(forecast)), key=lambda i: forecast[i])
        return sorted(sorted_indices[:8])
