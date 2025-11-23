/**
 * Configuration Manager Component
 * 
 * Comprehensive configuration management interface with:
 * - Configuration list with search and filtering
 * - Configuration editor with validation
 * - Configuration comparison
 * - Configuration templates
 * - Import/Export functionality
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Dialog } from 'primereact/dialog';
import { TabView, TabPanel } from 'primereact/tabview';
import { Toast } from 'primereact/toast';
import { ConfirmDialog } from 'primereact/confirmdialog';
import { Toolbar } from 'primereact/toolbar';
import { Tag } from 'primereact/tag';
import { Chip } from 'primereact/chip';
import { ProgressBar } from 'primereact/progressbar';
import { FileUpload } from 'primereact/fileupload';
import './ConfigurationManager.css';

import ConfigurationEditor from './ConfigurationEditor';
import ConfigurationComparison from './ConfigurationComparison';
import ConfigurationTemplates from './ConfigurationTemplates';
import ConfigurationImportExport from './ConfigurationImportExport';

interface Configuration {
  id: number;
  key: string;
  value: string;
  value_type: string;
  description: string;
  category: string;
  namespace: string;
  version: number;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
}

interface ConfigurationSearch {
  query: string;
  namespace: string;
  category: string;
  is_active: boolean | null;
  is_system: boolean | null;
}

const ConfigurationManager: React.FC = () => {
  const [configurations, setConfigurations] = useState<Configuration[]>([]);
  const [selectedConfigurations, setSelectedConfigurations] = useState<Configuration[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalRecords, setTotalRecords] = useState(0);
  const [first, setFirst] = useState(0);
  const [rows, setRows] = useState(20);
  
  // Search and filter state
  const [searchParams, setSearchParams] = useState<ConfigurationSearch>({
    query: '',
    namespace: '',
    category: '',
    is_active: null,
    is_system: null
  });
  
  // Dialog states
  const [editorVisible, setEditorVisible] = useState(false);
  const [comparisonVisible, setComparisonVisible] = useState(false);
  const [templatesVisible, setTemplatesVisible] = useState(false);
  const [importExportVisible, setImportExportVisible] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<Configuration | null>(null);
  
  // Toast ref
  const toast = React.useRef<Toast>(null);
  
  // Namespace and category options
  const namespaceOptions = [
    { label: 'All Namespaces', value: '' },
    { label: 'Global', value: 'global' },
    { label: 'Solar', value: 'solar' },
    { label: 'Heat Pump', value: 'heatpump' },
    { label: 'PDF', value: 'pdf' },
    { label: 'CRM', value: 'crm' },
    { label: 'Pricing', value: 'pricing' }
  ];
  
  const categoryOptions = [
    { label: 'All Categories', value: '' },
    { label: 'System', value: 'system' },
    { label: 'User', value: 'user' },
    { label: 'Module', value: 'module' },
    { label: 'Feature', value: 'feature' }
  ];
  
  const activeOptions = [
    { label: 'All', value: null },
    { label: 'Active', value: true },
    { label: 'Inactive', value: false }
  ];
  
  // Load configurations
  useEffect(() => {
    loadConfigurations();
  }, [first, rows, searchParams]);
  
  const loadConfigurations = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        offset: first.toString(),
        limit: rows.toString(),
        ...Object.fromEntries(
          Object.entries(searchParams).filter(([_, v]) => v !== '' && v !== null)
        )
      });
      
      const response = await fetch(`/api/v1/configurations/search?${params}`);
      const data = await response.json();
      
      setConfigurations(data.configurations);
      setTotalRecords(data.total);
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load configurations',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Handle search
  const handleSearch = (field: keyof ConfigurationSearch, value: any) => {
    setSearchParams(prev => ({ ...prev, [field]: value }));
    setFirst(0); // Reset to first page
  };
  
  // Handle create
  const handleCreate = () => {
    setSelectedConfig(null);
    setEditorVisible(true);
  };
  
  // Handle edit
  const handleEdit = (config: Configuration) => {
    setSelectedConfig(config);
    setEditorVisible(true);
  };
  
  // Handle delete
  const handleDelete = async (config: Configuration) => {
    try {
      const response = await fetch(`/api/v1/configurations/${config.id}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Configuration deleted successfully',
          life: 3000
        });
        loadConfigurations();
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to delete configuration',
        life: 3000
      });
    }
  };
  
  // Handle compare
  const handleCompare = () => {
    if (selectedConfigurations.length < 2) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Warning',
        detail: 'Please select at least 2 configurations to compare',
        life: 3000
      });
      return;
    }
    setComparisonVisible(true);
  };
  
  // Handle save from editor
  const handleSave = () => {
    setEditorVisible(false);
    loadConfigurations();
    toast.current?.show({
      severity: 'success',
      summary: 'Success',
      detail: 'Configuration saved successfully',
      life: 3000
    });
  };
  
  // Toolbar content
  const leftToolbarTemplate = () => {
    return (
      <div className="flex gap-2">
        <Button
          label="New"
          icon="pi pi-plus"
          severity="success"
          onClick={handleCreate}
        />
        <Button
          label="Compare"
          icon="pi pi-clone"
          severity="info"
          onClick={handleCompare}
          disabled={selectedConfigurations.length < 2}
        />
        <Button
          label="Templates"
          icon="pi pi-book"
          severity="help"
          onClick={() => setTemplatesVisible(true)}
        />
        <Button
          label="Import/Export"
          icon="pi pi-file-export"
          severity="warning"
          onClick={() => setImportExportVisible(true)}
        />
      </div>
    );
  };
  
  const rightToolbarTemplate = () => {
    return (
      <div className="flex gap-2">
        <Button
          label="Refresh"
          icon="pi pi-refresh"
          onClick={loadConfigurations}
        />
      </div>
    );
  };
  
  // Column templates
  const keyBodyTemplate = (rowData: Configuration) => {
    return (
      <div className="flex align-items-center gap-2">
        <span className="font-semibold">{rowData.key}</span>
        {rowData.is_system && <Tag value="System" severity="danger" />}
      </div>
    );
  };
  
  const valueBodyTemplate = (rowData: Configuration) => {
    const maxLength = 50;
    const value = rowData.value || '';
    const truncated = value.length > maxLength ? value.substring(0, maxLength) + '...' : value;
    
    return (
      <span className="text-sm" title={value}>
        {truncated}
      </span>
    );
  };
  
  const namespaceBodyTemplate = (rowData: Configuration) => {
    return <Chip label={rowData.namespace} className="text-sm" />;
  };
  
  const categoryBodyTemplate = (rowData: Configuration) => {
    const severityMap: Record<string, any> = {
      system: 'danger',
      user: 'success',
      module: 'info',
      feature: 'warning'
    };
    
    return (
      <Tag
        value={rowData.category}
        severity={severityMap[rowData.category] || 'info'}
      />
    );
  };
  
  const statusBodyTemplate = (rowData: Configuration) => {
    return (
      <Tag
        value={rowData.is_active ? 'Active' : 'Inactive'}
        severity={rowData.is_active ? 'success' : 'danger'}
      />
    );
  };
  
  const versionBodyTemplate = (rowData: Configuration) => {
    return <span className="text-sm">v{rowData.version}</span>;
  };
  
  const actionsBodyTemplate = (rowData: Configuration) => {
    return (
      <div className="flex gap-2">
        <Button
          icon="pi pi-pencil"
          rounded
          text
          severity="info"
          onClick={() => handleEdit(rowData)}
          tooltip="Edit"
        />
        <Button
          icon="pi pi-trash"
          rounded
          text
          severity="danger"
          onClick={() => handleDelete(rowData)}
          tooltip="Delete"
          disabled={rowData.is_system}
        />
        <Button
          icon="pi pi-history"
          rounded
          text
          severity="help"
          onClick={() => {/* Show version history */}}
          tooltip="Version History"
        />
      </div>
    );
  };
  
  return (
    <div className="configuration-manager">
      <Toast ref={toast} />
      <ConfirmDialog />
      
      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Configuration Management</h2>
        
        {/* Search and Filter Bar */}
        <div className="mb-4 grid grid-cols-1 md:grid-cols-5 gap-3">
          <span className="p-input-icon-left">
            <i className="pi pi-search" />
            <InputText
              placeholder="Search configurations..."
              value={searchParams.query}
              onChange={(e) => handleSearch('query', e.target.value)}
              className="w-full"
            />
          </span>
          
          <Dropdown
            value={searchParams.namespace}
            options={namespaceOptions}
            onChange={(e) => handleSearch('namespace', e.value)}
            placeholder="Namespace"
            className="w-full"
          />
          
          <Dropdown
            value={searchParams.category}
            options={categoryOptions}
            onChange={(e) => handleSearch('category', e.value)}
            placeholder="Category"
            className="w-full"
          />
          
          <Dropdown
            value={searchParams.is_active}
            options={activeOptions}
            onChange={(e) => handleSearch('is_active', e.value)}
            placeholder="Status"
            className="w-full"
          />
          
          <Button
            label="Clear Filters"
            icon="pi pi-filter-slash"
            onClick={() => {
              setSearchParams({
                query: '',
                namespace: '',
                category: '',
                is_active: null,
                is_system: null
              });
            }}
            className="w-full"
          />
        </div>
        
        {/* Toolbar */}
        <Toolbar
          left={leftToolbarTemplate}
          right={rightToolbarTemplate}
          className="mb-4"
        />
        
        {/* Data Table */}
        <DataTable
          value={configurations}
          selection={selectedConfigurations}
          onSelectionChange={(e) => setSelectedConfigurations(e.value)}
          dataKey="id"
          paginator
          rows={rows}
          rowsPerPageOptions={[10, 20, 50, 100]}
          totalRecords={totalRecords}
          lazy
          first={first}
          onPage={(e) => {
            setFirst(e.first);
            setRows(e.rows);
          }}
          loading={loading}
          className="configuration-table"
          emptyMessage="No configurations found"
          stripedRows
          showGridlines
        >
          <Column selectionMode="multiple" headerStyle={{ width: '3rem' }} />
          <Column field="key" header="Key" body={keyBodyTemplate} sortable />
          <Column field="value" header="Value" body={valueBodyTemplate} />
          <Column field="namespace" header="Namespace" body={namespaceBodyTemplate} sortable />
          <Column field="category" header="Category" body={categoryBodyTemplate} sortable />
          <Column field="is_active" header="Status" body={statusBodyTemplate} sortable />
          <Column field="version" header="Version" body={versionBodyTemplate} sortable />
          <Column header="Actions" body={actionsBodyTemplate} style={{ width: '12rem' }} />
        </DataTable>
      </div>
      
      {/* Configuration Editor Dialog */}
      <Dialog
        visible={editorVisible}
        onHide={() => setEditorVisible(false)}
        header={selectedConfig ? 'Edit Configuration' : 'Create Configuration'}
        style={{ width: '50vw' }}
        breakpoints={{ '960px': '75vw', '641px': '90vw' }}
      >
        <ConfigurationEditor
          configuration={selectedConfig}
          onSave={handleSave}
          onCancel={() => setEditorVisible(false)}
        />
      </Dialog>
      
      {/* Configuration Comparison Dialog */}
      <Dialog
        visible={comparisonVisible}
        onHide={() => setComparisonVisible(false)}
        header="Compare Configurations"
        style={{ width: '80vw' }}
        breakpoints={{ '960px': '90vw' }}
      >
        <ConfigurationComparison
          configurations={selectedConfigurations}
          onClose={() => setComparisonVisible(false)}
        />
      </Dialog>
      
      {/* Configuration Templates Dialog */}
      <Dialog
        visible={templatesVisible}
        onHide={() => setTemplatesVisible(false)}
        header="Configuration Templates"
        style={{ width: '70vw' }}
        breakpoints={{ '960px': '85vw' }}
      >
        <ConfigurationTemplates
          onApply={(template) => {
            setTemplatesVisible(false);
            loadConfigurations();
            toast.current?.show({
              severity: 'success',
              summary: 'Success',
              detail: 'Template applied successfully',
              life: 3000
            });
          }}
          onClose={() => setTemplatesVisible(false)}
        />
      </Dialog>
      
      {/* Import/Export Dialog */}
      <Dialog
        visible={importExportVisible}
        onHide={() => setImportExportVisible(false)}
        header="Import/Export Configurations"
        style={{ width: '60vw' }}
        breakpoints={{ '960px': '80vw' }}
      >
        <ConfigurationImportExport
          onImportComplete={() => {
            setImportExportVisible(false);
            loadConfigurations();
            toast.current?.show({
              severity: 'success',
              summary: 'Success',
              detail: 'Import completed successfully',
              life: 3000
            });
          }}
          onClose={() => setImportExportVisible(false)}
        />
      </Dialog>
    </div>
  );
};

export default ConfigurationManager;
