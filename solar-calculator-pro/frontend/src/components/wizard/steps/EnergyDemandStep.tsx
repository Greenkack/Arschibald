/**
 * Step 4: Energy Demand Analysis (Energiebedarfsanalyse)
 * 
 * Features:
 * - Annual electricity consumption (kWh)
 * - Annual heating consumption (kWh) - for heat pump
 * - New building vs. existing building
 * - Partial vs. full feed-in
 * - Private vs. commercial customer
 */

import React from 'react';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { SelectButton } from 'primereact/selectbutton';
import { Divider } from 'primereact/divider';
import { ProjectWizardData } from '../ProjectWizard';

interface EnergyDemandStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const feedInTypes = [
  { label: 'Teileinspeisung', value: 'partial' },
  { label: 'Volleinspeisung', value: 'full' }
];

const customerTypes = [
  { label: 'Privat', value: 'private' },
  { label: 'Gewerblich', value: 'commercial' }
];

const buildingStatus = [
  { label: 'Bestandsgebäude', value: false },
  { label: 'Neubau', value: true }
];

// Typical consumption values for reference
const typicalConsumption = {
  '1_person': 1500,
  '2_persons': 2500,
  '3_persons': 3500,
  '4_persons': 4500,
  '5_plus_persons': 5500,
  'with_heatpump': 6000,
  'with_ev': 3000
};

