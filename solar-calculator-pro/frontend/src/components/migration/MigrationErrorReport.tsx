/**
 * Migration Error Report Component
 * Displays detailed error information during migration
 * Requirements: 5.6
 */

import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { Message } from 'primereact/message';
import { Accordion, AccordionTab } from 'primereact/accordion';
import './MigrationErrorReport.css';

interface MigrationError {
  id: string;
  timestamp: string;
  step: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  details?: string;
  stackTrace?: string;
  affectedItems?: string[];
  suggestedAction?: string;
}

interface MigrationErrorReportProps {
  errors: MigrationError[];
}

export const MigrationErrorReport: React.FC<MigrationErrorReportProps> = ({ errors }) => {
  const [selectedError, setSelectedError] = useState<MigrationError | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return 'pi pi-times-circle text-red-500';
      case 'warning':
        return 'pi pi-exclamation-triangle text-orange-500';
      case 'info':
        return 'pi pi-info-circle text-blue-500';
      default:
        return 'pi pi-circle';
    }
  };

  const severityTemplate = (rowData: MigrationError) => {
    return (
      <div className="severity-cell">
        <i className={getSeverityIcon(rowData.severity)} />
        <span className="severity-text">{rowData.severity.toUpperCase()}</span>
      </div>
    );
  };

  const timestampTemplate = (rowData: MigrationError) => {
    const date = new Date(rowData.timestamp);
    return date.toLocaleString('de-DE');
  };

  const actionTemplate = (rowData: MigrationError) => {
    return (
      <Button
        icon="pi pi-eye"
        label="Details"
        className="p-button-sm p-button-text"
        onClick={() => {
          setSelectedError(rowData);
          setShowDetailsDialog(true);
        }}
      />
    );
  };

  const exportErrors = () => {
    const errorData = JSON.stringify(errors, null, 2);
    const blob = new Blob([errorData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `migration-errors-${new Date().toISOString()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const errorCount = errors.filter(e => e.severity === 'error').length;
  const warningCount = errors.filter(e => e.severity === 'warning').length;

  return (
    <div className="migration-error-report">
      <Card title="Fehler und Warnungen">
        <div className="error-summary">
          <div className="error-stat">
            <i className="pi pi-times-circle text-red-500" />
            <span className="stat-value">{errorCount}</span>
            <span className="stat-label">Fehler</span>
          </div>
          <div className="error-stat">
            <i className="pi pi-exclamation-triangle text-orange-500" />
            <span className="stat-value">{warningCount}</span>
            <span className="stat-label">Warnungen</span>
          </div>
          <div className="error-stat">
            <i className="pi pi-info-circle text-blue-500" />
            <span className="stat-value">{errors.length - errorCount - warningCount}</span>
            <span className="stat-label">Informationen</span>
          </div>
        </div>

        {errorCount > 0 && (
          <Message
            severity="error"
            text="Es sind kritische Fehler aufgetreten. Bitte überprüfen Sie die Details und führen Sie ggf. einen Rollback durch."
          />
        )}

        <div className="error-table-container">
          <DataTable
            value={errors}
            paginator
            rows={10}
            rowsPerPageOptions={[5, 10, 25, 50]}
            sortField="timestamp"
            sortOrder={-1}
            className="migration-error-table"
            emptyMessage="Keine Fehler oder Warnungen"
          >
            <Column
              field="severity"
              header="Schweregrad"
              body={severityTemplate}
              sortable
              style={{ width: '150px' }}
            />
            <Column
              field="timestamp"
              header="Zeitstempel"
              body={timestampTemplate}
              sortable
              style={{ width: '180px' }}
            />
            <Column
              field="step"
              header="Schritt"
              sortable
              style={{ width: '200px' }}
            />
            <Column
              field="message"
              header="Nachricht"
              sortable
            />
            <Column
              body={actionTemplate}
              style={{ width: '120px' }}
            />
          </DataTable>
        </div>

        <div className="error-actions">
          <Button
            label="Fehler exportieren"
            icon="pi pi-download"
            onClick={exportErrors}
            className="p-button-secondary"
          />
        </div>
      </Card>

      {/* Error Details Dialog */}
      <Dialog
        header="Fehlerdetails"
        visible={showDetailsDialog}
        style={{ width: '800px' }}
        onHide={() => setShowDetailsDialog(false)}
        maximizable
      >
        {selectedError && (
          <div className="error-details">
            <div className="error-detail-section">
              <h4>Allgemeine Informationen</h4>
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Schweregrad:</label>
                  <span className={`severity-badge severity-${selectedError.severity}`}>
                    {selectedError.severity.toUpperCase()}
                  </span>
                </div>
                <div className="detail-item">
                  <label>Zeitstempel:</label>
                  <span>{new Date(selectedError.timestamp).toLocaleString('de-DE')}</span>
                </div>
                <div className="detail-item">
                  <label>Schritt:</label>
                  <span>{selectedError.step}</span>
                </div>
              </div>
            </div>

            <div className="error-detail-section">
              <h4>Fehlermeldung</h4>
              <p className="error-message">{selectedError.message}</p>
            </div>

            {selectedError.details && (
              <div className="error-detail-section">
                <h4>Details</h4>
                <pre className="error-details-text">{selectedError.details}</pre>
              </div>
            )}

            {selectedError.affectedItems && selectedError.affectedItems.length > 0 && (
              <div className="error-detail-section">
                <h4>Betroffene Elemente</h4>
                <ul className="affected-items-list">
                  {selectedError.affectedItems.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {selectedError.suggestedAction && (
              <div className="error-detail-section">
                <h4>Empfohlene Maßnahme</h4>
                <Message
                  severity="info"
                  text={selectedError.suggestedAction}
                />
              </div>
            )}

            {selectedError.stackTrace && (
              <Accordion>
                <AccordionTab header="Stack Trace (Technische Details)">
                  <pre className="stack-trace">{selectedError.stackTrace}</pre>
                </AccordionTab>
              </Accordion>
            )}
          </div>
        )}
      </Dialog>
    </div>
  );
};
