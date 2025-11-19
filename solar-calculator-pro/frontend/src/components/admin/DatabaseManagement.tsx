/**
 * Database Management Component
 * 
 * Provides comprehensive database management interface including:
 * - Backup and restore operations
 * - Database optimization
 * - Statistics display
 * - Data export functionality
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputSwitch } from 'primereact/inputswitch';
import { ProgressBar } from 'primereact/progressbar';
import { Message } from 'primereact/message';
import { Dropdown } from 'primereact/dropdown';
import { TabView, TabPanel } from 'primereact/tabview';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import api from '../../services/api';
import './DatabaseManagement.css';

interface Backup {
  filename: string;
  created_at: string;
  description?: string;
  compressed: boolean;
  size_mb: number;
}

interface DatabaseStats {
  database: {
    path: string;
    size_mb: number;
    page_size: number;
    page_count: number;
  };
  tables: {
    count: number;
    total_rows: number;
    details: Array<{
      name: string;
      rows: number;
      columns: number;
    }>;
  };
  indexes: {
    count: number;
  };
}

export const DatabaseManagement: React.FC = () => {
  const [backups, setBackups] = useState<Backup[]>([]);
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [showBackupDialog, setShowBackupDialog] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [backupDescription, setBackupDescription] = useState('');
  const [compressBackup, setCompressBackup] = useState(true);
  const [exportFormat, setExportFormat] = useState('json');
  const [selectedTable, setSelectedTable] = useState('');
  const toast = React.useRef<Toast>(null);

  useEffect(() => {
    loadBackups();
    loadStatistics();
  }, []);

  // ==================== Data Loading ====================

  const loadBackups = async () => {
    try {
      const response = await api.get('/api/v1/database/backups');
      setBackups(response.data.backups);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load backups',
        life: 3000
      });
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await api.get('/api/v1/database/statistics');
      setStats(response.data);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load statistics',
        life: 3000
      });
    }
  };

  // ==================== Backup Operations ====================

  const createBackup = async () => {
    setLoading(true);
    try {
      const response = await api.post('/api/v1/database/backup', {
        description: backupDescription,
        compress: compressBackup
      });

      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Backup created successfully',
        life: 3000
      });

      setShowBackupDialog(false);
      setBackupDescription('');
      loadBackups();
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to create backup',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const restoreBackup = (backup: Backup) => {
    confirmDialog({
      message: `Are you sure you want to restore from "${backup.filename}"? This will replace the current database!`,
      header: 'Confirm Restore',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        setLoading(true);
        try {
          await api.post('/api/v1/database/restore', {
            backup_filename: backup.filename,
            create_backup_before: true
          });

          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Database restored successfully',
            life: 3000
          });

          loadStatistics();
        } catch (error: any) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to restore backup',
            life: 3000
          });
        } finally {
          setLoading(false);
        }
      }
    });
  };

  const deleteBackup = (backup: Backup) => {
    confirmDialog({
      message: `Are you sure you want to delete "${backup.filename}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-trash',
      accept: async () => {
        try {
          await api.delete('/api/v1/database/backup', {
            data: { backup_filename: backup.filename }
          });

          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Backup deleted successfully',
            life: 3000
          });

          loadBackups();
        } catch (error: any) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to delete backup',
            life: 3000
          });
        }
      }
    });
  };

  // ==================== Optimization Operations ====================

  const optimizeDatabase = () => {
    confirmDialog({
      message: 'This will optimize the database (VACUUM, ANALYZE, REINDEX). This may take some time. Continue?',
      header: 'Confirm Optimization',
      icon: 'pi pi-cog',
      accept: async () => {
        setLoading(true);
        try {
          const response = await api.post('/api/v1/database/optimize');

          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: `Database optimized. Space saved: ${response.data.space_saved_mb} MB`,
            life: 5000
          });

          loadStatistics();
        } catch (error: any) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to optimize database',
            life: 3000
          });
        } finally {
          setLoading(false);
        }
      }
    });
  };

  const checkIntegrity = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/database/integrity');

      toast.current?.show({
        severity: response.data.integrity_ok ? 'success' : 'error',
        summary: response.data.integrity_ok ? 'Integrity OK' : 'Integrity Issues',
        detail: response.data.message,
        life: 5000
      });
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to check integrity',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  // ==================== Export Operations ====================

  const exportTable = async () => {
    if (!selectedTable) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Warning',
        detail: 'Please select a table to export',
        life: 3000
      });
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/api/v1/database/export/table', {
        table_name: selectedTable,
        format: exportFormat
      });

      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: `Table exported: ${response.data.rows_exported} rows`,
        life: 3000
      });

      setShowExportDialog(false);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to export table',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const exportFullDatabase = () => {
    confirmDialog({
      message: 'This will export the entire database. This may take some time. Continue?',
      header: 'Confirm Full Export',
      icon: 'pi pi-download',
      accept: async () => {
        setLoading(true);
        try {
          const response = await api.post('/api/v1/database/export/full', {
            format: exportFormat
          });

          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: `Database exported: ${response.data.size_mb} MB`,
            life: 5000
          });
        } catch (error: any) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to export database',
            life: 3000
          });
        } finally {
          setLoading(false);
        }
      }
    });
  };

  // ==================== Template Functions ====================

  const dateTemplate = (rowData: Backup) => {
    return new Date(rowData.created_at).toLocaleString();
  };

  const sizeTemplate = (rowData: Backup) => {
    return `${rowData.size_mb} MB`;
  };

  const compressedTemplate = (rowData: Backup) => {
    return rowData.compressed ? (
      <i className="pi pi-check text-green-500"></i>
    ) : (
      <i className="pi pi-times text-red-500"></i>
    );
  };

  const actionsTemplate = (rowData: Backup) => {
    return (
      <div className="flex gap-2">
        <Button
          icon="pi pi-replay"
          className="p-button-sm p-button-success"
          onClick={() => restoreBackup(rowData)}
          tooltip="Restore"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-trash"
          className="p-button-sm p-button-danger"
          onClick={() => deleteBackup(rowData)}
          tooltip="Delete"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  };

  // ==================== Render ====================

  return (
    <div className="database-management">
      <Toast ref={toast} />
      <ConfirmDialog />

      <div className="grid">
        {/* Statistics Card */}
        <div className="col-12 lg:col-4">
          <Card title="Database Statistics" className="h-full">
            {stats && (
              <div className="stats-grid">
                <div className="stat-item">
                  <div className="stat-label">Database Size</div>
                  <div className="stat-value">{stats.database.size_mb} MB</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Tables</div>
                  <div className="stat-value">{stats.tables.count}</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Total Rows</div>
                  <div className="stat-value">{stats.tables.total_rows.toLocaleString()}</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Indexes</div>
                  <div className="stat-value">{stats.indexes.count}</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Page Size</div>
                  <div className="stat-value">{stats.database.page_size} bytes</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Page Count</div>
                  <div className="stat-value">{stats.database.page_count.toLocaleString()}</div>
                </div>
              </div>
            )}
            <div className="mt-4 flex gap-2">
              <Button
                label="Refresh"
                icon="pi pi-refresh"
                onClick={loadStatistics}
                className="p-button-sm"
              />
              <Button
                label="Check Integrity"
                icon="pi pi-shield"
                onClick={checkIntegrity}
                className="p-button-sm p-button-info"
              />
            </div>
          </Card>
        </div>

        {/* Quick Actions Card */}
        <div className="col-12 lg:col-8">
          <Card title="Quick Actions">
            <div className="grid">
              <div className="col-12 md:col-6">
                <Button
                  label="Create Backup"
                  icon="pi pi-save"
                  onClick={() => setShowBackupDialog(true)}
                  className="w-full p-button-lg"
                  disabled={loading}
                />
              </div>
              <div className="col-12 md:col-6">
                <Button
                  label="Optimize Database"
                  icon="pi pi-cog"
                  onClick={optimizeDatabase}
                  className="w-full p-button-lg p-button-warning"
                  disabled={loading}
                />
              </div>
              <div className="col-12 md:col-6">
                <Button
                  label="Export Data"
                  icon="pi pi-download"
                  onClick={() => setShowExportDialog(true)}
                  className="w-full p-button-lg p-button-success"
                  disabled={loading}
                />
              </div>
              <div className="col-12 md:col-6">
                <Button
                  label="Export Full Database"
                  icon="pi pi-database"
                  onClick={exportFullDatabase}
                  className="w-full p-button-lg p-button-info"
                  disabled={loading}
                />
              </div>
            </div>
          </Card>
        </div>

        {/* Backups Table */}
        <div className="col-12">
          <Card title="Backup History">
            <DataTable
              value={backups}
              paginator
              rows={10}
              emptyMessage="No backups found"
              loading={loading}
            >
              <Column field="filename" header="Filename" sortable />
              <Column
                field="created_at"
                header="Created"
                body={dateTemplate}
                sortable
              />
              <Column field="description" header="Description" />
              <Column
                field="size_mb"
                header="Size"
                body={sizeTemplate}
                sortable
              />
              <Column
                field="compressed"
                header="Compressed"
                body={compressedTemplate}
              />
              <Column body={actionsTemplate} header="Actions" />
            </DataTable>
          </Card>
        </div>

        {/* Table Details */}
        {stats && (
          <div className="col-12">
            <Card title="Table Details">
              <DataTable
                value={stats.tables.details}
                paginator
                rows={10}
                sortField="rows"
                sortOrder={-1}
              >
                <Column field="name" header="Table Name" sortable />
                <Column
                  field="rows"
                  header="Rows"
                  sortable
                  body={(rowData) => rowData.rows.toLocaleString()}
                />
                <Column field="columns" header="Columns" sortable />
              </DataTable>
            </Card>
          </div>
        )}
      </div>

      {/* Create Backup Dialog */}
      <Dialog
        header="Create Backup"
        visible={showBackupDialog}
        style={{ width: '500px' }}
        onHide={() => setShowBackupDialog(false)}
      >
        <div className="p-fluid">
          <div className="field">
            <label htmlFor="description">Description (Optional)</label>
            <InputText
              id="description"
              value={backupDescription}
              onChange={(e) => setBackupDescription(e.target.value)}
              placeholder="Enter backup description"
            />
          </div>
          <div className="field-checkbox">
            <InputSwitch
              id="compress"
              checked={compressBackup}
              onChange={(e) => setCompressBackup(e.value)}
            />
            <label htmlFor="compress" className="ml-2">
              Compress backup (recommended)
            </label>
          </div>
        </div>
        <div className="flex justify-content-end gap-2 mt-4">
          <Button
            label="Cancel"
            icon="pi pi-times"
            onClick={() => setShowBackupDialog(false)}
            className="p-button-text"
          />
          <Button
            label="Create Backup"
            icon="pi pi-check"
            onClick={createBackup}
            loading={loading}
          />
        </div>
      </Dialog>

      {/* Export Dialog */}
      <Dialog
        header="Export Data"
        visible={showExportDialog}
        style={{ width: '500px' }}
        onHide={() => setShowExportDialog(false)}
      >
        <div className="p-fluid">
          <div className="field">
            <label htmlFor="table">Select Table</label>
            <Dropdown
              id="table"
              value={selectedTable}
              options={stats?.tables.details.map(t => ({ label: t.name, value: t.name })) || []}
              onChange={(e) => setSelectedTable(e.value)}
              placeholder="Select a table"
            />
          </div>
          <div className="field">
            <label htmlFor="format">Export Format</label>
            <Dropdown
              id="format"
              value={exportFormat}
              options={[
                { label: 'JSON', value: 'json' },
                { label: 'CSV', value: 'csv' }
              ]}
              onChange={(e) => setExportFormat(e.value)}
            />
          </div>
        </div>
        <div className="flex justify-content-end gap-2 mt-4">
          <Button
            label="Cancel"
            icon="pi pi-times"
            onClick={() => setShowExportDialog(false)}
            className="p-button-text"
          />
          <Button
            label="Export"
            icon="pi pi-download"
            onClick={exportTable}
            loading={loading}
          />
        </div>
      </Dialog>

      {loading && (
        <div className="loading-overlay">
          <ProgressBar mode="indeterminate" />
        </div>
      )}
    </div>
  );
};
