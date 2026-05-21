/**
 * Step 6: Additional Options (Zusatzoptionen)
 * 
 * Features:
 * - Financing options (down payment, loan term, interest rate)
 * - Discounts (percentage and fixed)
 * - Surcharges (percentage and fixed)
 * - Maintenance contract
 * - Payment terms
 */

import React from 'react';
import { InputNumber } from 'primereact/inputnumber';
import { Checkbox } from 'primereact/checkbox';
import { Dropdown } from 'primereact/dropdown';
import { Divider } from 'primereact/divider';
import { ProjectWizardData } from '../ProjectWizard';

interface AdditionalOptionsStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const paymentTermsOptions = [
  { label: '50% Anzahlung, 50% bei Fertigstellung', value: '50_50' },
  { label: '30% Anzahlung, 70% bei Fertigstellung', value: '30_70' },
  { label: '100% bei Fertigstellung', value: '0_100' },
  { label: '30% Anzahlung, 30% bei Lieferung, 40% bei Fertigstellung', value: '30_30_40' },
  { label: 'Individuelle Vereinbarung', value: 'custom' }
];

const loanTermOptions = [
  { label: '5 Jahre', value: 5 },
  { label: '7 Jahre', value: 7 },
  { label: '10 Jahre', value: 10 },
  { label: '12 Jahre', value: 12 },
  { label: '15 Jahre', value: 15 },
  { label: '20 Jahre', value: 20 }
];

