/**
 * Solar Calculator Multi-Step Form
 * 
 * A comprehensive form for solar system calculation with:
 * - Multi-step wizard interface
 * - Roof configuration
 * - Location selection with autocomplete
 * - Module type selection with product images
 * - Consumption input with validation
 * - German number formatting
 */

import React, { useState, useEffect } from 'react';
import { Steps } from 'primereact/steps';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { Checkbox } from 'primereact/checkbox';
import { AutoComplete } from 'primereact/autocomplete';
import { Message } from 'primereact/message';
import { Divider } from 'primereact/divider';
import { GermanNumberInput } from '../GermanNumberInput';
import { GermanCurrencyInput } from '../GermanCurrencyInput';
import './SolarCalculatorForm.css';

// Types
interface SolarFormData {
  // Customer data
  customerName: string;
  customerEmail: string;
  
  // Location
  latitude: number | null;
  longitude: number | null;
  address: string;
  
  // Roof configuration
  roofAreaM2: number | null;
  roofOrientation: string;
  roofInclinationDeg: number;
  roofType: string;
  
  // Module configuration
  selectedModuleId: number | null;
  moduleQuantity: number;
  moduleCapacityW: number | null;
  
  // Consumption
  annualConsumptionKwhYr: number;
  consumptionHeatingKwhYr: number;
  electricityPriceKwh: number;
  
  // Storage
  includeStorage: boolean;
  selectedStorageId: number | null;
  selectedStorageCapacityKwh: number;
  
  // Economic parameters
  simulationPeriodYears: number;
  electricityPriceIncreaseAnnualPercent: number;
  
  // Options
  usePvgis: boolean;
  globalYieldAdjustmentPercent: number;
}

interface Module {
  id: number;
  name: string;
  manufacturer: string;
  capacityW: number;
  imageUrl?: string;
  price: number;
}

interface Storage {
  id: number;
  name: string;
  manufacturer: string;
  capacityKwh: number;
  price: number;
}

interface LocationSuggestion {
  label: string;
  latitude: number;
  longitude: number;
}

interface SolarCalculatorFormProps {
  onSubmit: (data: SolarFormData) => void;
  onCancel?: () => void;
  initialData?: Partial<SolarFormData>;
  loading?: boolean;
}

