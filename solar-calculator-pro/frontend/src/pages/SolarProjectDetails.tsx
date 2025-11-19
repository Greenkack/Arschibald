/**
 * Solar Project Details Page
 * 
 * Detailed view of a single project with:
 * - Project information display
 * - Calculation results display
 * - 3D visualization integration
 * - Edit and delete actions
 * - PDF generation button
 * 
 * Requirements: 7.1
 */

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Tag } from 'primereact/tag';
import { Divider } from 'primereact/divider';
import { ProgressSpinner } from 'primereact/progressspinner';
import { TabView, TabPanel } from 'primereact/tabview';
import SolarCalculationResults from '../components/solar/SolarCalculationResults';
import { Viewer3D } from '../components/3d/Viewer3D';
import api from '../services/api';
import './SolarProjectDetails.css';

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

interface SolarCalculationResponse {
  calculation_id?: string;
  calculation_timestamp: string;
  system_sizing: {
    system_size_kwp: number;
    module_count: number;
    module_capacity_w: number;
    total_roof_area_required_m2?: number;
    specific_yield_kwh_kwp: number;
  };
  energy_production: {
    annual_production_kwh: number;
    monthly_production_kwh: any;
    pvgis_data_used: boolean;
    pvgis_source: string;
  };
  self_consumption: {
    annual_self_consumption_kwh: number;
    self_consumption_rate_percent: number;
    autarky_degree_percent: number;
    annual_grid_feed_in_kwh: number;
    annual_grid_purchase_kwh: number;
    monthly_self_consumption_kwh?: any;
  };
  economic_analysis: {
    total_investment_cost_net: number;
    total_investment_cost_gross: number;
    annual_savings_year1: number;
    payback_period_years: number;
    total_savings_20years: number;
    total_savings_25years: number;
    net_present_value?: number;
    internal_rate_of_return_percent?: number;
    annual_feed_in_revenue: number;
  };
  environmental_impact: {
    annual_co2_savings_kg: number;
    total_co2_savings_25years_kg: number;
    equivalent_trees: number;
    equivalent_car_km: number;
    co2_payback_time_years?: number;
  };
  storage_analysis?: {
    storage_capacity_kwh: number;
    storage_efficiency_percent: number;
    annual_storage_cycles: number;
    additional_self_consumption_kwh: number;
    storage_contribution_to_autarky_percent: number;
  };
  warnings: string[];
  errors: string[];
}

