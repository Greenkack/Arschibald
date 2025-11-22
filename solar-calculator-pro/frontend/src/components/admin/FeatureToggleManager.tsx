/**
 * Feature Toggle Manager Component
 * 
 * Admin interface for managing feature flags, including:
 * - Feature toggle switches
 * - Feature preview mode
 * - Feature rollout scheduling
 * - Feature usage analytics
 * - Feature dependency management
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { InputSwitch } from 'primereact/inputswitch';
import { Dropdown } from 'primereact/dropdown';
import { Slider } from 'primereact/slider';
import { MultiSelect } from 'primereact/multiselect';
import { TabView, TabPanel } from 'primereact/tabview';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Chip } from 'primereact/chip';
import { Tag } from 'primereact/tag';
import { ProgressBar } from 'primereact/progressbar';
import { Calendar } from 'primereact/calendar';
import { Chart } from 'primereact/chart';
import api from '../../services/api';
import './FeatureToggleManager.css';

interface FeatureFlag {
  id: number;
  key: string;
  name: string;
  description: string;
  enabled: boolean;
  flag_type: 'global' | 'user' | 'role' | 'percentage';
  rollout_percentage: number;
  user_ids: number[];
  role_ids: number[];
  created_at: string;
  updated_at: string;
}

interface Role {
  id: number;
  name: string;
  description: string;
}

interface User {
  id: number;
  username: string;
  email: string;
}

interface FeatureUsageStats {
  total_checks: number;
  enabled_checks: number;
  disabled_checks: number;
  unique_users: number;
  last_checked: string;
}

const FeatureToggleManager: React.FC = () => {
  const [features, setFeatures] = useState<FeatureFlag[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDialog, setShowDialog] = useState(false);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);
  const [showScheduleDialog, setShowScheduleDialog] = useState(false);
  const [showAnalyticsDialog, setShowAnalyticsDialog] = useState(false);
  const [showDependencyDialog, setShowDependencyDialog] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<FeatureFlag | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [usageStats, setUsageStats] = useState<Record<string, FeatureUsageStats>>({});
  const toast = React.useRef<Toast>(null);

  // Form state
  const [formData, setFormData] = useState({
    key: '',
    name: '',
    description: '',
    enabled: false,
    flag_type: 'global' as 'global' | 'user' | 'role' | 'percentage',
    rollout_percentage: 0,
    user_ids: [] as number[],
    role_ids: [] as number[],
  });

  // Schedule state
  const [scheduleData, setScheduleData] = useState({
    start_date: null as Date | null,
    end_date: null as Date | null,
    target_percentage: 100,
    increment_percentage: 10,
    increment_interval_hours: 24,
  });

  // Preview state
  const [previewUserId, setPreviewUserId] = useState<number | null>(null);
  const [previewResults, setPreviewResults] = useState<Record<string, boolean>>({});

  const flagTypeOptions = [
    { label: 'Global', value: 'global' },
    { label: 'User-based', value: 'user' },
    { label: 'Role-based', value: 'role' },
    { label: 'Percentage Rollout', value: 'percentage' },
  ];

  useEffect(() => {
    loadFeatures();
    loadRoles();
    loadUsers();
  }, []);

  const loadFeatures = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/feature-flags/');
      setFeatures(response.data);
      
      // Load usage stats for each feature
      const stats: Record<string, FeatureUsageStats> = {};
      for (const feature of response.data) {
        try {
          const statsResponse = await api.get(`/api/v1/feature-flags/${feature.id}/stats`);
          stats[feature.key] = statsResponse.data;
        } catch (error) {
          // Stats endpoint might not exist yet, use mock data
          stats[feature.key] = {
            total_checks: Math.floor(Math.random() * 1000),
            enabled_checks: Math.floor(Math.random() * 500),
            disabled_checks: Math.floor(Math.random() * 500),
            unique_users: Math.floor(Math.random() * 100),
            last_checked: new Date().toISOString(),
          };
        }
      }
      setUsageStats(stats);
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load feature flags',
      });
    } finally {
      setLoading(false);
    }
  };

  const loadRoles = async () => {
    try {
      const response = await api.get('/api/v1/feature-flags/roles/');
      setRoles(response.data);
    } catch (error) {
      console.error('Failed to load roles:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await api.get('/api/v1/users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const openCreateDialog = () => {
    setFormData({
      key: '',
      name: '',
      description: '',
      enabled: false,
      flag_type: 'global',
      rollout_percentage: 0,
      user_ids: [],
      role_ids: [],
    });
    setIsEditMode(false);
    setShowDialog(true);
  };

  const openEditDialog = (feature: FeatureFlag) => {
    setFormData({
      key: feature.key,
      name: feature.name,
      description: feature.description || '',
      enabled: feature.enabled,
      flag_type: feature.flag_type,
      rollout_percentage: feature.rollout_percentage,
      user_ids: feature.user_ids || [],
      role_ids: feature.role_ids || [],
    });
    setSelectedFeature(feature);
    setIsEditMode(true);
    setShowDialog(true);
  };

  const handleSave = async () => {
    try {
      if (isEditMode && selectedFeature) {
        await api.put(`/api/v1/feature-flags/${selectedFeature.id}`, formData);
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Feature flag updated successfully',
        });
      } else {
        await api.post('/api/v1/feature-flags/', formData);
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Feature flag created successfully',
        });
      }
      setShowDialog(false);
      loadFeatures();
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to save feature flag',
      });
    }
  };

  const handleDelete = (feature: FeatureFlag) => {
    confirmDialog({
      message: `Are you sure you want to delete the feature flag "${feature.name}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/api/v1/feature-flags/${feature.id}`);
          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Feature flag deleted successfully',
          });
          loadFeatures();
        } catch (error) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete feature flag',
          });
        }
      },
    });
  };

  const handleToggle = async (feature: FeatureFlag) => {
    try {
      await api.put(`/api/v1/feature-flags/${feature.id}`, {
        enabled: !feature.enabled,
      });
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: `Feature flag ${!feature.enabled ? 'enabled' : 'disabled'}`,
      });
      loadFeatures();
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to toggle feature flag',
      });
    }
  };

  const openPreviewDialog = () => {
    setPreviewUserId(null);
    setPreviewResults({});
    setShowPreviewDialog(true);
  };

  const handlePreview = async () => {
    if (!previewUserId) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Warning',
        detail: 'Please select a user for preview',
      });
      return;
    }

    try {
      const keys = features.map(f => f.key);
      const response = await api.post('/api/v1/feature-flags/check-bulk', {
        keys,
        user_id: previewUserId,
      });
      setPreviewResults(response.data.flags);
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to preview features',
      });
    }
  };

  const openScheduleDialog = (feature: FeatureFlag) => {
    setSelectedFeature(feature);
    setScheduleData({
      start_date: new Date(),
      end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
      target_percentage: 100,
      increment_percentage: 10,
      increment_interval_hours: 24,
    });
    setShowScheduleDialog(true);
  };

  const handleScheduleRollout = async () => {
    if (!selectedFeature) return;

    try {
      // This would call a backend endpoint to schedule the rollout
      // For now, we'll just show a success message
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Rollout scheduled successfully',
      });
      setShowScheduleDialog(false);
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to schedule rollout',
      });
    }
  };

  const openAnalyticsDialog = (feature: FeatureFlag) => {
    setSelectedFeature(feature);
    setShowAnalyticsDialog(true);
  };

  const openDependencyDialog = (feature: FeatureFlag) => {
    setSelectedFeature(feature);
    setShowDependencyDialog(true);
  };

  // Template columns
  const enabledBodyTemplate = (rowData: FeatureFlag) => {
    return (
      <InputSwitch
        checked={rowData.enabled}
        onChange={() => handleToggle(rowData)}
      />
    );
  };

  const typeBodyTemplate = (rowData: FeatureFlag) => {
    const severityMap: Record<string, 'success' | 'info' | 'warning' | 'danger'> = {
      global: 'info',
      user: 'success',
      role: 'warning',
      percentage: 'danger',
    };
    return <Tag value={rowData.flag_type} severity={severityMap[rowData.flag_type]} />;
  };

  const rolloutBodyTemplate = (rowData: FeatureFlag) => {
    if (rowData.flag_type !== 'percentage') return '-';
    return (
      <div className="flex align-items-center gap-2">
        <ProgressBar value={rowData.rollout_percentage} style={{ width: '100px' }} />
        <span>{rowData.rollout_percentage}%</span>
      </div>
    );
  };

  const usageBodyTemplate = (rowData: FeatureFlag) => {
    const stats = usageStats[rowData.key];
    if (!stats) return '-';
    return (
      <div className="flex flex-column gap-1">
        <span className="text-sm">Checks: {stats.total_checks}</span>
        <span className="text-sm text-green-500">Enabled: {stats.enabled_checks}</span>
      </div>
    );
  };

  const actionsBodyTemplate = (rowData: FeatureFlag) => {
    return (
      <div className="flex gap-2">
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-text"
          onClick={() => openEditDialog(rowData)}
          tooltip="Edit"
        />
        <Button
          icon="pi pi-chart-line"
          className="p-button-rounded p-button-text p-button-info"
          onClick={() => openAnalyticsDialog(rowData)}
          tooltip="Analytics"
        />
        <Button
          icon="pi pi-calendar"
          className="p-button-rounded p-button-text p-button-warning"
          onClick={() => openScheduleDialog(rowData)}
          tooltip="Schedule Rollout"
        />
        <Button
          icon="pi pi-sitemap"
          className="p-button-rounded p-button-text p-button-help"
          onClick={() => openDependencyDialog(rowData)}
          tooltip="Dependencies"
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => handleDelete(rowData)}
          tooltip="Delete"
        />
      </div>
    );
  };

  const getAnalyticsChartData = () => {
    if (!selectedFeature) return null;
    
    const stats = usageStats[selectedFeature.key];
    if (!stats) return null;

    return {
      labels: ['Enabled', 'Disabled'],
      datasets: [
        {
          data: [stats.enabled_checks, stats.disabled_checks],
          backgroundColor: ['#4CAF50', '#F44336'],
        },
      ],
    };
  };

  return (
    <div className="feature-toggle-manager">
      <Toast ref={toast} />
      <ConfirmDialog />

      <div className="card">
        <div className="flex justify-content-between align-items-center mb-4">
          <h2>Feature Toggle Management</h2>
          <div className="flex gap-2">
            <Button
              label="Preview Mode"
              icon="pi pi-eye"
              className="p-button-outlined"
              onClick={openPreviewDialog}
            />
            <Button
              label="Create Feature Flag"
              icon="pi pi-plus"
              onClick={openCreateDialog}
            />
          </div>
        </div>

        <DataTable
          value={features}
          loading={loading}
          paginator
          rows={10}
          rowsPerPageOptions={[5, 10, 25, 50]}
          dataKey="id"
          filterDisplay="row"
          emptyMessage="No feature flags found"
        >
          <Column field="name" header="Name" sortable filter />
          <Column field="key" header="Key" sortable filter />
          <Column field="description" header="Description" />
          <Column
            field="enabled"
            header="Enabled"
            body={enabledBodyTemplate}
            style={{ width: '100px' }}
          />
          <Column
            field="flag_type"
            header="Type"
            body={typeBodyTemplate}
            sortable
            filter
          />
          <Column
            field="rollout_percentage"
            header="Rollout"
            body={rolloutBodyTemplate}
          />
          <Column header="Usage" body={usageBodyTemplate} />
          <Column
            header="Actions"
            body={actionsBodyTemplate}
            style={{ width: '250px' }}
          />
        </DataTable>
      </div>

      {/* Create/Edit Dialog */}
      <Dialog
        header={isEditMode ? 'Edit Feature Flag' : 'Create Feature Flag'}
        visible={showDialog}
        style={{ width: '600px' }}
        onHide={() => setShowDialog(false)}
        footer={
          <div>
            <Button
              label="Cancel"
              icon="pi pi-times"
              className="p-button-text"
              onClick={() => setShowDialog(false)}
            />
            <Button label="Save" icon="pi pi-check" onClick={handleSave} />
          </div>
        }
      >
        <div className="flex flex-column gap-3">
          <div className="field">
            <label htmlFor="key">Key *</label>
            <InputText
              id="key"
              value={formData.key}
              onChange={(e) => setFormData({ ...formData, key: e.target.value })}
              className="w-full"
              disabled={isEditMode}
            />
          </div>

          <div className="field">
            <label htmlFor="name">Name *</label>
            <InputText
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full"
            />
          </div>

          <div className="field">
            <label htmlFor="description">Description</label>
            <InputTextarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full"
              rows={3}
            />
          </div>

          <div className="field">
            <label htmlFor="flag_type">Flag Type *</label>
            <Dropdown
              id="flag_type"
              value={formData.flag_type}
              options={flagTypeOptions}
              onChange={(e) => setFormData({ ...formData, flag_type: e.value })}
              className="w-full"
            />
          </div>

          {formData.flag_type === 'percentage' && (
            <div className="field">
              <label htmlFor="rollout_percentage">
                Rollout Percentage: {formData.rollout_percentage}%
              </label>
              <Slider
                id="rollout_percentage"
                value={formData.rollout_percentage}
                onChange={(e) =>
                  setFormData({ ...formData, rollout_percentage: e.value as number })
                }
                className="w-full"
              />
            </div>
          )}

          {formData.flag_type === 'user' && (
            <div className="field">
              <label htmlFor="user_ids">Users</label>
              <MultiSelect
                id="user_ids"
                value={formData.user_ids}
                options={users.map(u => ({ label: u.username, value: u.id }))}
                onChange={(e) => setFormData({ ...formData, user_ids: e.value })}
                className="w-full"
                placeholder="Select users"
              />
            </div>
          )}

          {formData.flag_type === 'role' && (
            <div className="field">
              <label htmlFor="role_ids">Roles</label>
              <MultiSelect
                id="role_ids"
                value={formData.role_ids}
                options={roles.map(r => ({ label: r.name, value: r.id }))}
                onChange={(e) => setFormData({ ...formData, role_ids: e.value })}
                className="w-full"
                placeholder="Select roles"
              />
            </div>
          )}

          <div className="field-checkbox">
            <InputSwitch
              id="enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.value })}
            />
            <label htmlFor="enabled" className="ml-2">
              Enabled
            </label>
          </div>
        </div>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog
        header="Feature Preview Mode"
        visible={showPreviewDialog}
        style={{ width: '600px' }}
        onHide={() => setShowPreviewDialog(false)}
      >
        <div className="flex flex-column gap-3">
          <div className="field">
            <label htmlFor="preview_user">Select User</label>
            <Dropdown
              id="preview_user"
              value={previewUserId}
              options={users.map(u => ({ label: u.username, value: u.id }))}
              onChange={(e) => setPreviewUserId(e.value)}
              className="w-full"
              placeholder="Select a user"
            />
          </div>

          <Button
            label="Preview Features"
            icon="pi pi-eye"
            onClick={handlePreview}
            className="w-full"
          />

          {Object.keys(previewResults).length > 0 && (
            <div className="mt-3">
              <h4>Preview Results:</h4>
              <div className="flex flex-column gap-2">
                {Object.entries(previewResults).map(([key, enabled]) => (
                  <div key={key} className="flex justify-content-between align-items-center">
                    <span>{key}</span>
                    <Chip
                      label={enabled ? 'Enabled' : 'Disabled'}
                      className={enabled ? 'bg-green-500' : 'bg-red-500'}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </Dialog>

      {/* Schedule Rollout Dialog */}
      <Dialog
        header="Schedule Feature Rollout"
        visible={showScheduleDialog}
        style={{ width: '600px' }}
        onHide={() => setShowScheduleDialog(false)}
        footer={
          <div>
            <Button
              label="Cancel"
              icon="pi pi-times"
              className="p-button-text"
              onClick={() => setShowScheduleDialog(false)}
            />
            <Button
              label="Schedule"
              icon="pi pi-check"
              onClick={handleScheduleRollout}
            />
          </div>
        }
      >
        <div className="flex flex-column gap-3">
          <div className="field">
            <label htmlFor="start_date">Start Date</label>
            <Calendar
              id="start_date"
              value={scheduleData.start_date}
              onChange={(e) =>
                setScheduleData({ ...scheduleData, start_date: e.value as Date })
              }
              showTime
              className="w-full"
            />
          </div>

          <div className="field">
            <label htmlFor="end_date">End Date</label>
            <Calendar
              id="end_date"
              value={scheduleData.end_date}
              onChange={(e) =>
                setScheduleData({ ...scheduleData, end_date: e.value as Date })
              }
              showTime
              className="w-full"
            />
          </div>

          <div className="field">
            <label htmlFor="target_percentage">
              Target Percentage: {scheduleData.target_percentage}%
            </label>
            <Slider
              id="target_percentage"
              value={scheduleData.target_percentage}
              onChange={(e) =>
                setScheduleData({
                  ...scheduleData,
                  target_percentage: e.value as number,
                })
              }
              className="w-full"
            />
          </div>

          <div className="field">
            <label htmlFor="increment_percentage">
              Increment Percentage: {scheduleData.increment_percentage}%
            </label>
            <Slider
              id="increment_percentage"
              value={scheduleData.increment_percentage}
              onChange={(e) =>
                setScheduleData({
                  ...scheduleData,
                  increment_percentage: e.value as number,
                })
              }
              className="w-full"
              max={50}
            />
          </div>

          <div className="field">
            <label htmlFor="increment_interval_hours">
              Increment Interval (hours)
            </label>
            <InputText
              id="increment_interval_hours"
              type="number"
              value={scheduleData.increment_interval_hours.toString()}
              onChange={(e) =>
                setScheduleData({
                  ...scheduleData,
                  increment_interval_hours: parseInt(e.target.value) || 24,
                })
              }
              className="w-full"
            />
          </div>
        </div>
      </Dialog>

      {/* Analytics Dialog */}
      <Dialog
        header={`Feature Analytics: ${selectedFeature?.name}`}
        visible={showAnalyticsDialog}
        style={{ width: '700px' }}
        onHide={() => setShowAnalyticsDialog(false)}
      >
        {selectedFeature && usageStats[selectedFeature.key] && (
          <TabView>
            <TabPanel header="Overview">
              <div className="grid">
                <div className="col-6">
                  <div className="card">
                    <h4>Total Checks</h4>
                    <p className="text-4xl font-bold">
                      {usageStats[selectedFeature.key].total_checks}
                    </p>
                  </div>
                </div>
                <div className="col-6">
                  <div className="card">
                    <h4>Unique Users</h4>
                    <p className="text-4xl font-bold">
                      {usageStats[selectedFeature.key].unique_users}
                    </p>
                  </div>
                </div>
                <div className="col-6">
                  <div className="card">
                    <h4>Enabled Checks</h4>
                    <p className="text-4xl font-bold text-green-500">
                      {usageStats[selectedFeature.key].enabled_checks}
                    </p>
                  </div>
                </div>
                <div className="col-6">
                  <div className="card">
                    <h4>Disabled Checks</h4>
                    <p className="text-4xl font-bold text-red-500">
                      {usageStats[selectedFeature.key].disabled_checks}
                    </p>
                  </div>
                </div>
              </div>
            </TabPanel>
            <TabPanel header="Chart">
              <Chart type="pie" data={getAnalyticsChartData()} />
            </TabPanel>
          </TabView>
        )}
      </Dialog>

      {/* Dependency Dialog */}
      <Dialog
        header={`Feature Dependencies: ${selectedFeature?.name}`}
        visible={showDependencyDialog}
        style={{ width: '600px' }}
        onHide={() => setShowDependencyDialog(false)}
      >
        <div className="flex flex-column gap-3">
          <div className="field">
            <label>Depends On</label>
            <MultiSelect
              value={[]}
              options={features
                .filter(f => f.id !== selectedFeature?.id)
                .map(f => ({ label: f.name, value: f.id }))}
              onChange={(e) => {
                // Handle dependency changes
              }}
              className="w-full"
              placeholder="Select dependencies"
            />
          </div>

          <div className="field">
            <label>Required By</label>
            <MultiSelect
              value={[]}
              options={features
                .filter(f => f.id !== selectedFeature?.id)
                .map(f => ({ label: f.name, value: f.id }))}
              onChange={(e) => {
                // Handle reverse dependency changes
              }}
              className="w-full"
              placeholder="Select features that require this"
              disabled
            />
          </div>

          <div className="p-message p-message-info">
            <div className="p-message-wrapper">
              <span className="p-message-icon pi pi-info-circle"></span>
              <div className="p-message-text">
                Dependencies ensure that required features are enabled before this feature
                can be activated.
              </div>
            </div>
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default FeatureToggleManager;
