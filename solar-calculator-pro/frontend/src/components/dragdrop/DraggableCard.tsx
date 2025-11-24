/**
 * Draggable Card Component
 * Provides a card that can be dragged and dropped
 */

import React from 'react';
import { useDragAndDrop, DragItem } from '../../hooks/useDragAndDrop';
import './DraggableCard.css';

export interface DraggableCardProps {
  id: string;
  type: string;
  data: any;
  children: React.ReactNode;
  className?: string;
  onDragStart?: (item: DragItem) => void;
  onDragEnd?: (item: DragItem) => void;
  disabled?: boolean;
}

export const DraggableCard: React.FC<DraggableCardProps> = ({
  id,
  type,
  data,
  children,
  className = '',
  onDragStart,
  onDragEnd,
  disabled = false,
}) => {
  const item: DragItem = { id, type, data };
  
  const { isDragging, handleDragStart, handleDragEnd } = useDragAndDrop({
    onDragStart,
    onDragEnd,
  });

  return (
    <div
      className={`draggable-card ${isDragging ? 'dragging' : ''} ${
        disabled ? 'disabled' : ''
      } ${className}`}
      draggable={!disabled}
      onDragStart={handleDragStart(item)}
      onDragEnd={handleDragEnd(item)}
    >
      {children}
    </div>
  );
};
