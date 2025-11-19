/**
 * Admin Page
 * 
 * System administration and settings
 */

import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Card } from 'primereact/card';
import UserManagement from './UserManagement';
import SystemSettings from '@components/admin/SystemSettings';
import './Admin.css';

const Admin: React.FC = () => {
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <div className="admin">
      <h1>Admin Panel</h1>
      <Card className="admin-card">
        <TabView activeIndex={activeIndex} onTabChange={(e) => setActiveIndex(e.index)}>
          <TabPanel header="User Management" leftIcon="pi pi-users">
            <UserManagement />
          </TabPanel>

          <TabPanel header="System Settings" leftIcon="pi pi-cog">
            <SystemSettings />
          </TabPanel>

          <TabPanel header="Database Management" leftIcon="pi pi-database">
            <div className="coming-soon">
              <i className="pi pi-database" style={{ fontSize: '3rem', color: 'var(--text-color-secondary)' }}></i>
              <h3>Database Management</h3>
              <p>Database tools and utilities will be available here.</p>
            </div>
          </TabPanel>
        </TabView>
      </Card>
    </div>
  );
};

export default Admin;
