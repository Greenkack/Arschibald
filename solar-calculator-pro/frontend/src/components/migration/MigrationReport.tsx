/**
 * Migration Report Component
 * Displays comprehensive migration report with statistics and details
 * Requirements: 5.5, 5.6
 */

import React from 'react';
import { Card } from 'primereact/card';
import { TabView, TabPanel } from 'primereact/tabview';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Chart } from 'primereact/chart';
import { Message } from 'primereact/message';
import './MigrationReport.css';

interface MigrationReportData {
  started_at: string;
  completed_at: string;
  source_path: string;
  target_path: string;
  backup_path: string;
  success: boolean;
  errors: string[];
  steps: {
    step: string;
    success: boolean;
    message: string;
    files_backed_up?: number;
    databases_migrated?: number;
    tables_migrated?: number;
    records_migrated?: number;
    settings_migrated?: number;
    projects_migrated?: number;
    users_migrated?: number;
    checks?: {
      name: string;
      passed: boolean;
      details: any;
    }[];
  }[];
  rollback?: {
    rollback_attempted: boolean;
    success: boolean;
    message: string;
  };
}

interface MigrationReportProps {
  report: MigrationReportData | null;
}

export const MigrationReport: React.FC<MigrationReportProps> = ({ report }) => {
  if (!report) {
    return (
      <Message
        severity="info"
        text="Kein Migrationsbericht verfügbar."
      />
    );
  }

  const calculateDuration = () => {
    const start = new Date(report.started_at);
    const end = new Date(report.completed_at);
    const duration = Math.floor((end.getTime() - start.getTime()) / 1000);
    
    const hours = Math.floor(duration / 3600);
    const minutes = Math.floor((duration % 3600) / 60);
    const seconds = duration % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  };

  const getStepStatistics = () => {
    const stats = {
      totalDatabases: 0,
      totalTables: 0,
      totalRecords: 0,
      totalSettings: 0,
      totalProjects: 0,
      totalUsers: 0,
      totalFiles: 0
    };

    report.steps.forEach(step => {
      stats.totalDatabases += step.databases_migrated || 0;
      stats.totalTables += step.tables_migrated || 0;
      stats.totalRecords += step.records_migrated || 0;
      stats.totalSettings += step.settings_migrated || 0;
      stats.totalProjects += step.projects_migrated || 0;
      stats.totalUsers += step.users_migrated || 0;
      stats.totalFiles += step.files_backed_up || 0;
    });

    return stats;
  };

  const stats = getStepStatistics();

  const chartData = {
    labels: ['Datenbanken', 'Tabellen', 'Datensätze', 'Einstellungen', 'Projekte', 'Benutzer'],
    datasets: [
      {
        label: 'Migrierte Elemente',
        data: [
          stats.totalDatabases,
          stats.totalTables,
          stats.totalRecords,
          stats.totalSettings,
          stats.totalProjects,
          stats.totalUsers
        ],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 205, 86, 0.6)'
        ],
        borderColor: [
          'rgb(54, 162, 235)',
          'rgb(75, 192, 192)',
          'rgb(153, 102, 255)',
          'rgb(255, 159, 64)',
          'rgb(255, 99, 132)',
          'rgb(255, 205, 86)'
        ],
        borderWidth: 1
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    }
  };

  const exportReport = () => {
    const reportData = JSON.stringify(report, null, 2);
    const blob = new Blob([reportData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `migration-report-${new Date().toISOString()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportPDF = () => {
    // TODO: Implement PDF export
    console.log('PDF export not yet implemented');
  };

  const statusTemplate = (rowData: any) => {
    return (
      <span className={`status-badge ${rowData.success ? 'success' : 'failed'}`}>
        {rowData.success ? 'Erfolgreich' : 'Fehlgeschlagen'}
      </span>
    );
  };

  const checkStatusTemplate = (rowData: any) => {
    return (
      <span className={`status-badge ${rowData.passed ? 'success' : 'failed'}`}>
        {rowData.passed ? 'Bestanden' : 'Nicht bestanden'}
      </span>
    );
  };

  return (
    <div className="migration-report">
      {/* Summary Card */}
      <Card className="report-summary">
        <div className="summary-header">
          <div className="summary-status">
            {report.success ? (
              <>
                <i className="pi pi-check-circle text-green-500" style={{ fontSize: '3rem' }} />
                <h2>Migration erfolgreich</h2>
              </>
            ) : (
              <>
                <i className="pi pi-times-circle text-red-500" style={{ fontSize: '3rem' }} />
                <h2>Migration fehlgeschlagen</h2>
              </>
            )}
          </div>
          
          <div className="summary-stats">
            <div className="stat-item">
              <label>Dauer:</label>
              <span>{calculateDuration()}</span>
            </div>
            <div className="stat-item">
              <label>Gestartet:</label>
              <span>{new Date(report.started_at).toLocaleString('de-DE')}</span>
            </div>
            <div className="stat-item">
              <label>Abgeschlossen:</label>
              <span>{new Date(report.completed_at).toLocaleString('de-DE')}</span>
            </div>
          </div>
        </div>

        <div className="summary-actions">
          <Button
            label="Bericht exportieren (JSON)"
            icon="pi pi-download"
            onClick={exportReport}
            className="p-button-secondary"
          />
          <Button
            label="Bericht exportieren (PDF)"
            icon="pi pi-file-pdf"
            onClick={exportPDF}
            className="p-button-secondary"
          />
        </div>
      </Card>

      {/* Detailed Report Tabs */}
      <TabView className="report-tabs">
        {/* Overview Tab */}
        <TabPanel header="Übersicht" leftIcon="pi pi-chart-bar">
          <div className="overview-content">
            <div className="statistics-grid">
              <Card title="Migrierte Datenbanken" className="stat-card">
                <div className="stat-value">{stats.totalDatabases}</div>
                <div className="stat-label">Datenbanken</div>
              </Card>
              <Card title="Migrierte Tabellen" className="stat-card">
                <div className="stat-value">{stats.totalTables}</div>
                <div className="stat-label">Tabellen</div>
              </Card>
              <Card title="Migrierte Datensätze" className="stat-card">
                <div className="stat-value">{stats.totalRecords.toLocaleString('de-DE')}</div>
                <div className="stat-label">Datensätze</div>
              </Card>
              <Card title="Migrierte Einstellungen" className="stat-card">
                <div className="stat-value">{stats.totalSettings}</div>
                <div className="stat-label">Einstellungen</div>
              </Card>
              <Card title="Migrierte Projekte" className="stat-card">
                <div className="stat-value">{stats.totalProjects}</div>
                <div className="stat-label">Projekte</div>
              </Card>
              <Card title="Migrierte Benutzer" className="stat-card">
                <div className="stat-value">{stats.totalUsers}</div>
                <div className="stat-label">Benutzer</div>
              </Card>
            </div>

            <Card title="Migrationsstatistik" className="chart-card">
              <div style={{ height: '300px' }}>
                <Chart type="bar" data={chartData} options={chartOptions} />
              </div>
            </Card>
          </div>
        </TabPanel>

        {/* Steps Tab */}
        <TabPanel header="Schritte" leftIcon="pi pi-list">
          <DataTable
            value={report.steps}
            className="steps-table"
          >
            <Column
              field="step"
              header="Schritt"
              style={{ width: '200px' }}
            />
            <Column
              field="success"
              header="Status"
              body={statusTemplate}
              style={{ width: '150px' }}
            />
            <Column
              field="message"
              header="Nachricht"
            />
          </DataTable>
        </TabPanel>

        {/* Validation Tab */}
        <TabPanel header="Validierung" leftIcon="pi pi-check-square">
          {report.steps.find(s => s.step === 'validation')?.checks ? (
            <DataTable
              value={report.steps.find(s => s.step === 'validation')?.checks}
              className="validation-table"
            >
              <Column
                field="name"
                header="Prüfung"
                style={{ width: '250px' }}
              />
              <Column
                field="passed"
                header="Status"
                body={checkStatusTemplate}
                style={{ width: '150px' }}
              />
              <Column
                field="details"
                header="Details"
                body={(rowData) => (
                  <pre className="details-text">
                    {JSON.stringify(rowData.details, null, 2)}
                  </pre>
                )}
              />
            </DataTable>
          ) : (
            <Message
              severity="info"
              text="Keine Validierungsdaten verfügbar."
            />
          )}
        </TabPanel>

        {/* Paths Tab */}
        <TabPanel header="Pfade" leftIcon="pi pi-folder">
          <div className="paths-content">
            <div className="path-item">
              <label>Quellpfad:</label>
              <code>{report.source_path}</code>
            </div>
            <div className="path-item">
              <label>Zielpfad:</label>
              <code>{report.target_path}</code>
            </div>
            <div className="path-item">
              <label>Backup-Pfad:</label>
              <code>{report.backup_path}</code>
            </div>
          </div>
        </TabPanel>

        {/* Errors Tab */}
        {report.errors.length > 0 && (
          <TabPanel header="Fehler" leftIcon="pi pi-exclamation-triangle">
            <Message
              severity="error"
              text={`${report.errors.length} Fehler aufgetreten`}
            />
            <ul className="error-list">
              {report.errors.map((error, index) => (
                <li key={index} className="error-item">
                  {error}
                </li>
              ))}
            </ul>
          </TabPanel>
        )}

        {/* Rollback Tab */}
        {report.rollback && (
          <TabPanel header="Rollback" leftIcon="pi pi-undo">
            <Card>
              <div className="rollback-info">
                <div className="rollback-status">
                  {report.rollback.success ? (
                    <>
                      <i className="pi pi-check-circle text-green-500" />
                      <span>Rollback erfolgreich</span>
                    </>
                  ) : (
                    <>
                      <i className="pi pi-times-circle text-red-500" />
                      <span>Rollback fehlgeschlagen</span>
                    </>
                  )}
                </div>
                <p>{report.rollback.message}</p>
              </div>
            </Card>
          </TabPanel>
        )}
      </TabView>
    </div>
  );
};
