# 3D Visualization Integration Guide

## Overview

This guide covers the 3D visualization system integrated into the Solar Calculator Pro application using Three.js, React Three Fiber, and React Three Drei.

## Features

### ✅ Implemented Features

1. **3D Roof Model Viewer**
   - Support for multiple roof types (flat, gable, hip)
   - Configurable dimensions (width, length, height)
   - Adjustable roof angles
   - Realistic rendering with materials and lighting

2. **Solar Module Placement**
   - Automatic optimal placement algorithm
   - Configurable module count
   - Visual representation of solar panels
   - Module selection and highlighting
   - Proper spacing between modules

3. **Camera Controls**
   - Orbit controls (rotate, zoom, pan)
   - Auto-rotate mode
   - Adjustable camera distance
   - Reset view functionality
   - Smooth damping for natural movement

4. **Export Functionality**
   - GLTF export (text format)
   - GLB export (binary format)
   - STL export (3D printing)
   - OBJ export (Wavefront)
   - PNG image export

5. **Visual Enhancements**
   - Grid overlay (toggleable)
   - Sky environment (toggleable)
   - Realistic lighting (ambient, directional, point lights)
   - Shadows
   - Material properties (metalness, roughness)

## Installation

### Dependencies

The following packages have been added to `package.json`:

```json
{
  "dependencies": {
    "three": "^0.160.0",
    "@react-three/fiber": "^8.15.13",
    "@react-three/drei": "^9.93.0"
  },
  "devDependencies": {
    "@types/three": "^0.160.0"
  }
}
```

### Install Dependencies

```bash
cd solar-calculator-pro/frontend
npm install
```

## Component Architecture

### Core Components

#### 1. `Scene3D`
Main 3D scene component that orchestrates all 3D elements.

```typescript
<Scene3D
  roofType="gable"
  roofWidth={10}
  roofLength={12}
  roofHeight={3}
  roofAngle={30}
  moduleCount={24}
  showGrid={true}
  showSky={true}
  autoRotate={false}
  cameraPosition={[15, 10, 15]}
/>
```

#### 2. `RoofModel`
Renders different types of roofs with configurable properties.

**Supported Roof Types:**
- **Flat**: Simple flat roof surface
- **Gable**: Two-sided pitched roof
- **Hip**: Four-sided pitched roof

#### 3. `SolarModule`
Individual solar panel component with realistic appearance.

**Features:**
- Configurable dimensions (default: 1.7m × 1.0m)
- Metallic appearance with solar cells
- Selection highlighting
- Click interaction

#### 4. `ModulePlacement`
Handles automatic placement of solar modules on the roof.

**Algorithm:**
- Calculates optimal grid layout
- Respects spacing requirements
- Centers module array on roof
- Matches roof angle

#### 5. `CameraControls`
Provides intuitive camera manipulation.

**Controls:**
- **Rotate**: Left mouse button + drag
- **Zoom**: Mouse wheel or pinch
- **Pan**: Right mouse button + drag

#### 6. `ExportControls`
Enables exporting 3D models in various formats.

**Export Formats:**
- **GLTF**: Text-based 3D format (good for web)
- **GLB**: Binary 3D format (smaller file size)
- **STL**: For 3D printing
- **OBJ**: Universal 3D format
- **PNG**: Screenshot of current view

#### 7. `Viewer3D`
Complete viewer with UI controls and configuration panel.

### Page Component

#### `Visualization3D`
Full-featured page with configuration panel and 3D viewer.

**Configuration Options:**
- Roof type selection
- Roof dimensions (width, length, height)
- Roof angle slider
- Module count
- Quick presets for common scenarios

## Usage Examples

### Basic Usage

```typescript
import { Viewer3D } from '@components/3d';

function MyComponent() {
  return (
    <Viewer3D
      roofType="gable"
      roofWidth={10}
      roofLength={12}
      roofHeight={3}
      roofAngle={30}
      moduleCount={24}
    />
  );
}
```

### Custom Scene

```typescript
import { Canvas } from '@react-three/fiber';
import { RoofModel, ModulePlacement, CameraControls } from '@components/3d';

function CustomScene() {
  return (
    <Canvas camera={{ position: [15, 10, 15] }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} />
      
      <RoofModel
        roofType="flat"
        width={8}
        length={10}
        height={3}
        angle={0}
      />
      
      <ModulePlacement
        roofWidth={8}
        roofLength={10}
        roofHeight={3}
        roofAngle={0}
        moduleCount={16}
      />
      
      <CameraControls />
    </Canvas>
  );
}
```

### Integration with Solar Calculator

```typescript
import { Viewer3D } from '@components/3d';
import { useSolarCalculation } from '@hooks/useSolarCalculation';

function SolarCalculatorWithVisualization() {
  const { result } = useSolarCalculation();
  
  return (
    <div>
      {/* Solar calculator form */}
      <SolarCalculatorForm />
      
      {/* 3D visualization */}
      {result && (
        <Viewer3D
          roofType={result.roofType}
          roofWidth={result.roofWidth}
          roofLength={result.roofLength}
          roofAngle={result.roofAngle}
          moduleCount={result.moduleCount}
        />
      )}
    </div>
  );
}
```

