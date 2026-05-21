/**
 * Settings Page
 * 
 * User settings and preferences including profile and password management
 */

import React from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import Profile from './Profile';
import { PasswordChangeForm } from '@components/PasswordChangeForm';
import './Settings.css';

const Settings: React.FC = () => {
  return (
    <div className="settings-container">
      <div className="settings-header">
        <h1>Settings</h1>
        <p className="settings-subtitle">Manage your account settings and preferences</p>
      </div>

      <TabView className="settings-tabs">
        <TabPanel header="Profile" leftIcon="pi pi-user">
          <Profile />
        </TabPanel>

        <TabPanel header="Security" leftIcon="pi pi-shield">
          <div className="settings-security">
            <PasswordChangeForm />
          </div>
        </TabPanel>

        <TabPanel header="Preferences" leftIcon="pi pi-cog">
          <div className="settings-preferences">
            <p>Application preferences will be implemented here.</p>
          </div>
        </TabPanel>

        <TabPanel header="Notifications" leftIcon="pi pi-bell">
          <div className="settings-notifications">
            <p>Notification settings will be implemented here.</p>
          </div>
        </TabPanel>
      </TabView>
    </div>
  );
};

export default Settings;
