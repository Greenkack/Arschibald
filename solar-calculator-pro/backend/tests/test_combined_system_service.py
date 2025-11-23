"""
Tests for Combined Heat Pump + PV System Integration Service.
"""

import pytest
from services.combined_system_service import CombinedSystemService
from models.combined_system_schemas import (
    CombinedSystemRequest,
    ControlStrategy,
    TimeOfUseProfile,
    OptimizationRequest
)


@pytest.fixture
def service():
    """Create service instance"""
    return CombinedSystemService()


@pytest.fixture
def basic_request():
    """Create basic test request"""
    return CombinedSystemRequest(
        pv_system_size=10.0,
        pv_annual_production=10000.0,
        pv_module_count=30,
        pv_orientation="south",
        pv_tilt_angle=30.0,
        hp_model="Test Heat Pump",
        hp_cop=4.0,
        hp_heating_capacity=8.0,
        hp_power_consumption=2.0,
        annual_heating_demand=12000.0,
        building_insulation_quality="good",
        battery_capacity=10.0,
        battery_efficiency=0.95,
        electricity_price=0.30,
        feed_in_tariff=0.08,
        control_strategy=ControlStrategy.SELF_CONSUMPTION,
        location="Berlin",
        latitude=52.52,
        longitude=13.40
    )


class TestCombinedSystemAnalysis:
    """Test combined system analysis"""
    
    def test_basic_analysis(self, service, basic_request):
        """Test basic system analysis"""
        result = service.analyze_combined_system(basic_request)
        
        assert result is not None
        assert result.self_consumption_rate > 0
        assert result.self_consumption_rate <= 1
        assert result.grid_independence_rate > 0
        assert result.grid_independence_rate <= 1
        assert result.financial_analysis.total_investment > 0
        assert result.financial_analysis.annual_savings > 0
    
    def test_synergy_calculation(self, service, basic_request):
        """Test synergy analysis"""
        result = service.analyze_combined_system(basic_request)
        synergy = result.synergy_analysis
        
        assert synergy.pv_to_hp_direct >= 0
        assert synergy.pv_to_hp_via_battery >= 0
        assert synergy.total_pv_for_heating >= 0
        assert synergy.heating_cost_reduction >= 0
        assert synergy.cop_improvement >= 0
        assert 0 <= synergy.grid_independence_heating <= 100
    
    def test_financial_analysis(self, service, basic_request):
        """Test financial analysis"""
        result = service.analyze_combined_system(basic_request)
        financial = result.financial_analysis
        
        assert financial.total_investment > 0
        assert financial.pv_system_cost > 0
        assert financial.heat_pump_cost > 0
        assert financial.battery_cost >= 0
        assert financial.annual_savings > 0
        assert financial.simple_payback_years > 0
        assert financial.npv_20_years != 0
    
    def test_control_schedule_generation(self, service, basic_request):
        """Test smart control schedule generation"""
        result = service.analyze_combined_system(basic_request)
        schedule = result.smart_control_schedule
        
        assert len(schedule) == 24  # One day
        for entry in schedule:
            assert 0 <= entry.hour <= 23
            assert entry.hp_operation_mode in ["on", "off", "modulated"]
            assert 0 <= entry.hp_power_level <= 1
            assert len(entry.reason) > 0


class TestControlStrategies:
    """Test different control strategies"""
    
    def test_self_consumption_strategy(self, service, basic_request):
        """Test self-consumption strategy"""
        basic_request.control_strategy = ControlStrategy.SELF_CONSUMPTION
        result = service.analyze_combined_system(basic_request)
        
        # Self-consumption strategy should maximize self-consumption
        assert result.self_consumption_rate > 0.6
    
    def test_cost_optimization_strategy(self, service, basic_request):
        """Test cost optimization strategy"""
        basic_request.control_strategy = ControlStrategy.COST_OPTIMIZATION
        result = service.analyze_combined_system(basic_request)
        
        # Should produce valid results
        assert result.financial_analysis.annual_savings > 0
    
    def test_grid_independence_strategy(self, service, basic_request):
        """Test grid independence strategy"""
        basic_request.control_strategy = ControlStrategy.GRID_INDEPENDENCE
        result = service.analyze_combined_system(basic_request)
        
        # Grid independence strategy should minimize grid import
        assert result.grid_independence_rate > 0.5
    
    def test_balanced_strategy(self, service, basic_request):
        """Test balanced strategy"""
        basic_request.control_strategy = ControlStrategy.BALANCED
        result = service.analyze_combined_system(basic_request)
        
        # Should balance all factors
        assert result.self_consumption_rate > 0.5
        assert result.grid_independence_rate > 0.4


class TestBatteryIntegration:
    """Test battery storage integration"""
    
    def test_with_battery(self, service, basic_request):
        """Test system with battery"""
        basic_request.battery_capacity = 10.0
        result = service.analyze_combined_system(basic_request)
        
        # Battery should improve self-consumption
        assert result.self_consumption_rate > 0.6
        assert result.financial_analysis.battery_cost > 0
    
    def test_without_battery(self, service, basic_request):
        """Test system without battery"""
        basic_request.battery_capacity = None
        result = service.analyze_combined_system(basic_request)
        
        # Should still work without battery
        assert result.self_consumption_rate > 0
        assert result.financial_analysis.battery_cost == 0
    
    def test_battery_size_impact(self, service, basic_request):
        """Test impact of battery size"""
        # Small battery
        basic_request.battery_capacity = 5.0
        result_small = service.analyze_combined_system(basic_request)
        
        # Large battery
        basic_request.battery_capacity = 15.0
        result_large = service.analyze_combined_system(basic_request)
        
        # Larger battery should improve self-consumption
        assert result_large.self_consumption_rate >= result_small.self_consumption_rate


