/**
 * useModuleFeatures Hook
 * 
 * Custom hook for checking module-level feature status
 */

import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export interface ModuleStatus {
  enabled: boolean;
  sub_features: Record<string, boolean>;
}

export interface ModulesStatus {
  solar_calculator: ModuleStatus;
  heat_pump: ModuleStatus;
  price_matrix: ModuleStatus;
  pdf_generation: ModuleStatus;
  crm: ModuleStatus;
  '3d_visualization': ModuleStatus;
}

interface UseModuleFeaturesOptions {
  userId?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const useModuleFeatures = (options: UseModuleFeaturesOptions = {}) => {
  const [modules, setModules] = useState<ModulesStatus | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const { userId, autoRefresh = false, refreshInterval = 60000 } = options;

  const loadModuleStatus = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = userId ? { user_id: userId } : {};
      const response = await api.get('/api/v1/module-features/status', { params });

      setModules(response.data.modules);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load module status');
      console.error('Failed to load module status:', err);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    loadModuleStatus();

    if (autoRefresh) {
      const interval = setInterval(loadModuleStatus, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [loadModuleStatus, autoRefresh, refreshInterval]);

  const isModuleEnabled = useCallback(
    (moduleName: keyof ModulesStatus): boolean => {
      return modules?.[moduleName]?.enabled || false;
    },
    [modules]
  );

  const isSubFeatureEnabled = useCallback(
    (moduleName: keyof ModulesStatus, subFeatureKey: string): boolean => {
      return modules?.[moduleName]?.sub_features?.[subFeatureKey] || false;
    },
    [modules]
  );

  return {
    modules,
    isLoading,
    error,
    refresh: loadModuleStatus,
    isModuleEnabled,
    isSubFeatureEnabled,
  };
};

/**
 * Hook for checking a specific module
 */
export const useModule = (moduleKey: string, options: UseModuleFeaturesOptions = {}) => {
  const [isEnabled, setIsEnabled] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const { userId } = options;

  const checkModule = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = userId ? { user_id: userId } : {};
      const response = await api.get(`/api/v1/module-features/check-module/${moduleKey}`, {
        params,
      });

      setIsEnabled(response.data.enabled);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to check module');
      setIsEnabled(false);
    } finally {
      setIsLoading(false);
    }
  }, [moduleKey, userId]);

  useEffect(() => {
    checkModule();
  }, [checkModule]);

  return {
    isEnabled,
    isLoading,
    error,
    refresh: checkModule,
  };
};

/**
 * Hook for checking a specific sub-feature
 */
export const useSubFeature = (
  moduleKey: string,
  subFeatureKey: string,
  options: UseModuleFeaturesOptions = {}
) => {
  const [isEnabled, setIsEnabled] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const { userId } = options;

  const checkSubFeature = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = userId ? { user_id: userId } : {};
      const response = await api.get(
        `/api/v1/module-features/check-sub-feature/${moduleKey}/${subFeatureKey}`,
        { params }
      );

      setIsEnabled(response.data.enabled);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to check sub-feature');
      setIsEnabled(false);
    } finally {
      setIsLoading(false);
    }
  }, [moduleKey, subFeatureKey, userId]);

  useEffect(() => {
    checkSubFeature();
  }, [checkSubFeature]);

  return {
    isEnabled,
    isLoading,
    error,
    refresh: checkSubFeature,
  };
};

/**
 * Module feature keys constants
 */
export const MODULE_KEYS = {
  SOLAR_CALCULATOR: 'module.solar_calculator',
  HEAT_PUMP: 'module.heat_pump',
  PRICE_MATRIX: 'module.price_matrix',
  PDF_GENERATION: 'module.pdf_generation',
  CRM: 'module.crm',
  VISUALIZATION_3D: 'module.3d_visualization',
} as const;

export const SOLAR_SUB_FEATURES = {
  BASIC_CALC: 'module.solar_calculator.basic_calculation',
  ADVANCED_CALC: 'module.solar_calculator.advanced_calculation',
  SHADING_ANALYSIS: 'module.solar_calculator.shading_analysis',
  BATTERY_STORAGE: 'module.solar_calculator.battery_storage',
  FINANCIAL_ANALYSIS: 'module.solar_calculator.financial_analysis',
  WEATHER_INTEGRATION: 'module.solar_calculator.weather_integration',
  MONITORING: 'module.solar_calculator.monitoring',
} as const;

export const HEAT_PUMP_SUB_FEATURES = {
  BASIC_CALC: 'module.heat_pump.basic_calculation',
  ADVANCED_CALC: 'module.heat_pump.advanced_calculation',
  DYNAMIC_TARIFF: 'module.heat_pump.dynamic_tariff',
  PV_INTEGRATION: 'module.heat_pump.pv_integration',
  ENVIRONMENTAL: 'module.heat_pump.environmental_analysis',
} as const;

export const PRICE_MATRIX_SUB_FEATURES = {
  UPLOAD: 'module.price_matrix.upload',
  FORMULA_ENGINE: 'module.price_matrix.formula_engine',
  VALIDATION: 'module.price_matrix.validation',
  VERSIONING: 'module.price_matrix.versioning',
  EXTRAS: 'module.price_matrix.extras',
  MULTI_CURRENCY: 'module.price_matrix.multi_currency',
} as const;

export const PDF_SUB_FEATURES = {
  BASIC_GENERATION: 'module.pdf_generation.basic',
  ADVANCED_TEMPLATES: 'module.pdf_generation.advanced_templates',
  MULTI_LANGUAGE: 'module.pdf_generation.multi_language',
  CUSTOM_BRANDING: 'module.pdf_generation.custom_branding',
  BATCH_PROCESSING: 'module.pdf_generation.batch_processing',
  CHART_INTEGRATION: 'module.pdf_generation.chart_integration',
} as const;

export const CRM_SUB_FEATURES = {
  CUSTOMER_MANAGEMENT: 'module.crm.customer_management',
  OFFER_TRACKING: 'module.crm.offer_tracking',
  TASK_MANAGEMENT: 'module.crm.task_management',
  COMMUNICATION: 'module.crm.communication',
  LEAD_SCORING: 'module.crm.lead_scoring',
  FORECASTING: 'module.crm.forecasting',
  CONTRACT_MANAGEMENT: 'module.crm.contract_management',
} as const;

export const VIZ_3D_SUB_FEATURES = {
  BASIC: 'module.3d_visualization.basic',
  ADVANCED_RENDERING: 'module.3d_visualization.advanced_rendering',
  AUTO_PLACEMENT: 'module.3d_visualization.auto_placement',
  COLLISION_DETECTION: 'module.3d_visualization.collision_detection',
  ANIMATION: 'module.3d_visualization.animation',
  EXPORT: 'module.3d_visualization.export',
  MOUNTING_SYSTEM: 'module.3d_visualization.mounting_system',
} as const;
