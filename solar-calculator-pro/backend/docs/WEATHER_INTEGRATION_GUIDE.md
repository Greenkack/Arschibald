# Solar Weather Integration Guide

## Overview

The Weather Integration Service provides comprehensive weather data integration for solar production forecasting and analysis. It supports multiple weather data providers and offers historical analysis, real-time monitoring, and production forecasting capabilities.

## Features

### 1. Historical Weather Analysis
- Fetch historical weather data for any location
- Analyze weather patterns over multiple years
- Calculate seasonal variations
- Generate monthly averages
- Determine sunshine hours

### 2. Production Forecasting
- Weather-based production forecasts (up to 14 days)
- Confidence levels for each forecast
- Temperature impact calculations
- Cloud cover adjustments
- Optimal vs. expected production comparison

### 3. Climate Zone Determination
- Automatic climate zone classification
- Solar potential assessment
- Location-based recommendations

### 4. Real-Time Weather Monitoring
- Current weather conditions
- Live production estimates
- Instant performance indicators

### 5. Seasonal Analysis
- Seasonal production variation
- Annual production estimates
- Month-by-month breakdown

## Supported Weather Providers

### Open-Meteo (Default)
- **Free**: No API key required
- **Coverage**: Global
- **Data**: Historical (1940-present), Forecast (16 days)
- **Resolution**: Hourly
- **Best for**: Development, testing, and production use

### OpenWeather
- **Requires**: API key
- **Coverage**: Global
- **Data**: Historical, Current, Forecast
- **Resolution**: Hourly
- **Best for**: Production use with paid plan

### WeatherAPI
- **Requires**: API key
- **Coverage**: Global
- **Data**: Historical, Current, Forecast
- **Resolution**: Hourly
- **Best for**: Production use

### Visual Crossing
- **Requires**: API key
- **Coverage**: Global
- **Data**: Historical, Current, Forecast
- **Resolution**: Hourly
- **Best for**: Advanced analytics

## Installation

```bash
# Install required dependencies
pip install aiohttp

# The service is ready to use with Open-Meteo (no API key needed)
```

## Quick Start

### Basic Usage

```python
from services.weather_service import WeatherService, WeatherProvider

# Initialize service (uses Open-Meteo by default)
service = WeatherService()

# Or specify a provider with API key
service = WeatherService(
    provider=WeatherProvider.OPENWEATHER,
    api_key="your_api_key_here"
)
```

### Get Historical Weather Data

```python
from datetime import datetime, timedelta

# Define location and date range
latitude = 52.52  # Berlin
longitude = 13.41
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 1, 31)

# Fetch historical data
weather_data = await service.get_historical_weather(
    latitude=latitude,
    longitude=longitude,
    start_date=start_date,
    end_date=end_date
)

# Process data
for data in weather_data:
    print(f"{data.timestamp}: {data.temperature}°C, {data.solar_irradiance} W/m²")
```

### Analyze Historical Weather

```python
# Analyze 5 years of historical data
summary = await service.analyze_historical_weather(
    latitude=52.52,
    longitude=13.41,
    years=5
)

print(f"Average Temperature: {summary.avg_temperature}°C")
print(f"Average Solar Irradiance: {summary.avg_solar_irradiance} W/m²")
print(f"Seasonal Variation: {summary.seasonal_variation}")
```

### Forecast Production

```python
# Forecast production for 7 days
forecasts = await service.forecast_production(
    latitude=52.52,
    longitude=13.41,
    system_size_kwp=10.0,
    days_ahead=7
)

for forecast in forecasts:
    print(f"{forecast.date.date()}: {forecast.expected_production:.1f} kWh")
    print(f"  Confidence: {forecast.confidence:.1f}%")
    print(f"  Weather Factor: {forecast.weather_factor:.2f}")
```

### Get Real-Time Weather

```python
# Get current weather
weather = await service.get_real_time_weather(
    latitude=52.52,
    longitude=13.41
)

print(f"Current Temperature: {weather.temperature}°C")
print(f"Solar Irradiance: {weather.solar_irradiance} W/m²")
print(f"Cloud Cover: {weather.cloud_cover}%")
```

### Determine Climate Zone

```python
# Determine climate zone
climate_zone = service.determine_climate_zone(
    latitude=52.52,
    avg_temperature=10.0,
    avg_precipitation=600.0
)

print(f"Climate Zone: {climate_zone.value}")
```

