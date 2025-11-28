/**
 * Step 3: Building Data (Gebäudedaten)
 * 
 * Features:
 * - Building year (for insulation standard estimation)
 * - Roof type and material
 * - Roof inclination and orientation
 * - Available roof/installation area
 * - Building height (for scaffolding costs if >7m)
 * - Building type
 */

import React from 'react';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { Slider } from 'primereact/slider';
import { Divider } from 'primereact/divider';
import { ProjectWizardData } from '../ProjectWizard';

interface BuildingDataStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const roofTypes = [
  { label: 'Satteldach', value: 'satteldach' },
  { label: 'Pultdach', value: 'pultdach' },
  { label: 'Flachdach', value: 'flachdach' },
  { label: 'Walmdach', value: 'walmdach' },
  { label: 'Krüppelwalmdach', value: 'krueppelwalmdach' },
  { label: 'Zeltdach', value: 'zeltdach' },
  { label: 'Mansarddach', value: 'mansarddach' },
  { label: 'Schleppdach', value: 'schleppdach' }
];

const roofMaterials = [
  { label: 'Ziegel (Ton)', value: 'ziegel' },
  { label: 'Betondachstein', value: 'beton' },
  { label: 'Schiefer', value: 'schiefer' },
  { label: 'Metall/Blech', value: 'metall' },
  { label: 'Bitumen/Teerpappe', value: 'bitumen' },
  { label: 'Trapezblech', value: 'trapezblech' },
  { label: 'Wellblech', value: 'wellblech' },
  { label: 'Faserzement', value: 'faserzement' },
  { label: 'Reet/Stroh', value: 'reet' },
  { label: 'Gründach', value: 'gruendach' }
];

const roofOrientations = [
  { label: 'Süd (optimal)', value: 'süd' },
  { label: 'Süd-Ost', value: 'süd-ost' },
  { label: 'Süd-West', value: 'süd-west' },
  { label: 'Ost', value: 'ost' },
  { label: 'West', value: 'west' },
  { label: 'Nord-Ost', value: 'nord-ost' },
  { label: 'Nord-West', value: 'nord-west' },
  { label: 'Nord', value: 'nord' },
  { label: 'Ost-West (Flachdach)', value: 'ost-west' }
];

const buildingTypes = [
  { label: 'Einfamilienhaus', value: 'einfamilienhaus' },
  { label: 'Zweifamilienhaus', value: 'zweifamilienhaus' },
  { label: 'Mehrfamilienhaus', value: 'mehrfamilienhaus' },
  { label: 'Reihenhaus', value: 'reihenhaus' },
  { label: 'Doppelhaushälfte', value: 'doppelhaushaelfte' },
  { label: 'Bungalow', value: 'bungalow' },
  { label: 'Gewerbegebäude', value: 'gewerbe' },
  { label: 'Landwirtschaftliches Gebäude', value: 'landwirtschaft' },
  { label: 'Carport/Garage', value: 'carport' }
];

