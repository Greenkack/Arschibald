/**
 * Interactive Dashboard Component
 * 
 * Displays interactive result dashboards with customizable widgets.
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { Dropdown } from 'primereact/dropdown';
import './InteractiveDashboard.css';

interface DashboardWidget {
  id: string;
  type: string;
  title: string;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  data: any;
  config?: any;
}

interface Dashboard {
  id: string;
  name: string;
  description?: string;
  calculation_id: number;
  widgets: DashboardWidget[];
  layout: string;
  created_at: string;
  updated_at: string;
}

interface InteractiveDashboardProps {
  dashboardId?: string;
  calculationId?: number;
  calculationData?: any;
  onSave?: (dashboard: Dashboard) => void;
}

export const InteractiveDashboard: React.FC<InteractiveDashboardProps> = ({
  dashboardId,
  calculationId,
  calculationData,
  onSave
}) => {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [showWidgetDialog, setShowWidgetDialog] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState<DashboardWidget | null>(null);

  useEffect(() => {
    if (dashboardId) {
      loadDashboard(dashboardId);
    } else if (calculationId && calculationData) {
      createDefaultDashboard();
    }
  }, [dashboardId, calculationId]);

  const loadDashboard = async (id: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/results-visualization/dashboards/${id}`);
      const data = await response.json();
      setDashboard(data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const createDefaultDashboard = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/results-visualization/dashboards/default', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          calculation_id: calculationId,
          calculation_data: calculationData
        })
      });
      const data = await response.json();
      setDashboard(data);
    } catch (error) {
      console.error('Error creating dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderWidget = (widget: DashboardWidget) => {
    switch (widget.type) {
      case 'metric':
        return renderMetricWidget(widget);
      case 'chart':
        return renderChartWidget(widget);
      case 'table':
        return renderTableWidget(widget);
      case 'text':
        return renderTextWidget(widget);
      default:
        return <div>Unknown widget type: {widget.type}</div>;
    }
  };

  const renderMetricWidget = (widget: DashboardWidget) => {
    const { value, unit, formatted, trend } = widget.data;
    
    return (
      <div className="metric-widget">
        <div className="metric-value">
          {formatted || `${value} ${unit}`}
        </div>
        {trend && (
          <div className={`metric-trend trend-${trend}`}>
            <i className={`pi pi-arrow-${trend === 'up' ? 'up' : 'down'}`} />
          </div>
        )}
      </div>
    );
  };

  const renderChartWidget = (widget: DashboardWidget) => {
    const { chart_type, data } = widget.data;
    
    return (
      <div className="chart-widget">
        <div className="chart-placeholder">
          {chart_type} Chart
          {/* In production, integrate with actual chart library */}
        </div>
      </div>
    );
  };

  const renderTableWidget = (widget: DashboardWidget) => {
    return (
      <div className="table-widget">
        <div className="table-placeholder">
          Table Widget
          {/* In production, integrate with DataTable */}
        </div>
      </div>
    );
  };

  const renderTextWidget = (widget: DashboardWidget) => {
    return (
      <div className="text-widget">
        {widget.data.text || 'Text content'}
      </div>
    );
  };

  const handleSaveDashboard = async () => {
    if (!dashboard) return;

    try {
      const response = await fetch(`/api/v1/results-visualization/dashboards/${dashboard.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          widgets: dashboard.widgets,
          layout: dashboard.layout
        })
      });
      const data = await response.json();
      setDashboard(data);
      setEditMode(false);
      
      if (onSave) {
        onSave(data);
      }
    } catch (error) {
      console.error('Error saving dashboard:', error);
    }
  };

  const handleExport = async (format: string) => {
    if (!dashboard) return;

    try {
      const response = await fetch('/api/v1/results-visualization/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          visualization_id: dashboard.id,
          visualization_type: 'dashboard',
          format: format,
          include_charts: true,
          include_data: true,
          include_metadata: true
        })
      });
      const data = await response.json();
      console.log('Export data:', data);
      // Handle download
    } catch (error) {
      console.error('Error exporting dashboard:', error);
    }
  };

  if (loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>;
  }

  if (!dashboard) {
    return <div className="dashboard-empty">No dashboard available</div>;
  }

  return (
    <div className="interactive-dashboard">
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h2>{dashboard.name}</h2>
          {dashboard.description && (
            <p className="dashboard-description">{dashboard.description}</p>
          )}
        </div>
        
        <div className="dashboard-actions">
          <Button
            label={editMode ? 'Save' : 'Edit'}
            icon={editMode ? 'pi pi-check' : 'pi pi-pencil'}
            onClick={editMode ? handleSaveDashboard : () => setEditMode(true)}
            className="p-button-sm"
          />
          
          <Dropdown
            value={null}
            options={[
              { label: 'Export as PDF', value: 'pdf' },
              { label: 'Export as PNG', value: 'png' },
              { label: 'Export as JSON', value: 'json' }
            ]}
            onChange={(e) => handleExport(e.value)}
            placeholder="Export"
            className="export-dropdown"
          />
          
          <Button
            icon="pi pi-refresh"
            onClick={() => loadDashboard(dashboard.id)}
            className="p-button-sm p-button-text"
            tooltip="Refresh"
          />
        </div>
      </div>

      <div className={`dashboard-grid layout-${dashboard.layout}`}>
        {dashboard.widgets.map((widget) => (
          <Card
            key={widget.id}
            title={widget.title}
            className="dashboard-widget"
            style={{
              gridColumn: `${widget.position.x + 1} / span ${widget.position.width}`,
              gridRow: `${widget.position.y + 1} / span ${widget.position.height}`
            }}
          >
            {renderWidget(widget)}
            
            {editMode && (
              <div className="widget-edit-overlay">
                <Button
                  icon="pi pi-cog"
                  className="p-button-sm p-button-rounded"
                  onClick={() => {
                    setSelectedWidget(widget);
                    setShowWidgetDialog(true);
                  }}
                />
              </div>
            )}
          </Card>
        ))}
      </div>

      <Dialog
        header="Edit Widget"
        visible={showWidgetDialog}
        style={{ width: '50vw' }}
        onHide={() => setShowWidgetDialog(false)}
      >
        {selectedWidget && (
          <div className="widget-editor">
            <p>Widget: {selectedWidget.title}</p>
            <p>Type: {selectedWidget.type}</p>
            {/* Add widget configuration UI */}
          </div>
        )}
      </Dialog>
    </div>
  );
};
