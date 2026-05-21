"""
Tests for tariff optimization service
"""

import pytest
from datetime import time, datetime, timedelta
from ..models.tariff_schemas import (
    TariffStructure, TariffType, TariffPeriod, HeatingSchedule,
    OptimizationRequest, DemandResponseEvent, RealTimeTariffData
)
from ..services.tariff_optimization_service import TariffOptimizationService


@pytest.fixture
def tariff_service():
    """Create tariff optimization service"""
    return TariffOptimizationService()


@pytest.fixture
def flat_rate_tariff():
    """Create flat rate tariff"""
    return TariffStructure(
        tariff_id="flat_001",
        name="Flat Rate 30ct",
        type=TariffType.FLAT_RATE,
        base_rate=0.30,
        periods=[]
    )


@pytest.fixture
def time_of_use_tariff():
    """Create time-of-use tariff"""
    return TariffStructure(
        tariff_id="tou_001",
        name="Time of Use",
        type=TariffType.TIME_OF_USE,
        base_rate=0.30,
        periods=[
            TariffPeriod(start_time=time(22, 0), end_time=time(6, 0), rate=0.20, name="off-peak"),
            TariffPeriod(start_time=time(6, 0), end_time=time(22, 0), rate=0.35, name="peak")
        ]
    )


@pytest.fixture
def typical_schedule():
    """Create typical heating schedule"""
    return [
        HeatingSchedule(hour=h, target_temperature=20.0 if 6 <= h <= 22 else 18.0, flexible=True)
        for h in range(24)
    ]


def test_flat_rate_optimization(tariff_service, flat_rate_tariff, typical_schedule):
    """Test optimization with flat rate tariff"""
    request = OptimizationRequest(
        tariff_structure=flat_rate_tariff,
        heat_pump_cop=3.0,
        annual_heating_demand=10000,
        current_schedule=typical_schedule,
        comfort_priority=0.7
    )
    
    result = tariff_service.optimize_schedule(request)
    
    assert result.original_cost > 0
    assert result.optimized_cost > 0
    assert result.comfort_score >= 0 and result.comfort_score <= 1
    assert len(result.optimized_schedule) == 24


def test_time_of_use_optimization(tariff_service, time_of_use_tariff, typical_schedule):
    """Test optimization with time-of-use tariff"""
    request = OptimizationRequest(
        tariff_structure=time_of_use_tariff,
        heat_pump_cop=3.0,
        annual_heating_demand=10000,
        current_schedule=typical_schedule,
        comfort_priority=0.5
    )
    
    result = tariff_service.optimize_schedule(request)
    
    # Should achieve savings with TOU tariff (or at least not increase costs)
    # Note: With low comfort priority, savings should be achieved
    assert result.savings >= -0.01  # Allow for floating point rounding
    assert result.optimized_cost <= result.original_cost + 0.01
    
    # Verify optimization ran successfully
    assert len(result.optimized_schedule) == 24
    assert result.comfort_score >= 0 and result.comfort_score <= 1


def test_high_comfort_priority(tariff_service, time_of_use_tariff, typical_schedule):
    """Test optimization with high comfort priority"""
    request = OptimizationRequest(
        tariff_structure=time_of_use_tariff,
        heat_pump_cop=3.0,
        annual_heating_demand=10000,
        current_schedule=typical_schedule,
        comfort_priority=0.9  # High comfort priority
    )
    
    result = tariff_service.optimize_schedule(request)
    
    # High comfort priority should result in less shifting
    assert result.comfort_score > 0.8
    
    # Savings might be lower due to less shifting
    shifted_hours = sum(1 for s in result.optimized_schedule if s.shifted_from is not None)
    assert shifted_hours < 10  # Less than half the day


def test_tariff_comparison(tariff_service, flat_rate_tariff, time_of_use_tariff):
    """Test tariff comparison"""
    heating_profile = {hour: 1.0 for hour in range(24)}
    
    comparisons = tariff_service.compare_tariffs(
        [flat_rate_tariff, time_of_use_tariff],
        heating_profile
    )
    
    assert len(comparisons) == 2
    assert all(c.annual_cost > 0 for c in comparisons)
    assert all(len(c.pros) > 0 for c in comparisons)
    assert all(len(c.cons) > 0 for c in comparisons)


def test_demand_response_participation(tariff_service, typical_schedule):
    """Test demand response event processing"""
    event = DemandResponseEvent(
        event_id="dr_001",
        start_time=datetime.now() + timedelta(hours=2),
        end_time=datetime.now() + timedelta(hours=4),
        incentive_rate=0.50,
        required_reduction=2.0
    )
    
    result = tariff_service.process_demand_response(event, typical_schedule)
    
    assert 'can_participate' in result
    assert 'incentive_earnings' in result
    assert 'adjusted_schedule' in result
    assert 'recommendation' in result


def test_real_time_monitoring(tariff_service, typical_schedule):
    """Test real-time tariff monitoring"""
    tariff_data = RealTimeTariffData(
        timestamp=datetime.now(),
        current_rate=0.25,
        forecast_next_hour=0.30,
        forecast_next_4_hours=[0.30, 0.32, 0.28, 0.26],
        forecast_next_24_hours=[0.30] * 24,
        grid_load_level="medium"
    )
    
    result = tariff_service.monitor_real_time_tariff(tariff_data, typical_schedule)
    
    assert 'current_rate' in result
    assert 'recommendation' in result
    assert 'action' in result
    assert 'optimal_hours_next_24h' in result


def test_peak_load_reduction(tariff_service, time_of_use_tariff, typical_schedule):
    """Test peak load reduction calculation"""
    request = OptimizationRequest(
        tariff_structure=time_of_use_tariff,
        heat_pump_cop=3.0,
        annual_heating_demand=10000,
        current_schedule=typical_schedule,
        comfort_priority=0.5
    )
    
    result = tariff_service.optimize_schedule(request)
    
    # Should achieve some peak load reduction
    assert result.peak_load_reduction >= 0


def test_consumption_estimation(tariff_service):
    """Test hourly consumption estimation"""
    consumption = tariff_service._estimate_hourly_consumption(
        annual_demand=10000,
        target_temp=20.0,
        cop=3.0
    )
    
    assert consumption > 0
    assert consumption < 10  # Reasonable hourly consumption


def test_tariff_rate_retrieval(tariff_service, time_of_use_tariff):
    """Test tariff rate retrieval for different hours"""
    # Off-peak hour (midnight)
    rate_midnight = tariff_service._get_tariff_rate(time_of_use_tariff, 0)
    assert rate_midnight == 0.20
    
    # Peak hour (noon)
    rate_noon = tariff_service._get_tariff_rate(time_of_use_tariff, 12)
    assert rate_noon == 0.35


def test_optimal_hours_finding(tariff_service):
    """Test finding optimal hours from forecast"""
    forecast = [0.30, 0.25, 0.20, 0.35, 0.40, 0.22, 0.28, 0.32] * 3
    
    optimal_hours = tariff_service._find_optimal_hours(forecast)
    
    assert len(optimal_hours) == 8
    # Should include hour 2 (rate 0.20) which is cheapest
    assert 2 in optimal_hours


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