class TestTimeOfUseTariff:
    """Test time-of-use tariff optimization"""
    
    def test_with_tou_tariff(self, service, basic_request):
        """Test with time-of-use tariff"""
        tariff = [
            TimeOfUseProfile(hour=h, price_per_kwh=0.40, is_peak=True)
            for h in range(17, 21)
        ] + [
            TimeOfUseProfile(hour=h, price_per_kwh=0.20, is_peak=False)
            for h in range(0, 6)
        ] + [
            TimeOfUseProfile(hour=h, price_per_kwh=0.30, is_peak=False)
            for h in range(6, 17)
        ] + [
            TimeOfUseProfile(hour=h, price_per_kwh=0.30, is_peak=False)
            for h in range(21, 24)
        ]
        
        basic_request.time_of_use_tariff = tariff
        basic_request.control_strategy = ControlStrategy.COST_OPTIMIZATION
        result = service.analyze_combined_system(basic_request)
        
        # Should optimize for TOU tariff
        assert result.financial_analysis.annual_savings > 0


class TestPerformanceMetrics:
    """Test performance metric calculations"""
    
    def test_self_consumption_rate(self, service, basic_request):
        """Test self-consumption rate calculation"""
        result = service.analyze_combined_system(basic_request)
        
        assert 0 <= result.self_consumption_rate <= 1
        # With battery, should be > 60%
        assert result.self_consumption_rate > 0.6
    
    def test_grid_independence_rate(self, service, basic_request):
        """Test grid independence rate calculation"""
        result = service.analyze_combined_system(basic_request)
        
        assert 0 <= result.grid_independence_rate <= 1
        # Should achieve some independence
        assert result.grid_independence_rate > 0.4
    
    def test_renewable_energy_rate(self, service, basic_request):
        """Test renewable energy rate calculation"""
        result = service.analyze_combined_system(basic_request)
        
        assert 0 <= result.renewable_energy_rate <= 1
        # Should have significant renewable share
        assert result.renewable_energy_rate > 0.5


class TestEnvironmentalImpact:
    """Test environmental impact calculations"""
    
    def test_co2_savings(self, service, basic_request):
        """Test CO2 savings calculation"""
        result = service.analyze_combined_system(basic_request)
        
        assert result.annual_co2_savings > 0
        assert result.equivalent_trees_planted > 0
        # Typical system should save several tons of CO2
        assert result.annual_co2_savings > 1000


class TestComparisons:
    """Test scenario comparisons"""
    
    def test_pv_only_comparison(self, service, basic_request):
        """Test PV-only comparison"""
        result = service.analyze_combined_system(basic_request)
        
        assert result.comparison_pv_only['investment'] > 0
        assert result.comparison_pv_only['annual_savings'] > 0
        assert result.comparison_pv_only['payback_years'] > 0
    
    def test_hp_only_comparison(self, service, basic_request):
        """Test HP-only comparison"""
        result = service.analyze_combined_system(basic_request)
        
        assert result.comparison_hp_only['investment'] > 0
        assert result.comparison_hp_only['annual_savings'] > 0
        assert result.comparison_hp_only['payback_years'] > 0
    
    def test_synergy_benefit(self, service, basic_request):
        """Test synergy benefit calculation"""
        result = service.analyze_combined_system(basic_request)
        
        # Combined system should have synergy benefits
        assert result.synergy_benefit > 0


class TestOptimization:
    """Test system optimization"""
    
    def test_optimization_request(self, service):
        """Test optimization request"""
        request = OptimizationRequest(
            system_id=1,
            optimization_goal="minimize_cost",
            time_horizon_days=7
        )
        
        result = service.optimize_system(request)
        
        assert len(result.optimized_schedule) > 0
        assert result.expected_savings >= 0
        assert 0 <= result.expected_self_consumption_rate <= 1
        assert 0 <= result.optimization_quality <= 1
        assert result.computation_time_ms > 0


class TestMonitoring:
    """Test system monitoring"""
    
    def test_get_monitoring_data(self, service):
        """Test monitoring data retrieval"""
        monitoring = service.get_monitoring_data(system_id=1)
        
        assert monitoring.pv_current_power >= 0
        assert monitoring.hp_status in ["on", "off", "standby"]
        assert monitoring.hp_current_cop > 0
        if monitoring.battery_soc is not None:
            assert 0 <= monitoring.battery_soc <= 100


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_zero_battery(self, service, basic_request):
        """Test with zero battery capacity"""
        basic_request.battery_capacity = 0
        result = service.analyze_combined_system(basic_request)
        
        assert result is not None
        assert result.financial_analysis.battery_cost == 0
    
    def test_high_cop(self, service, basic_request):
        """Test with high COP heat pump"""
        basic_request.hp_cop = 5.5
        result = service.analyze_combined_system(basic_request)
        
        # Higher COP should reduce HP consumption
        assert result.synergy_analysis.total_pv_for_heating > 0
    
    def test_poor_insulation(self, service, basic_request):
        """Test with poor building insulation"""
        basic_request.building_insulation_quality = "poor"
        result = service.analyze_combined_system(basic_request)
        
        # Poor insulation increases heating demand
        assert result.annual_energy_flow['total_hp_consumption'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
