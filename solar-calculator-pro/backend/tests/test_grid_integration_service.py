"""
Tests for Grid Integration Service
"""

import pytest
from ..services.grid_integration_service import GridIntegrationService
from ..models.grid_schemas import (
    FeedInTariffRequest, NetMeteringRequest, GridConnectionRequest,
    PowerQualityRequest, GridStabilityRequest, SmartGridRequest,
    GridIntegrationAnalysisRequest, GridConnectionType, MeteringType,
    PowerQualityStandard
)


@pytest.fixture
def grid_service():
    """Fixture for grid integration service"""
    return GridIntegrationService()


class TestFeedInTariff:
    """Tests for feed-in tariff calculations"""
    
    def test_basic_feed_in_calculation(self, grid_service):
        """Test basic feed-in tariff calculation"""
        request = FeedInTariffRequest(
            system_size_kwp=10.0,
            annual_production_kwh=12000,
            self_consumption_rate=0.3,
            feed_in_tariff_per_kwh=0.10,
            electricity_price_per_kwh=0.30,
            contract_duration_years=20
        )
        
        result = grid_service.calculate_feed_in_tariff(request)
        
        assert result.annual_feed_in_kwh == 8400  # 70% of 12000
        assert result.annual_self_consumption_kwh == 3600  # 30% of 12000
        assert result.annual_feed_in_revenue == 840  # 8400 * 0.10
        assert result.annual_self_consumption_savings == 1080  # 3600 * 0.30
        assert result.total_annual_benefit == 1920
        assert result.payback_period_years is not None
    
    def test_feed_in_with_degradation(self, grid_service):
        """Test feed-in calculation with system degradation"""
        request = FeedInTariffRequest(
            system_size_kwp=10.0,
            annual_production_kwh=12000,
            self_consumption_rate=0.3,
            feed_in_tariff_per_kwh=0.10,
            electricity_price_per_kwh=0.30,
            contract_duration_years=20,
            degradation_rate=0.005  # 0.5% per year
        )
        
        result = grid_service.calculate_feed_in_tariff(request)
        
        # Lifetime values should be less than 20x annual due to degradation
        assert result.lifetime_feed_in_revenue < result.annual_feed_in_revenue * 20
        assert result.total_lifetime_benefit > 0


class TestNetMetering:
    """Tests for net metering analysis"""
    
    def test_net_metering_with_surplus(self, grid_service):
        """Test net metering with energy surplus"""
        monthly_prod = [1000] * 12  # 12000 kWh/year
        monthly_cons = [800] * 12   # 9600 kWh/year
        
        request = NetMeteringRequest(
            system_size_kwp=10.0,
            annual_production_kwh=12000,
            annual_consumption_kwh=9600,
            electricity_price_per_kwh=0.30,
            net_metering_credit_per_kwh=0.27,
            monthly_production=monthly_prod,
            monthly_consumption=monthly_cons,
            rollover_allowed=True
        )
        
        result = grid_service.analyze_net_metering(request)
        
        assert result.annual_net_export_kwh > 0
        assert result.annual_credits_earned > 0
        assert result.self_sufficiency_rate >= 1.0  # Producing more than or equal to consuming
        assert len(result.monthly_analysis) == 12
    
    def test_net_metering_with_deficit(self, grid_service):
        """Test net metering with energy deficit"""
        monthly_prod = [800] * 12   # 9600 kWh/year
        monthly_cons = [1000] * 12  # 12000 kWh/year
        
        request = NetMeteringRequest(
            system_size_kwp=10.0,
            annual_production_kwh=9600,
            annual_consumption_kwh=12000,
            electricity_price_per_kwh=0.30,
            net_metering_credit_per_kwh=0.27,
            monthly_production=monthly_prod,
            monthly_consumption=monthly_cons,
            rollover_allowed=True
        )
        
        result = grid_service.analyze_net_metering(request)
        
        assert result.annual_net_import_kwh > 0
        assert result.self_sufficiency_rate < 1.0
        assert result.grid_independence_rate < 1.0


