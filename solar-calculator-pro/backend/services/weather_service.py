"""
Solar Weather Integration Service

Integrates weather data APIs for solar production forecasting and analysis.
Provides historical weather analysis, real-time monitoring, and climate zone calculations.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import aiohttp
from enum import Enum
import math


class WeatherProvider(Enum):
    """Supported weather data providers"""
    OPEN_METEO = "open_meteo"  # Free, no API key required
    OPENWEATHER = "openweather"
    WEATHERAPI = "weatherapi"
    VISUAL_CROSSING = "visual_crossing"


class ClimateZone(Enum):
    """Climate zones for solar calculations"""
    POLAR = "polar"
    COLD = "cold"
    TEMPERATE = "temperate"
    SUBTROPICAL = "subtropical"
    TROPICAL = "tropical"
    ARID = "arid"


@dataclass
class WeatherData:
    """Weather data point"""
    timestamp: datetime
    temperature: float  # Celsius
    cloud_cover: float  # Percentage 0-100
    solar_irradiance: float  # W/m²
    wind_speed: float  # m/s
    precipitation: float  # mm
    humidity: float  # Percentage 0-100
    pressure: float  # hPa
    uv_index: float


@dataclass
class HistoricalWeatherSummary:
    """Historical weather summary for a location"""
    location: str
    latitude: float
    longitude: float
    start_date: datetime
    end_date: datetime
    avg_temperature: float
    avg_cloud_cover: float
    avg_solar_irradiance: float
    total_sunshine_hours: float
    seasonal_variation: Dict[str, float]
    monthly_averages: Dict[str, Dict[str, float]]


@dataclass
class ProductionForecast:
    """Solar production forecast"""
    date: datetime
    expected_production: float  # kWh
    confidence: float  # Percentage 0-100
    weather_factor: float  # Multiplier based on weather
    temperature_factor: float  # Efficiency adjustment
    cloud_factor: float  # Reduction due to clouds
    optimal_production: float  # kWh under ideal conditions


class WeatherService:
    """
    Weather integration service for solar calculations.
    
    Provides:
    - Historical weather data analysis
    - Real-time weather monitoring
    - Weather-based production forecasting
    - Climate zone calculations
    - Seasonal variation analysis
    """
    
    def __init__(
        self,
        provider: WeatherProvider = WeatherProvider.OPEN_METEO,
        api_key: Optional[str] = None
    ):
        self.provider = provider
        self.api_key = api_key
        self.base_urls = {
            WeatherProvider.OPEN_METEO: "https://api.open-meteo.com/v1",
            WeatherProvider.OPENWEATHER: "https://api.openweathermap.org/data/2.5",
            WeatherProvider.WEATHERAPI: "https://api.weatherapi.com/v1",
            WeatherProvider.VISUAL_CROSSING: "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services"
        }
        
        # Temperature coefficient for solar panels (typical: -0.4% per °C above 25°C)
        self.temperature_coefficient = -0.004
        self.reference_temperature = 25.0  # °C
        
        # Standard Test Conditions (STC) irradiance
        self.stc_irradiance = 1000.0  # W/m²
    
    async def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[WeatherData]:
        """
        Fetch historical weather data for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            List of weather data points
        """
        if self.provider == WeatherProvider.OPEN_METEO:
            return await self._fetch_open_meteo_historical(
                latitude, longitude, start_date, end_date
            )
        elif self.provider == WeatherProvider.OPENWEATHER:
            return await self._fetch_openweather_historical(
                latitude, longitude, start_date, end_date
            )
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")
    
    async def _fetch_open_meteo_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[WeatherData]:
        """Fetch historical data from Open-Meteo API"""
        url = f"{self.base_urls[WeatherProvider.OPEN_METEO]}/archive"
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "hourly": "temperature_2m,cloudcover,shortwave_radiation,windspeed_10m,precipitation,relativehumidity_2m,surface_pressure",
            "timezone": "auto"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Weather API error: {response.status}")
                
                data = await response.json()
                return self._parse_open_meteo_response(data)
    
    def _parse_open_meteo_response(self, data: Dict[str, Any]) -> List[WeatherData]:
        """Parse Open-Meteo API response"""
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        
        weather_data = []
        for i, time_str in enumerate(times):
            weather_data.append(WeatherData(
                timestamp=datetime.fromisoformat(time_str),
                temperature=hourly.get("temperature_2m", [])[i] or 0,
                cloud_cover=hourly.get("cloudcover", [])[i] or 0,
                solar_irradiance=hourly.get("shortwave_radiation", [])[i] or 0,
                wind_speed=hourly.get("windspeed_10m", [])[i] or 0,
                precipitation=hourly.get("precipitation", [])[i] or 0,
                humidity=hourly.get("relativehumidity_2m", [])[i] or 0,
                pressure=hourly.get("surface_pressure", [])[i] or 1013.25,
                uv_index=0  # Not provided by Open-Meteo archive
            ))
        
        return weather_data
    
    async def _fetch_openweather_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[WeatherData]:
        """Fetch historical data from OpenWeather API (requires API key)"""
        if not self.api_key:
            raise ValueError("API key required for OpenWeather")
        
        # OpenWeather historical data is available through Time Machine API
        weather_data = []
        current_date = start_date
        
        async with aiohttp.ClientSession() as session:
            while current_date <= end_date:
                timestamp = int(current_date.timestamp())
                url = f"{self.base_urls[WeatherProvider.OPENWEATHER]}/onecall/timemachine"
                
                params = {
                    "lat": latitude,
                    "lon": longitude,
                    "dt": timestamp,
                    "appid": self.api_key,
                    "units": "metric"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather_data.extend(self._parse_openweather_response(data))
                
                current_date += timedelta(days=1)
        
        return weather_data
    
    def _parse_openweather_response(self, data: Dict[str, Any]) -> List[WeatherData]:
        """Parse OpenWeather API response"""
        hourly = data.get("hourly", [])
        
        weather_data = []
        for hour_data in hourly:
            weather_data.append(WeatherData(
                timestamp=datetime.fromtimestamp(hour_data.get("dt", 0)),
                temperature=hour_data.get("temp", 0),
                cloud_cover=hour_data.get("clouds", 0),
                solar_irradiance=self._estimate_irradiance_from_clouds(
                    hour_data.get("clouds", 0)
                ),
                wind_speed=hour_data.get("wind_speed", 0),
                precipitation=hour_data.get("rain", {}).get("1h", 0),
                humidity=hour_data.get("humidity", 0),
                pressure=hour_data.get("pressure", 1013.25),
                uv_index=hour_data.get("uvi", 0)
            ))
        
        return weather_data
    
    def _estimate_irradiance_from_clouds(self, cloud_cover: float) -> float:
        """
        Estimate solar irradiance from cloud cover percentage.
        
        Uses empirical formula: Irradiance = STC * (1 - 0.75 * cloud_cover/100)
        """
        return self.stc_irradiance * (1 - 0.75 * (cloud_cover / 100))
    
    async def analyze_historical_weather(
        self,
        latitude: float,
        longitude: float,
        years: int = 5
    ) -> HistoricalWeatherSummary:
        """
        Analyze historical weather patterns for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            years: Number of years to analyze
            
        Returns:
            Historical weather summary
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)
        
        weather_data = await self.get_historical_weather(
            latitude, longitude, start_date, end_date
        )
        
        # Calculate averages
        total_temp = sum(w.temperature for w in weather_data)
        total_clouds = sum(w.cloud_cover for w in weather_data)
        total_irradiance = sum(w.solar_irradiance for w in weather_data)
        count = len(weather_data)
        
        avg_temperature = total_temp / count if count > 0 else 0
        avg_cloud_cover = total_clouds / count if count > 0 else 0
        avg_solar_irradiance = total_irradiance / count if count > 0 else 0
        
        # Calculate sunshine hours (irradiance > 120 W/m² is considered sunshine)
        sunshine_threshold = 120.0
        sunshine_hours = sum(1 for w in weather_data if w.solar_irradiance > sunshine_threshold)
        
        # Calculate seasonal variation
        seasonal_variation = self._calculate_seasonal_variation(weather_data)
        
        # Calculate monthly averages
        monthly_averages = self._calculate_monthly_averages(weather_data)
        
        return HistoricalWeatherSummary(
            location=f"{latitude},{longitude}",
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            avg_temperature=avg_temperature,
            avg_cloud_cover=avg_cloud_cover,
            avg_solar_irradiance=avg_solar_irradiance,
            total_sunshine_hours=sunshine_hours,
            seasonal_variation=seasonal_variation,
            monthly_averages=monthly_averages
        )
    
    def _calculate_seasonal_variation(
        self,
        weather_data: List[WeatherData]
    ) -> Dict[str, float]:
        """Calculate seasonal variation in solar irradiance"""
        seasons = {
            "winter": [],
            "spring": [],
            "summer": [],
            "autumn": []
        }
        
        for data in weather_data:
            month = data.timestamp.month
            if month in [12, 1, 2]:
                seasons["winter"].append(data.solar_irradiance)
            elif month in [3, 4, 5]:
                seasons["spring"].append(data.solar_irradiance)
            elif month in [6, 7, 8]:
                seasons["summer"].append(data.solar_irradiance)
            else:
                seasons["autumn"].append(data.solar_irradiance)
        
        return {
            season: sum(values) / len(values) if values else 0
            for season, values in seasons.items()
        }
    
    def _calculate_monthly_averages(
        self,
        weather_data: List[WeatherData]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate monthly averages for all weather parameters"""
        monthly_data = {month: [] for month in range(1, 13)}
        
        for data in weather_data:
            monthly_data[data.timestamp.month].append(data)
        
        monthly_averages = {}
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        for month, data_list in monthly_data.items():
            if not data_list:
                continue
            
            count = len(data_list)
            monthly_averages[month_names[month - 1]] = {
                "temperature": sum(d.temperature for d in data_list) / count,
                "cloud_cover": sum(d.cloud_cover for d in data_list) / count,
                "solar_irradiance": sum(d.solar_irradiance for d in data_list) / count,
                "precipitation": sum(d.precipitation for d in data_list) / count,
                "humidity": sum(d.humidity for d in data_list) / count
            }
        
        return monthly_averages
    
    async def forecast_production(
        self,
        latitude: float,
        longitude: float,
        system_size_kwp: float,
        days_ahead: int = 7
    ) -> List[ProductionForecast]:
        """
        Forecast solar production based on weather predictions.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            system_size_kwp: System size in kWp
            days_ahead: Number of days to forecast
            
        Returns:
            List of production forecasts
        """
        # Fetch weather forecast
        weather_forecast = await self._get_weather_forecast(
            latitude, longitude, days_ahead
        )
        
        forecasts = []
        for weather in weather_forecast:
            # Calculate optimal production (STC conditions)
            optimal_production = system_size_kwp * 24  # kWh per day at full capacity
            
            # Apply weather factor (based on irradiance)
            weather_factor = weather.solar_irradiance / self.stc_irradiance
            
            # Apply temperature factor (efficiency decreases with temperature)
            temp_diff = weather.temperature - self.reference_temperature
            temperature_factor = 1 + (self.temperature_coefficient * temp_diff)
            
            # Apply cloud factor
            cloud_factor = 1 - (weather.cloud_cover / 100 * 0.75)
            
            # Calculate expected production
            expected_production = (
                optimal_production *
                weather_factor *
                temperature_factor *
                cloud_factor
            )
            
            # Calculate confidence based on weather stability
            confidence = self._calculate_forecast_confidence(weather, days_ahead)
            
            forecasts.append(ProductionForecast(
                date=weather.timestamp,
                expected_production=expected_production,
                confidence=confidence,
                weather_factor=weather_factor,
                temperature_factor=temperature_factor,
                cloud_factor=cloud_factor,
                optimal_production=optimal_production
            ))
        
        return forecasts
    
    async def _get_weather_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int
    ) -> List[WeatherData]:
        """Get weather forecast from API"""
        if self.provider == WeatherProvider.OPEN_METEO:
            return await self._fetch_open_meteo_forecast(latitude, longitude, days)
        else:
            raise NotImplementedError(f"Forecast for {self.provider} not implemented")
    
    async def _fetch_open_meteo_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int
    ) -> List[WeatherData]:
        """Fetch forecast from Open-Meteo API"""
        url = f"{self.base_urls[WeatherProvider.OPEN_METEO]}/forecast"
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,cloudcover,shortwave_radiation,windspeed_10m,precipitation,relativehumidity_2m,surface_pressure",
            "forecast_days": days,
            "timezone": "auto"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Weather API error: {response.status}")
                
                data = await response.json()
                return self._parse_open_meteo_response(data)
    
    def _calculate_forecast_confidence(
        self,
        weather: WeatherData,
        days_ahead: int
    ) -> float:
        """
        Calculate confidence level for forecast.
        
        Confidence decreases with:
        - Days ahead (further = less confident)
        - High cloud cover variability
        - Extreme weather conditions
        """
        # Base confidence decreases with time
        time_factor = max(0, 100 - (days_ahead * 10))
        
        # Reduce confidence for high cloud cover (more variable)
        cloud_factor = 100 - (weather.cloud_cover * 0.3)
        
        # Reduce confidence for extreme temperatures
        temp_factor = 100
        if weather.temperature < -10 or weather.temperature > 40:
            temp_factor = 70
        
        # Average all factors
        confidence = (time_factor + cloud_factor + temp_factor) / 3
        
        return max(0, min(100, confidence))
    
    def determine_climate_zone(
        self,
        latitude: float,
        avg_temperature: float,
        avg_precipitation: float
    ) -> ClimateZone:
        """
        Determine climate zone based on location and weather data.
        
        Args:
            latitude: Location latitude
            avg_temperature: Average annual temperature (°C)
            avg_precipitation: Average annual precipitation (mm)
            
        Returns:
            Climate zone classification
        """
        abs_lat = abs(latitude)
        
        # Polar zones (>66.5°)
        if abs_lat > 66.5:
            return ClimateZone.POLAR
        
        # Cold zones (45-66.5°)
        if abs_lat > 45:
            if avg_temperature < 10:
                return ClimateZone.COLD
            return ClimateZone.TEMPERATE
        
        # Temperate zones (30-45°)
        if abs_lat > 30:
            if avg_precipitation < 500:
                return ClimateZone.ARID
            return ClimateZone.TEMPERATE
        
        # Subtropical and tropical zones (<30°)
        if avg_temperature > 18:
            if avg_precipitation < 500:
                return ClimateZone.ARID
            elif abs_lat > 23.5:
                return ClimateZone.SUBTROPICAL
            else:
                return ClimateZone.TROPICAL
        
        return ClimateZone.TEMPERATE
    
    async def get_real_time_weather(
        self,
        latitude: float,
        longitude: float
    ) -> WeatherData:
        """
        Get current real-time weather data.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Current weather data
        """
        if self.provider == WeatherProvider.OPEN_METEO:
            return await self._fetch_open_meteo_current(latitude, longitude)
        else:
            raise NotImplementedError(f"Real-time for {self.provider} not implemented")
    
    async def _fetch_open_meteo_current(
        self,
        latitude: float,
        longitude: float
    ) -> WeatherData:
        """Fetch current weather from Open-Meteo API"""
        url = f"{self.base_urls[WeatherProvider.OPEN_METEO]}/forecast"
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
            "hourly": "temperature_2m,cloudcover,shortwave_radiation,windspeed_10m,precipitation,relativehumidity_2m,surface_pressure",
            "forecast_days": 1,
            "timezone": "auto"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Weather API error: {response.status}")
                
                data = await response.json()
                current = data.get("current_weather", {})
                hourly = data.get("hourly", {})
                
                # Get the first hourly data point (current hour)
                return WeatherData(
                    timestamp=datetime.now(),
                    temperature=current.get("temperature", 0),
                    cloud_cover=hourly.get("cloudcover", [0])[0],
                    solar_irradiance=hourly.get("shortwave_radiation", [0])[0],
                    wind_speed=current.get("windspeed", 0),
                    precipitation=hourly.get("precipitation", [0])[0],
                    humidity=hourly.get("relativehumidity_2m", [0])[0],
                    pressure=hourly.get("surface_pressure", [1013.25])[0],
                    uv_index=0
                )
    
    def calculate_seasonal_production_variation(
        self,
        historical_summary: HistoricalWeatherSummary,
        system_size_kwp: float
    ) -> Dict[str, float]:
        """
        Calculate expected seasonal production variation.
        
        Args:
            historical_summary: Historical weather summary
            system_size_kwp: System size in kWp
            
        Returns:
            Dictionary of seasonal production estimates (kWh/day)
        """
        seasonal_production = {}
        
        for season, avg_irradiance in historical_summary.seasonal_variation.items():
            # Calculate daily production for this season
            # Assuming 12 hours of daylight on average
            daily_hours = 12
            
            # Production = System Size * Hours * (Irradiance / STC Irradiance)
            production = (
                system_size_kwp *
                daily_hours *
                (avg_irradiance / self.stc_irradiance)
            )
            
            seasonal_production[season] = production
        
        return seasonal_production
