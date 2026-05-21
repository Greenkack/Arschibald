/**
 * User Settings Component
 * 
 * Manage user preferences and settings
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Dropdown } from 'primereact/dropdown';
import { InputSwitch } from 'primereact/inputswitch';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './UserSettings.css';

interface Settings {
  theme: string;
  language: string;
  notifications_enabled: boolean;
  email_notifications: boolean;
  timezone: string;
  date_format: string;
  number_format: string;
}

const UserSettings: React.FC = () => {
  const [settings, setSettings] = useState<Settings>({
    theme: 'light',
    language: 'de',
    notifications_enabled: true,
    email_notifications: true,
    timezone: 'Europe/Berlin',
    date_format: 'DD.MM.YYYY',
    number_format: 'de-DE'
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const toast = React.useRef<Toast>(null);

  const themes = [
    { label: 'Light', value: 'light' },
    { label: 'Dark', value: 'dark' },
    { label: 'Auto', value: 'auto' }
  ];

  const languages = [
    { label: 'Deutsch', value: 'de' },
    { label: 'English', value: 'en' }
  ];

  const timezones = [
    { label: 'Europe/Berlin', value: 'Europe/Berlin' },
    { label: 'Europe/London', value: 'Europe/London' },
    { label: 'Europe/Paris', value: 'Europe/Paris' },
    { label: 'America/New_York', value: 'America/New_York' },
    { label: 'America/Los_Angeles', value: 'America/Los_Angeles' },
    { label: 'Asia/Tokyo', value: 'Asia/Tokyo' }
  ];

  const dateFormats = [
    { label: 'DD.MM.YYYY', value: 'DD.MM.YYYY' },
    { label: 'MM/DD/YYYY', value: 'MM/DD/YYYY' },
    { label: 'YYYY-MM-DD', value: 'YYYY-MM-DD' }
  ];

  const numberFormats = [
    { label: 'German (1.234,56)', value: 'de-DE' },
    { label: 'English (1,234.56)', value: 'en-US' }
  ];

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/users/me/settings');
      setSettings(response.data);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to load settings',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put('/api/v1/users/me/settings', settings);
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Settings saved successfully',
        life: 3000
      });
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to save settings',
        life: 3000
      });
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof Settings, value: any) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return <div className="loading-container">Loading settings...</div>;
  }

  return (
    <div className="user-settings">
      <Toast ref={toast} />
      
      <Card title="User Settings" className="settings-card">
        <div className="settings-section">
          <h3>Appearance</h3>
          <div className="setting-item">
            <label>Theme</label>
            <Dropdown
              value={settings.theme}
              options={themes}
              onChange={(e) => handleChange('theme', e.value)}
              placeholder="Select Theme"
            />
          </div>
        </div>

        <div className="settings-section">
          <h3>Localization</h3>
          <div className="setting-item">
            <label>Language</label>
            <Dropdown
              value={settings.language}
              options={languages}
              onChange={(e) => handleChange('language', e.value)}
              placeholder="Select Language"
            />
          </div>

          <div className="setting-item">
            <label>Timezone</label>
            <Dropdown
              value={settings.timezone}
              options={timezones}
              onChange={(e) => handleChange('timezone', e.value)}
              placeholder="Select Timezone"
            />
          </div>

          <div className="setting-item">
            <label>Date Format</label>
            <Dropdown
              value={settings.date_format}
              options={dateFormats}
              onChange={(e) => handleChange('date_format', e.value)}
              placeholder="Select Date Format"
            />
          </div>

          <div className="setting-item">
            <label>Number Format</label>
            <Dropdown
              value={settings.number_format}
              options={numberFormats}
              onChange={(e) => handleChange('number_format', e.value)}
              placeholder="Select Number Format"
            />
          </div>
        </div>

        <div className="settings-section">
          <h3>Notifications</h3>
          <div className="setting-item">
            <label>Enable Notifications</label>
            <InputSwitch
              checked={settings.notifications_enabled}
              onChange={(e) => handleChange('notifications_enabled', e.value)}
            />
          </div>

          <div className="setting-item">
            <label>Email Notifications</label>
            <InputSwitch
              checked={settings.email_notifications}
              onChange={(e) => handleChange('email_notifications', e.value)}
            />
          </div>
        </div>

        <div className="settings-actions">
          <Button
            label="Save Settings"
            icon="pi pi-check"
            onClick={handleSave}
            loading={saving}
          />
        </div>
      </Card>
    </div>
  );
};

export default UserSettings;
