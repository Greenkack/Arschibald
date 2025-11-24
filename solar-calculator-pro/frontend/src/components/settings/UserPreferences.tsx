// frontend/src/components/settings/UserPreferences.tsx

import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { InputNumber } from 'primereact/inputnumber';
import { InputSwitch } from 'primereact/inputswitch';
import { Dropdown } from 'primereact/dropdown';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Toast } from 'primereact/toast';
import { FileUpload } from 'primereact/fileupload';
import { usePreferences } from '../../hooks/usePreferences';
import './UserPreferences.css';

export const UserPreferences: React.FC = () => {
  const {
    preferences,
    loading,
    error,
    getPreference,
    setPreference,
    resetCategory,
    resetAll,
    exportPreferences,
    importPreferences,
  } = usePreferences();

  const [activeIndex, setActiveIndex] = useState(0);
  const toast = React.useRef<Toast>(null);

  const handlePreferenceChange = async (category: string, key: string, value: any) => {
    try {
      await setPreference(category, key, value);
      toast.current?.show({
        severity: 'success',
        summary: 'Saved',
        detail: 'Preference updated successfully',
        life: 3000,
      });
    } catch (err) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to update preference',
        life: 3000,
      });
    }
  };

  const handleResetCategory = (category: string) => {
    confirmDialog({
      message: `Are you sure you want to reset all ${category} preferences to defaults?`,
      header: 'Confirm Reset',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await resetCategory(category);
          toast.current?.show({
            severity: 'success',
            summary: 'Reset',
            detail: `${category} preferences reset to defaults`,
            life: 3000,
          });
        } catch (err) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to reset preferences',
            life: 3000,
          });
        }
      },
    });
  };

  const handleResetAll = () => {
    confirmDialog({
      message: 'Are you sure you want to reset ALL preferences to defaults? This cannot be undone.',
      header: 'Confirm Reset All',
      icon: 'pi pi-exclamation-triangle',
      acceptClassName: 'p-button-danger',
      accept: async () => {
        try {
          await resetAll();
          toast.current?.show({
            severity: 'success',
            summary: 'Reset',
            detail: 'All preferences reset to defaults',
            life: 3000,
          });
        } catch (err) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to reset preferences',
            life: 3000,
          });
        }
      },
    });
  };

  const handleExport = async () => {
    try {
      const data = await exportPreferences();
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `preferences_${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);

      toast.current?.show({
        severity: 'success',
        summary: 'Exported',
        detail: 'Preferences exported successfully',
        life: 3000,
      });
    } catch (err) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to export preferences',
        life: 3000,
      });
    }
  };

  const handleImport = async (event: any) => {
    const file = event.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      await importPreferences(text, true);
      
      toast.current?.show({
        severity: 'success',
        summary: 'Imported',
        detail: 'Preferences imported successfully',
        life: 3000,
      });
    } catch (err) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to import preferences',
        life: 3000,
      });
    }
  };

  if (loading) {
    return <div className="p-d-flex p-jc-center p-ai-center" style={{ height: '400px' }}>
      <i className="pi pi-spin pi-spinner" style={{ fontSize: '3rem' }}></i>
    </div>;
  }

  return (
    <div className="user-preferences">
      <Toast ref={toast} />
      <ConfirmDialog />

      <div className="preferences-header">
        <h2>User Preferences</h2>
        <div className="preferences-actions">
          <Button
            label="Export"
            icon="pi pi-download"
            className="p-button-outlined"
            onClick={handleExport}
          />
          <FileUpload
            mode="basic"
            name="preferences"
            accept="application/json"
            maxFileSize={1000000}
            customUpload
            uploadHandler={handleImport}
            chooseLabel="Import"
            className="p-button-outlined"
          />
          <Button
            label="Reset All"
            icon="pi pi-refresh"
            className="p-button-danger p-button-outlined"
            onClick={handleResetAll}
          />
        </div>
      </div>

      {error && (
        <Message severity="error" text={error} className="p-mb-3" />
      )}

      <TabView activeIndex={activeIndex} onTabChange={(e) => setActiveIndex(e.index)}>
        {/* UI Preferences */}
        <TabPanel header="User Interface">
          <Card title="UI Preferences" className="preference-card">
            <div className="preference-group">
              <div className="preference-item">
                <label>Theme</label>
                <Dropdown
                  value={getPreference('ui', 'theme', 'light')}
                  options={[
                    { label: 'Light', value: 'light' },
                    { label: 'Dark', value: 'dark' },
                    { label: 'Auto', value: 'auto' },
                  ]}
                  onChange={(e) => handlePreferenceChange('ui', 'theme', e.value)}
                  placeholder="Select theme"
                />
              </div>

              <div className="preference-item">
                <label>Language</label>
                <Dropdown
                  value={getPreference('ui', 'language', 'de')}
                  options={[
                    { label: 'Deutsch', value: 'de' },
                    { label: 'English', value: 'en' },
                  ]}
                  onChange={(e) => handlePreferenceChange('ui', 'language', e.value)}
                  placeholder="Select language"
                />
              </div>

              <div className="preference-item">
                <label>Sidebar Collapsed</label>
                <InputSwitch
                  checked={getPreference('ui', 'sidebar_collapsed', false)}
                  onChange={(e) => handlePreferenceChange('ui', 'sidebar_collapsed', e.value)}
                />
              </div>

              <div className="preference-item">
                <label>Items Per Page</label>
                <InputNumber
                  value={getPreference('ui', 'items_per_page', 25)}
                  onValueChange={(e) => handlePreferenceChange('ui', 'items_per_page', e.value)}
                  min={10}
                  max={100}
                  step={5}
                />
              </div>

              <div className="preference-item">
                <label>Date Format</label>
                <Dropdown
                  value={getPreference('ui', 'date_format', 'DD.MM.YYYY')}
                  options={[
                    { label: 'DD.MM.YYYY', value: 'DD.MM.YYYY' },
                    { label: 'MM/DD/YYYY', value: 'MM/DD/YYYY' },
                    { label: 'YYYY-MM-DD', value: 'YYYY-MM-DD' },
                  ]}
                  onChange={(e) => handlePreferenceChange('ui', 'date_format', e.value)}
                />
              </div>

              <div className="preference-item">
                <label>Time Format</label>
                <Dropdown
                  value={getPreference('ui', 'time_format', 'HH:mm')}
                  options={[
                    { label: '24-hour (HH:mm)', value: 'HH:mm' },
                    { label: '12-hour (hh:mm A)', value: 'hh:mm A' },
                  ]}
                  onChange={(e) => handlePreferenceChange('ui', 'time_format', e.value)}
                />
              </div>
            </div>

            <Button
              label="Reset UI Preferences"
              icon="pi pi-refresh"
              className="p-button-sm p-button-outlined p-mt-3"
              onClick={() => handleResetCategory('ui')}
            />
          </Card>
        </TabPanel>

        {/* Calculation Preferences */}
        <TabPanel header="Calculations">
          <Card title="Calculation Preferences" className="preference-card">
            <div className="preference-group">
              <div className="preference-item">
                <label>Auto Save</label>
                <InputSwitch
                  checked={getPreference('calculation', 'auto_save', true)}
                  onChange={(e) => handlePreferenceChange('calculation', 'auto_save', e.value)}
                />
              </div>

              <div className="preference-item">
                <label>Default Location</label>
                <InputText
                  value={getPreference('calculation', 'default_location', 'Berlin')}
                  onChange={(e) => handlePreferenceChange('calculation', 'default_location', e.target.value)}
                />
              </div>

              <div className="preference-item">
                <label>Precision (Decimal Places)</label>
                <InputNumber
                  value={getPreference('calculation', 'precision', 2)}
                  onValueChange={(e) => handlePreferenceChange('calculation', 'precision', e.value)}
                  min={0}
                  max={6}
                />
              </div>

              <div className="preference-item">
                <label>Show Advanced Options</label>
                <InputSwitch
                  checked={getPreference('calculation', 'show_advanced_options', false)}
                  onChange={(e) => handlePreferenceChange('calculation', 'show_advanced_options', e.value)}
                />
              </div>
            </div>

            <Button
              label="Reset Calculation Preferences"
              icon="pi pi-refresh"
              className="p-button-sm p-button-outlined p-mt-3"
              onClick={() => handleResetCategory('calculation')}
            />
          </Card>
        </TabPanel>

        {/* PDF Preferences */}
        <TabPanel header="PDF">
          <Card title="PDF Preferences" className="preference-card">
            <div className="preference-group">
              <div className="preference-item">
                <label>Default Template</label>
                <Dropdown
                  value={getPreference('pdf', 'default_template', 'standard')}
                  options={[
                    { label: 'Standard', value: 'standard' },
                    { label: 'Extended', value: 'extended' },
                    { label: 'Minimal', value: 'minimal' },
                  ]}
                  onChange={(e) => handlePreferenceChange('pdf', 'default_template', e.value)}
                />
              </div>

              <div className="preference-item">
                <label>Auto Download</label>
                <InputSwitch
                  checked={getPreference('pdf', 'auto_download', true)}
                  onChange={(e) => handlePreferenceChange('pdf', 'auto_download', e.value)}
                />
              </div>

              <div className="preference-item">
                <label>Include Charts</label>
                <InputSwitch
                  checked={getPreference('pdf', 'include_charts', true)}
                  onChange={(e) => handlePreferenceChange('pdf', 'include_charts', e.value)}
                />
              </div>

              <div className="preference-item">
                <label>Compression Level</label>
                <Dropdown
                  value={getPreference('pdf', 'compression_level', 'medium')}
                  options={[
                    { label: 'None', value: 'none' },
                    { label: 'Low', value: 'low' },
                    { label: 'Medium', value: 'medium' },
                    { label: 'High', value: 'high' },
                  ]}
                  onChange={(e) => handlePreferenceChange('pdf', 'compression_level', e.value)}
                />
              </div>
            </div>

            <Button
              label="Reset PDF Preferences"
              icon="pi pi-refresh"
              className="p-button-sm p-button-outlined p-mt-3"
              onClick={() => handleResetCategory('pdf')}
            />
          </Card>
        </TabPanel>

        {/* Notification Preferences */}
        <TabPanel header="Notifications">
          <Card title="Notification Preferences" className="preference-card">
            <div className="preference-group">
              <div className="preference-item">
                <label>Enable Notifications</label>
                <InputSwitch
                  checked={getPreference('notifications', 'enabled', true)}
                  onChange={(e) => handlePreferenceChange('notifications', 'enabled', e.value)}
                />
              </div>

              <div className="preference-item">
                <label>Sound</label>
                <InputSwitch
                  checked={getPreference('notifications', 'sound', true)}
                  onChange={(e) => handlePreferenceChange('notifications', 'sound', e.value)}
                  disabled={!getPreference('notifications', 'enabled', true)}
                />
              </div>

              <div className="preference-item">
                <label>Desktop Notifications</label>
                <InputSwitch
                  checked={getPreference('notifications', 'desktop', true)}
                  onChange={(e) => handlePreferenceChange('notifications', 'desktop', e.value)}
                  disabled={!getPreference('notifications', 'enabled', true)}
                />
              </div>

              <div className="preference-item">
                <label>Email Notifications</label>
                <InputSwitch
                  checked={getPreference('notifications', 'email', false)}
                  onChange={(e) => handlePreferenceChange('notifications', 'email', e.value)}
                  disabled={!getPreference('notifications', 'enabled', true)}
                />
              </div>
            </div>

            <Button
              label="Reset Notification Preferences"
              icon="pi pi-refresh"
              className="p-button-sm p-button-outlined p-mt-3"
              onClick={() => handleResetCategory('notifications')}
            />
          </Card>
        </TabPanel>
      </TabView>
    </div>
  );
};