const BuildingDataStep: React.FC<BuildingDataStepProps> = ({ data, onUpdate }) => {
  // Calculate insulation standard based on building year
  const getInsulationStandard = (year: number | null): string => {
    if (!year) return 'Unbekannt';
    if (year >= 2016) return 'Sehr gut (EnEV 2016+)';
    if (year >= 2009) return 'Gut (EnEV 2009)';
    if (year >= 2002) return 'Mittel (EnEV 2002)';
    if (year >= 1995) return 'Mäßig (WSchV 1995)';
    if (year >= 1984) return 'Gering (WSchV 1984)';
    if (year >= 1977) return 'Schlecht (WSchV 1977)';
    return 'Sehr schlecht (vor 1977)';
  };

  return (
    <div className="step-form">
      <h3 className="step-title">
        <i className="pi pi-home"></i>
        Gebäudedaten erfassen
      </h3>
      <p className="step-description">
        Erfassen Sie die Schlüsseldaten zum Gebäude. Diese sind wichtig für die 
        Heizlastberechnung (Wärmepumpe) und die PV-Installation.
      </p>

      {/* Building Type Section */}
      <div className="section-title">
        <i className="pi pi-building"></i>
        Gebäudeart
      </div>

      <div className="form-row form-row-2">
        <div className="form-group">
          <label>Gebäudetyp</label>
          <Dropdown
            value={data.buildingType}
            options={buildingTypes}
            onChange={(e) => onUpdate({ buildingType: e.value })}
            placeholder="Gebäudetyp wählen"
          />
        </div>
        
        <div className="form-group">
          <label>Baujahr</label>
          <InputNumber
            value={data.buildingYear}
            onValueChange={(e) => onUpdate({ buildingYear: e.value })}
            placeholder="z.B. 1990"
            min={1800}
            max={new Date().getFullYear()}
            useGrouping={false}
          />
          <span className="field-hint">
            Dämmstandard: {getInsulationStandard(data.buildingYear)}
          </span>
        </div>
      </div>

      <div className="form-group">
        <label>Gebäudehöhe (m)</label>
        <InputNumber
          value={data.buildingHeight}
          onValueChange={(e) => onUpdate({ buildingHeight: e.value })}
          placeholder="z.B. 8"
          min={2}
          max={50}
          minFractionDigits={1}
          maxFractionDigits={1}
          suffix=" m"
        />
        {data.buildingHeight && data.buildingHeight > 7 && (
          <div className="info-box" style={{ marginTop: '0.5rem' }}>
            <i className="pi pi-exclamation-triangle" style={{ color: 'var(--orange-500)' }}></i>
            <p>
              <strong>Hinweis:</strong> Bei einer Gebäudehöhe über 7 m können zusätzliche 
              Gerüstkosten anfallen.
            </p>
          </div>
        )}
      </div>

      <Divider />

      {/* Roof Section */}
      <div className="section-title">
        <i className="pi pi-th-large"></i>
        Dachdaten
      </div>

      <div className="form-row form-row-2">
        <div className="form-group">
          <label>Dachtyp <span className="required">*</span></label>
          <Dropdown
            value={data.roofType}
            options={roofTypes}
            onChange={(e) => onUpdate({ roofType: e.value })}
            placeholder="Dachtyp wählen"
          />
        </div>
        
        <div className="form-group">
          <label>Dachmaterial</label>
          <Dropdown
            value={data.roofMaterial}
            options={roofMaterials}
            onChange={(e) => onUpdate({ roofMaterial: e.value })}
            placeholder="Material wählen"
          />
        </div>
      </div>

      <div className="form-row form-row-2">
        <div className="form-group">
          <label>Dachneigung: {data.roofInclination}°</label>
          <Slider
            value={data.roofInclination}
            onChange={(e) => onUpdate({ roofInclination: e.value as number })}
            min={0}
            max={60}
            step={5}
          />
          <div className="field-hint" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>0° (Flach)</span>
            <span>30° (Optimal)</span>
            <span>60° (Steil)</span>
          </div>
        </div>
        
        <div className="form-group">
          <label>Dachausrichtung <span className="required">*</span></label>
          <Dropdown
            value={data.roofOrientation}
            options={roofOrientations}
            onChange={(e) => onUpdate({ roofOrientation: e.value })}
            placeholder="Ausrichtung wählen"
          />
          {data.roofOrientation === 'nord' && (
            <span className="field-hint" style={{ color: 'var(--orange-500)' }}>
              ⚠️ Nordausrichtung ist für PV nicht optimal
            </span>
          )}
        </div>
      </div>

      <div className="form-group">
        <label>Verfügbare Dachfläche (m²) <span className="required">*</span></label>
        <InputNumber
          value={data.roofArea}
          onValueChange={(e) => onUpdate({ roofArea: e.value })}
          placeholder="z.B. 60"
          min={1}
          max={10000}
          suffix=" m²"
        />
        <span className="field-hint">
          Nutzbare Fläche für die PV-Installation (abzüglich Dachfenster, Schornstein, etc.)
        </span>
      </div>

      {/* Info Box */}
      <div className="info-box" style={{ marginTop: '1.5rem' }}>
        <i className="pi pi-info-circle"></i>
        <p>
          <strong>Tipp:</strong> Die optimale Dachneigung für PV-Anlagen in Deutschland liegt 
          bei ca. 30-35° mit Südausrichtung. Bei Flachdächern kann eine Aufständerung 
          (Ost-West oder Süd) die Erträge optimieren.
        </p>
      </div>
    </div>
  );
};

export default BuildingDataStep;
