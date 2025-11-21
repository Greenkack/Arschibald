/**
 * Custom Hook for Migration Management
 * Handles migration state and API calls
 * Requirements: 5.5, 5.6, 5.7
 */

import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

interface MigrationState {
  status: 'idle' | 'running' | 'completed' | 'failed';
  progress: number;
  currentStep: string;
  details: {
    step: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    message: string;
    startTime?: string;
    endTime?: string;
    itemsProcessed?: number;
    totalItems?: number;
  }[];
  errors: {
    id: string;
    timestamp: string;
    step: string;
    severity: 'error' | 'warning' | 'info';
    message: string;
    details?: string;
    stackTrace?: string;
    affectedItems?: string[];
    suggestedAction?: string;
  }[];
}

interface MigrationConfig {
  sourcePath: string;
  targetPath: string;
  backupEnabled: boolean;
  validateAfterMigration: boolean;
}

export const useMigration = () => {
  const [migrationState, setMigrationState] = useState<MigrationState>({
    status: 'idle',
    progress: 0,
    currentStep: '',
    details: [],
    errors: []
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [migrationReport, setMigrationReport] = useState<any>(null);

  // Poll migration status
  const pollMigrationStatus = useCallback(async () => {
    try {
      const response = await api.get('/api/v1/migration/status');
      const status = response.data;
      
      setMigrationState({
        status: status.status,
        progress: status.progress,
        currentStep: status.current_step,
        details: status.details || [],
        errors: status.errors || []
      });

      // If migration is complete or failed, stop polling
      if (status.status === 'completed' || status.status === 'failed') {
        if (status.status === 'completed') {
          // Fetch final report
          const reportResponse = await api.get('/api/v1/migration/report');
          setMigrationReport(reportResponse.data);
        }
        return false; // Stop polling
      }
      
      return true; // Continue polling
    } catch (err: any) {
      console.error('Error polling migration status:', err);
      setError(err.response?.data?.message || 'Fehler beim Abrufen des Migrationsstatus');
      return false;
    }
  }, []);

  // Start migration
  const startMigration = useCallback(async (config?: Partial<MigrationConfig>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/migration/start', config || {});
      
      setMigrationState({
        status: 'running',
        progress: 0,
        currentStep: 'Initialisierung',
        details: [],
        errors: []
      });

      // Start polling for status updates
      const pollInterval = setInterval(async () => {
        const shouldContinue = await pollMigrationStatus();
        if (!shouldContinue) {
          clearInterval(pollInterval);
          setIsLoading(false);
        }
      }, 2000); // Poll every 2 seconds

      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Fehler beim Starten der Migration');
      setMigrationState(prev => ({ ...prev, status: 'failed' }));
      setIsLoading(false);
      throw err;
    }
  }, [pollMigrationStatus]);

  // Rollback migration
  const rollbackMigration = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/migration/rollback');
      
      setMigrationState({
        status: 'idle',
        progress: 0,
        currentStep: '',
        details: [],
        errors: []
      });
      
      setIsLoading(false);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Fehler beim Rollback');
      setIsLoading(false);
      throw err;
    }
  }, []);

  // Validate migration
  const validateMigration = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/migration/validate');
      setIsLoading(false);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Fehler bei der Validierung');
      setIsLoading(false);
      throw err;
    }
  }, []);

  // Get migration report
  const getMigrationReport = useCallback(() => {
    return migrationReport;
  }, [migrationReport]);

  // Check if migration is available
  const checkMigrationAvailable = useCallback(async () => {
    try {
      const response = await api.get('/api/v1/migration/check');
      return response.data;
    } catch (err: any) {
      console.error('Error checking migration availability:', err);
      return { available: false, reason: err.response?.data?.message };
    }
  }, []);

  return {
    migrationState,
    startMigration,
    rollbackMigration,
    validateMigration,
    getMigrationReport,
    checkMigrationAvailable,
    isLoading,
    error
  };
};
