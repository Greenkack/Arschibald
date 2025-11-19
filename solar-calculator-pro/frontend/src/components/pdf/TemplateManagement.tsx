/**
 * PDF Template Management Component
 * 
 * Provides interface for managing PDF templates including:
 * - Viewing all templates
 * - Editing template metadata
 * - Deleting templates
 * - Setting default templates
 */

import React, { useState, useEffect, useRef } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dialog } from 'primereact/dialog';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Toast } from 'primereact/toast';
import { Tag } from 'primereact/tag';
import { Toolbar } from 'primereact/toolbar';
import { FilterMatchMode } from 'primereact/api';
import api from '../../services/api';
import { PDFTemplate } from './TemplateGallery';
import './TemplateManagement.css';

interface TemplateManagementProps {
  onTemplateChange?: () => void;
}

export const TemplateManagement: React.FC<TemplateManagementProps> = ({
  onTemplateChange
}) => {
  const [templates, setTemplates] = useState<PDFTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');
  const [selectedTemplates, setSelectedTemplates] = useState<PDFTemplate[]>([]);
  const [editDialogVisible, setEditDialogVisible] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<PDFTemplate | null>(null);
  const toast = useRef<Toast>(null);

  const [filters] = useState({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    display_name: { value: null, matchMode: FilterMatchMode.CONTAINS },
    description: { value: null, matchMode: FilterMatchMode.CONTAINS }
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/pdf/templates');
      setTemplates(response.data);
    } catch (err: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: err.response?.data?.error?.message || 'Failed to load templates',
        life: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (template: PDFTemplate) => {
    setEditingTemplate({ ...template });
    setEditDialogVisible(true);
  };

  const handleSaveEdit = async () => {
    if (!editingTemplate) return;

    try {
      await api.put(`/api/v1/pdf/templates/${editingTemplate.name}`, {
        display_name: editingTemplate.display_name,
        description: editingTemplate.description
      });

      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Template updated successfully',
        life: 3000
      });

      setEditDialogVisible(false);
      setEditingTemplate(null);
      loadTemplates();
      onTemplateChange?.();
    } catch (err: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: err.response?.data?.error?.message || 'Failed to update template',
        life: 5000
      });
    }
  };

  const handleDelete = (template: PDFTemplate) => {
    confirmDialog({
      message: `Are you sure you want to delete the template "${template.display_name}"?`,
      header: 'Confirm Deletion',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/api/v1/pdf/templates/${template.name}`);
          
          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Template deleted successfully',
            life: 3000
          });

          loadTemplates();
          onTemplateChange?.();
        } catch (err: any) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: err.response?.data?.error?.message || 'Failed to delete template',
            life: 5000
          });
        }
      }
    });
  };

  const handleBulkDelete = () => {
    if (selectedTemplates.length === 0) return;

    confirmDialog({
      message: `Are you sure you want to delete ${selectedTemplates.length} template(s)?`,
      header: 'Confirm Bulk Deletion',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await Promise.all(
            selectedTemplates.map(template =>
              api.delete(`/api/v1/pdf/templates/${template.name}`)
            )
          );

          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: `${selectedTemplates.length} template(s) deleted successfully`,
            life: 3000
          });

          setSelectedTemplates([]);
          loadTemplates();
          onTemplateChange?.();
        } catch (err: any) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete some templates',
            life: 5000
          });
        }
      }
    });
  };

  const handleSetDefault = async (template: PDFTemplate) => {
    try {
      await api.post(`/api/v1/pdf/templates/${template.name}/set-default`);
      
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Default template updated',
        life: 3000
      });

      loadTemplates();
      onTemplateChange?.();
    } catch (err: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: err.response?.data?.error?.message || 'Failed to set default template',
        life: 5000
      });
    }
  };

  const nameBodyTemplate = (rowData: PDFTemplate) => {
    return (
      <div className="template-name-cell">
        <i className="pi pi-file-pdf"></i>
        <span>{rowData.display_name}</span>
      </div>
    );
  };

  const typeBodyTemplate = (rowData: PDFTemplate) => {
    return rowData.is_custom ? (
      <Tag value="Custom" severity="info" />
    ) : (
      <Tag value="Built-in" severity="success" />
    );
  };

  const dateBodyTemplate = (rowData: PDFTemplate) => {
    if (!rowData.created_at) return '-';
    return new Date(rowData.created_at).toLocaleDateString('de-DE');
  };

  const sizeBodyTemplate = (rowData: PDFTemplate) => {
    if (!rowData.file_size) return '-';
    return `${(rowData.file_size / 1024).toFixed(2)} KB`;
  };

  const actionsBodyTemplate = (rowData: PDFTemplate) => {
    return (
      <div className="template-actions">
        <Button
          icon="pi pi-pencil"
          className="p-button-text p-button-sm"
          onClick={() => handleEdit(rowData)}
          tooltip="Edit"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-star"
          className="p-button-text p-button-sm"
          onClick={() => handleSetDefault(rowData)}
          tooltip="Set as Default"
          tooltipOptions={{ position: 'top' }}
        />
        {rowData.is_custom && (
          <Button
            icon="pi pi-trash"
            className="p-button-text p-button-danger p-button-sm"
            onClick={() => handleDelete(rowData)}
            tooltip="Delete"
            tooltipOptions={{ position: 'top' }}
          />
        )}
      </div>
    );
  };

  const renderHeader = () => {
    return (
      <div className="table-header">
        <h3>📋 Template Management</h3>
        <span className="p-input-icon-left">
          <i className="pi pi-search" />
          <InputText
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder="Search templates..."
          />
        </span>
      </div>
    );
  };

  const renderToolbar = () => {
    return (
      <Toolbar
        left={
          <div className="toolbar-left">
            <Button
              label="Refresh"
              icon="pi pi-refresh"
              onClick={loadTemplates}
              className="p-button-outlined"
            />
          </div>
        }
        right={
          <div className="toolbar-right">
            <Button
              label="Delete Selected"
              icon="pi pi-trash"
              onClick={handleBulkDelete}
              className="p-button-danger"
              disabled={selectedTemplates.length === 0}
            />
          </div>
        }
      />
    );
  };

  const renderEditDialog = () => {
    return (
      <Dialog
        visible={editDialogVisible}
        onHide={() => setEditDialogVisible(false)}
        header="Edit Template"
        style={{ width: '500px' }}
        footer={
          <div>
            <Button
              label="Cancel"
              icon="pi pi-times"
              onClick={() => setEditDialogVisible(false)}
              className="p-button-text"
            />
            <Button
              label="Save"
              icon="pi pi-check"
              onClick={handleSaveEdit}
            />
          </div>
        }
      >
        {editingTemplate && (
          <div className="edit-form">
            <div className="form-field">
              <label htmlFor="edit-name">Display Name</label>
              <InputText
                id="edit-name"
                value={editingTemplate.display_name}
                onChange={(e) =>
                  setEditingTemplate({
                    ...editingTemplate,
                    display_name: e.target.value
                  })
                }
                className="w-full"
              />
            </div>
            <div className="form-field">
              <label htmlFor="edit-description">Description</label>
              <InputText
                id="edit-description"
                value={editingTemplate.description}
                onChange={(e) =>
                  setEditingTemplate({
                    ...editingTemplate,
                    description: e.target.value
                  })
                }
                className="w-full"
              />
            </div>
          </div>
        )}
      </Dialog>
    );
  };

  return (
    <div className="template-management">
      <Toast ref={toast} />
      <ConfirmDialog />
      
      {renderToolbar()}
      
      <DataTable
        value={templates}
        loading={loading}
        header={renderHeader()}
        filters={filters}
        globalFilterFields={['display_name', 'description']}
        globalFilter={globalFilter}
        selection={selectedTemplates}
        onSelectionChange={(e) => setSelectedTemplates(e.value)}
        dataKey="name"
        paginator
        rows={10}
        rowsPerPageOptions={[5, 10, 25, 50]}
        emptyMessage="No templates found"
        className="template-table"
      >
        <Column selectionMode="multiple" style={{ width: '3rem' }} />
        <Column field="display_name" header="Name" body={nameBodyTemplate} sortable />
        <Column field="description" header="Description" sortable />
        <Column header="Type" body={typeBodyTemplate} sortable />
        <Column field="created_at" header="Created" body={dateBodyTemplate} sortable />
        <Column field="file_size" header="Size" body={sizeBodyTemplate} sortable />
        <Column header="Actions" body={actionsBodyTemplate} style={{ width: '12rem' }} />
      </DataTable>

      {renderEditDialog()}
    </div>
  );
};
