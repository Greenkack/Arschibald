"""
Tests for 3D Visualization Advanced Features Service

Tests cover:
- Material rendering
- Lighting and shadows
- Weather visualization
- Time-of-day simulation
- Seasonal visualization
- Photo-realistic rendering

Task: 134
"""

import pytest
from datetime import datetime
from services.visualization_3d_advanced_features import (
    Visualization3DAdvancedFeatures,
    MaterialProperties,
    LightSource,
    WeatherConditions,
    TimeOfDay
)


@pytest.fixture
def viz_service():
    """Create visualization service instance."""
    return Visualization3DAdvancedFeatures()


@pytest.fixture
def sample_scene_data():
    """Create sample scene data."""
    return {
        "building": {"length": 10.0, "width": 6.0, "height": 6.0},
        "modules": [
            {"x": 2.0, "y": 2.0, "z": 6.5},
            {"x": 4.0, "y": 2.0, "z": 6.5}
        ]
    }


@pytest.fixture
def sample_time_of_day():
    """Create sample time of day."""
    return TimeOfDay(
        hour=12,
        minute=0,
        date=datetime(2024, 6, 21),
        latitude=51.5,
        longitude=0.0,
        timezone_offset=0
    )


@pytest.fixture
def sample_weather():
    """Create sample weather conditions."""
    return WeatherConditions(
        cloud_coverage=0.2,
        sun_intensity=1.0,
        ambient_light=0.5,
        fog_density=0.0,
        precipitation="none",
        wind_speed_ms=2.0,
        temperature_c=25.0
    )


class TestMaterialSystem:
    """Test material rendering system."""
    
    def test_material_library_initialization(self, viz_service):
        """Test that material library is properly initialized."""
        assert len(viz_service.material_library) > 0
        assert "pv_module_glass" in viz_service.material_library
        assert "roof_tile_clay" in viz_service.material_library
    
    def test_get_material(self, viz_service):
        """Test getting material by name."""
        material = viz_service.get_material("pv_module_glass")
        assert isinstance(material, MaterialProperties)
        assert material.name == "PV Module Glass"
        assert 0 <= material.metallic <= 1
        assert 0 <= material.roughness <= 1
    
    def test_get_nonexistent_material(self, viz_service):
        """Test getting non-existent material returns default."""
        material = viz_service.get_material("nonexistent")
        assert isinstance(material, MaterialProperties)
    
    def test_apply_materials_to_scene(self, viz_service, sample_scene_data):
        """Test applying materials to scene."""
        result = viz_service.apply_materials_to_scene(sample_scene_data)
        assert "pv_modules_material" in result
        assert "roof_material" in result


class TestLightingSystem:
    """Test lighting and shadow system."""
    
    def test_calculate_sun_position(self, viz_service, sample_time_of_day):
        """Test sun position calculation."""
        position = viz_service.calculate_sun_position(sample_time_of_day)
        assert len(position) == 3
        assert all(isinstance(p, float) for p in position)
        # At noon on summer solstice, sun should be high
        assert position[2] > 0.5  # High elevation
    
    def test_create_lighting_setup(self, viz_service, sample_time_of_day, sample_weather):
        """Test creating lighting setup."""
        lights = viz_service.create_lighting_setup(
            sample_time_of_day, sample_weather, "high"
        )
        assert len(lights) > 0
        assert all(isinstance(light, LightSource) for light in lights)
        # Should have at least sun and sky lights
        assert any(light.type == "directional" for light in lights)
        assert any(light.type == "ambient" for light in lights)
    
    def test_lighting_quality_levels(self, viz_service, sample_time_of_day, sample_weather):
        """Test different lighting quality levels."""
        for quality in ["low", "medium", "high", "ultra"]:
            lights = viz_service.create_lighting_setup(
                sample_time_of_day, sample_weather, quality
            )
            assert len(lights) > 0
    
    def test_calculate_shadows(self, viz_service, sample_scene_data, sample_time_of_day, sample_weather):
        """Test shadow calculation."""
        lights = viz_service.create_lighting_setup(
            sample_time_of_day, sample_weather, "high"
        )
        shadows = viz_service.calculate_shadows(
            sample_scene_data, lights, "high"
        )
        assert "shadow_maps" in shadows
        assert "ambient_occlusion" in shadows


