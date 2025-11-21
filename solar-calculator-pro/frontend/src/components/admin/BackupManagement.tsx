/**
 * Backup Management Component
 * Provides UI for creating, restoring, and managing backups
 * Requirements: 5.5
 */

import React, { useState, useEffect } from 'react';
import { Button } from 'primereact/button';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Checkbox } from 'primereact/checkbox';
import { ProgressBar } from 'primereact/progressbar';
import { Message } from 'primereact/message';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import api from '../../services/api';
import './BackupManagement.css';

interface Backup {
  backup_name: string;
  timestamp: string;
  created_at: string;
  description: string;
  files_count: number;
  total_size_bytes: number;
  size_formatted: string;
  is_compressed: boolean;
  components: {
    databases?: { files_count: number };
    settings?: { files_count: number };
    user_data?: { files_count: number };
    projects?: { files_count: number };
  };
}

interface BackupCreateOptions {
  backup_name: string;
  description: string;
  include_databases: boolean;
  include_settings: boolean;
  include_user_data: boolean;
  include_projects: boolean;
  compress: boolean;
}

export const BackupManagement: React.FC = () => {
  const [backups, setBackups] = useState<Backup[]>([]);
  const [loading, setLoading] = useState(false);
  const [createDialogVisible, setCreateDialogVisible] = useState(false);
  const [verifyDialogVisible, setVerifyDialogVisible] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState<Backup | null>(null);
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const toast = React.useRef<Toast>(null);

  const [createOptions, setCreateOptions] = useState<BackupCreateOptions>({
    backup_name: '',
    description: '',
    include_databases: true,
    include_settings: true,
    include_user_data: true,
    include_projects: true,
    compress: true
  });

  useEffect(() => {
    loadBackups();
  }, []);

  const loadBackups = async () => {
    setLoading(true);
    try {
      const response = await api.get('/backup/list');
      setBackups(response.data.backups || []);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to load backups',
        life: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    setLoading(true);
    try {
      const response = await api.post('/backup/create', createOptions);
      
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: response.data.message,
        life: 5000
      });

      setCreateDialogVisible(false);
      resetCreateOptions();
      await loadBackups();
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to create backup',
        life: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRestoreBackup = (backup: Backup) => {
    confirmDialog({
      message: `Are you sure you want to restore backup "${backup.backup_name}"? This will replace current data with backup data. A backup of current data will be created automatically.`,
      header: 'Confirm Restore',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        setLoading(true);
        try {
          const response = await api.post('/backup/restore', {
            backup_name: backup.backup_name,
            verify_before_restore: true
          });

          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: response.data.message,
            life: 5000
          });

          await loadBackups();
        } catch (error: any) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to restore backup',
            life: 5000
          });
        } finally {
          setLoading(false);
        }
      }
    });
  };

  const handleVerifyBackup = async (backup: Backup) => {
    setSelectedBackup(backup);
    setLoading(true);
    try {
      const response = await api.get(`/backup/verify/${backup.backup_name}`);
      setVerificationResult(response.data);
      setVerifyDialogVisible(true);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to verify backup',
        life: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBackup = (backup: Backup) => {
    confirmDialog({
      message: `Are you sure you want to delete backup "${backup.backup_name}"? This action cannot be undone.`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      acceptClassName: 'p-button-danger',
      accept: async () => {
        setLoading(true);
        try {
          const response = await api.delete(`/backup/delete/${backup.backup_name}`);

          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: response.data.message,
            life: 5000
          });

          await loadBackups();
        } catch (error: any) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to delete backup',
            life: 5000
          });
        } finally {
          setLoading(false);
        }
      }
    });
  };

  const resetCreateOptions = () => {
    setCreateOptions({
      backup_name: '',
      description: '',
      include_databases: true,
      include_settings: true,
      include_user_data: true,
      include_projects: true,
      compress: true
    });
  };

  const actionBodyTemplate = (rowData: Backup) => {
    return (
      <div className="backup-actions">
        <Button
          icon="pi pi-refresh"
          className="p-button-rounded p-button-success p-button-sm"
          onClick={() => handleRestoreBackup(rowData)}
          tooltip="Restore Backup"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-check-circle"
          className="p-button-rounded p-button-info p-button-sm"
          onClick={() => handleVerifyBackup(rowData)}
          tooltip="Verify Backup"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-danger p-button-sm"
          onClick={() => handleDeleteBackup(rowData)}
          tooltip="Delete Backup"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  };

  const dateBodyTemplate = (rowData: Backup) => {
    return new Date(rowData.created_at).toLocaleString();
  };

  const sizeBodyTemplate = (rowData: Backup) => {
    return rowData.size_formatted;
  };

  const componentsBodyTemplate = (rowData: Backup) => {
    const components = [];
    if (rowData.components.databases) components.push('DB');
    if (rowData.components.settings) components.push('Settings');
    if (rowData.components.user_data) components.push('Users');
    if (rowData.components.projects) components.push('Projects');
    return components.join(', ');
  };

  const compressionBodyTemplate = (rowData: Backup) => {
    return rowData.is_compressed ? (
      <i className="pi pi-check text-green-500" />
    ) : (
      <i className="pi pi-times text-red-500" />
    );
  };

  return (
    <div className="backup-management">
      <Toast ref={toast} />
      <ConfirmDialog />

      <div className="backup-header">
        <h2>Backup Management</h2>
        <div className="backup-header-actions">
          <Button
            label="Create Backup"
            icon="pi pi-plus"
            onClick={() => setCreateDialogVisible(true)}
            disabled={loading}
          />
          <Button
            label="Refresh"
            icon="pi pi-refresh"
            className="p-button-outlined"
            onClick={loadBackups}
            disabled={loading}
          />
        </div>
      </div>

      {loading && <ProgressBar mode="indeterminate" style={{ height: '6px' }} />}

      <Message
        severity="info"
        text="Backups are automatically created before migrations and can be manually created at any time. Restoring a backup will create a backup of current data first."
      />

      <DataTable
        value={backups}
        loading={loading}
        emptyMessage="No backups found"
        paginator
        rows={10}
        rowsPerPageOptions={[5, 10, 25, 50]}
        className="backup-table"
      >
        <Column field="backup_name" header="Backup Name" sortable />
        <Column field="created_at" header="Created" body={dateBodyTemplate} sortable />
        <Column field="description" header="Description" />
        <Column field="files_count" header="Files" sortable />
        <Column field="size_formatted" header="Size" body={sizeBodyTemplate} sortable />
        <Column header="Components" body={componentsBodyTemplate} />
        <Column header="Compressed" body={compressionBodyTemplate} />
        <Column header="Actions" body={actionBodyTemplate} />
      </DataTable>

      {/* Create Backup Dialog */}
      <Dialog
        header="Create Backup"
        visible={createDialogVisible}
        style={{ width: '600px' }}
        onHide={() => {
          setCreateDialogVisible(false);
          resetCreateOptions();
        }}
        footer={
          <div>
            <Button
              label="Cancel"
              icon="pi pi-times"
              onClick={() => {
                setCreateDialogVisible(false);
                resetCreateOptions();
              }}
              className="p-button-text"
            />
            <Button
              label="Create"
              icon="pi pi-check"
              onClick={handleCreateBackup}
              disabled={loading}
            />
          </div>
        }
      >
        <div className="backup-create-form">
          <div className="field">
            <label htmlFor="backup_name">Backup Name (optional)</label>
            <InputText
              id="backup_name"
              value={createOptions.backup_name}
              onChange={(e) => setCreateOptions({ ...createOptions, backup_name: e.target.value })}
              placeholder="Auto-generated if empty"
              className="w-full"
            />
            <small>Leave empty for automatic timestamp-based name</small>
          </div>

          <div className="field">
            <label htmlFor="description">Description</label>
            <InputTextarea
              id="description"
              value={createOptions.description}
              onChange={(e) => setCreateOptions({ ...createOptions, description: e.target.value })}
              rows={3}
              className="w-full"
              placeholder="Optional description for this backup"
            />
          </div>

          <div className="field">
            <label>Components to Include</label>
            <div className="backup-components">
              <div className="field-checkbox">
                <Checkbox
                  inputId="include_databases"
                  checked={createOptions.include_databases}
                  onChange={(e) => setCreateOptions({ ...createOptions, include_databases: e.checked || false })}
                />
                <label htmlFor="include_databases">Databases</label>
              </div>

              <div className="field-checkbox">
                <Checkbox
                  inputId="include_settings"
                  checked={createOptions.include_settings}
                  onChange={(e) => setCreateOptions({ ...createOptions, include_settings: e.checked || false })}
                />
                <label htmlFor="include_settings">Settings</label>
              </div>

              <div className="field-checkbox">
                <Checkbox
                  inputId="include_user_data"
                  checked={createOptions.include_user_data}
                  onChange={(e) => setCreateOptions({ ...createOptions, include_user_data: e.checked || false })}
                />
                <label htmlFor="include_user_data">User Data</label>
              </div>

              <div className="field-checkbox">
                <Checkbox
                  inputId="include_projects"
                  checked={createOptions.include_projects}
                  onChange={(e) => setCreateOptions({ ...createOptions, include_projects: e.checked || false })}
                />
                <label htmlFor="include_projects">Projects</label>
              </div>
            </div>
          </div>

          <div className="field">
            <div className="field-checkbox">
              <Checkbox
                inputId="compress"
                checked={createOptions.compress}
                onChange={(e) => setCreateOptions({ ...createOptions, compress: e.checked || false })}
              />
              <label htmlFor="compress">Compress backup (ZIP)</label>
            </div>
            <small>Compression reduces backup size but takes longer</small>
          </div>
        </div>
      </Dialog>

      {/* Verify Backup Dialog */}
      <Dialog
        header={`Verify Backup: ${selectedBackup?.backup_name}`}
        visible={verifyDialogVisible}
        style={{ width: '600px' }}
        onHide={() => {
          setVerifyDialogVisible(false);
          setVerificationResult(null);
        }}
        footer={
          <Button
            label="Close"
            icon="pi pi-times"
            onClick={() => {
              setVerifyDialogVisible(false);
              setVerificationResult(null);
            }}
          />
        }
      >
        {verificationResult && (
          <div className="backup-verification">
            <Message
              severity={verificationResult.valid ? 'success' : 'error'}
              text={verificationResult.message}
            />

            <h4>Verification Checks</h4>
            {verificationResult.checks.map((check: any, index: number) => (
              <div key={index} className="verification-check">
                <div className="check-header">
                  {check.passed ? (
                    <i className="pi pi-check-circle text-green-500" />
                  ) : (
                    <i className="pi pi-times-circle text-red-500" />
                  )}
                  <span className="check-name">{check.name}</span>
                </div>
                {check.details && (
                  <pre className="check-details">
                    {JSON.stringify(check.details, null, 2)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}
      </Dialog>
    </div>
  );
};

export default BackupManagement;
