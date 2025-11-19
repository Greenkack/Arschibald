/**
 * Logging Configuration Component
 * 
 * Logging settings and log file management
 */

import React, { useState, useEffect } from 'react';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { InputSwitch } from 'primereact/inputswitch';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Dialog } from 'primereact/dialog';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import api from '@services/api';

interface LoggingSettingsData {
  log_level: string;
  log_to_file: boolean;
  log_to_console: boolean;
  log_file_path: string;
  max_log_file_size_mb: number;
  log_file_retention_days: number;
  log_rotation_enabled: boolean;
  log_format: string;
  log_api_requests: boolean;
  log_database_queries: boolean;
  log_errors_only: boolean;
  enable_debug_mode: boolean;
  current_log_size_mb: number;
  total_log_files: number;
  updated_at: string;
}

interface LogFileInfo {
  filename: string;
  size_mb: number;
  created_at: string;
  modified_at: string;
  lines: number;
}

interface LoggingConfigurationProps {
  onUpdate?: () => void;
}

const LoggingConfiguration: React.FC<LoggingConfigurationProps> = ({ onUpdate }) => {
  const [settings, setSettings] = useState<LoggingSettingsData | null>(null);
  const [logFiles, setLogFiles] = useState<LogFileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showLogFiles, setShowLogFiles] = useState(false);
  const [message, setMessage] = useState<{ severity: 'success' | 'error' | 'info' | 'warn'; text: string } | null>(null);

  const logLevelOptions = [
    { label: 'DEBUG', value: 'DEBUG' },
    { label: 'INFO', value: 'INFO' },
    { label: 'WARNING', value: 'WARNING' },
    { label: 'ERROR', value: 'ERROR' },
    { label: 'CRITICAL', value: 'CRITICAL' },
  ];

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/system-settings/logging');
      setSettings(response.data);
    } catch (error: any) {
      setMessage({
        severity: 'error',
        text: `Failed to load settings: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const loadLogFiles = async () => {
    try {
      const response = await api.get('/api/v1/system-settings/logging/files');
      setLogFiles(response.data.log_files);
    } catch (error: any) {
      setMessage({
        severity: 'error',
        text: `Failed to load log files: ${error.response?.data?.detail || error.message}`
      });
    }
  };

  const handleSave = async () => {
    if (!settings) return;

    try {
      setSaving(true);
      setMessage(null);
      
      const response = await api.put('/api/v1/system-settings/logging', settings);
      setSettings(response.data);
      
      setMessage({
        severity: 'success',
        text: 'Logging settings saved successfully'
      });
      
      if (settings.enable_debug_mode) {
        setMessage({
          severity: 'warn',
          text: 'Debug mode enabled. This may impact performance and generate large log files.'
        });
      }
      
      if (onUpdate) {
        onUpdate();
      }
    } catch (error: any) {
      setMessage({
        severity: 'error',
        text: `Failed to save settings: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setSaving(false);
    }
  };

  const handleShowLogFiles = () => {
    setShowLogFiles(true);
    loadLogFiles();
  };

  const handleReset = () => {
    loadSettings();
    setMessage(null);
  };

  const formatBytes = (mb: number) => {
    if (mb < 1) {
      return `${(mb * 1024).toFixed(2)} KB`;
    } else if (mb > 1024) {
      return `${(mb / 1024).toFixed(2)} GB`;
    }
    return `${mb.toFixed(2)} MB`;
  };

  const sizeBodyTemplate = (rowData: LogFileInfo) => {
    return formatBytes(rowData.size_mb);
  };

  const dateBodyTemplate = (rowData: LogFileInfo) => {
    return new Date(rowData.modified_at).toLocaleString();
  };

  const linesBodyTemplate = (rowData: LogFileInfo) => {
    return rowData.lines.toLocaleString();
  };

  if (loading) {
    return (
      <div className="settings-loading">
        <ProgressSpinner />
        <p>Loading logging settings...</p>
      </div>
    );
  }

  if (!settings) {
    return <Message severity="error" text="Failed to load settings" />;
  }

  return (
    <div className="logging-configuration">
      {message && (
        <Message 
          severity={message.severity} 
          text={message.text} 
          className="settings-message"
        />
      )}

      <div className="settings-section">
        <h3>Log Level</h3>
        
        <div className="p-field">
          <label htmlFor="log_level">Log Level</label>
          <Dropdown
            id="log_level"
            value={settings.log_level}
            options={logLevelOptions}
            onChange={(e) => setSettings({ ...settings, log_level: e.value })}
            className="w-full"
          />
          <small>
            DEBUG: All messages | INFO: Informational and above | WARNING: Warnings and errors | ERROR: Errors only | CRITICAL: Critical errors only
          </small>
        </div>

        <div className="p-field-checkbox">
          <InputSwitch
            id="enable_debug_mode"
            checked={settings.enable_debug_mode}
            onChange={(e) => setSettings({ ...settings, enable_debug_mode: e.value })}
          />
          <label htmlFor="enable_debug_mode">Enable Debug Mode</label>
          <small>Enables verbose logging for troubleshooting (may impact performance)</small>
        </div>
      </div>

      <div className="settings-section">
        <h3>Log Destinations</h3>
        
        <div className="p-field-checkbox">
          <InputSwitch
            id="log_to_file"
            checked={settings.log_to_file}
            onChange={(e) => setSettings({ ...settings, log_to_file: e.value })}
          />
          <label htmlFor="log_to_file">Log to File</label>
        </div>

        <div className="p-field-checkbox">
          <InputSwitch
            id="log_to_console"
            checked={settings.log_to_console}
            onChange={(e) => setSettings({ ...settings, log_to_console: e.value })}
          />
          <label htmlFor="log_to_console">Log to Console</label>
        </div>

        <div className="p-field">
          <label htmlFor="log_file_path">Log File Path</label>
          <InputText
            id="log_file_path"
            value={settings.log_file_path}
            onChange={(e) => setSettings({ ...settings, log_file_path: e.target.value })}
            disabled={!settings.log_to_file}
            className="w-full"
          />
        </div>
      </div>

      <div className="settings-section">
        <h3>Log Rotation</h3>
        
        <div className="p-field-checkbox">
          <InputSwitch
            id="log_rotation_enabled"
            checked={settings.log_rotation_enabled}
            onChange={(e) => setSettings({ ...settings, log_rotation_enabled: e.value })}
          />
          <label htmlFor="log_rotation_enabled">Enable Log Rotation</label>
        </div>

        <div className="p-field">
          <label htmlFor="max_log_file_size_mb">Maximum Log File Size (MB)</label>
          <InputNumber
            id="max_log_file_size_mb"
            value={settings.max_log_file_size_mb}
            onValueChange={(e) => setSettings({ ...settings, max_log_file_size_mb: e.value || 100 })}
            min={1}
            max={1000}
            disabled={!settings.log_rotation_enabled}
            className="w-full"
          />
          <small>Rotate log file when it reaches this size</small>
        </div>

        <div className="p-field">
          <label htmlFor="log_file_retention_days">Log File Retention (days)</label>
          <InputNumber
            id="log_file_retention_days"
            value={settings.log_file_retention_days}
            onValueChange={(e) => setSettings({ ...settings, log_file_retention_days: e.value || 30 })}
            min={1}
            max={365}
            disabled={!settings.log_rotation_enabled}
            className="w-full"
          />
          <small>Delete log files older than this</small>
        </div>
      </div>

      <div className="settings-section">
        <h3>Log Content</h3>
        
        <div className="p-field-checkbox">
          <InputSwitch
            id="log_api_requests"
            checked={settings.log_api_requests}
            onChange={(e) => setSettings({ ...settings, log_api_requests: e.value })}
          />
          <label htmlFor="log_api_requests">Log API Requests</label>
          <small>Log all incoming API requests</small>
        </div>

        <div className="p-field-checkbox">
          <InputSwitch
            id="log_database_queries"
            checked={settings.log_database_queries}
            onChange={(e) => setSettings({ ...settings, log_database_queries: e.value })}
          />
          <label htmlFor="log_database_queries">Log Database Queries</label>
          <small>Log all database queries (may generate large logs)</small>
        </div>

        <div className="p-field-checkbox">
          <InputSwitch
            id="log_errors_only"
            checked={settings.log_errors_only}
            onChange={(e) => setSettings({ ...settings, log_errors_only: e.value })}
          />
          <label htmlFor="log_errors_only">Log Errors Only</label>
          <small>Only log errors and critical messages</small>
        </div>

        <div className="p-field">
          <label htmlFor="log_format">Log Format</label>
          <InputText
            id="log_format"
            value={settings.log_format}
            onChange={(e) => setSettings({ ...settings, log_format: e.target.value })}
            className="w-full"
          />
          <small>Python logging format string</small>
        </div>
      </div>

      <div className="settings-section">
        <h3>Current Status</h3>
        <div className="log-status">
          <div className="status-item">
            <i className="pi pi-file" style={{ marginRight: '8px' }}></i>
            <span>Current Log Size: {formatBytes(settings.current_log_size_mb)}</span>
          </div>
          <div className="status-item">
            <i className="pi pi-list" style={{ marginRight: '8px' }}></i>
            <span>Total Log Files: {settings.total_log_files}</span>
          </div>
        </div>
      </div>

      <div className="settings-actions">
        <Button
          label="Save Changes"
          icon="pi pi-check"
          onClick={handleSave}
          loading={saving}
          className="p-button-success"
        />
        <Button
          label="View Log Files"
          icon="pi pi-list"
          onClick={handleShowLogFiles}
          className="p-button-secondary"
        />
        <Button
          label="Reset"
          icon="pi pi-refresh"
          onClick={handleReset}
          className="p-button-secondary"
          disabled={saving}
        />
      </div>

      {settings.updated_at && (
        <div className="settings-footer">
          <small>Last updated: {new Date(settings.updated_at).toLocaleString()}</small>
        </div>
      )}

      {/* Log Files Dialog */}
      <Dialog
        header="Log Files"
        visible={showLogFiles}
        style={{ width: '800px' }}
        onHide={() => setShowLogFiles(false)}
      >
        <DataTable value={logFiles} paginator rows={10} emptyMessage="No log files found">
          <Column field="filename" header="Filename" sortable />
          <Column body={dateBodyTemplate} header="Modified" sortable field="modified_at" />
          <Column body={sizeBodyTemplate} header="Size" sortable field="size_mb" />
          <Column body={linesBodyTemplate} header="Lines" sortable field="lines" />
        </DataTable>
      </Dialog>
    </div>
  );
};

export default LoggingConfiguration;
