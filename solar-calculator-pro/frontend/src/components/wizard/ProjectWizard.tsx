/**
 * Multi-Step Project Wizard Component
 * 
 * Implements the complete project creation workflow from funktionen.txt:
 * - Step 1: Anlagenmodus (System Type Selection)
 * - Step 2: Kundendaten (Customer Data with Address Auto-Parsing)
 * - Step 3: Gebäudedaten (Building Data)
 * - Step 4: Energiebedarfsanalyse (Energy Demand Analysis)
 * - Step 5: Kundenbedürfnisse (Customer Needs)
 * - Step 6: Zusatzoptionen (Additional Options)
 */

import React, { useState, useCallback, useRef } from 'react';
import { Steps } from 'primereact/steps';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Toast } from 'primereact/toast';
import { ProgressBar } from 'primereact/progressbar';
import { Divider } from 'primereact/divider';

// Step Components
import SystemTypeStep from './steps/SystemTypeStep';
import CustomerDataStep from './steps/CustomerDataStep';
import BuildingDataStep from './steps/BuildingDataStep';
import EnergyDemandStep from './steps/EnergyDemandStep';
import CustomerNeedsStep from './steps/CustomerNeedsStep';
import AdditionalOptionsStep from './steps/AdditionalOptionsStep';

import './ProjectWizard.css';

// Types
export interface ProjectWizardData {
  // Step 1: System Type
  systemType: 'pv' | 'wp' | 'pv_wp';
  
  // Step 2: Customer Data
  salutation: string;
  title: string;
  firstName: string;
  lastName: string;
  fullAddress: string; // For auto-parsing
  street: string;
  houseNumber: string;
  postalCode: string;
  city: string;
  bundesland: string;
  email: string;
  phoneFixed: string;
  phoneMobile: string;
  notes: string;
  
  // Step 3: Building Data
  buildingYear: number | null;
  roofType: string;
  roofMaterial: string;
  roofInclination: number;
  roofOrientation: string;
  roofArea: number | null;
  buildingHeight: number | null;
  buildingType: string;
  
  // Step 4: Energy Demand
  annualElectricityConsumption: number | null;
  annualHeatingConsumption: number | null;
  isNewBuilding: boolean;
  feedInType: 'partial' | 'full';
  customerType: 'private' | 'commercial';
  
  // Step 5: Customer Needs
  wantsWallbox: boolean;
  prioritizeAmortization: boolean;
  wantsBatteryStorage: boolean;
  additionalWishes: string;
  
  // Step 6: Additional Options
  wantsFinancing: boolean;
  downPayment: number | null;
  loanTerm: number | null;
  interestRate: number | null;
  discountPercent: number | null;
  discountFixed: number | null;
  surchargePercent: number | null;
  surchargeFixed: number | null;
  wantsMaintenanceContract: boolean;
  paymentTerms: string;
}

interface ProjectWizardProps {
  onComplete: (data: ProjectWizardData) => void;
  onCancel: () => void;
  initialData?: Partial<ProjectWizardData>;
}

const defaultWizardData: ProjectWizardData = {
  // Step 1
  systemType: 'pv',
  
  // Step 2
  salutation: '',
  title: '',
  firstName: '',
  lastName: '',
  fullAddress: '',
  street: '',
  houseNumber: '',
  postalCode: '',
  city: '',
  bundesland: '',
  email: '',
  phoneFixed: '',
  phoneMobile: '',
  notes: '',
  
  // Step 3
  buildingYear: null,
  roofType: 'satteldach',
  roofMaterial: 'ziegel',
  roofInclination: 30,
  roofOrientation: 'süd',
  roofArea: null,
  buildingHeight: null,
  buildingType: 'einfamilienhaus',
  
  // Step 4
  annualElectricityConsumption: null,
  annualHeatingConsumption: null,
  isNewBuilding: false,
  feedInType: 'partial',
  customerType: 'private',
  
  // Step 5
  wantsWallbox: false,
  prioritizeAmortization: false,
  wantsBatteryStorage: false,
  additionalWishes: '',
  
  // Step 6
  wantsFinancing: false,
  downPayment: null,
  loanTerm: null,
  interestRate: null,
  discountPercent: null,
  discountFixed: null,
  surchargePercent: null,
  surchargeFixed: null,
  wantsMaintenanceContract: false,
  paymentTerms: '50_50'
};

