"""
Demo Script for Shading Analysis Service

Demonstrates all features of the solar shading analysis system.
"""

from datetime import datetime, timedelta
import json

from services.shading_analysis_service import (
    ShadingAnalysisService,
    ShadingAnalysisRequest,
    ObstacleModel,
    LocationModel
)


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_basic_analysis():
    """Demonstrate basic shading analysis"""
    print_section("DEMO 1: Basic Shading Analysis")
    
    # Define location (Berlin, Germany)
    location = LocationModel(
        latitude=52.52,
        longitude=13.405,
        timezone="Europe/Berlin",
        elevation=34.0
    )
    
    # Define obstacles
    obstacles = [
        ObstacleModel(
            id="building_south",
            type="building",
            height=15.0,
            distance=25.0,
            azimuth=180.0,
            width=12.0,
            description="Neighboring building to the south"
        ),
        ObstacleModel(
            id="tree_southeast",
            type="tree",
            height=10.0,
            distance=15.0,
            azimuth=135.0,
            width=6.0,
            description="Large oak tree"
        )
    ]
    
    # Create analysis request
    request = ShadingAnalysisRequest(
        location=location,
        obstacles=obstacles,
        module_tilt=30.0,
        module_azimuth=180.0,
        module_area=50.0,
        analysis_start_date=datetime(2024, 1, 1),
        analysis_end_date=datetime(2024, 12, 31),
        time_resolution=60
    )
    
    # Perform analysis
    service = ShadingAnalysisService()
    result = service.analyze_shading(request)
    
    # Display results
    print(f"📊 SHADING LOSS ANALYSIS")
    print(f"   Total Annual Loss: {result.losses.total_annual_loss_percent:.2f}%")
    print(f"   Affected Area: {result.losses.affected_area_percent:.2f}%")
    print(f"\n📅 MONTHLY LOSSES:")
    for month, loss in list(result.losses.monthly_losses.items())[:6]:
        print(f"   {month}: {loss:.2f}%")
    
    print(f"\n⚠️  CRITICAL PERIODS (Top 5):")
    for period in result.losses.critical_periods[:5]:
        print(f"   {period['date']}: {period['loss_percent']:.2f}% loss, {period['shaded_hours']:.1f} hours shaded")
    
    print(f"\n💡 OPTIMIZATION SUGGESTIONS ({len(result.suggestions)} total):")
    for i, suggestion in enumerate(result.suggestions[:3], 1):
        print(f"\n   {i}. {suggestion.type.upper()}")
        print(f"      {suggestion.description}")
        print(f"      Potential Improvement: {suggestion.potential_improvement_percent:.1f}%")
        print(f"      Difficulty: {suggestion.implementation_difficulty}")
        if suggestion.estimated_cost:
            print(f"      Estimated Cost: €{suggestion.estimated_cost:,.2f}")


def demo_quick_check():
    """Demonstrate quick shading check"""
    print_section("DEMO 2: Quick Shading Check")
    
    location = LocationModel(
        latitude=52.52,
        longitude=13.405,
        timezone="Europe/Berlin"
    )
    
    obstacles = [
        ObstacleModel(
            id="chimney",
            type="chimney",
            height=8.0,
            distance=12.0,
            azimuth=180.0,
            width=2.0
        )
    ]
    
    service = ShadingAnalysisService()
    result = service.quick_shading_check(
        location,
        obstacles,
        module_azimuth=180.0
    )
    
    print(f"🌞 CURRENT CONDITIONS")
    print(f"   Timestamp: {result['timestamp']}")
    print(f"   Sun Altitude: {result['sun_altitude']:.2f}°")
    print(f"   Sun Azimuth: {result['sun_azimuth']:.2f}°")
    print(f"   Currently Shaded: {'Yes ⚠️' if result['currently_shaded'] else 'No ✅'}")
    print(f"   Shading Percentage: {result['shading_percent']:.2f}%")
    
    if result['shading_obstacles']:
        print(f"\n   Shading Obstacles:")
        for obs in result['shading_obstacles']:
            print(f"      - {obs['obstacle_type']} ({obs['obstacle_id']}): {obs['shading_percent']:.2f}%")