const AdditionalOptionsStep: React.FC<AdditionalOptionsStepProps> = ({ data, onUpdate }) => {
  return (
    <div className="step-form">
      <h3 className="step-title">
        <i className="pi pi-plus-circle"></i>
        Zusatzoptionen
      </h3>
      <p className="step-description">
        Konfigurieren Sie projektspezifische Optionen wie Finanzierung, Rabatte, 
        Zuschläge und Zahlungsmodalitäten.
      </p>

      {/* Financing Section */}
      <div className="section-title">
        <i className="pi pi-wallet"></i>
        Finanzierung
      </div>

      <div className="checkbox-group">
        <div className="checkbox-item">
          <Checkbox
            inputId="wantsFinancing"
            checked={data.wantsFinancing}
            onChange={(e) => onUpdate({ wantsFinancing: e.checked || false })}
          />
          <label htmlFor="wantsFinancing">
            <strong>Finanzierung gewünscht</strong>
            <br />
            <span className="field-hint">
              Ratenzahlung über einen Kredit
            </span>
          </label>
        </div>
      </div>

      {data.wantsFinancing && (
        <div className="conditional-fields">
          <div className="form-row form-row-3">
            <div className="form-group">
              <label>Anzahlung (€)</label>
              <InputNumber
                value={data.downPayment}
                onValueChange={(e) => onUpdate({ downPayment: e.value })}
                placeholder="z.B. 5000"
                min={0}
                mode="currency"
                currency="EUR"
                locale="de-DE"
              />
            </div>
            
            <div className="form-group">
              <label>Kreditlaufzeit <span className="required">*</span></label>
              <Dropdown
                value={data.loanTerm}
                options={loanTermOptions}
                onChange={(e) => onUpdate({ loanTerm: e.value })}
                placeholder="Laufzeit wählen"
              />
            </div>
            
            <div className="form-group">
              <label>Zinssatz (% p.a.) <span className="required">*</span></label>
              <InputNumber
                value={data.interestRate}
                onValueChange={(e) => onUpdate({ interestRate: e.value })}
                placeholder="z.B. 4,5"
                min={0}
                max={20}
                minFractionDigits={1}
                maxFractionDigits={2}
                suffix=" %"
              />
            </div>
          </div>

          <div className="info-box" style={{ marginTop: '1rem' }}>
            <i className="pi pi-info-circle"></i>
            <p>
              <strong>Hinweis:</strong> Die Finanzierungsdaten werden in die 
              Amortisationsberechnung einbezogen. Die monatliche Rate wird im 
              Angebot ausgewiesen.
            </p>
          </div>
        </div>
      )}

      <Divider />

      {/* Discounts Section */}
      <div className="section-title">
        <i className="pi pi-percentage"></i>
        Rabatte
      </div>

      <div className="form-row form-row-2">
        <div className="form-group">
          <label>Rabatt (Prozent)</label>
          <InputNumber
            value={data.discountPercent}
            onValueChange={(e) => onUpdate({ discountPercent: e.value })}
            placeholder="z.B. 5"
            min={0}
            max={100}
            suffix=" %"
          />
          <span className="field-hint">Prozentualer Nachlass auf den Gesamtpreis</span>
        </div>
        
        <div className="form-group">
          <label>Rabatt (Festbetrag)</label>
          <InputNumber
            value={data.discountFixed}
            onValueChange={(e) => onUpdate({ discountFixed: e.value })}
            placeholder="z.B. 500"
            min={0}
            mode="currency"
            currency="EUR"
            locale="de-DE"
          />
          <span className="field-hint">Fester Nachlass in Euro</span>
        </div>
      </div>

      <Divider />

      {/* Surcharges Section */}
      <div className="section-title">
        <i className="pi pi-plus"></i>
        Zuschläge
      </div>

      <div className="form-row form-row-2">
        <div className="form-group">
          <label>Zuschlag (Prozent)</label>
          <InputNumber
            value={data.surchargePercent}
            onValueChange={(e) => onUpdate({ surchargePercent: e.value })}
            placeholder="z.B. 10"
            min={0}
            max={100}
            suffix=" %"
          />
          <span className="field-hint">z.B. für erschwerte Montage</span>
        </div>
        
        <div className="form-group">
          <label>Zuschlag (Festbetrag)</label>
          <InputNumber
            value={data.surchargeFixed}
            onValueChange={(e) => onUpdate({ surchargeFixed: e.value })}
            placeholder="z.B. 1000"
            min={0}
            mode="currency"
            currency="EUR"
            locale="de-DE"
          />
          <span className="field-hint">z.B. für Gerüst bei hohen Gebäuden</span>
        </div>
      </div>

      <Divider />

      {/* Service Contract */}
      <div className="section-title">
        <i className="pi pi-wrench"></i>
        Service & Wartung
      </div>

      <div className="checkbox-group">
        <div className="checkbox-item">
          <Checkbox
            inputId="wantsMaintenanceContract"
            checked={data.wantsMaintenanceContract}
            onChange={(e) => onUpdate({ wantsMaintenanceContract: e.checked || false })}
          />
          <label htmlFor="wantsMaintenanceContract">
            <strong>Wartungsvertrag gewünscht</strong>
            <br />
            <span className="field-hint">
              Regelmäßige Wartung und Inspektion der Anlage
            </span>
          </label>
        </div>
      </div>

      {data.wantsMaintenanceContract && (
        <div className="info-box" style={{ marginTop: '1rem' }}>
          <i className="pi pi-info-circle"></i>
          <p>
            <strong>Wartungsvertrag beinhaltet:</strong>
            <br />
            • Jährliche Inspektion der Anlage
            <br />
            • Reinigung der Module (bei Bedarf)
            <br />
            • Überprüfung aller elektrischen Verbindungen
            <br />
            • Ertragsüberwachung und Reporting
            <br />
            • Prioritärer Service bei Störungen
          </p>
        </div>
      )}

      <Divider />

      {/* Payment Terms */}
      <div className="section-title">
        <i className="pi pi-credit-card"></i>
        Zahlungsmodalitäten
      </div>

      <div className="form-group">
        <label>Zahlungsbedingungen</label>
        <Dropdown
          value={data.paymentTerms}
          options={paymentTermsOptions}
          onChange={(e) => onUpdate({ paymentTerms: e.value })}
          placeholder="Zahlungsbedingungen wählen"
        />
      </div>

      {/* Summary */}
      <div className="info-box" style={{ marginTop: '1.5rem', background: 'var(--surface-ground)' }}>
        <i className="pi pi-calculator"></i>
        <div>
          <p style={{ margin: '0 0 0.5rem 0' }}><strong>Preismodifikationen:</strong></p>
          <ul style={{ margin: 0, paddingLeft: '1.5rem', fontSize: '0.9rem' }}>
            {data.discountPercent && data.discountPercent > 0 && (
              <li>Rabatt: -{data.discountPercent}%</li>
            )}
            {data.discountFixed && data.discountFixed > 0 && (
              <li>Rabatt: -{data.discountFixed.toLocaleString('de-DE')} €</li>
            )}
            {data.surchargePercent && data.surchargePercent > 0 && (
              <li>Zuschlag: +{data.surchargePercent}%</li>
            )}
            {data.surchargeFixed && data.surchargeFixed > 0 && (
              <li>Zuschlag: +{data.surchargeFixed.toLocaleString('de-DE')} €</li>
            )}
            {data.wantsFinancing && (
              <li>Finanzierung: {data.loanTerm} Jahre @ {data.interestRate}%</li>
            )}
            {data.wantsMaintenanceContract && (
              <li>Wartungsvertrag: Ja</li>
            )}
            {!data.discountPercent && !data.discountFixed && !data.surchargePercent && 
             !data.surchargeFixed && !data.wantsFinancing && !data.wantsMaintenanceContract && (
              <li>Keine Modifikationen</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AdditionalOptionsStep;
