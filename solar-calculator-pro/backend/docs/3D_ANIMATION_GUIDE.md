# 3D Animation System - Complete Guide

## Overview

The 3D Animation System provides comprehensive animation capabilities for solar installations, including:

- **360° Rotation**: Showcase installations from all angles
- **Fly-Through**: Smooth camera movements through waypoints
- **Assembly**: Step-by-step installation visualization
- **Time-Lapse**: Sun movement throughout the day
- **Presentation Mode**: Multi-scene professional presentations
- **Export**: GIF, MP4, WebM, and frame sequences

## Table of Contents

1. [Quick Start](#quick-start)
2. [Animation Types](#animation-types)
3. [Configuration](#configuration)
4. [API Reference](#api-reference)
5. [Export Formats](#export-formats)
6. [Best Practices](#best-practices)
7. [Examples](#examples)

## Quick Start

### Basic 360° Rotation

```python
from services.animation_3d_service import (
    Animation3DService,
    AnimationType,
    AnimationConfig
)

# Create service
service = Animation3DService()

# Configure animation
config = AnimationConfig(
    animation_type=AnimationType.ROTATION_360,
    duration=10.0,  # 10 seconds
    fps=30,
    resolution=(1920, 1080),
    quality='high',
    loop=True
)

# Generate frames
frames = service.generate_rotation_360(
    center_point=(0, 0, 0),
    radius=15.0,
    height=10.0,
    config=config
)

# Export as MP4
result = service.export_animation(
    frames=frames,
    output_format=AnimationFormat.MP4,
    output_path='rotation.mp4',
    config=config
)
```

### Using the API

```bash
# Create 360° rotation animation
curl -X POST http://localhost:8000/api/v1/animation-3d/rotation-360 \
  -H "Content-Type: application/json" \
  -d '{
    "center_point": [0, 0, 0],
    "radius": 15.0,
    "height": 10.0,
    "config": {
      "animation_type": "rotation_360",
      "duration": 10.0,
      "fps": 30,
      "resolution": [1920, 1080],
      "quality": "high",
      "loop": true
    }
  }'
```

## Animation Types

### 1. 360° Rotation

Perfect for showcasing solar installations from all angles.

**Features:**
- Smooth circular camera movement
- Constant height and radius
- Always looks at center point
- Configurable rotation speed

**Use Cases:**
- Product showcases
- Installation overviews
- Marketing materials

**Example:**
```python
frames = service.generate_rotation_360(
    center_point=(0, 0, 0),  # Center of rotation
    radius=15.0,              # Distance from center
    height=10.0,              # Camera height
    config=config
)
```

### 2. Fly-Through

Smooth camera movement through multiple waypoints.

**Features:**
- Multiple waypoints
- Smooth interpolation
- Cubic easing for natural movement
- Independent look-at points

**Use Cases:**
- Site tours
- Detailed inspections
- Architectural presentations

**Example:**
```python
waypoints = [
    (0, 0, 5),    # Start position
    (10, 0, 5),   # Move right
    (10, 10, 5),  # Move forward
    (0, 10, 5)    # Move left
]

look_at_points = [
    (5, 5, 0),    # Always look at center
    (5, 5, 0),
    (5, 5, 0),
    (5, 5, 0)
]

frames = service.generate_fly_through(
    waypoints=waypoints,
    look_at_points=look_at_points,
    config=config
)
```

### 3. Assembly Animation

Shows objects appearing sequentially.

**Features:**
- Sequential object appearance
- Configurable timing
- Fixed camera position
- Progress tracking

**Use Cases:**
- Installation process
- Component breakdown
- Educational content

**Example:**
```python
objects = [
    {'id': 'module1', 'name': 'Solar Module 1'},
    {'id': 'module2', 'name': 'Solar Module 2'},
    {'id': 'inverter', 'name': 'Inverter'},
    {'id': 'battery', 'name': 'Battery Storage'}
]

frames = service.generate_assembly_animation(
    objects=objects,
    config=config
)
```

### 4. Time-Lapse (Sun Movement)

Demonstrates sun movement throughout the day.

**Features:**
- Accurate solar position calculation
- Latitude/longitude support
- Date-specific calculations
- Sun elevation tracking

**Use Cases:**
- Shading analysis
- Energy production visualization
- Seasonal comparisons

**Example:**
```python
from datetime import datetime

frames = service.generate_time_lapse(
    location=(52.52, 13.405),  # Berlin (lat, lon)
    date=datetime(2024, 6, 21),  # Summer solstice
    config=config
)
```

### 5. Presentation Mode

Multi-scene professional presentations.

**Features:**
- Multiple scenes
- Scene transitions
- Custom camera angles
- Annotations support

**Use Cases:**
- Client presentations
- Sales pitches
- Technical reviews

**Example:**
```python
scenes = [
    {
        'name': 'Overview',
        'description': 'Full installation view',
        'camera_position': (20, 20, 15),
        'camera_target': (0, 0, 0)
    },
    {
        'name': 'Detail View',
        'description': 'Close-up of modules',
        'camera_position': (5, 5, 3),
        'camera_target': (0, 0, 1)
    },
    {
        'name': 'Side View',
        'description': 'Profile view',
        'camera_position': (0, 20, 10),
        'camera_target': (0, 0, 0)
    }
]

frames = service.generate_presentation_mode(
    scenes=scenes,
    config=config
)
```

## Configuration

### AnimationConfig

```python
class AnimationConfig:
    animation_type: AnimationType  # Type of animation
    duration: float                # Duration in seconds (max 300)
    fps: int                       # Frames per second (15-60)
    resolution: Tuple[int, int]    # Width x Height
    quality: str                   # 'low', 'medium', 'high', 'ultra'
    loop: bool                     # Loop animation
    smooth_transitions: bool       # Use smooth easing
```

### Quality Settings

| Quality | Bitrate | Preset | Use Case |
|---------|---------|--------|----------|
| Low | 1M | fast | Quick previews |
| Medium | 2M | medium | Standard output |
| High | 5M | slow | Professional use |
| Ultra | 10M | veryslow | Maximum quality |

### Resolution Presets

| Preset | Resolution | Aspect Ratio |
|--------|------------|--------------|
| HD | 1280 x 720 | 16:9 |
| Full HD | 1920 x 1080 | 16:9 |
| 2K | 2560 x 1440 | 16:9 |
| 4K | 3840 x 2160 | 16:9 |

### FPS Recommendations

| FPS | Use Case |
|-----|----------|
| 15 | Low bandwidth, small file size |
| 24 | Cinematic look |
| 30 | Standard video |
| 60 | Smooth motion, high quality |

## API Reference

### POST /api/v1/animation-3d/rotation-360

Create a 360° rotation animation.

**Request Body:**
```json
{
  "center_point": [0, 0, 0],
  "radius": 15.0,
  "height": 10.0,
  "config": {
    "animation_type": "rotation_360",
    "duration": 10.0,
    "fps": 30,
    "resolution": [1920, 1080],
    "quality": "high",
    "loop": true,
    "smooth_transitions": true
  }
}
```

**Response:**
```json
{
  "animation_id": "rot360_20240101_120000",
  "animation_type": "rotation_360",
  "frame_count": 300,
  "duration": 10.0,
  "fps": 30,
  "resolution": [1920, 1080],
  "metadata": {
    "frame_count": 300,
    "duration": 10.0,
    "fps": 30.0,
    "has_sun_data": false,
    "has_visibility_data": false
  }
}
```

### POST /api/v1/animation-3d/fly-through

Create a fly-through animation.

**Request Body:**
```json
{
  "waypoints": [
    [0, 0, 5],
    [10, 0, 5],
    [10, 10, 5]
  ],
  "look_at_points": [
    [5, 5, 0],
    [5, 5, 0],
    [5, 5, 0]
  ],
  "config": {
    "animation_type": "fly_through",
    "duration": 15.0,
    "fps": 30,
    "resolution": [1920, 1080],
    "quality": "high"
  }
}
```

### POST /api/v1/animation-3d/assembly

Create an assembly animation.

**Request Body:**
```json
{
  "objects": [
    {"id": "module1", "name": "Solar Module 1"},
    {"id": "module2", "name": "Solar Module 2"},
    {"id": "inverter", "name": "Inverter"}
  ],
  "config": {
    "animation_type": "assembly",
    "duration": 12.0,
    "fps": 30,
    "resolution": [1920, 1080],
    "quality": "medium"
  }
}
```

### POST /api/v1/animation-3d/time-lapse

Create a time-lapse animation.

**Request Body:**
```json
{
  "location": [52.52, 13.405],
  "date": "2024-06-21T00:00:00",
  "config": {
    "animation_type": "time_lapse",
    "duration": 20.0,
    "fps": 30,
    "resolution": [1920, 1080],
    "quality": "high"
  }
}
```

### POST /api/v1/animation-3d/presentation

Create a presentation mode animation.

**Request Body:**
```json
{
  "scenes": [
    {
      "name": "Overview",
      "description": "Full installation view",
      "camera_position": [20, 20, 15],
      "camera_target": [0, 0, 0],
      "camera_up": [0, 0, 1]
    },
    {
      "name": "Detail",
      "description": "Close-up view",
      "camera_position": [5, 5, 3],
      "camera_target": [0, 0, 1]
    }
  ],
  "config": {
    "animation_type": "presentation",
    "duration": 20.0,
    "fps": 30,
    "resolution": [1920, 1080],
    "quality": "high"
  }
}
```

### POST /api/v1/animation-3d/export

Export animation to file.

**Request Body:**
```json
{
  "animation_id": "rot360_20240101_120000",
  "output_format": "mp4",
  "output_filename": "my_animation.mp4"
}
```

**Response:**
```json
{
  "success": true,
  "animation_id": "rot360_20240101_120000",
  "output_path": "/exports/my_animation.mp4",
  "format": "mp4",
  "download_url": "/api/v1/animation-3d/download/rot360_20240101_120000"
}
```

## Export Formats

### GIF

**Pros:**
- Universal support
- Small file size
- Loops automatically

**Cons:**
- Limited colors (256)
- Lower quality
- No audio support

**Best For:**
- Web previews
- Email attachments
- Social media

### MP4 (H.264)

**Pros:**
- High quality
- Wide compatibility
- Good compression

**Cons:**
- Larger file size
- Requires codec

**Best For:**
- Professional presentations
- Video platforms
- Client deliverables

### WebM (VP9)

**Pros:**
- Excellent compression
- Open format
- Web-optimized

**Cons:**
- Limited compatibility
- Slower encoding

**Best For:**
- Web applications
- Modern browsers
- Streaming

### Frame Sequence (PNG)

**Pros:**
- Maximum quality
- Frame-by-frame control
- No compression artifacts

**Cons:**
- Very large file size
- Requires post-processing

**Best For:**
- Video editing
- Custom processing
- Quality control

## Best Practices

### Performance

1. **Choose Appropriate FPS**
   - Use 30 FPS for most cases
   - Use 60 FPS only for smooth motion requirements
   - Use 24 FPS for cinematic look

2. **Optimize Duration**
   - Keep animations under 30 seconds
   - Use presentation mode for longer content
   - Split long animations into scenes

3. **Resolution Selection**
   - Use 1080p for standard output
   - Use 4K only when necessary
   - Consider target platform

### Quality

1. **Camera Movement**
   - Use smooth transitions
   - Avoid jerky movements
   - Maintain consistent speed

2. **Composition**
   - Follow rule of thirds
   - Keep subject in frame
   - Use appropriate camera angles

3. **Lighting**
   - Use time-lapse for sun studies
   - Consider shadows
   - Maintain consistent lighting

### File Size

1. **Compression**
   - Use appropriate quality setting
   - Balance quality vs. file size
   - Consider delivery method

2. **Format Selection**
   - GIF for small, looping animations
   - MP4 for general use
   - WebM for web delivery

## Examples

### Example 1: Product Showcase

```python
# 360° rotation with high quality
config = AnimationConfig(
    animation_type=AnimationType.ROTATION_360,
    duration=15.0,
    fps=30,
    resolution=(1920, 1080),
    quality='high',
    loop=True,
    smooth_transitions=True
)

frames = service.generate_rotation_360(
    center_point=(0, 0, 2),
    radius=12.0,
    height=8.0,
    config=config
)

service.export_animation(
    frames=frames,
    output_format=AnimationFormat.MP4,
    output_path='product_showcase.mp4',
    config=config
)
```

### Example 2: Site Tour

```python
# Fly-through of installation site
waypoints = [
    (0, -20, 10),   # Start from distance
    (0, -10, 8),    # Move closer
    (5, 0, 5),      # Move to side
    (0, 10, 8),     # Move to other side
    (0, 20, 10)     # End at distance
]

look_at_points = [(0, 0, 2)] * len(waypoints)

config = AnimationConfig(
    animation_type=AnimationType.FLY_THROUGH,
    duration=20.0,
    fps=30,
    resolution=(1920, 1080),
    quality='high',
    smooth_transitions=True
)

frames = service.generate_fly_through(
    waypoints=waypoints,
    look_at_points=look_at_points,
    config=config
)
```

### Example 3: Installation Process

```python
# Assembly animation showing installation steps
objects = [
    {'id': 'mounting', 'name': 'Mounting System'},
    {'id': 'module1', 'name': 'Module Row 1'},
    {'id': 'module2', 'name': 'Module Row 2'},
    {'id': 'module3', 'name': 'Module Row 3'},
    {'id': 'inverter', 'name': 'Inverter'},
    {'id': 'battery', 'name': 'Battery Storage'},
    {'id': 'cables', 'name': 'Wiring'}
]

config = AnimationConfig(
    animation_type=AnimationType.ASSEMBLY,
    duration=14.0,
    fps=30,
    resolution=(1920, 1080),
    quality='medium'
)

frames = service.generate_assembly_animation(
    objects=objects,
    config=config
)
```

### Example 4: Sun Study

```python
# Time-lapse showing sun movement
from datetime import datetime

config = AnimationConfig(
    animation_type=AnimationType.TIME_LAPSE,
    duration=30.0,
    fps=30,
    resolution=(1920, 1080),
    quality='high'
)

frames = service.generate_time_lapse(
    location=(52.52, 13.405),  # Berlin
    date=datetime(2024, 6, 21),  # Summer solstice
    config=config
)
```

### Example 5: Client Presentation

```python
# Multi-scene presentation
scenes = [
    {
        'name': 'Introduction',
        'description': 'Overview of installation',
        'camera_position': (25, 25, 20),
        'camera_target': (0, 0, 0)
    },
    {
        'name': 'Roof Detail',
        'description': 'Close-up of roof modules',
        'camera_position': (8, 8, 5),
        'camera_target': (0, 0, 2)
    },
    {
        'name': 'Ground Equipment',
        'description': 'Inverter and battery',
        'camera_position': (5, -5, 3),
        'camera_target': (0, -10, 1)
    },
    {
        'name': 'Final View',
        'description': 'Complete system',
        'camera_position': (20, -20, 15),
        'camera_target': (0, 0, 0)
    }
]

config = AnimationConfig(
    animation_type=AnimationType.PRESENTATION,
    duration=40.0,
    fps=30,
    resolution=(1920, 1080),
    quality='high'
)

frames = service.generate_presentation_mode(
    scenes=scenes,
    config=config
)
```

## Troubleshooting

### Common Issues

**Issue: Animation is choppy**
- Solution: Increase FPS or enable smooth_transitions

**Issue: File size too large**
- Solution: Reduce resolution, duration, or quality setting

**Issue: Export fails**
- Solution: Check disk space and file permissions

**Issue: Sun position incorrect**
- Solution: Verify latitude/longitude and date

### Performance Tips

1. Generate preview at lower quality first
2. Use appropriate resolution for target platform
3. Enable caching for repeated operations
4. Consider background processing for large exports

## Requirements

- Python 3.10+
- NumPy
- PIL/Pillow (for GIF export)
- ffmpeg-python (for video export)
- FastAPI (for API endpoints)

## Related Documentation

- [3D Visualization Guide](3D_VISUALIZATION_GUIDE.md)
- [Export Formats Guide](3D_EXPORT_FORMATS_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
