/**
 * Dashboard Customizer Component
 * Allows users to customize dashboard layout with drag and drop
 */

import React, { useState } from 'react';
import { DraggableCard } from './DraggableCard';
import { DropZone } from './DropZone';
import { DragItem } from '../../hooks/useDragAndDrop';
import { Button } from 'primereact/button';
import './DashboardCustomizer.css';

export interface DashboardWidget {
  id: string;
  type: string;
  title: string;
  component: React.ComponentType<any>;
  props?: any;
  size?: 'small' | 'medium' | 'large';
}

export interface DashboardLayout {
  zones: {
    [key: string]: DashboardWidget[];
  };
}

export interface DashboardCustomizerProps {
  availableWidgets: DashboardWidget[];
  initialLayout: DashboardLayout;
  onLayoutChange: (layout: DashboardLayout) => void;
  zones: string[];
}

export const DashboardCustomizer: React.FC<DashboardCustomizerProps> = ({
  availableWidgets,
  initialLayout,
  onLayoutChange,
  zones,
}) => {
  const [layout, setLayout] = useState<DashboardLayout>(initialLayout);
  const [isCustomizing, setIsCustomizing] = useState(false);

  const handleDrop = (zoneId: string) => (item: DragItem) => {
    const widget = availableWidgets.find((w) => w.id === item.id);
    if (!widget) return;

    // Remove widget from all zones
    const newLayout = { ...layout };
    Object.keys(newLayout.zones).forEach((zone) => {
      newLayout.zones[zone] = newLayout.zones[zone].filter((w) => w.id !== widget.id);
    });

    // Add widget to target zone
    if (!newLayout.zones[zoneId]) {
      newLayout.zones[zoneId] = [];
    }
    newLayout.zones[zoneId].push(widget);

    setLayout(newLayout);
    onLayoutChange(newLayout);
  };

  const handleRemoveWidget = (zoneId: string, widgetId: string) => {
    const newLayout = { ...layout };
    newLayout.zones[zoneId] = newLayout.zones[zoneId].filter((w) => w.id !== widgetId);
    setLayout(newLayout);
    onLayoutChange(newLayout);
  };

  const handleResetLayout = () => {
    setLayout(initialLayout);
    onLayoutChange(initialLayout);
  };

  const getWidgetSizeClass = (size?: string) => {
    switch (size) {
      case 'small':
        return 'widget-small';
      case 'large':
        return 'widget-large';
      default:
        return 'widget-medium';
    }
  };

  return (
    <div className="dashboard-customizer">
      <div className="customizer-header">
        <h2>Dashboard Customization</h2>
        <div className="customizer-actions">
          <Button
            label={isCustomizing ? 'Done' : 'Customize'}
            icon={isCustomizing ? 'pi pi-check' : 'pi pi-cog'}
            onClick={() => setIsCustomizing(!isCustomizing)}
          />
          {isCustomizing && (
            <Button
              label="Reset"
              icon="pi pi-refresh"
              className="p-button-secondary"
              onClick={handleResetLayout}
            />
          )}
        </div>
      </div>

      {isCustomizing && (
        <div className="widget-palette">
          <h3>Available Widgets</h3>
          <div className="widget-palette-grid">
            {availableWidgets.map((widget) => {
              const isUsed = Object.values(layout.zones).some((zone) =>
                zone.some((w) => w.id === widget.id)
              );
              return (
                <DraggableCard
                  key={widget.id}
                  id={widget.id}
                  type="widget"
                  data={widget}
                  disabled={isUsed}
                  className="widget-palette-item"
                >
                  <div className="widget-preview">
                    <i className="pi pi-th-large"></i>
                    <span>{widget.title}</span>
                  </div>
                </DraggableCard>
              );
            })}
          </div>
        </div>
      )}

      <div className="dashboard-zones">
        {zones.map((zoneId) => (
          <div key={zoneId} className="dashboard-zone">
            <h3>{zoneId}</h3>
            <DropZone
              id={zoneId}
              accepts={['widget']}
              onDrop={handleDrop(zoneId)}
              disabled={!isCustomizing}
              emptyMessage={isCustomizing ? 'Drop widgets here' : 'No widgets'}
            >
              <div className="widget-grid">
                {layout.zones[zoneId]?.map((widget) => {
                  const WidgetComponent = widget.component;
                  return (
                    <div
                      key={widget.id}
                      className={`dashboard-widget ${getWidgetSizeClass(widget.size)}`}
                    >
                      {isCustomizing && (
                        <Button
                          icon="pi pi-times"
                          className="p-button-rounded p-button-danger p-button-text widget-remove"
                          onClick={() => handleRemoveWidget(zoneId, widget.id)}
                        />
                      )}
                      <div className="widget-content">
                        <h4>{widget.title}</h4>
                        <WidgetComponent {...widget.props} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </DropZone>
          </div>
        ))}
      </div>
    </div>
  );
};
