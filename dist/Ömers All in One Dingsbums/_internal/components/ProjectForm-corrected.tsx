import React, { useState } from 'react';
import { Project, Customer } from '../packages/core/src/types/db';

interface ProjectFormProps {
  project?: Partial<Project>;
  customer: Customer;
  mode: 'add' | 'edit';
  onSave: (project: Omit<Project, 'id'>) => void;
  onCancel: () => void;
  texts?: Record<string, string>;
}

export const ProjectForm: React.FC<ProjectFormProps> = ({
  project,
  customer,
  mode,
  onSave,
  onCancel,
  texts = {}
}) => {
  const [formData, setFormData] = useState<Omit<Project, 'id'>>({
    customer_id: customer.id!,
    project_name: project?.project_name || '',
    project_status: project?.project_status || '',
    roof_type: project?.roof_type || '',
    roof_covering_type: project?.roof_covering_type || '',
    free_roof_area_sqm: project?.free_roof_area_sqm || 0,
    roof_orientation: project?.roof_orientation || '',
    roof_inclination_deg: project?.roof_inclination_deg || 0,
    building_height_gt_7m: project?.building_height_gt_7m || 0,
    annual_consumption_kwh: project?.annual_consumption_kwh || 0,
    costs_household_euro_mo: project?.costs_household_euro_mo || 0,
    annual_heating_kwh: project?.annual_heating_kwh || 0,
    costs_heating_euro_mo: project?.costs_heating_euro_mo || 0,
    anlage_type: project?.anlage_type || '',
    feed_in_type: project?.feed_in_type || '',
    module_quantity: project?.module_quantity || 0,
    selected_module_id: project?.selected_module_id || undefined,
    selected_inverter_id: project?.selected_inverter_id || undefined,
    include_storage: project?.include_storage || 0,
    selected_storage_id: project?.selected_storage_id || undefined,
    selected_storage_storage_power_kw: project?.selected_storage_storage_power_kw || 0,
    include_additional_components: project?.include_additional_components || 0,
    selected_wallbox_id: project?.selected_wallbox_id || undefined,
    selected_ems_id: project?.selected_ems_id || undefined,
    selected_optimizer_id: project?.selected_optimizer_id || undefined,
    selected_carport_id: project?.selected_carport_id || undefined,
    selected_notstrom_id: project?.selected_notstrom_id || undefined,
    selected_tierabwehr_id: project?.selected_tierabwehr_id || undefined,
    visualize_roof_in_pdf: project?.visualize_roof_in_pdf || 0,
    latitude: project?.latitude || undefined,
    longitude: project?.longitude || undefined,
    creation_date: project?.creation_date || new Date().toISOString(),
    last_updated: new Date().toISOString()
  });

  const handleInputChange = (field: keyof Omit<Project, 'id'>, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
      last_updated: new Date().toISOString()
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  const getLabel = (key: string, fallback: string) => texts[key] || fallback;

  return (
    <div className="project-form-container">
      <form onSubmit={handleSubmit} className="project-form">
        <h2>{mode === 'add' 
          ? getLabel('crm_add_new_project_header', 'Neues Projekt anlegen')
          : getLabel('crm_edit_project_header', 'Projekt bearbeiten')
        }</h2>

        <div className="form-section">
          <h3>{getLabel('crm_project_basic_info', 'Grunddaten')}</h3>
          
          <div className="form-group">
            <label>Kunde</label>
            <input
              type="text"
              value={`${customer.first_name} ${customer.last_name}${customer.company_name ? ` (${customer.company_name})` : ''}`}
              disabled
              title="Ausgewählter Kunde"
            />
          </div>

          <div className="form-group">
            <label>{getLabel('crm_project_name_label', 'Projektname')}</label>
            <input
              type="text"
              value={formData.project_name}
              onChange={(e) => handleInputChange('project_name', e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>{getLabel('crm_project_status_label', 'Status')}</label>
            <select
              value={formData.project_status || ''}
              onChange={(e) => handleInputChange('project_status', e.target.value)}
            >
              <option value="">-- Bitte auswählen --</option>
              <option value="Angebot">Angebot</option>
              <option value="In Planung">In Planung</option>
              <option value="Installiert">Installiert</option>
              <option value="Abgeschlossen">Abgeschlossen</option>
              <option value="Storniert">Storniert</option>
            </select>
          </div>
        </div>

        <div className="form-section">
          <h3>{getLabel('crm_project_roof_details', 'Dachdaten')}</h3>
          
          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('roof_type_label', 'Dachart')}</label>
              <select
                value={formData.roof_type || ''}
                onChange={(e) => handleInputChange('roof_type', e.target.value)}
              >
                <option value="">-- Bitte auswählen --</option>
                <option value="Satteldach">Satteldach</option>
                <option value="Flachdach">Flachdach</option>
                <option value="Sonstiges">Sonstiges</option>
              </select>
            </div>
            
            <div className="form-group flex-1">
              <label>{getLabel('roof_covering_label', 'Dachdeckungsart')}</label>
              <select
                value={formData.roof_covering_type || ''}
                onChange={(e) => handleInputChange('roof_covering_type', e.target.value)}
              >
                <option value="">-- Bitte auswählen --</option>
                <option value="Ziegel">Ziegel</option>
                <option value="Blech">Blech</option>
                <option value="Bitumen">Bitumen</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('free_roof_area_label', 'Freie Dachfläche (m²)')}</label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={formData.free_roof_area_sqm || 0}
                onChange={(e) => handleInputChange('free_roof_area_sqm', parseFloat(e.target.value) || 0)}
              />
            </div>
            
            <div className="form-group flex-1">
              <label>{getLabel('roof_orientation_label', 'Dachausrichtung')}</label>
              <select
                value={formData.roof_orientation || ''}
                onChange={(e) => handleInputChange('roof_orientation', e.target.value)}
              >
                <option value="">-- Bitte auswählen --</option>
                <option value="Süd">Süd</option>
                <option value="Ost">Ost</option>
                <option value="West">West</option>
                <option value="Nord">Nord</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('roof_inclination_label', 'Dachneigung (°)')}</label>
              <input
                type="number"
                min="0"
                max="90"
                step="1"
                value={formData.roof_inclination_deg || 0}
                onChange={(e) => handleInputChange('roof_inclination_deg', parseInt(e.target.value) || 0)}
                placeholder="Dachneigung in Grad eingeben"
              />
            </div>

            <div className="form-group flex-1">
              <label>{getLabel('building_height_label', 'Gebäudehöhe > 7m (1=Ja, 0=Nein)')}</label>
              <select
                value={formData.building_height_gt_7m || 0}
                onChange={(e) => handleInputChange('building_height_gt_7m', parseInt(e.target.value) || 0)}
              >
                <option value={0}>Nein</option>
                <option value={1}>Ja</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>{getLabel('crm_project_consumption', 'Verbrauchsdaten')}</h3>
          
          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('annual_consumption_label', 'Jahresverbrauch Haushalt (kWh)')}</label>
              <input
                type="number"
                min="0"
                value={formData.annual_consumption_kwh || 0}
                onChange={(e) => handleInputChange('annual_consumption_kwh', parseInt(e.target.value) || 0)}
              />
            </div>
            
            <div className="form-group flex-1">
              <label>{getLabel('costs_household_label', 'Stromkosten Haushalt (€/Monat)')}</label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={formData.costs_household_euro_mo || 0}
                onChange={(e) => handleInputChange('costs_household_euro_mo', parseFloat(e.target.value) || 0)}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('annual_heating_label', 'Jahresverbrauch Heizung (kWh)')}</label>
              <input
                type="number"
                min="0"
                value={formData.annual_heating_kwh || 0}
                onChange={(e) => handleInputChange('annual_heating_kwh', parseInt(e.target.value) || 0)}
              />
            </div>
            
            <div className="form-group flex-1">
              <label>{getLabel('costs_heating_label', 'Heizkosten (€/Monat)')}</label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={formData.costs_heating_euro_mo || 0}
                onChange={(e) => handleInputChange('costs_heating_euro_mo', parseFloat(e.target.value) || 0)}
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>{getLabel('crm_project_system_config', 'Anlagenkonfiguration')}</h3>
          
          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('anlage_type_label', 'Anlagentyp')}</label>
              <input
                type="text"
                value={formData.anlage_type || ''}
                onChange={(e) => handleInputChange('anlage_type', e.target.value)}
                placeholder="Anlagentyp eingeben"
              />
            </div>
            
            <div className="form-group flex-1">
              <label>{getLabel('feed_in_type_label', 'Einspeiseart')}</label>
              <input
                type="text"
                value={formData.feed_in_type || ''}
                onChange={(e) => handleInputChange('feed_in_type', e.target.value)}
                placeholder="Einspeiseart eingeben"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="module_quantity">{getLabel('module_quantity_label', 'Anzahl Module')}</label>
            <input
              id="module_quantity"
              type="number"
              min="0"
              value={formData.module_quantity || 0}
              onChange={(e) => handleInputChange('module_quantity', parseInt(e.target.value) || 0)}
              placeholder="Anzahl der Module eingeben"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>{getLabel('crm_project_components', 'Komponenten')}</h3>
          
          <div className="form-row">
            <div className="form-group flex-1">
              <label>
                <input
                  type="checkbox"
                  checked={(formData.include_storage || 0) === 1}
                  onChange={(e) => handleInputChange('include_storage', e.target.checked ? 1 : 0)}
                />
                {getLabel('include_storage_label', 'Speicher einschließen')}
              </label>
            </div>

            <div className="form-group flex-1">
              <label>
                <input
                  type="checkbox"
                  checked={(formData.include_additional_components || 0) === 1}
                  onChange={(e) => handleInputChange('include_additional_components', e.target.checked ? 1 : 0)}
                />
                {getLabel('include_additional_components_label', 'Zusatzkomponenten einschließen')}
              </label>
            </div>
          </div>

          {formData.include_storage === 1 && (
            <div className="form-group">
              <label>{getLabel('storage_power_label', 'Speicherleistung (kW)')}</label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={formData.selected_storage_storage_power_kw || 0}
                onChange={(e) => handleInputChange('selected_storage_storage_power_kw', parseFloat(e.target.value) || 0)}
              />
            </div>
          )}

          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={(formData.visualize_roof_in_pdf || 0) === 1}
                onChange={(e) => handleInputChange('visualize_roof_in_pdf', e.target.checked ? 1 : 0)}
              />
              {getLabel('visualize_roof_label', 'Dach in PDF visualisieren')}
            </label>
          </div>
        </div>

        <div className="form-section">
          <h3>{getLabel('crm_project_location', 'Standort')}</h3>
          
          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('latitude_label', 'Breitengrad')}</label>
              <input
                type="number"
                step="0.000001"
                value={formData.latitude || ''}
                onChange={(e) => handleInputChange('latitude', parseFloat(e.target.value) || undefined)}
              />
            </div>
            
            <div className="form-group flex-1">
              <label>{getLabel('longitude_label', 'Längengrad')}</label>
              <input
                type="number"
                step="0.000001"
                value={formData.longitude || ''}
                onChange={(e) => handleInputChange('longitude', parseFloat(e.target.value) || undefined)}
              />
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={onCancel}>
            {getLabel('cancel_button', 'Abbrechen')}
          </button>
          <button type="submit" className="btn btn-primary">
            {mode === 'add' 
              ? getLabel('save_project_button', 'Projekt speichern')
              : getLabel('update_project_button', 'Änderungen speichern')
            }
          </button>
        </div>
      </form>
    </div>
  );
};