const SolarCalculatorForm: React.FC<SolarCalculatorFormProps> = ({
  onSubmit,
  onCancel,
  initialData,
  loading = false
}) => {
  // Form state
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<SolarFormData>({
    customerName: '',
    customerEmail: '',
    latitude: null,
    longitude: null,
    address: '',
    roofAreaM2: null,
    roofOrientation: 'Süd',
    roofInclinationDeg: 30,
    roofType: 'Satteldach',
    selectedModuleId: null,
    moduleQuantity: 0,
    moduleCapacityW: null,
    annualConsumptionKwhYr: 4000,
    consumptionHeatingKwhYr: 0,
    electricityPriceKwh: 0.30,
    includeStorage: false,
    selectedStorageId: null,
    selectedStorageCapacityKwh: 0,
    simulationPeriodYears: 25,
    electricityPriceIncreaseAnnualPercent: 2.0,
    usePvgis: true,
    globalYieldAdjustmentPercent: 0,
    ...initialData
  });

  // Validation errors
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Location autocomplete
  const [locationSuggestions, setLocationSuggestions] = useState<LocationSuggestion[]>([]);
  const [filteredLocations, setFilteredLocations] = useState<LocationSuggestion[]>([]);

  // Module and storage data
  const [modules, setModules] = useState<Module[]>([]);
  const [storages, setStorages] = useState<Storage[]>([]);

  // Steps configuration
  const steps = [
    { label: 'Kunde & Standort' },
    { label: 'Dachkonfiguration' },
    { label: 'Modulauswahl' },
    { label: 'Verbrauch' },
    { label: 'Speicher & Optionen' }
  ];

  // Roof orientation options
  const roofOrientations = [
    { label: 'Süd', value: 'Süd' },
    { label: 'Südost', value: 'Südost' },
    { label: 'Südwest', value: 'Südwest' },
    { label: 'Ost', value: 'Ost' },
    { label: 'West', value: 'West' },
    { label: 'Nord', value: 'Nord' },
    { label: 'Nordost', value: 'Nordost' },
    { label: 'Nordwest', value: 'Nordwest' },
    { label: 'Flachdach', value: 'Flachdach' }
  ];

  // Roof type options
  const roofTypes = [
    { label: 'Satteldach', value: 'Satteldach' },
    { label: 'Flachdach', value: 'Flachdach' },
    { label: 'Walmdach', value: 'Walmdach' },
    { label: 'Pultdach', value: 'Pultdach' },
    { label: 'Sonstige', value: 'Sonstige' }
  ];

  // Load modules and storages on mount
  useEffect(() => {
    loadModules();
    loadStorages();
    loadLocationSuggestions();
  }, []);

  const loadModules = async () => {
    // TODO: Load from API
    // Placeholder data
    setModules([
      {
        id: 1,
        name: 'Trina Solar TSM-400W',
        manufacturer: 'Trina Solar',
        capacityW: 400,
        price: 150,
        imageUrl: '/images/modules/trina-400.jpg'
      },
      {
        id: 2,
        name: 'JA Solar JAM72S20-450W',
        manufacturer: 'JA Solar',
        capacityW: 450,
        price: 170,
        imageUrl: '/images/modules/ja-450.jpg'
      },
      {
        id: 3,
        name: 'Longi LR5-72HPH-450M',
        manufacturer: 'Longi',
        capacityW: 450,
        price: 165,
        imageUrl: '/images/modules/longi-450.jpg'
      }
    ]);
  };

  const loadStorages = async () => {
    // TODO: Load from API
    // Placeholder data
    setStorages([
      {
        id: 1,
        name: 'BYD Battery-Box Premium HVS 7.7',
        manufacturer: 'BYD',
        capacityKwh: 7.7,
        price: 5500
      },
      {
        id: 2,
        name: 'Huawei LUNA2000-10-S0',
        manufacturer: 'Huawei',
        capacityKwh: 10,
        price: 6500
      },
      {
        id: 3,
        name: 'Sonnen Batterie 10',
        manufacturer: 'Sonnen',
        capacityKwh: 10,
        price: 8500
      }
    ]);
  };

  const loadLocationSuggestions = () => {
    // Common German cities with coordinates
    setLocationSuggestions([
      { label: 'Berlin', latitude: 52.5200, longitude: 13.4050 },
      { label: 'München', latitude: 48.1351, longitude: 11.5820 },
      { label: 'Hamburg', latitude: 53.5511, longitude: 9.9937 },
      { label: 'Frankfurt am Main', latitude: 50.1109, longitude: 8.6821 },
      { label: 'Köln', latitude: 50.9375, longitude: 6.9603 },
      { label: 'Stuttgart', latitude: 48.7758, longitude: 9.1829 },
      { label: 'Düsseldorf', latitude: 51.2277, longitude: 6.7735 },
      { label: 'Dortmund', latitude: 51.5136, longitude: 7.4653 },
      { label: 'Essen', latitude: 51.4556, longitude: 7.0116 },
      { label: 'Leipzig', latitude: 51.3397, longitude: 12.3731 }
    ]);
  };

  const searchLocation = (event: { query: string }) => {
    const query = event.query.toLowerCase();
    const filtered = locationSuggestions.filter(loc =>
      loc.label.toLowerCase().includes(query)
    );
    setFilteredLocations(filtered);
  };

  const handleLocationSelect = (location: LocationSuggestion) => {
    setFormData(prev => ({
      ...prev,
      address: location.label,
      latitude: location.latitude,
      longitude: location.longitude
    }));
  };

  const handleModuleSelect = (moduleId: number) => {
    const module = modules.find(m => m.id === moduleId);
    if (module) {
      setFormData(prev => ({
        ...prev,
        selectedModuleId: moduleId,
        moduleCapacityW: module.capacityW
      }));
    }
  };

  const handleStorageSelect = (storageId: number) => {
    const storage = storages.find(s => s.id === storageId);
    if (storage) {
      setFormData(prev => ({
        ...prev,
        selectedStorageId: storageId,
        selectedStorageCapacityKwh: storage.capacityKwh
      }));
    }
  };

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 0: // Customer & Location
        if (!formData.customerName.trim()) {
          newErrors.customerName = 'Kundenname ist erforderlich';
        }
        if (!formData.address.trim()) {
          newErrors.address = 'Adresse ist erforderlich';
        }
        if (formData.latitude === null || formData.longitude === null) {
          newErrors.location = 'Bitte wählen Sie einen Standort aus';
        }
        break;

      case 1: // Roof Configuration
        if (!formData.roofAreaM2 || formData.roofAreaM2 <= 0) {
          newErrors.roofAreaM2 = 'Dachfläche muss größer als 0 sein';
        }
        if (formData.roofInclinationDeg < 0 || formData.roofInclinationDeg > 90) {
          newErrors.roofInclinationDeg = 'Dachneigung muss zwischen 0° und 90° liegen';
        }
        break;

      case 2: // Module Selection
        if (!formData.selectedModuleId) {
          newErrors.selectedModuleId = 'Bitte wählen Sie ein Modul aus';
        }
        if (formData.moduleQuantity <= 0) {
          newErrors.moduleQuantity = 'Modulanzahl muss größer als 0 sein';
        }
        break;

      case 3: // Consumption
        if (formData.annualConsumptionKwhYr <= 0) {
          newErrors.annualConsumptionKwhYr = 'Jahresverbrauch muss größer als 0 sein';
        }
        if (formData.electricityPriceKwh <= 0) {
          newErrors.electricityPriceKwh = 'Strompreis muss größer als 0 sein';
        }
        break;

      case 4: // Storage & Options
        if (formData.includeStorage && !formData.selectedStorageId) {
          newErrors.selectedStorageId = 'Bitte wählen Sie einen Speicher aus';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep(prev => Math.min(prev + 1, steps.length - 1));
    }
  };

  const handleBack = () => {
    setActiveStep(prev => Math.max(prev - 1, 0));
  };

  const handleSubmit = () => {
    if (validateStep(activeStep)) {
      onSubmit(formData);
    }
  };

  const updateFormData = (field: keyof SolarFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Render step content
  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderCustomerLocationStep();
      case 1:
        return renderRoofConfigurationStep();
      case 2:
        return renderModuleSelectionStep();
      case 3:
        return renderConsumptionStep();
      case 4:
        return renderStorageOptionsStep();
      default:
        return null;
    }
  };

  const renderCustomerLocationStep = () => (
    <div className="form-step">
      <h3>☀️ Kunde & Standort</h3>
      <Divider />

      <div className="p-fluid">
        <div className="p-field">
          <label htmlFor="customerName">Kundenname *</label>
          <InputText
            id="customerName"
            value={formData.customerName}
            onChange={(e) => updateFormData('customerName', e.target.value)}
            className={errors.customerName ? 'p-invalid' : ''}
            placeholder="Max Mustermann"
          />
          {errors.customerName && (
            <small className="p-error">{errors.customerName}</small>
          )}
        </div>

        <div className="p-field">
          <label htmlFor="customerEmail">E-Mail</label>
          <InputText
            id="customerEmail"
            type="email"
            value={formData.customerEmail}
            onChange={(e) => updateFormData('customerEmail', e.target.value)}
            placeholder="max@example.com"
          />
        </div>

        <div className="p-field">
          <label htmlFor="address">📍 Standort *</label>
          <AutoComplete
            id="address"
            value={formData.address}
            suggestions={filteredLocations}
            completeMethod={searchLocation}
            field="label"
            onChange={(e) => updateFormData('address', e.value)}
            onSelect={(e) => handleLocationSelect(e.value)}
            placeholder="Stadt oder Adresse eingeben"
            className={errors.address || errors.location ? 'p-invalid' : ''}
          />
          {(errors.address || errors.location) && (
            <small className="p-error">{errors.address || errors.location}</small>
          )}
        </div>

        {formData.latitude && formData.longitude && (
          <Message
            severity="success"
            text={`Koordinaten: ${formData.latitude.toFixed(4)}°N, ${formData.longitude.toFixed(4)}°E`}
          />
        )}
      </div>
    </div>
  );

  const renderRoofConfigurationStep = () => (
    <div className="form-step">
      <h3>🏠 Dachkonfiguration</h3>
      <Divider />

      <div className="p-fluid">
        <div className="p-field">
          <label htmlFor="roofAreaM2">Verfügbare Dachfläche (m²) *</label>
          <GermanNumberInput
            id="roofAreaM2"
            value={formData.roofAreaM2 || 0}
            onChange={(value) => updateFormData('roofAreaM2', value)}
            min={0}
            max={1000}
            suffix=" m²"
            className={errors.roofAreaM2 ? 'p-invalid' : ''}
          />
          {errors.roofAreaM2 && (
            <small className="p-error">{errors.roofAreaM2}</small>
          )}
        </div>

        <div className="p-field">
          <label htmlFor="roofType">Dachtyp</label>
          <Dropdown
            id="roofType"
            value={formData.roofType}
            options={roofTypes}
            onChange={(e) => updateFormData('roofType', e.value)}
            placeholder="Dachtyp wählen"
          />
        </div>

        <div className="p-field">
          <label htmlFor="roofOrientation">Dachausrichtung</label>
          <Dropdown
            id="roofOrientation"
            value={formData.roofOrientation}
            options={roofOrientations}
            onChange={(e) => updateFormData('roofOrientation', e.value)}
            placeholder="Ausrichtung wählen"
          />
        </div>

        <div className="p-field">
          <label htmlFor="roofInclinationDeg">Dachneigung (°) *</label>
          <InputNumber
            id="roofInclinationDeg"
            value={formData.roofInclinationDeg}
            onValueChange={(e) => updateFormData('roofInclinationDeg', e.value)}
            min={0}
            max={90}
            suffix="°"
            className={errors.roofInclinationDeg ? 'p-invalid' : ''}
          />
          {errors.roofInclinationDeg && (
            <small className="p-error">{errors.roofInclinationDeg}</small>
          )}
        </div>

        <Message
          severity="info"
          text="Optimale Ausrichtung: Süd mit 30° Neigung für maximalen Ertrag"
        />
      </div>
    </div>
  );

  const renderModuleSelectionStep = () => (
    <div className="form-step">
      <h3>⚡ Modulauswahl</h3>
      <Divider />

      <div className="p-fluid">
        <div className="p-field">
          <label>PV-Modul auswählen *</label>
          <div className="module-grid">
            {modules.map(module => (
              <Card
                key={module.id}
                className={`module-card ${formData.selectedModuleId === module.id ? 'selected' : ''}`}
                onClick={() => handleModuleSelect(module.id)}
              >
                {module.imageUrl && (
                  <img
                    src={module.imageUrl}
                    alt={module.name}
                    className="module-image"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = '/images/placeholder-module.png';
                    }}
                  />
                )}
                <h4>{module.manufacturer}</h4>
                <p>{module.name}</p>
                <p className="module-capacity">{module.capacityW}W</p>
                <p className="module-price">{module.price.toFixed(2)} €</p>
              </Card>
            ))}
          </div>
          {errors.selectedModuleId && (
            <small className="p-error">{errors.selectedModuleId}</small>
          )}
        </div>

        <div className="p-field">
          <label htmlFor="moduleQuantity">Anzahl Module *</label>
          <InputNumber
            id="moduleQuantity"
            value={formData.moduleQuantity}
            onValueChange={(e) => updateFormData('moduleQuantity', e.value)}
            min={0}
            max={200}
            showButtons
            className={errors.moduleQuantity ? 'p-invalid' : ''}
          />
          {errors.moduleQuantity && (
            <small className="p-error">{errors.moduleQuantity}</small>
          )}
        </div>

        {formData.selectedModuleId && formData.moduleQuantity > 0 && (
          <Message
            severity="success"
            text={`Systemgröße: ${((formData.moduleCapacityW || 0) * formData.moduleQuantity / 1000).toFixed(2)} kWp`}
          />
        )}
      </div>
    </div>
  );

  const renderConsumptionStep = () => (
    <div className="form-step">
      <h3>💡 Stromverbrauch</h3>
      <Divider />

      <div className="p-fluid">
        <div className="p-field">
          <label htmlFor="annualConsumptionKwhYr">Jahresverbrauch Haushalt (kWh/Jahr) *</label>
          <GermanNumberInput
            id="annualConsumptionKwhYr"
            value={formData.annualConsumptionKwhYr}
            onChange={(value) => updateFormData('annualConsumptionKwhYr', value)}
            min={0}
            max={50000}
            suffix=" kWh/Jahr"
            className={errors.annualConsumptionKwhYr ? 'p-invalid' : ''}
          />
          {errors.annualConsumptionKwhYr && (
            <small className="p-error">{errors.annualConsumptionKwhYr}</small>
          )}
        </div>

        <div className="p-field">
          <label htmlFor="consumptionHeatingKwhYr">Jahresverbrauch Heizung (kWh/Jahr)</label>
          <GermanNumberInput
            id="consumptionHeatingKwhYr"
            value={formData.consumptionHeatingKwhYr}
            onChange={(value) => updateFormData('consumptionHeatingKwhYr', value)}
            min={0}
            max={50000}
            suffix=" kWh/Jahr"
          />
        </div>

        <div className="p-field">
          <label htmlFor="electricityPriceKwh">Strompreis (€/kWh) *</label>
          <GermanCurrencyInput
            id="electricityPriceKwh"
            value={formData.electricityPriceKwh}
            onChange={(value) => updateFormData('electricityPriceKwh', value)}
            min={0}
            max={1}
            className={errors.electricityPriceKwh ? 'p-invalid' : ''}
          />
          {errors.electricityPriceKwh && (
            <small className="p-error">{errors.electricityPriceKwh}</small>
          )}
        </div>

        <div className="p-field">
          <label htmlFor="electricityPriceIncreaseAnnualPercent">Jährliche Strompreissteigerung (%)</label>
          <InputNumber
            id="electricityPriceIncreaseAnnualPercent"
            value={formData.electricityPriceIncreaseAnnualPercent}
            onValueChange={(e) => updateFormData('electricityPriceIncreaseAnnualPercent', e.value)}
            min={0}
            max={20}
            suffix="%"
            minFractionDigits={1}
            maxFractionDigits={1}
          />
        </div>

        <Message
          severity="info"
          text="Durchschnittlicher Haushalt: 3.000-5.000 kWh/Jahr"
        />
      </div>
    </div>
  );

  const renderStorageOptionsStep = () => (
    <div className="form-step">
      <h3>🔋 Speicher & Optionen</h3>
      <Divider />

      <div className="p-fluid">
        <div className="p-field-checkbox">
          <Checkbox
            inputId="includeStorage"
            checked={formData.includeStorage}
            onChange={(e) => updateFormData('includeStorage', e.checked)}
          />
          <label htmlFor="includeStorage">Batteriespeicher hinzufügen</label>
        </div>

        {formData.includeStorage && (
          <>
            <div className="p-field">
              <label>Speicher auswählen *</label>
              <div className="storage-list">
                {storages.map(storage => (
                  <Card
                    key={storage.id}
                    className={`storage-card ${formData.selectedStorageId === storage.id ? 'selected' : ''}`}
                    onClick={() => handleStorageSelect(storage.id)}
                  >
                    <h4>{storage.manufacturer}</h4>
                    <p>{storage.name}</p>
                    <p className="storage-capacity">{storage.capacityKwh} kWh</p>
                    <p className="storage-price">{storage.price.toFixed(2)} €</p>
                  </Card>
                ))}
              </div>
              {errors.selectedStorageId && (
                <small className="p-error">{errors.selectedStorageId}</small>
              )}
            </div>
          </>
        )}

        <Divider />

        <div className="p-field">
          <label htmlFor="simulationPeriodYears">Simulationszeitraum (Jahre)</label>
          <InputNumber
            id="simulationPeriodYears"
            value={formData.simulationPeriodYears}
            onValueChange={(e) => updateFormData('simulationPeriodYears', e.value)}
            min={1}
            max={50}
            suffix=" Jahre"
          />
        </div>

        <div className="p-field-checkbox">
          <Checkbox
            inputId="usePvgis"
            checked={formData.usePvgis}
            onChange={(e) => updateFormData('usePvgis', e.checked)}
          />
          <label htmlFor="usePvgis">PVGIS für Ertragsberechnung verwenden</label>
        </div>

        <div className="p-field">
          <label htmlFor="globalYieldAdjustmentPercent">Globale Ertragsanpassung (%)</label>
          <InputNumber
            id="globalYieldAdjustmentPercent"
            value={formData.globalYieldAdjustmentPercent}
            onValueChange={(e) => updateFormData('globalYieldAdjustmentPercent', e.value)}
            min={-50}
            max={50}
            suffix="%"
          />
        </div>
      </div>
    </div>
  );

  return (
    <div className="solar-calculator-form">
      <Card>
        <Steps
          model={steps}
          activeIndex={activeStep}
          onSelect={(e) => setActiveStep(e.index)}
          readOnly={false}
        />

        <div className="form-content">
          {renderStepContent()}
        </div>

        <div className="form-actions">
          <Button
            label="Zurück"
            icon="pi pi-arrow-left"
            onClick={handleBack}
            disabled={activeStep === 0 || loading}
            className="p-button-secondary"
          />

          {activeStep < steps.length - 1 ? (
            <Button
              label="Weiter"
              icon="pi pi-arrow-right"
              iconPos="right"
              onClick={handleNext}
              disabled={loading}
            />
          ) : (
            <Button
              label="Berechnen"
              icon="pi pi-check"
              onClick={handleSubmit}
              loading={loading}
              className="p-button-success"
            />
          )}

          {onCancel && (
            <Button
              label="Abbrechen"
              icon="pi pi-times"
              onClick={onCancel}
              disabled={loading}
              className="p-button-text"
            />
          )}
        </div>
      </Card>
    </div>
  );
};

export default SolarCalculatorForm;
