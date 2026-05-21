import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Checkbox } from 'primereact/checkbox';
import { Slider } from 'primereact/slider';
import { Scene3D } from './Scene3D';
import { ExportControls } from './ExportControls';
import './Viewer3D.css';

interface Viewer3DProps {
  roofType: 'flat' | 'gable' | 'hip';
  roofWidth: number;
  roofLength: number;
  roofHeight?: number;
  roofAngle: number;
  moduleCount: number;
}

export const Viewer3D: React.FC<Viewer3DProps> = ({
  roofType,
  roofWidth,
  roofLength,
  roofHeight = 3,
  roofAngle,
  moduleCount
}) => {
  const [showGrid, setShowGrid] = useState(true);
  const [showSky, setShowSky] = useState(true);
  const [autoRotate, setAutoRotate] = useState(false);
  const [cameraDistance, setCameraDistance] = useState(15);

  const cameraPosition: [number, number, number] = [
    cameraDistance,
    cameraDistance * 0.7,
    cameraDistance
  ];

  const resetView = () => {
    setCameraDistance(15);
    setAutoRotate(false);
  };

  return (
    <Card className="viewer-3d-card">
      <div className="viewer-3d-container">
        <div className="viewer-3d-header">
          <h3>3D Visualization</h3>
          <div className="viewer-3d-controls">
            <div className="control-group">
              <Checkbox
                inputId="grid"
                checked={showGrid}
                onChange={(e) => setShowGrid(e.checked || false)}
              />
              <label htmlFor="grid">Show Grid</label>
            </div>
            <div className="control-group">
              <Checkbox
                inputId="sky"
                checked={showSky}
                onChange={(e) => setShowSky(e.checked || false)}
              />
              <label htmlFor="sky">Show Sky</label>
            </div>
            <div className="control-group">
              <Checkbox
                inputId="rotate"
                checked={autoRotate}
                onChange={(e) => setAutoRotate(e.checked || false)}
              />
              <label htmlFor="rotate">Auto Rotate</label>
            </div>
            <Button
              label="Reset View"
              icon="pi pi-refresh"
              onClick={resetView}
              className="p-button-sm p-button-outlined"
            />
          </div>
        </div>

        <div className="viewer-3d-zoom-control">
          <label>Camera Distance:</label>
          <Slider
            value={cameraDistance}
            onChange={(e) => setCameraDistance(e.value as number)}
            min={5}
            max={50}
            step={1}
            style={{ width: '200px' }}
          />
          <span>{cameraDistance}m</span>
        </div>

        <div className="viewer-3d-scene">
          <Scene3D
            roofType={roofType}
            roofWidth={roofWidth}
            roofLength={roofLength}
            roofHeight={roofHeight}
            roofAngle={roofAngle}
            moduleCount={moduleCount}
            showGrid={showGrid}
            showSky={showSky}
            autoRotate={autoRotate}
            cameraPosition={cameraPosition}
          />
        </div>

        <div className="viewer-3d-info">
          <div className="info-item">
            <strong>Roof Type:</strong> {roofType}
          </div>
          <div className="info-item">
            <strong>Dimensions:</strong> {roofWidth}m × {roofLength}m
          </div>
          <div className="info-item">
            <strong>Roof Angle:</strong> {roofAngle}°
          </div>
          <div className="info-item">
            <strong>Modules:</strong> {moduleCount}
          </div>
        </div>

        <div className="viewer-3d-export">
          <h4>Export 3D Model</h4>
          <ExportControls filename={`solar-${roofType}-${moduleCount}modules`} />
        </div>

        <div className="viewer-3d-instructions">
          <h4>Controls:</h4>
          <ul>
            <li><strong>Rotate:</strong> Left mouse button + drag</li>
            <li><strong>Zoom:</strong> Mouse wheel or pinch</li>
            <li><strong>Pan:</strong> Right mouse button + drag</li>
          </ul>
        </div>
      </div>
    </Card>
  );
};