class TestGridConnection:
    """Tests for grid connection requirements"""
    
    def test_single_phase_connection(self, grid_service):
        """Test single-phase grid connection"""
        request = GridConnectionRequest(
            system_size_kwp=5.0,
            connection_type=GridConnectionType.SINGLE_PHASE,
            voltage_level=230,
            distance_to_grid_m=50,
            inverter_power_kw=5.0,
            location="Residential Area"
        )
        
        result = grid_service.calculate_grid_connection_requirements(request)
        
        assert result.connection_feasible
        assert result.required_cable_size_mm2 > 0
        assert result.estimated_connection_cost > 0
        assert result.voltage_drop_percent <= 3.0
        assert len(result.required_protection_devices) > 0
    
    def test_three_phase_connection(self, grid_service):
        """Test three-phase grid connection"""
        request = GridConnectionRequest(
            system_size_kwp=15.0,
            connection_type=GridConnectionType.THREE_PHASE,
            voltage_level=400,
            distance_to_grid_m=100,
            inverter_power_kw=15.0,
            location="Commercial Area"
        )
        
        result = grid_service.calculate_grid_connection_requirements(request)
        
        assert result.connection_feasible
        assert result.connection_type_recommended == GridConnectionType.THREE_PHASE
        assert "Grid Monitoring Relay" in result.required_protection_devices
    
    def test_long_distance_connection(self, grid_service):
        """Test connection with long distance"""
        request = GridConnectionRequest(
            system_size_kwp=10.0,
            connection_type=GridConnectionType.SINGLE_PHASE,
            voltage_level=230,
            distance_to_grid_m=200,
            inverter_power_kw=10.0,
            location="Rural Area"
        )
        
        result = grid_service.calculate_grid_connection_requirements(request)
        
        # Long distance should require larger cable
        assert result.required_cable_size_mm2 > 10
        assert "Transformer upgrade may be needed" in result.additional_requirements


class TestPowerQuality:
    """Tests for power quality analysis"""
    
    def test_compliant_power_quality(self, grid_service):
        """Test compliant power quality"""
        request = PowerQualityRequest(
            system_size_kwp=10.0,
            inverter_specs={
                "rated_power_kw": 10.0,
                "efficiency": 0.97,
                "power_factor": 0.99,
                "thd": 0.03
            },
            grid_voltage=400,
            standard=PowerQualityStandard.VDE_AR_N_4105
        )
        
        result = grid_service.analyze_power_quality(request)
        
        assert result.compliant
        assert result.power_factor >= 0.95
        assert result.total_harmonic_distortion_percent <= 5.0
        assert len(result.compliance_issues) == 0
    
    def test_non_compliant_power_quality(self, grid_service):
        """Test non-compliant power quality"""
        request = PowerQualityRequest(
            system_size_kwp=10.0,
            inverter_specs={
                "rated_power_kw": 10.0,
                "efficiency": 0.95,
                "power_factor": 0.90,  # Below minimum
                "thd": 0.08  # Above limit
            },
            grid_voltage=400,
            standard=PowerQualityStandard.VDE_AR_N_4105
        )
        
        result = grid_service.analyze_power_quality(request)
        
        assert not result.compliant
        assert len(result.compliance_issues) > 0
        assert len(result.recommendations) > 0