const ProjectWizard: React.FC<ProjectWizardProps> = ({
  onComplete,
  onCancel,
  initialData
}) => {
  const toast = useRef<Toast>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [wizardData, setWizardData] = useState<ProjectWizardData>({
    ...defaultWizardData,
    ...initialData
  });
  const [stepValidation, setStepValidation] = useState<boolean[]>([true, false, false, false, false, false]);

  // Step definitions
  const steps = [
    { label: 'Anlagenmodus', icon: 'pi pi-cog' },
    { label: 'Kundendaten', icon: 'pi pi-user' },
    { label: 'Gebäudedaten', icon: 'pi pi-home' },
    { label: 'Energiebedarf', icon: 'pi pi-bolt' },
    { label: 'Bedürfnisse', icon: 'pi pi-heart' },
    { label: 'Zusatzoptionen', icon: 'pi pi-plus-circle' }
  ];

  // Update wizard data
  const updateData = useCallback((updates: Partial<ProjectWizardData>) => {
    setWizardData(prev => ({ ...prev, ...updates }));
  }, []);

  // Validate current step
  const validateStep = useCallback((step: number): boolean => {
    switch (step) {
      case 0: // System Type
        return !!wizardData.systemType;
      
      case 1: // Customer Data
        return !!(
          wizardData.firstName &&
          wizardData.lastName &&
          (wizardData.street || wizardData.fullAddress) &&
          wizardData.postalCode &&
          wizardData.city
        );
      
      case 2: // Building Data
        return !!(
          wizardData.roofType &&
          wizardData.roofOrientation &&
          wizardData.roofArea && wizardData.roofArea > 0
        );
      
      case 3: // Energy Demand
        if (wizardData.systemType === 'pv' || wizardData.systemType === 'pv_wp') {
          if (!wizardData.annualElectricityConsumption || wizardData.annualElectricityConsumption <= 0) {
            return false;
          }
        }
        if (wizardData.systemType === 'wp' || wizardData.systemType === 'pv_wp') {
          if (!wizardData.annualHeatingConsumption || wizardData.annualHeatingConsumption <= 0) {
            return false;
          }
        }
        return true;
      
      case 4: // Customer Needs
        return true; // Optional step
      
      case 5: // Additional Options
        if (wizardData.wantsFinancing) {
          return !!(
            wizardData.loanTerm && wizardData.loanTerm > 0 &&
            wizardData.interestRate !== null && wizardData.interestRate >= 0
          );
        }
        return true;
      
      default:
        return false;
    }
  }, [wizardData]);

  // Navigation handlers
  const goToNextStep = useCallback(() => {
    if (!validateStep(activeStep)) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Validierung',
        detail: 'Bitte füllen Sie alle Pflichtfelder aus',
        life: 3000
      });
      return;
    }

    const newValidation = [...stepValidation];
    newValidation[activeStep] = true;
    setStepValidation(newValidation);

    if (activeStep < steps.length - 1) {
      setActiveStep(activeStep + 1);
    }
  }, [activeStep, validateStep, stepValidation, steps.length]);

  const goToPreviousStep = useCallback(() => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1);
    }
  }, [activeStep]);

  const goToMainMenu = useCallback(() => {
    onCancel();
  }, [onCancel]);

  const handleComplete = useCallback(() => {
    if (!validateStep(activeStep)) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Validierung',
        detail: 'Bitte füllen Sie alle Pflichtfelder aus',
        life: 3000
      });
      return;
    }

    // Validate all steps
    for (let i = 0; i < steps.length; i++) {
      if (!validateStep(i)) {
        toast.current?.show({
          severity: 'error',
          summary: 'Unvollständig',
          detail: `Bitte überprüfen Sie Schritt ${i + 1}: ${steps[i].label}`,
          life: 5000
        });
        setActiveStep(i);
        return;
      }
    }

    onComplete(wizardData);
  }, [activeStep, validateStep, steps, wizardData, onComplete]);

  // Calculate progress
  const progress = ((activeStep + 1) / steps.length) * 100;

  // Render current step content
  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <SystemTypeStep
            data={wizardData}
            onUpdate={updateData}
          />
        );
      case 1:
        return (
          <CustomerDataStep
            data={wizardData}
            onUpdate={updateData}
          />
        );
      case 2:
        return (
          <BuildingDataStep
            data={wizardData}
            onUpdate={updateData}
          />
        );
      case 3:
        return (
          <EnergyDemandStep
            data={wizardData}
            onUpdate={updateData}
          />
        );
      case 4:
        return (
          <CustomerNeedsStep
            data={wizardData}
            onUpdate={updateData}
          />
        );
      case 5:
        return (
          <AdditionalOptionsStep
            data={wizardData}
            onUpdate={updateData}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="project-wizard">
      <Toast ref={toast} />
      
      {/* Header */}
      <Card className="wizard-header-card">
        <div className="wizard-header">
          <h2>🏠 Projekt & Bedarfsanalyse</h2>
          <p>Erfassen Sie alle Basisinformationen für Ihr PV/WP-Projekt</p>
        </div>
        
        {/* Progress Bar */}
        <div className="wizard-progress">
          <ProgressBar value={progress} showValue={false} />
          <span className="progress-text">
            Schritt {activeStep + 1} von {steps.length}
          </span>
        </div>
      </Card>

      {/* Steps Navigation */}
      <Card className="wizard-steps-card">
        <Steps
          model={steps}
          activeIndex={activeStep}
          onSelect={(e) => {
            // Only allow navigation to completed steps or current step
            if (e.index <= activeStep || stepValidation[e.index - 1]) {
              setActiveStep(e.index);
            }
          }}
          readOnly={false}
        />
      </Card>

      {/* Step Content */}
      <Card className="wizard-content-card">
        <div className="step-content">
          {renderStepContent()}
        </div>
      </Card>

      {/* Navigation Buttons */}
      <Card className="wizard-navigation-card">
        <div className="wizard-navigation">
          <div className="nav-left">
            <Button
              label="Hauptmenü"
              icon="pi pi-home"
              className="p-button-text"
              onClick={goToMainMenu}
            />
          </div>
          
          <div className="nav-center">
            <Button
              label="Zurück"
              icon="pi pi-arrow-left"
              className="p-button-secondary"
              onClick={goToPreviousStep}
              disabled={activeStep === 0}
            />
          </div>
          
          <div className="nav-right">
            {activeStep < steps.length - 1 ? (
              <Button
                label="Weiter"
                icon="pi pi-arrow-right"
                iconPos="right"
                className="p-button-primary"
                onClick={goToNextStep}
              />
            ) : (
              <Button
                label="Projekt erstellen"
                icon="pi pi-check"
                iconPos="right"
                className="p-button-success"
                onClick={handleComplete}
              />
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ProjectWizard;