class TestWeatherVisualization:
    """Test weather effects."""
    
    def test_create_weather_effects(self, viz_service, sample_weather):
        """Test creating weather effects."""
        effects = viz_service.create_weather_effects(
            sample_weather, (50.0, 50.0, 20.0)
        )
        assert "clouds" in effects
        assert "fog" in effects
        assert "precipitation" in effects
        assert "atmosphere" in effects
    
    def test_cloud_layer_creation(self, viz_service):
        """Test cloud layer with different coverage."""
        # Clear sky
        weather_clear = WeatherConditions(
            cloud_coverage=0.0,
            sun_intensity=1.0,
            ambient_light=0.5,
            fog_density=0.0,
            precipitation="none",
            wind_speed_ms=2.0,
            temperature_c=25.0
        )
        effects_clear = viz_service.create_weather_effects(
            weather_clear, (50.0, 50.0, 20.0)
        )
        assert effects_clear["clouds"]["enabled"] == False
        
        # Cloudy
        weather_cloudy = WeatherConditions(
            cloud_coverage=0.8,
            sun_intensity=0.5,
            ambient_light=0.3,
            fog_density=0.0,
            precipitation="none",
            wind_speed_ms=3.0,
            temperature_c=20.0
        )
        effects_cloudy = viz_service.create_weather_effects(
            weather_cloudy, (50.0, 50.0, 20.0)
        )
        assert effects_cloudy["clouds"]["enabled"] == True
        assert effects_cloudy["clouds"]["coverage"] == 0.8


class TestSunPath:
    """Test sun path calculation."""
    
    def test_calculate_sun_path(self, viz_service):
        """Test calculating sun path for a day."""
        date = datetime(2024, 6, 21)  # Summer solstice
        sun_path = viz_service.calculate_sun_path(
            date, 51.5, 0.0, 0
        )
        assert len(sun_path) > 0
        # Should have multiple positions throughout the day
        assert len(sun_path) > 20
        # All positions should be above horizon
        assert all(p["position"][2] > 0 for p in sun_path)
    
    def test_sun_path_caching(self, viz_service):
        """Test that sun path is cached."""
        date = datetime(2024, 6, 21)
        path1 = viz_service.calculate_sun_path(date, 51.5, 0.0, 0)
        path2 = viz_service.calculate_sun_path(date, 51.5, 0.0, 0)
        assert path1 == path2


class TestTimeOfDaySimulation:
    """Test time-of-day simulation."""
    
    def test_simulate_time_of_day(self, viz_service, sample_scene_data, sample_time_of_day):
        """Test simulating different times of day."""
        snapshots = viz_service.simulate_time_of_day(
            sample_scene_data,
            sample_time_of_day,
            duration_hours=6.0,
            steps=12
        )
        assert len(snapshots) == 12
        assert all("time" in s for s in snapshots)
        assert all("lighting" in s for s in snapshots)
        assert all("sky_color" in s for s in snapshots)
    
    def test_sky_color_changes(self, viz_service, sample_scene_data):
        """Test that sky color changes with time."""
        # Dawn
        time_dawn = TimeOfDay(
            hour=6, minute=0,
            date=datetime(2024, 6, 21),
            latitude=51.5, longitude=0.0, timezone_offset=0
        )
        # Noon
        time_noon = TimeOfDay(
            hour=12, minute=0,
            date=datetime(2024, 6, 21),
            latitude=51.5, longitude=0.0, timezone_offset=0
        )
        
        snapshots_dawn = viz_service.simulate_time_of_day(
            sample_scene_data, time_dawn, 1.0, 2
        )
        snapshots_noon = viz_service.simulate_time_of_day(
            sample_scene_data, time_noon, 1.0, 2
        )
        
        # Colors should be different
        assert snapshots_dawn[0]["sky_color"] != snapshots_noon[0]["sky_color"]


