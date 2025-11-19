/**
 * Solar Projects Page
 * 
 * Project list page with DataTable, search, filtering, and CRUD operations
 * 
 * Requirements: 7.1
 */

import React, { useState, useEffect, useRef } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Dialog } from 'primereact/dialog';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Tag } from 'primereact/tag';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './SolarProjects.css';

interface Project {
  id: number;
  name: string;
  customer_id: number;
  project_type: string;
  status: string;
  data: any;
  dynamic_key: string;
  created_at: string;
  updated_at: string;
}

interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const SolarProjects: React.FC = () => {
  const navigate = useNavigate();
  const toast = useRef<Toast>(null);
  
  // State
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalRecords, setTotalRecords] = useState(0);
  const [first, setFirst] = useState(0);
  const [rows, setRows] = useState(20);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [projectTypeFilter, setProjectTypeFilter] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  
  // Dialog state
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectType, setNewProjectType] = useState('solar');
  const [newCustomerId, setNewCustomerId] = useState<number>(1); // TODO: Get from customer selection
  
  // Project type options
  const projectTypeOptions = [
    { label: 'Alle Typen', value: null },
    { label: 'Solar', value: 'solar' },
    { label: 'Wärmepumpe', value: 'heatpump' },
    { label: 'Kombiniert', value: 'combined' }
  ];
  
  // Status options
  const statusOptions = [
    { label: 'Alle Status', value: null },
    { label: 'Entwurf', value: 'draft' },
    { label: 'Aktiv', value: 'active' },
    { label: 'Abgeschlossen', value: 'completed' },
    { label: 'Archiviert', value: 'archived' }
  ];
  
  // Load projects
  const loadProjects = async () => {
    setLoading(true);
    
    try {
      const page = Math.floor(first / rows) + 1;
      const params: any = {
        page,
        page_size: rows
      };
      
      if (searchTerm) {
        params.search = searchTerm;
      }
      
      if (projectTypeFilter) {
        params.project_type = projectTypeFilter;
      }
      
      if (statusFilter) {
        params.status = statusFilter;
      }
      
      const response = await api.get<ProjectListResponse>('/api/v1/solar/projects', { params });
      
      setProjects(response.data.items);
      setTotalRecords(response.data.total);
    } catch (error: any) {
      console.error('Failed to load projects:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: error.response?.data?.detail || 'Projekte konnten nicht geladen werden',
        life: 5000
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Load projects on mount and when filters change
  useEffect(() => {
    loadProjects();
  }, [first, rows, searchTerm, projectTypeFilter, statusFilter]);
  
  // Create project
  const handleCreateProject = async () => {
    if (!newProjectName.trim()) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Warnung',
        detail: 'Bitte geben Sie einen Projektnamen ein',
        life: 3000
      });
      return;
    }
    
    try {
      await api.post('/api/v1/solar/projects', {
        name: newProjectName,
        customer_id: newCustomerId,
        project_type: newProjectType,
        data: {}
      });
      
      toast.current?.show({
        severity: 'success',
        summary: 'Erfolg',
        detail: 'Projekt wurde erfolgreich erstellt',
        life: 3000
      });
      
      setShowCreateDialog(false);
      setNewProjectName('');
      setNewProjectType('solar');
      loadProjects();
    } catch (error: any) {
      console.error('Failed to create project:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: error.response?.data?.detail || 'Projekt konnte nicht erstellt werden',
        life: 5000
      });
    }
  };
  
  // Delete project
  const handleDeleteProject = (project: Project) => {
    confirmDialog({
      message: `Möchten Sie das Projekt "${project.name}" wirklich löschen?`,
      header: 'Löschen bestätigen',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Ja, löschen',
      rejectLabel: 'Abbrechen',
      acceptClassName: 'p-button-danger',
      accept: async () => {
        try {
          await api.delete(`/api/v1/solar/projects/${project.id}`);
          
          toast.current?.show({
            severity: 'success',
            summary: 'Erfolg',
            detail: 'Projekt wurde gelöscht',
            life: 3000
          });
          
          loadProjects();
        } catch (error: any) {
          console.error('Failed to delete project:', error);
          toast.current?.show({
            severity: 'error',
            summary: 'Fehler',
            detail: error.response?.data?.detail || 'Projekt konnte nicht gelöscht werden',
            life: 5000
          });
        }
      }
    });
  };
  
  // View project details
  const handleViewProject = (project: Project) => {
    navigate(`/solar-projects/${project.id}`);
  };
  
  // Edit project
  const handleEditProject = (project: Project) => {
    navigate(`/solar-projects/${project.id}/edit`);
  };
  
  // Template functions for DataTable
  const projectTypeBodyTemplate = (rowData: Project) => {
    const typeLabels: Record<string, string> = {
      solar: 'Solar',
      heatpump: 'Wärmepumpe',
      combined: 'Kombiniert'
    };
    
    return typeLabels[rowData.project_type] || rowData.project_type;
  };
  
  const statusBodyTemplate = (rowData: Project) => {
    const statusConfig: Record<string, { label: string; severity: any }> = {
      draft: { label: 'Entwurf', severity: 'info' },
      active: { label: 'Aktiv', severity: 'success' },
      completed: { label: 'Abgeschlossen', severity: 'warning' },
      archived: { label: 'Archiviert', severity: 'secondary' }
    };
    
    const config = statusConfig[rowData.status] || { label: rowData.status, severity: 'info' };
    
    return <Tag value={config.label} severity={config.severity} />;
  };
  
  const dateBodyTemplate = (rowData: Project) => {
    return new Date(rowData.created_at).toLocaleDateString('de-DE');
  };
  
  const actionsBodyTemplate = (rowData: Project) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-text p-button-info"
          onClick={() => handleViewProject(rowData)}
          tooltip="Anzeigen"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-text p-button-warning"
          onClick={() => handleEditProject(rowData)}
          tooltip="Bearbeiten"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => handleDeleteProject(rowData)}
          tooltip="Löschen"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  };
  
  // Header with search and filters
  const tableHeader = (
    <div className="table-header">
      <div className="header-left">
        <h2>Solar Projekte</h2>
      </div>
      <div className="header-right">
        <span className="p-input-icon-left">
          <i className="pi pi-search" />
          <InputText
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Suchen..."
          />
        </span>
        <Dropdown
          value={projectTypeFilter}
          options={projectTypeOptions}
          onChange={(e) => setProjectTypeFilter(e.value)}
          placeholder="Projekttyp"
          className="filter-dropdown"
        />
        <Dropdown
          value={statusFilter}
          options={statusOptions}
          onChange={(e) => setStatusFilter(e.value)}
          placeholder="Status"
          className="filter-dropdown"
        />
        <Button
          label="Neues Projekt"
          icon="pi pi-plus"
          onClick={() => setShowCreateDialog(true)}
          className="p-button-success"
        />
      </div>
    </div>
  );
  
  return (
    <div className="solar-projects-page">
      <Toast ref={toast} />
      <ConfirmDialog />
      
      <div className="page-content">
        <DataTable
          value={projects}
          loading={loading}
          header={tableHeader}
          paginator
          rows={rows}
          first={first}
          totalRecords={totalRecords}
          onPage={(e) => {
            setFirst(e.first);
            setRows(e.rows);
          }}
          rowsPerPageOptions={[10, 20, 50]}
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="{first} bis {last} von {totalRecords} Projekten"
          emptyMessage="Keine Projekte gefunden"
          className="projects-table"
          stripedRows
          responsiveLayout="scroll"
        >
          <Column field="name" header="Projektname" sortable />
          <Column field="project_type" header="Typ" body={projectTypeBodyTemplate} sortable />
          <Column field="status" header="Status" body={statusBodyTemplate} sortable />
          <Column field="created_at" header="Erstellt am" body={dateBodyTemplate} sortable />
          <Column body={actionsBodyTemplate} header="Aktionen" style={{ width: '150px' }} />
        </DataTable>
      </div>
      
      {/* Create Project Dialog */}
      <Dialog
        header="Neues Projekt erstellen"
        visible={showCreateDialog}
        style={{ width: '500px' }}
        onHide={() => setShowCreateDialog(false)}
        footer={
          <div>
            <Button
              label="Abbrechen"
              icon="pi pi-times"
              onClick={() => setShowCreateDialog(false)}
              className="p-button-text"
            />
            <Button
              label="Erstellen"
              icon="pi pi-check"
              onClick={handleCreateProject}
              autoFocus
            />
          </div>
        }
      >
        <div className="create-project-form">
          <div className="field">
            <label htmlFor="projectName">Projektname *</label>
            <InputText
              id="projectName"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              placeholder="Mein Solar Projekt"
              className="w-full"
            />
          </div>
          
          <div className="field">
            <label htmlFor="projectType">Projekttyp</label>
            <Dropdown
              id="projectType"
              value={newProjectType}
              options={[
                { label: 'Solar', value: 'solar' },
                { label: 'Wärmepumpe', value: 'heatpump' },
                { label: 'Kombiniert', value: 'combined' }
              ]}
              onChange={(e) => setNewProjectType(e.value)}
              className="w-full"
            />
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default SolarProjects;