## Customization

### Styling

The 3D viewer can be styled using CSS:

```css
.viewer-3d-scene {
  border: 2px solid var(--surface-border);
  border-radius: 8px;
  background: #87CEEB; /* Sky blue background */
}
```

### Module Appearance

Customize solar module appearance:

```typescript
<SolarModule
  position={[0, 0, 0]}
  width={1.7}
  height={1.0}
  thickness={0.04}
  color="#1a1a2e"  // Custom color
  selected={false}
/>
```

### Lighting

Adjust scene lighting:

```typescript
<ambientLight intensity={0.5} />
<directionalLight 
  position={[10, 10, 5]} 
  intensity={1}
  castShadow
/>
<pointLight position={[-10, 10, -10]} intensity={0.5} />
```

## Performance Optimization

### Best Practices

1. **Use Suspense for Lazy Loading**
   ```typescript
   <Suspense fallback={<Loading />}>
     <Scene3D {...props} />
   </Suspense>
   ```

2. **Limit Module Count**
   - Recommended maximum: 100 modules
   - Use LOD (Level of Detail) for large installations

3. **Optimize Geometry**
   - Reuse geometries and materials
   - Use instanced meshes for repeated elements

4. **Control Render Loop**
   - Disable auto-rotation when not needed
   - Use `frameloop="demand"` for static scenes

### Memory Management

```typescript
// Clean up resources
useEffect(() => {
  return () => {
    // Dispose geometries and materials
    scene.traverse((object) => {
      if (object.geometry) object.geometry.dispose();
      if (object.material) object.material.dispose();
    });
  };
}, []);
```

## Troubleshooting

### Common Issues

#### 1. Black Screen
**Cause**: Missing lights or camera position issues
**Solution**: Ensure proper lighting and camera setup

```typescript
<ambientLight intensity={0.5} />
<directionalLight position={[10, 10, 5]} />
```

#### 2. Performance Issues
**Cause**: Too many modules or complex geometry
**Solution**: Reduce module count or simplify geometry

#### 3. Export Not Working
**Cause**: Missing exporters or scene not ready
**Solution**: Ensure all exporters are imported

```typescript
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter';
import { STLExporter } from 'three/examples/jsm/exporters/STLExporter';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter';
```

#### 4. Controls Not Responding
**Cause**: Event handlers not properly attached
**Solution**: Ensure OrbitControls is inside Canvas

## API Reference

### Scene3D Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| roofType | 'flat' \| 'gable' \| 'hip' | - | Type of roof |
| roofWidth | number | - | Roof width in meters |
| roofLength | number | - | Roof length in meters |
| roofHeight | number | - | Building height in meters |
| roofAngle | number | - | Roof angle in degrees |
| moduleCount | number | - | Number of solar modules |
| showGrid | boolean | true | Show/hide grid |
| showSky | boolean | true | Show/hide sky |
| autoRotate | boolean | false | Enable auto-rotation |
| cameraPosition | [number, number, number] | [15, 10, 15] | Initial camera position |

### Viewer3D Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| roofType | 'flat' \| 'gable' \| 'hip' | - | Type of roof |
| roofWidth | number | - | Roof width in meters |
| roofLength | number | - | Roof length in meters |
| roofHeight | number | 3 | Building height in meters |
| roofAngle | number | - | Roof angle in degrees |
| moduleCount | number | - | Number of solar modules |

## Future Enhancements

### Planned Features

1. **Advanced Module Placement**
   - Manual drag-and-drop placement
   - Obstacle avoidance
   - Shading analysis visualization

2. **Realistic Rendering**
   - Time-of-day simulation
   - Seasonal sun path
   - Shadow casting from modules

3. **Interactive Features**
   - Module information on hover
   - Performance metrics overlay
   - Heat map visualization

4. **Additional Export Formats**
   - PDF 3D export
   - DXF for CAD software
   - Video animation export

5. **VR/AR Support**
   - WebXR integration
   - Mobile AR preview
   - VR walkthrough

## Resources

### Documentation
- [Three.js Documentation](https://threejs.org/docs/)
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)
- [React Three Drei](https://github.com/pmndrs/drei)

### Examples
- [Three.js Examples](https://threejs.org/examples/)
- [React Three Fiber Examples](https://docs.pmnd.rs/react-three-fiber/getting-started/examples)

### Community
- [Three.js Discourse](https://discourse.threejs.org/)
- [React Three Fiber Discord](https://discord.gg/poimandres)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API reference
3. Consult Three.js documentation
4. Contact the development team

## License

This 3D visualization system is part of the Solar Calculator Pro application and follows the same license terms.
