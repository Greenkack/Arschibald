/**
 * Step 5: Customer Needs (Kundenbedürfnisse)
 * 
 * Features:
 * - Wallbox for E-vehicles
 * - Priority on short amortization time
 * - Battery storage preference
 * - Additional wishes/notes
 */

import React from 'react';
import { Checkbox } from 'primereact/checkbox';
import { InputTextarea } from 'primereact/inputtextarea';
import { Divider } from 'primereact/divider';
import { ProjectWizardData } from '../ProjectWizard';

interface CustomerNeedsStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const CustomerNeedsStep: React.FC<CustomerNeedsStepProps> = ({ data, onUpdate }) => {
  const showPVOptions = data.systemType === 'pv' || data.systemType === 'pv_wp';

  return (
    <div className="step-form">
      <h3 className="step-title">
        <i className="pi pi-heart"></i>
        Kundenbedürfnisse
      </h3>
      <p className="step-description">
        Erfassen Sie besondere Wünsche und Präferenzen des Kunden. Diese Informationen 
        helfen bei der optimalen Planung und Auslegung des Systems.
      </p>

      {/* E-Mobility Section */}
      {showPVOptions && (
        <>
          <div className="section-title">
            <i className="pi pi-car"></i>
            E-Mobilität
          </div>

          <div className="checkbox-group">
            <div className="checkbox-item">
              <Checkbox
                inputId="wantsWallbox"
                checked={data.wantsWallbox}
                onChange={(e) => onUpdate({ wantsWallbox: e.checked || false })}
              />
              <label htmlFor="wantsWallbox">
                <strong>Wallbox für E-Fahrzeug gewünscht</strong>
                <br />
                <span className="field-hint">
                  Ladestation für Elektrofahrzeuge (11 kW oder 22 kW)
                </span>
              </label>
            </div>
          </div>

          {data.wantsWallbox && (
            <div className="info-box" style={{ marginTop: '1rem' }}>
              <i className="pi pi-info-circle"></i>
              <p>
                <strong>Tipp:</strong> Mit einer Wallbox können Sie Ihr E-Auto mit selbst 
                erzeugtem Solarstrom laden. Bei einem durchschnittlichen E-Auto-Verbrauch 
                von ca. 15-20 kWh/100km und 15.000 km/Jahr benötigen Sie zusätzlich 
                ca. 2.500-3.000 kWh Strom pro Jahr.
              </p>
            </div>
          )}

          <Divider />
        </>
      )}

      {/* Storage Section */}
      {showPVOptions && (
        <>
          <div className="section-title">
            <i className="pi pi-database"></i>
            Energiespeicher
          </div>

          <div className="checkbox-group">
            <div className="checkbox-item">
              <Checkbox
                inputId="wantsBatteryStorage"
                checked={data.wantsBatteryStorage}
                onChange={(e) => onUpdate({ wantsBatteryStorage: e.checked || false })}
              />
              <label htmlFor="wantsBatteryStorage">
                <strong>Batteriespeicher gewünscht</strong>
                <br />
                <span className="field-hint">
                  Speichert überschüssigen Solarstrom für die Nutzung am Abend/Nacht
                </span>
              </label>
            </div>
          </div>

          {data.wantsBatteryStorage && (
            <div className="info-box" style={{ marginTop: '1rem' }}>
              <i className="pi pi-info-circle"></i>
              <p>
                <strong>Vorteile eines Batteriespeichers:</strong>
                <br />
                • Erhöhung des Eigenverbrauchs von ca. 30% auf bis zu 70-80%
                <br />
                • Unabhängigkeit vom Stromnetz (höhere Autarkie)
                <br />
                • Nutzung des günstigen Solarstroms auch abends und nachts
                <br />
                • Optional: Notstromfunktion bei Stromausfall
              </p>
            </div>
          )}

          <Divider />
        </>
      )}

      {/* Economic Priorities */}
      <div className="section-title">
        <i className="pi pi-chart-line"></i>
        Wirtschaftliche Prioritäten
      </div>

      <div className="checkbox-group">
        <div className="checkbox-item">
          <Checkbox
            inputId="prioritizeAmortization"
            checked={data.prioritizeAmortization}
            onChange={(e) => onUpdate({ prioritizeAmortization: e.checked || false })}
          />
          <label htmlFor="prioritizeAmortization">
            <strong>Kurze Amortisationszeit priorisieren</strong>
            <br />
            <span className="field-hint">
              Fokus auf schnelle Refinanzierung der Investition
            </span>
          </label>
        </div>
      </div>

      {data.prioritizeAmortization && (
        <div className="info-box" style={{ marginTop: '1rem' }}>
          <i className="pi pi-info-circle"></i>
          <p>
            <strong>Hinweis:</strong> Bei Fokus auf kurze Amortisation empfehlen wir:
            <br />
            • Optimale Anlagengröße für hohen Eigenverbrauch
            <br />
            • Ggf. kleinerer oder kein Speicher (längere Amortisation)
            <br />
            • Nutzung aller verfügbaren Fördermittel
          </p>
        </div>
      )}

      <Divider />

      {/* Additional Wishes */}
      <div className="section-title">
        <i className="pi pi-comment"></i>
        Weitere Wünsche
      </div>

      <div className="form-group">
        <label>Zusätzliche Wünsche und Anmerkungen</label>
        <InputTextarea
          value={data.additionalWishes}
          onChange={(e) => onUpdate({ additionalWishes: e.target.value })}
          placeholder="z.B. besondere Anforderungen, Zeitrahmen, Budget-Vorstellungen, Ästhetik-Wünsche (schwarze Module), etc."
          rows={4}
          autoResize
        />
      </div>

      {/* Summary */}
      <div className="info-box" style={{ marginTop: '1.5rem', background: 'var(--surface-ground)' }}>
        <i className="pi pi-list"></i>
        <div>
          <p style={{ margin: '0 0 0.5rem 0' }}><strong>Zusammenfassung der Kundenwünsche:</strong></p>
          <ul style={{ margin: 0, paddingLeft: '1.5rem', fontSize: '0.9rem' }}>
            {data.wantsWallbox && <li>✓ Wallbox für E-Fahrzeug</li>}
            {data.wantsBatteryStorage && <li>✓ Batteriespeicher</li>}
            {data.prioritizeAmortization && <li>✓ Kurze Amortisationszeit priorisiert</li>}
            {!data.wantsWallbox && !data.wantsBatteryStorage && !data.prioritizeAmortization && (
              <li>Keine besonderen Präferenzen angegeben</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CustomerNeedsStep;
