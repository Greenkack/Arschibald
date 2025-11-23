"""
Tests for Weather Service

Comprehensive test suite for weather integration functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from services.weather_service import (
    WeatherService,
    WeatherProvider,
    ClimateZone,
    WeatherData,
    HistoricalWeatherSummary,
    ProductionForecast
)


@pytest.fixture
def weather_service():
    """Create weather service instance"""
    return WeatherService(provider=WeatherProvider.OPEN_METEO)


@pytest.fixture
def sample_weather_data():
    """Create sample weather data"""
    return [
        WeatherData(
            timestamp=datetime(2024, 1, 1, 12, 0),
            temperature=15.0,
            cloud_cover=30.0,
            solar_irradiance=600.0,
            wind_speed=5.0,
            precipitation=0.0,
            humidity=65.0,
            pressure=1013.25,
            uv_index=3.0
        ),
        WeatherData(
            timestamp=datetime(2024, 1, 1, 13, 0),
            temperature=16.0,
            cloud_cover=25.0,
            solar_irradiance=700.0,
            wind_speed=4.5,
            precipitation=0.0,
            humidity=60.0,
            pressure=1013.0,
            uv_index=4.0
        )
    ]


class TestWeatherService:
    """Test WeatherService class"""
    
    def test_initialization(self):
        """Test service initialization"""
        service = WeatherService(provider=WeatherProvider.OPEN_METEO)
        assert service.provider == WeatherProvider.OPEN_METEO
        assert service.temperature_coefficient == -0.004
        assert service.reference_temperature == 25.0
        assert service.stc_irradiance == 1000.0
    
    def test_initialization_with_api_key(self):
        """Test service initialization with API key"""
        service = WeatherService(
            provider=WeatherProvider.OPENWEATHER,
            api_key="test_key"
        )
        assert service.api_key == "test_key"
    
    def test_estimate_irradiance_from_clouds(self, weather_service):
        """Test irradiance estimation from cloud cover"""
        # Clear sky (0% clouds)
        irradiance = weather_service._estimate_irradiance_from_clouds(0)
        assert irradiance == 1000.0
        
        # 50% cloud cover
        irradiance = weather_service._estimate_irradiance_from_clouds(50)
        assert irradiance == pytest.approx(625.0, rel=0.01)
        
        # Overcast (100% clouds)
        irradiance = weather_service._estimate_irradiance_from_clouds(100)
        assert irradiance == pytest.approx(250.0, rel=0.01)
    
    def test_calculate_seasonal_variation(self, weather_service, sample_weather_data):
        """Test seasonal variation calculation"""
        # Create data for all seasons
        weather_data = []
        for month in range(1, 13):
            for day in range(1, 3):
                weather_data.append(WeatherData(
                    timestamp=datetime(2024, month, day, 12, 0),
                    temperature=15.0,
                    cloud_cover=30.0,
                    solar_irradiance=500.0 + (month * 20),  # Vary by month
                    wind_speed=5.0,
                    precipitation=0.0,
                    humidity=65.0,
                    pressure=1013.25,
                    uv_index=3.0
                ))
        
        variation = weather_service._calculate_seasonal_variation(weather_data)
        
        assert "winter" in variation
        assert "spring" in variation
        assert "summer" in variation
        assert "autumn" in variation
        
        # Summer should have higher irradiance than winter
        assert variation["summer"] > variation["winter"]
    
    def test_calculate_monthly_averages(self, weather_service, sample_weather_data):
        """Test monthly averages calculation"""
        # Create data for multiple months
        weather_data = []
        for month in [1, 2, 3]:
            for day in range(1, 5):
                weather_data.append(WeatherData(
                    timestamp=datetime(2024, month, day, 12, 0),
                    temperature=10.0 + month,
                    cloud_cover=30.0,
                    solar_irradiance=500.0,
                    wind_speed=5.0,
                    precipitation=1.0,
                    humidity=65.0,
                    pressure=1013.25,
                    uv_index=3.0
                ))
        
        monthly_avg = weather_service._calculate_monthly_averages(weather_data)
        
        assert "January" in monthly_avg
        assert "February" in monthly_avg
        assert "March" in monthly_avg
        
        # Check that averages are calculated
        assert monthly_avg["January"]["temperature"] == pytest.approx(11.0, rel=0.01)
        assert monthly_avg["February"]["temperature"] == pytest.approx(12.0, rel=0.01)
    
    def test_calculate_forecast_confidence(self, weather_service):
        """Test forecast confidence calculation"""
        weather = WeatherData(
            timestamp=datetime.now(),
            temperature=20.0,
            cloud_cover=30.0,
            solar_irradiance=700.0,
            wind_speed=5.0,
            precipitation=0.0,
            humidity=65.0,
            pressure=1013.25,
            uv_index=3.0
        )
        
        # Confidence should decrease with days ahead
        confidence_1_day = weather_service._calculate_forecast_confidence(weather, 1)
        confidence_7_days = weather_service._calculate_forecast_confidence(weather, 7)
        
        assert confidence_1_day > confidence_7_days
        assert 0 <= confidence_1_day <= 100
        assert 0 <= confidence_7_days <= 100
    
    def test_determine_climate_zone_polar(self, weather_service):
        """Test polar climate zone determination"""
        zone = weather_service.determine_climate_zone(
            latitude=70.0,
            avg_temperature=-5.0,
            avg_precipitation=300.0
        )
        assert zone == ClimateZone.POLAR
    
    def test_determine_climate_zone_cold(self, weather_service):
        """Test cold climate zone determination"""
        zone = weather_service.determine_climate_zone(
            latitude=55.0,
            avg_temperature=5.0,
            avg_precipitation=600.0
        )
        assert zone == ClimateZone.COLD
    
    def test_determine_climate_zone_temperate(self, weather_service):
        """Test temperate climate zone determination"""
        zone = weather_service.determine_climate_zone(
            latitude=40.0,
            avg_temperature=15.0,
            avg_precipitation=800.0
        )
        assert zone == ClimateZone.TEMPERATE
    
    def test_determine_climate_zone_subtropical(self, weather_service):
        """Test subtropical climate zone determination"""
        zone = weather_service.determine_climate_zone(
            latitude=28.0,
            avg_temperature=20.0,
            avg_precipitation=1000.0
        )
        assert zone == ClimateZone.SUBTROPICAL
    
    def test_determine_climate_zone_tropical(self, weather_service):
        """Test tropical climate zone determination"""
        zone = weather_service.determine_climate_zone(
            latitude=10.0,
            avg_temperature=26.0,
            avg_precipitation=2000.0
        )
        assert zone == ClimateZone.TROPICAL
    
    def test_determine_climate_zone_arid(self, weather_service):
        """Test arid climate zone determination"""
        zone = weather_service.determine_climate_zone(
            latitude=35.0,
            avg_temperature=22.0,
            avg_precipitation=200.0
        )
        assert zone == ClimateZone.ARID
    
    def test_calculate_seasonal_production_variation(self, weather_service):
        """Test seasonal production variation calculation"""
        summary = HistoricalWeatherSummary(
            location="Test Location",
            latitude=52.52,
            longitude=13.41,
            start_date=datetime(2019, 1, 1),
            end_date=datetime(2024, 1, 1),
            avg_temperature=10.0,
            avg_cloud_cover=50.0,
            avg_solar_irradiance=400.0,
            total_sunshine_hours=1500.0,
            seasonal_variation={
                "winter": 200.0,
                "spring": 500.0,
                "summer": 700.0,
                "autumn": 400.0
            },
            monthly_averages={}
        )
        
        production = weather_service.calculate_seasonal_production_variation(
            historical_summary=summary,
            system_size_kwp=10.0
        )
        
        assert "winter" in production
        assert "spring" in production
        assert "summer" in production
        assert "autumn" in production
        
        # Summer should have highest production
        assert production["summer"] > production["winter"]
        assert production["summer"] > production["spring"]
        assert production["summer"] > production["autumn"]
    
    @pytest.mark.asyncio
    async def test_parse_open_meteo_response(self, weather_service):
        """Test Open-Meteo response parsing"""
        mock_response = {
            "hourly": {
                "time": [
                    "2024-01-01T12:00",
                    "2024-01-01T13:00"
                ],
                "temperature_2m": [15.0, 16.0],
                "cloudcover": [30.0, 25.0],
                "shortwave_radiation": [600.0, 700.0],
                "windspeed_10m": [5.0, 4.5],
                "precipitation": [0.0, 0.0],
                "relativehumidity_2m": [65.0, 60.0],
                "surface_pressure": [1013.25, 1013.0]
            }
        }
        
        weather_data = weather_service._parse_open_meteo_response(mock_response)
        
        assert len(weather_data) == 2
        assert weather_data[0].temperature == 15.0
        assert weather_data[0].cloud_cover == 30.0
        assert weather_data[1].temperature == 16.0
        assert weather_data[1].cloud_cover == 25.0


class TestProductionForecast:
    """Test production forecasting functionality"""
    
    @pytest.mark.asyncio
    async def test_forecast_production_calculation(self, weather_service):
        """Test production forecast calculation"""
        # Mock weather forecast
        mock_weather = [
            WeatherData(
                timestamp=datetime.now() + timedelta(days=1),
                temperature=20.0,
                cloud_cover=20.0,
                solar_irradiance=800.0,
                wind_speed=5.0,
                precipitation=0.0,
                humidity=60.0,
                pressure=1013.25,
                uv_index=5.0
            )
        ]
        
        with patch.object(
            weather_service,
            '_get_weather_forecast',
            return_value=mock_weather
        ):
            forecasts = await weather_service.forecast_production(
                latitude=52.52,
                longitude=13.41,
                system_size_kwp=10.0,
                days_ahead=1
            )
            
            assert len(forecasts) == 1
            forecast = forecasts[0]
            
            assert forecast.expected_production > 0
            assert 0 <= forecast.confidence <= 100
            assert forecast.weather_factor > 0
            assert forecast.temperature_factor > 0
            assert forecast.cloud_factor > 0
            assert forecast.optimal_production > 0
    
    def test_temperature_factor_calculation(self, weather_service):
        """Test temperature impact on production"""
        # At reference temperature (25°C), factor should be 1.0
        weather_25c = WeatherData(
            timestamp=datetime.now(),
            temperature=25.0,
            cloud_cover=0.0,
            solar_irradiance=1000.0,
            wind_speed=0.0,
            precipitation=0.0,
            humidity=50.0,
            pressure=1013.25,
            uv_index=5.0
        )
        
        temp_diff = weather_25c.temperature - weather_service.reference_temperature
        temp_factor = 1 + (weather_service.temperature_coefficient * temp_diff)
        assert temp_factor == pytest.approx(1.0, rel=0.01)
        
        # At higher temperature (35°C), efficiency should decrease
        weather_35c = WeatherData(
            timestamp=datetime.now(),
            temperature=35.0,
            cloud_cover=0.0,
            solar_irradiance=1000.0,
            wind_speed=0.0,
            precipitation=0.0,
            humidity=50.0,
            pressure=1013.25,
            uv_index=5.0
        )
        
        temp_diff = weather_35c.temperature - weather_service.reference_temperature
        temp_factor = 1 + (weather_service.temperature_coefficient * temp_diff)
        assert temp_factor < 1.0


class TestWeatherDataIntegration:
    """Test weather data integration"""
    
    @pytest.mark.asyncio
    async def test_get_historical_weather_date_range(self, weather_service):
        """Test historical weather data retrieval"""
        # This test would require mocking the API call
        # For now, we'll test the structure
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 7)
        
        with patch.object(
            weather_service,
            '_fetch_open_meteo_historical',
            return_value=[]
        ):
            weather_data = await weather_service.get_historical_weather(
                latitude=52.52,
                longitude=13.41,
                start_date=start_date,
                end_date=end_date
            )
            
            assert isinstance(weather_data, list)
    
    @pytest.mark.asyncio
    async def test_analyze_historical_weather_structure(self, weather_service):
        """Test historical weather analysis structure"""
        # Mock the historical data fetch
        mock_data = [
            WeatherData(
                timestamp=datetime(2024, month, 1, 12, 0),
                temperature=10.0 + month,
                cloud_cover=30.0,
                solar_irradiance=400.0 + (month * 20),
                wind_speed=5.0,
                precipitation=1.0,
                humidity=65.0,
                pressure=1013.25,
                uv_index=3.0
            )
            for month in range(1, 13)
        ]
        
        with patch.object(
            weather_service,
            'get_historical_weather',
            return_value=mock_data
        ):
            summary = await weather_service.analyze_historical_weather(
                latitude=52.52,
                longitude=13.41,
                years=1
            )
            
            assert isinstance(summary, HistoricalWeatherSummary)
            assert summary.latitude == 52.52
            assert summary.longitude == 13.41
            assert summary.avg_temperature > 0
            assert summary.avg_cloud_cover >= 0
            assert summary.avg_solar_irradiance > 0
            assert len(summary.seasonal_variation) == 4
            assert len(summary.monthly_averages) > 0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_invalid_provider(self):
        """Test invalid weather provider"""
        with pytest.raises(ValueError):
            WeatherProvider("invalid_provider")
    
    def test_extreme_latitude(self, weather_service):
        """Test extreme latitude values"""
        # North Pole
        zone = weather_service.determine_climate_zone(
            latitude=90.0,
            avg_temperature=-20.0,
            avg_precipitation=100.0
        )
        assert zone == ClimateZone.POLAR
        
        # South Pole
        zone = weather_service.determine_climate_zone(
            latitude=-90.0,
            avg_temperature=-30.0,
            avg_precipitation=50.0
        )
        assert zone == ClimateZone.POLAR
    
    def test_zero_system_size(self, weather_service):
        """Test production calculation with zero system size"""
        summary = HistoricalWeatherSummary(
            location="Test",
            latitude=0.0,
            longitude=0.0,
            start_date=datetime.now(),
            end_date=datetime.now(),
            avg_temperature=20.0,
            avg_cloud_cover=50.0,
            avg_solar_irradiance=500.0,
            total_sunshine_hours=1000.0,
            seasonal_variation={"winter": 300.0, "spring": 500.0, "summer": 700.0, "autumn": 400.0},
            monthly_averages={}
        )
        
        production = weather_service.calculate_seasonal_production_variation(
            historical_summary=summary,
            system_size_kwp=0.0
        )
        
        # All production values should be zero
        assert all(value == 0.0 for value in production.values())
    
    def test_missing_weather_data(self, weather_service):
        """Test handling of missing weather data"""
        # Empty weather data list
        variation = weather_service._calculate_seasonal_variation([])
        
        # Should return zeros for all seasons
        assert variation["winter"] == 0.0
        assert variation["spring"] == 0.0
        assert variation["summer"] == 0.0
        assert variation["autumn"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