def demo_sun_path():
    """Demonstrate sun path calculation"""
    print_section("DEMO 3: Sun Path Calculation")
    
    from services.shading_analysis_service import SunPositionCalculator
    
    location = LocationModel(
        latitude=52.52,
        longitude=13.405,
        timezone="Europe/Berlin"
    )
    
    # Calculate sun path for summer solstice
    summer_date = datetime(2024, 6, 21)
    sun_path = SunPositionCalculator.calculate_sun_path(
        location,
        summer_date,
        time_resolution=60
    )
    
    print(f"☀️  SUN PATH - Summer Solstice (June 21, 2024)")
    print(f"   Total daylight hours: {len(sun_path)}")
    print(f"\n   Sample positions:")
    
    # Show positions at key times
    key_times = [6, 9, 12, 15, 18]
    for hour in key_times:
        positions = [p for p in sun_path if p['hour'] == hour]
        if positions:
            pos = positions[0]
            print(f"   {hour:02d}:00 - Altitude: {pos['altitude']:6.2f}°, Azimuth: {pos['azimuth']:6.2f}°")
    
    # Calculate for winter solstice
    winter_date = datetime(2024, 12, 21)
    winter_path = SunPositionCalculator.calculate_sun_path(
        location,
        winter_date,
        time_resolution=60
    )
    
    print(f"\n❄️  SUN PATH - Winter Solstice (December 21, 2024)")
    print(f"   Total daylight hours: {len(winter_path)}")
    print(f"   Difference from summer: {len(sun_path) - len(winter_path)} hours")


def demo_shadow_profile():
    """Demonstrate shadow profile calculation"""
    print_section("DEMO 4: Daily Shadow Profile")
    
    from services.shading_analysis_service import (
        SunPositionCalculator,
        ObstacleShadowCalculator
    )
    
    location = LocationModel(
        latitude=52.52,
        longitude=13.405,
        timezone="Europe/Berlin"
    )
    
    obstacles = [
        ObstacleModel(
            id="building",
            type="building",
            height=20.0,
            distance=30.0,
            azimuth=180.0,
            width=15.0
        )
    ]
    
    date = datetime(2024, 6, 21)
    sun_path = SunPositionCalculator.calculate_sun_path(location, date, time_resolution=60)
    shadow_profile = ObstacleShadowCalculator.calculate_shadow_profile(
        obstacles,
        sun_path,
        module_azimuth=180.0
    )
    
    print(f"🌓 SHADOW PROFILE - June 21, 2024")
    print(f"   Total time periods analyzed: {len(shadow_profile)}")
    
    shaded_periods = [p for p in shadow_profile if p['shaded']]
    print(f"   Shaded periods: {len(shaded_periods)}")
    
    if shaded_periods:
        max_shading = max(p['shading_percent'] for p in shaded_periods)
        print(f"   Maximum shading: {max_shading:.2f}%")
        
        print(f"\n   Shaded time periods:")
        for period in shaded_periods[:5]:
            time = datetime.fromisoformat(period['timestamp']).strftime("%H:%M")
            print(f"   {time} - {period['shading_percent']:.2f}% shaded")


def demo_optimization_suggestions():
    """Demonstrate optimization suggestions"""
    print_section("DEMO 5: Optimization Suggestions")
    
    from services.shading_analysis_service import ShadingOptimizationSuggester
    
    location = LocationModel(
        latitude=52.52,
        longitude=13.405,
        timezone="Europe/Berlin"
    )
    
    # Scenario with multiple obstacles
    obstacles = [
        ObstacleModel(
            id="building_1",
            type="building",
            height=18.0,
            distance=22.0,
            azimuth=180.0,
            width=12.0
        ),
        ObstacleModel(
            id="tree_1",
            type="tree",
            height=14.0,
            distance=10.0,
            azimuth=160.0,
            width=6.0
        ),
        ObstacleModel(
            id="tree_2",
            type="tree",
            height=12.0,
            distance=8.0,
            azimuth=200.0,
            width=5.0
        )
    ]
    
    suggestions = ShadingOptimizationSuggester.generate_all_suggestions(
        current_tilt=25.0,
        current_azimuth=180.0,
        obstacles=obstacles,
        location=location
    )
    
    print(f"💡 OPTIMIZATION SUGGESTIONS")
    print(f"   Total suggestions: {len(suggestions)}")
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n   {i}. {suggestion.type.replace('_', ' ').upper()}")
        print(f"      Description: {suggestion.description}")
        print(f"      Potential Improvement: {suggestion.potential_improvement_percent:.1f}%")
        print(f"      Implementation: {suggestion.implementation_difficulty}")
        if suggestion.estimated_cost:
            print(f"      Estimated Cost: €{suggestion.estimated_cost:,.2f}")


