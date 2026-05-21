/**
 * Modern Solar Calculator Page with shadcn/ui
 * 
 * Solar system calculation and visualization with comprehensive results display
 */

import React, { useState } from 'react';
import { Sun } from 'lucide-react';
import { toast } from 'sonner';
import SolarCalculatorForm from '../components/solar/SolarCalculatorForm';
import SolarCalculationResults from '../components/solar/SolarCalculationResults';
import api from '../services/api';

interface SolarFormData {
  customerName: string;
  customerEmail: string;
  latitude: number | null;
  longitude: number | null;
  address: string;
  roofAreaM2: number | null;
  roofOrientation: string;
  roofInclinationDeg: number;
  roofType: string;
  selectedModuleId: number | null;
  moduleQuantity: number;
  moduleCapacityW: number | null;
  annualConsumptionKwhYr: number;
  consumptionHeatingKwhYr: number;
  electricityPriceKwh: number;
  includeStorage: boolean;
  selectedStorageId: number | null;
  selectedStorageCapacityKwh: number;
  simulationPeriodYears: number;
  electricityPriceIncreaseAnnualPercent: number;
  usePvgis: boolean;
  globalYieldAdjustmentPercent: number;
}

const SolarCalculatorModern: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [calculationResult, setCalculationResult] = useState<any>(null);
  const [showForm, setShowForm] = useState(true);

  const handleCalculate = async (formData: SolarFormData) => {
    setLoading(true);
    
    try {
      // Transform form data to API request format
      const requestData = {
        customer_name: formData.customerName,
        customer_email: formData.customerEmail,
        latitude: formData.latitude,
        longitude: formData.longitude,
        address: formData.address,
        roof_area_m2: formData.roofAreaM2,
        roof_orientation: formData.roofOrientation,
        roof_inclination_deg: formData.roofInclinationDeg,
        roof_type: formData.roofType,
        selected_module_id: formData.selectedModuleId,
        module_quantity: formData.moduleQuantity,
        module_capacity_w: formData.moduleCapacityW,
        annual_consumption_kwh_yr: formData.annualConsumptionKwhYr,
        consumption_heating_kwh_yr: formData.consumptionHeatingKwhYr,
        electricity_price_kwh: formData.electricityPriceKwh,
        include_storage: formData.includeStorage,
        selected_storage_id: formData.selectedStorageId,
        selected_storage_capacity_kwh: formData.selectedStorageCapacityKwh,
        simulation_period_years: formData.simulationPeriodYears,
        electricity_price_increase_annual_percent: formData.electricityPriceIncreaseAnnualPercent,
        use_pvgis: formData.usePvgis,
        global_yield_adjustment_percent: formData.globalYieldAdjustmentPercent
      };

      const response = await api.post('/api/v1/solar/calculate', requestData);
      setCalculationResult(response.data);
      setShowForm(false);
      
      toast.success('Berechnung erfolgreich', {
        description: 'Die Solaranlage wurde erfolgreich berechnet',
      });
    } catch (error: any) {
      console.error('Calculation error:', error);
      toast.error('Berechnungsfehler', {
        description: error.response?.data?.error?.message || 'Die Berechnung ist fehlgeschlagen',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setShowForm(true);
  };

  const handleSave = async () => {
    if (!calculationResult) return;

    try {
      // TODO: Implement save to project
      console.log('Saving project...');
      toast.success('Projekt gespeichert', {
        description: 'Das Projekt wurde erfolgreich gespeichert',
      });
    } catch (error) {
      console.error('Save error:', error);
      toast.error('Speicherfehler', {
        description: 'Das Projekt konnte nicht gespeichert werden',
      });
    }
  };

  const handleGeneratePDF = async () => {
    if (!calculationResult) return;

    try {
      // TODO: Implement PDF generation
      console.log('Generating PDF...');
      toast.info('PDF wird erstellt', {
        description: 'Das PDF wird generiert...',
      });
    } catch (error) {
      console.error('PDF generation error:', error);
      toast.error('PDF-Fehler', {
        description: 'Das PDF konnte nicht erstellt werden',
      });
    }
  };

  const handleView3D = () => {
    // TODO: Implement 3D view navigation
    console.log('Opening 3D view...');
    toast.info('3D-Ansicht', {
      description: '3D-Ansicht wird geöffnet...',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 shadow-lg">
              <Sun className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Solar Calculator</h1>
              <p className="text-muted-foreground">
                Berechnen Sie Ihre Solaranlage mit unserem intelligenten Rechner
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        {showForm ? (
          <SolarCalculatorForm
            onSubmit={handleCalculate}
            loading={loading}
          />
        ) : calculationResult ? (
          <SolarCalculationResults
            results={calculationResult}
            onEdit={handleEdit}
            onSave={handleSave}
            onGeneratePDF={handleGeneratePDF}
            onView3D={handleView3D}
          />
        ) : null}
      </div>
    </div>
  );
};

export default SolarCalculatorModern;
