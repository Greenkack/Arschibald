"""
Solar Shading Analysis Service

Implements comprehensive shading analysis algorithms for solar installations:
- Time-based shading simulation
- Obstacle detection and modeling
- Shading loss calculations
- Optimization suggestions
- Visualization data generation
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import math
import numpy as np
from pydantic import BaseModel


# ============================================================================
# Data Models
# ============================================================================

class ObstacleModel(BaseModel):
    """Model for obstacles that cause shading"""
    id: str
    type: str  # 'building', 'tree', 'chimney', 'other'
    height: float  # meters
    distance: float  # meters from installation
    azimuth: float  # degrees (0=North, 90=East, 180=South, 270=West)
    width: float  # meters
    description: Optional[str] = None


class LocationModel(BaseModel):
    """Geographic location for sun path calculations"""
    latitude: float
    longitude: float
    timezone: str
    elevation: float = 0.0  # meters above sea level


class ShadingAnalysisRequest(BaseModel):
    """Request model for shading analysis"""
    location: LocationModel
    obstacles: List[ObstacleModel]
    module_tilt: float  # degrees
    module_azimuth: float  # degrees
    module_area: float  # square meters
    analysis_start_date: datetime
    analysis_end_date: datetime
    time_resolution: int = 60  # minutes


class ShadingLossResult(BaseModel):
    """Result of shading loss calculation"""
    total_annual_loss_percent: float
    monthly_losses: Dict[str, float]
    hourly_shading_profile: List[Dict[str, Any]]
    critical_periods: List[Dict[str, Any]]
    affected_area_percent: float


class ShadingVisualization(BaseModel):
    """Data for shading visualization"""
    sun_path_data: List[Dict[str, Any]]
    shading_timeline: List[Dict[str, Any]]
    obstacle_shadows: List[Dict[str, Any]]
    heatmap_data: Dict[str, Any]


class OptimizationSuggestion(BaseModel):
    """Optimization suggestion to reduce shading"""
    type: str  # 'tilt_adjustment', 'azimuth_adjustment', 'module_relocation', 'obstacle_removal'
    description: str
    potential_improvement_percent: float
    implementation_difficulty: str  # 'easy', 'moderate', 'difficult'
    estimated_cost: Optional[float] = None


class ShadingAnalysisResponse(BaseModel):
    """Complete shading analysis response"""
    losses: ShadingLossResult
    visualization: ShadingVisualization
    suggestions: List[OptimizationSuggestion]
    analysis_metadata: Dict[str, Any]


# ============================================================================
# Sun Position Calculator
# ============================================================================

class SunPositionCalculator:
    """Calculate sun position for any location and time"""
    
    @staticmethod
    def calculate_sun_position(
        latitude: float,
        longitude: float,
        timestamp: datetime
    ) -> Tuple[float, float]:
        """
        Calculate sun altitude and azimuth angles
        
        Returns:
            Tuple of (altitude, azimuth) in degrees
        """
        # Convert to radians
        lat_rad = math.radians(latitude)
        
        # Calculate day of year
        day_of_year = timestamp.timetuple().tm_yday
        
        # Calculate solar declination
        declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
        dec_rad = math.radians(declination)
        
        # Calculate hour angle
        hour = timestamp.hour + timestamp.minute / 60.0
        hour_angle = 15 * (hour - 12)  # degrees
        hour_angle_rad = math.radians(hour_angle)
        
        # Calculate altitude
        sin_altitude = (
            math.sin(lat_rad) * math.sin(dec_rad) +
            math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_angle_rad)
        )
        altitude = math.degrees(math.asin(sin_altitude))
        
        # Calculate azimuth
        cos_azimuth = (
            (math.sin(dec_rad) - math.sin(lat_rad) * sin_altitude) /
            (math.cos(lat_rad) * math.cos(math.radians(altitude)))
        )
        
        # Clamp to valid range
        cos_azimuth = max(-1, min(1, cos_azimuth))
        azimuth = math.degrees(math.acos(cos_azimuth))
        
        # Adjust azimuth for afternoon
        if hour > 12:
            azimuth = 360 - azimuth
        
        return altitude, azimuth
    
    @staticmethod
    def calculate_sun_path(
        location: LocationModel,
        date: datetime,
        time_resolution: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Calculate complete sun path for a day
        
        Args:
            location: Geographic location
            date: Date for calculation
            time_resolution: Minutes between calculations
            
        Returns:
            List of sun positions throughout the day
        """
        sun_path = []
        current_time = date.replace(hour=0, minute=0, second=0)
        end_time = date.replace(hour=23, minute=59, second=59)
        
        while current_time <= end_time:
            altitude, azimuth = SunPositionCalculator.calculate_sun_position(
                location.latitude,
                location.longitude,
                current_time
            )
            
            if altitude > 0:  # Sun is above horizon
                sun_path.append({
                    'timestamp': current_time.isoformat(),
                    'altitude': round(altitude, 2),
                    'azimuth': round(azimuth, 2),
                    'hour': current_time.hour,
                    'minute': current_time.minute
                })
            
            current_time += timedelta(minutes=time_resolution)
        
        return sun_path