const EnergyDemandStep: React.FC<EnergyDemandStepProps> = ({ data, onUpdate }) => {
  const showElectricity = data.systemType === 'pv' || data.systemType === 'pv_wp';
  const showHeating = data.systemType === 'wp' || data.systemType === 'pv_wp';

  // Estimate heating consumption from building data
  const estimateHeatingConsumption = (): number | null => {
    if (!data.buildingYear || !data.roofArea) return null;
    
    // Rough estimation based on building year and area
    // Assuming roof area ≈ 50% of living area for typical houses
    const estimatedLivingArea = data.roofArea * 2;
    
    let kwhPerM2: number;
    if (data.buildingYear >= 2016) kwhPerM2 = 50;
    else if (data.buildingYear >= 2009) kwhPerM2 = 70;
    else if (data.buildingYear >= 2002) kwhPerM2 = 100;
    else if (data.buildingYear >= 1995) kwhPerM2 = 130;
    else if (data.buildingYear >= 1984) kwhPerM2 = 160;
    else if (data.buildingYear >= 1977) kwhPerM2 = 200;
    else kwhPerM2 = 250;
    
    return Math.round(estimatedLivingArea * kwhPerM2);
  };

  const estimatedHeating = estimateHeatingConsumption();

  return (
    <div className="step-form">
      <h3 className="step-title">
        <i className="pi pi-bolt"></i>
        Energiebedarfsanalyse
      </h3>
      <p className="step-description">
        Ermitteln Sie den aktuellen Energieverbrauch des Kunden. Diese Werte sind 
        die Grundlage für die Anlagenauslegung und Wirtschaftlichkeitsberechnung.
      </p>

      {/* Customer Type */}
      <div className="section-title">
        <i className="pi pi-user"></i>
        Kundentyp
      </div>

      <div className="form-row form-row-2">
        <div className="form-group">
          <label>Kundenart</label>
          <SelectButton
            value={data.customerType}
            options={customerTypes}
            onChange={(e) => onUpdate({ customerType: e.value })}
          />
          <span className="field-hint">
            {data.customerType === 'commercial' 
              ? 'Gewerblich: MwSt. wird ausgewiesen' 
              : 'Privat: Bruttopreise'}
          </span>
        </div>
        
        <div className="form-group">
          <label>Gebäudestatus</label>
          <SelectButton
            value={data.isNewBuilding}
            options={buildingStatus}
            onChange={(e) => onUpdate({ isNewBuilding: e.value })}
          />
        </div>
      </div>

      <Divider />

      {/* Electricity Consumption */}
      {showElectricity && (
        <>
          <div className="section-title">
            <i className="pi pi-bolt"></i>
            Stromverbrauch (PV)
          </div>

          <div className="form-group">
            <label>
              Jährlicher Stromverbrauch (kWh/Jahr) 
              <span className="required">*</span>
            </label>
            <InputNumber
              value={data.annualElectricityConsumption}
              onValueChange={(e) => onUpdate({ annualElectricityConsumption: e.value })}
              placeholder="z.B. 4500"
              min={0}
              max={1000000}
              suffix=" kWh/Jahr"
            />
          </div>

          {/* Reference Values */}
          <div className="info-box" style={{ marginBottom: '1rem' }}>
            <i className="pi pi-info-circle"></i>
            <div>
              <p style={{ margin: '0 0 0.5rem 0' }}><strong>Richtwerte Stromverbrauch:</strong></p>
              <ul style={{ margin: 0, paddingLeft: '1.5rem', fontSize: '0.9rem' }}>
                <li>1 Person: ca. {typicalConsumption['1_person'].toLocaleString('de-DE')} kWh/Jahr</li>
                <li>2 Personen: ca. {typicalConsumption['2_persons'].toLocaleString('de-DE')} kWh/Jahr</li>
                <li>3 Personen: ca. {typicalConsumption['3_persons'].toLocaleString('de-DE')} kWh/Jahr</li>
                <li>4 Personen: ca. {typicalConsumption['4_persons'].toLocaleString('de-DE')} kWh/Jahr</li>
                <li>+ Wärmepumpe: ca. +{typicalConsumption['with_heatpump'].toLocaleString('de-DE')} kWh/Jahr</li>
                <li>+ E-Auto: ca. +{typicalConsumption['with_ev'].toLocaleString('de-DE')} kWh/Jahr</li>
              </ul>
            </div>
          </div>

          <div className="form-group">
            <label>Einspeiseart</label>
            <SelectButton
              value={data.feedInType}
              options={feedInTypes}
              onChange={(e) => onUpdate({ feedInType: e.value })}
            />
            <span className="field-hint">
              {data.feedInType === 'partial' 
                ? 'Teileinspeisung: Eigenverbrauch + Überschuss ins Netz' 
                : 'Volleinspeisung: Gesamte Produktion ins Netz (höhere Vergütung)'}
            </span>
          </div>

          <Divider />
        </>
      )}

      {/* Heating Consumption */}
      {showHeating && (
        <>
          <div className="section-title">
            <i className="pi pi-sun"></i>
            Heizenergieverbrauch (Wärmepumpe)
          </div>

          <div className="form-group">
            <label>
              Jährlicher Heizenergieverbrauch (kWh/Jahr) 
              <span className="required">*</span>
            </label>
            <InputNumber
              value={data.annualHeatingConsumption}
              onValueChange={(e) => onUpdate({ annualHeatingConsumption: e.value })}
              placeholder="z.B. 15000"
              min={0}
              max={500000}
              suffix=" kWh/Jahr"
            />
            {estimatedHeating && !data.annualHeatingConsumption && (
              <div style={{ marginTop: '0.5rem' }}>
                <span className="field-hint">
                  Geschätzter Verbrauch basierend auf Gebäudedaten: ca. {estimatedHeating.toLocaleString('de-DE')} kWh/Jahr
                </span>
                <button
                  type="button"
                  className="p-button p-button-text p-button-sm"
                  onClick={() => onUpdate({ annualHeatingConsumption: estimatedHeating })}
                  style={{ marginLeft: '0.5rem' }}
                >
                  Übernehmen
                </button>
              </div>
            )}
          </div>

          <div className="info-box">
            <i className="pi pi-info-circle"></i>
            <div>
              <p style={{ margin: '0 0 0.5rem 0' }}><strong>Umrechnung Brennstoffverbrauch:</strong></p>
              <ul style={{ margin: 0, paddingLeft: '1.5rem', fontSize: '0.9rem' }}>
                <li>1 Liter Heizöl ≈ 10 kWh</li>
                <li>1 m³ Erdgas ≈ 10 kWh</li>
                <li>1 kg Pellets ≈ 5 kWh</li>
                <li>Beispiel: 1.500 Liter Öl/Jahr = ca. 15.000 kWh/Jahr</li>
              </ul>
            </div>
          </div>
        </>
      )}

      {/* Combined System Info */}
      {data.systemType === 'pv_wp' && (
        <div className="info-box" style={{ marginTop: '1.5rem', background: 'var(--green-50)', borderColor: 'var(--green-200)' }}>
          <i className="pi pi-check-circle" style={{ color: 'var(--green-500)' }}></i>
          <p style={{ color: 'var(--green-900)' }}>
            <strong>Kombisystem PV+WP:</strong> Der Stromverbrauch der Wärmepumpe wird 
            bei der Autarkie-Berechnung berücksichtigt. So können Sie den selbst erzeugten 
            PV-Strom optimal für die Wärmepumpe nutzen.
          </p>
        </div>
      )}
    </div>
  );
};

export default EnergyDemandStep;
