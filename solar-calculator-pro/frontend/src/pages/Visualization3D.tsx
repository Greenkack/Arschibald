import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { Slider } from 'primereact/slider';
import { Viewer3D } from '../components/3d';
import './Visualization3D.css';

export const Visualization3D: React.FC = () => {
  const [roofType, setRoofType] = useState<'flat' | 'gable' | 'hip'>('gable');
  const [roofWidth, setRoofWidth] = useState(10);
  const [roofLength, setRoofLength] = useState(12);
  const [roofHeight, setRoofHeight] = useState(3);
  const [roofAngle, setRoofAngle] = useState(30);
  const [moduleCount, setModuleCount] = useState(24);

  const roofTypes = [
    { label: 'Flat Roof', value: 'flat' },
    { label: 'Gable Roof', value: 'gable' },
    { label: 'Hip Roof', value: 'hip' }
  ];

  return (
    <div className="visualization-3d-page">
      <div className="page-header">
        <h1>3D Solar Installation Visualization</h1>
        <p>Configure your solar installation and view it in 3D</p>
      </div>

      <div className="visualization-3d-content">
        <Card className="configuration-card">
          <h3>Configuration</h3>
          
          <div className="config-section">
            <h4>Roof Configuration</h4>
            
            <div className="form-field">
              <label htmlFor="roofType">Roof Type</label>
              <Dropdown
                id="roofType"
                value={roofType}
                options={roofTypes}
                onChange={(e) => setRoofType(e.value)}
                placeholder="Select roof type"
              />
            </div>

            <div className="form-field">
              <label htmlFor="roofWidth">Roof Width (m)</label>
              <InputNumber
                id="roofWidth"
                value={roofWidth}
                onValueChange={(e) => setRoofWidth(e.value || 10)}
                min={5}
                max={30}
                step={0.5}
                showButtons
              />
            </div>

            <div className="form-field">
              <label htmlFor="roofLength">Roof Length (m)</label>
              <InputNumber
                id="roofLength"
                value={roofLength}
                onValueChange={(e) => setRoofLength(e.value || 12)}
                min={5}
                max={30}
                step={0.5}
                showButtons
              />
            </div>

            <div className="form-field">
              <label htmlFor="roofHeight">Building Height (m)</label>
              <InputNumber
                id="roofHeight"
                value={roofHeight}
                onValueChange={(e) => setRoofHeight(e.value || 3)}
                min={2}
                max={10}
                step={0.5}
                showButtons
              />
            </div>

            <div className="form-field">
              <label htmlFor="roofAngle">
                Roof Angle: {roofAngle}°
              </label>
              <Slider
                id="roofAngle"
                value={roofAngle}
                onChange={(e) => setRoofAngle(e.value as number)}
                min={0}
                max={60}
                step={5}
              />
            </div>
          </div>

          <div className="config-section">
            <h4>Solar Modules</h4>
            
            <div className="form-field">
              <label htmlFor="moduleCount">Number of Modules</label>
              <InputNumber
                id="moduleCount"
                value={moduleCount}
                onValueChange={(e) => setModuleCount(e.value || 24)}
                min={1}
                max={100}
                step={1}
                showButtons
              />
            </div>

            <div className="info-box">
              <p><strong>Module Specifications:</strong></p>
              <ul>
                <li>Size: 1.7m × 1.0m</li>
                <li>Power: 400W per module</li>
                <li>Total Power: {(moduleCount * 400 / 1000).toFixed(2)} kWp</li>
              </ul>
            </div>
          </div>

          <div className="config-section">
            <h4>Quick Presets</h4>
            <div className="preset-buttons">
              <button
                className="preset-button"
                onClick={() => {
                  setRoofType('flat');
                  setRoofWidth(8);
                  setRoofLength(10);
                  setRoofAngle(0);
                  setModuleCount(16);
                }}
              >
                Small Flat Roof
              </button>
              <button
                className="preset-button"
                onClick={() => {
                  setRoofType('gable');
                  setRoofWidth(12);
                  setRoofLength(15);
                  setRoofAngle(35);
                  setModuleCount(36);
                }}
              >
                Medium Gable Roof
              </button>
              <button
                className="preset-button"
                onClick={() => {
                  setRoofType('hip');
                  setRoofWidth(15);
                  setRoofLength(18);
                  setRoofAngle(25);
                  setModuleCount(48);
                }}
              >
                Large Hip Roof
              </button>
            </div>
          </div>
        </Card>

        <div className="viewer-container">
          <Viewer3D
            roofType={roofType}
            roofWidth={roofWidth}
            roofLength={roofLength}
            roofHeight={roofHeight}
            roofAngle={roofAngle}
            moduleCount={moduleCount}
          />
        </div>
      </div>
    </div>
  );
};
