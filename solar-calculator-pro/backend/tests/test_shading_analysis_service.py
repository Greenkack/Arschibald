"""
Tests for Shading Analysis Service

Comprehensive test suite for solar shading analysis functionality.
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from ..services.shading_analysis_service import (
    ShadingAnalysisService,
    ShadingAnalysisRequest,
    ObstacleModel,
    LocationModel,
    SunPositionCalculator,
    ObstacleShadowCalculator,
    ShadingLossCalculator,
    ShadingOptimizationSuggester,
    ShadingVisualizationGenerator
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def berlin_location():
    """Berlin, Germany location"""
    return LocationModel(
        latitude=52.52,
        longitude=13.405,
        timezone="Europe/Berlin",
        elevation=34.0
    )


@pytest.fixture
def sample_obstacles():
    """Sample obstacles for testing"""
    return [
        ObstacleModel(
            id="building_1",
            type="building",
            height=15.0,
            distance=20.0,
            azimuth=180.0,
            width=10.0,
            description="Neighboring building"
        ),
        ObstacleModel(
            id="tree_1",
            type="tree",
            height=12.0,
            distance=15.0,
            azimuth=135.0,
            width=5.0,
            description="Large oak tree"
        )
    ]


@pytest.fixture
def analysis_request(berlin_location, sample_obstacles):
    """Complete analysis request"""
    return ShadingAnalysisRequest(
        location=berlin_location,
        obstacles=sample_obstacles,
        module_tilt=30.0,
        module_azimuth=180.0,
        module_area=50.0,
        analysis_start_date=datetime(2024, 1, 1),
        analysis_end_date=datetime(2024, 1, 7),  # One week for testing
        time_resolution=60
    )


# ============================================================================
# Sun Position Calculator Tests
# ============================================================================

class TestSunPositionCalculator:
    """Test sun position calculations"""
    
    def test_calculate_sun_position_noon(self, berlin_location):
        """Test sun position at solar noon"""
        # Summer solstice at noon
        timestamp = datetime(2024, 6, 21, 12, 0, 0)
        
        altitude, azimuth = SunPositionCalculator.calculate_sun_position(
            berlin_location.latitude,
            berlin_location.longitude,
            timestamp
        )
        
        # At solar noon, sun should be roughly south (180°)
        assert 0 < altitude < 90, "Altitude should be positive"
        assert 150 < azimuth < 210, "Azimuth should be roughly south"
    
    def test_calculate_sun_position_sunrise(self, berlin_location):
        """Test sun position at sunrise"""
        timestamp = datetime(2024, 6, 21, 5, 0, 0)
        
        altitude, azimuth = SunPositionCalculator.calculate_sun_position(
            berlin_location.latitude,
            berlin_location.longitude,
            timestamp
        )
        
        # At sunrise, altitude should be low, azimuth should be east
        assert altitude < 30, "Altitude should be low at sunrise"
        assert 45 < azimuth < 135, "Azimuth should be roughly east"
    
    def test_calculate_sun_path(self, berlin_location):
        """Test complete sun path calculation"""
        date = datetime(2024, 6, 21)
        
        sun_path = SunPositionCalculator.calculate_sun_path(
            berlin_location,
            date,
            time_resolution=60
        )
        
        assert len(sun_path) > 0, "Sun path should have data points"
        assert all('altitude' in p for p in sun_path), "All points should have altitude"
        assert all('azimuth' in p for p in sun_path), "All points should have azimuth"
        assert all(p['altitude'] > 0 for p in sun_path), "All points should be above horizon"
    
    def test_sun_path_seasonal_variation(self, berlin_location):
        """Test sun path varies by season"""
        summer_date = datetime(2024, 6, 21)
        winter_date = datetime(2024, 12, 21)
        
        summer_path = SunPositionCalculator.calculate_sun_path(
            berlin_location, summer_date, time_resolution=60
        )
        winter_path = SunPositionCalculator.calculate_sun_path(
            berlin_location, winter_date, time_resolution=60
        )
        
        # Summer should have more daylight hours
        assert len(summer_path) > len(winter_path), "Summer should have longer days"
        
        # Summer sun should reach higher altitude
        max_summer_alt = max(p['altitude'] for p in summer_path)
        max_winter_alt = max(p['altitude'] for p in winter_path)
        assert max_summer_alt > max_winter_alt, "Summer sun should be higher"


# ============================================================================
# Obstacle Shadow Calculator Tests
# ============================================================================

class TestObstacleShadowCalculator:
    """Test obstacle shadow calculations"""
    
    def test_calculate_shadow_angle(self):
        """Test shadow angle calculation"""
        # 10m tall obstacle, 20m away, sun at 45° altitude
        shadow_angle = ObstacleShadowCalculator.calculate_shadow_angle(
            obstacle_height=10.0,
            obstacle_distance=20.0,
            sun_altitude=45.0
        )
        
        assert shadow_angle > 0, "Shadow angle should be positive"
        assert shadow_angle < 90, "Shadow angle should be less than 90°"
    
    def test_is_module_shaded_direct(self):
        """Test direct shading detection"""
        obstacle = ObstacleModel(
            id="test",
            type="building",
            height=10.0,
            distance=15.0,
            azimuth=180.0,
            width=10.0
        )
        
        # Sun directly behind obstacle
        is_shaded, shading_pct = ObstacleShadowCalculator.is_module_shaded(
            obstacle,
            sun_altitude=30.0,
            sun_azimuth=180.0,
            module_azimuth=180.0
        )
        
        assert is_shaded, "Module should be shaded"
        assert shading_pct > 0, "Shading percentage should be positive"
    
    def test_is_module_not_shaded(self):
        """Test no shading when sun is opposite"""
        obstacle = ObstacleModel(
            id="test",
            type="building",
            height=10.0,
            distance=15.0,
            azimuth=180.0,
            width=10.0
        )
        
        # Sun opposite to obstacle
        is_shaded, shading_pct = ObstacleShadowCalculator.is_module_shaded(
            obstacle,
            sun_altitude=30.0,
            sun_azimuth=0.0,  # North
            module_azimuth=180.0  # South
        )
        
        assert not is_shaded, "Module should not be shaded"
        assert shading_pct == 0, "Shading percentage should be zero"
    
    def test_calculate_shadow_profile(self, berlin_location, sample_obstacles):
        """Test complete shadow profile calculation"""
        date = datetime(2024, 6, 21)
        sun_path = SunPositionCalculator.calculate_sun_path(
            berlin_location, date, time_resolution=60
        )
        
        shadow_profile = ObstacleShadowCalculator.calculate_shadow_profile(
            sample_obstacles,
            sun_path,
            module_azimuth=180.0
        )
        
        assert len(shadow_profile) == len(sun_path), "Profile should match sun path length"
        assert all('shading_percent' in p for p in shadow_profile), "All entries should have shading percent"
        assert all('shaded' in p for p in shadow_profile), "All entries should have shaded flag"


# ============================================================================
# Shading Loss Calculator Tests
# ============================================================================

class TestShadingLossCalculator:
    """Test shading loss calculations"""
    
    def test_calculate_hourly_irradiance_no_shading(self):
        """Test irradiance calculation without shading"""
        irradiance = ShadingLossCalculator.calculate_hourly_irradiance(
            sun_altitude=45.0,
            shading_percent=0.0,
            clear_sky_irradiance=1000.0
        )
        
        assert irradiance > 0, "Irradiance should be positive"
        assert irradiance <= 1000.0, "Irradiance should not exceed clear sky value"
    
    def test_calculate_hourly_irradiance_with_shading(self):
        """Test irradiance calculation with shading"""
        no_shade = ShadingLossCalculator.calculate_hourly_irradiance(
            sun_altitude=45.0,
            shading_percent=0.0
        )
        
        with_shade = ShadingLossCalculator.calculate_hourly_irradiance(
            sun_altitude=45.0,
            shading_percent=50.0
        )
        
        assert with_shade < no_shade, "Shading should reduce irradiance"
        assert with_shade == pytest.approx(no_shade * 0.5, rel=0.1), "50% shading should halve irradiance"
    
    def test_calculate_daily_loss(self, berlin_location, sample_obstacles):
        """Test daily energy loss calculation"""
        date = datetime(2024, 6, 21)
        sun_path = SunPositionCalculator.calculate_sun_path(
            berlin_location, date, time_resolution=60
        )
        
        shadow_profile = ObstacleShadowCalculator.calculate_shadow_profile(
            sample_obstacles,
            sun_path,
            module_azimuth=180.0
        )
        
        daily_loss = ShadingLossCalculator.calculate_daily_loss(
            shadow_profile,
            module_area=50.0
        )
        
        assert 'potential_energy_wh' in daily_loss
        assert 'actual_energy_wh' in daily_loss
        assert 'energy_loss_wh' in daily_loss
        assert 'loss_percent' in daily_loss
        
        assert daily_loss['potential_energy_wh'] >= daily_loss['actual_energy_wh']
        assert daily_loss['loss_percent'] >= 0
        assert daily_loss['loss_percent'] <= 100
    
    def test_calculate_annual_loss(self, berlin_location, sample_obstacles):
        """Test annual energy loss calculation"""
        result = ShadingLossCalculator.calculate_annual_loss(
            berlin_location,
            sample_obstacles,
            module_azimuth=180.0,
            module_area=50.0,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 7)  # One week for testing
        )
        
        assert result.total_annual_loss_percent >= 0
        assert result.total_annual_loss_percent <= 100
        assert len(result.monthly_losses) > 0
        assert result.affected_area_percent >= 0


# ============================================================================
# Optimization Suggester Tests
# ============================================================================

class TestShadingOptimizationSuggester:
    """Test optimization suggestion generation"""
    
    def test_analyze_tilt_adjustment(self, berlin_location, sample_obstacles):
        """Test tilt adjustment suggestion"""
        suggestion = ShadingOptimizationSuggester.analyze_tilt_adjustment(
            current_tilt=20.0,
            obstacles=sample_obstacles,
            location=berlin_location
        )
        
        # May or may not return suggestion depending on conditions
        if suggestion:
            assert suggestion.type == 'tilt_adjustment'
            assert suggestion.potential_improvement_percent > 0
            assert suggestion.implementation_difficulty in ['easy', 'moderate', 'difficult']
    
    def test_analyze_azimuth_adjustment(self, sample_obstacles):
        """Test azimuth adjustment suggestion"""
        suggestion = ShadingOptimizationSuggester.analyze_azimuth_adjustment(
            current_azimuth=180.0,
            obstacles=sample_obstacles
        )
        
        # May or may not return suggestion
        if suggestion:
            assert suggestion.type == 'azimuth_adjustment'
            assert suggestion.potential_improvement_percent > 0
    
    def test_analyze_obstacle_removal(self):
        """Test obstacle removal suggestions"""
        obstacles = [
            ObstacleModel(
                id="tree_1",
                type="tree",
                height=15.0,
                distance=10.0,
                azimuth=180.0,
                width=5.0
            )
        ]
        
        suggestions = ShadingOptimizationSuggester.analyze_obstacle_removal(obstacles)
        
        assert len(suggestions) > 0, "Should suggest removing tall tree"
        assert all(s.type == 'obstacle_removal' for s in suggestions)
    
    def test_generate_all_suggestions(self, berlin_location, sample_obstacles):
        """Test complete suggestion generation"""
        suggestions = ShadingOptimizationSuggester.generate_all_suggestions(
            current_tilt=30.0,
            current_azimuth=180.0,
            obstacles=sample_obstacles,
            location=berlin_location
        )
        
        assert isinstance(suggestions, list)
        # Suggestions are sorted by potential improvement
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i].potential_improvement_percent >= suggestions[i+1].potential_improvement_percent


# ============================================================================
# Visualization Generator Tests
# ============================================================================

class TestShadingVisualizationGenerator:
    """Test visualization data generation"""
    
    def test_generate_sun_path_data(self, berlin_location):
        """Test sun path data generation"""
        date = datetime(2024, 6, 21)
        
        sun_path = ShadingVisualizationGenerator.generate_sun_path_data(
            berlin_location, date
        )
        
        assert len(sun_path) > 0
        assert all('altitude' in p for p in sun_path)
        assert all('azimuth' in p for p in sun_path)
    
    def test_generate_obstacle_shadows(self, sample_obstacles):
        """Test obstacle shadow visualization data"""
        shadows = ShadingVisualizationGenerator.generate_obstacle_shadows(
            sample_obstacles,
            sun_altitude=45.0,
            sun_azimuth=180.0
        )
        
        assert len(shadows) == len(sample_obstacles)
        assert all('shadow_length' in s for s in shadows)
        assert all('obstacle_id' in s for s in shadows)
    
    def test_generate_heatmap_data(self, berlin_location, sample_obstacles):
        """Test heatmap data generation"""
        start_date = datetime(2024, 1, 1)
        
        heatmap = ShadingVisualizationGenerator.generate_heatmap_data(
            berlin_location,
            sample_obstacles,
            module_azimuth=180.0,
            start_date=start_date,
            days=30  # One month for testing
        )
        
        assert 'data' in heatmap
        assert 'min_shading' in heatmap
        assert 'max_shading' in heatmap
        assert len(heatmap['data']) > 0


# ============================================================================
# Main Service Tests
# ============================================================================

class TestShadingAnalysisService:
    """Test main shading analysis service"""
    
    def test_analyze_shading_complete(self, analysis_request):
        """Test complete shading analysis"""
        service = ShadingAnalysisService()
        
        result = service.analyze_shading(analysis_request)
        
        # Check losses
        assert result.losses is not None
        assert result.losses.total_annual_loss_percent >= 0
        assert result.losses.total_annual_loss_percent <= 100
        
        # Check visualization
        assert result.visualization is not None
        assert len(result.visualization.sun_path_data) > 0
        
        # Check suggestions
        assert result.suggestions is not None
        assert isinstance(result.suggestions, list)
        
        # Check metadata
        assert result.analysis_metadata is not None
        assert 'analysis_date' in result.analysis_metadata
        assert 'obstacles_count' in result.analysis_metadata
    
    def test_quick_shading_check(self, berlin_location, sample_obstacles):
        """Test quick shading check"""
        service = ShadingAnalysisService()
        
        result = service.quick_shading_check(
            berlin_location,
            sample_obstacles,
            module_azimuth=180.0
        )
        
        assert 'timestamp' in result
        assert 'sun_altitude' in result
        assert 'sun_azimuth' in result
        assert 'currently_shaded' in result
        assert 'shading_percent' in result
        assert isinstance(result['currently_shaded'], bool)
        assert 0 <= result['shading_percent'] <= 100
    
    def test_analysis_with_no_obstacles(self, berlin_location):
        """Test analysis with no obstacles"""
        request = ShadingAnalysisRequest(
            location=berlin_location,
            obstacles=[],
            module_tilt=30.0,
            module_azimuth=180.0,
            module_area=50.0,
            analysis_start_date=datetime(2024, 1, 1),
            analysis_end_date=datetime(2024, 1, 2),
            time_resolution=60
        )
        
        service = ShadingAnalysisService()
        result = service.analyze_shading(request)
        
        # With no obstacles, losses should be zero or very low
        assert result.losses.total_annual_loss_percent == 0.0
    
    def test_analysis_with_multiple_obstacles(self, berlin_location):
        """Test analysis with multiple obstacles"""
        obstacles = [
            ObstacleModel(
                id=f"obstacle_{i}",
                type="building",
                height=10.0 + i * 2,
                distance=15.0 + i * 5,
                azimuth=180.0 - i * 30,
                width=8.0
            )
            for i in range(5)
        ]
        
        request = ShadingAnalysisRequest(
            location=berlin_location,
            obstacles=obstacles,
            module_tilt=30.0,
            module_azimuth=180.0,
            module_area=50.0,
            analysis_start_date=datetime(2024, 1, 1),
            analysis_end_date=datetime(2024, 1, 2),
            time_resolution=60
        )
        
        service = ShadingAnalysisService()
        result = service.analyze_shading(request)
        
        # With multiple obstacles, should have some losses
        assert result.losses.total_annual_loss_percent >= 0
        assert len(result.suggestions) > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestShadingAnalysisIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_analysis_workflow(self, analysis_request):
        """Test complete analysis workflow from request to response"""
        service = ShadingAnalysisService()
        
        # Perform analysis
        result = service.analyze_shading(analysis_request)
        
        # Verify all components are present and valid
        assert result.losses.total_annual_loss_percent >= 0
        assert len(result.visualization.sun_path_data) > 0
        assert len(result.suggestions) >= 0
        assert result.analysis_metadata['obstacles_count'] == len(analysis_request.obstacles)
        
        # Verify data consistency
        if result.losses.monthly_losses:
            for month, loss in result.losses.monthly_losses.items():
                assert 0 <= loss <= 100, f"Monthly loss {month} out of range: {loss}"
    
    def test_seasonal_comparison(self, berlin_location, sample_obstacles):
        """Test shading analysis across seasons"""
        service = ShadingAnalysisService()
        
        seasons = [
            ("winter", datetime(2024, 12, 21)),
            ("spring", datetime(2024, 3, 21)),
            ("summer", datetime(2024, 6, 21)),
            ("fall", datetime(2024, 9, 21))
        ]
        
        results = {}
        for season_name, date in seasons:
            request = ShadingAnalysisRequest(
                location=berlin_location,
                obstacles=sample_obstacles,
                module_tilt=30.0,
                module_azimuth=180.0,
                module_area=50.0,
                analysis_start_date=date,
                analysis_end_date=date + timedelta(days=1),
                time_resolution=60
            )
            
            result = service.analyze_shading(request)
            results[season_name] = result.losses.total_annual_loss_percent
        
        # Verify we got results for all seasons
        assert len(results) == 4
        assert all(0 <= loss <= 100 for loss in results.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
