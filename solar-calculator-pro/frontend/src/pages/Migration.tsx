/**
 * Migration Page
 * Main page for data migration from Streamlit to Electron
 * Requirements: 5.5, 5.6, 5.7
 */

import React from 'react';
import { MigrationWizard } from '../components/migration/MigrationWizard';
import './Migration.css';

export const Migration: React.FC = () => {
  return (
    <div className="migration-page">
      <div className="page-header">
        <h1>Datenmigration</h1>
        <p className="page-description">
          Migrieren Sie Ihre Daten von der Streamlit-Anwendung zur neuen Electron-Anwendung.
          Der Assistent führt Sie durch den gesamten Prozess.
        </p>
      </div>
      
      <MigrationWizard />
    </div>
  );
};
