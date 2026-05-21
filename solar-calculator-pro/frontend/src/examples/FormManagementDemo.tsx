/**
 * Form Management Demo
 * 
 * Comprehensive demonstration of the form management system including:
 * - React Hook Form integration
 * - Zod validation
 * - Reusable form components
 * - Auto-save functionality
 * - Error handling
 */

import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Card } from 'primereact/card';
import { Divider } from 'primereact/divider';
import { useForm } from '../hooks/useForm';
import {
  FormTextField,
  FormNumberField,
  FormTextareaField,
  FormDropdownField,
  FormMultiSelectField,
  FormDateField,
  FormCheckboxField,
  FormRadioField,
  FormSliderField,
  FormPasswordField,
} from '../components/forms/FormField';
import { FormContainer } from '../components/forms/FormContainer';
import {
  loginSchema,
  solarCalculatorSchema,
  projectSchema,
  customerSchema,
  type LoginFormData,
  type SolarCalculatorFormData,
  type ProjectFormData,
  type CustomerFormData,
} from '../utils/formValidation';
import './FormManagementDemo.css';

/**
 * Login Form Example
 */
function LoginFormExample() {
  const { control, handleSubmit, formState } = useForm<LoginFormData>({
    schema: loginSchema,
    defaultValues: {
      username: '',
      password: '',
      rememberMe: false,
    },
    onSubmitSuccess: (data) => {
      console.log('Login successful:', data);
    },
  });

  return (
    <FormContainer
      onSubmit={handleSubmit}
      title="Login Formular"
      description="Beispiel für ein einfaches Login-Formular mit Validierung"
      submitLabel="Anmelden"
      isSubmitting={formState.isSubmitting}
    >
      <FormTextField
        name="username"
        control={control}
        label="Benutzername"
        placeholder="Benutzername eingeben"
        required
      />

      <FormPasswordField
        name="password"
        control={control}
        label="Passwort"
        placeholder="Passwort eingeben"
        required
        feedback={false}
      />

      <FormCheckboxField
        name="rememberMe"
        control={control}
        label="Angemeldet bleiben"
      />
    </FormContainer>
  );
}

/**
 * Solar Calculator Form Example with Auto-Save
 */