# ============================================================================
# Obstacle Shadow Calculator
# ============================================================================

class ObstacleShadowCalculator:
    """Calculate shadows cast by obstacles"""
    
    @staticmethod
    def calculate_shadow_angle(
        obstacle_height: float,
        obstacle_distance: float,
        sun_altitude: float
    ) -> float:
        """
        Calculate the angle of shadow cast by obstacle
        
        Returns:
            Shadow angle in degrees
        """
        if sun_altitude <= 0:
            return 0.0
        
        # Calculate shadow length
        shadow_length = obstacle_height / math.tan(math.radians(sun_altitude))
        
        # Calculate angle from module to shadow tip
        shadow_angle = math.degrees(math.atan2(obstacle_height, obstacle_distance + shadow_length))
        
        return shadow_angle
    
    @staticmethod
    def is_module_shaded(
        obstacle: ObstacleModel,
        sun_altitude: float,
        sun_azimuth: float,
        module_azimuth: float
    ) -> Tuple[bool, float]:
        """
        Determine if module is shaded by obstacle
        
        Returns:
            Tuple of (is_shaded, shading_percentage)
        """
        # Calculate azimuth difference
        azimuth_diff = abs(sun_azimuth - obstacle.azimuth)
        if azimuth_diff > 180:
            azimuth_diff = 360 - azimuth_diff
        
        # Obstacle must be between sun and module
        if azimuth_diff > 90:
            return False, 0.0
        
        # Calculate shadow angle
        shadow_angle = ObstacleShadowCalculator.calculate_shadow_angle(
            obstacle.height,
            obstacle.distance,
            sun_altitude
        )
        
        # Calculate shading percentage based on shadow angle and obstacle width
        if shadow_angle > 0:
            # Simple model: shading percentage based on obstacle width and distance
            angular_width = math.degrees(math.atan2(obstacle.width, obstacle.distance))
            shading_factor = min(1.0, angular_width / 45.0)  # Normalize to 45 degrees
            
            return True, shading_factor * 100
        
        return False, 0.0
    
    @staticmethod
    def calculate_shadow_profile(
        obstacles: List[ObstacleModel],
        sun_path: List[Dict[str, Any]],
        module_azimuth: float
    ) -> List[Dict[str, Any]]:
        """
        Calculate complete shadow profile for all obstacles
        
        Returns:
            List of shading events with timestamps and percentages
        """
        shadow_profile = []
        
        for sun_pos in sun_path:
            sun_altitude = sun_pos['altitude']
            sun_azimuth = sun_pos['azimuth']
            
            max_shading = 0.0
            shading_obstacles = []
            
            for obstacle in obstacles:
                is_shaded, shading_pct = ObstacleShadowCalculator.is_module_shaded(
                    obstacle,
                    sun_altitude,
                    sun_azimuth,
                    module_azimuth
                )
                
                if is_shaded:
                    max_shading = max(max_shading, shading_pct)
                    shading_obstacles.append({
                        'obstacle_id': obstacle.id,
                        'obstacle_type': obstacle.type,
                        'shading_percent': round(shading_pct, 2)
                    })
            
            shadow_profile.append({
                'timestamp': sun_pos['timestamp'],
                'sun_altitude': sun_pos['altitude'],
                'sun_azimuth': sun_pos['azimuth'],
                'shading_percent': round(max_shading, 2),
                'shaded': max_shading > 0,
                'obstacles': shading_obstacles
            })
        
        return shadow_profile


