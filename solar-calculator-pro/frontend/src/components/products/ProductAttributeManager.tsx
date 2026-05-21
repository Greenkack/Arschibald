/**
 * ProductAttributeManager Component - Task 51
 * 
 * Complete product attribute management interface with:
 * - Attribute definition interface
 * - Attribute value management
 * - Attribute groups
 * - Custom attributes
 * - Attribute templates
 */

import React, { useState, useEffect, useRef } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { InputTextarea } from 'primereact/inputtextarea';
import { Checkbox } from 'primereact/checkbox';
import { TabView, TabPanel } from 'primereact/tabview';
import { Tag } from 'primereact/tag';
import { Toolbar } from 'primereact/toolbar';
import { Chips } from 'primereact/chips';
import api from '../../services/api';
import './ProductAttributeManager.css';

export interface ProductAttribute {
  id: number;
  name: string;
  label: string;
  type: 'text' | 'number' | 'boolean' | 'select' | 'multiselect' | 'date';
  required: boolean;
  default_value?: any;
  options?: string[];
  validation_rules?: Record<string, any>;
  group_id?: number;
  group_name?: string;
  description?: string;
  unit?: string;
  order: number;
  is_custom: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AttributeGroup {
  id: number;
  name: string;
  label: string;
  description?: string;
  order: number;
  is_collapsible: boolean;
  is_expanded_by_default: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AttributeTemplate {
  id: number;
  name: string;
  description?: string;
  category: string;
  attributes: number[];
  created_at?: string;
  updated_at?: string;
}

const ProductAttributeManager: React.FC = () => {
  const [attributes, setAttributes] = useState<ProductAttribute[]>([]);
  const [groups, setGroups] = useState<AttributeGroup[]>([]);
  const [templates, setTemplates] = useState<AttributeTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  
  // Attribute dialog states
  const [showAttributeDialog, setShowAttributeDialog] = useState(false);
  const [editingAttribute, setEditingAttribute] = useState<ProductAttribute | null>(null);
  
  // Group dialog states
  const [showGroupDialog, setShowGroupDialog] = useState(false);
  const [editingGroup, setEditingGroup] = useState<AttributeGroup | null>(null);
  
  // Template dialog states
  const [showTemplateDialog, setShowTemplateDialog] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<AttributeTemplate | null>(null);
  
  const toastRef = useRef<Toast>(null);

  useEffect(() => {
    loadAttributes();
    loadGroups();
    loadTemplates();
  }, []);

  const loadAttributes = async () => {
    setLoading(true);
    try {
      const response = await api.get('/products/attributes');
      setAttributes(response.data.attributes || []);
    } catch (error) {
      console.error('Failed to load attributes:', error);
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load attributes',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const loadGroups = async () => {
    try {
      const response = await api.get('/products/attribute-groups');
      setGroups(response.data.groups || []);
    } catch (error) {
      console.error('Failed to load groups:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await api.get('/products/attribute-templates');
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleDeleteAttribute = (attribute: ProductAttribute) => {
    confirmDialog({
      message: `Are you sure you want to delete attribute "${attribute.label}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/products/attributes/${attribute.id}`);
          toastRef.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Attribute deleted successfully',
            life: 3000
          });
          loadAttributes();
        } catch (error) {
          console.error('Failed to delete attribute:', error);
          toastRef.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete attribute',
            life: 3000
          });
        }
      }
    });
  };

  const handleDeleteGroup = (group: AttributeGroup) => {
    confirmDialog({
      message: `Are you sure you want to delete group "${group.label}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/products/attribute-groups/${group.id}`);
          toastRef.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Group deleted successfully',
            life: 3000
          });
          loadGroups();
          loadAttributes();
        } catch (error) {
          console.error('Failed to delete group:', error);
          toastRef.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete group',
            life: 3000
          });
        }
      }
    });
  };

  const handleDeleteTemplate = (template: AttributeTemplate) => {
    confirmDialog({
      message: `Are you sure you want to delete template "${template.name}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/products/attribute-templates/${template.id}`);
          toastRef.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Template deleted successfully',
            life: 3000
          });
          loadTemplates();
        } catch (error) {
          console.error('Failed to delete template:', error);
          toastRef.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete template',
            life: 3000
          });
        }
      }
    });
  };

  // Render functions for DataTable
  const typeBodyTemplate = (rowData: ProductAttribute) => {
    const typeColors: Record<string, string> = {
      text: 'info',
      number: 'success',
      boolean: 'warning',
      select: 'primary',
      multiselect: 'primary',
      date: 'secondary'
    };
    return <Tag value={rowData.type} severity={typeColors[rowData.type] as any} />;
  };

  const requiredBodyTemplate = (rowData: ProductAttribute) => {
    return rowData.required ? (
      <i className="pi pi-check-circle" style={{ color: 'green' }} />
    ) : (
      <i className="pi pi-times-circle" style={{ color: 'gray' }} />
    );
  };

  const customBodyTemplate = (rowData: ProductAttribute) => {
    return rowData.is_custom ? (
      <Tag value="Custom" severity="info" />
    ) : (
      <Tag value="Standard" severity="secondary" />
    );
  };

  const attributeActionsTemplate = (rowData: ProductAttribute) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-text"
          onClick={() => {
            setEditingAttribute(rowData);
            setShowAttributeDialog(true);
          }}
          tooltip="Edit"
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => handleDeleteAttribute(rowData)}
          tooltip="Delete"
        />
      </div>
    );
  };

  const groupActionsTemplate = (rowData: AttributeGroup) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-text"
          onClick={() => {
            setEditingGroup(rowData);
            setShowGroupDialog(true);
          }}
          tooltip="Edit"
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => handleDeleteGroup(rowData)}
          tooltip="Delete"
        />
      </div>
    );
  };

  const templateActionsTemplate = (rowData: AttributeTemplate) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-text"
          onClick={() => {
            setEditingTemplate(rowData);
            setShowTemplateDialog(true);
          }}
          tooltip="Edit"
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => handleDeleteTemplate(rowData)}
          tooltip="Delete"
        />
      </div>
    );
  };

  return (
    <div className="product-attribute-manager">
      <Toast ref={toastRef} />
      <ConfirmDialog />

      <div className="manager-header">
        <h2>Product Attribute Management</h2>
        <p>Define and manage product attributes, groups, and templates</p>
      </div>

      <TabView activeIndex={activeTab} onTabChange={(e) => setActiveTab(e.index)}>
        <TabPanel header="Attributes" leftIcon="pi pi-list">
          <Toolbar
            left={
              <Button
                label="New Attribute"
                icon="pi pi-plus"
                className="p-button-success"
                onClick={() => {
                  setEditingAttribute(null);
                  setShowAttributeDialog(true);
                }}
              />
            }
          />

          <DataTable
            value={attributes}
            loading={loading}
            paginator
            rows={20}
            className="attributes-table"
            emptyMessage="No attributes defined"
          >
            <Column field="label" header="Label" sortable />
            <Column field="name" header="Name" sortable />
            <Column field="type" header="Type" body={typeBodyTemplate} sortable />
            <Column field="group_name" header="Group" sortable />
            <Column field="required" header="Required" body={requiredBodyTemplate} />
            <Column field="is_custom" header="Type" body={customBodyTemplate} />
            <Column field="order" header="Order" sortable style={{ width: '100px' }} />
            <Column header="Actions" body={attributeActionsTemplate} style={{ width: '120px' }} />
          </DataTable>
        </TabPanel>

        <TabPanel header="Groups" leftIcon="pi pi-folder">
          <Toolbar
            left={
              <Button
                label="New Group"
                icon="pi pi-plus"
                className="p-button-success"
                onClick={() => {
                  setEditingGroup(null);
                  setShowGroupDialog(true);
                }}
              />
            }
          />

          <DataTable
            value={groups}
            loading={loading}
            paginator
            rows={20}
            className="groups-table"
            emptyMessage="No groups defined"
          >
            <Column field="label" header="Label" sortable />
            <Column field="name" header="Name" sortable />
            <Column field="description" header="Description" />
            <Column field="order" header="Order" sortable style={{ width: '100px' }} />
            <Column header="Actions" body={groupActionsTemplate} style={{ width: '120px' }} />
          </DataTable>
        </TabPanel>

        <TabPanel header="Templates" leftIcon="pi pi-clone">
          <Toolbar
            left={
              <Button
                label="New Template"
                icon="pi pi-plus"
                className="p-button-success"
                onClick={() => {
                  setEditingTemplate(null);
                  setShowTemplateDialog(true);
                }}
              />
            }
          />

          <DataTable
            value={templates}
            loading={loading}
            paginator
            rows={20}
            className="templates-table"
            emptyMessage="No templates defined"
          >
            <Column field="name" header="Name" sortable />
            <Column field="category" header="Category" sortable />
            <Column field="description" header="Description" />
            <Column 
              field="attributes" 
              header="Attributes" 
              body={(rowData) => <Tag value={`${rowData.attributes.length} attributes`} />}
            />
            <Column header="Actions" body={templateActionsTemplate} style={{ width: '120px' }} />
          </DataTable>
        </TabPanel>
      </TabView>

      {/* Attribute Dialog */}
      <Dialog
        visible={showAttributeDialog}
        onHide={() => {
          setShowAttributeDialog(false);
          setEditingAttribute(null);
        }}
        header={editingAttribute ? 'Edit Attribute' : 'Create Attribute'}
        modal
        style={{ width: '700px' }}
      >
        <AttributeForm
          attribute={editingAttribute}
          groups={groups}
          onSubmit={async (data) => {
            try {
              if (editingAttribute) {
                await api.put(`/products/attributes/${editingAttribute.id}`, data);
                toastRef.current?.show({
                  severity: 'success',
                  summary: 'Success',
                  detail: 'Attribute updated successfully',
                  life: 3000
                });
              } else {
                await api.post('/products/attributes', data);
                toastRef.current?.show({
                  severity: 'success',
                  summary: 'Success',
                  detail: 'Attribute created successfully',
                  life: 3000
                });
              }
              setShowAttributeDialog(false);
              setEditingAttribute(null);
              loadAttributes();
            } catch (error) {
              console.error('Failed to save attribute:', error);
              toastRef.current?.show({
                severity: 'error',
                summary: 'Error',
                detail: 'Failed to save attribute',
                life: 3000
              });
            }
          }}
          onCancel={() => {
            setShowAttributeDialog(false);
            setEditingAttribute(null);
          }}
        />
      </Dialog>

      {/* Group Dialog */}
      <Dialog
        visible={showGroupDialog}
        onHide={() => {
          setShowGroupDialog(false);
          setEditingGroup(null);
        }}
        header={editingGroup ? 'Edit Group' : 'Create Group'}
        modal
        style={{ width: '600px' }}
      >
        <GroupForm
          group={editingGroup}
          onSubmit={async (data) => {
            try {
              if (editingGroup) {
                await api.put(`/products/attribute-groups/${editingGroup.id}`, data);
                toastRef.current?.show({
                  severity: 'success',
                  summary: 'Success',
                  detail: 'Group updated successfully',
                  life: 3000
                });
              } else {
                await api.post('/products/attribute-groups', data);
                toastRef.current?.show({
                  severity: 'success',
                  summary: 'Success',
                  detail: 'Group created successfully',
                  life: 3000
                });
              }
              setShowGroupDialog(false);
              setEditingGroup(null);
              loadGroups();
            } catch (error) {
              console.error('Failed to save group:', error);
              toastRef.current?.show({
                severity: 'error',
                summary: 'Error',
                detail: 'Failed to save group',
                life: 3000
              });
            }
          }}
          onCancel={() => {
            setShowGroupDialog(false);
            setEditingGroup(null);
          }}
        />
      </Dialog>

      {/* Template Dialog */}
      <Dialog
        visible={showTemplateDialog}
        onHide={() => {
          setShowTemplateDialog(false);
          setEditingTemplate(null);
        }}
        header={editingTemplate ? 'Edit Template' : 'Create Template'}
        modal
        style={{ width: '700px' }}
      >
        <TemplateForm
          template={editingTemplate}
          attributes={attributes}
          onSubmit={async (data) => {
            try {
              if (editingTemplate) {
                await api.put(`/products/attribute-templates/${editingTemplate.id}`, data);
                toastRef.current?.show({
                  severity: 'success',
                  summary: 'Success',
                  detail: 'Template updated successfully',
                  life: 3000
                });
              } else {
                await api.post('/products/attribute-templates', data);
                toastRef.current?.show({
                  severity: 'success',
                  summary: 'Success',
                  detail: 'Template created successfully',
                  life: 3000
                });
              }
              setShowTemplateDialog(false);
              setEditingTemplate(null);
              loadTemplates();
            } catch (error) {
              console.error('Failed to save template:', error);
              toastRef.current?.show({
                severity: 'error',
                summary: 'Error',
                detail: 'Failed to save template',
                life: 3000
              });
            }
          }}
          onCancel={() => {
            setShowTemplateDialog(false);
            setEditingTemplate(null);
          }}
        />
      </Dialog>
    </div>
  );
};

export default ProductAttributeManager;