function SolarCalculatorFormExample() {
  const [savedData, setSavedData] = useState<SolarCalculatorFormData | null>(null);

  const {
    control,
    handleSubmit,
    formState,
    isAutoSaving,
    lastSaved,
  } = useForm<SolarCalculatorFormData>({
    schema: solarCalculatorSchema,
    defaultValues: {
      roofArea: 50,
      roofType: 'gable',
      roofAngle: 30,
      orientation: 'south',
      moduleType: '',
      annualConsumption: 4000,
      location: '',
      batteryStorage: false,
      batteryCapacity: 0,
    },
    autoSave: true,
    autoSaveInterval: 3000,
    onAutoSave: async (data) => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setSavedData(data);
      console.log('Auto-saved:', data);
    },
    onSubmitSuccess: (data) => {
      console.log('Form submitted:', data);
    },
    showSuccessToast: true,
  });

  const roofTypeOptions = [
    { label: 'Flachdach', value: 'flat' },
    { label: 'Satteldach', value: 'gable' },
    { label: 'Walmdach', value: 'hip' },
    { label: 'Pultdach', value: 'shed' },
  ];

  const orientationOptions = [
    { label: 'Norden', value: 'north' },
    { label: 'Nordosten', value: 'northeast' },
    { label: 'Osten', value: 'east' },
    { label: 'Südosten', value: 'southeast' },
    { label: 'Süden', value: 'south' },
    { label: 'Südwesten', value: 'southwest' },
    { label: 'Westen', value: 'west' },
    { label: 'Nordwesten', value: 'northwest' },
  ];

  return (
    <div>
      <FormContainer
        onSubmit={handleSubmit}
        title="Solar Rechner"
        description="Formular mit Auto-Save Funktionalität (speichert alle 3 Sekunden)"
        submitLabel="Berechnen"
        isSubmitting={formState.isSubmitting}
        isAutoSaving={isAutoSaving}
        lastSaved={lastSaved}
      >
        <div className="form-grid">
          <FormNumberField
            name="roofArea"
            control={control}
            label="Dachfläche"
            placeholder="Fläche eingeben"
            suffix=" m²"
            min={1}
            max={1000}
            required
            helperText="Verfügbare Dachfläche in Quadratmetern"
          />

          <FormDropdownField
            name="roofType"
            control={control}
            label="Dachtyp"
            placeholder="Typ auswählen"
            options={roofTypeOptions}
            required
          />

          <FormSliderField
            name="roofAngle"
            control={control}
            label="Dachneigung"
            min={0}
            max={90}
            step={5}
            required
          />

          <FormRadioField
            name="orientation"
            control={control}
            label="Ausrichtung"
            options={orientationOptions}
            required
          />

          <FormTextField
            name="moduleType"
            control={control}
            label="Modultyp"
            placeholder="z.B. Monokristallin"
            required
          />

          <FormNumberField
            name="annualConsumption"
            control={control}
            label="Jahresverbrauch"
            placeholder="Verbrauch eingeben"
            suffix=" kWh"
            min={0}
            required
          />

          <FormTextField
            name="location"
            control={control}
            label="Standort"
            placeholder="Stadt oder PLZ"
            required
          />

          <FormCheckboxField
            name="batteryStorage"
            control={control}
            label="Batteriespeicher hinzufügen"
          />

          <FormNumberField
            name="batteryCapacity"
            control={control}
            label="Speicherkapazität"
            placeholder="Kapazität eingeben"
            suffix=" kWh"
            min={0}
            helperText="Nur relevant wenn Batteriespeicher ausgewählt"
          />
        </div>
      </FormContainer>

      {savedData && (
        <Card title="Zuletzt gespeicherte Daten" className="saved-data-card">
          <pre>{JSON.stringify(savedData, null, 2)}</pre>
        </Card>
      )}
    </div>
  );
}

/**
 * Project Form Example
 */
function ProjectFormExample() {
  const { control, handleSubmit, formState } = useForm<ProjectFormData>({
    schema: projectSchema,
    defaultValues: {
      name: '',
      customerName: '',
      customerEmail: '',
      customerPhone: '',
      projectType: 'solar',
      status: 'draft',
      notes: '',
    },
    onSubmitSuccess: (data) => {
      console.log('Project created:', data);
    },
  });

  const projectTypeOptions = [
    { label: 'Solar', value: 'solar' },
    { label: 'Wärmepumpe', value: 'heatpump' },
    { label: 'Kombiniert', value: 'combined' },
  ];

  const statusOptions = [
    { label: 'Entwurf', value: 'draft' },
    { label: 'Aktiv', value: 'active' },
    { label: 'Abgeschlossen', value: 'completed' },
    { label: 'Archiviert', value: 'archived' },
  ];

  return (
    <FormContainer
      onSubmit={handleSubmit}
      title="Neues Projekt"
      description="Projekt mit Kundeninformationen erstellen"
      submitLabel="Projekt erstellen"
      cancelLabel="Abbrechen"
      showCancelButton
      onCancel={() => console.log('Cancelled')}
      isSubmitting={formState.isSubmitting}
    >
      <FormTextField
        name="name"
        control={control}
        label="Projektname"
        placeholder="Name des Projekts"
        required
      />

      <Divider />

      <h3>Kundeninformationen</h3>

      <div className="form-grid">
        <FormTextField
          name="customerName"
          control={control}
          label="Kundenname"
          placeholder="Vor- und Nachname"
          required
        />

        <FormTextField
          name="customerEmail"
          control={control}
          label="E-Mail"
          placeholder="kunde@beispiel.de"
        />

        <FormTextField
          name="customerPhone"
          control={control}
          label="Telefon"
          placeholder="+49 123 456789"
        />
      </div>

      <Divider />

      <h3>Projektdetails</h3>

      <div className="form-grid">
        <FormDropdownField
          name="projectType"
          control={control}
          label="Projekttyp"
          options={projectTypeOptions}
          required
        />

        <FormDropdownField
          name="status"
          control={control}
          label="Status"
          options={statusOptions}
        />
      </div>

      <FormTextareaField
        name="notes"
        control={control}
        label="Notizen"
        placeholder="Zusätzliche Informationen..."
        rows={4}
        autoResize
      />
    </FormContainer>
  );
}

