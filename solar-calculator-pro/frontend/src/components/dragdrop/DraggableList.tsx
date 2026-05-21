/**
 * Draggable List Component
 * Provides a list with drag and drop reordering capability
 */

import React from 'react';
import { useListReorder } from '../../hooks/useDragAndDrop';
import './DraggableList.css';

export interface DraggableListProps<T> {
  items: T[];
  onReorder: (items: T[]) => void;
  getId: (item: T) => string;
  renderItem: (item: T, index: number) => React.ReactNode;
  className?: string;
  itemClassName?: string;
  dragHandleClassName?: string;
  showDragHandle?: boolean;
}

export function DraggableList<T>({
  items,
  onReorder,
  getId,
  renderItem,
  className = '',
  itemClassName = '',
  dragHandleClassName = '',
  showDragHandle = true,
}: DraggableListProps<T>) {
  const { draggedIndex, dropIndex, handleDragStart, handleDragOver, handleDrop, handleDragEnd } =
    useListReorder({
      items,
      onReorder,
      getId,
    });

  return (
    <div className={`draggable-list ${className}`}>
      {items.map((item, index) => (
        <div
          key={getId(item)}
          className={`draggable-list-item ${itemClassName} ${
            draggedIndex === index ? 'dragging' : ''
          } ${dropIndex === index ? 'drop-target' : ''}`}
          draggable
          onDragStart={handleDragStart(index)}
          onDragOver={handleDragOver(index)}
          onDrop={handleDrop(index)}
          onDragEnd={handleDragEnd}
        >
          {showDragHandle && (
            <div className={`drag-handle ${dragHandleClassName}`}>
              <i className="pi pi-bars"></i>
            </div>
          )}
          <div className="draggable-list-item-content">{renderItem(item, index)}</div>
        </div>
      ))}
    </div>
  );
}