class TestSeasonalSimulation:
    """Test seasonal visualization."""
    
    def test_simulate_seasons(self, viz_service, sample_scene_data):
        """Test simulating all four seasons."""
        seasons = viz_service.simulate_seasons(
            sample_scene_data,
            (51.5, 0.0),
            2024
        )
        assert len(seasons) == 4
        assert "spring" in seasons
        assert "summer" in seasons
        assert "autumn" in seasons
        assert "winter" in seasons
    
    def test_seasonal_differences(self, viz_service, sample_scene_data):
        """Test that seasons have different characteristics."""
        seasons = viz_service.simulate_seasons(
            sample_scene_data,
            (51.5, 0.0),
            2024
        )
        
        # Summer should have more daylight than winter
        summer_daylight = seasons["summer"]["daylight_hours"]
        winter_daylight = seasons["winter"]["daylight_hours"]
        assert summer_daylight > winter_daylight
        
        # Ground colors should differ
        assert seasons["spring"]["ground_color"] != seasons["winter"]["ground_color"]


class TestPhotorealisticRendering:
    """Test photo-realistic rendering."""
    
    def test_create_photorealistic_render(
        self, viz_service, sample_scene_data,
        sample_time_of_day, sample_weather
    ):
        """Test creating photorealistic render configuration."""
        render_config = viz_service.create_photorealistic_render(
            sample_scene_data,
            sample_time_of_day,
            sample_weather
        )
        
        assert "scene" in render_config
        assert "camera" in render_config
        assert "lighting" in render_config
        assert "shadows" in render_config
        assert "weather_effects" in render_config
        assert "post_processing" in render_config
        assert "metadata" in render_config
    
    def test_render_quality_settings(
        self, viz_service, sample_scene_data,
        sample_time_of_day, sample_weather
    ):
        """Test different render quality settings."""
        for quality in ["low", "medium", "high", "ultra"]:
            render_settings = {
                "quality": quality,
                "samples": 64,
                "resolution": (1920, 1080)
            }
            render_config = viz_service.create_photorealistic_render(
                sample_scene_data,
                sample_time_of_day,
                sample_weather,
                render_settings=render_settings
            )
            assert render_config["render_settings"]["quality"] == quality
    
    def test_render_time_estimation(self, viz_service):
        """Test render time estimation."""
        render_settings_low = {"quality": "low", "samples": 32, "resolution": (1920, 1080)}
        render_settings_ultra = {"quality": "ultra", "samples": 512, "resolution": (3840, 2160)}
        
        time_low = viz_service._estimate_render_time(render_settings_low)
        time_ultra = viz_service._estimate_render_time(render_settings_ultra)
        
        # Ultra should take significantly longer
        assert time_ultra > time_low * 5


class TestIntegration:
    """Integration tests combining multiple features."""
    
    def test_complete_workflow(
        self, viz_service, sample_scene_data,
        sample_time_of_day, sample_weather
    ):
        """Test complete workflow from scene to render."""
        # Apply materials
        scene_with_materials = viz_service.apply_materials_to_scene(sample_scene_data)
        
        # Create lighting
        lights = viz_service.create_lighting_setup(
            sample_time_of_day, sample_weather, "high"
        )
        
        # Calculate shadows
        shadows = viz_service.calculate_shadows(
            scene_with_materials, lights, "high"
        )
        
        # Create weather effects
        weather_effects = viz_service.create_weather_effects(
            sample_weather, (50.0, 50.0, 20.0)
        )
        
        # Create photorealistic render
        render_config = viz_service.create_photorealistic_render(
            sample_scene_data,
            sample_time_of_day,
            sample_weather
        )
        
        # Verify all components are present
        assert scene_with_materials is not None
        assert len(lights) > 0
        assert shadows is not None
        assert weather_effects is not None
        assert render_config is not None
