/**
 * Modern Project Wizard Page with shadcn/ui
 * 
 * Multi-step project creation wizard for PV/WP projects
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { ProjectWizard as ProjectWizardComponent, ProjectWizardData } from '../components/wizard';
import api from '../services/api';

const ProjectWizardModern: React.FC = () => {
  const navigate = useNavigate();

  const handleComplete = async (data: ProjectWizardData) => {
    try {
      const projectData = {
        system_type: data.systemType,
        
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
        
        energy: {
          annual_electricity_consumption: data.annualElectricityConsumption,
          annual_heating_consumption: data.annualHeatingConsumption,
          is_new_building: data.isNewBuilding,
          feed_in_type: data.feedInType,
          customer_type: data.customerType
        },
        
        needs: {
          wants_wallbox: data.wantsWallbox,
          prioritize_amortization: data.prioritizeAmortization,
          wants_battery_storage: data.wantsBatteryStorage,
          additional_wishes: data.additionalWishes
        },
        
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

      const response = await api.post('/api/v1/projects', projectData);
      
      toast.success('Projekt erstellt', {
        description: 'Das Projekt wurde erfolgreich angelegt',
      });

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
      toast.error('Fehler', {
        description: error.response?.data?.error?.message || 'Das Projekt konnte nicht erstellt werden',
      });
    }
  };

  const handleCancel = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        <ProjectWizardComponent
          onComplete={handleComplete}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
};

export default ProjectWizardModern;
