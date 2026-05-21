# Phase 2, Task 4: Quick Reference Guide

## Sonnenverlauf-Animation Optimierungen

### Quick Start

```python
import plotly.graph_objects as go
from utils.solar_animation import (
    create_sun_path_animation,
    update_shadows_realtime,
    render_animation_controls_enhanced
)

# 1. Create base figure
fig = go.Figure()

# 2. Add building and modules to figure
# ... (your existing code)

# 3. Create optimized animation
building_center = (5.0, 4.0, 0.0)

animated_fig = create_sun_path_animation(
    fig,
    building_center=building_center,
    radius=50.0,
    num_frames=24,        # 12-48 frames
    fps=30,               # 12-60 FPS
    time_compression=10.0 # 1-100x speed
)

# 4. Add real-time shadows
module_positions = [
    (2.0, 2.0, 6.0),
    (4.0, 2.0, 6.0),
    # ... more modules
]

final_fig = update_shadows_realtime(
    animated_fig,
    sun_azimuth=180.0,    # 0°=North, 180°=South
    sun_elevation=45.0,   # 0°=Horizon, 90°=Zenith
    module_positions=module_positions
)

# 5. Display
st.plotly_chart(final_fig)
```

---

## New Features

### 1. Configurable FPS (12-60)

**Purpose:** Control animation smoothness

**Usage:**
```python
# Smooth animation (higher CPU usage)
fig = create_sun_path_animation(fig, center, fps=60)

# Standard animation (balanced)
fig = create_sun_path_animation(fig, center, fps=24)

# Performance mode (lower CPU usage)
fig = create_sun_path_animation(fig, center, fps=12)
```

**Recommendations:**
- 60 FPS: High-end presentations
- 30 FPS: Standard use
- 24 FPS: Default (cinema standard)
- 12 FPS: Low-power devices

---

### 2. Time Compression (1-100x)

**Purpose:** Speed up or slow down animation

**Usage:**
```python
# Real-time (1 hour = 1 hour)
fig = create_sun_path_animation(fig, center, time_compression=1.0)

# 10x speed (1 hour = 6 minutes) - DEFAULT
fig = create_sun_path_animation(fig, center, time_compression=10.0)

# 100x speed (1 hour = 36 seconds)
fig = create_sun_path_animation(fig, center, time_compression=100.0)
```

**Recommendations:**
- 1x: Educational/detailed analysis
- 10x: Standard presentations
- 50x: Quick overview
- 100x: Very fast preview

---

### 3. Caching

**Purpose:** Improve performance by caching sun positions

**Automatic:** No code changes needed!

**How it works:**
```python
# First call: Calculates positions
positions1 = _calculate_sun_positions_cached(48.0, 11.0, "2024-06-21", 24)

# Second call: Returns cached result (instant!)
positions2 = _calculate_sun_positions_cached(48.0, 11.0, "2024-06-21", 24)
```

**Cache size:** 128 entries (automatically managed)

---

### 4. Real-time Shadows

**Purpose:** Show realistic shadows based on sun position

**Usage:**
```python
# Add shadows for current sun position
fig = update_shadows_realtime(
    fig,
    sun_azimuth=180.0,    # Sun in South
    sun_elevation=45.0,   # Sun at 45° above horizon
    module_positions=[(x, y, z), ...]
)
```

**Sun Position Guide:**
- **Azimuth:**
  - 0° = North
  - 90° = East
  - 180° = South
  - 270° = West
  
- **Elevation:**
  - 0° = Horizon (sunrise/sunset)
  - 45° = Mid-morning/afternoon
  - 90° = Zenith (noon at equator)

**Performance:** Automatically limited to 20 shadows

---

### 5. Enhanced UI Controls

**Purpose:** User-friendly controls for all parameters

**Usage:**
```python
import streamlit as st
from utils.solar_animation import render_animation_controls_enhanced

# Render controls
params = render_animation_controls_enhanced(animation_type="sun_path")

# Use parameters
fig = create_sun_path_animation(
    fig,
    building_center,
    fps=params['fps'],
    time_compression=params['time_compression'],
    num_frames=params['num_frames'],
    radius=params['radius']
)

# Optional: Use advanced options
if params.get('show_shadows', True):
    fig = update_shadows_realtime(fig, 180.0, 45.0, module_positions)
```

