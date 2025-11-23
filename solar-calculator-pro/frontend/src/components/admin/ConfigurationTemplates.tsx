/**
 * Configuration Templates Component
 * 
 * Manage and apply configuration templates
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dialog } from 'primereact/dialog';
import { Tag } from 'primereact/tag';
import { Chip } from 'primereact/chip';
import { Card } from 'primereact/card';
import { Toast } from 'primereact/toast';
import { Dropdown } from 'primereact/dropdown';
import { Checkbox } from 'primereact/checkbox';

interface ConfigurationTemplate {
  id: number;
  template_name: string;
  template_type: string;
  description: string;
  configuration_data: any;
  category: string;
  tags: string[];
  usage_count: number;
  last_used_at: string | null;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
}

interface ConfigurationTemplatesProps {
  onApply: (template: ConfigurationTemplate) => void;
  onClose: () => void;
}

const ConfigurationTemplates: React.FC<ConfigurationTemplatesProps> = ({
  onApply,
  onClose
}) => {
  const [templates, setTemplates] = useState<ConfigurationTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ConfigurationTemplate | null>(null);
  const [loading, setLoading] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [applyDialogVisible, setApplyDialogVisible] = useState(false);
  
  // Apply options
  const [applyOptions, setApplyOptions] = useState({
    namespace: 'global',
    merge_mode: 'replace',
    overrides: {}
  });
  
  const toast = React.useRef<Toast>(null);
  
  // Load templates
  useEffect(() => {
    loadTemplates();
  }, []);
  
  const loadTemplates = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/configuration-templates');
      const data = await response.json();
      setTemplates(data);
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load templates',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Handle preview
  const handlePreview = (template: ConfigurationTemplate) => {
    setSelectedTemplate(template);
    setPreviewVisible(true);
  };
  
  // Handle apply
  const handleApplyClick = (template: ConfigurationTemplate) => {
    setSelectedTemplate(template);
    setApplyDialogVisible(true);
  };
  
  const handleApplyConfirm = async () => {
    if (!selectedTemplate) return;
    
    try {
      const response = await fetch('/api/v1/configuration-templates/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          template_id: selectedTemplate.id,
          ...applyOptions
        })
      });
      
      if (response.ok) {
        onApply(selectedTemplate);
        setApplyDialogVisible(false);
      } else {
        throw new Error('Apply failed');
      }
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to apply template',
        life: 3000
      });
    }
  };
  
  // Column templates
  const nameBodyTemplate = (rowData: ConfigurationTemplate) => {
    return (
      <div>
        <div className="font-semibold">{rowData.template_name}</div>
        <div className="text-sm text-gray-600">{rowData.description}</div>
      </div>
    );
  };
  
  const typeBodyTemplate = (rowData: ConfigurationTemplate) => {
    const severityMap: Record<string, any> = {
      system: 'danger',
      module: 'info',
      feature: 'warning',
      custom: 'success'
    };
    
    return (
      <Tag
        value={rowData.template_type}
        severity={severityMap[rowData.template_type] || 'info'}
      />
    );
  };
  
  const tagsBodyTemplate = (rowData: ConfigurationTemplate) => {
    if (!rowData.tags || rowData.tags.length === 0) {
      return <span className="text-gray-400">No tags</span>;
    }
    
    return (
      <div className="flex flex-wrap gap-1">
        {rowData.tags.slice(0, 3).map((tag, index) => (
          <Chip key={index} label={tag} className="text-xs" />
        ))}
        {rowData.tags.length > 3 && (
          <Chip label={`+${rowData.tags.length - 3}`} className="text-xs" />
        )}
      </div>
    );
  };
  
  const usageBodyTemplate = (rowData: ConfigurationTemplate) => {
    return (
      <div className="text-center">
        <div className="font-semibold">{rowData.usage_count}</div>
        {rowData.last_used_at && (
          <div className="text-xs text-gray-600">
            {new Date(rowData.last_used_at).toLocaleDateString()}
          </div>
        )}
      </div>
    );
  };
  
  const actionsBodyTemplate = (rowData: ConfigurationTemplate) => {
    return (
      <div className="flex gap-2">
        <Button
          icon="pi pi-eye"
          rounded
          text
          severity="info"
          onClick={() => handlePreview(rowData)}
          tooltip="Preview"
        />
        <Button
          icon="pi pi-check"
          rounded
          text
          severity="success"
          onClick={() => handleApplyClick(rowData)}
          tooltip="Apply Template"
        />
      </div>
    );
  };
  
  return (
    <div className="configuration-templates">
      <Toast ref={toast} />
      
      {/* Templates Table */}
      <DataTable
        value={templates}
        loading={loading}
        emptyMessage="No templates found"
        className="templates-table"
        stripedRows
        showGridlines
      >
        <Column field="template_name" header="Template" body={nameBodyTemplate} />
        <Column field="template_type" header="Type" body={typeBodyTemplate} />
        <Column field="category" header="Category" />
        <Column field="tags" header="Tags" body={tagsBodyTemplate} />
        <Column field="usage_count" header="Usage" body={usageBodyTemplate} />
        <Column header="Actions" body={actionsBodyTemplate} style={{ width: '8rem' }} />
      </DataTable>
      
      {/* Preview Dialog */}
      <Dialog
        visible={previewVisible}
        onHide={() => setPreviewVisible(false)}
        header={`Preview: ${selectedTemplate?.template_name}`}
        style={{ width: '60vw' }}
        breakpoints={{ '960px': '80vw' }}
      >
        {selectedTemplate && (
          <div>
            <Card className="mb-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <strong>Type:</strong> {selectedTemplate.template_type}
                </div>
                <div>
                  <strong>Category:</strong> {selectedTemplate.category}
                </div>
                <div className="col-span-2">
                  <strong>Description:</strong> {selectedTemplate.description}
                </div>
              </div>
            </Card>
            
            <h4 className="font-semibold mb-2">Configuration Data:</h4>
            <pre className="bg-gray-100 p-3 rounded overflow-auto max-h-96 text-sm">
              {JSON.stringify(selectedTemplate.configuration_data, null, 2)}
            </pre>
            
            <div className="flex justify-end gap-2 mt-4">
              <Button
                label="Close"
                icon="pi pi-times"
                severity="secondary"
                onClick={() => setPreviewVisible(false)}
              />
              <Button
                label="Apply This Template"
                icon="pi pi-check"
                severity="success"
                onClick={() => {
                  setPreviewVisible(false);
                  handleApplyClick(selectedTemplate);
                }}
              />
            </div>
          </div>
        )}
      </Dialog>
      
      {/* Apply Dialog */}
      <Dialog
        visible={applyDialogVisible}
        onHide={() => setApplyDialogVisible(false)}
        header={`Apply Template: ${selectedTemplate?.template_name}`}
        style={{ width: '50vw' }}
        breakpoints={{ '960px': '75vw' }}
      >
        <div className="grid grid-cols-1 gap-4">
          <div className="field">
            <label htmlFor="namespace" className="block font-semibold mb-2">
              Target Namespace
            </label>
            <Dropdown
              id="namespace"
              value={applyOptions.namespace}
              options={[
                { label: 'Global', value: 'global' },
                { label: 'Solar', value: 'solar' },
                { label: 'Heat Pump', value: 'heatpump' },
                { label: 'PDF', value: 'pdf' },
                { label: 'CRM', value: 'crm' },
                { label: 'Pricing', value: 'pricing' }
              ]}
              onChange={(e) => setApplyOptions(prev => ({ ...prev, namespace: e.value }))}
              className="w-full"
            />
          </div>
          
          <div className="field">
            <label htmlFor="merge_mode" className="block font-semibold mb-2">
              Merge Mode
            </label>
            <Dropdown
              id="merge_mode"
              value={applyOptions.merge_mode}
              options={[
                { label: 'Replace Existing', value: 'replace' },
                { label: 'Merge with Existing', value: 'merge' }
              ]}
              onChange={(e) => setApplyOptions(prev => ({ ...prev, merge_mode: e.value }))}
              className="w-full"
            />
            <small className="block mt-1 text-gray-600">
              Replace will overwrite existing configurations, Merge will keep existing values
            </small>
          </div>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
            <div className="flex align-items-start gap-2">
              <i className="pi pi-exclamation-triangle text-yellow-600 mt-1" />
              <div>
                <strong>Warning:</strong> Applying this template will create or update configurations
                in the selected namespace. This action cannot be undone.
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex justify-end gap-2 mt-4">
          <Button
            label="Cancel"
            icon="pi pi-times"
            severity="secondary"
            onClick={() => setApplyDialogVisible(false)}
          />
          <Button
            label="Apply Template"
            icon="pi pi-check"
            severity="success"
            onClick={handleApplyConfirm}
          />
        </div>
      </Dialog>
      
      {/* Action Buttons */}
      <div className="flex justify-end gap-2 mt-4">
        <Button
          label="Close"
          icon="pi pi-times"
          severity="secondary"
          onClick={onClose}
        />
      </div>
    </div>
  );
};

export default ConfigurationTemplates;
