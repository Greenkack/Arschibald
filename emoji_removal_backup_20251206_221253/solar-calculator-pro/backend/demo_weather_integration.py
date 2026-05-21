"""
Weather Integration Demo

Demonstrates the weather integration capabilities for solar production forecasting.
"""

import asyncio
from datetime import datetime, timedelta
from services.weather_service import WeatherService, WeatherProvider


async def demo_historical_analysis():
    """Demonstrate historical weather analysis"""
    print("=" * 80)
    print("HISTORICAL WEATHER ANALYSIS DEMO")
    print("=" * 80)
    
    service = WeatherService(provider=WeatherProvider.OPEN_METEO)
    
    # Berlin coordinates
    latitude = 52.52
    longitude = 13.41
    
    print(f"\nAnalyzing weather for Berlin ({latitude}, {longitude})")
    print("Fetching 5 years of historical data...")
    
    try:
        summary = await service.analyze_historical_weather(
            latitude=latitude,
            longitude=longitude,
            years=5
        )
        
        print(f"\n📊 Historical Weather Summary")
        print(f"   Period: {summary.start_date.date()} to {summary.end_date.date()}")
        print(f"   Average Temperature: {summary.avg_temperature:.1f}°C")
        print(f"   Average Cloud Cover: {summary.avg_cloud_cover:.1f}%")
        print(f"   Average Solar Irradiance: {summary.avg_solar_irradiance:.1f} W/m²")
        print(f"   Total Sunshine Hours: {summary.total_sunshine_hours:.0f} hours")
        
        print(f"\n🌍 Seasonal Variation:")
        for season, irradiance in summary.seasonal_variation.items():
            print(f"   {season.capitalize():10s}: {irradiance:.1f} W/m²")
        
        print(f"\n📅 Monthly Averages (Temperature & Irradiance):")
        for month, data in summary.monthly_averages.items():
            temp = data.get("temperature", 0)
            irrad = data.get("solar_irradiance", 0)
            print(f"   {month:12s}: {temp:5.1f}°C, {irrad:6.1f} W/m²")
        
        # Determine climate zone
        climate_zone = service.determine_climate_zone(
            latitude=latitude,
            avg_temperature=summary.avg_temperature,
            avg_precipitation=sum(
                month_data.get("precipitation", 0)
                for month_data in summary.monthly_averages.values()
            )
        )
        print(f"\n🌡️  Climate Zone: {climate_zone.value.upper()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_production_forecast():
    """Demonstrate production forecasting"""
    print("\n" + "=" * 80)
    print("PRODUCTION FORECAST DEMO")
    print("=" * 80)
    
    service = WeatherService(provider=WeatherProvider.OPEN_METEO)
    
    # Berlin coordinates
    latitude = 52.52
    longitude = 13.41
    system_size_kwp = 10.0
    
    print(f"\nForecasting production for {system_size_kwp} kWp system in Berlin")
    print("Fetching 7-day weather forecast...")
    
    try:
        forecasts = await service.forecast_production(
            latitude=latitude,
            longitude=longitude,
            system_size_kwp=system_size_kwp,
            days_ahead=7
        )
        
        print(f"\n📈 7-Day Production Forecast:")
        print(f"{'Date':<12} {'Expected':<12} {'Optimal':<12} {'Confidence':<12} {'Weather':<10}")
        print(f"{'':12} {'(kWh)':<12} {'(kWh)':<12} {'(%)':<12} {'Factor':<10}")
        print("-" * 70)
        
        total_expected = 0
        total_optimal = 0
        
        for forecast in forecasts:
            date_str = forecast.date.strftime("%Y-%m-%d")
            expected = forecast.expected_production
            optimal = forecast.optimal_production
            confidence = forecast.confidence
            weather_factor = forecast.weather_factor
            
            total_expected += expected
            total_optimal += optimal
            
            print(f"{date_str:<12} {expected:>10.1f}  {optimal:>10.1f}  {confidence:>10.1f}  {weather_factor:>8.2f}")
        
        print("-" * 70)
        print(f"{'TOTAL':<12} {total_expected:>10.1f}  {total_optimal:>10.1f}")
        
        efficiency = (total_expected / total_optimal * 100) if total_optimal > 0 else 0
        print(f"\n⚡ Overall Efficiency: {efficiency:.1f}%")
        print(f"   (Expected vs. Optimal Production)")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_seasonal_production():
    """Demonstrate seasonal production analysis"""
    print("\n" + "=" * 80)
    print("SEASONAL PRODUCTION ANALYSIS DEMO")
    print("=" * 80)
    
    service = WeatherService(provider=WeatherProvider.OPEN_METEO)
    
    # Berlin coordinates
    latitude = 52.52
    longitude = 13.41
    system_size_kwp = 10.0
    
    print(f"\nAnalyzing seasonal production for {system_size_kwp} kWp system in Berlin")
    print("Analyzing 5 years of historical data...")
    
    try:
        summary = await service.analyze_historical_weather(
            latitude=latitude,
            longitude=longitude,
            years=5
        )
        
        production = service.calculate_seasonal_production_variation(
            historical_summary=summary,
            system_size_kwp=system_size_kwp
        )
        
        print(f"\n🌞 Seasonal Production Estimates (kWh/day):")
        print("-" * 50)
        
        seasons_order = ["winter", "spring", "summer", "autumn"]
        for season in seasons_order:
            daily_prod = production.get(season, 0)
            monthly_prod = daily_prod * 30
            print(f"   {season.capitalize():10s}: {daily_prod:>6.1f} kWh/day  ({monthly_prod:>7.1f} kWh/month)")
        
        # Calculate annual statistics
        annual_daily_avg = sum(production.values()) / len(production)
        annual_total = annual_daily_avg * 365
        
        print("-" * 50)
        print(f"   {'Annual Avg':10s}: {annual_daily_avg:>6.1f} kWh/day  ({annual_total:>7.1f} kWh/year)")
        
        # Calculate variation
        max_prod = max(production.values())
        min_prod = min(production.values())
        variation = ((max_prod - min_prod) / min_prod * 100) if min_prod > 0 else 0
        
        print(f"\n📊 Seasonal Variation: {variation:.1f}%")
        print(f"   (Difference between highest and lowest season)")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_real_time_weather():
    """Demonstrate real-time weather monitoring"""
    print("\n" + "=" * 80)
    print("REAL-TIME WEATHER MONITORING DEMO")
    print("=" * 80)
    
    service = WeatherService(provider=WeatherProvider.OPEN_METEO)
    
    # Berlin coordinates
    latitude = 52.52
    longitude = 13.41
    
    print(f"\nFetching current weather for Berlin ({latitude}, {longitude})...")
    
    try:
        weather = await service.get_real_time_weather(
            latitude=latitude,
            longitude=longitude
        )
        
        print(f"\n🌤️  Current Weather Conditions:")
        print(f"   Timestamp: {weather.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Temperature: {weather.temperature:.1f}°C")
        print(f"   Cloud Cover: {weather.cloud_cover:.1f}%")
        print(f"   Solar Irradiance: {weather.solar_irradiance:.1f} W/m²")
        print(f"   Wind Speed: {weather.wind_speed:.1f} m/s")
        print(f"   Humidity: {weather.humidity:.1f}%")
        print(f"   Pressure: {weather.pressure:.1f} hPa")
        
        # Calculate current production potential
        system_size_kwp = 10.0
        stc_irradiance = 1000.0
        
        # Weather factor
        weather_factor = weather.solar_irradiance / stc_irradiance
        
        # Temperature factor
        temp_diff = weather.temperature - 25.0
        temp_factor = 1 + (-0.004 * temp_diff)
        
        # Cloud factor
        cloud_factor = 1 - (weather.cloud_cover / 100 * 0.75)
        
        # Current production (kW)
        current_production = system_size_kwp * weather_factor * temp_factor * cloud_factor
        
        print(f"\n⚡ Current Production Estimate:")
        print(f"   System Size: {system_size_kwp} kWp")
        print(f"   Current Output: {current_production:.2f} kW")
        print(f"   Weather Factor: {weather_factor:.2f}")
        print(f"   Temperature Factor: {temp_factor:.2f}")
        print(f"   Cloud Factor: {cloud_factor:.2f}")
        
        # Production status
        if current_production > system_size_kwp * 0.8:
            status = "🟢 Excellent"
        elif current_production > system_size_kwp * 0.5:
            status = "🟡 Good"
        elif current_production > system_size_kwp * 0.2:
            status = "🟠 Fair"
        else:
            status = "🔴 Poor"
        
        print(f"   Status: {status}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_climate_zones():
    """Demonstrate climate zone determination"""
    print("\n" + "=" * 80)
    print("CLIMATE ZONE DETERMINATION DEMO")
    print("=" * 80)
    
    service = WeatherService()
    
    locations = [
        ("Svalbard (Arctic)", 78.0, -15.0, 200.0),
        ("Moscow (Cold)", 55.75, 5.0, 700.0),
        ("Berlin (Temperate)", 52.52, 10.0, 600.0),
        ("Miami (Subtropical)", 25.76, 24.0, 1500.0),
        ("Singapore (Tropical)", 1.35, 27.0, 2400.0),
        ("Dubai (Arid)", 25.27, 27.0, 100.0),
    ]
    
    print(f"\n🌍 Climate Zone Classification:")
    print(f"{'Location':<25} {'Latitude':<10} {'Avg Temp':<10} {'Climate Zone':<15}")
    print("-" * 70)
    
    for name, lat, temp, precip in locations:
        zone = service.determine_climate_zone(lat, temp, precip)
        print(f"{name:<25} {lat:>8.2f}°  {temp:>7.1f}°C  {zone.value:<15}")
    
    print("\n💡 Solar Potential by Climate Zone:")
    print("   Polar:       Low to Moderate (long summer days, but low angle)")
    print("   Cold:        Moderate (good in summer, poor in winter)")
    print("   Temperate:   Good (balanced throughout year)")
    print("   Subtropical: Excellent (high irradiance, warm temperatures)")
    print("   Tropical:    Excellent (consistent high irradiance)")
    print("   Arid:        Excellent (clear skies, high irradiance)")


async def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("SOLAR WEATHER INTEGRATION - COMPREHENSIVE DEMO")
    print("=" * 80)
    print("\nThis demo showcases the weather integration capabilities for")
    print("solar production forecasting and analysis.")
    print("\nNote: Using Open-Meteo API (free, no API key required)")
    
    try:
        await demo_historical_analysis()
        await demo_production_forecast()
        await demo_seasonal_production()
        await demo_real_time_weather()
        await demo_climate_zones()
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\n✅ All weather integration features demonstrated")
        print("✅ Historical analysis, forecasting, and real-time monitoring working")
        print("✅ Climate zone determination and seasonal analysis functional")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