class TestGridStability:
    """Tests for grid stability calculations"""
    
    def test_strong_grid_stability(self, grid_service):
        """Test stability with strong grid"""
        request = GridStabilityRequest(
            system_size_kwp=10.0,
            grid_short_circuit_power_mva=100.0,  # Strong grid
            grid_impedance_ohm=0.05,
            inverter_response_time_ms=50,
            enable_reactive_power_support=True,
            enable_voltage_regulation=True
        )
        
        result = grid_service.calculate_grid_stability(request)
        
        assert result.stability_index > 0.7
        assert result.short_circuit_ratio > 10
        assert len(result.grid_support_services) > 0
        assert len(result.stability_concerns) == 0
    
    def test_weak_grid_stability(self, grid_service):
        """Test stability with weak grid"""
        request = GridStabilityRequest(
            system_size_kwp=10000.0,  # 10 MW system
            grid_short_circuit_power_mva=20.0,  # Weak grid (20 MVA)
            grid_impedance_ohm=0.5,
            inverter_response_time_ms=100
        )
        
        result = grid_service.calculate_grid_stability(request)
        
        assert result.short_circuit_ratio < 5  # Weak grid has SCR < 5
        assert len(result.stability_concerns) > 0
        assert "Weak grid" in result.stability_concerns[0]


class TestSmartGrid:
    """Tests for smart grid integration"""
    
    def test_smart_grid_with_battery(self, grid_service):
        """Test smart grid integration with battery"""
        request = SmartGridRequest(
            system_size_kwp=10.0,
            battery_capacity_kwh=10.0,
            enable_demand_response=True,
            enable_frequency_regulation=True,
            enable_voltage_support=True
        )
        
        result = grid_service.analyze_smart_grid_integration(request)
        
        assert result.smart_grid_ready
        assert result.frequency_regulation_capability
        assert result.voltage_support_capability
        assert result.annual_grid_services_revenue > 0
        assert len(result.available_services) >= 3
    
    def test_smart_grid_without_battery(self, grid_service):
        """Test smart grid integration without battery"""
        request = SmartGridRequest(
            system_size_kwp=10.0,
            battery_capacity_kwh=None,
            enable_demand_response=True,
            enable_voltage_support=True
        )
        
        result = grid_service.analyze_smart_grid_integration(request)
        
        assert not result.frequency_regulation_capability
        assert "Add battery storage" in result.recommended_upgrades[0]


class TestComprehensiveAnalysis:
    """Tests for comprehensive grid analysis"""
    
    def test_comprehensive_analysis(self, grid_service):
        """Test comprehensive grid integration analysis"""
        request = GridIntegrationAnalysisRequest(
            system_size_kwp=10.0,
            annual_production_kwh=12000,
            annual_consumption_kwh=10000,
            location="Test Location",
            connection_type=GridConnectionType.THREE_PHASE,
            metering_type=MeteringType.NET_METERING,
            feed_in_tariff_per_kwh=0.10,
            electricity_price_per_kwh=0.30,
            grid_voltage=400,
            distance_to_grid_m=50,
            battery_capacity_kwh=10.0,
            enable_smart_grid=True
        )
        
        result = grid_service.comprehensive_grid_analysis(request)
        
        assert result.feed_in_analysis is not None
        assert result.net_metering_analysis is not None
        assert result.connection_requirements is not None
        assert result.power_quality is not None
        assert result.grid_stability is not None
        assert result.smart_grid_potential is not None
        assert result.total_annual_benefit > 0
        assert result.overall_feasibility_score >= 0
        assert result.overall_feasibility_score <= 100
        assert result.compliance_status in ["Fully Compliant", "Requires Modifications"]
    
    def test_comprehensive_analysis_without_smart_grid(self, grid_service):
        """Test comprehensive analysis without smart grid"""
        request = GridIntegrationAnalysisRequest(
            system_size_kwp=10.0,
            annual_production_kwh=12000,
            annual_consumption_kwh=10000,
            location="Test Location",
            connection_type=GridConnectionType.SINGLE_PHASE,
            metering_type=MeteringType.FEED_IN_TARIFF,
            feed_in_tariff_per_kwh=0.10,
            electricity_price_per_kwh=0.30,
            grid_voltage=230,
            distance_to_grid_m=50,
            enable_smart_grid=False
        )
        
        result = grid_service.comprehensive_grid_analysis(request)
        
        assert result.smart_grid_potential is None
        assert result.net_metering_analysis is None  # Not applicable for FIT