/**
 * Customer Form Example with Multiple Field Types
 */
function CustomerFormExample() {
  const { control, handleSubmit, formState } = useForm<CustomerFormData>({
    schema: customerSchema,
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      postalCode: '',
      country: 'Deutschland',
      company: '',
      notes: '',
    },
    onSubmitSuccess: (data) => {
      console.log('Customer saved:', data);
    },
  });

  return (
    <FormContainer
      onSubmit={handleSubmit}
      title="Kundenverwaltung"
      description="Vollständiges Kundenformular mit allen Feldtypen"
      submitLabel="Kunde speichern"
      isSubmitting={formState.isSubmitting}
    >
      <div className="form-grid">
        <FormTextField
          name="firstName"
          control={control}
          label="Vorname"
          placeholder="Vorname"
          required
        />

        <FormTextField
          name="lastName"
          control={control}
          label="Nachname"
          placeholder="Nachname"
          required
        />

        <FormTextField
          name="email"
          control={control}
          label="E-Mail"
          placeholder="kunde@beispiel.de"
          required
        />

        <FormTextField
          name="phone"
          control={control}
          label="Telefon"
          placeholder="+49 123 456789"
        />

        <FormTextField
          name="company"
          control={control}
          label="Firma"
          placeholder="Firmenname (optional)"
        />
      </div>

      <Divider />

      <h3>Adresse</h3>

      <FormTextField
        name="address"
        control={control}
        label="Straße und Hausnummer"
        placeholder="Musterstraße 123"
      />

      <div className="form-grid">
        <FormTextField
          name="postalCode"
          control={control}
          label="Postleitzahl"
          placeholder="12345"
        />

        <FormTextField
          name="city"
          control={control}
          label="Stadt"
          placeholder="Musterstadt"
        />

        <FormTextField
          name="country"
          control={control}
          label="Land"
          placeholder="Deutschland"
        />
      </div>

      <FormTextareaField
        name="notes"
        control={control}
        label="Notizen"
        placeholder="Zusätzliche Informationen zum Kunden..."
        rows={3}
        autoResize
      />
    </FormContainer>
  );
}

/**
 * Main Demo Component
 */
export function FormManagementDemo() {
  return (
    <div className="form-management-demo">
      <div className="demo-header">
        <h1>Form Management System</h1>
        <p>
          Umfassendes Formular-Management mit React Hook Form, Zod Validierung,
          wiederverwendbaren Komponenten und Auto-Save Funktionalität.
        </p>
      </div>

      <TabView>
        <TabPanel header="Login Form">
          <LoginFormExample />
        </TabPanel>

        <TabPanel header="Solar Calculator (Auto-Save)">
          <SolarCalculatorFormExample />
        </TabPanel>

        <TabPanel header="Project Form">
          <ProjectFormExample />
        </TabPanel>

        <TabPanel header="Customer Form">
          <CustomerFormExample />
        </TabPanel>
      </TabView>

      <Card title="Features" className="features-card">
        <ul>
          <li>✅ React Hook Form Integration</li>
          <li>✅ Zod Schema Validation</li>
          <li>✅ Wiederverwendbare Form-Komponenten</li>
          <li>✅ Auto-Save Funktionalität</li>
          <li>✅ Fehlerbehandlung mit Toast-Benachrichtigungen</li>
          <li>✅ Deutsche Fehlermeldungen</li>
          <li>✅ Responsive Design</li>
          <li>✅ TypeScript Type Safety</li>
          <li>✅ PrimeReact UI-Komponenten</li>
          <li>✅ Alle Feldtypen: Text, Number, Textarea, Dropdown, MultiSelect, Date, Checkbox, Radio, Slider, Password</li>
        </ul>
      </Card>
    </div>
  );
}

export default FormManagementDemo;
