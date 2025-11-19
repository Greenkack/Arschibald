# 3D Visualization Quick Reference

## Installation

```bash
npm install three @react-three/fiber @react-three/drei
npm install --save-dev @types/three
```

## Quick Start

### Basic Viewer

```typescript
import { Viewer3D } from '@components/3d';

<Viewer3D
  roofType="gable"
  roofWidth={10}
  roofLength={12}
  roofAngle={30}
  moduleCount={24}
/>
```

### Custom Scene

```typescript
import { Canvas } from '@react-three/fiber';
import { RoofModel, ModulePlacement, CameraControls } from '@components/3d';

<Canvas>
  <ambientLight />
  <RoofModel roofType="flat" width={10} length={12} height={3} angle={0} />
  <ModulePlacement moduleCount={20} roofWidth={10} roofLength={12} />
  <CameraControls />
</Canvas>
```

## Components

### Viewer3D
Complete 3D viewer with controls
```typescript
<Viewer3D
  roofType="gable"      // 'flat' | 'gable' | 'hip'
  roofWidth={10}        // meters
  roofLength={12}       // meters
  roofHeight={3}        // meters
  roofAngle={30}        // degrees
  moduleCount={24}      // number of modules
/>
```

### Scene3D
Core 3D scene
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

### RoofModel
Individual roof component
```typescript
<RoofModel
  roofType="gable"
  width={10}
  length={12}
  height={3}
  angle={30}
  color="#8B4513"
/>
```

### SolarModule
Individual solar panel
```typescript
<SolarModule
  position={[0, 0, 0]}
  rotation={[0, 0, 0]}
  width={1.7}
  height={1.0}
  selected={false}
  onClick={() => {}}
/>
```

### ModulePlacement
Automatic module placement
```typescript
<ModulePlacement
  roofWidth={10}
  roofLength={12}
  roofHeight={3}
  roofAngle={30}
  moduleCount={24}
  moduleWidth={1.7}
  moduleHeight={1.0}
  spacing={0.05}
/>
```

### CameraControls
Camera manipulation
```typescript
<CameraControls
  enableRotate={true}
  enableZoom={true}
  enablePan={true}
  autoRotate={false}
  minDistance={5}
  maxDistance={50}
/>
```

### ExportControls
Export functionality
```typescript
<ExportControls filename="solar-installation" />
```

## Controls

### Mouse/Touch
- **Rotate**: Left click + drag
- **Zoom**: Mouse wheel / Pinch
- **Pan**: Right click + drag

### Keyboard
- **Arrow keys**: Rotate view
- **+/-**: Zoom in/out

## Export Formats

| Format | Use Case | File Extension |
|--------|----------|----------------|
| GLTF | Web, general 3D | .gltf |
| GLB | Web, smaller size | .glb |
| STL | 3D printing | .stl |
| OBJ | CAD software | .obj |
| PNG | Screenshot | .png |

## Common Patterns

### With State Management

```typescript
const [config, setConfig] = useState({
  roofType: 'gable',
  roofWidth: 10,
  roofLength: 12,
  moduleCount: 24
});

<Viewer3D {...config} />
```

### With Solar Calculator

```typescript
const { result } = useSolarCalculation();

{result && (
  <Viewer3D
    roofType={result.roofType}
    roofWidth={result.roofWidth}
    roofLength={result.roofLength}
    roofAngle={result.roofAngle}
    moduleCount={result.moduleCount}
  />
)}
```

### Responsive Container

```typescript
<div style={{ width: '100%', height: '600px' }}>
  <Scene3D {...props} />
</div>
```

## Performance Tips

1. **Limit module count** (max 100 recommended)
2. **Use Suspense** for lazy loading
3. **Disable auto-rotate** when not needed
4. **Reuse geometries** and materials
5. **Clean up** on unmount

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Black screen | Add lights: `<ambientLight />` |
| No controls | Ensure `<CameraControls />` inside `<Canvas>` |
| Poor performance | Reduce module count or simplify geometry |
| Export fails | Check all exporters are imported |

## File Structure

```
src/components/3d/
├── Scene3D.tsx           # Main scene
├── RoofModel.tsx         # Roof rendering
├── SolarModule.tsx       # Solar panel
├── ModulePlacement.tsx   # Module layout
├── CameraControls.tsx    # Camera controls
├── ExportControls.tsx    # Export functionality
├── Viewer3D.tsx          # Complete viewer
├── Viewer3D.css          # Styles
└── index.ts              # Exports
```

## Routes

Add to routes:
```typescript
{
  path: '3d-visualization',
  element: <Visualization3D />
}
```

## Dependencies

```json
{
  "three": "^0.160.0",
  "@react-three/fiber": "^8.15.13",
  "@react-three/drei": "^9.93.0",
  "@types/three": "^0.160.0"
}
```

## Resources

- [Three.js Docs](https://threejs.org/docs/)
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)
- [Drei Components](https://github.com/pmndrs/drei)