# ============================================================================
# Shading Loss Calculator
# ============================================================================

class ShadingLossCalculator:
    """Calculate energy losses due to shading"""
    
    @staticmethod
    def calculate_hourly_irradiance(
        sun_altitude: float,
        shading_percent: float,
        clear_sky_irradiance: float = 1000.0  # W/m²
    ) -> float:
        """
        Calculate actual irradiance considering shading
        
        Args:
            sun_altitude: Sun altitude in degrees
            shading_percent: Percentage of module shaded
            clear_sky_irradiance: Maximum irradiance under clear sky
            
        Returns:
            Actual irradiance in W/m²
        """
        if sun_altitude <= 0:
            return 0.0
        
        # Calculate base irradiance based on sun altitude
        base_irradiance = clear_sky_irradiance * math.sin(math.radians(sun_altitude))
        
        # Apply shading loss
        actual_irradiance = base_irradiance * (1 - shading_percent / 100)
        
        return max(0.0, actual_irradiance)
    
    @staticmethod
    def calculate_daily_loss(
        shadow_profile: List[Dict[str, Any]],
        module_area: float
    ) -> Dict[str, float]:
        """
        Calculate energy loss for a day
        
        Returns:
            Dictionary with loss metrics
        """
        total_potential_energy = 0.0
        total_actual_energy = 0.0
        shaded_hours = 0
        
        for entry in shadow_profile:
            sun_altitude = entry['sun_altitude']
            shading_percent = entry['shading_percent']
            
            # Calculate potential and actual irradiance
            potential_irradiance = ShadingLossCalculator.calculate_hourly_irradiance(
                sun_altitude, 0.0
            )
            actual_irradiance = ShadingLossCalculator.calculate_hourly_irradiance(
                sun_altitude, shading_percent
            )
            
            # Convert to energy (assuming 1-hour intervals)
            time_interval = 1.0  # hours
            total_potential_energy += potential_irradiance * module_area * time_interval
            total_actual_energy += actual_irradiance * module_area * time_interval
            
            if shading_percent > 0:
                shaded_hours += time_interval
        
        energy_loss = total_potential_energy - total_actual_energy
        loss_percent = (energy_loss / total_potential_energy * 100) if total_potential_energy > 0 else 0.0
        
        return {
            'potential_energy_wh': round(total_potential_energy, 2),
            'actual_energy_wh': round(total_actual_energy, 2),
            'energy_loss_wh': round(energy_loss, 2),
            'loss_percent': round(loss_percent, 2),
            'shaded_hours': round(shaded_hours, 2)
        }
    
    @staticmethod
    def calculate_annual_loss(
        location: LocationModel,
        obstacles: List[ObstacleModel],
        module_azimuth: float,
        module_area: float,
        start_date: datetime,
        end_date: datetime
    ) -> ShadingLossResult:
        """
        Calculate annual shading losses
        
        Returns:
            Complete shading loss analysis
        """
        monthly_losses = {}
        hourly_profile = []
        critical_periods = []
        
        current_date = start_date
        total_loss_percent = 0.0
        days_analyzed = 0
        
        while current_date <= end_date:
            # Calculate sun path for this day
            sun_path = SunPositionCalculator.calculate_sun_path(
                location, current_date, time_resolution=60
            )
            
            # Calculate shadow profile
            shadow_profile = ObstacleShadowCalculator.calculate_shadow_profile(
                obstacles, sun_path, module_azimuth
            )
            
            # Calculate daily loss
            daily_loss = ShadingLossCalculator.calculate_daily_loss(
                shadow_profile, module_area
            )
            
            # Store monthly data
            month_key = current_date.strftime('%Y-%m')
            if month_key not in monthly_losses:
                monthly_losses[month_key] = []
            monthly_losses[month_key].append(daily_loss['loss_percent'])
            
            # Identify critical periods (high shading)
            if daily_loss['loss_percent'] > 20:
                critical_periods.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'loss_percent': daily_loss['loss_percent'],
                    'shaded_hours': daily_loss['shaded_hours']
                })
            
            total_loss_percent += daily_loss['loss_percent']
            days_analyzed += 1
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Calculate monthly averages
        monthly_avg_losses = {
            month: round(sum(losses) / len(losses), 2)
            for month, losses in monthly_losses.items()
        }
        
        # Calculate average annual loss
        avg_annual_loss = round(total_loss_percent / days_analyzed, 2) if days_analyzed > 0 else 0.0
        
        return ShadingLossResult(
            total_annual_loss_percent=avg_annual_loss,
            monthly_losses=monthly_avg_losses,
            hourly_shading_profile=hourly_profile[:24],  # Sample day
            critical_periods=critical_periods[:10],  # Top 10 worst days
            affected_area_percent=round(avg_annual_loss, 2)
        )


