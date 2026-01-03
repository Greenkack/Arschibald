import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Steps } from 'primereact/steps';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { Toast } from 'primereact/toast';
import { Divider } from 'primereact/divider';
import { Chip } from 'primereact/chip';
import 'primereact/resources/themes/saga-blue/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import { Project, Customer } from '../packages/core/src/types/db';

// Product interfaces from Python logic
interface Product {
  id?: number;
  category: string;
  model_name: string;
  brand: string;
  price_euro: number;
  capacity_w?: number;
  storage_power_kw?: number;
  power_kw?: number;
  max_cycles?: number;
  warranty_years?: number;
  length_m?: number;
  width_m?: number;
  weight_kg?: number;
  efficiency_percent?: number;
  origin_country?: string;
  description?: string;
}

interface SystemConfiguration {
  anlage_kwp: number;
  pv_power_kw: number;
  pv_modules: Product[];
  inverter: Product;
  battery?: Product;
  wallbox?: Product;
}

interface ProjectCalculation {
  module_quantity: number;
  total_cost: number;
  annual_yield_kwh: number;
  roi_years: number;
  co2_savings_kg: number;
  battery_included: boolean;
  wallbox_included: boolean;
  optimal_tilt: number;
  optimal_azimuth: number;
  shading_factor: number;
  energy_independence_percent: number;
  annual_savings_euro: number;
  payback_period: number;
  lcoe_euro_kwh: number;
  investment_profitability: number;
  environmental_impact_score: number;
  // Added the missing field
  system_power_kwp: number;
}

interface ProjectFormProps {
  project?: Partial<Project>;
  customer?: Customer;
  onSave: (project: Omit<Project, 'id'>) => void;
  onCancel: () => void;
  onCalculate?: (data: any) => ProjectCalculation;
}

const getLabel = (key: string, fallback: string): string => {
  // Simplified localization - in real app this would use i18n
  const labels: Record<string, string> = {
    'crm_project_basic_info': 'Grunddaten',
    'crm_project_roof_details': 'Dachdaten',
    'crm_project_consumption': 'Verbrauchsdaten',
    'crm_project_system_config': 'Anlagenkonfiguration',
    'crm_project_location': 'Standortdaten',
    'crm_project_name': 'Projektname',
    'crm_project_status': 'Status',
    'crm_project_priority': 'Priorität',
    'crm_project_roof_type': 'Dachtyp',
    'crm_project_roof_covering': 'Dachbedeckung',
    'crm_project_roof_area': 'Dachfläche (m²)',
    'crm_project_roof_orientation': 'Ausrichtung',
    'crm_project_roof_inclination': 'Neigungswinkel',
    'crm_project_annual_consumption': 'Jahresverbrauch (kWh)',
    'crm_project_energy_costs': 'Stromkosten (€/Jahr)',
    'crm_project_plant_type': 'Anlagentyp',
    'crm_project_feed_in_type': 'Einspeiseart',
    'crm_project_module_quantity': 'Modulanzahl',
    'crm_project_street': 'Straße',
    'crm_project_city': 'Stadt',
    'crm_project_zip': 'PLZ',
    'crm_project_country': 'Land'
  };
  return labels[key] || fallback;
};

