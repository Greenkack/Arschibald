/**
 * Drop Zone Component
 * Provides a target area for dropping draggable items
 */

import React from 'react';
import { useDragAndDrop, DragItem, DropZone as DropZoneType } from '../../hooks/useDragAndDrop';
import './DropZone.css';

export interface DropZoneProps {
  id: string;
  accepts: string[];
  onDrop: (item: DragItem) => void;
  validateDrop?: (item: DragItem) => boolean;
  children?: React.ReactNode;
  className?: string;
  emptyMessage?: string;
  disabled?: boolean;
}

export const DropZone: React.FC<DropZoneProps> = ({
  id,
  accepts,
  onDrop,
  validateDrop,
  children,
  className = '',
  emptyMessage = 'Drop items here',
  disabled = false,
}) => {
  const dropZone: DropZoneType = {
    id,
    accepts,
    onDrop,
  };

  const { dropTarget, handleDragOver, handleDragLeave, handleDrop } = useDragAndDrop({
    validateDrop: validateDrop
      ? (item) => validateDrop(item)
      : undefined,
  });

  const isActive = dropTarget === id;

  return (
    <div
      className={`drop-zone ${isActive ? 'active' : ''} ${
        disabled ? 'disabled' : ''
      } ${className}`}
      onDragOver={disabled ? undefined : handleDragOver(dropZone)}
      onDragLeave={disabled ? undefined : handleDragLeave}
      onDrop={disabled ? undefined : handleDrop(dropZone)}
    >
      {children || (
        <div className="drop-zone-empty">
          <i className="pi pi-inbox" style={{ fontSize: '2rem' }}></i>
          <p>{emptyMessage}</p>
        </div>
      )}
      {isActive && (
        <div className="drop-zone-overlay">
          <i className="pi pi-download" style={{ fontSize: '2rem' }}></i>
          <p>Drop here</p>
        </div>
      )}
    </div>
  );
};
