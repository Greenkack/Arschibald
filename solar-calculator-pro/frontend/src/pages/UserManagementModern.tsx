/**
 * Modern User Management Page with shadcn/ui
 * 
 * Main page for user management with tabs for users, roles, and activity logs
 */

import React, { useState } from 'react';
import { Users, Plus, History, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import UserList from '../components/admin/UserList';
import UserForm from '../components/admin/UserForm';
import UserActivityLog from '../components/admin/UserActivityLog';
import UserSettings from '../components/admin/UserSettings';

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

const UserManagementModern: React.FC = () => {
  const [activeTab, setActiveTab] = useState('users');
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
    console.log('View user:', user);
  };

  const handleFormSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-cyan-600 shadow-lg">
              <Users className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">User Management</h1>
              <p className="text-muted-foreground">
                Manage users, roles, and permissions
              </p>
            </div>
          </div>
          {activeTab === 'users' && (
            <Button onClick={handleCreateUser} size="lg">
              <Plus className="mr-2 h-5 w-5" />
              Create User
            </Button>
          )}
        </div>

        {/* Main Content */}
        <Card>
          <CardContent className="p-6">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="users" className="gap-2">
                  <Users className="h-4 w-4" />
                  Users
                </TabsTrigger>
                <TabsTrigger value="activity" className="gap-2">
                  <History className="h-4 w-4" />
                  Activity Logs
                </TabsTrigger>
                <TabsTrigger value="settings" className="gap-2">
                  <Settings className="h-4 w-4" />
                  Settings
                </TabsTrigger>
              </TabsList>

              <TabsContent value="users" className="space-y-4">
                <UserList
                  onEdit={handleEditUser}
                  onView={handleViewUser}
                  refreshTrigger={refreshTrigger}
                />
              </TabsContent>

              <TabsContent value="activity" className="space-y-4">
                <UserActivityLog />
              </TabsContent>

              <TabsContent value="settings" className="space-y-4">
                <UserSettings />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <UserForm
          visible={formVisible}
          user={selectedUser}
          onHide={() => setFormVisible(false)}
          onSuccess={handleFormSuccess}
        />
      </div>
    </div>
  );
};

export default UserManagementModern;