# ============================================================================
# Optimization Suggester
# ============================================================================

class ShadingOptimizationSuggester:
    """Generate optimization suggestions to reduce shading"""
    
    @staticmethod
    def analyze_tilt_adjustment(
        current_tilt: float,
        obstacles: List[ObstacleModel],
        location: LocationModel
    ) -> Optional[OptimizationSuggestion]:
        """Suggest tilt angle adjustment"""
        # Simple heuristic: if obstacles are low, increase tilt
        avg_obstacle_height = sum(o.height for o in obstacles) / len(obstacles) if obstacles else 0
        
        if avg_obstacle_height < 5 and current_tilt < 35:
            potential_improvement = 5.0  # Estimated 5% improvement
            return OptimizationSuggestion(
                type='tilt_adjustment',
                description=f'Increase module tilt angle from {current_tilt}° to {current_tilt + 10}° to reduce morning/evening shading',
                potential_improvement_percent=potential_improvement,
                implementation_difficulty='easy',
                estimated_cost=500.0
            )
        
        return None
    
    @staticmethod
    def analyze_azimuth_adjustment(
        current_azimuth: float,
        obstacles: List[ObstacleModel]
    ) -> Optional[OptimizationSuggestion]:
        """Suggest azimuth angle adjustment"""
        # Check if obstacles are concentrated in one direction
        obstacle_azimuths = [o.azimuth for o in obstacles]
        
        if len(obstacle_azimuths) > 0:
            avg_obstacle_azimuth = sum(obstacle_azimuths) / len(obstacle_azimuths)
            azimuth_diff = abs(current_azimuth - avg_obstacle_azimuth)
            
            if azimuth_diff < 45:
                # Obstacles are in front of modules
                suggested_azimuth = (current_azimuth + 180) % 360
                return OptimizationSuggestion(
                    type='azimuth_adjustment',
                    description=f'Rotate modules from {current_azimuth}° to {suggested_azimuth}° to avoid primary obstacle direction',
                    potential_improvement_percent=15.0,
                    implementation_difficulty='moderate',
                    estimated_cost=1500.0
                )
        
        return None
    
    @staticmethod
    def analyze_module_relocation(
        obstacles: List[ObstacleModel]
    ) -> Optional[OptimizationSuggestion]:
        """Suggest module relocation"""
        # Check if there are many close obstacles
        close_obstacles = [o for o in obstacles if o.distance < 10]
        
        if len(close_obstacles) > 2:
            return OptimizationSuggestion(
                type='module_relocation',
                description=f'Relocate modules away from {len(close_obstacles)} nearby obstacles to reduce shading impact',
                potential_improvement_percent=25.0,
                implementation_difficulty='difficult',
                estimated_cost=5000.0
            )
        
        return None
    
    @staticmethod
    def analyze_obstacle_removal(
        obstacles: List[ObstacleModel]
    ) -> List[OptimizationSuggestion]:
        """Suggest obstacle removal or trimming"""
        suggestions = []
        
        for obstacle in obstacles:
            if obstacle.type == 'tree' and obstacle.height > 10:
                suggestions.append(OptimizationSuggestion(
                    type='obstacle_removal',
                    description=f'Trim or remove {obstacle.type} ({obstacle.description or obstacle.id}) to reduce shading',
                    potential_improvement_percent=10.0,
                    implementation_difficulty='easy',
                    estimated_cost=300.0
                ))
        
        return suggestions
    
    @staticmethod
    def generate_all_suggestions(
        current_tilt: float,
        current_azimuth: float,
        obstacles: List[ObstacleModel],
        location: LocationModel
    ) -> List[OptimizationSuggestion]:
        """Generate all applicable optimization suggestions"""
        suggestions = []
        
        # Tilt adjustment
        tilt_suggestion = ShadingOptimizationSuggester.analyze_tilt_adjustment(
            current_tilt, obstacles, location
        )
        if tilt_suggestion:
            suggestions.append(tilt_suggestion)
        
        # Azimuth adjustment
        azimuth_suggestion = ShadingOptimizationSuggester.analyze_azimuth_adjustment(
            current_azimuth, obstacles
        )
        if azimuth_suggestion:
            suggestions.append(azimuth_suggestion)
        
        # Module relocation
        relocation_suggestion = ShadingOptimizationSuggester.analyze_module_relocation(
            obstacles
        )
        if relocation_suggestion:
            suggestions.append(relocation_suggestion)
        
        # Obstacle removal
        removal_suggestions = ShadingOptimizationSuggester.analyze_obstacle_removal(
            obstacles
        )
        suggestions.extend(removal_suggestions)
        
        # Sort by potential improvement
        suggestions.sort(key=lambda x: x.potential_improvement_percent, reverse=True)
        
        return suggestions


