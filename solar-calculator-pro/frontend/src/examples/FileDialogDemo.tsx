/**
 * File Dialog Demo Component
 * 
 * Demonstrates all native file dialog capabilities including:
 * - Single file selection
 * - Multiple file selection
 * - Save file dialogs
 * - Directory selection
 * - File type filters
 * - Specialized dialogs for common file types
 */

import React, { useState } from 'react';
import { useFileDialog } from '../hooks/useFileDialog';
import './FileDialogDemo.css';

interface SelectedFile {
  path: string;
  name: string;
  type: string;
}

export const FileDialogDemo: React.FC = () => {
  const fileDialog = useFileDialog();
  const [selectedFiles, setSelectedFiles] = useState<SelectedFile[]>([]);
  const [lastAction, setLastAction] = useState<string>('');
  const [result, setResult] = useState<any>(null);

  const handleOpenFile = async () => {
    setLastAction('Opening single file...');
    const result = await fileDialog.openFile({
      title: 'Select a File',
      buttonLabel: 'Open',
    });
    
    setResult(result);
    if (!result.canceled && result.filePath) {
      setSelectedFiles([{
        path: result.filePath,
        name: result.fileName || '',
        type: 'single'
      }]);
      setLastAction(`Selected: ${result.fileName}`);
    } else {
      setLastAction('File selection canceled');
    }
  };

  const handleOpenFiles = async () => {
    setLastAction('Opening multiple files...');
    const result = await fileDialog.openFiles({
      title: 'Select Multiple Files',
      buttonLabel: 'Open All',
    });
    
    setResult(result);
    if (!result.canceled && result.filePaths.length > 0) {
      const files = result.filePaths.map((path, index) => ({
        path,
        name: result.fileNames?.[index] || '',
        type: 'multiple'
      }));
      setSelectedFiles(files);
      setLastAction(`Selected ${result.count} files`);
    } else {
      setLastAction('File selection canceled');
    }
  };

  const handleSaveFile = async () => {
    setLastAction('Opening save dialog...');
    const result = await fileDialog.saveFile({
      title: 'Save File As',
      buttonLabel: 'Save',
      defaultPath: 'my-document.txt',
      filters: [
        { name: 'Text Files', extensions: ['txt'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
    
    setResult(result);
    if (!result.canceled && result.filePath) {
      setLastAction(`Save location: ${result.fileName}`);
    } else {
      setLastAction('Save canceled');
    }
  };

  const handleOpenDirectory = async () => {
    setLastAction('Opening directory selection...');
    const result = await fileDialog.openDirectory({
      title: 'Select a Directory',
      buttonLabel: 'Select Folder',
    });
    
    setResult(result);
    if (!result.canceled && result.directoryPath) {
      setSelectedFiles([{
        path: result.directoryPath,
        name: result.directoryName || '',
        type: 'directory'
      }]);
      setLastAction(`Selected directory: ${result.directoryName}`);
    } else {
      setLastAction('Directory selection canceled');
    }
  };

  const handleOpenExcelFile = async () => {
    setLastAction('Opening Excel file selection...');
    const result = await fileDialog.openExcelFile({
      title: 'Select Excel File',
      defaultPath: process.env.HOME || process.env.USERPROFILE,
    });
    
    setResult(result);
    if (!result.canceled && result.filePath) {
      setSelectedFiles([{
        path: result.filePath,
        name: result.fileName || '',
        type: 'excel'
      }]);
      setLastAction(`Selected Excel file: ${result.fileName}`);
    } else {
      setLastAction('Excel file selection canceled');
    }
  };

  const handleOpenPDFFile = async () => {
    setLastAction('Opening PDF file selection...');
    const result = await fileDialog.openPDFFile({
      title: 'Select PDF File',
    });
    
    setResult(result);
    if (!result.canceled && result.filePath) {
      setSelectedFiles([{
        path: result.filePath,
        name: result.fileName || '',
        type: 'pdf'
      }]);
      setLastAction(`Selected PDF file: ${result.fileName}`);
    } else {
      setLastAction('PDF file selection canceled');
    }
  };

  const handleOpenImageFile = async () => {
    setLastAction('Opening image file selection...');
    const result = await fileDialog.openImageFile({
      title: 'Select Image File',
    });
    
    setResult(result);
    if (!result.canceled && result.filePath) {
      setSelectedFiles([{
        path: result.filePath,
        name: result.fileName || '',
        type: 'image'
      }]);
      setLastAction(`Selected image: ${result.fileName}`);
    } else {
      setLastAction('Image file selection canceled');
    }
  };

  const handleOpenImageFiles = async () => {
    setLastAction('Opening multiple image files selection...');
    const result = await fileDialog.openImageFiles({
      title: 'Select Multiple Images',
    });
    
    setResult(result);
    if (!result.canceled && result.filePaths.length > 0) {
      const files = result.filePaths.map((path, index) => ({
        path,
        name: result.fileNames?.[index] || '',
        type: 'images'
      }));
      setSelectedFiles(files);
      setLastAction(`Selected ${result.count} images`);
    } else {
      setLastAction('Image files selection canceled');
    }
  };

  const handleSaveExcelFile = async () => {
    setLastAction('Opening save Excel dialog...');
    const result = await fileDialog.saveExcelFile({
      title: 'Save Excel File',
      defaultPath: 'export.xlsx',
    });
    
    setResult(result);
    if (!result.canceled && result.filePath) {
      setLastAction(`Save Excel to: ${result.fileName}`);
    } else {
      setLastAction('Save Excel canceled');
    }
  };

  const handleSavePDFFile = async () => {
    setLastAction('Opening save PDF dialog...');
    const result = await fileDialog.savePDFFile({
      title: 'Save PDF File',
      defaultPath: 'document.pdf',
    });
    
    setResult(result);
    if (!result.canceled && result.filePath) {
      setLastAction(`Save PDF to: ${result.fileName}`);
    } else {
      setLastAction('Save PDF canceled');
    }
  };

  const handleSaveImageFile = async () => {
    setLastAction('Opening save image dialog...');
    const result = await fileDialog.saveImageFile({
      title: 'Save Image File',
      defaultPath: 'screenshot.png',
    });
    
    setResult(result);
    if (!result.canceled && result.filePath) {
      setLastAction(`Save image to: ${result.fileName}`);
    } else {
      setLastAction('Save image canceled');
    }
  };

  const handleCustomFilters = async () => {
    setLastAction('Opening file with custom filters...');
    const result = await fileDialog.openFile({
      title: 'Select Project File',
      buttonLabel: 'Open Project',
      filters: [
        { name: 'Project Files', extensions: ['proj', 'project'] },
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'XML Files', extensions: ['xml'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
    
    setResult(result);
    if (!result.canceled && result.filePath) {
      setSelectedFiles([{
        path: result.filePath,
        name: result.fileName || '',
        type: 'custom'
      }]);
      setLastAction(`Selected project file: ${result.fileName}`);
    } else {
      setLastAction('Project file selection canceled');
    }
  };

  const clearSelection = () => {
    setSelectedFiles([]);
    setLastAction('');
    setResult(null);
  };

  return (
    <div className="file-dialog-demo">
      <div className="demo-header">
        <h1>Native File Dialog Demo</h1>
        <p>Test all native file dialog capabilities</p>
      </div>

      <div className="demo-content">
        {/* Basic File Operations */}
        <section className="demo-section">
          <h2>Basic File Operations</h2>
          <div className="button-grid">
            <button 
              onClick={handleOpenFile}
              disabled={fileDialog.isOpen}
              className="demo-button"
            >
              📄 Open Single File
            </button>
            
            <button 
              onClick={handleOpenFiles}
              disabled={fileDialog.isOpen}
              className="demo-button"
            >
              📑 Open Multiple Files
            </button>
            
            <button 
              onClick={handleSaveFile}
              disabled={fileDialog.isOpen}
              className="demo-button"
            >
              💾 Save File
            </button>
            
            <button 
              onClick={handleOpenDirectory}
              disabled={fileDialog.isOpen}
              className="demo-button"
            >
              📁 Select Directory
            </button>
          </div>
        </section>

        {/* Specialized File Types */}
        <section className="demo-section">
          <h2>Specialized File Types</h2>
          <div className="button-grid">
            <button 
              onClick={handleOpenExcelFile}
              disabled={fileDialog.isOpen}
              className="demo-button excel"
            >
              📊 Open Excel File
            </button>
            
            <button 
              onClick={handleOpenPDFFile}
              disabled={fileDialog.isOpen}
              className="demo-button pdf"
            >
              📕 Open PDF File
            </button>
            
            <button 
              onClick={handleOpenImageFile}
              disabled={fileDialog.isOpen}
              className="demo-button image"
            >
              🖼️ Open Image File
            </button>
            
            <button 
              onClick={handleOpenImageFiles}
              disabled={fileDialog.isOpen}
              className="demo-button images"
            >
              🖼️ Open Multiple Images
            </button>
          </div>
        </section>

        {/* Specialized Save Dialogs */}
        <section className="demo-section">
          <h2>Specialized Save Dialogs</h2>
          <div className="button-grid">
            <button 
              onClick={handleSaveExcelFile}
              disabled={fileDialog.isOpen}
              className="demo-button excel"
            >
              💾 Save Excel File
            </button>
            
            <button 
              onClick={handleSavePDFFile}
              disabled={fileDialog.isOpen}
              className="demo-button pdf"
            >
              💾 Save PDF File
            </button>
            
            <button 
              onClick={handleSaveImageFile}
              disabled={fileDialog.isOpen}
              className="demo-button image"
            >
              💾 Save Image File
            </button>
          </div>
        </section>

        {/* Advanced Features */}
        <section className="demo-section">
          <h2>Advanced Features</h2>
          <div className="button-grid">
            <button 
              onClick={handleCustomFilters}
              disabled={fileDialog.isOpen}
              className="demo-button custom"
            >
              🔧 Custom File Filters
            </button>
            
            <button 
              onClick={clearSelection}
              disabled={fileDialog.isOpen}
              className="demo-button clear"
            >
              🗑️ Clear Selection
            </button>
          </div>
        </section>

        {/* Status Display */}
        <section className="demo-section">
          <h2>Status</h2>
          <div className="status-display">
            <div className="status-item">
              <strong>Dialog State:</strong>
              <span className={fileDialog.isOpen ? 'status-open' : 'status-closed'}>
                {fileDialog.isOpen ? 'Open' : 'Closed'}
              </span>
            </div>
            
            {lastAction && (
              <div className="status-item">
                <strong>Last Action:</strong>
                <span>{lastAction}</span>
              </div>
            )}
            
            {fileDialog.error && (
              <div className="status-item error">
                <strong>Error:</strong>
                <span>{fileDialog.error}</span>
              </div>
            )}
          </div>
        </section>

        {/* Selected Files Display */}
        {selectedFiles.length > 0 && (
          <section className="demo-section">
            <h2>Selected Files ({selectedFiles.length})</h2>
            <div className="file-list">
              {selectedFiles.map((file, index) => (
                <div key={index} className="file-item">
                  <div className="file-icon">
                    {file.type === 'directory' ? '📁' : 
                     file.type === 'excel' ? '📊' :
                     file.type === 'pdf' ? '📕' :
                     file.type === 'image' || file.type === 'images' ? '🖼️' :
                     '📄'}
                  </div>
                  <div className="file-info">
                    <div className="file-name">{file.name}</div>
                    <div className="file-path">{file.path}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Raw Result Display */}
        {result && (
          <section className="demo-section">
            <h2>Raw Result</h2>
            <pre className="result-display">
              {JSON.stringify(result, null, 2)}
            </pre>
          </section>
        )}
      </div>
    </div>
  );
};

export default FileDialogDemo;
