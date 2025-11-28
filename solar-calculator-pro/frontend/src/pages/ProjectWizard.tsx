/**
 * Project Wizard Page
 * 
 * Multi-step project creation wizard for PV/WP projects
 * Based on funktionen.txt "Projekt- und Bedarfsanalyse"
 */

import React, { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Toast } from 'primereact/toast';
import { ProjectWizard as ProjectWizardComponent, ProjectWizardData } from '../components/wizard';
import api from '../services/api';
import './ProjectWizard.css';

const ProjectWizardPage: React.FC = () => {
  const navigate = useNavigate();
  const toast = useRef<Toast>(null);

  const handleComplete = async (data: ProjectWizardData) => {
    try {
      // Transform wizard data to API format
      const projectData = {
        // System configuration
        system_type: data.systemType,
        
        // Customer data
        customer: {
          salutation: data.salutation,
          title: data.title,
          first_name: data.firstName,
          last_name: data.lastName,
          street: data.street,
          house_number: data.houseNumber,
          postal_code: data.postalCode,
          city: data.city,
          bundesland: data.bundesland,
          email: data.email,
          phone_fixed: data.phoneFixed,
          phone_mobile: data.phoneMobile,
          notes: data.notes
        },
        
        // Building data
        building: {
          year: data.buildingYear,
          type: data.buildingType,
          height: data.buildingHeight,
          roof_type: data.roofType,
          roof_material: data.roofMaterial,
          roof_inclination: data.roofInclination,
          roof_orientation: data.roofOrientation,
          roof_area: data.roofArea
        },
        
        // Energy demand
        energy: {
          annual_electricity_consumption: data.annualElectricityConsumption,
          annual_heating_consumption: data.annualHeatingConsumption,
          is_new_building: data.isNewBuilding,
          feed_in_type: data.feedInType,
          customer_type: data.customerType
        },
        
        // Customer needs
        needs: {
          wants_wallbox: data.wantsWallbox,
          prioritize_amortization: data.prioritizeAmortization,
          wants_battery_storage: data.wantsBatteryStorage,
          additional_wishes: data.additionalWishes
        },
        
        // Additional options
        options: {
          wants_financing: data.wantsFinancing,
          down_payment: data.downPayment,
          loan_term: data.loanTerm,
          interest_rate: data.interestRate,
          discount_percent: data.discountPercent,
          discount_fixed: data.discountFixed,
          surcharge_percent: data.surchargePercent,
          surcharge_fixed: data.surchargeFixed,
          wants_maintenance_contract: data.wantsMaintenanceContract,
          payment_terms: data.paymentTerms
        }
      };

      // Save project to backend
      const response = await api.post('/api/v1/projects', projectData);
      
      toast.current?.show({
        severity: 'success',
        summary: 'Projekt erstellt',
        detail: 'Das Projekt wurde erfolgreich angelegt',
        life: 3000
      });

      // Navigate to appropriate calculator based on system type
      setTimeout(() => {
        if (data.systemType === 'pv') {
          navigate('/solar-calculator', { state: { projectData: response.data } });
        } else if (data.systemType === 'wp') {
          navigate('/heat-pump', { state: { projectData: response.data } });
        } else {
          navigate('/combined-system', { state: { projectData: response.data } });
        }
      }, 1000);

    } catch (error: any) {
      console.error('Error creating project:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: error.response?.data?.error?.message || 'Das Projekt konnte nicht erstellt werden',
        life: 5000
      });
    }
  };

  const handleCancel = () => {
    navigate('/dashboard');
  };

  return (
    <div className="project-wizard-page">
      <Toast ref={toast} />
      <ProjectWizardComponent
        onComplete={handleComplete}
        onCancel={handleCancel}
      />
    </div>
  );
};

export default ProjectWizardPage;
