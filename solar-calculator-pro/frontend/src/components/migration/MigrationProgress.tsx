/**
 * Migration Progress Component
 * Displays real-time progress of migration process
 * Requirements: 5.5
 */

import React from 'react';
import { ProgressBar } from 'primereact/progressbar';
import { Card } from 'primereact/card';
import { Timeline } from 'primereact/timeline';
import { Badge } from 'primereact/badge';
import './MigrationProgress.css';

interface MigrationProgressProps {
  progress: number;
  currentStep: string;
  details: {
    step: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    message: string;
    startTime?: string;
    endTime?: string;
    itemsProcessed?: number;
    totalItems?: number;
  }[];
}

export const MigrationProgress: React.FC<MigrationProgressProps> = ({
  progress,
  currentStep,
  details
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return 'pi pi-check-circle text-green-500';
      case 'running':
        return 'pi pi-spin pi-spinner text-blue-500';
      case 'failed':
        return 'pi pi-times-circle text-red-500';
      default:
        return 'pi pi-circle text-gray-400';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'info';
      case 'failed':
        return 'danger';
      default:
        return 'secondary';
    }
  };

  const formatDuration = (startTime?: string, endTime?: string) => {
    if (!startTime) return '';
    
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const duration = Math.floor((end.getTime() - start.getTime()) / 1000);
    
    if (duration < 60) {
      return `${duration}s`;
    } else {
      const minutes = Math.floor(duration / 60);
      const seconds = duration % 60;
      return `${minutes}m ${seconds}s`;
    }
  };

  const customizedMarker = (item: any) => {
    return (
      <span className={`custom-marker ${getStatusIcon(item.status)}`}>
        <i className={getStatusIcon(item.status)} />
      </span>
    );
  };

  const customizedContent = (item: any) => {
    return (
      <Card className="migration-step-card">
        <div className="step-header">
          <h4>{item.step}</h4>
          <Badge
            value={item.status}
            severity={getStatusColor(item.status)}
          />
        </div>
        <p className="step-message">{item.message}</p>
        
        {item.itemsProcessed !== undefined && item.totalItems !== undefined && (
          <div className="step-progress">
            <span className="progress-text">
              {item.itemsProcessed} / {item.totalItems} Elemente
            </span>
            <ProgressBar
              value={(item.itemsProcessed / item.totalItems) * 100}
              showValue={false}
            />
          </div>
        )}
        
        {item.startTime && (
          <div className="step-timing">
            <i className="pi pi-clock" />
            <span>{formatDuration(item.startTime, item.endTime)}</span>
          </div>
        )}
      </Card>
    );
  };

  return (
    <div className="migration-progress">
      <Card title="Migrationsfortschritt">
        <div className="overall-progress">
          <div className="progress-header">
            <span className="current-step">{currentStep}</span>
            <span className="progress-percentage">{progress}%</span>
          </div>
          <ProgressBar
            value={progress}
            showValue={false}
            className="overall-progress-bar"
          />
        </div>

        <div className="step-timeline">
          <Timeline
            value={details}
            align="alternate"
            className="migration-timeline"
            marker={customizedMarker}
            content={customizedContent}
          />
        </div>
      </Card>
    </div>
  );
};
