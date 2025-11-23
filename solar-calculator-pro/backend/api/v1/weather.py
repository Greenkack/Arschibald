"""
Weather API Endpoints

Provides REST API endpoints for weather data integration and solar production forecasting.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from services.weather_service import (
    WeatherService,
    WeatherProvider,
    ClimateZone,
    WeatherData,
    HistoricalWeatherSummary,
    ProductionForecast
)


router = APIRouter(prefix="/weather", tags=["weather"])


# Request/Response Models

class WeatherDataResponse(BaseModel):
    """Weather data response model"""
    timestamp: datetime
    temperature: float = Field(..., description="Temperature in Celsius")
    cloud_cover: float = Field(..., description="Cloud cover percentage (0-100)")
    solar_irradiance: float = Field(..., description="Solar irradiance in W/m²")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    precipitation: float = Field(..., description="Precipitation in mm")
    humidity: float = Field(..., description="Humidity percentage (0-100)")
    pressure: float = Field(..., description="Atmospheric pressure in hPa")
    uv_index: float = Field(..., description="UV index")


class HistoricalWeatherRequest(BaseModel):
    """Request for historical weather data"""
    latitude: float = Field(..., ge=-90, le=90, description="Location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Location longitude")
    start_date: datetime = Field(..., description="Start date for historical data")
    end_date: datetime = Field(..., description="End date for historical data")
    provider: Optional[str] = Field("open_meteo", description="Weather data provider")


class HistoricalAnalysisRequest(BaseModel):
    """Request for historical weather analysis"""
    latitude: float = Field(..., ge=-90, le=90, description="Location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Location longitude")
    years: int = Field(5, ge=1, le=10, description="Number of years to analyze")
    provider: Optional[str] = Field("open_meteo", description="Weather data provider")


class HistoricalWeatherSummaryResponse(BaseModel):
    """Historical weather summary response"""
    location: str
    latitude: float
    longitude: float
    start_date: datetime
    end_date: datetime
    avg_temperature: float
    avg_cloud_cover: float
    avg_solar_irradiance: float
    total_sunshine_hours: float
    seasonal_variation: dict
    monthly_averages: dict
    climate_zone: str


class ProductionForecastRequest(BaseModel):
    """Request for production forecast"""
    latitude: float = Field(..., ge=-90, le=90, description="Location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Location longitude")
    system_size_kwp: float = Field(..., gt=0, description="System size in kWp")
    days_ahead: int = Field(7, ge=1, le=14, description="Number of days to forecast")
    provider: Optional[str] = Field("open_meteo", description="Weather data provider")


class ProductionForecastResponse(BaseModel):
    """Production forecast response"""
    date: datetime
    expected_production: float = Field(..., description="Expected production in kWh")
    confidence: float = Field(..., description="Confidence level (0-100)")
    weather_factor: float = Field(..., description="Weather impact factor")
    temperature_factor: float = Field(..., description="Temperature impact factor")
    cloud_factor: float = Field(..., description="Cloud cover impact factor")
    optimal_production: float = Field(..., description="Optimal production in kWh")


class ClimateZoneRequest(BaseModel):
    """Request for climate zone determination"""
    latitude: float = Field(..., ge=-90, le=90, description="Location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Location longitude")
    avg_temperature: float = Field(..., description="Average annual temperature in °C")
    avg_precipitation: float = Field(..., description="Average annual precipitation in mm")


class ClimateZoneResponse(BaseModel):
    """Climate zone response"""
    climate_zone: str
    description: str
    solar_potential: str


class RealTimeWeatherRequest(BaseModel):
    """Request for real-time weather"""
    latitude: float = Field(..., ge=-90, le=90, description="Location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Location longitude")
    provider: Optional[str] = Field("open_meteo", description="Weather data provider")


class SeasonalProductionRequest(BaseModel):
    """Request for seasonal production analysis"""
    latitude: float = Field(..., ge=-90, le=90, description="Location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Location longitude")
    system_size_kwp: float = Field(..., gt=0, description="System size in kWp")
    years: int = Field(5, ge=1, le=10, description="Number of years to analyze")


class SeasonalProductionResponse(BaseModel):
    """Seasonal production response"""
    winter: float = Field(..., description="Winter production in kWh/day")
    spring: float = Field(..., description="Spring production in kWh/day")
    summer: float = Field(..., description="Summer production in kWh/day")
    autumn: float = Field(..., description="Autumn production in kWh/day")
    annual_average: float = Field(..., description="Annual average in kWh/day")
    total_annual: float = Field(..., description="Total annual production in kWh")


# API Endpoints

@router.post("/historical", response_model=List[WeatherDataResponse])
async def get_historical_weather(request: HistoricalWeatherRequest):
    """
    Get historical weather data for a location.
    
    Returns hourly weather data for the specified date range.
    """
    try:
        provider = WeatherProvider(request.provider)
        service = WeatherService(provider=provider)
        
        weather_data = await service.get_historical_weather(
            latitude=request.latitude,
            longitude=request.longitude,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return [
            WeatherDataResponse(
                timestamp=data.timestamp,
                temperature=data.temperature,
                cloud_cover=data.cloud_cover,
                solar_irradiance=data.solar_irradiance,
                wind_speed=data.wind_speed,
                precipitation=data.precipitation,
                humidity=data.humidity,
                pressure=data.pressure,
                uv_index=data.uv_index
            )
            for data in weather_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/historical/analysis", response_model=HistoricalWeatherSummaryResponse)
async def analyze_historical_weather(request: HistoricalAnalysisRequest):
    """
    Analyze historical weather patterns for a location.
    
    Returns comprehensive weather analysis including averages, seasonal variation,
    and monthly statistics.
    """
    try:
        provider = WeatherProvider(request.provider)
        service = WeatherService(provider=provider)
        
        summary = await service.analyze_historical_weather(
            latitude=request.latitude,
            longitude=request.longitude,
            years=request.years
        )
        
        # Determine climate zone
        climate_zone = service.determine_climate_zone(
            latitude=request.latitude,
            avg_temperature=summary.avg_temperature,
            avg_precipitation=sum(
                month_data.get("precipitation", 0)
                for month_data in summary.monthly_averages.values()
            )
        )
        
        return HistoricalWeatherSummaryResponse(
            location=summary.location,
            latitude=summary.latitude,
            longitude=summary.longitude,
            start_date=summary.start_date,
            end_date=summary.end_date,
            avg_temperature=summary.avg_temperature,
            avg_cloud_cover=summary.avg_cloud_cover,
            avg_solar_irradiance=summary.avg_solar_irradiance,
            total_sunshine_hours=summary.total_sunshine_hours,
            seasonal_variation=summary.seasonal_variation,
            monthly_averages=summary.monthly_averages,
            climate_zone=climate_zone.value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/production", response_model=List[ProductionForecastResponse])
async def forecast_production(request: ProductionForecastRequest):
    """
    Forecast solar production based on weather predictions.
    
    Returns daily production forecasts with confidence levels and weather factors.
    """
    try:
        provider = WeatherProvider(request.provider)
        service = WeatherService(provider=provider)
        
        forecasts = await service.forecast_production(
            latitude=request.latitude,
            longitude=request.longitude,
            system_size_kwp=request.system_size_kwp,
            days_ahead=request.days_ahead
        )
        
        return [
            ProductionForecastResponse(
                date=forecast.date,
                expected_production=forecast.expected_production,
                confidence=forecast.confidence,
                weather_factor=forecast.weather_factor,
                temperature_factor=forecast.temperature_factor,
                cloud_factor=forecast.cloud_factor,
                optimal_production=forecast.optimal_production
            )
            for forecast in forecasts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/climate-zone", response_model=ClimateZoneResponse)
async def determine_climate_zone(request: ClimateZoneRequest):
    """
    Determine climate zone for a location.
    
    Returns climate zone classification and solar potential assessment.
    """
    try:
        service = WeatherService()
        
        climate_zone = service.determine_climate_zone(
            latitude=request.latitude,
            avg_temperature=request.avg_temperature,
            avg_precipitation=request.avg_precipitation
        )
        
        # Climate zone descriptions and solar potential
        descriptions = {
            ClimateZone.POLAR: ("Polar climate with extreme cold and long winters", "Low to Moderate"),
            ClimateZone.COLD: ("Cold climate with harsh winters", "Moderate"),
            ClimateZone.TEMPERATE: ("Temperate climate with moderate seasons", "Good"),
            ClimateZone.SUBTROPICAL: ("Subtropical climate with warm temperatures", "Excellent"),
            ClimateZone.TROPICAL: ("Tropical climate with high temperatures year-round", "Excellent"),
            ClimateZone.ARID: ("Arid climate with low precipitation", "Excellent")
        }
        
        description, solar_potential = descriptions.get(
            climate_zone,
            ("Unknown climate", "Unknown")
        )
        
        return ClimateZoneResponse(
            climate_zone=climate_zone.value,
            description=description,
            solar_potential=solar_potential
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/real-time", response_model=WeatherDataResponse)
async def get_real_time_weather(request: RealTimeWeatherRequest):
    """
    Get current real-time weather data.
    
    Returns current weather conditions for the specified location.
    """
    try:
        provider = WeatherProvider(request.provider)
        service = WeatherService(provider=provider)
        
        weather = await service.get_real_time_weather(
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        return WeatherDataResponse(
            timestamp=weather.timestamp,
            temperature=weather.temperature,
            cloud_cover=weather.cloud_cover,
            solar_irradiance=weather.solar_irradiance,
            wind_speed=weather.wind_speed,
            precipitation=weather.precipitation,
            humidity=weather.humidity,
            pressure=weather.pressure,
            uv_index=weather.uv_index
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seasonal-production", response_model=SeasonalProductionResponse)
async def calculate_seasonal_production(request: SeasonalProductionRequest):
    """
    Calculate seasonal production variation.
    
    Returns expected production for each season based on historical weather data.
    """
    try:
        service = WeatherService()
        
        # Get historical analysis
        summary = await service.analyze_historical_weather(
            latitude=request.latitude,
            longitude=request.longitude,
            years=request.years
        )
        
        # Calculate seasonal production
        seasonal_production = service.calculate_seasonal_production_variation(
            historical_summary=summary,
            system_size_kwp=request.system_size_kwp
        )
        
        # Calculate annual statistics
        annual_average = sum(seasonal_production.values()) / len(seasonal_production)
        total_annual = annual_average * 365
        
        return SeasonalProductionResponse(
            winter=seasonal_production.get("winter", 0),
            spring=seasonal_production.get("spring", 0),
            summer=seasonal_production.get("summer", 0),
            autumn=seasonal_production.get("autumn", 0),
            annual_average=annual_average,
            total_annual=total_annual
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=List[str])
async def list_weather_providers():
    """
    List available weather data providers.
    
    Returns list of supported weather API providers.
    """
    return [provider.value for provider in WeatherProvider]


@router.get("/health")
async def weather_service_health():
    """
    Check weather service health.
    
    Returns health status of the weather integration service.
    """
    try:
        service = WeatherService()
        # Test with a simple request
        weather = await service.get_real_time_weather(52.52, 13.41)  # Berlin
        
        return {
            "status": "healthy",
            "provider": service.provider.value,
            "last_check": datetime.now().isoformat(),
            "test_location": "Berlin",
            "test_successful": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }
