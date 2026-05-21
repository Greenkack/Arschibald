// System Configuration Manager Component

import React, { useState, useEffect } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { InputTextarea } from 'primereact/inputtextarea';
import { Checkbox } from 'primereact/checkbox';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { FileUpload } from 'primereact/fileupload';
import { Toolbar } from 'primereact/toolbar';
import { Tag } from 'primereact/tag';
import api from '../../services/api';
import './SystemConfigurationManager.css';

interface SystemConfig {
  id: number;
  key: string;
  value: string;
  value_type: string;
  category: string;
  description?: string;
  is_sensitive: boolean;
  is_readonly: boolean;
  created_at: string;
  updated_at: string;
}

interface ModuleConfig {
  id: number;
  module_name: string;
  key: string;
  value: string;
  value_type: string;
  description?: string;
  is_enabled: boolean;
  validation_rules?: any;
  default_value?: string;
  created_at: string;
  updated_at: string;
}

interface ConfigTemplate {
  id: number;
  name: string;
  description?: string;
  template_data: any;
  is_system: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const SystemConfigurationManager: React.FC = () => {
  const [systemConfigs, setSystemConfigs] = useState<SystemConfig[]>([]);
  const [moduleConfigs, setModuleConfigs] = useState<ModuleConfig[]>([]);
  const [templates, setTemplates] = useState<ConfigTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<SystemConfig | ModuleConfig | null>(null);
  const [showDialog, setShowDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [activeTab, setActiveTab] = useState(0);
  const toast = React.useRef<Toast>(null);

  const valueTypes = [
    { label: 'String', value: 'string' },
    { label: 'Number', value: 'number' },
    { label: 'Boolean', value: 'boolean' },
    { label: 'JSON', value: 'json' }
  ];

  const categories = [
    { label: 'General', value: 'general' },
    { label: 'Security', value: 'security' },
    { label: 'Database', value: 'database' },
    { label: 'Email', value: 'email' },
    { label: 'Backup', value: 'backup' },
    { label: 'Logging', value: 'logging' },
    { label: 'Performance', value: 'performance' },
    { label: 'UI', value: 'ui' },
    { label: 'API', value: 'api' }
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sysRes, modRes, tempRes] = await Promise.all([
        api.get('/api/v1/system-config/system'),
        api.get('/api/v1/system-config/module'),
        api.get('/api/v1/system-config/template')
      ]);
      
      setSystemConfigs(sysRes.data);
      setModuleConfigs(modRes.data);
      setTemplates(tempRes.data);
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load configuration data'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setSelectedConfig(null);
    setDialogMode('create');
    setShowDialog(true);
  };

  const handleEdit = (config: SystemConfig | ModuleConfig) => {
    setSelectedConfig(config);
    setDialogMode('edit');
    setShowDialog(true);
  };

  const handleDelete = (config: SystemConfig | ModuleConfig) => {
    confirmDialog({
      message: `Are you sure you want to delete this configuration?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          const endpoint = 'module_name' in config 
            ? `/api/v1/system-config/module/${config.id}`
            : `/api/v1/system-config/system/${config.id}`;
          
          await api.delete(endpoint);
          
          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Configuration deleted successfully'
          });
          
          loadData();
        } catch (error) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete configuration'
          });
        }
      }
    });
  };

  const handleSave = async (formData: any) => {
    try {
      if (dialogMode === 'create') {
        const endpoint = activeTab === 0 
          ? '/api/v1/system-config/system'
          : '/api/v1/system-config/module';
        
        await api.post(endpoint, formData);
        
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Configuration created successfully'
        });
      } else {
        const endpoint = activeTab === 0
          ? `/api/v1/system-config/system/${selectedConfig?.id}`
          : `/api/v1/system-config/module/${selectedConfig?.id}`;
        
        await api.put(endpoint, formData);
        
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Configuration updated successfully'
        });
      }
      
      setShowDialog(false);
      loadData();
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to save configuration'
      });
    }
  };

  const handleExport = async () => {
    try {
      const response = await api.get('/api/v1/system-config/export', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `config-export-${new Date().toISOString()}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Configuration exported successfully'
      });
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to export configuration'
      });
    }
  };

  const handleImport = async (event: any) => {
    const file = event.files[0];
    
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      
      const response = await api.post('/api/v1/system-config/import', data);
      
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: `Imported: ${response.data.imported}, Updated: ${response.data.updated}, Failed: ${response.data.failed}`
      });
      
      loadData();
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to import configuration'
      });
    }
  };

  const handleApplyTemplate = async (templateId: number) => {
    confirmDialog({
      message: 'Are you sure you want to apply this template? This will update existing configurations.',
      header: 'Confirm Apply Template',
      icon: 'pi pi-question-circle',
      accept: async () => {
        try {
          const response = await api.post(`/api/v1/system-config/template/${templateId}/apply`);
          
          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: `Applied: ${response.data.applied.length}, Failed: ${response.data.failed.length}`
          });
          
          loadData();
        } catch (error) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to apply template'
          });
        }
      }
    });
  };

  const categoryBodyTemplate = (rowData: SystemConfig) => {
    return <Tag value={rowData.category} severity="info" />;
  };

  const valueTypeBodyTemplate = (rowData: SystemConfig | ModuleConfig) => {
    return <Tag value={rowData.value_type} />;
  };

  const sensitiveBodyTemplate = (rowData: SystemConfig) => {
    return rowData.is_sensitive ? <i className="pi pi-lock" /> : null;
  };

  const readonlyBodyTemplate = (rowData: SystemConfig) => {
    return rowData.is_readonly ? <i className="pi pi-ban" /> : null;
  };

  const enabledBodyTemplate = (rowData: ModuleConfig) => {
    return rowData.is_enabled ? 
      <Tag value="Enabled" severity="success" /> : 
      <Tag value="Disabled" severity="danger" />;
  };

  const actionsBodyTemplate = (rowData: SystemConfig | ModuleConfig) => {
    const isReadonly = 'is_readonly' in rowData && rowData.is_readonly;
    
    return (
      <div className="flex gap-2">
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-text"
          onClick={() => handleEdit(rowData)}
          disabled={isReadonly}
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => handleDelete(rowData)}
          disabled={isReadonly}
        />
      </div>
    );
  };

  const templateActionsBodyTemplate = (rowData: ConfigTemplate) => {
    return (
      <div className="flex gap-2">
        <Button
          label="Apply"
          icon="pi pi-check"
          className="p-button-sm"
          onClick={() => handleApplyTemplate(rowData.id)}
          disabled={!rowData.is_active}
        />
      </div>
    );
  };

  const leftToolbarTemplate = () => {
    return (
      <div className="flex gap-2">
        <Button
          label="New"
          icon="pi pi-plus"
          className="p-button-success"
          onClick={handleCreate}
        />
        <Button
          label="Export"
          icon="pi pi-download"
          className="p-button-help"
          onClick={handleExport}
        />
      </div>
    );
  };

  const rightToolbarTemplate = () => {
    return (
      <FileUpload
        mode="basic"
        name="config"
        accept=".json"
        maxFileSize={1000000}
        onSelect={handleImport}
        auto
        chooseLabel="Import"
        className="p-button-outlined"
      />
    );
  };

  return (
    <div className="system-configuration-manager">
      <Toast ref={toast} />
      <ConfirmDialog />
      
      <div className="card">
        <h2>System Configuration Management</h2>
        
        <Toolbar left={leftToolbarTemplate} right={rightToolbarTemplate} className="mb-4" />
        
        <TabView activeIndex={activeTab} onTabChange={(e) => setActiveTab(e.index)}>
          <TabPanel header="System Configuration">
            <DataTable
              value={systemConfigs}
              loading={loading}
              paginator
              rows={10}
              rowsPerPageOptions={[10, 25, 50]}
              dataKey="id"
              filterDisplay="row"
              emptyMessage="No system configurations found"
            >
              <Column field="key" header="Key" sortable filter />
              <Column field="value" header="Value" sortable />
              <Column field="value_type" header="Type" body={valueTypeBodyTemplate} sortable />
              <Column field="category" header="Category" body={categoryBodyTemplate} sortable filter />
              <Column field="description" header="Description" />
              <Column header="Sensitive" body={sensitiveBodyTemplate} style={{ width: '100px' }} />
              <Column header="Readonly" body={readonlyBodyTemplate} style={{ width: '100px' }} />
              <Column header="Actions" body={actionsBodyTemplate} style={{ width: '150px' }} />
            </DataTable>
          </TabPanel>
          
          <TabPanel header="Module Configuration">
            <DataTable
              value={moduleConfigs}
              loading={loading}
              paginator
              rows={10}
              rowsPerPageOptions={[10, 25, 50]}
              dataKey="id"
              filterDisplay="row"
              emptyMessage="No module configurations found"
            >
              <Column field="module_name" header="Module" sortable filter />
              <Column field="key" header="Key" sortable filter />
              <Column field="value" header="Value" sortable />
              <Column field="value_type" header="Type" body={valueTypeBodyTemplate} sortable />
              <Column field="description" header="Description" />
              <Column header="Status" body={enabledBodyTemplate} sortable />
              <Column header="Actions" body={actionsBodyTemplate} style={{ width: '150px' }} />
            </DataTable>
          </TabPanel>
          
          <TabPanel header="Templates">
            <DataTable
              value={templates}
              loading={loading}
              paginator
              rows={10}
              rowsPerPageOptions={[10, 25, 50]}
              dataKey="id"
              emptyMessage="No templates found"
            >
              <Column field="name" header="Name" sortable />
              <Column field="description" header="Description" />
              <Column 
                field="is_system" 
                header="System" 
                body={(rowData) => rowData.is_system ? <Tag value="System" severity="warning" /> : null}
              />
              <Column 
                field="is_active" 
                header="Status" 
                body={(rowData) => rowData.is_active ? 
                  <Tag value="Active" severity="success" /> : 
                  <Tag value="Inactive" severity="danger" />
                }
              />
              <Column header="Actions" body={templateActionsBodyTemplate} style={{ width: '150px' }} />
            </DataTable>
          </TabPanel>
        </TabView>
      </div>
      
      <ConfigurationDialog
        visible={showDialog}
        mode={dialogMode}
        configType={activeTab === 0 ? 'system' : 'module'}
        config={selectedConfig}
        valueTypes={valueTypes}
        categories={categories}
        onHide={() => setShowDialog(false)}
        onSave={handleSave}
      />
    </div>
  );
};

// Configuration Dialog Component
interface ConfigurationDialogProps {
  visible: boolean;
  mode: 'create' | 'edit';
  configType: 'system' | 'module';
  config: SystemConfig | ModuleConfig | null;
  valueTypes: any[];
  categories: any[];
  onHide: () => void;
  onSave: (data: any) => void;
}

const ConfigurationDialog: React.FC<ConfigurationDialogProps> = ({
  visible,
  mode,
  configType,
  config,
  valueTypes,
  categories,
  onHide,
  onSave
}) => {
  const [formData, setFormData] = useState<any>({});

  useEffect(() => {
    if (config) {
      setFormData(config);
    } else {
      setFormData({
        key: '',
        value: '',
        value_type: 'string',
        category: configType === 'system' ? 'general' : undefined,
        module_name: configType === 'module' ? '' : undefined,
        description: '',
        is_sensitive: false,
        is_readonly: false,
        is_enabled: true
      });
    }
  }, [config, configType]);

  const handleSubmit = () => {
    onSave(formData);
  };

  return (
    <Dialog
      visible={visible}
      style={{ width: '600px' }}
      header={`${mode === 'create' ? 'Create' : 'Edit'} ${configType === 'system' ? 'System' : 'Module'} Configuration`}
      modal
      onHide={onHide}
      footer={
        <div>
          <Button label="Cancel" icon="pi pi-times" onClick={onHide} className="p-button-text" />
          <Button label="Save" icon="pi pi-check" onClick={handleSubmit} />
        </div>
      }
    >
      <div className="flex flex-column gap-3">
        {configType === 'module' && (
          <div className="field">
            <label htmlFor="module_name">Module Name</label>
            <InputText
              id="module_name"
              value={formData.module_name || ''}
              onChange={(e) => setFormData({ ...formData, module_name: e.target.value })}
              className="w-full"
              disabled={mode === 'edit'}
            />
          </div>
        )}
        
        <div className="field">
          <label htmlFor="key">Key</label>
          <InputText
            id="key"
            value={formData.key || ''}
            onChange={(e) => setFormData({ ...formData, key: e.target.value })}
            className="w-full"
            disabled={mode === 'edit'}
          />
        </div>
        
        <div className="field">
          <label htmlFor="value">Value</label>
          <InputText
            id="value"
            value={formData.value || ''}
            onChange={(e) => setFormData({ ...formData, value: e.target.value })}
            className="w-full"
          />
        </div>
        
        <div className="field">
          <label htmlFor="value_type">Value Type</label>
          <Dropdown
            id="value_type"
            value={formData.value_type}
            options={valueTypes}
            onChange={(e) => setFormData({ ...formData, value_type: e.value })}
            className="w-full"
          />
        </div>
        
        {configType === 'system' && (
          <div className="field">
            <label htmlFor="category">Category</label>
            <Dropdown
              id="category"
              value={formData.category}
              options={categories}
              onChange={(e) => setFormData({ ...formData, category: e.value })}
              className="w-full"
            />
          </div>
        )}
        
        <div className="field">
          <label htmlFor="description">Description</label>
          <InputTextarea
            id="description"
            value={formData.description || ''}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
            className="w-full"
          />
        </div>
        
        {configType === 'system' && (
          <>
            <div className="field-checkbox">
              <Checkbox
                inputId="is_sensitive"
                checked={formData.is_sensitive || false}
                onChange={(e) => setFormData({ ...formData, is_sensitive: e.checked })}
              />
              <label htmlFor="is_sensitive">Sensitive</label>
            </div>
            
            <div className="field-checkbox">
              <Checkbox
                inputId="is_readonly"
                checked={formData.is_readonly || false}
                onChange={(e) => setFormData({ ...formData, is_readonly: e.checked })}
              />
              <label htmlFor="is_readonly">Read-only</label>
            </div>
          </>
        )}
        
        {configType === 'module' && (
          <div className="field-checkbox">
            <Checkbox
              inputId="is_enabled"
              checked={formData.is_enabled !== false}
              onChange={(e) => setFormData({ ...formData, is_enabled: e.checked })}
            />
            <label htmlFor="is_enabled">Enabled</label>
          </div>
        )}
      </div>
    </Dialog>
  );
};
