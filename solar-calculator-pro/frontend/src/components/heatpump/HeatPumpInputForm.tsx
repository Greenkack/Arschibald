import React, { useState } from 'react';
import { InputText } from 'primereact/inputtext';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { Slider } from 'primereact/slider';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Divider } from 'primereact/divider';
import './HeatPumpInputForm.css';

interface BuildingData {
  // Building Information
  heatedArea: number;
  buildingType: string;
  buildingYear: string;
  insulationQuality: string;
  
  // Current Heating System
  currentHeatingSystem: string;
  hotWaterDemand: string;
  
  // Current Consumption
  oilConsumption: number;
  gasConsumption: number;
  woodConsumption: number;
  
  // System Efficiency
  systemEfficiency: number;
  heatingHours: number;
  
  // Heating Costs
  gasMonthlyC cost: number;
  oilPricePerTon: number;
  woodPricePerSter: number;
  
  // Advanced Parameters
  desiredTemperature: number;
  heatingDays: number;
  outsideTempDesign: number;
  heatingSystemTemp: string;
  
  // Location and Climate
  location: string;
  climateZone: string;
}

interface HeatPumpInputFormProps {
  onSubmit: (data: BuildingData) => void;
  initialData?: Partial<BuildingData>;
}

export const HeatPumpInputForm: React.FC<HeatPumpInputFormProps> = ({
  onSubmit,
  initialData = {}
}) => {
  const [formData, setFormData] = useState<BuildingData>({
    heatedArea: initialData.heatedArea || 150,
    buildingType: initialData.buildingType || 'Neubau Standard',
    buildingYear: initialData.buildingYear || 'Nach 2020',
    insulationQuality: initialData.insulationQuality || 'Gut',
    currentHeatingSystem: initialData.currentHeatingSystem || 'Gas-Brennwert',
    hotWaterDemand: initialData.hotWaterDemand || 'Mittel (3-4 Personen)',
    oilConsumption: initialData.oilConsumption || 0,
    gasConsumption: initialData.gasConsumption || 0,
    woodConsumption: initialData.woodConsumption || 0,
    systemEfficiency: initialData.systemEfficiency || 90,
    heatingHours: initialData.heatingHours || 1800,
    gasMonthlyC cost: initialData.gasMonthlyC cost || 0,
    oilPricePerTon: initialData.oilPricePerTon || 1071,
    woodPricePerSter: initialData.woodPricePerSter || 80,
    desiredTemperature: initialData.desiredTemperature || 21,
    heatingDays: initialData.heatingDays || 220,
    outsideTempDesign: initialData.outsideTempDesign || -12,
    heatingSystemTemp: initialData.heatingSystemTemp || 'Radiatoren (55°C)',
    location: initialData.location || '',
    climateZone: initialData.climateZone || 'Standard'
  });

  // Dropdown options
  const buildingTypes = [
    { label: 'Neubau KfW40', value: 'Neubau KfW40' },
    { label: 'Neubau KfW55', value: 'Neubau KfW55' },
    { label: 'Neubau Standard', value: 'Neubau Standard' },
    { label: 'Altbau saniert', value: 'Altbau saniert' },
    { label: 'Altbau teilsaniert', value: 'Altbau teilsaniert' },
    { label: 'Altbau unsaniert', value: 'Altbau unsaniert' }
  ];

  const buildingYears = [
    { label: 'Nach 2020', value: 'Nach 2020' },
    { label: '2010-2020', value: '2010-2020' },
    { label: '2000-2010', value: '2000-2010' },
    { label: '1990-2000', value: '1990-2000' },
    { label: '1980-1990', value: '1980-1990' },
    { label: '1970-1980', value: '1970-1980' },
    { label: 'Vor 1970', value: 'Vor 1970' }
  ];

  const insulationQualities = [
    { label: 'Sehr gut', value: 'Sehr gut' },
    { label: 'Gut', value: 'Gut' },
    { label: 'Mittel', value: 'Mittel' },
    { label: 'Schlecht', value: 'Schlecht' },
    { label: 'Sehr schlecht', value: 'Sehr schlecht' }
  ];

  const heatingSystems = [
    { label: 'Gas-Brennwert', value: 'Gas-Brennwert' },
    { label: 'Öl-Brennwert', value: 'Öl-Brennwert' },
    { label: 'Pellets', value: 'Pellets' },
    { label: 'Fernwärme', value: 'Fernwärme' },
    { label: 'Strom-Direktheizung', value: 'Strom-Direktheizung' },
    { label: 'Alte Gasheizung', value: 'Alte Gasheizung' },
    { label: 'Alte Ölheizung', value: 'Alte Ölheizung' }
  ];

  const hotWaterDemands = [
    { label: 'Niedrig (1-2 Personen)', value: 'Niedrig (1-2 Personen)' },
    { label: 'Mittel (3-4 Personen)', value: 'Mittel (3-4 Personen)' },
    { label: 'Hoch (5+ Personen)', value: 'Hoch (5+ Personen)' }
  ];

  const heatingSystemTemps = [
    { label: 'Fußbodenheizung (35°C)', value: 'Fußbodenheizung (35°C)' },
    { label: 'Wandheizung (40°C)', value: 'Wandheizung (40°C)' },
    { label: 'Radiatoren (55°C)', value: 'Radiatoren (55°C)' },
    { label: 'Alte Radiatoren (70°C)', value: 'Alte Radiatoren (70°C)' }
  ];

  const handleInputChange = (field: keyof BuildingData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  // Calculate total annual heating costs
  const gasAnnualCost = formData.gasMonthlyC cost * 12;
  const oilAnnualCost = (formData.oilConsumption / 1190) * formData.oilPricePerTon;
  const woodAnnualCost = formData.woodConsumption * formData.woodPricePerSter;
  const totalAnnualCost = gasAnnualCost + oilAnnualCost + woodAnnualCost;

  return (
    <form onSubmit={handleSubmit} className="heat-pump-input-form">
      <Card title="🏠 Gebäudedaten" className="form-section">
        <div className="p-fluid">
          <div className="p-grid">
            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="heatedArea">Beheizte Wohnfläche (m²)</label>
                <InputNumber
                  id="heatedArea"
                  value={formData.heatedArea}
                  onValueChange={(e) => handleInputChange('heatedArea', e.value)}
                  min={30}
                  max={1000}
                  step={10}
                  showButtons
                />
              </div>
            </div>

            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="buildingType">Gebäudetyp</label>
                <Dropdown
                  id="buildingType"
                  value={formData.buildingType}
                  options={buildingTypes}
                  onChange={(e) => handleInputChange('buildingType', e.value)}
                  placeholder="Wählen Sie einen Gebäudetyp"
                />
              </div>
            </div>

            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="buildingYear">Baujahr</label>
                <Dropdown
                  id="buildingYear"
                  value={formData.buildingYear}
                  options={buildingYears}
                  onChange={(e) => handleInputChange('buildingYear', e.value)}
                  placeholder="Wählen Sie das Baujahr"
                />
              </div>
            </div>

            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="insulationQuality">Dämmqualität</label>
                <Dropdown
                  id="insulationQuality"
                  value={formData.insulationQuality}
                  options={insulationQualities}
                  onChange={(e) => handleInputChange('insulationQuality', e.value)}
                  placeholder="Wählen Sie die Dämmqualität"
                />
              </div>
            </div>

            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="location">Standort (Stadt/PLZ)</label>
                <InputText
                  id="location"
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  placeholder="z.B. Berlin, 10115"
                />
              </div>
            </div>
          </div>
        </div>
      </Card>

      <Divider />

      <Card title="🔥 Aktuelles Heizsystem" className="form-section">
        <div className="p-fluid">
          <div className="p-grid">
            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="currentHeatingSystem">Aktuelles Heizsystem</label>
                <Dropdown
                  id="currentHeatingSystem"
                  value={formData.currentHeatingSystem}
                  options={heatingSystems}
                  onChange={(e) => handleInputChange('currentHeatingSystem', e.value)}
                  placeholder="Wählen Sie Ihr Heizsystem"
                />
              </div>
            </div>

            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="hotWaterDemand">Warmwasserbedarf</label>
                <Dropdown
                  id="hotWaterDemand"
                  value={formData.hotWaterDemand}
                  options={hotWaterDemands}
                  onChange={(e) => handleInputChange('hotWaterDemand', e.value)}
                  placeholder="Wählen Sie den Warmwasserbedarf"
                />
              </div>
            </div>

            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="heatingSystemTemp">Heizsystem-Temperatur</label>
                <Dropdown
                  id="heatingSystemTemp"
                  value={formData.heatingSystemTemp}
                  options={heatingSystemTemps}
                  onChange={(e) => handleInputChange('heatingSystemTemp', e.value)}
                  placeholder="Wählen Sie die Vorlauftemperatur"
                />
              </div>
            </div>
          </div>
        </div>
      </Card>

      <Divider />

      <Card title="📊 Aktueller Verbrauch (pro Jahr)" className="form-section">
        <div className="p-fluid">
          <div className="p-grid">
            <div className="p-col-12 p-md-4">
              <div className="p-field">
                <label htmlFor="oilConsumption">Heizöl (Liter/Jahr)</label>
                <InputNumber
                  id="oilConsumption"
                  value={formData.oilConsumption}
                  onValueChange={(e) => handleInputChange('oilConsumption', e.value)}
                  min={0}
                  step={50}
                  showButtons
                />
              </div>
            </div>

            <div className="p-col-12 p-md-4">
              <div className="p-field">
                <label htmlFor="gasConsumption">Erdgas (kWh/Jahr)</label>
                <InputNumber
                  id="gasConsumption"
                  value={formData.gasConsumption}
                  onValueChange={(e) => handleInputChange('gasConsumption', e.value)}
                  min={0}
                  step={100}
                  showButtons
                />
              </div>
            </div>

            <div className="p-col-12 p-md-4">
              <div className="p-field">
                <label htmlFor="woodConsumption">Holz (Ster/Jahr)</label>
                <InputNumber
                  id="woodConsumption"
                  value={formData.woodConsumption}
                  onValueChange={(e) => handleInputChange('woodConsumption', e.value)}
                  min={0}
                  step={0.5}
                  minFractionDigits={1}
                  maxFractionDigits={1}
                  showButtons
                />
              </div>
            </div>

            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="systemEfficiency">Wirkungsgrad aktuelles System (%)</label>
                <InputNumber
                  id="systemEfficiency"
                  value={formData.systemEfficiency}
                  onValueChange={(e) => handleInputChange('systemEfficiency', e.value)}
                  min={40}
                  max={105}
                  step={1}
                  suffix="%"
                  showButtons
                />
              </div>
            </div>

            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="heatingHours">Volllaststunden/Jahr (Schätzung)</label>
                <InputNumber
                  id="heatingHours"
                  value={formData.heatingHours}
                  onValueChange={(e) => handleInputChange('heatingHours', e.value)}
                  min={1200}
                  max={2600}
                  step={100}
                  showButtons
                />
              </div>
            </div>
          </div>
        </div>
      </Card>

      <Divider />

      <Card title="💰 Jährliche Heizkosten" className="form-section">
        <div className="p-fluid">
          <div className="p-grid">
            <div className="p-col-12 p-md-4">
              <div className="p-field">
                <label htmlFor="gasMonthlyC cost">Monatliche Gaskosten (€)</label>
                <InputNumber
                  id="gasMonthlyC cost"
                  value={formData.gasMonthlyC cost}
                  onValueChange={(e) => handleInputChange('gasMonthlyC cost', e.value)}
                  min={0}
                  step={10}
                  mode="currency"
                  currency="EUR"
                  locale="de-DE"
                  showButtons
                />
                {formData.gasMonthlyC cost > 0 && (
                  <small className="p-text-secondary">
                    Jährlich: {gasAnnualCost.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                  </small>
                )}
              </div>
            </div>

            <div className="p-col-12 p-md-4">
              <div className="p-field">
                <label htmlFor="oilPricePerTon">Preis pro Tonne Heizöl (€)</label>
                <InputNumber
                  id="oilPricePerTon"
                  value={formData.oilPricePerTon}
                  onValueChange={(e) => handleInputChange('oilPricePerTon', e.value)}
                  min={0}
                  step={50}
                  mode="currency"
                  currency="EUR"
                  locale="de-DE"
                  showButtons
                />
                {formData.oilConsumption > 0 && formData.oilPricePerTon > 0 && (
                  <small className="p-text-secondary">
                    Jährlich: {oilAnnualCost.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                  </small>
                )}
              </div>
            </div>

            <div className="p-col-12 p-md-4">
              <div className="p-field">
                <label htmlFor="woodPricePerSter">Preis pro Ster Holz (€)</label>
                <InputNumber
                  id="woodPricePerSter"
                  value={formData.woodPricePerSter}
                  onValueChange={(e) => handleInputChange('woodPricePerSter', e.value)}
                  min={0}
                  step={10}
                  mode="currency"
                  currency="EUR"
                  locale="de-DE"
                  showButtons
                />
                {formData.woodConsumption > 0 && formData.woodPricePerSter > 0 && (
                  <small className="p-text-secondary">
                    Jährlich: {woodAnnualCost.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                  </small>
                )}
              </div>
            </div>

            {totalAnnualCost > 0 && (
              <div className="p-col-12">
                <div className="total-cost-display">
                  <h3>💵 Gesamte jährliche Heizkosten</h3>
                  <div className="cost-value">
                    {totalAnnualCost.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                  </div>
                  <div className="cost-breakdown">
                    {gasAnnualCost > 0 && <span>Gas: {gasAnnualCost.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}</span>}
                    {oilAnnualCost > 0 && <span>Öl: {oilAnnualCost.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}</span>}
                    {woodAnnualCost > 0 && <span>Holz: {woodAnnualCost.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}</span>}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>

      <Divider />

      <Card title="⚙️ Erweiterte Parameter" className="form-section">
        <div className="p-fluid">
          <div className="p-grid">
            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="desiredTemperature">
                  Gewünschte Raumtemperatur: {formData.desiredTemperature}°C
                </label>
                <Slider
                  id="desiredTemperature"
                  value={formData.desiredTemperature}
                  onChange={(e) => handleInputChange('desiredTemperature', e.value)}
                  min={18}
                  max={24}
                  step={1}
                />
              </div>
            </div>

            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="heatingDays">
                  Heiztage pro Jahr: {formData.heatingDays}
                </label>
                <Slider
                  id="heatingDays"
                  value={formData.heatingDays}
                  onChange={(e) => handleInputChange('heatingDays', e.value)}
                  min={150}
                  max={300}
                  step={10}
                />
              </div>
            </div>

            <div className="p-col-12 p-md-6">
              <div className="p-field">
                <label htmlFor="outsideTempDesign">
                  Auslegungstemperatur außen: {formData.outsideTempDesign}°C
                </label>
                <Slider
                  id="outsideTempDesign"
                  value={formData.outsideTempDesign}
                  onChange={(e) => handleInputChange('outsideTempDesign', e.value)}
                  min={-20}
                  max={-5}
                  step={1}
                />
              </div>
            </div>
          </div>
        </div>
      </Card>

      <div className="form-actions">
        <Button
          type="submit"
          label="🔥 Heizlast berechnen"
          icon="pi pi-calculator"
          className="p-button-lg p-button-success"
        />
      </div>
    </form>
  );
};
