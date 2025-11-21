/**
 * React Hook for Native File Dialogs
 * 
 * Provides easy access to Electron's native file dialogs from React components.
 * Supports single/multiple file selection, save dialogs, and directory selection.
 * 
 * @module useFileDialog
 */

import { useState, useCallback } from 'react';

interface FileDialogOptions {
  title?: string;
  buttonLabel?: string;
  defaultPath?: string;
  filters?: Array<{ name: string; extensions: string[] }>;
  properties?: string[];
}

interface FileResult {
  canceled: boolean;
  filePath: string | null;
  fileName?: string;
}

interface FilesResult {
  canceled: boolean;
  filePaths: string[];
  fileNames?: string[];
  count?: number;
}

interface DirectoryResult {
  canceled: boolean;
  directoryPath: string | null;
  directoryName?: string;
}

/**
 * Hook for working with native file dialogs
 */
export const useFileDialog = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Open a single file selection dialog
   */
  const openFile = useCallback(async (options?: FileDialogOptions): Promise<FileResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.selectFile(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open file dialog';
      setError(errorMessage);
      return { canceled: true, filePath: null };
    } finally {
      setIsOpen(false);
    }
  }, []);

  /**
   * Open a multiple file selection dialog
   */
  const openFiles = useCallback(async (options?: FileDialogOptions): Promise<FilesResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.selectFiles(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open files dialog';
      setError(errorMessage);
      return { canceled: true, filePaths: [] };
    } finally {
      setIsOpen(false);
    }
  }, []);

  /**
   * Open a save file dialog
   */
  const saveFile = useCallback(async (options?: FileDialogOptions): Promise<FileResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.saveFile(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open save dialog';
      setError(errorMessage);
      return { canceled: true, filePath: null };
    } finally {
      setIsOpen(false);
    }
  }, []);

  /**
   * Open a directory selection dialog
   */
  const openDirectory = useCallback(async (options?: FileDialogOptions): Promise<DirectoryResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.selectDirectory(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open directory dialog';
      setError(errorMessage);
      return { canceled: true, directoryPath: null };
    } finally {
      setIsOpen(false);
    }
  }, []);

  /**
   * Open an Excel file selection dialog
   */
  const openExcelFile = useCallback(async (options?: FileDialogOptions): Promise<FileResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.selectExcelFile(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open Excel file dialog';
      setError(errorMessage);
      return { canceled: true, filePath: null };
    } finally {
      setIsOpen(false);
    }
  }, []);

  /**
   * Open a PDF file selection dialog
   */
  const openPDFFile = useCallback(async (options?: FileDialogOptions): Promise<FileResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.selectPDFFile(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open PDF file dialog';
      setError(errorMessage);
      return { canceled: true, filePath: null };
    } finally {
      setIsOpen(false);
    }
  }, []);

  /**
   * Open an image file selection dialog
   */
  const openImageFile = useCallback(async (options?: FileDialogOptions): Promise<FileResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.selectImageFile(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open image file dialog';
      setError(errorMessage);
      return { canceled: true, filePath: null };
    } finally {
      setIsOpen(false);
    }
  }, []);

  /**
   * Open a multiple image files selection dialog
   */
  const openImageFiles = useCallback(async (options?: FileDialogOptions): Promise<FilesResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.selectImageFiles(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open image files dialog';
      setError(errorMessage);
      return { canceled: true, filePaths: [] };
    } finally {
      setIsOpen(false);
    }
  }, []);

  /**
   * Open a save Excel file dialog
   */
  const saveExcelFile = useCallback(async (options?: FileDialogOptions): Promise<FileResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.saveExcelFile(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open save Excel dialog';
      setError(errorMessage);
      return { canceled: true, filePath: null };
    } finally {
      setIsOpen(false);
    }
  }, []);

  /**
   * Open a save PDF file dialog
   */
  const savePDFFile = useCallback(async (options?: FileDialogOptions): Promise<FileResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.savePDFFile(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open save PDF dialog';
      setError(errorMessage);
      return { canceled: true, filePath: null };
    } finally {
      setIsOpen(false);
    }
  }, []);

  /**
   * Open a save image file dialog
   */
  const saveImageFile = useCallback(async (options?: FileDialogOptions): Promise<FileResult> => {
    setIsOpen(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.saveImageFile(options);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to open save image dialog';
      setError(errorMessage);
      return { canceled: true, filePath: null };
    } finally {
      setIsOpen(false);
    }
  }, []);

  return {
    // State
    isOpen,
    error,
    
    // Methods
    openFile,
    openFiles,
    saveFile,
    openDirectory,
    
    // Specialized methods
    openExcelFile,
    openPDFFile,
    openImageFile,
    openImageFiles,
    saveExcelFile,
    savePDFFile,
    saveImageFile,
  };
};

export default useFileDialog;