### Calculate Seasonal Production

```python
# Get historical summary first
summary = await service.analyze_historical_weather(
    latitude=52.52,
    longitude=13.41,
    years=5
)

# Calculate seasonal production
production = service.calculate_seasonal_production_variation(
    historical_summary=summary,
    system_size_kwp=10.0
)

print(f"Winter: {production['winter']:.1f} kWh/day")
print(f"Spring: {production['spring']:.1f} kWh/day")
print(f"Summer: {production['summer']:.1f} kWh/day")
print(f"Autumn: {production['autumn']:.1f} kWh/day")
```

## API Endpoints

### POST /api/v1/weather/historical
Get historical weather data for a location.

**Request:**
```json
{
  "latitude": 52.52,
  "longitude": 13.41,
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-31T23:59:59",
  "provider": "open_meteo"
}
```

**Response:**
```json
[
  {
    "timestamp": "2024-01-01T12:00:00",
    "temperature": 5.2,
    "cloud_cover": 45.0,
    "solar_irradiance": 350.0,
    "wind_speed": 4.5,
    "precipitation": 0.0,
    "humidity": 75.0,
    "pressure": 1013.25,
    "uv_index": 1.0
  }
]
```

### POST /api/v1/weather/historical/analysis
Analyze historical weather patterns.

**Request:**
```json
{
  "latitude": 52.52,
  "longitude": 13.41,
  "years": 5,
  "provider": "open_meteo"
}
```

**Response:**
```json
{
  "location": "52.52,13.41",
  "latitude": 52.52,
  "longitude": 13.41,
  "start_date": "2019-01-01T00:00:00",
  "end_date": "2024-01-01T00:00:00",
  "avg_temperature": 10.5,
  "avg_cloud_cover": 55.0,
  "avg_solar_irradiance": 425.0,
  "total_sunshine_hours": 1650.0,
  "seasonal_variation": {
    "winter": 200.0,
    "spring": 500.0,
    "summer": 700.0,
    "autumn": 400.0
  },
  "monthly_averages": {
    "January": {
      "temperature": 2.0,
      "cloud_cover": 70.0,
      "solar_irradiance": 150.0
    }
  },
  "climate_zone": "temperate"
}
```

### POST /api/v1/weather/forecast/production
Forecast solar production based on weather.

**Request:**
```json
{
  "latitude": 52.52,
  "longitude": 13.41,
  "system_size_kwp": 10.0,
  "days_ahead": 7,
  "provider": "open_meteo"
}
```

**Response:**
```json
[
  {
    "date": "2024-01-15T00:00:00",
    "expected_production": 25.5,
    "confidence": 85.0,
    "weather_factor": 0.65,
    "temperature_factor": 0.98,
    "cloud_factor": 0.75,
    "optimal_production": 240.0
  }
]
```

### POST /api/v1/weather/real-time
Get current weather conditions.

**Request:**
```json
{
  "latitude": 52.52,
  "longitude": 13.41,
  "provider": "open_meteo"
}
```

**Response:**
```json
{
  "timestamp": "2024-01-15T14:30:00",
  "temperature": 8.5,
  "cloud_cover": 35.0,
  "solar_irradiance": 450.0,
  "wind_speed": 5.2,
  "precipitation": 0.0,
  "humidity": 68.0,
  "pressure": 1015.5,
  "uv_index": 2.0
}
```

### POST /api/v1/weather/climate-zone
Determine climate zone for a location.

**Request:**
```json
{
  "latitude": 52.52,
  "longitude": 13.41,
  "avg_temperature": 10.5,
  "avg_precipitation": 600.0
}
```

**Response:**
```json
{
  "climate_zone": "temperate",
  "description": "Temperate climate with moderate seasons",
  "solar_potential": "Good"
}
```

### POST /api/v1/weather/seasonal-production
Calculate seasonal production variation.

**Request:**
```json
{
  "latitude": 52.52,
  "longitude": 13.41,
  "system_size_kwp": 10.0,
  "years": 5
}
```

**Response:**
```json
{
  "winter": 15.5,
  "spring": 35.2,
  "summer": 48.7,
  "autumn": 28.3,
  "annual_average": 31.9,
  "total_annual": 11643.5
}
```

## Climate Zones

### Polar
- **Latitude**: >66.5°
- **Characteristics**: Extreme cold, long winters
- **Solar Potential**: Low to Moderate
- **Considerations**: Long summer days compensate for low sun angle

