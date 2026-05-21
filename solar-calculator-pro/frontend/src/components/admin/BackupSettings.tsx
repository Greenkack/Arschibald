/**
 * Backup Settings Component
 * 
 * Backup configuration and management
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
import { Checkbox } from 'primereact/checkbox';
import api from '@services/api';

interface BackupSettingsData {
  enabled: boolean;
  frequency: string;
  retention_days: number;
  backup_location: string;
  include_database: boolean;
  include_files: boolean;
  include_logs: boolean;
  compress_backups: boolean;
  encrypt_backups: boolean;
  max_backup_size_mb: number;
  notification_email: string | null;
  last_backup_at: string | null;
  last_backup_success: boolean | null;
  last_backup_size_mb: number | null;
  next_backup_at: string | null;
  total_backups: number;
  updated_at: string;
}

interface BackupInfo {
  id: number;
  filename: string;
  created_at: string;
  size_mb: number;
  description: string | null;
  includes_database: boolean;
  includes_files: boolean;
  includes_logs: boolean;
  is_compressed: boolean;
  is_encrypted: boolean;
}

interface BackupSettingsProps {
  onUpdate?: () => void;
}

const BackupSettings: React.FC<BackupSettingsProps> = ({ onUpdate }) => {
  const [settings, setSettings] = useState<BackupSettingsData | null>(null);
  const [backups, setBackups] = useState<BackupInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [creating, setCreating] = useState(false);
  const [showBackupDialog, setShowBackupDialog] = useState(false);
  const [showBackupList, setShowBackupList] = useState(false);
  const [backupOptions, setBackupOptions] = useState({
    include_database: true,
    include_files: true,
    include_logs: false,
    description: ''
  });
  const [message, setMessage] = useState<{ severity: 'success' | 'error' | 'info'; text: string } | null>(null);

  const frequencyOptions = [
    { label: 'Hourly', value: 'hourly' },
    { label: 'Daily', value: 'daily' },
    { label: 'Weekly', value: 'weekly' },
    { label: 'Monthly', value: 'monthly' },
  ];

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/system-settings/backup');
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

  const loadBackups = async () => {
    try {
      const response = await api.get('/api/v1/system-settings/backup/list');
      setBackups(response.data.backups);
    } catch (error: any) {
      setMessage({
        severity: 'error',
        text: `Failed to load backups: ${error.response?.data?.detail || error.message}`
      });
    }
  };

  const handleSave = async () => {
    if (!settings) return;

    try {
      setSaving(true);
      setMessage(null);
      
      const response = await api.put('/api/v1/system-settings/backup', settings);
      setSettings(response.data);
      
      setMessage({
        severity: 'success',
        text: 'Backup settings saved successfully'
      });
      
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

  const handleCreateBackup = async () => {
    try {
      setCreating(true);
      setMessage(null);
      
      const response = await api.post('/api/v1/system-settings/backup/create', backupOptions);
      
      setMessage({
        severity: 'success',
        text: `Backup created successfully: ${response.data.filename}`
      });
      
      setShowBackupDialog(false);
      loadSettings();
      
      if (showBackupList) {
        loadBackups();
      }
    } catch (error: any) {
      setMessage({
        severity: 'error',
        text: `Failed to create backup: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setCreating(false);
    }
  };

  const handleShowBackups = () => {
    setShowBackupList(true);
    loadBackups();
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

  const sizeBodyTemplate = (rowData: BackupInfo) => {
    return formatBytes(rowData.size_mb);
  };

  const dateBodyTemplate = (rowData: BackupInfo) => {
    return new Date(rowData.created_at).toLocaleString();
  };

  const includesBodyTemplate = (rowData: BackupInfo) => {
    const includes = [];
    if (rowData.includes_database) includes.push('DB');
    if (rowData.includes_files) includes.push('Files');
    if (rowData.includes_logs) includes.push('Logs');
    return includes.join(', ');
  };

  if (loading) {
    return (
      <div className="settings-loading">
        <ProgressSpinner />
        <p>Loading backup settings...</p>
      </div>
    );
  }

  if (!settings) {
    return <Message severity="error" text="Failed to load settings" />;
  }

  return (
    <div className="backup-settings">
      {message && (
        <Message 
          severity={message.severity} 
          text={message.text} 
          className="settings-message"
        />
      )}

      <div className="settings-section">
        <h3>Backup Configuration</h3>
        
        <div className="p-field-checkbox">
          <InputSwitch
            id="enabled"
            checked={settings.enabled}
            onChange={(e) => setSettings({ ...settings, enabled: e.value })}
          />
          <label htmlFor="enabled">Enable Automatic Backups</label>
        </div>

        <div className="p-field">
          <label htmlFor="frequency">Backup Frequency</label>
          <Dropdown
            id="frequency"
            value={settings.frequency}
            options={frequencyOptions}
            onChange={(e) => setSettings({ ...settings, frequency: e.value })}
            disabled={!settings.enabled}
            className="w-full"
          />
        </div>

        <div className="p-field">
          <label htmlFor="retention_days">Retention Period (days)</label>
          <InputNumber
            id="retention_days"
            value={settings.retention_days}
            onValueChange={(e) => setSettings({ ...settings, retention_days: e.value || 30 })}
            min={1}
            max={365}
            disabled={!settings.enabled}
            className="w-full"
          />
          <small>Backups older than this will be automatically deleted</small>
        </div>

        <div className="p-field">
          <label htmlFor="backup_location">Backup Location</label>
          <InputText
            id="backup_location"
            value={settings.backup_location}
            onChange={(e) => setSettings({ ...settings, backup_location: e.target.value })}
            className="w-full"
          />
        </div>

        <div className="p-field">
          <label htmlFor="max_backup_size_mb">Maximum Backup Size (MB)</label>
          <InputNumber
            id="max_backup_size_mb"
            value={settings.max_backup_size_mb}
            onValueChange={(e) => setSettings({ ...settings, max_backup_size_mb: e.value || 1000 })}
            min={100}
            max={10000}
            className="w-full"
          />
        </div>
      </div>

      <div className="settings-section">
        <h3>Backup Content</h3>
        
        <div className="p-field-checkbox">
          <Checkbox
            inputId="include_database"
            checked={settings.include_database}
            onChange={(e) => setSettings({ ...settings, include_database: e.checked || false })}
          />
          <label htmlFor="include_database">Include Database</label>
        </div>

        <div className="p-field-checkbox">
          <Checkbox
            inputId="include_files"
            checked={settings.include_files}
            onChange={(e) => setSettings({ ...settings, include_files: e.checked || false })}
          />
          <label htmlFor="include_files">Include Files</label>
        </div>

        <div className="p-field-checkbox">
          <Checkbox
            inputId="include_logs"
            checked={settings.include_logs}
            onChange={(e) => setSettings({ ...settings, include_logs: e.checked || false })}
          />
          <label htmlFor="include_logs">Include Logs</label>
        </div>
      </div>

      <div className="settings-section">
        <h3>Backup Options</h3>
        
        <div className="p-field-checkbox">
          <InputSwitch
            id="compress_backups"
            checked={settings.compress_backups}
            onChange={(e) => setSettings({ ...settings, compress_backups: e.value })}
          />
          <label htmlFor="compress_backups">Compress Backups</label>
          <small>Reduce backup size using ZIP compression</small>
        </div>

        <div className="p-field-checkbox">
          <InputSwitch
            id="encrypt_backups"
            checked={settings.encrypt_backups}
            onChange={(e) => setSettings({ ...settings, encrypt_backups: e.value })}
          />
          <label htmlFor="encrypt_backups">Encrypt Backups</label>
          <small>Encrypt backups for additional security</small>
        </div>

        <div className="p-field">
          <label htmlFor="notification_email">Notification Email (Optional)</label>
          <InputText
            id="notification_email"
            value={settings.notification_email || ''}
            onChange={(e) => setSettings({ ...settings, notification_email: e.target.value })}
            placeholder="admin@example.com"
            className="w-full"
          />
          <small>Receive notifications about backup status</small>
        </div>
      </div>

      {settings.last_backup_at && (
        <div className="settings-section">
          <h3>Last Backup</h3>
          <div className="backup-status">
            <div className="status-item">
              <i className={`pi ${settings.last_backup_success ? 'pi-check-circle' : 'pi-times-circle'}`} 
                 style={{ color: settings.last_backup_success ? 'green' : 'red', marginRight: '8px' }}></i>
              <span>
                {settings.last_backup_success ? 'Success' : 'Failed'} - {new Date(settings.last_backup_at).toLocaleString()}
              </span>
            </div>
            {settings.last_backup_size_mb && (
              <div className="status-item">
                <i className="pi pi-database" style={{ marginRight: '8px' }}></i>
                <span>Size: {formatBytes(settings.last_backup_size_mb)}</span>
              </div>
            )}
            {settings.next_backup_at && (
              <div className="status-item">
                <i className="pi pi-clock" style={{ marginRight: '8px' }}></i>
                <span>Next: {new Date(settings.next_backup_at).toLocaleString()}</span>
              </div>
            )}
            <div className="status-item">
              <i className="pi pi-list" style={{ marginRight: '8px' }}></i>
              <span>Total Backups: {settings.total_backups}</span>
            </div>
          </div>
        </div>
      )}

      <div className="settings-actions">
        <Button
          label="Save Changes"
          icon="pi pi-check"
          onClick={handleSave}
          loading={saving}
          className="p-button-success"
        />
        <Button
          label="Create Backup Now"
          icon="pi pi-save"
          onClick={() => setShowBackupDialog(true)}
          className="p-button-info"
        />
        <Button
          label="View Backups"
          icon="pi pi-list"
          onClick={handleShowBackups}
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

      {/* Create Backup Dialog */}
      <Dialog
        header="Create Backup"
        visible={showBackupDialog}
        style={{ width: '450px' }}
        onHide={() => setShowBackupDialog(false)}
        footer={
          <div>
            <Button
              label="Cancel"
              icon="pi pi-times"
              onClick={() => setShowBackupDialog(false)}
              className="p-button-text"
            />
            <Button
              label="Create Backup"
              icon="pi pi-save"
              onClick={handleCreateBackup}
              loading={creating}
              autoFocus
            />
          </div>
        }
      >
        <div className="backup-dialog-content">
          <p>Select what to include in the backup:</p>
          
          <div className="p-field-checkbox">
            <Checkbox
              inputId="backup_database"
              checked={backupOptions.include_database}
              onChange={(e) => setBackupOptions({ ...backupOptions, include_database: e.checked || false })}
            />
            <label htmlFor="backup_database">Database</label>
          </div>

          <div className="p-field-checkbox">
            <Checkbox
              inputId="backup_files"
              checked={backupOptions.include_files}
              onChange={(e) => setBackupOptions({ ...backupOptions, include_files: e.checked || false })}
            />
            <label htmlFor="backup_files">Files</label>
          </div>

          <div className="p-field-checkbox">
            <Checkbox
              inputId="backup_logs"
              checked={backupOptions.include_logs}
              onChange={(e) => setBackupOptions({ ...backupOptions, include_logs: e.checked || false })}
            />
            <label htmlFor="backup_logs">Logs</label>
          </div>

          <div className="p-field">
            <label htmlFor="backup_description">Description (Optional)</label>
            <InputText
              id="backup_description"
              value={backupOptions.description}
              onChange={(e) => setBackupOptions({ ...backupOptions, description: e.target.value })}
              placeholder="Manual backup before update"
              className="w-full"
            />
          </div>
        </div>
      </Dialog>

      {/* Backup List Dialog */}
      <Dialog
        header="Backup History"
        visible={showBackupList}
        style={{ width: '800px' }}
        onHide={() => setShowBackupList(false)}
      >
        <DataTable value={backups} paginator rows={10} emptyMessage="No backups found">
          <Column field="filename" header="Filename" sortable />
          <Column body={dateBodyTemplate} header="Created" sortable field="created_at" />
          <Column body={sizeBodyTemplate} header="Size" sortable field="size_mb" />
          <Column body={includesBodyTemplate} header="Includes" />
          <Column 
            field="is_compressed" 
            header="Compressed" 
            body={(rowData) => rowData.is_compressed ? <i className="pi pi-check" /> : <i className="pi pi-times" />}
          />
        </DataTable>
      </Dialog>
    </div>
  );
};

export default BackupSettings;