export default function ProjectForm({ 
  project, 
  customer, 
  onSave, 
  onCancel, 
  onCalculate 
}: ProjectFormProps) {
  // Form state
  const [formData, setFormData] = useState<Partial<Project>>({
    project_name: '',
    customer_id: customer?.id,
    project_status: 'Angebot',
    roof_type: 'Satteldach',
    roof_covering_type: 'Ziegel',
    free_roof_area_sqm: 0,
    roof_orientation: 'Süd',
    roof_inclination_deg: 30,
    annual_consumption_kwh: 0,
    costs_household_euro_mo: 0,
    anlage_type: 'Eigenverbrauch',
    feed_in_type: 'Überschusseinspeisung',
    ...project
  });

  // Wizard state
  const [activeStep, setActiveStep] = useState(0);
  const [calculation, setCalculation] = useState<ProjectCalculation | null>(null);
  const toast = useRef<Toast>(null);

  // Steps definition
  const stepItems = [
    { label: 'Grunddaten' },
    { label: 'Dach & Verbrauch' },
    { label: 'Anlagenkonfiguration' },
    { label: 'Komponenten & Standort' }
  ];

  // Dropdown options
  const statusOptions = [
    { label: 'Angebot', value: 'Angebot' },
    { label: 'In Bearbeitung', value: 'In Bearbeitung' },
    { label: 'Genehmigt', value: 'Genehmigt' },
    { label: 'Abgelehnt', value: 'Abgelehnt' },
    { label: 'Abgeschlossen', value: 'Abgeschlossen' }
  ];

  const priorityOptions = [
    { label: 'Niedrig', value: 'Niedrig' },
    { label: 'Normal', value: 'Normal' },
    { label: 'Hoch', value: 'Hoch' },
    { label: 'Kritisch', value: 'Kritisch' }
  ];

  const roofTypeOptions = [
    { label: 'Satteldach', value: 'Satteldach' },
    { label: 'Flachdach', value: 'Flachdach' },
    { label: 'Pultdach', value: 'Pultdach' },
    { label: 'Walmdach', value: 'Walmdach' }
  ];

  const roofCoveringOptions = [
    { label: 'Ziegel', value: 'Ziegel' },
    { label: 'Blech', value: 'Blech' },
    { label: 'Schiefer', value: 'Schiefer' },
    { label: 'Beton', value: 'Beton' }
  ];

  const orientationOptions = [
    { label: 'Süd', value: 'Süd' },
    { label: 'Südwest', value: 'Südwest' },
    { label: 'Südost', value: 'Südost' },
    { label: 'West', value: 'West' },
    { label: 'Ost', value: 'Ost' }
  ];

  const plantTypeOptions = [
    { label: 'Eigenverbrauch', value: 'Eigenverbrauch' },
    { label: 'Volleinspeisung', value: 'Volleinspeisung' },
    { label: 'Hybrid', value: 'Hybrid' }
  ];

  const feedInTypeOptions = [
    { label: 'Überschusseinspeisung', value: 'Überschusseinspeisung' },
    { label: 'Volleinspeisung', value: 'Volleinspeisung' },
    { label: 'Keine Einspeisung', value: 'Keine Einspeisung' }
  ];

  // Form handlers
  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    if (activeStep < stepItems.length - 1) {
      setActiveStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (activeStep > 0) {
      setActiveStep(prev => prev - 1);
    }
  };

  const handleCalculate = () => {
    if (onCalculate) {
      const result = onCalculate(formData);
      setCalculation(result);
      toast.current?.show({
        severity: 'success',
        summary: 'Berechnung abgeschlossen',
        detail: `Anlage: ${result.system_power_kwp} kWp, Jahresertrag: ${result.annual_yield_kwh.toLocaleString()} kWh`
      });
    }
  };

  const handleSubmit = () => {
    if (!formData.project_name?.trim()) {
      toast.current?.show({
        severity: 'error',
        summary: 'Validierungsfehler',
        detail: 'Projektname ist erforderlich'
      });
      return;
    }

    onSave(formData as Omit<Project, 'id'>);
  };

  const canProceed = (step: number): boolean => {
    switch (step) {
      case 0:
        return !!(formData.project_name?.trim());
      case 1:
        return !!(formData.free_roof_area_sqm && formData.annual_consumption_kwh);
      case 2:
        return true; // Simplified for now
      default:
        return true;
    }
  };

  return (
    <div className="project-form-container p-4">
      <Toast ref={toast} />
      
      <Card className="mb-4">
        <div className="card-header flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">
            {project?.id ? 'Projekt bearbeiten' : 'Neues Projekt'}
          </h2>
          {customer && (
            <div className="customer-info">
              <Chip 
                label={`${customer.first_name} ${customer.last_name}`}
                icon="pi pi-user"
                className="mr-2"
              />
            </div>
          )}
        </div>

        {/* Progress Steps */}
        <Steps 
          model={stepItems} 
          activeIndex={activeStep} 
          className="mb-6"
          readOnly={false}
        />

        <form className="project-form">
          {/* Step 0: Grunddaten */}
          {activeStep === 0 && (
            <div className="form-step">
              <div className="form-section">
                <h3 className="text-xl font-semibold mb-4">
                  <i className="pi pi-info-circle mr-2"></i>
                  {getLabel('crm_project_basic_info', 'Grunddaten')}
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="field">
                    <label htmlFor="project_name" className="font-medium">
                      {getLabel('crm_project_name', 'Projektname')} *
                    </label>
                    <InputText
                      id="project_name"
                      value={formData.project_name || ''}
                      onChange={(e) => handleInputChange('project_name', e.target.value)}
                      placeholder="PV-Anlage Familie Mustermann"
                      className="w-full"
                      required
                    />
                  </div>

                  <div className="field">
                    <label htmlFor="status" className="font-medium">
                      {getLabel('crm_project_status', 'Status')}
                    </label>
                    <Dropdown
                      id="status"
                      value={formData.project_status}
                      options={statusOptions}
                      onChange={(e) => handleInputChange('project_status', e.value)}
                      placeholder="Status auswählen"
                      className="w-full"
                    />
                  </div>

                  {/* Priority field removed as not in Project interface */}
                </div>
              </div>
            </div>
          )}

          {/* Step 1: Dach & Verbrauch */}
          {activeStep === 1 && (
            <div className="form-step">
              <div className="form-section">
                <h3 className="text-xl font-semibold mb-4">
                  <i className="pi pi-home mr-2"></i>
                  {getLabel('crm_project_roof_details', 'Dachdaten')}
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="field">
                    <label htmlFor="roof_type" className="font-medium">
                      {getLabel('crm_project_roof_type', 'Dachtyp')}
                    </label>
                    <Dropdown
                      id="roof_type"
                      value={formData.roof_type}
                      options={roofTypeOptions}
                      onChange={(e) => handleInputChange('roof_type', e.value)}
                      className="w-full"
                    />
                  </div>

                  <div className="field">
                    <label htmlFor="roof_covering" className="font-medium">
                      {getLabel('crm_project_roof_covering', 'Dachbedeckung')}
                    </label>
                    <Dropdown
                      id="roof_covering"
                      value={formData.roof_covering_type}
                      options={roofCoveringOptions}
                      onChange={(e) => handleInputChange('roof_covering_type', e.value)}
                      className="w-full"
                    />
                  </div>

                  <div className="field">
                    <label htmlFor="roof_area" className="font-medium">
                      {getLabel('crm_project_roof_area', 'Dachfläche (m²)')} *
                    </label>
                    <InputNumber
                      id="roof_area"
                      value={formData.free_roof_area_sqm}
                      onChange={(e) => handleInputChange('free_roof_area_sqm', e.value)}
                      placeholder="120"
                      suffix=" m²"
                      min={0}
                      max={1000}
                      className="w-full"
                      required
                    />
                  </div>

                  <div className="field">
                    <label htmlFor="roof_orientation" className="font-medium">
                      {getLabel('crm_project_roof_orientation', 'Ausrichtung')}
                    </label>
                    <Dropdown
                      id="roof_orientation"
                      value={formData.roof_orientation}
                      options={orientationOptions}
                      onChange={(e) => handleInputChange('roof_orientation', e.value)}
                      className="w-full"
                    />
                  </div>

                  <div className="field">
                    <label htmlFor="roof_inclination" className="font-medium">
                      {getLabel('crm_project_roof_inclination', 'Neigungswinkel')}
                    </label>
                    <InputNumber
                      id="roof_inclination"
                      value={formData.roof_inclination_deg}
                      onChange={(e) => handleInputChange('roof_inclination_deg', e.value)}
                      placeholder="30"
                      suffix="°"
                      min={0}
                      max={90}
                      className="w-full"
                    />
                  </div>
                </div>

                <Divider />

                <h4 className="text-lg font-semibold mb-3">
                  <i className="pi pi-bolt mr-2"></i>
                  {getLabel('crm_project_consumption', 'Verbrauchsdaten')}
                </h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="field">
                    <label htmlFor="annual_consumption" className="font-medium">
                      {getLabel('crm_project_annual_consumption', 'Jahresverbrauch (kWh)')} *
                    </label>
                    <InputNumber
                      id="annual_consumption"
                      value={formData.annual_consumption_kwh}
                      onChange={(e) => handleInputChange('annual_consumption_kwh', e.value)}
                      placeholder="4000"
                      suffix=" kWh"
                      min={0}
                      className="w-full"
                      required
                    />
                  </div>

                  <div className="field">
                    <label htmlFor="energy_costs" className="font-medium">
                      {getLabel('crm_project_energy_costs', 'Stromkosten (€/Monat)')}
                    </label>
                    <InputNumber
                      id="energy_costs"
                      value={formData.costs_household_euro_mo}
                      onChange={(e) => handleInputChange('costs_household_euro_mo', e.value)}
                      placeholder="100"
                      mode="currency"
                      currency="EUR"
                      locale="de-DE"
                      min={0}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Anlagenkonfiguration */}
          {activeStep === 2 && (
            <div className="form-step">
              <div className="form-section">
                <h3 className="text-xl font-semibold mb-4">
                  <i className="pi pi-cog mr-2"></i>
                  {getLabel('crm_project_system_config', 'Anlagenkonfiguration')}
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="field">
                    <label htmlFor="plant_type" className="font-medium">
                      {getLabel('crm_project_plant_type', 'Anlagentyp')}
                    </label>
                    <Dropdown
                      id="plant_type"
                      value={formData.anlage_type}
                      options={plantTypeOptions}
                      onChange={(e) => handleInputChange('anlage_type', e.value)}
                      className="w-full"
                    />
                  </div>

                  <div className="field">
                    <label htmlFor="feed_in_type" className="font-medium">
                      {getLabel('crm_project_feed_in_type', 'Einspeiseart')}
                    </label>
                    <Dropdown
                      id="feed_in_type"
                      value={formData.feed_in_type}
                      options={feedInTypeOptions}
                      onChange={(e) => handleInputChange('feed_in_type', e.value)}
                      className="w-full"
                    />
                  </div>

                  <div className="field">
                    <label htmlFor="module_quantity" className="font-medium">
                      {getLabel('crm_project_module_quantity', 'Modulanzahl')} *
                    </label>
                    <InputNumber
                      id="module_quantity"
                      value={formData.module_quantity}
                      onChange={(e) => handleInputChange('module_quantity', e.value)}
                      placeholder="20"
                      min={1}
                      max={100}
                      className="w-full"
                      required
                    />
                  </div>
                </div>

                {calculation && (
                  <div className="calculation-results mt-4 p-4 bg-gray-50 rounded">
                    <h4 className="text-lg font-semibold mb-3">Berechnungsergebnis</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div className="stat">
                        <span className="text-sm text-gray-600">Anlagenleistung</span>
                        <div className="text-lg font-bold">{calculation.system_power_kwp} kWp</div>
                      </div>
                      <div className="stat">
                        <span className="text-sm text-gray-600">Jahresertrag</span>
                        <div className="text-lg font-bold">{calculation.annual_yield_kwh.toLocaleString()} kWh</div>
                      </div>
                      <div className="stat">
                        <span className="text-sm text-gray-600">Gesamtkosten</span>
                        <div className="text-lg font-bold">{calculation.total_cost.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}</div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="mt-4">
                  <Button
                    label="Berechnung ausführen"
                    icon="pi pi-calculator"
                    onClick={handleCalculate}
                    className="p-button-outlined"
                    disabled={!canProceed(2)}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Komponenten & Standort */}
          {activeStep === 3 && (
            <div className="form-step">
              <div className="form-section">
                <h3 className="text-xl font-semibold mb-4">
                  <i className="pi pi-map-marker mr-2"></i>
                  {getLabel('crm_project_location', 'Standortdaten')}
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="field">
                    <p className="text-gray-600">
                      Standortdaten werden automatisch aus den Kundendaten übernommen.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="form-navigation flex justify-between mt-6 pt-4 border-t border-gray-200">
            <Button
              label="Zurück"
              icon="pi pi-chevron-left"
              className="p-button-outlined"
              onClick={handlePrevious}
              disabled={activeStep === 0}
            />

            <div className="flex gap-2">
              <Button
                label="Abbrechen"
                icon="pi pi-times"
                className="p-button-outlined p-button-danger"
                onClick={onCancel}
              />

              {activeStep < stepItems.length - 1 ? (
                <Button
                  label="Weiter"
                  icon="pi pi-chevron-right"
                  iconPos="right"
                  onClick={handleNext}
                  disabled={!canProceed(activeStep)}
                />
              ) : (
                <Button
                  label="Projekt speichern"
                  icon="pi pi-save"
                  className="p-button-success"
                  onClick={handleSubmit}
                  disabled={!canProceed(activeStep)}
                />
              )}
            </div>
          </div>
        </form>
      </Card>
    </div>
  );
}
