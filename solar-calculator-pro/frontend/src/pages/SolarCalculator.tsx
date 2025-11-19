/**
 * Solar Calculator Page
 * 
 * Solar system calculation and visualization with comprehensive results display
 */

import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { Toast } from 'primereact/toast';
import { useRef } from 'react';
import SolarCalculatorForm from '../components/solar/SolarCalculatorForm';
import SolarCalculationResults from '../components/solar/SolarCalculationResults';
import api from '../services/api';
import './SolarCalculator.css';

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

const SolarCalculator: React.FC = () => {
  const toast = useRef<Toast>(null);
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
      
      toast.current?.show({
        severity: 'success',
        summary: 'Berechnung erfolgreich',
        detail: 'Die Solaranlage wurde erfolgreich berechnet',
        life: 3000
      });
    } catch (error: any) {
      console.error('Calculation error:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Berechnungsfehler',
        detail: error.response?.data?.error?.message || 'Die Berechnung ist fehlgeschlagen',
        life: 5000
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
      toast.current?.show({
        severity: 'success',
        summary: 'Projekt gespeichert',
        detail: 'Das Projekt wurde erfolgreich gespeichert',
        life: 3000
      });
    } catch (error) {
      console.error('Save error:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Speicherfehler',
        detail: 'Das Projekt konnte nicht gespeichert werden',
        life: 5000
      });
    }
  };

  const handleGeneratePDF = async () => {
    if (!calculationResult) return;

    try {
      // TODO: Implement PDF generation
      console.log('Generating PDF...');
      toast.current?.show({
        severity: 'info',
        summary: 'PDF wird erstellt',
        detail: 'Das PDF wird generiert...',
        life: 3000
      });
    } catch (error) {
      console.error('PDF generation error:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'PDF-Fehler',
        detail: 'Das PDF konnte nicht erstellt werden',
        life: 5000
      });
    }
  };

  const handleView3D = () => {
    // TODO: Implement 3D view navigation
    console.log('Opening 3D view...');
    toast.current?.show({
      severity: 'info',
      summary: '3D-Ansicht',
      detail: '3D-Ansicht wird geöffnet...',
      life: 3000
    });
  };

  return (
    <div className="solar-calculator-page">
      <Toast ref={toast} />
      
      <div className="page-header">
        <h1>☀️ Solar Calculator</h1>
        <p>Berechnen Sie Ihre Solaranlage mit unserem intelligenten Rechner</p>
      </div>

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
  );
};

export default SolarCalculator;
