/**
 * Update Notification Dialog
 * 
 * Displays when a new update is available with version info and release notes
 */

import React, { useState, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { Checkbox } from 'primereact/checkbox';
import { ScrollPanel } from 'primereact/scrollpanel';
import { Tag } from 'primereact/tag';
import './UpdateNotification.css';

interface UpdateInfo {
  version: string;
  releaseDate: string;
  releaseNotes?: string;
  releaseNotesUrl?: string;
  currentVersion: string;
  updateChannel?: string;
}

interface UpdateNotificationProps {
  visible: boolean;
  updateInfo: UpdateInfo | null;
  onDownload: () => void;
  onSkipVersion: () => void;
  onRemindLater: () => void;
  onClose: () => void;
}

export const UpdateNotification: React.FC<UpdateNotificationProps> = ({
  visible,
  updateInfo,
  onDownload,
  onSkipVersion,
  onRemindLater,
  onClose
}) => {
  const [skipThisVersion, setSkipThisVersion] = useState(false);

  useEffect(() => {
    if (!visible) {
      setSkipThisVersion(false);
    }
  }, [visible]);

  if (!updateInfo) return null;

  const handleSkip = () => {
    if (skipThisVersion) {
      onSkipVersion();
    } else {
      onRemindLater();
    }
    onClose();
  };

  const handleDownload = () => {
    onDownload();
    onClose();
  };

  const getChannelSeverity = (channel?: string) => {
    switch (channel) {
      case 'alpha':
        return 'danger';
      case 'beta':
        return 'warning';
      default:
        return 'success';
    }
  };

  const footer = (
    <div className="update-notification-footer">
      <div className="update-notification-skip">
        <Checkbox
          inputId="skip-version"
          checked={skipThisVersion}
          onChange={(e) => setSkipThisVersion(e.checked || false)}
        />
        <label htmlFor="skip-version" className="ml-2">
          Skip this version
        </label>
      </div>
      <div className="update-notification-actions">
        <Button
          label={skipThisVersion ? 'Skip Version' : 'Remind Me Later'}
          icon="pi pi-times"
          onClick={handleSkip}
          className="p-button-text"
        />
        <Button
          label="Download Update"
          icon="pi pi-download"
          onClick={handleDownload}
          className="p-button-primary"
          autoFocus
        />
      </div>
    </div>
  );

  return (
    <Dialog
      header={
        <div className="update-notification-header">
          <i className="pi pi-info-circle mr-2" />
          <span>Update Available</span>
          {updateInfo.updateChannel && updateInfo.updateChannel !== 'latest' && (
            <Tag
              value={updateInfo.updateChannel.toUpperCase()}
              severity={getChannelSeverity(updateInfo.updateChannel)}
              className="ml-2"
            />
          )}
        </div>
      }
      visible={visible}
      style={{ width: '600px' }}
      footer={footer}
      onHide={onClose}
      draggable={false}
      resizable={false}
      className="update-notification-dialog"
    >
      <div className="update-notification-content">
        <div className="update-version-info">
          <div className="version-comparison">
            <div className="version-item">
              <span className="version-label">Current Version</span>
              <span className="version-number">{updateInfo.currentVersion}</span>
            </div>
            <i className="pi pi-arrow-right version-arrow" />
            <div className="version-item">
              <span className="version-label">New Version</span>
              <span className="version-number version-new">{updateInfo.version}</span>
            </div>
          </div>
          <div className="release-date">
            <i className="pi pi-calendar mr-2" />
            Released: {new Date(updateInfo.releaseDate).toLocaleDateString()}
          </div>
        </div>

        {updateInfo.releaseNotes && (
          <div className="release-notes">
            <h4>What's New</h4>
            <ScrollPanel style={{ width: '100%', height: '200px' }}>
              <div
                className="release-notes-content"
                dangerouslySetInnerHTML={{ __html: updateInfo.releaseNotes }}
              />
            </ScrollPanel>
          </div>
        )}

        {updateInfo.releaseNotesUrl && (
          <div className="release-notes-link">
            <Button
              label="View Full Release Notes"
              icon="pi pi-external-link"
              className="p-button-link"
              onClick={() => window.open(updateInfo.releaseNotesUrl, '_blank')}
            />
          </div>
        )}

        <div className="update-info-message">
          <i className="pi pi-info-circle mr-2" />
          <span>
            The update will be downloaded in the background. You can continue working
            and install it when ready.
          </span>
        </div>
      </div>
    </Dialog>
  );
};
