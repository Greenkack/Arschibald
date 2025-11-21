/**
 * Update Preferences Component
 * 
 * Allows users to configure update settings
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { InputSwitch } from 'primereact/inputswitch';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { Divider } from 'primereact/divider';
import './UpdatePreferences.css';

interface UpdatePreferencesData {
  autoDownload: boolean;
  autoInstallOnAppQuit: boolean;
  checkOnStartup: boolean;
  checkInterval: number;
  updateChannel: string;
  skipVersion: string | null;
  notifyOnNoUpdate: boolean;
}

interface UpdatePreferencesProps {
  preferences: UpdatePreferencesData;
  currentVersion: string;
  onSave: (preferences: UpdatePreferencesData) => Promise<void>;
  onCheckNow: () => void;
  onClearSkipVersion: () => void;
}

export const UpdatePreferences: React.FC<UpdatePreferencesProps> = ({
  preferences: initialPreferences,
  currentVersion,
  onSave,
  onCheckNow,
  onClearSkipVersion
}) => {
  const [preferences, setPreferences] = useState<UpdatePreferencesData>(initialPreferences);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setPreferences(initialPreferences);
  }, [initialPreferences]);

  useEffect(() => {
    const changed = JSON.stringify(preferences) !== JSON.stringify(initialPreferences);
    setHasChanges(changed);
    if (changed) {
      setSaved(false);
    }
  }, [preferences, initialPreferences]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(preferences);
      setSaved(true);
      setHasChanges(false);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setPreferences(initialPreferences);
  };

  const updateChannelOptions = [
    { label: 'Stable (Recommended)', value: 'latest', description: 'Production releases' },
    { label: 'Beta', value: 'beta', description: 'Pre-release versions' },
    { label: 'Alpha', value: 'alpha', description: 'Development builds' }
  ];

  const checkIntervalOptions = [
    { label: 'Every 15 minutes', value: 900000 },
    { label: 'Every 30 minutes', value: 1800000 },
    { label: 'Every hour', value: 3600000 },
    { label: 'Every 4 hours', value: 14400000 },
    { label: 'Every 12 hours', value: 43200000 },
    { label: 'Once a day', value: 86400000 }
  ];

  const channelTemplate = (option: any) => {
    return (
      <div className="channel-option">
        <div className="channel-label">{option.label}</div>
        <div className="channel-description">{option.description}</div>
      </div>
    );
  };

  return (
    <div className="update-preferences">
      <Card title="Update Settings" className="preferences-card">
        <div className="preferences-section">
          <div className="preference-item">
            <div className="preference-info">
              <label htmlFor="auto-download">Automatic Download</label>
              <span className="preference-description">
                Automatically download updates when available
              </span>
            </div>
            <InputSwitch
              inputId="auto-download"
              checked={preferences.autoDownload}
              onChange={(e) => setPreferences({ ...preferences, autoDownload: e.value })}
            />
          </div>

          <Divider />

          <div className="preference-item">
            <div className="preference-info">
              <label htmlFor="auto-install">Install on Quit</label>
              <span className="preference-description">
                Automatically install updates when closing the application
              </span>
            </div>
            <InputSwitch
              inputId="auto-install"
              checked={preferences.autoInstallOnAppQuit}
              onChange={(e) =>
                setPreferences({ ...preferences, autoInstallOnAppQuit: e.value })
              }
            />
          </div>

          <Divider />

          <div className="preference-item">
            <div className="preference-info">
              <label htmlFor="check-startup">Check on Startup</label>
              <span className="preference-description">
                Check for updates when the application starts
              </span>
            </div>
            <InputSwitch
              inputId="check-startup"
              checked={preferences.checkOnStartup}
              onChange={(e) => setPreferences({ ...preferences, checkOnStartup: e.value })}
            />
          </div>

          <Divider />

          <div className="preference-item">
            <div className="preference-info">
              <label htmlFor="notify-no-update">Notify When No Update</label>
              <span className="preference-description">
                Show notification when no updates are available
              </span>
            </div>
            <InputSwitch
              inputId="notify-no-update"
              checked={preferences.notifyOnNoUpdate}
              onChange={(e) =>
                setPreferences({ ...preferences, notifyOnNoUpdate: e.value })
              }
            />
          </div>
        </div>

        <Divider />

        <div className="preferences-section">
          <div className="preference-item-vertical">
            <label htmlFor="update-channel">Update Channel</label>
            <Dropdown
              inputId="update-channel"
              value={preferences.updateChannel}
              options={updateChannelOptions}
              onChange={(e) => setPreferences({ ...preferences, updateChannel: e.value })}
              itemTemplate={channelTemplate}
              className="w-full"
            />
            <span className="preference-description">
              Choose which type of updates you want to receive
            </span>
          </div>

          <div className="preference-item-vertical">
            <label htmlFor="check-interval">Check Frequency</label>
            <Dropdown
              inputId="check-interval"
              value={preferences.checkInterval}
              options={checkIntervalOptions}
              onChange={(e) => setPreferences({ ...preferences, checkInterval: e.value })}
              className="w-full"
            />
            <span className="preference-description">
              How often to check for new updates
            </span>
          </div>
        </div>

        {preferences.skipVersion && (
          <>
            <Divider />
            <div className="preferences-section">
              <Message
                severity="info"
                text={`You are skipping version ${preferences.skipVersion}`}
                className="w-full"
              />
              <Button
                label="Clear Skipped Version"
                icon="pi pi-times"
                onClick={onClearSkipVersion}
                className="p-button-text p-button-sm mt-2"
              />
            </div>
          </>
        )}

        <Divider />

        <div className="preferences-actions">
          <div className="current-version">
            <span className="version-label">Current Version:</span>
            <span className="version-number">{currentVersion}</span>
          </div>
          <div className="action-buttons">
            <Button
              label="Check for Updates"
              icon="pi pi-refresh"
              onClick={onCheckNow}
              className="p-button-outlined"
            />
            {hasChanges && (
              <>
                <Button
                  label="Reset"
                  icon="pi pi-undo"
                  onClick={handleReset}
                  className="p-button-text"
                />
                <Button
                  label="Save Changes"
                  icon="pi pi-check"
                  onClick={handleSave}
                  loading={saving}
                  className="p-button-success"
                />
              </>
            )}
          </div>
        </div>

        {saved && (
          <Message
            severity="success"
            text="Preferences saved successfully"
            className="mt-3"
          />
        )}
      </Card>
    </div>
  );
};
