import React, { useState, useEffect } from 'react';
import { Customer } from '../packages/core/src/types/db';

interface CustomerFormProps {
  customer?: Partial<Customer>;
  mode: 'add' | 'edit';
  onSave: (customer: Omit<Customer, 'id'>) => void;
  onCancel: () => void;
  texts?: Record<string, string>;
}

export const CustomerForm: React.FC<CustomerFormProps> = ({
  customer,
  mode,
  onSave,
  onCancel,
  texts = {}
}) => {
  const [formData, setFormData] = useState<Omit<Customer, 'id'>>({
    salutation: customer?.salutation || '',
    title: customer?.title || '',
    first_name: customer?.first_name || '',
    last_name: customer?.last_name || '',
    company_name: customer?.company_name || '',
    address: customer?.address || '',
    house_number: customer?.house_number || '',
    zip_code: customer?.zip_code || '',
    city: customer?.city || '',
    state: customer?.state || '',
    region: customer?.region || '',
    email: customer?.email || '',
    phone_landline: customer?.phone_landline || '',
    phone_mobile: customer?.phone_mobile || '',
    income_tax_rate_percent: customer?.income_tax_rate_percent || 0,
    creation_date: customer?.creation_date || new Date().toISOString(),
    last_updated: new Date().toISOString()
  });

  const handleInputChange = (field: keyof Omit<Customer, 'id'>, value: any) => {
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
    <div className="customer-form-container">
      <form onSubmit={handleSubmit} className="customer-form">
        <h2>{mode === 'add' 
          ? getLabel('crm_add_new_customer_header', 'Neuen Kunden anlegen')
          : getLabel('crm_edit_customer_header', 'Kunde bearbeiten')
        }</h2>

        <div className="form-section">
          <h3>{getLabel('crm_personal_data_section', 'Persönliche Daten')}</h3>
          
          <div className="form-group">
            <label>{getLabel('salutation_label', 'Anrede')}</label>
            <select
              value={formData.salutation}
              onChange={(e) => handleInputChange('salutation', e.target.value)}
            >
              <option value="">-- Bitte auswählen --</option>
              <option value="Herr">Herr</option>
              <option value="Frau">Frau</option>
              <option value="Familie">Familie</option>
              <option value="Divers">Divers</option>
            </select>
          </div>

          <div className="form-group">
            <label>{getLabel('title_label', 'Titel')}</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              placeholder="z.B. Dr., Prof."
              title="Titel eingeben"
            />
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('first_name_label', 'Vorname')}</label>
              <input
                type="text"
                value={formData.first_name}
                onChange={(e) => handleInputChange('first_name', e.target.value)}
                required
              />
            </div>
            
            <div className="form-group flex-1">
              <label>{getLabel('last_name_label', 'Nachname')}</label>
              <input
                type="text"
                value={formData.last_name}
                onChange={(e) => handleInputChange('last_name', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>{getLabel('company_name_label', 'Firmenname (optional)')}</label>
            <input
              type="text"
              value={formData.company_name}
              onChange={(e) => handleInputChange('company_name', e.target.value)}
            />
          </div>
        </div>

        <div className="form-section">
          <h3>{getLabel('crm_address_section', 'Adresse')}</h3>
          
          <div className="form-row">
            <div className="form-group flex-3">
              <label>{getLabel('street_label', 'Straße')}</label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
              />
            </div>
            
            <div className="form-group flex-1">
              <label>{getLabel('house_number_label', 'Hausnummer')}</label>
              <input
                type="text"
                value={formData.house_number}
                onChange={(e) => handleInputChange('house_number', e.target.value)}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('zip_code_label', 'PLZ')}</label>
              <input
                type="text"
                value={formData.zip_code}
                onChange={(e) => handleInputChange('zip_code', e.target.value)}
                placeholder="PLZ eingeben"
                title="Postleitzahl"
              />
            </div>
            
            <div className="form-group flex-2">
              <label>{getLabel('city_label', 'Ort')}</label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => handleInputChange('city', e.target.value)}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('state_label', 'Bundesland')}</label>
              <input
                type="text"
                value={formData.state}
                onChange={(e) => handleInputChange('state', e.target.value)}
              />
            </div>
            
            <div className="form-group flex-1">
              <label>{getLabel('region_label', 'Region')}</label>
              <input
                type="text"
                value={formData.region}
                onChange={(e) => handleInputChange('region', e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>{getLabel('crm_contact_section', 'Kontaktdaten')}</h3>
          
          <div className="form-group">
            <label>{getLabel('email_label', 'E-Mail')}</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              title="E-Mail-Adresse eingeben"
            />
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>{getLabel('phone_landline_label', 'Telefon (Festnetz)')}</label>
              <input
                type="tel"
                value={formData.phone_landline}
                onChange={(e) => handleInputChange('phone_landline', e.target.value)}
              />
            </div>
            
            <div className="form-group flex-1">
              <label>{getLabel('phone_mobile_label', 'Telefon (Mobil)')}</label>
              <input
                type="tel"
                value={formData.phone_mobile}
                onChange={(e) => handleInputChange('phone_mobile', e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>{getLabel('crm_financial_section', 'Finanzdaten')}</h3>
          
          <div className="form-group">
            <label>{getLabel('income_tax_rate_label', 'Einkommenssteuersatz (%)')}</label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={formData.income_tax_rate_percent}
              onChange={(e) => handleInputChange('income_tax_rate_percent', parseFloat(e.target.value) || 0)}
              placeholder="z.B. 25.5"
              title="Einkommenssteuersatz in Prozent"
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={onCancel}>
            {getLabel('cancel_button', 'Abbrechen')}
          </button>
          <button type="submit" className="btn btn-primary">
            {mode === 'add' 
              ? getLabel('save_customer_button', 'Kunde speichern')
              : getLabel('update_customer_button', 'Änderungen speichern')
            }
          </button>
        </div>
      </form>
    </div>
  );
};
