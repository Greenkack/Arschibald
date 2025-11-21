/**
 * Update System Demo
 * 
 * Example integration of all update UI components
 */

import React, { useEffect } from 'react';
import { Toast } from 'primereact/toast';
import {
  UpdateNotification,
  UpdateProgress,
  UpdateReady,
  UpdatePreferences,
  ReleaseNotes
} from '../components/update';
import { useUpdate } from '../hooks/useUpdate';
import './UpdateSystemDemo.css';

export const UpdateSystemDemo: React.FC = () => {
  const toast = React.useRef<Toast>(null);
  const {
    updateAvailable,
    updateInfo,
    downloading,
    downloadProgress,
    updateReady,
    checking,
    error,
    preferences,
    checkForUpdates,
    downloadUpdate,
    installUpdate,
    skipVersion,
    cancelDownload,
    setPreferences,
    clearSkipVersion
  } = useUpdate();

  const [showNotification, setShowNotification] = React.useState(false);
  const [showProgress, setShowProgress] = React.useState(false);
  const [showReady, setShowReady] = React.useState(false);

  // Show notification when update is available
  useEffect(() => {
    if (updateAvailable && updateInfo) {
      setShowNotification(true);
    }
  }, [updateAvailable, updateInfo]);

  // Show progress when downloading
  useEffect(() => {
    if (downloading) {
      setShowProgress(true);
      setShowNotification(false);
    } else {
      setShowProgress(false);
    }
  }, [downloading]);

  // Show ready dialog when update is downloaded
  useEffect(() => {
    if (updateReady && updateInfo) {
      setShowReady(true);
      setShowProgress(false);
      
      toast.current?.show({
        severity: 'success',
        summary: 'Update Ready',
        detail: `Version ${updateInfo.version} is ready to install`,
        life: 5000
      });
    }
  }, [updateReady, updateInfo]);

  // Show error toast
  useEffect(() => {
    if (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Update Error',
        detail: error,
        life: 5000
      });
    }
  }, [error]);

  // Show checking toast
  useEffect(() => {
    if (checking) {
      toast.current?.show({
        severity: 'info',
        summary: 'Checking for Updates',
        detail: 'Please wait...',
        life: 3000
      });
    }
  }, [checking]);

  const handleDownload = () => {
    downloadUpdate();
  };

  const handleSkipVersion = () => {
    skipVersion();
    setShowNotification(false);
  };

  const handleRemindLater = () => {
    setShowNotification(false);
  };

  const handleCancelDownload = () => {
    cancelDownload();
  };

  const handleInstallNow = () => {
    installUpdate();
  };

  const handleInstallLater = () => {
    setShowReady(false);
    toast.current?.show({
      severity: 'info',
      summary: 'Update Scheduled',
      detail: 'Update will be installed when you close the application',
      life: 5000
    });
  };

  const handleSavePreferences = async (prefs: any) => {
    await setPreferences(prefs);
    toast.current?.show({
      severity: 'success',
      summary: 'Preferences Saved',
      detail: 'Update preferences have been saved',
      life: 3000
    });
  };

  const handleClearSkipVersion = () => {
    clearSkipVersion();
    toast.current?.show({
      severity: 'info',
      summary: 'Skip Version Cleared',
      detail: 'You will be notified about this version again',
      life: 3000
    });
  };

  const fetchReleaseNotes = async (version: string) => {
    // This would fetch from the update server
    // For demo purposes, return mock data
    return {
      version,
      releaseDate: new Date().toISOString(),
      notes: `
# What's New in Version ${version}

## New Features
- **Enhanced Performance**: Improved application startup time by 40%
- **New Dashboard**: Redesigned dashboard with better visualizations
- **Dark Mode**: Added full dark mode support

## Improvements
- Better error handling and user feedback
- Optimized memory usage
- Improved update system with better progress tracking

## Bug Fixes
- Fixed issue with PDF generation
- Resolved calculation errors in solar module placement
- Fixed memory leak in 3D visualization

## Technical Changes
- Updated to Electron 27
- Upgraded React to version 18.2
- Improved TypeScript type definitions
      `,
      channel: 'latest'
    };
  };

  return (
    <div className="update-system-demo">
      <Toast ref={toast} />

      <div className="demo-header">
        <h1>Update System Demo</h1>
        <p>
          This demo shows all update UI components and their integration with the
          auto-update system.
        </p>
      </div>

      <div className="demo-content">
        {/* Update Preferences */}
        {preferences && (
          <div className="demo-section">
            <h2>Update Preferences</h2>
            <UpdatePreferences
              preferences={preferences}
              currentVersion="1.0.0"
              onSave={handleSavePreferences}
              onCheckNow={checkForUpdates}
              onClearSkipVersion={handleClearSkipVersion}
            />
          </div>
        )}

        {/* Release Notes */}
        <div className="demo-section">
          <h2>Release Notes</h2>
          <ReleaseNotes
            version="1.1.0"
            onFetchNotes={fetchReleaseNotes}
          />
        </div>
      </div>

      {/* Update Notification Dialog */}
      <UpdateNotification
        visible={showNotification}
        updateInfo={updateInfo}
        onDownload={handleDownload}
        onSkipVersion={handleSkipVersion}
        onRemindLater={handleRemindLater}
        onClose={() => setShowNotification(false)}
      />

      {/* Update Progress Dialog */}
      <UpdateProgress
        visible={showProgress}
        progress={downloadProgress}
        version={updateInfo?.version || ''}
        onCancel={handleCancelDownload}
      />

      {/* Update Ready Dialog */}
      <UpdateReady
        visible={showReady}
        version={updateInfo?.version || ''}
        onInstallNow={handleInstallNow}
        onInstallLater={handleInstallLater}
      />
    </div>
  );
};
