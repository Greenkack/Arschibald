/**
 * General Settings Component
 * 
 * General application settings configuration
 */

import React, { useState, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { InputSwitch } from 'primereact/inputswitch';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { ProgressSpinner } from 'primereact/progressspinner';
import api from '@services/api';

interface GeneralSettingsData {
  app_name: string;
  app_description: string;
  default_language: string;
  default_currency: string;
  timezone: string;
  date_format: string;
  time_format: string;
  items_per_page: number;
  session_timeout: number;
  enable_analytics: boolean;
  enable_telemetry: boolean;
  maintenance_mode: boolean;
  updated_at: string;
}

interface GeneralSettingsProps {
  onUpdate?: () => void;
}

const GeneralSettings: React.FC<GeneralSettingsProps> = ({ onUpdate }) => {
  const [settings, setSettings] = useState<GeneralSettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ severity: 'success' | 'error'; text: string } | null>(null);

  const languageOptions = [
    { label: 'Deutsch (Deutschland)', value: 'de-DE' },
    { label: 'English (US)', value: 'en-US' },
    { label: 'English (UK)', value: 'en-GB' },
    { label: 'Français', value: 'fr-FR' },
    { label: 'Español', value: 'es-ES' },
  ];

  const currencyOptions = [
    { label: 'EUR (€)', value: 'EUR' },
    { label: 'USD ($)', value: 'USD' },
    { label: 'GBP (£)', value: 'GBP' },
    { label: 'CHF (Fr)', value: 'CHF' },
  ];

  const timezoneOptions = [
    { label: 'Europe/Berlin', value: 'Europe/Berlin' },
    { label: 'Europe/London', value: 'Europe/London' },
    { label: 'Europe/Paris', value: 'Europe/Paris' },
    { label: 'America/New_York', value: 'America/New_York' },
    { label: 'America/Los_Angeles', value: 'America/Los_Angeles' },
    { label: 'Asia/Tokyo', value: 'Asia/Tokyo' },
  ];

  const dateFormatOptions = [
    { label: 'DD.MM.YYYY', value: 'DD.MM.YYYY' },
    { label: 'MM/DD/YYYY', value: 'MM/DD/YYYY' },
    { label: 'YYYY-MM-DD', value: 'YYYY-MM-DD' },
  ];

  const timeFormatOptions = [
    { label: '24-hour (HH:mm)', value: 'HH:mm' },
    { label: '12-hour (hh:mm A)', value: 'hh:mm A' },
  ];

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/system-settings/general');
      setSettings(response.data);
    } catch (error: any) {
      setMessage({
        severity: 'error',
        text: `Failed to load settings: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;

    try {
      setSaving(true);
      setMessage(null);
      
      const response = await api.put('/api/v1/system-settings/general', settings);
      setSettings(response.data);
      
      setMessage({
        severity: 'success',
        text: 'General settings saved successfully'
      });
      
      if (onUpdate) {
        onUpdate();
      }
    } catch (error: any) {
      setMessage({
        severity: 'error',
        text: `Failed to save settings: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    loadSettings();
    setMessage(null);
  };

  if (loading) {
    return (
      <div className="settings-loading">
        <ProgressSpinner />
        <p>Loading general settings...</p>
      </div>
    );
  }

  if (!settings) {
    return <Message severity="error" text="Failed to load settings" />;
  }

  return (
    <div className="general-settings">
      {message && (
        <Message 
          severity={message.severity} 
          text={message.text} 
          className="settings-message"
        />
      )}

      <div className="settings-section">
        <h3>Application Information</h3>
        
        <div className="p-field">
          <label htmlFor="app_name">Application Name</label>
          <InputText
            id="app_name"
            value={settings.app_name}
            onChange={(e) => setSettings({ ...settings, app_name: e.target.value })}
            className="w-full"
          />
        </div>

        <div className="p-field">
          <label htmlFor="app_description">Application Description</label>
          <InputTextarea
            id="app_description"
            value={settings.app_description}
            onChange={(e) => setSettings({ ...settings, app_description: e.target.value })}
            rows={3}
            className="w-full"
          />
        </div>
      </div>

      <div className="settings-section">
        <h3>Localization</h3>
        
        <div className="p-field">
          <label htmlFor="default_language">Default Language</label>
          <Dropdown
            id="default_language"
            value={settings.default_language}
            options={languageOptions}
            onChange={(e) => setSettings({ ...settings, default_language: e.value })}
            className="w-full"
          />
        </div>

        <div className="p-field">
          <label htmlFor="default_currency">Default Currency</label>
          <Dropdown
            id="default_currency"
            value={settings.default_currency}
            options={currencyOptions}
            onChange={(e) => setSettings({ ...settings, default_currency: e.value })}
            className="w-full"
          />
        </div>

        <div className="p-field">
          <label htmlFor="timezone">Timezone</label>
          <Dropdown
            id="timezone"
            value={settings.timezone}
            options={timezoneOptions}
            onChange={(e) => setSettings({ ...settings, timezone: e.value })}
            className="w-full"
          />
        </div>

        <div className="p-field">
          <label htmlFor="date_format">Date Format</label>
          <Dropdown
            id="date_format"
            value={settings.date_format}
            options={dateFormatOptions}
            onChange={(e) => setSettings({ ...settings, date_format: e.value })}
            className="w-full"
          />
        </div>

        <div className="p-field">
          <label htmlFor="time_format">Time Format</label>
          <Dropdown
            id="time_format"
            value={settings.time_format}
            options={timeFormatOptions}
            onChange={(e) => setSettings({ ...settings, time_format: e.value })}
            className="w-full"
          />
        </div>
      </div>

      <div className="settings-section">
        <h3>User Interface</h3>
        
        <div className="p-field">
          <label htmlFor="items_per_page">Items Per Page</label>
          <InputNumber
            id="items_per_page"
            value={settings.items_per_page}
            onValueChange={(e) => setSettings({ ...settings, items_per_page: e.value || 25 })}
            min={10}
            max={100}
            className="w-full"
          />
          <small>Number of items to display per page in lists and tables</small>
        </div>

        <div className="p-field">
          <label htmlFor="session_timeout">Session Timeout (minutes)</label>
          <InputNumber
            id="session_timeout"
            value={settings.session_timeout}
            onValueChange={(e) => setSettings({ ...settings, session_timeout: e.value || 60 })}
            min={5}
            max={1440}
            className="w-full"
          />
          <small>Automatic logout after inactivity</small>
        </div>
      </div>

      <div className="settings-section">
        <h3>Features</h3>
        
        <div className="p-field-checkbox">
          <InputSwitch
            id="enable_analytics"
            checked={settings.enable_analytics}
            onChange={(e) => setSettings({ ...settings, enable_analytics: e.value })}
          />
          <label htmlFor="enable_analytics">Enable Analytics</label>
          <small>Collect anonymous usage statistics</small>
        </div>

        <div className="p-field-checkbox">
          <InputSwitch
            id="enable_telemetry"
            checked={settings.enable_telemetry}
            onChange={(e) => setSettings({ ...settings, enable_telemetry: e.value })}
          />
          <label htmlFor="enable_telemetry">Enable Telemetry</label>
          <small>Send diagnostic data to improve the application</small>
        </div>

        <div className="p-field-checkbox">
          <InputSwitch
            id="maintenance_mode"
            checked={settings.maintenance_mode}
            onChange={(e) => setSettings({ ...settings, maintenance_mode: e.value })}
          />
          <label htmlFor="maintenance_mode">Maintenance Mode</label>
          <small>Restrict access to administrators only</small>
        </div>
      </div>

      <div className="settings-actions">
        <Button
          label="Save Changes"
          icon="pi pi-check"
          onClick={handleSave}
          loading={saving}
          className="p-button-success"
        />
        <Button
          label="Reset"
          icon="pi pi-refresh"
          onClick={handleReset}
          className="p-button-secondary"
          disabled={saving}
        />
      </div>

      {settings.updated_at && (
        <div className="settings-footer">
          <small>Last updated: {new Date(settings.updated_at).toLocaleString()}</small>
        </div>
      )}
    </div>
  );
};

export default GeneralSettings;
