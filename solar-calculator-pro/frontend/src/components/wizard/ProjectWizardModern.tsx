/**
 * Multi-Step Project Wizard Component (Modern - shadcn/ui)
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/components/ui/use-toast';
import { Home, ArrowLeft, ArrowRight, Check, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

// Step Components
import SystemTypeStepModern from './steps/SystemTypeStepModern';
import CustomerDataStepModern from './steps/CustomerDataStepModern';
import BuildingDataStepModern from './steps/BuildingDataStepModern';
import EnergyDemandStepModern from './steps/EnergyDemandStepModern';
import CustomerNeedsStepModern from './steps/CustomerNeedsStepModern';
import AdditionalOptionsStepModern from './steps/AdditionalOptionsStepModern';

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
  systemType: 'pv',
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
  buildingYear: null,
  roofType: 'satteldach',
  roofMaterial: 'ziegel',
  roofInclination: 30,
  roofOrientation: 'süd',
  roofArea: null,
  buildingHeight: null,
  buildingType: 'einfamilienhaus',
  annualElectricityConsumption: null,
  annualHeatingConsumption: null,
  isNewBuilding: false,
  feedInType: 'partial',
  customerType: 'private',
  wantsWallbox: false,
  prioritizeAmortization: false,
  wantsBatteryStorage: false,
  additionalWishes: '',
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

const ProjectWizardModern: React.FC<ProjectWizardProps> = ({
  onComplete,
  onCancel,
  initialData
}) => {
  const { toast } = useToast();
  const [activeStep, setActiveStep] = useState(0);
  const [wizardData, setWizardData] = useState<ProjectWizardData>({
    ...defaultWizardData,
    ...initialData
  });
  const [stepValidation, setStepValidation] = useState<boolean[]>([true, false, false, false, false, false]);

  // Step definitions
  const steps = [
    { label: 'Anlagenmodus', icon: '⚙️' },
    { label: 'Kundendaten', icon: '👤' },
    { label: 'Gebäudedaten', icon: '🏠' },
    { label: 'Energiebedarf', icon: '⚡' },
    { label: 'Bedürfnisse', icon: '❤️' },
    { label: 'Zusatzoptionen', icon: '➕' }
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
      toast({
        title: 'Validierung',
        description: 'Bitte füllen Sie alle Pflichtfelder aus',
        variant: 'destructive'
      });
      return;
    }

    const newValidation = [...stepValidation];
    newValidation[activeStep] = true;
    setStepValidation(newValidation);

    if (activeStep < steps.length - 1) {
      setActiveStep(activeStep + 1);
    }
  }, [activeStep, validateStep, stepValidation, steps.length, toast]);

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
      toast({
        title: 'Validierung',
        description: 'Bitte füllen Sie alle Pflichtfelder aus',
        variant: 'destructive'
      });
      return;
    }

    // Validate all steps
    for (let i = 0; i < steps.length; i++) {
      if (!validateStep(i)) {
        toast({
          title: 'Unvollständig',
          description: `Bitte überprüfen Sie Schritt ${i + 1}: ${steps[i].label}`,
          variant: 'destructive'
        });
        setActiveStep(i);
        return;
      }
    }

    onComplete(wizardData);
  }, [activeStep, validateStep, steps, wizardData, onComplete, toast]);

  // Calculate progress
  const progress = ((activeStep + 1) / steps.length) * 100;

  // Render current step content
  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return <SystemTypeStepModern data={wizardData} onUpdate={updateData} />;
      case 1:
        return <CustomerDataStepModern data={wizardData} onUpdate={updateData} />;
      case 2:
        return <BuildingDataStepModern data={wizardData} onUpdate={updateData} />;
      case 3:
        return <EnergyDemandStepModern data={wizardData} onUpdate={updateData} />;
      case 4:
        return <CustomerNeedsStepModern data={wizardData} onUpdate={updateData} />;
      case 5:
        return <AdditionalOptionsStepModern data={wizardData} onUpdate={updateData} />;
      default:
        return null;
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6 p-4">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <Home className="h-6 w-6" />
            Projekt & Bedarfsanalyse
          </CardTitle>
          <CardDescription>
            Erfassen Sie alle Basisinformationen für Ihr PV/WP-Projekt
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Progress value={progress} className="h-2" />
            <p className="text-sm text-muted-foreground text-center">
              Schritt {activeStep + 1} von {steps.length}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Steps Navigation */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <React.Fragment key={index}>
                <button
                  onClick={() => {
                    if (index <= activeStep || stepValidation[index - 1]) {
                      setActiveStep(index);
                    }
                  }}
                  disabled={index > activeStep && !stepValidation[index - 1]}
                  className={cn(
                    'flex flex-col items-center gap-2 transition-colors',
                    index === activeStep && 'text-primary',
                    index < activeStep && 'text-green-600',
                    index > activeStep && !stepValidation[index - 1] && 'text-muted-foreground opacity-50'
                  )}
                >
                  <div className={cn(
                    'h-10 w-10 rounded-full flex items-center justify-center text-lg border-2 transition-colors',
                    index === activeStep && 'border-primary bg-primary/10',
                    index < activeStep && 'border-green-600 bg-green-50 dark:bg-green-950',
                    index > activeStep && 'border-muted-foreground/30'
                  )}>
                    {index < activeStep ? <CheckCircle2 className="h-5 w-5 text-green-600" /> : step.icon}
                  </div>
                  <span className="text-xs font-medium hidden md:block">{step.label}</span>
                </button>
                {index < steps.length - 1 && (
                  <div className={cn(
                    'flex-1 h-0.5 mx-2',
                    index < activeStep ? 'bg-green-600' : 'bg-muted-foreground/30'
                  )} />
                )}
              </React.Fragment>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Step Content */}
      <Card>
        <CardContent className="pt-6">
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Navigation Buttons */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={goToMainMenu}
              className="gap-2"
            >
              <Home className="h-4 w-4" />
              Hauptmenü
            </Button>
            
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={goToPreviousStep}
                disabled={activeStep === 0}
                className="gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Zurück
              </Button>
              
              {activeStep < steps.length - 1 ? (
                <Button
                  onClick={goToNextStep}
                  className="gap-2"
                >
                  Weiter
                  <ArrowRight className="h-4 w-4" />
                </Button>
              ) : (
                <Button
                  onClick={handleComplete}
                  className="gap-2 bg-green-600 hover:bg-green-700"
                >
                  <Check className="h-4 w-4" />
                  Projekt erstellen
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProjectWizardModern;