# ============================================================================
# Visualization Data Generator
# ============================================================================

class ShadingVisualizationGenerator:
    """Generate data for shading visualizations"""
    
    @staticmethod
    def generate_sun_path_data(
        location: LocationModel,
        date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate sun path visualization data"""
        return SunPositionCalculator.calculate_sun_path(location, date, time_resolution=30)
    
    @staticmethod
    def generate_shading_timeline(
        shadow_profile: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate timeline visualization data"""
        return [
            {
                'time': entry['timestamp'],
                'shading_percent': entry['shading_percent'],
                'shaded': entry['shaded']
            }
            for entry in shadow_profile
        ]
    
    @staticmethod
    def generate_obstacle_shadows(
        obstacles: List[ObstacleModel],
        sun_altitude: float,
        sun_azimuth: float
    ) -> List[Dict[str, Any]]:
        """Generate obstacle shadow visualization data"""
        shadows = []
        
        for obstacle in obstacles:
            shadow_length = obstacle.height / math.tan(math.radians(max(sun_altitude, 1)))
            
            shadows.append({
                'obstacle_id': obstacle.id,
                'obstacle_type': obstacle.type,
                'shadow_length': round(shadow_length, 2),
                'shadow_azimuth': sun_azimuth,
                'obstacle_height': obstacle.height,
                'obstacle_distance': obstacle.distance
            })
        
        return shadows
    
    @staticmethod
    def generate_heatmap_data(
        location: LocationModel,
        obstacles: List[ObstacleModel],
        module_azimuth: float,
        start_date: datetime,
        days: int = 365
    ) -> Dict[str, Any]:
        """Generate annual shading heatmap data"""
        heatmap = []
        
        for day in range(0, days, 7):  # Weekly sampling
            current_date = start_date + timedelta(days=day)
            sun_path = SunPositionCalculator.calculate_sun_path(location, current_date)
            shadow_profile = ObstacleShadowCalculator.calculate_shadow_profile(
                obstacles, sun_path, module_azimuth
            )
            
            # Calculate average shading for this day
            avg_shading = sum(e['shading_percent'] for e in shadow_profile) / len(shadow_profile) if shadow_profile else 0
            
            heatmap.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day_of_year': day,
                'avg_shading_percent': round(avg_shading, 2)
            })
        
        return {
            'data': heatmap,
            'min_shading': min(d['avg_shading_percent'] for d in heatmap) if heatmap else 0,
            'max_shading': max(d['avg_shading_percent'] for d in heatmap) if heatmap else 0
        }


# ============================================================================
# Main Shading Analysis Service
# ============================================================================

