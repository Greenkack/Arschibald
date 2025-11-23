# 3D Animation System - Quick Reference

## Animation Types

| Type | Use Case | Key Features |
|------|----------|--------------|
| **360° Rotation** | Product showcase | Circular camera movement, constant height |
| **Fly-Through** | Site tours | Multiple waypoints, smooth interpolation |
| **Assembly** | Installation process | Sequential object appearance |
| **Time-Lapse** | Sun movement | Solar position calculation, shading analysis |
| **Presentation** | Client presentations | Multiple scenes, transitions |

## Quick Start Examples

### 360° Rotation
```python
frames = service.generate_rotation_360(
    center_point=(0, 0, 0),
    radius=15.0,
    height=10.0,
    config=config
)
```

### Fly-Through
```python
frames = service.generate_fly_through(
    waypoints=[(0,0,5), (10,0,5), (10,10,5)],
    look_at_points=[(5,5,0), (5,5,0), (5,5,0)],
    config=config
)
```

### Assembly
```python
frames = service.generate_assembly_animation(
    objects=[
        {'id': 'obj1', 'name': 'Module 1'},
        {'id': 'obj2', 'name': 'Module 2'}
    ],
    config=config
)
```

### Time-Lapse
```python
frames = service.generate_time_lapse(
    location=(52.52, 13.405),  # lat, lon
    date=datetime(2024, 6, 21),
    config=config
)
```

### Presentation
```python
frames = service.generate_presentation_mode(
    scenes=[
        {
            'name': 'Scene 1',
            'camera_position': (10, 10, 10),
            'camera_target': (0, 0, 0)
        }
    ],
    config=config
)
```

## Configuration

```python
config = AnimationConfig(
    animation_type=AnimationType.ROTATION_360,
    duration=10.0,        # seconds (max 300)
    fps=30,               # 15, 24, 30, or 60
    resolution=(1920, 1080),
    quality='high',       # low, medium, high, ultra
    loop=True,
    smooth_transitions=True
)
```

## Export Formats

```python
# GIF
service.export_animation(frames, AnimationFormat.GIF, 'output.gif', config)

# MP4
service.export_animation(frames, AnimationFormat.MP4, 'output.mp4', config)

# WebM
service.export_animation(frames, AnimationFormat.WEBM, 'output.webm', config)

# PNG Frames
service.export_animation(frames, AnimationFormat.FRAMES, 'output/', config)
```

## API Endpoints

### Create Animation
```bash
POST /api/v1/animation-3d/rotation-360
POST /api/v1/animation-3d/fly-through
POST /api/v1/animation-3d/assembly
POST /api/v1/animation-3d/time-lapse
POST /api/v1/animation-3d/presentation
```

### Export Animation
```bash
POST /api/v1/animation-3d/export
```

### Download Animation
```bash
GET /api/v1/animation-3d/download/{animation_id}
```

## Quality Settings

| Quality | Bitrate | Use Case |
|---------|---------|----------|
| Low | 1M | Quick previews |
| Medium | 2M | Standard output |
| High | 5M | Professional use |
| Ultra | 10M | Maximum quality |

## Resolution Presets

| Name | Resolution | Aspect Ratio |
|------|------------|--------------|
| HD | 1280 x 720 | 16:9 |
| Full HD | 1920 x 1080 | 16:9 |
| 2K | 2560 x 1440 | 16:9 |
| 4K | 3840 x 2160 | 16:9 |

## FPS Recommendations

| FPS | Use Case |
|-----|----------|
| 15 | Low bandwidth |
| 24 | Cinematic |
| 30 | Standard |
| 60 | Smooth motion |

## Common Patterns

### Product Showcase (360°)
- Duration: 10-15 seconds
- FPS: 30
- Quality: High
- Resolution: 1920x1080

### Site Tour (Fly-Through)
- Duration: 15-30 seconds
- FPS: 30
- Quality: High
- Smooth transitions: True

### Installation Process (Assembly)
- Duration: 10-20 seconds
- FPS: 30
- Quality: Medium
- Sequential appearance

### Sun Study (Time-Lapse)
- Duration: 20-30 seconds
- FPS: 30
- Quality: High
- Full day simulation

### Client Presentation (Multi-Scene)
- Duration: 30-60 seconds
- FPS: 30
- Quality: High
- 3-5 scenes

## Best Practices

### Performance
- ✅ Use 30 FPS for most cases
- ✅ Keep animations under 30 seconds
- ✅ Use appropriate resolution
- ❌ Avoid 4K unless necessary
- ❌ Don't use 60 FPS for long animations

### Quality
- ✅ Enable smooth transitions
- ✅ Use consistent camera speed
- ✅ Follow composition rules
- ❌ Avoid jerky movements
- ❌ Don't overuse effects

### File Size
- ✅ Use appropriate quality setting
- ✅ Choose right format (GIF/MP4/WebM)
- ✅ Optimize for delivery method
- ❌ Don't use ultra quality for web
- ❌ Avoid unnecessary resolution

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Choppy animation | Increase FPS or enable smooth_transitions |
| Large file size | Reduce resolution, duration, or quality |
| Export fails | Check disk space and permissions |
| Wrong sun position | Verify latitude/longitude and date |
| Slow generation | Reduce FPS or resolution |

## Requirements

- Python 3.10+
- NumPy
- PIL/Pillow (GIF export)
- ffmpeg-python (video export)
- FastAPI (API)

## Related Documentation

- [Complete Guide](3D_ANIMATION_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [3D Visualization Guide](3D_VISUALIZATION_GUIDE.md)
