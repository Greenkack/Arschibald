/**
 * System Settings Component
 * 
 * Comprehensive system settings management interface
 */

import React, { useState, useEffect } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { ProgressSpinner } from 'primereact/progressspinner';
import GeneralSettings from './GeneralSettings';
import EmailConfiguration from './EmailConfiguration';
import BackupSettings from './BackupSettings';
import LoggingConfiguration from './LoggingConfiguration';
import SystemInformation from './SystemInformation';
import './SystemSettings.css';

interface SystemSettingsProps {
  onSettingsChange?: () => void;
}

const SystemSettings: React.FC<SystemSettingsProps> = ({ onSettingsChange }) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTabChange = (e: any) => {
    setActiveIndex(e.index);
    setError(null);
  };

  const handleSettingsUpdate = () => {
    if (onSettingsChange) {
      onSettingsChange();
    }
  };

  return (
    <div className="system-settings">
      <div className="system-settings-header">
        <h2>System Settings</h2>
        <p className="system-settings-subtitle">
          Configure system-wide settings, email, backups, logging, and view system information
        </p>
      </div>

      {error && (
        <Message severity="error" text={error} className="system-settings-error" />
      )}

      {loading ? (
        <div className="system-settings-loading">
          <ProgressSpinner />
          <p>Loading settings...</p>
        </div>
      ) : (
        <Card className="system-settings-card">
          <TabView 
            activeIndex={activeIndex} 
            onTabChange={handleTabChange}
            className="system-settings-tabs"
          >
            <TabPanel header="General" leftIcon="pi pi-cog">
              <GeneralSettings onUpdate={handleSettingsUpdate} />
            </TabPanel>

            <TabPanel header="Email" leftIcon="pi pi-envelope">
              <EmailConfiguration onUpdate={handleSettingsUpdate} />
            </TabPanel>

            <TabPanel header="Backup" leftIcon="pi pi-save">
              <BackupSettings onUpdate={handleSettingsUpdate} />
            </TabPanel>

            <TabPanel header="Logging" leftIcon="pi pi-file">
              <LoggingConfiguration onUpdate={handleSettingsUpdate} />
            </TabPanel>

            <TabPanel header="System Info" leftIcon="pi pi-info-circle">
              <SystemInformation />
            </TabPanel>
          </TabView>
        </Card>
      )}
    </div>
  );
};

export default SystemSettings;
