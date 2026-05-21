/**
 * Update Ready Dialog
 * 
 * Displays when update is downloaded and ready to install
 */

import React from 'react';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import './UpdateReady.css';

interface UpdateReadyProps {
  visible: boolean;
  version: string;
  onInstallNow: () => void;
  onInstallLater: () => void;
}

export const UpdateReady: React.FC<UpdateReadyProps> = ({
  visible,
  version,
  onInstallNow,
  onInstallLater
}) => {
  const footer = (
    <div className="update-ready-footer">
      <Button
        label="Install on Quit"
        icon="pi pi-clock"
        onClick={onInstallLater}
        className="p-button-text"
      />
      <Button
        label="Restart and Install"
        icon="pi pi-refresh"
        onClick={onInstallNow}
        className="p-button-success"
        autoFocus
      />
    </div>
  );

  return (
    <Dialog
      header={
        <div className="update-ready-header">
          <i className="pi pi-check-circle mr-2" />
          <span>Update Ready to Install</span>
        </div>
      }
      visible={visible}
      style={{ width: '500px' }}
      footer={footer}
      onHide={onInstallLater}
      draggable={false}
      resizable={false}
      className="update-ready-dialog"
    >
      <div className="update-ready-content">
        <div className="update-ready-icon">
          <i className="pi pi-check-circle" />
        </div>

        <div className="update-ready-message">
          <h3>Version {version} is ready to install</h3>
          <p>
            The update has been downloaded successfully and is ready to be installed.
          </p>
        </div>

        <div className="update-ready-options">
          <div className="option-card">
            <div className="option-icon">
              <i className="pi pi-refresh" />
            </div>
            <div className="option-content">
              <h4>Restart and Install Now</h4>
              <p>
                The application will close, install the update, and restart automatically.
                Make sure to save your work first.
              </p>
            </div>
          </div>

          <div className="option-card">
            <div className="option-icon">
              <i className="pi pi-clock" />
            </div>
            <div className="option-content">
              <h4>Install on Quit</h4>
              <p>
                Continue working and the update will be installed automatically
                when you close the application.
              </p>
            </div>
          </div>
        </div>

        <div className="update-ready-info">
          <i className="pi pi-info-circle mr-2" />
          <span>
            Your settings and data will be preserved during the update.
          </span>
        </div>
      </div>
    </Dialog>
  );
};
