/**
 * Theme Import/Export Component
 * Allows users to export and import theme configurations
 */

import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dialog } from 'primereact/dialog';
import { Message } from 'primereact/message';
import { useThemeStore } from '../../store/themeStore';
import './ThemeImportExport.css';

export const ThemeImportExport: React.FC = () => {
  const { exportTheme, importTheme } = useThemeStore();
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [exportedTheme, setExportedTheme] = useState('');
  const [importText, setImportText] = useState('');
  const [importError, setImportError] = useState('');
  const [importSuccess, setImportSuccess] = useState(false);

  const handleExport = () => {
    const themeJson = exportTheme();
    setExportedTheme(themeJson);
    setShowExportDialog(true);
  };

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(exportedTheme);
      // Could add a toast notification here
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([exportedTheme], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'theme-config.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    setImportError('');
    setImportSuccess(false);

    try {
      importTheme(importText);
      setImportSuccess(true);
      setTimeout(() => {
        setShowImportDialog(false);
        setImportText('');
        setImportSuccess(false);
      }, 2000);
    } catch (error) {
      setImportError(error instanceof Error ? error.message : 'Failed to import theme');
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setImportText(content);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="theme-import-export">
      <div className="import-export-buttons">
        <Button
          label="Export Theme"
          icon="pi pi-download"
          onClick={handleExport}
          className="p-button-outlined"
        />
        <Button
          label="Import Theme"
          icon="pi pi-upload"
          onClick={() => setShowImportDialog(true)}
          className="p-button-outlined"
        />
      </div>

      {/* Export Dialog */}
      <Dialog
        header="Export Theme"
        visible={showExportDialog}
        onHide={() => setShowExportDialog(false)}
        style={{ width: '600px' }}
        footer={
          <div>
            <Button
              label="Copy to Clipboard"
              icon="pi pi-copy"
              onClick={handleCopyToClipboard}
              className="p-button-text"
            />
            <Button label="Download" icon="pi pi-download" onClick={handleDownload} />
          </div>
        }
      >
        <div className="export-content">
          <p>Copy this configuration or download it as a file:</p>
          <InputTextarea
            value={exportedTheme}
            readOnly
            rows={15}
            className="w-full"
            style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}
          />
        </div>
      </Dialog>

      {/* Import Dialog */}
      <Dialog
        header="Import Theme"
        visible={showImportDialog}
        onHide={() => {
          setShowImportDialog(false);
          setImportText('');
          setImportError('');
          setImportSuccess(false);
        }}
        style={{ width: '600px' }}
        footer={
          <div>
            <Button
              label="Cancel"
              icon="pi pi-times"
              onClick={() => setShowImportDialog(false)}
              className="p-button-text"
            />
            <Button label="Import" icon="pi pi-check" onClick={handleImport} disabled={!importText} />
          </div>
        }
      >
        <div className="import-content">
          <p>Paste theme configuration or upload a file:</p>

          <div className="file-upload-section">
            <input
              type="file"
              accept=".json"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              id="theme-file-upload"
            />
            <label htmlFor="theme-file-upload">
              <Button
                label="Choose File"
                icon="pi pi-file"
                className="p-button-outlined"
                onClick={() => document.getElementById('theme-file-upload')?.click()}
              />
            </label>
          </div>

          <InputTextarea
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            rows={15}
            className="w-full"
            placeholder="Paste theme JSON here..."
            style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}
          />

          {importError && (
            <Message severity="error" text={importError} className="w-full" style={{ marginTop: '1rem' }} />
          )}

          {importSuccess && (
            <Message
              severity="success"
              text="Theme imported successfully!"
              className="w-full"
              style={{ marginTop: '1rem' }}
            />
          )}
        </div>
      </Dialog>
    </div>
  );
};
