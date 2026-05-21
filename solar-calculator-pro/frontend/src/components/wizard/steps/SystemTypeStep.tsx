/**
 * Step 1: System Type Selection (Anlagenmodus)
 * 
 * Allows user to select between:
 * - Photovoltaik (PV)
 * - Wärmepumpe (WP)
 * - Kombination PV+WP
 */

import React from 'react';
import { ProjectWizardData } from '../ProjectWizard';

interface SystemTypeStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const SystemTypeStep: React.FC<SystemTypeStepProps> = ({ data, onUpdate }) => {
  const systemTypes = [
    {
      id: 'pv',
      icon: '☀️',
      title: 'Photovoltaik',
      description: 'Solaranlage zur Stromerzeugung mit optionalem Batteriespeicher'
    },
    {
      id: 'wp',
      icon: '🔥',
      title: 'Wärmepumpe',
      description: 'Effiziente Heizungslösung für Ihr Gebäude'
    },
    {
      id: 'pv_wp',
      icon: '⚡',
      title: 'PV + Wärmepumpe',
      description: 'Kombinierte Lösung für maximale Energieeffizienz und Autarkie'
    }
  ];

  return (
    <div className="step-form">
      <h3 className="step-title">
        <i className="pi pi-cog"></i>
        Anlagenmodus wählen
      </h3>
      <p className="step-description">
        Wählen Sie den Systemtyp für Ihr Projekt. Diese Auswahl bestimmt, welche 
        Eingabefelder und Berechnungen im weiteren Verlauf relevant sind.
      </p>

      <div className="system-type-selection">
        {systemTypes.map((type) => (
          <div
            key={type.id}
            className={`system-type-card ${data.systemType === type.id ? 'selected' : ''}`}
            onClick={() => onUpdate({ systemType: type.id as 'pv' | 'wp' | 'pv_wp' })}
            role="button"
            tabIndex={0}
            onKeyPress={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                onUpdate({ systemType: type.id as 'pv' | 'wp' | 'pv_wp' });
              }
            }}
          >
            <div className="icon">{type.icon}</div>
            <h3>{type.title}</h3>
            <p>{type.description}</p>
          </div>
        ))}
      </div>

      <div className="info-box" style={{ marginTop: '1.5rem' }}>
        <i className="pi pi-info-circle"></i>
        <p>
          <strong>Tipp:</strong> Bei der Kombination PV+WP können Sie den selbst erzeugten 
          Solarstrom direkt für die Wärmepumpe nutzen und so Ihre Energiekosten maximieren.
        </p>
      </div>
    </div>
  );
};

export default SystemTypeStep;
