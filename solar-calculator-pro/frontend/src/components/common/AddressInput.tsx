/**
 * Address Input Component with Auto-Parsing
 * Intelligent address input that parses German addresses automatically
 */

import React, { useState, useEffect, useRef } from 'react';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { ProgressSpinner } from 'primereact/progressspinner';
import { useAddressParsing } from '../../hooks/useAddressParsing';
import { ParsedAddress } from '../../services/addressParsingService';
import './AddressInput.css';

export interface AddressInputProps {
  value?: Partial<ParsedAddress>;
  onChange?: (address: ParsedAddress) => void;
  onValidationChange?: (isValid: boolean, errors: string[]) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  showManualInput?: boolean;
  showValidation?: boolean;
  className?: string;
}

const AddressInput: React.FC<AddressInputProps> = ({
  value, onChange, onValidationChange,
  placeholder = 'z.B. Musterstraße 123, 12345 Berlin',
  disabled = false, required = false,
  showManualInput = true, showValidation = true, className = ''
}) => {
  const [fullAddress, setFullAddress] = useState('');
  const [useAutoParse, setUseAutoParse] = useState(true);
  const [showDetails, setShowDetails] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  
  const {
    parsedAddress, validationResult, isLoading, suggestions,
    parseAddress, validateAddress, clearAddress, formatAddress, isGermanAddress
  } = useAddressParsing({ autoParseOnChange: useAutoParse, validateOnChange: showValidation, debounceMs: 500 });

  useEffect(() => {
    if (value && (value.street || value.postalCode || value.city)) {
      const formatted = formatAddress();
      if (formatted && formatted !== fullAddress) {
        setFullAddress(formatted);
        setUseAutoParse(false);
        setShowDetails(true);
      }
    }
  }, [value]);

  const handleFullAddressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newAddress = e.target.value;
    setFullAddress(newAddress);
    if (useAutoParse && newAddress.trim()) parseAddress(newAddress);
  };

  useEffect(() => {
    if (parsedAddress.isValid && onChange) onChange(parsedAddress);
  }, [parsedAddress, onChange]);

  useEffect(() => {
    if (validationResult && onValidationChange) {
      onValidationChange(validationResult.isValid, validationResult.errors);
    }
  }, [validationResult, onValidationChange]);

  const handleManualChange = (field: keyof ParsedAddress, newValue: string) => {
    const updated = { ...parsedAddress, [field]: newValue };
    if (showValidation) validateAddress(updated);
    if (onChange) onChange(updated as ParsedAddress);
  };

  const toggleInputMode = () => {
    if (useAutoParse) { setUseAutoParse(false); setShowDetails(true); }
    else { setUseAutoParse(true); setShowDetails(false); if (fullAddress.trim()) parseAddress(fullAddress); }
  };

  const handleClear = () => {
    setFullAddress('');
    clearAddress();
    setShowDetails(false);
    inputRef.current?.focus();
  };

  return (
    <div className={`address-input ${className}`}>
      {useAutoParse && (
        <div className="auto-parse-section">
          <div className="input-with-actions">
            <span className="p-input-icon-right" style={{ flex: 1 }}>
              {isLoading && <ProgressSpinner style={{ width: '1rem', height: '1rem' }} />}
              <InputText
                ref={inputRef}
                value={fullAddress}
                onChange={handleFullAddressChange}
                placeholder={placeholder}
                disabled={disabled}
                className={`full-address-input ${validationResult && !validationResult.isValid ? 'p-invalid' : ''} ${parsedAddress.isValid ? 'p-valid' : ''}`}
                style={{ width: '100%' }}
              />
            </span>
            <div className="input-actions">
              {fullAddress && <Button icon="pi pi-times" className="p-button-text p-button-sm" onClick={handleClear} tooltip="Löschen" />}
              {showManualInput && <Button icon="pi pi-pencil" label="Manuell" className="p-button-text p-button-sm" onClick={toggleInputMode} />}
            </div>
          </div>
          <div className="parsing-hint">
            <i className="pi pi-info-circle"></i>
            <span>Vollständige Adresse eingeben - wird automatisch in Einzelfelder zerlegt</span>
          </div>
          {fullAddress && !isGermanAddress(fullAddress) && (
            <Message severity="warn" text="Diese Adresse scheint nicht aus Deutschland zu sein." />
          )}
        </div>
      )}

      {(!useAutoParse || showDetails) && (
        <Card className="manual-input-section">
          <div className="manual-input-header">
            <h4 style={{ margin: 0 }}>Adressdetails</h4>
            {!useAutoParse && <Button icon="pi pi-magic-wand" label="Auto-Parse" className="p-button-text p-button-sm" onClick={toggleInputMode} />}
          </div>
          <div className="manual-fields">
            <div className="field-row">
              <div className="field-group" style={{ flex: 2 }}>
                <label>Straße {required && <span style={{ color: 'var(--red-500)' }}>*</span>}</label>
                <InputText value={parsedAddress.street} onChange={(e) => handleManualChange('street', e.target.value)} placeholder="Straße" disabled={disabled} />
              </div>
              <div className="field-group" style={{ flex: 1 }}>
                <label>Nr.</label>
                <InputText value={parsedAddress.houseNumber} onChange={(e) => handleManualChange('houseNumber', e.target.value)} placeholder="123a" disabled={disabled} />
              </div>
            </div>
            <div className="field-row">
              <div className="field-group">
                <label>PLZ {required && <span style={{ color: 'var(--red-500)' }}>*</span>}</label>
                <InputText value={parsedAddress.postalCode} onChange={(e) => handleManualChange('postalCode', e.target.value)} placeholder="12345" disabled={disabled} maxLength={5} />
              </div>
              <div className="field-group" style={{ flex: 2 }}>
                <label>Ort {required && <span style={{ color: 'var(--red-500)' }}>*</span>}</label>
                <InputText value={parsedAddress.city} onChange={(e) => handleManualChange('city', e.target.value)} placeholder="Berlin" disabled={disabled} />
              </div>
              <div className="field-group">
                <label>Bundesland</label>
                <InputText value={parsedAddress.bundesland} disabled={true} placeholder="BE" style={{ backgroundColor: 'var(--surface-100)' }} />
              </div>
            </div>
          </div>
        </Card>
      )}

      {showValidation && validationResult && !validationResult.isValid && (
        <div className="validation-messages">
          {validationResult.errors.map((error, i) => <Message key={i} severity="error" text={error} />)}
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="suggestions-section">
          <h5 style={{ margin: '0 0 0.5rem 0' }}>Vorschläge:</h5>
          {suggestions.map((s, i) => <Button key={i} label={s} className="p-button-text p-button-sm" onClick={() => { setFullAddress(s); parseAddress(s); }} />)}
        </div>
      )}

      {parsedAddress.confidence > 0 && (
        <div className="confidence-indicator">
          <span style={{ fontSize: '0.75rem', color: 'var(--text-color-secondary)' }}>Parsing-Qualität:</span>
          <div className="confidence-bar" style={{ width: `${parsedAddress.confidence * 100}%` }}></div>
        </div>
      )}
    </div>
  );
};

export default AddressInput;
