/**
 * File Drop Zone Component
 * Provides a drag and drop area for file uploads
 */

import React from 'react';
import { useFileDragAndDrop } from '../../hooks/useDragAndDrop';
import './FileDropZone.css';

export interface FileDropZoneProps {
  onFileDrop: (files: File[]) => void;
  accept?: string[];
  maxSize?: number;
  maxFiles?: number;
  validateFile?: (file: File) => boolean;
  className?: string;
  children?: React.ReactNode;
  disabled?: boolean;
}

export const FileDropZone: React.FC<FileDropZoneProps> = ({
  onFileDrop,
  accept,
  maxSize,
  maxFiles,
  validateFile,
  className = '',
  children,
  disabled = false,
}) => {
  const { isDraggingOver, error, handleDragOver, handleDragLeave, handleDrop } =
    useFileDragAndDrop({
      onFileDrop,
      accept,
      maxSize,
      maxFiles,
      validateFile,
    });

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      onFileDrop(files);
    }
  };

  return (
    <div
      className={`file-drop-zone ${isDraggingOver ? 'dragging-over' : ''} ${
        disabled ? 'disabled' : ''
      } ${className}`}
      onDragOver={disabled ? undefined : handleDragOver}
      onDragLeave={disabled ? undefined : handleDragLeave}
      onDrop={disabled ? undefined : handleDrop}
    >
      <input
        type="file"
        id="file-input"
        className="file-input"
        onChange={handleFileInput}
        accept={accept?.join(',')}
        multiple={!maxFiles || maxFiles > 1}
        disabled={disabled}
      />
      
      <label htmlFor="file-input" className="file-drop-label">
        {children || (
          <div className="file-drop-content">
            <i className="pi pi-cloud-upload" style={{ fontSize: '3rem' }}></i>
            <p className="file-drop-text">
              {isDraggingOver
                ? 'Drop files here'
                : 'Drag and drop files here or click to browse'}
            </p>
            {accept && accept.length > 0 && (
              <p className="file-drop-hint">Accepted: {accept.join(', ')}</p>
            )}
            {maxSize && (
              <p className="file-drop-hint">
                Max size: {(maxSize / 1024 / 1024).toFixed(2)}MB
              </p>
            )}
            {maxFiles && <p className="file-drop-hint">Max files: {maxFiles}</p>}
          </div>
        )}
      </label>

      {error && <div className="file-drop-error">{error}</div>}
    </div>
  );
};
