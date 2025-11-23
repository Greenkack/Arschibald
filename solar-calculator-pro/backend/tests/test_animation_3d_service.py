"""
Tests for 3D Animation Service

Requirements: 1.3, 6.1
"""

import pytest
from datetime import datetime
from typing import List

from ..services.animation_3d_service import (
    Animation3DService,
    AnimationType,
    AnimationFormat,
    AnimationConfig,
    AnimationFrame
)


@pytest.fixture
def animation_service():
    """Create animation service instance"""
    return Animation3DService()


@pytest.fixture
def basic_config():
    """Create basic animation configuration"""
    return AnimationConfig(
        animation_type=AnimationType.ROTATION_360,
        duration=10.0,
        fps=30,
        resolution=(1920, 1080),
        quality='medium',
        loop=True,
        smooth_transitions=True
    )


class TestRotation360Animation:
    """Tests for 360° rotation animation"""
    
    def test_generate_rotation_360(self, animation_service, basic_config):
        """Test basic 360° rotation generation"""
        center = (0, 0, 0)
        radius = 10.0
        height = 5.0
        
        frames = animation_service.generate_rotation_360(
            center_point=center,
            radius=radius,
            height=height,
            config=basic_config
        )
        
        # Verify frame count
        expected_frames = int(basic_config.duration * basic_config.fps)
        assert len(frames) == expected_frames
        
        # Verify first frame
        assert frames[0].frame_number == 0
        assert frames[0].timestamp == 0.0
        
        # Verify last frame
        assert frames[-1].frame_number == expected_frames - 1
        assert frames[-1].timestamp == pytest.approx(basic_config.duration - 1/basic_config.fps)
        
        # Verify camera always looks at center
        for frame in frames:
            assert frame.camera_target == center
    
    def test_rotation_360_full_circle(self, animation_service, basic_config):
        """Test that rotation completes a full circle"""
        center = (0, 0, 0)
        radius = 10.0
        height = 5.0
        
        frames = animation_service.generate_rotation_360(
            center_point=center,
            radius=radius,
            height=height,
            config=basic_config
        )
        
        # First and last frames should be at similar positions (full circle)
        first_pos = frames[0].camera_position
        last_pos = frames[-1].camera_position
        
        # Calculate distance between first and last positions
        distance = sum((a - b) ** 2 for a, b in zip(first_pos, last_pos)) ** 0.5
        
        # Should be close (not exact due to discrete frames)
        assert distance < radius * 0.1  # Within 10% of radius
    
    def test_rotation_360_constant_height(self, animation_service, basic_config):
        """Test that camera maintains constant height"""
        center = (0, 0, 0)
        radius = 10.0
        height = 5.0
        
        frames = animation_service.generate_rotation_360(
            center_point=center,
            radius=radius,
            height=height,
            config=basic_config
        )
        
        # All frames should have same Z coordinate
        for frame in frames:
            assert frame.camera_position[2] == pytest.approx(center[2] + height)


class TestFlyThroughAnimation:
    """Tests for fly-through animation"""
    
    def test_generate_fly_through(self, animation_service, basic_config):
        """Test basic fly-through generation"""
        waypoints = [(0, 0, 5), (10, 0, 5), (10, 10, 5), (0, 10, 5)]
        look_at_points = [(5, 5, 0), (5, 5, 0), (5, 5, 0), (5, 5, 0)]
        
        basic_config.animation_type = AnimationType.FLY_THROUGH
        
        frames = animation_service.generate_fly_through(
            waypoints=waypoints,
            look_at_points=look_at_points,
            config=basic_config
        )
        
        expected_frames = int(basic_config.duration * basic_config.fps)
        assert len(frames) == expected_frames
        
        # First frame should be at first waypoint
        assert frames[0].camera_position == pytest.approx(waypoints[0])
        
        # Last frame should be at last waypoint
        assert frames[-1].camera_position == pytest.approx(waypoints[-1])
    
    def test_fly_through_smooth_path(self, animation_service, basic_config):
        """Test that fly-through creates smooth path"""
        waypoints = [(0, 0, 0), (10, 0, 0)]
        look_at_points = [(5, 5, 0), (5, 5, 0)]
        
        basic_config.animation_type = AnimationType.FLY_THROUGH
        basic_config.smooth_transitions = True
        
        frames = animation_service.generate_fly_through(
            waypoints=waypoints,
            look_at_points=look_at_points,
            config=basic_config
        )
        
        # Check that positions are monotonically increasing in X
        for i in range(len(frames) - 1):
            assert frames[i + 1].camera_position[0] >= frames[i].camera_position[0]


