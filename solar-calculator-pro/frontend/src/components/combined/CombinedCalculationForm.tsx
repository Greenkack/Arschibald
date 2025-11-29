/**
 * Combined Calculation Form Component
 * 
 * Integrated form for both solar and heat pump system inputs
 */

import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Divider } from 'primereact/divider';
import { Checkbox } from 'primereact/checkbox';
import './CombinedCalculationForm.css';

interface CombinedCalculationFormProps {
  onSubmit: (data: any) => void;
  loading?: boolean;
}

export const CombinedCalculationForm: React.FC<CombinedCalculationFormProps> = ({
  onSubmit,
  loading = false
}) => {
  // Solar system inputs
  const [roofArea, setRoofArea] = useState<number>(50);
  const [roofOrientation, setRoofOrientation] = useState<string>('Süd');
  const [roofAngle, setRoofAngle] = useState<number>(30);
  const [moduleType, setModuleType] = useState<string>('standard');
  const [annualConsumption, setAnnualConsumption] = useState<number>(4000);
  
  // Heat pump inputs
  const [heatedArea, setHeatedArea] = useState<number>(150);
  const [buildingType, setBuildingType] = useState<string>('Altbau saniert');
  const [insulationQuality, setInsulationQuality] = useState<string>('Gut');
  const [currentHeatingSystem, setCurrentHeatingSystem] = useState<string>('Gas');
  const [hotWaterDemand, setHotWaterDemand] = useState<string>('Mittel');
  
  // Combined system options
  const [optimizeForSelfConsumption, setOptimizeForSelfConsumption] = useState<boolean>(true);
  const [includeStorage, setIncludeStorage] = useState<boolean>(false);
  const [storageCapacity, setStorageCapacity] = useState<number>(10);
  const [smartControlEnabled, setSmartControlEnabled] = useState<boolean>(true);
  
  // Location
  const [location, setLocation] = useState<string>('Berlin');

  const orientationOptions = [
    { label: 'Süd', value: 'Süd' },
    { label: 'Süd-Ost', value: 'Süd-Ost' },
    { label: 'Süd-West', value: 'Süd-West' },
    { label: 'Ost', value: 'Ost' },
    { label: 'West', value: 'West' }
  ];

  const moduleTypeOptions = [
    { label: 'Standard (Poly)', value: 'standard' },
    { label: 'Premium (Mono)', value: 'premium' },
    { label: 'High-Efficiency', value: 'high-efficiency' }
  ];

  const buildingTypeOptions = [
    { label: 'Neubau KfW40', value: 'Neubau KfW40' },
    { label: 'Neubau KfW55', value: 'Neubau KfW55' },
    { label: 'Neubau Standard', value: 'Neubau Standard' },
    { label: 'Altbau saniert', value: 'Altbau saniert' },
    { label: 'Altbau teilsaniert', value: 'Altbau teilsaniert' },
    { label: 'Altbau unsaniert', value: 'Altbau unsaniert' }
  ];

  const insulationOptions = [
    { label: 'Sehr gut', value: 'Sehr gut' },
    { label: 'Gut', value: 'Gut' },
    { label: 'Mittel', value: 'Mittel' },
    { label: 'Schlecht', value: 'Schlecht' }
  ];

  const heatingSystemOptions = [
    { label: 'Gas', value: 'Gas' },
    { label: 'Öl', value: 'Öl' },
    { label: 'Strom', value: 'Strom' },
    { label: 'Holz', value: 'Holz' }
  ];

  const hotWaterDemandOptions = [
    { label: 'Niedrig', value: 'Niedrig' },
    { label: 'Mittel', value: 'Mittel' },
    { label: 'Hoch', value: 'Hoch' }
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const formData = {
      solar: {
        roofArea,
        roofOrientation,
        roofAngle,
        moduleType,
        annualConsumption
      },
      heatPump: {
        heatedArea,
        buildingType,
        insulationQuality,
        currentHeatingSystem,
        hotWaterDemand
      },
      combined: {
        optimizeForSelfConsumption,
        includeStorage,
        storageCapacity: includeStorage ? storageCapacity : 0,
        smartControlEnabled
      },
      location
    };
    
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="combined-calculation-form">
      {/* Location */}
      <Card className="form-section">
        <h3>📍 Standort</h3>
        <Divider />
        <div className="form-field">
          <label htmlFor="location">Standort</label>
          <InputText
            id="location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="z.B. Berlin, München, Hamburg"
            className="w-full"
          />
        </div>
      </Card>

      {/* Solar System Inputs */}
      <Card className="form-section">
        <h3>☀️ PV-Anlage</h3>
        <Divider />
        
        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="roofArea">Dachfläche (m²)</label>
            <InputNumber
              id="roofArea"
              value={roofArea}
              onValueChange={(e) => setRoofArea(e.value || 0)}
              min={10}
              max={500}
              showButtons
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="roofOrientation">Dachausrichtung</label>
            <Dropdown
              id="roofOrientation"
              value={roofOrientation}
              options={orientationOptions}
              onChange={(e) => setRoofOrientation(e.value)}
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="roofAngle">Dachneigung (°)</label>
            <InputNumber
              id="roofAngle"
              value={roofAngle}
              onValueChange={(e) => setRoofAngle(e.value || 0)}
              min={0}
              max={90}
              showButtons
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="moduleType">Modultyp</label>
            <Dropdown
              id="moduleType"
              value={moduleType}
              options={moduleTypeOptions}
              onChange={(e) => setModuleType(e.value)}
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="annualConsumption">Jahresverbrauch (kWh)</label>
            <InputNumber
              id="annualConsumption"
              value={annualConsumption}
              onValueChange={(e) => setAnnualConsumption(e.value || 0)}
              min={1000}
              max={20000}
              step={500}
              showButtons
              className="w-full"
            />
          </div>
        </div>
      </Card>

      {/* Heat Pump Inputs */}
      <Card className="form-section">
        <h3>🔥 Wärmepumpe</h3>
        <Divider />
        
        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="heatedArea">Wohnfläche (m²)</label>
            <InputNumber
              id="heatedArea"
              value={heatedArea}
              onValueChange={(e) => setHeatedArea(e.value || 0)}
              min={50}
              max={500}
              showButtons
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="buildingType">Gebäudetyp</label>
            <Dropdown
              id="buildingType"
              value={buildingType}
              options={buildingTypeOptions}
              onChange={(e) => setBuildingType(e.value)}
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="insulationQuality">Dämmqualität</label>
            <Dropdown
              id="insulationQuality"
              value={insulationQuality}
              options={insulationOptions}
              onChange={(e) => setInsulationQuality(e.value)}
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="currentHeatingSystem">Aktuelles Heizsystem</label>
            <Dropdown
              id="currentHeatingSystem"
              value={currentHeatingSystem}
              options={heatingSystemOptions}
              onChange={(e) => setCurrentHeatingSystem(e.value)}
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="hotWaterDemand">Warmwasserbedarf</label>
            <Dropdown
              id="hotWaterDemand"
              value={hotWaterDemand}
              options={hotWaterDemandOptions}
              onChange={(e) => setHotWaterDemand(e.value)}
              className="w-full"
            />
          </div>
        </div>
      </Card>

      {/* Combined System Options */}
      <Card className="form-section">
        <h3>🔄 Systemoptimierung</h3>
        <Divider />
        
        <div className="form-options">
          <div className="form-checkbox">
            <Checkbox
              inputId="optimizeForSelfConsumption"
              checked={optimizeForSelfConsumption}
              onChange={(e) => setOptimizeForSelfConsumption(e.checked || false)}
            />
            <label htmlFor="optimizeForSelfConsumption">
              Für maximalen Eigenverbrauch optimieren
            </label>
          </div>

          <div className="form-checkbox">
            <Checkbox
              inputId="smartControlEnabled"
              checked={smartControlEnabled}
              onChange={(e) => setSmartControlEnabled(e.checked || false)}
            />
            <label htmlFor="smartControlEnabled">
              Intelligente Steuerung aktivieren
            </label>
          </div>

          <div className="form-checkbox">
            <Checkbox
              inputId="includeStorage"
              checked={includeStorage}
              onChange={(e) => setIncludeStorage(e.checked || false)}
            />
            <label htmlFor="includeStorage">
              Batteriespeicher einbeziehen
            </label>
          </div>

          {includeStorage && (
            <div className="form-field storage-capacity">
              <label htmlFor="storageCapacity">Speicherkapazität (kWh)</label>
              <InputNumber
                id="storageCapacity"
                value={storageCapacity}
                onValueChange={(e) => setStorageCapacity(e.value || 0)}
                min={5}
                max={30}
                step={5}
                showButtons
                className="w-full"
              />
            </div>
          )}
        </div>
      </Card>

      {/* Submit Button */}
      <div className="form-actions">
        <Button
          type="submit"
          label="Berechnung starten"
          icon="pi pi-calculator"
          loading={loading}
          className="p-button-lg"
        />
      </div>
    </form>
  );
};