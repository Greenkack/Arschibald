/**
 * Custom hook for drag and drop functionality
 * Provides reusable drag and drop logic for various components
 */

import { useState, useCallback, DragEvent } from 'react';

export interface DragItem {
  id: string;
  type: string;
  data: any;
}

export interface DropZone {
  id: string;
  accepts: string[];
  onDrop: (item: DragItem) => void;
}

export interface UseDragAndDropOptions {
  onDragStart?: (item: DragItem) => void;
  onDragEnd?: (item: DragItem) => void;
  onDrop?: (item: DragItem, dropZone: DropZone) => void;
  validateDrop?: (item: DragItem, dropZone: DropZone) => boolean;
}

export const useDragAndDrop = (options: UseDragAndDropOptions = {}) => {
  const [draggedItem, setDraggedItem] = useState<DragItem | null>(null);
  const [dropTarget, setDropTarget] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragStart = useCallback(
    (item: DragItem) => (e: DragEvent) => {
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('application/json', JSON.stringify(item));
      setDraggedItem(item);
      setIsDragging(true);
      options.onDragStart?.(item);
    },
    [options]
  );

  const handleDragEnd = useCallback(
    (item: DragItem) => (e: DragEvent) => {
      setDraggedItem(null);
      setIsDragging(false);
      setDropTarget(null);
      options.onDragEnd?.(item);
    },
    [options]
  );

  const handleDragOver = useCallback(
    (dropZone: DropZone) => (e: DragEvent) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      
      if (draggedItem && dropZone.accepts.includes(draggedItem.type)) {
        setDropTarget(dropZone.id);
      }
    },
    [draggedItem]
  );

  const handleDragLeave = useCallback(() => {
    setDropTarget(null);
  }, []);

  const handleDrop = useCallback(
    (dropZone: DropZone) => (e: DragEvent) => {
      e.preventDefault();
      
      try {
        const data = e.dataTransfer.getData('application/json');
        const item: DragItem = JSON.parse(data);
        
        // Validate drop
        if (options.validateDrop && !options.validateDrop(item, dropZone)) {
          return;
        }
        
        // Check if drop zone accepts this item type
        if (!dropZone.accepts.includes(item.type)) {
          return;
        }
        
        dropZone.onDrop(item);
        options.onDrop?.(item, dropZone);
      } catch (error) {
        console.error('Error handling drop:', error);
      } finally {
        setDropTarget(null);
        setDraggedItem(null);
        setIsDragging(false);
      }
    },
    [options]
  );

  return {
    draggedItem,
    dropTarget,
    isDragging,
    handleDragStart,
    handleDragEnd,
    handleDragOver,
    handleDragLeave,
    handleDrop,
  };
};

/**
 * Hook for file drag and drop
 */
export interface UseFileDragAndDropOptions {
  onFileDrop: (files: File[]) => void;
  accept?: string[];
  maxSize?: number; // in bytes
  maxFiles?: number;
  validateFile?: (file: File) => boolean;
}

export const useFileDragAndDrop = (options: UseFileDragAndDropOptions) => {
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFiles = useCallback(
    (files: File[]): { valid: File[]; errors: string[] } => {
      const valid: File[] = [];
      const errors: string[] = [];

      if (options.maxFiles && files.length > options.maxFiles) {
        errors.push(`Maximum ${options.maxFiles} files allowed`);
        return { valid, errors };
      }

      for (const file of files) {
        // Check file type
        if (options.accept && options.accept.length > 0) {
          const fileType = file.type || '';
          const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
          const isAccepted = options.accept.some(
            (accept) =>
              accept === fileType ||
              accept === fileExt ||
              (accept.endsWith('/*') && fileType.startsWith(accept.replace('/*', '')))
          );
          
          if (!isAccepted) {
            errors.push(`File type not accepted: ${file.name}`);
            continue;
          }
        }

        // Check file size
        if (options.maxSize && file.size > options.maxSize) {
          errors.push(`File too large: ${file.name} (max ${options.maxSize / 1024 / 1024}MB)`);
          continue;
        }

        // Custom validation
        if (options.validateFile && !options.validateFile(file)) {
          errors.push(`File validation failed: ${file.name}`);
          continue;
        }

        valid.push(file);
      }

      return { valid, errors };
    },
    [options]
  );

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(true);
    setError(null);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDraggingOver(false);

      const files = Array.from(e.dataTransfer.files);
      const { valid, errors } = validateFiles(files);

      if (errors.length > 0) {
        setError(errors.join(', '));
        return;
      }

      if (valid.length > 0) {
        options.onFileDrop(valid);
        setError(null);
      }
    },
    [options, validateFiles]
  );

  return {
    isDraggingOver,
    error,
    handleDragOver,
    handleDragLeave,
    handleDrop,
  };
};

/**
 * Hook for list reordering with drag and drop
 */
export interface UseListReorderOptions<T> {
  items: T[];
  onReorder: (items: T[]) => void;
  getId: (item: T) => string;
}

export const useListReorder = <T,>(options: UseListReorderOptions<T>) => {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dropIndex, setDropIndex] = useState<number | null>(null);

  const handleDragStart = useCallback((index: number) => (e: DragEvent) => {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', index.toString());
    setDraggedIndex(index);
  }, []);

  const handleDragOver = useCallback((index: number) => (e: DragEvent) => {
    e.preventDefault();
    if (draggedIndex !== null && draggedIndex !== index) {
      setDropIndex(index);
    }
  }, [draggedIndex]);

  const handleDrop = useCallback((index: number) => (e: DragEvent) => {
    e.preventDefault();
    
    if (draggedIndex === null || draggedIndex === index) {
      return;
    }

    const newItems = [...options.items];
    const [removed] = newItems.splice(draggedIndex, 1);
    newItems.splice(index, 0, removed);

    options.onReorder(newItems);
    setDraggedIndex(null);
    setDropIndex(null);
  }, [draggedIndex, options]);

  const handleDragEnd = useCallback(() => {
    setDraggedIndex(null);
    setDropIndex(null);
  }, []);

  return {
    draggedIndex,
    dropIndex,
    handleDragStart,
    handleDragOver,
    handleDrop,
    handleDragEnd,
  };
};