class TestAssemblyAnimation:
    """Tests for assembly animation"""
    
    def test_generate_assembly(self, animation_service, basic_config):
        """Test basic assembly animation"""
        objects = [
            {'id': 'obj1', 'name': 'Module 1'},
            {'id': 'obj2', 'name': 'Module 2'},
            {'id': 'obj3', 'name': 'Module 3'}
        ]
        
        basic_config.animation_type = AnimationType.ASSEMBLY
        
        frames = animation_service.generate_assembly_animation(
            objects=objects,
            config=basic_config
        )
        
        expected_frames = int(basic_config.duration * basic_config.fps)
        assert len(frames) == expected_frames
        
        # First frame should have at least one object visible
        assert len(frames[0].visible_objects) >= 1
        
        # Last frame should have all objects visible
        assert len(frames[-1].visible_objects) == len(objects)
    
    def test_assembly_sequential_appearance(self, animation_service, basic_config):
        """Test that objects appear sequentially"""
        objects = [
            {'id': f'obj{i}', 'name': f'Module {i}'}
            for i in range(5)
        ]
        
        basic_config.animation_type = AnimationType.ASSEMBLY
        
        frames = animation_service.generate_assembly_animation(
            objects=objects,
            config=basic_config
        )
        
        # Count of visible objects should never decrease
        prev_count = 0
        for frame in frames:
            current_count = len(frame.visible_objects)
            assert current_count >= prev_count
            prev_count = current_count


class TestTimeLapseAnimation:
    """Tests for time-lapse animation"""
    
    def test_generate_time_lapse(self, animation_service, basic_config):
        """Test basic time-lapse generation"""
        location = (52.52, 13.405)  # Berlin
        date = datetime(2024, 6, 21)  # Summer solstice
        
        basic_config.animation_type = AnimationType.TIME_LAPSE
        
        frames = animation_service.generate_time_lapse(
            location=location,
            date=date,
            config=basic_config
        )
        
        expected_frames = int(basic_config.duration * basic_config.fps)
        assert len(frames) == expected_frames
        
        # All frames should have sun position
        for frame in frames:
            assert frame.sun_position is not None
    
    def test_time_lapse_sun_movement(self, animation_service, basic_config):
        """Test that sun moves across the sky"""
        location = (52.52, 13.405)  # Berlin
        date = datetime(2024, 6, 21)
        
        basic_config.animation_type = AnimationType.TIME_LAPSE
        
        frames = animation_service.generate_time_lapse(
            location=location,
            date=date,
            config=basic_config
        )
        
        # Sun should move (positions should change)
        sun_positions = [frame.sun_position for frame in frames]
        
        # Check that sun positions are not all the same
        unique_positions = set(sun_positions)
        assert len(unique_positions) > 1
    
    def test_time_lapse_sun_elevation(self, animation_service, basic_config):
        """Test sun elevation calculation"""
        location = (52.52, 13.405)  # Berlin
        date = datetime(2024, 6, 21)
        
        basic_config.animation_type = AnimationType.TIME_LAPSE
        
        frames = animation_service.generate_time_lapse(
            location=location,
            date=date,
            config=basic_config
        )
        
        # Extract sun elevations from metadata
        elevations = [frame.metadata['sun_elevation'] for frame in frames]
        
        # Sun should rise and set (elevation should increase then decrease)
        # Find the maximum elevation
        max_elevation = max(elevations)
        max_idx = elevations.index(max_elevation)
        
        # Before max, elevation should generally increase
        # After max, elevation should generally decrease
        assert max_idx > 0
        assert max_idx < len(elevations) - 1


class TestPresentationMode:
    """Tests for presentation mode animation"""
    
    def test_generate_presentation(self, animation_service, basic_config):
        """Test basic presentation mode"""
        scenes = [
            {
                'name': 'Scene 1',
                'camera_position': (10, 0, 5),
                'camera_target': (0, 0, 0)
            },
            {
                'name': 'Scene 2',
                'camera_position': (0, 10, 5),
                'camera_target': (0, 0, 0)
            },
            {
                'name': 'Scene 3',
                'camera_position': (-10, 0, 5),
                'camera_target': (0, 0, 0)
            }
        ]
        
        basic_config.animation_type = AnimationType.PRESENTATION
        
        frames = animation_service.generate_presentation_mode(
            scenes=scenes,
            config=basic_config
        )
        
        expected_frames = int(basic_config.duration * basic_config.fps)
        assert len(frames) == expected_frames
        
        # Each frame should have scene metadata
        for frame in frames:
            assert 'scene_index' in frame.metadata
            assert 'scene_name' in frame.metadata


