"""
Demo script for 3D Animation System

Demonstrates all animation types and export formats.

Requirements: 1.3, 6.1
"""

from datetime import datetime
from services.animation_3d_service import (
    Animation3DService,
    AnimationType,
    AnimationFormat,
    AnimationConfig
)


def demo_rotation_360():
    """Demonstrate 360° rotation animation"""
    print("\n" + "="*60)
    print("DEMO: 360° Rotation Animation")
    print("="*60)
    
    service = Animation3DService()
    
    config = AnimationConfig(
        animation_type=AnimationType.ROTATION_360,
        duration=10.0,
        fps=30,
        resolution=(1920, 1080),
        quality='high',
        loop=True,
        smooth_transitions=True
    )
    
    print(f"\nGenerating {config.duration}s animation at {config.fps} FPS...")
    
    frames = service.generate_rotation_360(
        center_point=(0, 0, 0),
        radius=15.0,
        height=10.0,
        config=config
    )
    
    print(f" Generated {len(frames)} frames")
    
    # Show sample frames
    print("\nSample frames:")
    for i in [0, len(frames)//4, len(frames)//2, 3*len(frames)//4, len(frames)-1]:
        frame = frames[i]
        print(f"  Frame {frame.frame_number}: "
              f"Camera at {frame.camera_position}, "
              f"Looking at {frame.camera_target}")
    
    # Get metadata
    metadata = service.get_animation_metadata(frames)
    print(f"\nMetadata:")
    print(f"  Duration: {metadata['duration']:.2f}s")
    print(f"  FPS: {metadata['fps']:.1f}")
    print(f"  Frame count: {metadata['frame_count']}")
    
    return frames, config


def demo_fly_through():
    """Demonstrate fly-through animation"""
    print("\n" + "="*60)
    print("DEMO: Fly-Through Animation")
    print("="*60)
    
    service = Animation3DService()
    
    # Define a path around the installation
    waypoints = [
        (0, -20, 10),   # Start from south
        (0, -10, 8),    # Move closer
        (10, 0, 6),     # Move to east
        (0, 10, 8),     # Move to north
        (-10, 0, 6),    # Move to west
        (0, -20, 10)    # Return to start
    ]
    
    # Always look at the center
    look_at_points = [(0, 0, 2)] * len(waypoints)
    
    config = AnimationConfig(
        animation_type=AnimationType.FLY_THROUGH,
        duration=15.0,
        fps=30,
        resolution=(1920, 1080),
        quality='high',
        smooth_transitions=True
    )
    
    print(f"\nGenerating fly-through with {len(waypoints)} waypoints...")
    
    frames = service.generate_fly_through(
        waypoints=waypoints,
        look_at_points=look_at_points,
        config=config
    )
    
    print(f" Generated {len(frames)} frames")
    
    # Show waypoint progression
    print("\nWaypoint progression:")
    for i, waypoint in enumerate(waypoints):
        print(f"  Waypoint {i+1}: {waypoint}")
    
    return frames, config


def demo_assembly():
    """Demonstrate assembly animation"""
    print("\n" + "="*60)
    print("DEMO: Assembly Animation")
    print("="*60)
    
    service = Animation3DService()
    
    # Define installation components
    objects = [
        {'id': 'mounting', 'name': 'Mounting System'},
        {'id': 'module_row1', 'name': 'Module Row 1 (10 modules)'},
        {'id': 'module_row2', 'name': 'Module Row 2 (10 modules)'},
        {'id': 'module_row3', 'name': 'Module Row 3 (10 modules)'},
        {'id': 'inverter', 'name': 'Inverter'},
        {'id': 'battery', 'name': 'Battery Storage'},
        {'id': 'wiring', 'name': 'Electrical Wiring'},
        {'id': 'monitoring', 'name': 'Monitoring System'}
    ]
    
    config = AnimationConfig(
        animation_type=AnimationType.ASSEMBLY,
        duration=16.0,
        fps=30,
        resolution=(1920, 1080),
        quality='medium'
    )
    
    print(f"\nGenerating assembly animation with {len(objects)} components...")
    
    frames = service.generate_assembly_animation(
        objects=objects,
        config=config
    )
    
    print(f" Generated {len(frames)} frames")
    
    # Show assembly progression
    print("\nAssembly sequence:")
    for i, obj in enumerate(objects):
        print(f"  Step {i+1}: {obj['name']}")
    
    # Show visibility progression
    print("\nVisibility progression (sample frames):")
    for i in [0, len(frames)//4, len(frames)//2, 3*len(frames)//4, len(frames)-1]:
        frame = frames[i]
        visible_count = len(frame.visible_objects) if frame.visible_objects else 0
        print(f"  Frame {frame.frame_number}: {visible_count}/{len(objects)} objects visible")
    
    return frames, config


def demo_time_lapse():
    """Demonstrate time-lapse animation"""
    print("\n" + "="*60)
    print("DEMO: Time-Lapse Animation (Sun Movement)")
    print("="*60)
    
    service = Animation3DService()
    
    # Berlin coordinates
    location = (52.52, 13.405)
    # Summer solstice for maximum sun exposure
    date = datetime(2024, 6, 21)
    
    config = AnimationConfig(
        animation_type=AnimationType.TIME_LAPSE,
        duration=20.0,
        fps=30,
        resolution=(1920, 1080),
        quality='high'
    )
    
    print(f"\nGenerating time-lapse for:")
    print(f"  Location: {location[0]}°N, {location[1]}°E (Berlin)")
    print(f"  Date: {date.strftime('%Y-%m-%d')} (Summer Solstice)")
    
    frames = service.generate_time_lapse(
        location=location,
        date=date,
        config=config
    )
    
    print(f" Generated {len(frames)} frames")
    
    # Show sun position progression
    print("\nSun position progression:")
    for i in [0, len(frames)//4, len(frames)//2, 3*len(frames)//4, len(frames)-1]:
        frame = frames[i]
        elevation = frame.metadata['sun_elevation']
        time = frame.metadata['current_time']
        print(f"  {time}: Sun elevation {elevation:.1f}°")
    
    return frames, config


def demo_presentation():
    """Demonstrate presentation mode animation"""
    print("\n" + "="*60)
    print("DEMO: Presentation Mode Animation")
    print("="*60)
    
    service = Animation3DService()
    
    # Define presentation scenes
    scenes = [
        {
            'name': 'Introduction',
            'description': 'Overview of the complete solar installation',
            'camera_position': (25, 25, 20),
            'camera_target': (0, 0, 0)
        },
        {
            'name': 'Roof Modules',
            'description': 'Close-up view of solar modules on roof',
            'camera_position': (8, 8, 5),
            'camera_target': (0, 0, 2)
        },
        {
            'name': 'Ground Equipment',
            'description': 'Inverter and battery storage system',
            'camera_position': (5, -8, 3),
            'camera_target': (0, -10, 1)
        },
        {
            'name': 'Side Profile',
            'description': 'Profile view showing mounting system',
            'camera_position': (0, 20, 10),
            'camera_target': (0, 0, 2)
        },
        {
            'name': 'Final Overview',
            'description': 'Complete system from optimal angle',
            'camera_position': (20, -20, 15),
            'camera_target': (0, 0, 0)
        }
    ]
    
    config = AnimationConfig(
        animation_type=AnimationType.PRESENTATION,
        duration=25.0,
        fps=30,
        resolution=(1920, 1080),
        quality='high'
    )
    
    print(f"\nGenerating presentation with {len(scenes)} scenes...")
    
    frames = service.generate_presentation_mode(
        scenes=scenes,
        config=config
    )
    
    print(f" Generated {len(frames)} frames")
    
    # Show scene breakdown
    print("\nScene breakdown:")
    frames_per_scene = len(frames) // len(scenes)
    for i, scene in enumerate(scenes):
        start_frame = i * frames_per_scene
        end_frame = min((i + 1) * frames_per_scene, len(frames))
        duration = (end_frame - start_frame) / config.fps
        print(f"  Scene {i+1}: {scene['name']}")
        print(f"    Duration: {duration:.1f}s")
        print(f"    Description: {scene['description']}")
    
    return frames, config


def demo_export_formats():
    """Demonstrate different export formats"""
    print("\n" + "="*60)
    print("DEMO: Export Formats")
    print("="*60)
    
    service = Animation3DService()
    
    # Generate a simple animation
    config = AnimationConfig(
        animation_type=AnimationType.ROTATION_360,
        duration=5.0,
        fps=30,
        resolution=(1280, 720),
        quality='medium'
    )
    
    frames = service.generate_rotation_360(
        center_point=(0, 0, 0),
        radius=10.0,
        height=8.0,
        config=config
    )
    
    print(f"\nGenerated {len(frames)} frames for export demo")
    
    # Demonstrate each export format
    formats = [
        (AnimationFormat.GIF, 'animation.gif'),
        (AnimationFormat.MP4, 'animation.mp4'),
        (AnimationFormat.WEBM, 'animation.webm'),
        (AnimationFormat.FRAMES, 'frames/')
    ]
    
    print("\nExport formats:")
    for format_type, filename in formats:
        result = service.export_animation(
            frames=frames,
            output_format=format_type,
            output_path=filename,
            config=config
        )
        
        print(f"\n  {format_type.value.upper()}:")
        print(f"    Filename: {filename}")
        print(f"    Success: {result['success']}")
        print(f"    Frame count: {result['frame_count']}")
        print(f"    Duration: {result['duration']}s")
        print(f"    Resolution: {result['resolution']}")
        
        if format_type == AnimationFormat.MP4:
            print(f"    Codec: {result.get('codec', 'N/A')}")
            print(f"    Bitrate: {result.get('bitrate', 'N/A')}")


def demo_quality_comparison():
    """Demonstrate quality settings"""
    print("\n" + "="*60)
    print("DEMO: Quality Settings Comparison")
    print("="*60)
    
    service = Animation3DService()
    
    qualities = ['low', 'medium', 'high', 'ultra']
    
    print("\nQuality settings:")
    for quality in qualities:
        settings = service.quality_settings[quality]
        print(f"\n  {quality.upper()}:")
        print(f"    Bitrate: {settings['bitrate']}")
        print(f"    Preset: {settings['preset']}")
        
        # Estimate file size (rough approximation)
        bitrate_mbps = float(settings['bitrate'].rstrip('M'))
        duration = 10.0  # seconds
        estimated_size_mb = (bitrate_mbps * duration) / 8
        print(f"    Estimated size (10s): ~{estimated_size_mb:.1f} MB")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("3D ANIMATION SYSTEM - COMPREHENSIVE DEMO")
    print("="*60)
    print("\nThis demo showcases all animation types and features.")
    
    try:
        # Run each demo
        demo_rotation_360()
        demo_fly_through()
        demo_assembly()
        demo_time_lapse()
        demo_presentation()
        demo_export_formats()
        demo_quality_comparison()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nAll animation types demonstrated successfully!")
        print("\nFor more information, see:")
        print("  - docs/3D_ANIMATION_GUIDE.md")
        print("  - docs/3D_ANIMATION_QUICK_REFERENCE.md")
        
    except Exception as e:
        print(f"\n Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
