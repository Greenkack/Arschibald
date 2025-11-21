/**
 * Update Progress Dialog
 * 
 * Shows download progress with percentage, speed, and size information
 */

import React from 'react';
import { Dialog } from 'primereact/dialog';
import { ProgressBar } from 'primereact/progressbar';
import { Button } from 'primereact/button';
import './UpdateProgress.css';

interface ProgressInfo {
  percent: number;
  bytesPerSecond: number;
  transferred: number;
  total: number;
}

interface UpdateProgressProps {
  visible: boolean;
  progress: ProgressInfo | null;
  version: string;
  onCancel: () => void;
}

export const UpdateProgress: React.FC<UpdateProgressProps> = ({
  visible,
  progress,
  version,
  onCancel
}) => {
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  const formatSpeed = (bytesPerSecond: number): string => {
    return `${formatBytes(bytesPerSecond)}/s`;
  };

  const formatTime = (seconds: number): string => {
    if (!isFinite(seconds) || seconds < 0) return 'Calculating...';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const getEstimatedTime = (): string => {
    if (!progress || progress.bytesPerSecond === 0) {
      return 'Calculating...';
    }
    const remaining = progress.total - progress.transferred;
    const seconds = remaining / progress.bytesPerSecond;
    return formatTime(seconds);
  };

  const footer = (
    <div className="update-progress-footer">
      <Button
        label="Cancel Download"
        icon="pi pi-times"
        onClick={onCancel}
        className="p-button-text p-button-danger"
      />
    </div>
  );

  return (
    <Dialog
      header={
        <div className="update-progress-header">
          <i className="pi pi-download mr-2" />
          <span>Downloading Update</span>
        </div>
      }
      visible={visible}
      style={{ width: '500px' }}
      footer={footer}
      onHide={onCancel}
      draggable={false}
      resizable={false}
      closable={false}
      className="update-progress-dialog"
    >
      <div className="update-progress-content">
        <div className="update-version">
          <span className="version-label">Version:</span>
          <span className="version-number">{version}</span>
        </div>

        <div className="progress-section">
          <div className="progress-info">
            <span className="progress-percent">
              {progress ? `${Math.round(progress.percent)}%` : '0%'}
            </span>
            <span className="progress-size">
              {progress
                ? `${formatBytes(progress.transferred)} / ${formatBytes(progress.total)}`
                : 'Preparing...'}
            </span>
          </div>

          <ProgressBar
            value={progress?.percent || 0}
            showValue={false}
            className="update-progress-bar"
          />

          <div className="progress-details">
            <div className="progress-detail-item">
              <i className="pi pi-bolt mr-2" />
              <span className="detail-label">Speed:</span>
              <span className="detail-value">
                {progress ? formatSpeed(progress.bytesPerSecond) : 'N/A'}
              </span>
            </div>
            <div className="progress-detail-item">
              <i className="pi pi-clock mr-2" />
              <span className="detail-label">Time Remaining:</span>
              <span className="detail-value">{getEstimatedTime()}</span>
            </div>
          </div>
        </div>

        <div className="progress-message">
          <i className="pi pi-info-circle mr-2" />
          <span>
            You can continue working while the update downloads. The installation
            will begin when you close the application.
          </span>
        </div>
      </div>
    </Dialog>
  );
};