**Available Parameters:**
- `fps`: Frames per second (12-60)
- `time_compression`: Speed multiplier (1-100x)
- `num_frames`: Number of frames (12-48)
- `month`: Month selection (Januar-Dezember)
- `radius`: Sun path radius (30-100m)
- `show_shadows`: Enable/disable shadows
- `show_sun_rays`: Enable/disable sun rays
- `auto_play`: Auto-start animation

---

## Performance Tips

### 1. Optimize Frame Count
```python
# More frames = smoother but slower
fig = create_sun_path_animation(fig, center, num_frames=48)  # Detailed

# Fewer frames = faster but less smooth
fig = create_sun_path_animation(fig, center, num_frames=12)  # Fast
```

### 2. Limit Shadows
```python
# Shadows are automatically limited to 20 modules
# If you have 100 modules, only first 20 get shadows

# To control which modules get shadows:
important_modules = module_positions[:20]  # Select first 20
fig = update_shadows_realtime(fig, 180.0, 45.0, important_modules)
```

### 3. Use Caching
```python
# Cache is automatic, but you can help by:
# - Using consistent parameters
# - Reusing the same date/location
# - Avoiding unnecessary recalculations

# Good (uses cache):
for i in range(10):
    positions = _calculate_sun_positions_cached(48.0, 11.0, "2024-06-21", 24)

# Bad (bypasses cache):
for i in range(10):
    positions = _calculate_sun_positions_cached(48.0+i*0.01, 11.0, "2024-06-21", 24)
```

---

## Common Use Cases

### Case 1: Standard Presentation
```python
# Balanced performance and quality
fig = create_sun_path_animation(
    fig, center,
    fps=24,
    time_compression=10.0,
    num_frames=24
)
```

### Case 2: High-Quality Demo
```python
# Maximum quality for important presentations
fig = create_sun_path_animation(
    fig, center,
    fps=60,
    time_compression=5.0,
    num_frames=48
)
```

### Case 3: Quick Preview
```python
# Fast preview for testing
fig = create_sun_path_animation(
    fig, center,
    fps=12,
    time_compression=50.0,
    num_frames=12
)
```

### Case 4: Educational/Detailed
```python
# Slow, detailed animation for learning
fig = create_sun_path_animation(
    fig, center,
    fps=24,
    time_compression=1.0,  # Real-time
    num_frames=48
)
```

---

## Troubleshooting

### Animation is too fast
```python
# Reduce time compression
fig = create_sun_path_animation(fig, center, time_compression=1.0)
```

### Animation is choppy
```python
# Increase FPS or frame count
fig = create_sun_path_animation(fig, center, fps=30, num_frames=36)
```

### Shadows not appearing
```python
# Check sun elevation (must be > 0)
if sun_elevation > 0:
    fig = update_shadows_realtime(fig, azimuth, elevation, positions)
```

### Performance is slow
```python
# Reduce frame count and FPS
fig = create_sun_path_animation(fig, center, fps=12, num_frames=12)

# Limit module count for shadows
fig = update_shadows_realtime(fig, azimuth, elevation, positions[:10])
```

---

## API Reference

### create_sun_path_animation()
```python
def create_sun_path_animation(
    fig: go.Figure,
    building_center: Tuple[float, float, float],
    radius: float = 50.0,
    num_frames: int = 24,
    fps: int = 24,
    time_compression: float = 1.0
) -> go.Figure
```

**Parameters:**
- `fig`: Plotly Figure object
- `building_center`: (x, y, z) center point
- `radius`: Sun path radius in meters (30-100)
- `num_frames`: Number of animation frames (12-48)
- `fps`: Frames per second (12-60)
- `time_compression`: Speed multiplier (1-100)

**Returns:** Figure with animation

---

### update_shadows_realtime()
```python
def update_shadows_realtime(
    fig: go.Figure,
    sun_azimuth: float,
    sun_elevation: float,
    module_positions: List[Tuple[float, float, float]]
) -> go.Figure
```

**Parameters:**
- `fig`: Plotly Figure object
- `sun_azimuth`: Sun direction in degrees (0-360)
- `sun_elevation`: Sun height in degrees (0-90)
- `module_positions`: List of (x, y, z) tuples

**Returns:** Figure with shadows

---

### render_animation_controls_enhanced()
```python
def render_animation_controls_enhanced(
    animation_type: str = "sun_path"
) -> Dict[str, Any]
```

**Parameters:**
- `animation_type`: Type of animation ("sun_path", "rotation", etc.)

**Returns:** Dictionary with user-selected parameters

---

## Examples

See `tests/test_phase2_task4_sun_animation.py` for comprehensive examples.

---

*Last Updated: January 3, 2026*