class ShadingAnalysisService:
    """Main service for comprehensive shading analysis"""
    
    def __init__(self):
        self.sun_calculator = SunPositionCalculator()
        self.shadow_calculator = ObstacleShadowCalculator()
        self.loss_calculator = ShadingLossCalculator()
        self.optimization_suggester = ShadingOptimizationSuggester()
        self.visualization_generator = ShadingVisualizationGenerator()
    
    def analyze_shading(
        self,
        request: ShadingAnalysisRequest
    ) -> ShadingAnalysisResponse:
        """
        Perform complete shading analysis
        
        Args:
            request: Shading analysis request with all parameters
            
        Returns:
            Complete shading analysis with losses, visualizations, and suggestions
        """
        # Calculate shading losses
        losses = self.loss_calculator.calculate_annual_loss(
            request.location,
            request.obstacles,
            request.module_azimuth,
            request.module_area,
            request.analysis_start_date,
            request.analysis_end_date
        )
        
        # Generate visualization data
        sample_date = request.analysis_start_date
        sun_path_data = self.visualization_generator.generate_sun_path_data(
            request.location, sample_date
        )
        
        shadow_profile = self.shadow_calculator.calculate_shadow_profile(
            request.obstacles, sun_path_data, request.module_azimuth
        )
        
        shading_timeline = self.visualization_generator.generate_shading_timeline(
            shadow_profile
        )
        
        # Get noon sun position for obstacle shadows
        noon_sun = [s for s in sun_path_data if s['hour'] == 12]
        if noon_sun:
            obstacle_shadows = self.visualization_generator.generate_obstacle_shadows(
                request.obstacles,
                noon_sun[0]['altitude'],
                noon_sun[0]['azimuth']
            )
        else:
            obstacle_shadows = []
        
        heatmap_data = self.visualization_generator.generate_heatmap_data(
            request.location,
            request.obstacles,
            request.module_azimuth,
            request.analysis_start_date
        )
        
        visualization = ShadingVisualization(
            sun_path_data=sun_path_data,
            shading_timeline=shading_timeline,
            obstacle_shadows=obstacle_shadows,
            heatmap_data=heatmap_data
        )
        
        # Generate optimization suggestions
        suggestions = self.optimization_suggester.generate_all_suggestions(
            request.module_tilt,
            request.module_azimuth,
            request.obstacles,
            request.location
        )
        
        # Compile metadata
        metadata = {
            'analysis_date': datetime.now().isoformat(),
            'location': {
                'latitude': request.location.latitude,
                'longitude': request.location.longitude
            },
            'obstacles_count': len(request.obstacles),
            'analysis_period_days': (request.analysis_end_date - request.analysis_start_date).days,
            'module_configuration': {
                'tilt': request.module_tilt,
                'azimuth': request.module_azimuth,
                'area': request.module_area
            }
        }
        
        return ShadingAnalysisResponse(
            losses=losses,
            visualization=visualization,
            suggestions=suggestions,
            analysis_metadata=metadata
        )
    
    def quick_shading_check(
        self,
        location: LocationModel,
        obstacles: List[ObstacleModel],
        module_azimuth: float
    ) -> Dict[str, Any]:
        """
        Perform quick shading check for current conditions
        
        Returns:
            Quick assessment of current shading status
        """
        current_time = datetime.now()
        
        # Calculate current sun position
        altitude, azimuth = self.sun_calculator.calculate_sun_position(
            location.latitude,
            location.longitude,
            current_time
        )
        
        # Check if currently shaded
        max_shading = 0.0
        shading_obstacles = []
        
        for obstacle in obstacles:
            is_shaded, shading_pct = self.shadow_calculator.is_module_shaded(
                obstacle,
                altitude,
                azimuth,
                module_azimuth
            )
            
            if is_shaded:
                max_shading = max(max_shading, shading_pct)
                shading_obstacles.append({
                    'obstacle_id': obstacle.id,
                    'obstacle_type': obstacle.type,
                    'shading_percent': round(shading_pct, 2)
                })
        
        return {
            'timestamp': current_time.isoformat(),
            'sun_altitude': round(altitude, 2),
            'sun_azimuth': round(azimuth, 2),
            'currently_shaded': max_shading > 0,
            'shading_percent': round(max_shading, 2),
            'shading_obstacles': shading_obstacles
        }
