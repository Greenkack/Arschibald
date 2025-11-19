/**
 * State Management Demo
 * 
 * Demonstrates how to use all three stores together in a real-world scenario
 */

import React, { useEffect } from 'react';
import { useAuthStore, useUIStore, useProjectStore, type Project } from '@/store';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Dropdown } from 'primereact/dropdown';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';

/**
 * Example: Complete application flow using all stores
 */
export const StateManagementDemo: React.FC = () => {
  // Auth Store
  const { user, isAuthenticated, logout } = useAuthStore();
  
  // UI Store
  const { 
    theme, 
    setTheme, 
    sidebarCollapsed, 
    toggleSidebar,
    addNotification,
    setGlobalLoading 
  } = useUIStore();
  
  // Project Store
  const { 
    projects, 
    currentProject,
    setCurrentProject,
    addProject,
    updateProject,
    deleteProject,
    isLoading: projectsLoading 
  } = useProjectStore();

  // Load projects on mount
  useEffect(() => {
    if (isAuthenticated) {
      loadProjects();
    }
  }, [isAuthenticated]);

  /**
   * Load projects from API
   */
  const loadProjects = async () => {
    setGlobalLoading(true, 'Loading projects...');
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockProjects: Project[] = [
        {
          id: 1,
          name: 'Solar Installation - Smith Residence',
          customerName: 'John Smith',
          customerEmail: 'john@example.com',
          projectType: 'solar',
          status: 'active',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          data: { systemSize: 10.5, moduleCount: 30 }
        },
        {
          id: 2,
          name: 'Heat Pump - Johnson Home',
          customerName: 'Sarah Johnson',
          customerEmail: 'sarah@example.com',
          projectType: 'heatpump',
          status: 'draft',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          data: { heatPumpType: 'air-source', capacity: 12 }
        }
      ];
      
      // Update store
      useProjectStore.getState().setProjects(mockProjects);
      
      addNotification({
        type: 'success',
        title: 'Projects Loaded',
        message: `Successfully loaded ${mockProjects.length} projects`
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to load projects'
      });
    } finally {
      setGlobalLoading(false);
    }
  };

  /**
   * Create a new project
   */
  const handleCreateProject = async () => {
    setGlobalLoading(true, 'Creating project...');
    
    try {
      const newProject: Project = {
        id: Date.now(),
        name: 'New Project',
        customerName: 'New Customer',
        projectType: 'solar',
        status: 'draft',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        data: {}
      };
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Update store
      addProject(newProject);
      setCurrentProject(newProject);
      
      addNotification({
        type: 'success',
        title: 'Project Created',
        message: 'New project created successfully'
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to create project'
      });
    } finally {
      setGlobalLoading(false);
    }
  };

  /**
   * Update project status
   */
  const handleUpdateStatus = async (projectId: number, newStatus: Project['status']) => {
    try {
      // Optimistic update
      updateProject(projectId, { status: newStatus });
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 300));
      
      addNotification({
        type: 'success',
        title: 'Status Updated',
        message: `Project status changed to ${newStatus}`
      });
    } catch (error) {
      // Rollback on error
      const original = projects.find(p => p.id === projectId);
      if (original) {
        updateProject(projectId, { status: original.status });
      }
      
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to update project status'
      });
    }
  };

  /**
   * Delete project
   */
  const handleDeleteProject = async (projectId: number) => {
    if (!confirm('Are you sure you want to delete this project?')) {
      return;
    }
    
    setGlobalLoading(true, 'Deleting project...');
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Update store
      deleteProject(projectId);
      
      addNotification({
        type: 'success',
        title: 'Project Deleted',
        message: 'Project deleted successfully'
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to delete project'
      });
    } finally {
      setGlobalLoading(false);
    }
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    logout();
    addNotification({
      type: 'info',
      title: 'Logged Out',
      message: 'You have been logged out successfully'
    });
  };

  // Status options for dropdown
  const statusOptions = [
    { label: 'Draft', value: 'draft' },
    { label: 'Active', value: 'active' },
    { label: 'Completed', value: 'completed' },
    { label: 'Archived', value: 'archived' }
  ];

  // Theme options
  const themeOptions = [
    { label: 'Light', value: 'light' },
    { label: 'Dark', value: 'dark' },
    { label: 'Auto', value: 'auto' }
  ];

  // Status template for DataTable
  const statusBodyTemplate = (rowData: Project) => {
    return (
      <Dropdown
        value={rowData.status}
        options={statusOptions}
        onChange={(e) => handleUpdateStatus(rowData.id, e.value)}
        className="w-full"
      />
    );
  };

  // Actions template for DataTable
  const actionsBodyTemplate = (rowData: Project) => {
    return (
      <div className="flex gap-2">
        <Button
          icon="pi pi-eye"
          className="p-button-sm p-button-info"
          onClick={() => setCurrentProject(rowData)}
          tooltip="View"
        />
        <Button
          icon="pi pi-trash"
          className="p-button-sm p-button-danger"
          onClick={() => handleDeleteProject(rowData.id)}
          tooltip="Delete"
        />
      </div>
    );
  };

  if (!isAuthenticated) {
    return (
      <Card title="Not Authenticated">
        <p>Please log in to view this demo.</p>
      </Card>
    );
  }

  return (
    <div className="state-management-demo p-4">
      <h1>State Management Demo</h1>
      
      {/* User Info & Controls */}
      <Card className="mb-4">
        <div className="flex justify-content-between align-items-center">
          <div>
            <h3>Welcome, {user?.username}!</h3>
            <p className="text-sm text-gray-600">
              Email: {user?.email}
            </p>
          </div>
          
          <div className="flex gap-2 align-items-center">
            {/* Theme Selector */}
            <div className="flex align-items-center gap-2">
              <label>Theme:</label>
              <Dropdown
                value={theme}
                options={themeOptions}
                onChange={(e) => setTheme(e.value)}
              />
            </div>
            
            {/* Sidebar Toggle */}
            <Button
              icon={sidebarCollapsed ? 'pi pi-angle-right' : 'pi pi-angle-left'}
              onClick={toggleSidebar}
              tooltip={sidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            />
            
            {/* Logout */}
            <Button
              label="Logout"
              icon="pi pi-sign-out"
              className="p-button-danger"
              onClick={handleLogout}
            />
          </div>
        </div>
      </Card>

      {/* Current Project */}
      {currentProject && (
        <Card title="Current Project" className="mb-4">
          <div className="grid">
            <div className="col-12 md:col-6">
              <p><strong>Name:</strong> {currentProject.name}</p>
              <p><strong>Customer:</strong> {currentProject.customerName}</p>
              <p><strong>Type:</strong> {currentProject.projectType}</p>
            </div>
            <div className="col-12 md:col-6">
              <p><strong>Status:</strong> {currentProject.status}</p>
              <p><strong>Created:</strong> {new Date(currentProject.createdAt).toLocaleDateString()}</p>
              <p><strong>Updated:</strong> {new Date(currentProject.updatedAt).toLocaleDateString()}</p>
            </div>
          </div>
          
          <Button
            label="Clear Selection"
            icon="pi pi-times"
            className="p-button-secondary mt-3"
            onClick={() => setCurrentProject(null)}
          />
        </Card>
      )}

      {/* Projects List */}
      <Card title="Projects">
        <div className="flex justify-content-between align-items-center mb-3">
          <h3>All Projects ({projects.length})</h3>
          <div className="flex gap-2">
            <Button
              label="Refresh"
              icon="pi pi-refresh"
              onClick={loadProjects}
              loading={projectsLoading}
            />
            <Button
              label="New Project"
              icon="pi pi-plus"
              onClick={handleCreateProject}
            />
          </div>
        </div>

        <DataTable
          value={projects}
          loading={projectsLoading}
          emptyMessage="No projects found"
          paginator
          rows={10}
          rowsPerPageOptions={[5, 10, 25, 50]}
        >
          <Column field="name" header="Name" sortable />
          <Column field="customerName" header="Customer" sortable />
          <Column field="projectType" header="Type" sortable />
          <Column 
            field="status" 
            header="Status" 
            body={statusBodyTemplate}
            sortable 
          />
          <Column 
            field="createdAt" 
            header="Created" 
            body={(rowData) => new Date(rowData.createdAt).toLocaleDateString()}
            sortable 
          />
          <Column 
            header="Actions" 
            body={actionsBodyTemplate}
            style={{ width: '120px' }}
          />
        </DataTable>
      </Card>

      {/* Store State Debug Info */}
      <Card title="Store State (Debug)" className="mt-4">
        <div className="grid">
          <div className="col-12 md:col-4">
            <h4>Auth Store</h4>
            <pre className="text-sm">
              {JSON.stringify({
                isAuthenticated,
                username: user?.username,
                email: user?.email
              }, null, 2)}
            </pre>
          </div>
          
          <div className="col-12 md:col-4">
            <h4>UI Store</h4>
            <pre className="text-sm">
              {JSON.stringify({
                theme,
                sidebarCollapsed
              }, null, 2)}
            </pre>
          </div>
          
          <div className="col-12 md:col-4">
            <h4>Project Store</h4>
            <pre className="text-sm">
              {JSON.stringify({
                projectCount: projects.length,
                currentProjectId: currentProject?.id,
                isLoading: projectsLoading
              }, null, 2)}
            </pre>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default StateManagementDemo;