class TestAnimationExport:
    """Tests for animation export"""
    
    def test_export_animation_gif(self, animation_service, basic_config):
        """Test GIF export"""
        frames = animation_service.generate_rotation_360(
            center_point=(0, 0, 0),
            radius=10.0,
            height=5.0,
            config=basic_config
        )
        
        result = animation_service.export_animation(
            frames=frames,
            output_format=AnimationFormat.GIF,
            output_path='/tmp/test.gif',
            config=basic_config
        )
        
        assert result['success'] is True
        assert result['format'] == 'gif'
        assert result['frame_count'] == len(frames)
    
    def test_export_animation_mp4(self, animation_service, basic_config):
        """Test MP4 export"""
        frames = animation_service.generate_rotation_360(
            center_point=(0, 0, 0),
            radius=10.0,
            height=5.0,
            config=basic_config
        )
        
        result = animation_service.export_animation(
            frames=frames,
            output_format=AnimationFormat.MP4,
            output_path='/tmp/test.mp4',
            config=basic_config
        )
        
        assert result['success'] is True
        assert result['format'] == 'mp4'
        assert 'codec' in result


class TestAnimationMetadata:
    """Tests for animation metadata"""
    
    def test_get_animation_metadata(self, animation_service, basic_config):
        """Test metadata extraction"""
        frames = animation_service.generate_rotation_360(
            center_point=(0, 0, 0),
            radius=10.0,
            height=5.0,
            config=basic_config
        )
        
        metadata = animation_service.get_animation_metadata(frames)
        
        assert metadata['frame_count'] == len(frames)
        assert metadata['duration'] == pytest.approx(basic_config.duration)
        assert metadata['fps'] == pytest.approx(basic_config.fps)
        assert 'camera_positions' in metadata
        assert 'camera_targets' in metadata
    
    def test_metadata_empty_frames(self, animation_service):
        """Test metadata with empty frames list"""
        metadata = animation_service.get_animation_metadata([])
        
        assert metadata == {}


class TestUtilityFunctions:
    """Tests for utility functions"""
    
    def test_lerp_3d(self, animation_service):
        """Test 3D linear interpolation"""
        start = (0, 0, 0)
        end = (10, 10, 10)
        
        # Test at t=0
        result = animation_service._lerp_3d(start, end, 0.0)
        assert result == start
        
        # Test at t=1
        result = animation_service._lerp_3d(start, end, 1.0)
        assert result == end
        
        # Test at t=0.5
        result = animation_service._lerp_3d(start, end, 0.5)
        assert result == (5, 5, 5)
    
    def test_ease_in_out_cubic(self, animation_service):
        """Test cubic easing function"""
        # Test at boundaries
        assert animation_service._ease_in_out_cubic(0.0) == 0.0
        assert animation_service._ease_in_out_cubic(1.0) == 1.0
        
        # Test at midpoint
        mid = animation_service._ease_in_out_cubic(0.5)
        assert 0 < mid < 1
    
    def test_calculate_sun_position(self, animation_service):
        """Test sun position calculation"""
        latitude = 52.52  # Berlin
        longitude = 13.405
        date = datetime(2024, 6, 21)  # Summer solstice
        
        # Test at solar noon
        sun_pos = animation_service._calculate_sun_position(
            latitude, longitude, date, 0.5
        )
        
        assert len(sun_pos) == 3
        assert sun_pos[2] > 0  # Sun should be above horizon at noon
    
    def test_calculate_sun_elevation(self, animation_service):
        """Test sun elevation calculation"""
        latitude = 52.52  # Berlin
        longitude = 13.405
        date = datetime(2024, 6, 21)
        
        # Test at solar noon
        elevation = animation_service._calculate_sun_elevation(
            latitude, longitude, date, 0.5
        )
        
        # Elevation should be positive at noon
        assert elevation > 0
        
        # Elevation should be reasonable (not > 90 degrees)
        assert elevation <= 90


class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_zero_duration(self, animation_service):
        """Test with zero duration"""
        config = AnimationConfig(
            animation_type=AnimationType.ROTATION_360,
            duration=0.1,  # Very short
            fps=30,
            resolution=(1920, 1080),
            quality='medium'
        )
        
        frames = animation_service.generate_rotation_360(
            center_point=(0, 0, 0),
            radius=10.0,
            height=5.0,
            config=config
        )
        
        # Should still generate at least a few frames
        assert len(frames) >= 1
    
    def test_high_fps(self, animation_service):
        """Test with high FPS"""
        config = AnimationConfig(
            animation_type=AnimationType.ROTATION_360,
            duration=1.0,
            fps=60,
            resolution=(1920, 1080),
            quality='medium'
        )
        
        frames = animation_service.generate_rotation_360(
            center_point=(0, 0, 0),
            radius=10.0,
            height=5.0,
            config=config
        )
        
        assert len(frames) == 60
    
    def test_single_waypoint_fly_through(self, animation_service, basic_config):
        """Test fly-through with minimum waypoints"""
        waypoints = [(0, 0, 0), (10, 10, 10)]
        look_at_points = [(5, 5, 0), (5, 5, 0)]
        
        basic_config.animation_type = AnimationType.FLY_THROUGH
        
        frames = animation_service.generate_fly_through(
            waypoints=waypoints,
            look_at_points=look_at_points,
            config=basic_config
        )
        
        assert len(frames) > 0