const SolarProjectDetails: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const toast = useRef<Toast>(null);
  
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [generatingPDF, setGeneratingPDF] = useState(false);
  
  // Load project details
  useEffect(() => {
    loadProject();
  }, [projectId]);
  
  const loadProject = async () => {
    if (!projectId) return;
    
    setLoading(true);
    
    try {
      const response = await api.get<Project>(`/api/v1/solar/projects/${projectId}`);
      setProject(response.data);
    } catch (error: any) {
      console.error('Failed to load project:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: error.response?.data?.detail || 'Projekt konnte nicht geladen werden',
        life: 5000
      });
      
      // Navigate back if project not found
      if (error.response?.status === 404) {
        setTimeout(() => navigate('/solar-projects'), 2000);
      }
    } finally {
      setLoading(false);
    }
  };
  
  const handleEdit = () => {
    navigate(`/solar-projects/${projectId}/edit`);
  };
  
  const handleDelete = () => {
    if (!project) return;
    
    confirmDialog({
      message: `Möchten Sie das Projekt "${project.name}" wirklich löschen?`,
      header: 'Löschen bestätigen',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Ja, löschen',
      rejectLabel: 'Abbrechen',
      acceptClassName: 'p-button-danger',
      accept: async () => {
        try {
          await api.delete(`/api/v1/solar/projects/${projectId}`);
          
          toast.current?.show({
            severity: 'success',
            summary: 'Erfolg',
            detail: 'Projekt wurde gelöscht',
            life: 3000
          });
          
          setTimeout(() => navigate('/solar-projects'), 1000);
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
  
  const handleGeneratePDF = async () => {
    if (!project || !projectId) return;
    
    setGeneratingPDF(true);
    
    try {
      // Call PDF generation API
      const response = await api.post(`/api/v1/pdf/generate`, {
        project_id: parseInt(projectId),
        template: 'solar_offer',
        options: {
          include_3d: true,
          include_charts: true,
          language: 'de'
        }
      }, {
        responseType: 'blob'
      });
      
      // Create download link
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${project.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.current?.show({
        severity: 'success',
        summary: 'Erfolg',
        detail: 'PDF wurde erfolgreich erstellt und heruntergeladen',
        life: 3000
      });
    } catch (error: any) {
      console.error('Failed to generate PDF:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: error.response?.data?.detail || 'PDF konnte nicht erstellt werden',
        life: 5000
      });
    } finally {
      setGeneratingPDF(false);
    }
  };
  
  const handleView3D = () => {
    setActiveTab(2); // Switch to 3D visualization tab
  };
  
  const handleEditCalculation = () => {
    navigate('/solar-calculator', { state: { projectId, projectData: project?.data } });
  };
  
  // Check if project has calculation results
  const hasCalculationResults = () => {
    return project?.data?.calculation_results && 
           Object.keys(project.data.calculation_results).length > 0;
  };
  
  // Get calculation results from project data
  const getCalculationResults = (): SolarCalculationResponse | null => {
    if (!hasCalculationResults()) return null;
    return project?.data?.calculation_results || null;
  };
  
  // Get 3D visualization data from project
  const get3DVisualizationData = () => {
    const data = project?.data?.input_data || {};
    return {
      roofType: data.roof_type || 'flat',
      roofWidth: data.roof_width || 10,
      roofLength: data.roof_length || 10,
      roofHeight: data.roof_height || 3,
      roofAngle: data.roof_angle || 30,
      moduleCount: project?.data?.calculation_results?.system_sizing?.module_count || 20
    };
  };
  
  const getStatusConfig = (status: string) => {
    const configs: Record<string, { label: string; severity: any }> = {
      draft: { label: 'Entwurf', severity: 'info' },
      active: { label: 'Aktiv', severity: 'success' },
      completed: { label: 'Abgeschlossen', severity: 'warning' },
      archived: { label: 'Archiviert', severity: 'secondary' }
    };
    
    return configs[status] || { label: status, severity: 'info' };
  };
  
  const getProjectTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      solar: 'Solar',
      heatpump: 'Wärmepumpe',
      combined: 'Kombiniert'
    };
    
    return labels[type] || type;
  };
  
  if (loading) {
    return (
      <div className="solar-project-details-page loading-container">
        <ProgressSpinner />
        <p>Projekt wird geladen...</p>
      </div>
    );
  }
  
  if (!project) {
    return (
      <div className="solar-project-details-page error-container">
        <i className="pi pi-exclamation-circle" style={{ fontSize: '3rem', color: '#dc3545' }} />
        <h2>Projekt nicht gefunden</h2>
        <Button
          label="Zurück zur Übersicht"
          icon="pi pi-arrow-left"
          onClick={() => navigate('/solar-projects')}
        />
      </div>
    );
  }
  
  const statusConfig = getStatusConfig(project.status);
  
  const calculationResults = getCalculationResults();
  const visualizationData = get3DVisualizationData();
  
  return (
    <div className="solar-project-details-page">
      <Toast ref={toast} />
      <ConfirmDialog />
      
      {/* Header */}
      <div className="page-header">
        <div className="header-left">
          <Button
            icon="pi pi-arrow-left"
            className="p-button-text"
            onClick={() => navigate('/solar-projects')}
            tooltip="Zurück"
          />
          <div className="header-info">
            <h1>{project.name}</h1>
            <div className="header-meta">
              <Tag value={statusConfig.label} severity={statusConfig.severity} />
              <span className="project-type">{getProjectTypeLabel(project.project_type)}</span>
              <span className="project-key">{project.dynamic_key}</span>
            </div>
          </div>
        </div>
        <div className="header-actions">
          {hasCalculationResults() && (
            <>
              <Button
                label="3D-Ansicht"
                icon="pi pi-box"
                className="p-button-info"
                onClick={handleView3D}
                disabled={!hasCalculationResults()}
              />
              <Button
                label="PDF erstellen"
                icon="pi pi-file-pdf"
                className="p-button-secondary"
                onClick={handleGeneratePDF}
                loading={generatingPDF}
                disabled={!hasCalculationResults()}
              />
            </>
          )}
          <Button
            label="Bearbeiten"
            icon="pi pi-pencil"
            className="p-button-warning"
            onClick={handleEdit}
          />
          <Button
            label="Löschen"
            icon="pi pi-trash"
            className="p-button-danger"
            onClick={handleDelete}
          />
        </div>
      </div>
      
      {/* Content with Tabs */}
      <div className="page-content">
        <TabView activeIndex={activeTab} onTabChange={(e) => setActiveTab(e.index)}>
          {/* Project Information Tab */}
          <TabPanel header="Projektinformationen" leftIcon="pi pi-info-circle">
            <div className="content-grid">
              <Card title="Projektdetails" className="info-card">
                <div className="info-grid">
                  <div className="info-item">
                    <label>Projekt-ID</label>
                    <span>{project.id}</span>
                  </div>
                  <div className="info-item">
                    <label>Projekttyp</label>
                    <span>{getProjectTypeLabel(project.project_type)}</span>
                  </div>
                  <div className="info-item">
                    <label>Status</label>
                    <Tag value={statusConfig.label} severity={statusConfig.severity} />
                  </div>
                  <div className="info-item">
                    <label>Kunden-ID</label>
                    <span>{project.customer_id}</span>
                  </div>
                  <div className="info-item">
                    <label>Dynamischer Schlüssel</label>
                    <span className="monospace">{project.dynamic_key}</span>
                  </div>
                  <div className="info-item">
                    <label>Erstellt am</label>
                    <span>{new Date(project.created_at).toLocaleString('de-DE')}</span>
                  </div>
                  {project.updated_at && (
                    <div className="info-item">
                      <label>Aktualisiert am</label>
                      <span>{new Date(project.updated_at).toLocaleString('de-DE')}</span>
                    </div>
                  )}
                </div>
              </Card>
              
              {/* Input Data Summary */}
              {project.data?.input_data && (
                <Card title="Eingabedaten" className="input-data-card">
                  <div className="info-grid">
                    {project.data.input_data.roof_area && (
                      <div className="info-item">
                        <label>Dachfläche</label>
                        <span>{project.data.input_data.roof_area} m²</span>
                      </div>
                    )}
                    {project.data.input_data.roof_type && (
                      <div className="info-item">
                        <label>Dachtyp</label>
                        <span>{project.data.input_data.roof_type}</span>
                      </div>
                    )}
                    {project.data.input_data.roof_angle && (
                      <div className="info-item">
                        <label>Dachneigung</label>
                        <span>{project.data.input_data.roof_angle}°</span>
                      </div>
                    )}
                    {project.data.input_data.orientation && (
                      <div className="info-item">
                        <label>Ausrichtung</label>
                        <span>{project.data.input_data.orientation}</span>
                      </div>
                    )}
                    {project.data.input_data.annual_consumption && (
                      <div className="info-item">
                        <label>Jahresverbrauch</label>
                        <span>{project.data.input_data.annual_consumption} kWh</span>
                      </div>
                    )}
                    {project.data.input_data.location && (
                      <div className="info-item">
                        <label>Standort</label>
                        <span>{project.data.input_data.location}</span>
                      </div>
                    )}
                  </div>
                </Card>
              )}
            </div>
          </TabPanel>
          
          {/* Calculation Results Tab */}
          <TabPanel header="Berechnungsergebnisse" leftIcon="pi pi-chart-line">
            {hasCalculationResults() && calculationResults ? (
              <SolarCalculationResults
                results={calculationResults}
                onEdit={handleEditCalculation}
                onGeneratePDF={handleGeneratePDF}
                onView3D={handleView3D}
              />
            ) : (
              <Card className="no-results-card">
                <div className="no-results-content">
                  <i className="pi pi-chart-line" style={{ fontSize: '4rem', color: '#94a3b8' }} />
                  <h3>Keine Berechnungsergebnisse vorhanden</h3>
                  <p>
                    Führen Sie eine Berechnung durch, um detaillierte Ergebnisse, Diagramme und 
                    Wirtschaftlichkeitsanalysen anzuzeigen.
                  </p>
                  <Button
                    label="Neue Berechnung starten"
                    icon="pi pi-calculator"
                    onClick={() => navigate('/solar-calculator', { state: { projectId } })}
                    className="p-button-lg"
                  />
                </div>
              </Card>
            )}
          </TabPanel>
          
          {/* 3D Visualization Tab */}
          <TabPanel header="3D-Visualisierung" leftIcon="pi pi-box">
            {hasCalculationResults() ? (
              <div className="visualization-container">
                <Viewer3D
                  roofType={visualizationData.roofType as 'flat' | 'gable' | 'hip'}
                  roofWidth={visualizationData.roofWidth}
                  roofLength={visualizationData.roofLength}
                  roofHeight={visualizationData.roofHeight}
                  roofAngle={visualizationData.roofAngle}
                  moduleCount={visualizationData.moduleCount}
                />
                <Card className="visualization-info-card">
                  <h3>Visualisierungsdetails</h3>
                  <Divider />
                  <div className="info-grid">
                    <div className="info-item">
                      <label>Dachtyp</label>
                      <span>{visualizationData.roofType}</span>
                    </div>
                    <div className="info-item">
                      <label>Dachbreite</label>
                      <span>{visualizationData.roofWidth} m</span>
                    </div>
                    <div className="info-item">
                      <label>Dachlänge</label>
                      <span>{visualizationData.roofLength} m</span>
                    </div>
                    <div className="info-item">
                      <label>Dachhöhe</label>
                      <span>{visualizationData.roofHeight} m</span>
                    </div>
                    <div className="info-item">
                      <label>Dachneigung</label>
                      <span>{visualizationData.roofAngle}°</span>
                    </div>
                    <div className="info-item">
                      <label>Modulanzahl</label>
                      <span>{visualizationData.moduleCount} Module</span>
                    </div>
                  </div>
                </Card>
              </div>
            ) : (
              <Card className="no-visualization-card">
                <div className="no-results-content">
                  <i className="pi pi-box" style={{ fontSize: '4rem', color: '#94a3b8' }} />
                  <h3>Keine 3D-Visualisierung verfügbar</h3>
                  <p>
                    Führen Sie zuerst eine Berechnung durch, um die 3D-Visualisierung 
                    Ihrer PV-Anlage anzuzeigen.
                  </p>
                  <Button
                    label="Berechnung starten"
                    icon="pi pi-calculator"
                    onClick={() => navigate('/solar-calculator', { state: { projectId } })}
                    className="p-button-lg"
                  />
                </div>
              </Card>
            )}
          </TabPanel>
        </TabView>
      </div>
    </div>
  );
};

export default SolarProjectDetails;
