/**
 * User Management Page
 * 
 * Main page for user management with tabs for users, roles, and activity logs
 */

import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import UserList from '../components/admin/UserList';
import UserForm from '../components/admin/UserForm';
import UserActivityLog from '../components/admin/UserActivityLog';
import UserSettings from '../components/admin/UserSettings';
import './UserManagement.css';

interface User {
  id?: number;
  username: string;
  email: string;
  password?: string;
  first_name: string;
  last_name: string;
  role: string;
  status: string;
  phone?: string;
  department?: string;
}

const UserManagement: React.FC = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [formVisible, setFormVisible] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleCreateUser = () => {
    setSelectedUser(null);
    setFormVisible(true);
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setFormVisible(true);
  };

  const handleViewUser = (user: User) => {
    // TODO: Implement user detail view
    console.log('View user:', user);
  };

  const handleFormSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const usersHeader = (
    <div className="tab-header">
      <h2>User Management</h2>
      <Button
        label="Create User"
        icon="pi pi-plus"
        onClick={handleCreateUser}
        className="p-button-success"
      />
    </div>
  );

  return (
    <div className="user-management">
      <Card className="management-card">
        <TabView activeIndex={activeIndex} onTabChange={(e) => setActiveIndex(e.index)}>
          <TabPanel header="Users" leftIcon="pi pi-users">
            {usersHeader}
            <UserList
              onEdit={handleEditUser}
              onView={handleViewUser}
              refreshTrigger={refreshTrigger}
            />
          </TabPanel>

          <TabPanel header="Activity Logs" leftIcon="pi pi-history">
            <h2>Activity Logs</h2>
            <UserActivityLog />
          </TabPanel>

          <TabPanel header="Settings" leftIcon="pi pi-cog">
            <UserSettings />
          </TabPanel>
        </TabView>
      </Card>

      <UserForm
        visible={formVisible}
        user={selectedUser}
        onHide={() => setFormVisible(false)}
        onSuccess={handleFormSuccess}
      />
    </div>
  );
};

export default UserManagement;