### Cold
- **Latitude**: 45-66.5°
- **Characteristics**: Harsh winters, moderate summers
- **Solar Potential**: Moderate
- **Considerations**: Good summer production, poor winter production

### Temperate
- **Latitude**: 30-45°
- **Characteristics**: Moderate seasons
- **Solar Potential**: Good
- **Considerations**: Balanced production throughout year

### Subtropical
- **Latitude**: 23.5-30°
- **Characteristics**: Warm temperatures
- **Solar Potential**: Excellent
- **Considerations**: High irradiance, consistent production

### Tropical
- **Latitude**: <23.5°
- **Characteristics**: High temperatures year-round
- **Solar Potential**: Excellent
- **Considerations**: Consistent high irradiance, temperature effects

### Arid
- **Characteristics**: Low precipitation
- **Solar Potential**: Excellent
- **Considerations**: Clear skies, minimal cloud cover

## Production Calculation

### Weather Factor
```
weather_factor = solar_irradiance / 1000.0
```
Where 1000 W/m² is Standard Test Conditions (STC) irradiance.

### Temperature Factor
```
temperature_factor = 1 + (temperature_coefficient × (temperature - 25°C))
```
Where temperature_coefficient is typically -0.004 (-0.4% per °C).

### Cloud Factor
```
cloud_factor = 1 - (cloud_cover / 100 × 0.75)
```
Clouds reduce irradiance by approximately 75% at 100% coverage.

### Expected Production
```
expected_production = system_size_kwp × hours × weather_factor × temperature_factor × cloud_factor
```

## Best Practices

### 1. Use Appropriate Time Ranges
- Historical analysis: 3-5 years for reliable patterns
- Forecasting: 7-14 days for reasonable accuracy
- Real-time: Update every 15-30 minutes

### 2. Handle API Errors Gracefully
```python
try:
    weather = await service.get_real_time_weather(lat, lon)
except Exception as e:
    # Fallback to cached data or default values
    logger.error(f"Weather API error: {e}")
```

### 3. Cache Historical Data
Historical data doesn't change, so cache it to reduce API calls:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_historical_summary(lat, lon, years):
    return await service.analyze_historical_weather(lat, lon, years)
```

### 4. Validate Coordinates
```python
def validate_coordinates(lat, lon):
    if not (-90 <= lat <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    if not (-180 <= lon <= 180):
        raise ValueError("Longitude must be between -180 and 180")
```

### 5. Consider Time Zones
Weather data is returned in the location's local timezone. Ensure proper timezone handling when displaying or storing data.

## Troubleshooting

### API Rate Limits
- Open-Meteo: No rate limits for reasonable use
- OpenWeather: Check your plan's rate limits
- Solution: Implement caching and request throttling

### Missing Data
- Some historical periods may have gaps
- Solution: Interpolate missing values or use nearby locations

### Inaccurate Forecasts
- Weather forecasts become less accurate beyond 7 days
- Solution: Update forecasts daily and show confidence levels

### Timezone Issues
- Weather data may be in different timezones
- Solution: Always convert to UTC for storage, local time for display

## Performance Optimization

### 1. Batch Requests
```python
# Instead of multiple single requests
locations = [(52.52, 13.41), (48.85, 2.35), (51.51, -0.13)]
tasks = [service.get_real_time_weather(lat, lon) for lat, lon in locations]
results = await asyncio.gather(*tasks)
```

### 2. Use Async Operations
All weather service methods are async for optimal performance:
```python
# Good - concurrent execution
weather_task = service.get_real_time_weather(lat, lon)
forecast_task = service.forecast_production(lat, lon, size, days)
weather, forecast = await asyncio.gather(weather_task, forecast_task)
```

### 3. Implement Caching
```python
from datetime import timedelta
import redis

cache = redis.Redis()

async def get_weather_cached(lat, lon):
    key = f"weather:{lat}:{lon}"
    cached = cache.get(key)
    
    if cached:
        return json.loads(cached)
    
    weather = await service.get_real_time_weather(lat, lon)
    cache.setex(key, timedelta(minutes=15), json.dumps(weather))
    
    return weather
```

## Examples

See `demo_weather_integration.py` for comprehensive examples of all features.

## Support

For issues or questions:
1. Check the API documentation
2. Review the demo script
3. Check provider-specific documentation
4. Contact support

## License

This weather integration service is part of the Solar Calculator Pro application.
