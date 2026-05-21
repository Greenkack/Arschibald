/**
 * Migration Wizard Component
 * Provides step-by-step interface for migrating from Streamlit to Electron
 * Requirements: 5.5, 5.6, 5.7
 */

import React, { useState, useEffect } from 'react';
import { Steps } from 'primereact/steps';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { Dialog } from 'primereact/dialog';
import { ConfirmDialog } from 'primereact/confirmdialog';
import { MigrationProgress } from './MigrationProgress';
import { MigrationErrorReport } from './MigrationErrorReport';
import { MigrationReport } from './MigrationReport';
import { useMigration } from '../../hooks/useMigration';
import './MigrationWizard.css';

interface MigrationStep {
  label: string;
  icon: string;
  component: React.ReactNode;
}

export const MigrationWizard: React.FC = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [showRollbackDialog, setShowRollbackDialog] = useState(false);
  const [showReportDialog, setShowReportDialog] = useState(false);
  
  const {
    migrationState,
    startMigration,
    rollbackMigration,
    validateMigration,
    getMigrationReport,
    isLoading,
    error
  } = useMigration();

  const steps: MigrationStep[] = [
    {
      label: 'Vorbereitung',
      icon: 'pi pi-cog',
      component: <PreparationStep />
    },
    {
      label: 'Backup',
      icon: 'pi pi-save',
      component: <BackupStep />
    },
    {
      label: 'Migration',
      icon: 'pi pi-sync',
      component: <MigrationStep />
    },
    {
      label: 'Validierung',
      icon: 'pi pi-check-circle',
      component: <ValidationStep />
    },
    {
      label: 'Abschluss',
      icon: 'pi pi-flag',
      component: <CompletionStep />
    }
  ];

  const handleNext = () => {
    if (activeIndex < steps.length - 1) {
      setActiveIndex(activeIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (activeIndex > 0) {
      setActiveIndex(activeIndex - 1);
    }
  };

  const handleStartMigration = async () => {
    try {
      await startMigration();
      handleNext();
    } catch (err) {
      console.error('Migration failed:', err);
    }
  };

  const handleRollback = async () => {
    try {
      await rollbackMigration();
      setShowRollbackDialog(false);
      setActiveIndex(0);
    } catch (err) {
      console.error('Rollback failed:', err);
    }
  };

  const handleViewReport = () => {
    setShowReportDialog(true);
  };

  return (
    <div className="migration-wizard">
      <Card title="Datenmigration - Streamlit zu Electron">
        <div className="wizard-header">
          <Steps
            model={steps.map(step => ({
              label: step.label,
              icon: step.icon
            }))}
            activeIndex={activeIndex}
            onSelect={(e) => setActiveIndex(e.index)}
            readOnly={migrationState.status === 'running'}
          />
        </div>

        {error && (
          <Message
            severity="error"
            text={error}
            className="migration-error"
          />
        )}

        <div className="wizard-content">
          {steps[activeIndex].component}
        </div>

        {migrationState.status === 'running' && (
          <MigrationProgress
            progress={migrationState.progress}
            currentStep={migrationState.currentStep}
            details={migrationState.details}
          />
        )}

        {migrationState.errors.length > 0 && (
          <MigrationErrorReport errors={migrationState.errors} />
        )}

        <div className="wizard-footer">
          <Button
            label="Zurück"
            icon="pi pi-arrow-left"
            onClick={handlePrevious}
            disabled={activeIndex === 0 || migrationState.status === 'running'}
            className="p-button-secondary"
          />

          {activeIndex === 2 && migrationState.status === 'idle' && (
            <Button
              label="Migration starten"
              icon="pi pi-play"
              onClick={handleStartMigration}
              loading={isLoading}
              className="p-button-success"
            />
          )}

          {migrationState.status === 'completed' && (
            <>
              <Button
                label="Bericht anzeigen"
                icon="pi pi-file"
                onClick={handleViewReport}
                className="p-button-info"
              />
              <Button
                label="Weiter"
                icon="pi pi-arrow-right"
                onClick={handleNext}
                disabled={activeIndex === steps.length - 1}
              />
            </>
          )}

          {migrationState.status === 'failed' && (
            <Button
              label="Rollback durchführen"
              icon="pi pi-undo"
              onClick={() => setShowRollbackDialog(true)}
              className="p-button-danger"
            />
          )}

          {activeIndex !== 2 && migrationState.status !== 'running' && (
            <Button
              label="Weiter"
              icon="pi pi-arrow-right"
              onClick={handleNext}
              disabled={activeIndex === steps.length - 1}
            />
          )}
        </div>
      </Card>

      {/* Rollback Confirmation Dialog */}
      <Dialog
        header="Rollback bestätigen"
        visible={showRollbackDialog}
        style={{ width: '450px' }}
        onHide={() => setShowRollbackDialog(false)}
        footer={
          <div>
            <Button
              label="Abbrechen"
              icon="pi pi-times"
              onClick={() => setShowRollbackDialog(false)}
              className="p-button-text"
            />
            <Button
              label="Rollback durchführen"
              icon="pi pi-undo"
              onClick={handleRollback}
              className="p-button-danger"
              loading={isLoading}
            />
          </div>
        }
      >
        <div className="rollback-warning">
          <i className="pi pi-exclamation-triangle" style={{ fontSize: '3rem', color: 'var(--orange-500)' }} />
          <p>
            Möchten Sie wirklich einen Rollback durchführen? Dies wird alle migrierten Daten
            entfernen und die ursprünglichen Daten aus dem Backup wiederherstellen.
          </p>
          <p><strong>Diese Aktion kann nicht rückgängig gemacht werden.</strong></p>
        </div>
      </Dialog>

      {/* Migration Report Dialog */}
      <Dialog
        header="Migrationsbericht"
        visible={showReportDialog}
        style={{ width: '80vw', maxWidth: '1200px' }}
        onHide={() => setShowReportDialog(false)}
        maximizable
      >
        <MigrationReport report={getMigrationReport()} />
      </Dialog>
    </div>
  );
};

// Step Components
const PreparationStep: React.FC = () => {
  return (
    <div className="preparation-step">
      <h3>Vorbereitung der Migration</h3>
      <p>
        Bevor Sie mit der Migration beginnen, stellen Sie bitte sicher, dass:
      </p>
      <ul>
        <li>Die Streamlit-Anwendung geschlossen ist</li>
        <li>Alle Daten gespeichert sind</li>
        <li>Ausreichend Speicherplatz verfügbar ist (mindestens 2x die Größe der aktuellen Daten)</li>
        <li>Sie über Administratorrechte verfügen</li>
      </ul>
      <Message
        severity="info"
        text="Die Migration kann je nach Datenmenge 5-30 Minuten dauern."
      />
    </div>
  );
};

const BackupStep: React.FC = () => {
  return (
    <div className="backup-step">
      <h3>Backup-Erstellung</h3>
      <p>
        Ein vollständiges Backup Ihrer Daten wird erstellt, bevor die Migration beginnt.
        Dies ermöglicht einen Rollback im Fehlerfall.
      </p>
      <Message
        severity="warn"
        text="Stellen Sie sicher, dass während des Backups keine Änderungen an den Daten vorgenommen werden."
      />
    </div>
  );
};

const MigrationStep: React.FC = () => {
  return (
    <div className="migration-step">
      <h3>Datenmigration</h3>
      <p>
        Die folgenden Daten werden migriert:
      </p>
      <ul>
        <li>Datenbanken (SQLite)</li>
        <li>Einstellungen und Konfigurationen</li>
        <li>Projektdaten</li>
        <li>Benutzerdaten und Profile</li>
        <li>Hochgeladene Dateien</li>
      </ul>
      <Message
        severity="info"
        text="Bitte schließen Sie die Anwendung nicht während der Migration."
      />
    </div>
  );
};

const ValidationStep: React.FC = () => {
  return (
    <div className="validation-step">
      <h3>Validierung</h3>
      <p>
        Die migrierten Daten werden auf Vollständigkeit und Integrität geprüft:
      </p>
      <ul>
        <li>Datenbankintegrität</li>
        <li>Dateianzahl und -größe</li>
        <li>Datenintegrität (Checksums)</li>
        <li>Referenzielle Integrität</li>
      </ul>
    </div>
  );
};

const CompletionStep: React.FC = () => {
  return (
    <div className="completion-step">
      <h3>Migration abgeschlossen</h3>
      <div className="success-message">
        <i className="pi pi-check-circle" style={{ fontSize: '4rem', color: 'var(--green-500)' }} />
        <p>
          Die Migration wurde erfolgreich abgeschlossen! Ihre Daten wurden sicher übertragen.
        </p>
      </div>
      <Message
        severity="success"
        text="Sie können nun die neue Electron-Anwendung verwenden. Die Streamlit-Daten bleiben als Backup erhalten."
      />
    </div>
  );
};