def demo_visualization_data():
    """Demonstrate visualization data generation"""
    print_section("DEMO 6: Visualization Data")
    
    from services.shading_analysis_service import ShadingVisualizationGenerator
    
    location = LocationModel(
        latitude=52.52,
        longitude=13.405,
        timezone="Europe/Berlin"
    )
    
    obstacles = [
        ObstacleModel(
            id="building",
            type="building",
            height=15.0,
            distance=20.0,
            azimuth=180.0,
            width=10.0
        )
    ]
    
    viz_gen = ShadingVisualizationGenerator()
    
    # Generate heatmap data
    start_date = datetime(2024, 1, 1)
    heatmap = viz_gen.generate_heatmap_data(
        location,
        obstacles,
        module_azimuth=180.0,
        start_date=start_date,
        days=365
    )
    
    print(f"📊 ANNUAL SHADING HEATMAP")
    print(f"   Data points: {len(heatmap['data'])}")
    print(f"   Minimum shading: {heatmap['min_shading']:.2f}%")
    print(f"   Maximum shading: {heatmap['max_shading']:.2f}%")
    
    # Show sample data points
    print(f"\n   Sample data points:")
    for data_point in heatmap['data'][:5]:
        print(f"   {data_point['date']}: {data_point['avg_shading_percent']:.2f}% average shading")
    
    # Generate obstacle shadows
    sun_path = viz_gen.generate_sun_path_data(location, start_date)
    noon_sun = [s for s in sun_path if s['hour'] == 12]
    
    if noon_sun:
        shadows = viz_gen.generate_obstacle_shadows(
            obstacles,
            noon_sun[0]['altitude'],
            noon_sun[0]['azimuth']
        )
        
        print(f"\n🌑 OBSTACLE SHADOWS (at solar noon)")
        for shadow in shadows:
            print(f"   {shadow['obstacle_type']} ({shadow['obstacle_id']})")
            print(f"      Shadow length: {shadow['shadow_length']:.2f}m")
            print(f"      Obstacle height: {shadow['obstacle_height']:.2f}m")
            print(f"      Distance: {shadow['obstacle_distance']:.2f}m")


def demo_seasonal_comparison():
    """Demonstrate seasonal shading comparison"""
    print_section("DEMO 7: Seasonal Comparison")
    
    location = LocationModel(
        latitude=52.52,
        longitude=13.405,
        timezone="Europe/Berlin"
    )
    
    obstacles = [
        ObstacleModel(
            id="building",
            type="building",
            height=15.0,
            distance=20.0,
            azimuth=180.0,
            width=10.0
        )
    ]
    
    service = ShadingAnalysisService()
    
    seasons = [
        ("Winter", datetime(2024, 12, 21)),
        ("Spring", datetime(2024, 3, 21)),
        ("Summer", datetime(2024, 6, 21)),
        ("Fall", datetime(2024, 9, 21))
    ]
    
    print(f"🌍 SEASONAL SHADING COMPARISON")
    print(f"\n   Season      | Loss % | Daylight Hours")
    print(f"   " + "-" * 45)
    
    for season_name, date in seasons:
        request = ShadingAnalysisRequest(
            location=location,
            obstacles=obstacles,
            module_tilt=30.0,
            module_azimuth=180.0,
            module_area=50.0,
            analysis_start_date=date,
            analysis_end_date=date + timedelta(days=1),
            time_resolution=60
        )
        
        result = service.analyze_shading(request)
        
        # Get daylight hours
        from services.shading_analysis_service import SunPositionCalculator
        sun_path = SunPositionCalculator.calculate_sun_path(location, date)
        daylight_hours = len(sun_path)
        
        print(f"   {season_name:12} | {result.losses.total_annual_loss_percent:5.2f}% | {daylight_hours:2d} hours")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  SOLAR SHADING ANALYSIS SERVICE - COMPREHENSIVE DEMO")
    print("=" * 80)
    
    try:
        demo_basic_analysis()
        demo_quick_check()
        demo_sun_path()
        demo_shadow_profile()
        demo_optimization_suggestions()
        demo_visualization_data()
        demo_seasonal_comparison()
        
        print("\n" + "=" * 80)
        print("  ✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
