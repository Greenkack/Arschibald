import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { Grid, Sky, Environment } from '@react-three/drei';
import { RoofModel } from './RoofModel';
import { ModulePlacement } from './ModulePlacement';
import { CameraControls } from './CameraControls';

interface Scene3DProps {
  roofType: 'flat' | 'gable' | 'hip';
  roofWidth: number;
  roofLength: number;
  roofHeight: number;
  roofAngle: number;
  moduleCount: number;
  showGrid?: boolean;
  showSky?: boolean;
  autoRotate?: boolean;
  cameraPosition?: [number, number, number];
}

export const Scene3D: React.FC<Scene3DProps> = ({
  roofType,
  roofWidth,
  roofLength,
  roofHeight,
  roofAngle,
  moduleCount,
  showGrid = true,
  showSky = true,
  autoRotate = false,
  cameraPosition = [15, 10, 15]
}) => {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Canvas
        camera={{
          position: cameraPosition,
          fov: 50
        }}
        shadows
      >
        <Suspense fallback={null}>
          {/* Lighting */}
          <ambientLight intensity={0.5} />
          <directionalLight
            position={[10, 10, 5]}
            intensity={1}
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          <pointLight position={[-10, 10, -10]} intensity={0.5} />

          {/* Environment */}
          {showSky && <Sky sunPosition={[100, 20, 100]} />}
          <Environment preset="sunset" />

          {/* Grid */}
          {showGrid && (
            <Grid
              args={[50, 50]}
              cellSize={1}
              cellThickness={0.5}
              cellColor="#6f6f6f"
              sectionSize={5}
              sectionThickness={1}
              sectionColor="#9d4b4b"
              fadeDistance={50}
              fadeStrength={1}
              followCamera={false}
            />
          )}

          {/* 3D Models */}
          <RoofModel
            roofType={roofType}
            width={roofWidth}
            length={roofLength}
            height={roofHeight}
            angle={roofAngle}
          />

          <ModulePlacement
            roofWidth={roofWidth}
            roofLength={roofLength}
            roofHeight={roofHeight}
            roofAngle={roofAngle}
            moduleCount={moduleCount}
          />

          {/* Camera Controls */}
          <CameraControls autoRotate={autoRotate} />
        </Suspense>
      </Canvas>
    </div>
  );
};
