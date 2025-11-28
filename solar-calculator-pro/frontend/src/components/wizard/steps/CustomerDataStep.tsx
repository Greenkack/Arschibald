/**
 * Step 2: Customer Data (Kundendaten)
 * 
 * Features:
 * - Salutation, Title, First/Last Name
 * - Address with Auto-Parsing (single field → street, number, postal code, city)
 * - Email, Phone (fixed/mobile)
 * - Bundesland selection
 * - Notes field
 */

import React, { useState, useCallback, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { Divider } from 'primereact/divider';
import { ProjectWizardData } from '../ProjectWizard';

interface CustomerDataStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

// German Bundesländer
const bundeslaender = [
  { label: 'Baden-Württemberg', value: 'BW' },
  { label: 'Bayern', value: 'BY' },
  { label: 'Berlin', value: 'BE' },
  { label: 'Brandenburg', value: 'BB' },
  { label: 'Bremen', value: 'HB' },
  { label: 'Hamburg', value: 'HH' },
  { label: 'Hessen', value: 'HE' },
  { label: 'Mecklenburg-Vorpommern', value: 'MV' },
  { label: 'Niedersachsen', value: 'NI' },
  { label: 'Nordrhein-Westfalen', value: 'NW' },
  { label: 'Rheinland-Pfalz', value: 'RP' },
  { label: 'Saarland', value: 'SL' },
  { label: 'Sachsen', value: 'SN' },
  { label: 'Sachsen-Anhalt', value: 'ST' },
  { label: 'Schleswig-Holstein', value: 'SH' },
  { label: 'Thüringen', value: 'TH' }
];

const salutations = [
  { label: 'Herr', value: 'Herr' },
  { label: 'Frau', value: 'Frau' },
  { label: 'Divers', value: 'Divers' },
  { label: 'Firma', value: 'Firma' }
];

const titles = [
  { label: 'Kein Titel', value: '' },
  { label: 'Dr.', value: 'Dr.' },
  { label: 'Prof.', value: 'Prof.' },
  { label: 'Prof. Dr.', value: 'Prof. Dr.' },
  { label: 'Ing.', value: 'Ing.' },
  { label: 'Dipl.-Ing.', value: 'Dipl.-Ing.' }
];

// PLZ to Bundesland mapping (simplified - first 2 digits)
const plzToBundesland: { [key: string]: string } = {
  '01': 'SN', '02': 'SN', '03': 'BB', '04': 'SN', '06': 'ST', '07': 'TH', '08': 'SN', '09': 'SN',
  '10': 'BE', '12': 'BE', '13': 'BE', '14': 'BB', '15': 'BB', '16': 'BB', '17': 'MV', '18': 'MV', '19': 'MV',
  '20': 'HH', '21': 'NI', '22': 'HH', '23': 'SH', '24': 'SH', '25': 'SH', '26': 'NI', '27': 'NI', '28': 'HB', '29': 'NI',
  '30': 'NI', '31': 'NI', '32': 'NW', '33': 'NW', '34': 'HE', '35': 'HE', '36': 'HE', '37': 'NI', '38': 'NI', '39': 'ST',
  '40': 'NW', '41': 'NW', '42': 'NW', '44': 'NW', '45': 'NW', '46': 'NW', '47': 'NW', '48': 'NW', '49': 'NI',
  '50': 'NW', '51': 'NW', '52': 'NW', '53': 'NW', '54': 'RP', '55': 'RP', '56': 'RP', '57': 'NW', '58': 'NW', '59': 'NW',
  '60': 'HE', '61': 'HE', '63': 'HE', '64': 'HE', '65': 'HE', '66': 'SL', '67': 'RP', '68': 'BW', '69': 'BW',
  '70': 'BW', '71': 'BW', '72': 'BW', '73': 'BW', '74': 'BW', '75': 'BW', '76': 'BW', '77': 'BW', '78': 'BW', '79': 'BW',
  '80': 'BY', '81': 'BY', '82': 'BY', '83': 'BY', '84': 'BY', '85': 'BY', '86': 'BY', '87': 'BY', '88': 'BW', '89': 'BW',
  '90': 'BY', '91': 'BY', '92': 'BY', '93': 'BY', '94': 'BY', '95': 'BY', '96': 'BY', '97': 'BY', '98': 'TH', '99': 'TH'
};

const CustomerDataStep: React.FC<CustomerDataStepProps> = ({ data, onUpdate }) => {
  const [useAutoParse, setUseAutoParse] = useState(true);

  // Auto-parse address function
  const parseAddress = useCallback((fullAddress: string) => {
    if (!fullAddress.trim()) return;

    // Pattern: "Straße Hausnummer, PLZ Ort" or "Straße Hausnummer PLZ Ort"
    // Examples: "Musterstraße 123, 12345 Berlin" or "Musterstraße 123 12345 Berlin"
    
    const patterns = [
      // Pattern 1: Street Number, PLZ City
      /^(.+?)\s+(\d+[a-zA-Z]?)\s*,\s*(\d{5})\s+(.+)$/,
      // Pattern 2: Street Number PLZ City (no comma)
      /^(.+?)\s+(\d+[a-zA-Z]?)\s+(\d{5})\s+(.+)$/,
      // Pattern 3: Street, PLZ City (no house number)
      /^(.+?)\s*,\s*(\d{5})\s+(.+)$/
    ];

    for (const pattern of patterns) {
      const match = fullAddress.match(pattern);
      if (match) {
        if (match.length === 5) {
          // Pattern 1 or 2: Street, Number, PLZ, City
          const [, street, houseNumber, postalCode, city] = match;
          const bundesland = plzToBundesland[postalCode.substring(0, 2)] || '';
          
          onUpdate({
            street: street.trim(),
            houseNumber: houseNumber.trim(),
            postalCode: postalCode.trim(),
            city: city.trim(),
            bundesland
          });
          return;
        } else if (match.length === 4) {
          // Pattern 3: Street, PLZ, City (no house number)
          const [, street, postalCode, city] = match;
          const bundesland = plzToBundesland[postalCode.substring(0, 2)] || '';
          
          onUpdate({
            street: street.trim(),
            houseNumber: '',
            postalCode: postalCode.trim(),
            city: city.trim(),
            bundesland
          });
          return;
        }
      }
    }
  }, [onUpdate]);

  // Auto-detect Bundesland from PLZ
  useEffect(() => {
    if (data.postalCode && data.postalCode.length >= 2) {
      const prefix = data.postalCode.substring(0, 2);
      const detectedBundesland = plzToBundesland[prefix];
      if (detectedBundesland && detectedBundesland !== data.bundesland) {
        onUpdate({ bundesland: detectedBundesland });
      }
    }
  }, [data.postalCode, data.bundesland, onUpdate]);

  return (
    <div className="step-form">
      <h3 className="step-title">
        <i className="pi pi-user"></i>
        Kundendaten eingeben
      </h3>
      <p className="step-description">
        Erfassen Sie die Kontaktdaten des Kunden. Diese werden im CRM gespeichert 
        und stehen als Platzhalter für Angebote zur Verfügung.
      </p>

      {/* Name Section */}
      <div className="section-title">
        <i className="pi pi-id-card"></i>
        Persönliche Daten
      </div>
      
      <div className="form-row form-row-4">
        <div className="form-group">
          <label>Anrede</label>
          <Dropdown
            value={data.salutation}
            options={salutations}
            onChange={(e) => onUpdate({ salutation: e.value })}
            placeholder="Anrede wählen"
          />
        </div>
        
        <div className="form-group">
          <label>Titel</label>
          <Dropdown
            value={data.title}
            options={titles}
            onChange={(e) => onUpdate({ title: e.value })}
            placeholder="Titel wählen"
          />
        </div>
        
        <div className="form-group">
          <label>Vorname <span className="required">*</span></label>
          <InputText
            value={data.firstName}
            onChange={(e) => onUpdate({ firstName: e.target.value })}
            placeholder="Vorname"
          />
        </div>
        
        <div className="form-group">
          <label>Nachname <span className="required">*</span></label>
          <InputText
            value={data.lastName}
            onChange={(e) => onUpdate({ lastName: e.target.value })}
            placeholder="Nachname"
          />
        </div>
      </div>

      <Divider />

      {/* Address Section */}
      <div className="section-title">
        <i className="pi pi-map-marker"></i>
        Adresse
      </div>

      {useAutoParse && (
        <div className="address-auto-parse">
          <div className="form-group">
            <label>Vollständige Adresse (Auto-Parsing)</label>
            <InputText
              value={data.fullAddress}
              onChange={(e) => {
                onUpdate({ fullAddress: e.target.value });
              }}
              onBlur={(e) => parseAddress(e.target.value)}
              placeholder="z.B. Musterstraße 123, 12345 Berlin"
              style={{ width: '100%' }}
            />
            <div className="hint">
              <i className="pi pi-info-circle"></i>
              Geben Sie die vollständige Adresse ein - sie wird automatisch in Einzelfelder zerlegt
            </div>
          </div>
          <Button
            label="Manuell eingeben"
            icon="pi pi-pencil"
            className="p-button-text p-button-sm"
            onClick={() => setUseAutoParse(false)}
            style={{ marginTop: '0.5rem' }}
          />
        </div>
      )}

      <div className="form-row form-row-3">
        <div className="form-group" style={{ gridColumn: 'span 2' }}>
          <label>Straße <span className="required">*</span></label>
          <InputText
            value={data.street}
            onChange={(e) => onUpdate({ street: e.target.value })}
            placeholder="Straße"
            disabled={useAutoParse && !data.street}
          />
        </div>
        
        <div className="form-group">
          <label>Hausnummer</label>
          <InputText
            value={data.houseNumber}
            onChange={(e) => onUpdate({ houseNumber: e.target.value })}
            placeholder="Nr."
            disabled={useAutoParse && !data.houseNumber}
          />
        </div>
      </div>

      <div className="form-row form-row-3">
        <div className="form-group">
          <label>PLZ <span className="required">*</span></label>
          <InputText
            value={data.postalCode}
            onChange={(e) => onUpdate({ postalCode: e.target.value })}
            placeholder="PLZ"
            maxLength={5}
            disabled={useAutoParse && !data.postalCode}
          />
        </div>
        
        <div className="form-group">
          <label>Ort <span className="required">*</span></label>
          <InputText
            value={data.city}
            onChange={(e) => onUpdate({ city: e.target.value })}
            placeholder="Ort"
            disabled={useAutoParse && !data.city}
          />
        </div>
        
        <div className="form-group">
          <label>Bundesland</label>
          <Dropdown
            value={data.bundesland}
            options={bundeslaender}
            onChange={(e) => onUpdate({ bundesland: e.value })}
            placeholder="Bundesland"
          />
          <span className="field-hint">Wird automatisch aus PLZ ermittelt</span>
        </div>
      </div>

      <Divider />

      {/* Contact Section */}
      <div className="section-title">
        <i className="pi pi-phone"></i>
        Kontaktdaten
      </div>

      <div className="form-row form-row-3">
        <div className="form-group">
          <label>E-Mail</label>
          <InputText
            value={data.email}
            onChange={(e) => onUpdate({ email: e.target.value })}
            placeholder="email@beispiel.de"
            type="email"
          />
        </div>
        
        <div className="form-group">
          <label>Telefon (Festnetz)</label>
          <InputText
            value={data.phoneFixed}
            onChange={(e) => onUpdate({ phoneFixed: e.target.value })}
            placeholder="030 12345678"
          />
        </div>
        
        <div className="form-group">
          <label>Telefon (Mobil)</label>
          <InputText
            value={data.phoneMobile}
            onChange={(e) => onUpdate({ phoneMobile: e.target.value })}
            placeholder="0170 12345678"
          />
        </div>
      </div>

      <Divider />

      {/* Notes Section */}
      <div className="section-title">
        <i className="pi pi-comment"></i>
        Anmerkungen
      </div>

      <div className="form-group">
        <label>Notizen</label>
        <InputTextarea
          value={data.notes}
          onChange={(e) => onUpdate({ notes: e.target.value })}
          placeholder="Zusätzliche Anmerkungen zum Kunden..."
          rows={3}
          autoResize
        />
      </div>
    </div>
  );
};

export default CustomerDataStep;
