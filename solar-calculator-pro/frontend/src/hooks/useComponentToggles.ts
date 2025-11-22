/**
 * Component Toggles Hook
 * 
 * React hook for managing component-level feature toggles including:
 * - Chart visibility
 * - Form field toggles
 * - Calculation options
 * - Export formats
 * - UI themes
 * - Languages
 */

import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export interface ComponentToggle {
  id: number;
  category: string;
  component_key: string;
  component_name: string;
  enabled: boolean;
  toggle_type: string;
  user_id?: number;
  metadata: Record<string, any>;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export interface UseComponentTogglesReturn {
  // Chart toggles
  visibleCharts: string[];
  toggleChart: (chartType: string, enabled: boolean) => Promise<void>;
  isChartVisible: (chartType: string) => boolean;
  
  // Form field toggles
  getEnabledFormFields: (formName: string) => Promise<string[]>;
  toggleFormField: (formName: string, fieldKey: string, enabled: boolean) => Promise<void>;
  isFormFieldEnabled: (formName: string, fieldKey: string) => boolean;
  
  // Calculation option toggles
  getEnabledCalculationOptions: (calculatorType: string) => Promise<string[]>;
  toggleCalculationOption: (calculatorType: string, optionKey: string, enabled: boolean) => Promise<void>;
  isCalculationOptionEnabled: (calculatorType: string, optionKey: string) => boolean;
  
  // Export format toggles
  availableExportFormats: string[];
  toggleExportFormat: (formatKey: string, enabled: boolean) => Promise<void>;
  isExportFormatAvailable: (formatKey: string) => boolean;
  
  // Theme toggles
  availableThemes: string[];
  toggleTheme: (themeKey: string, enabled: boolean) => Promise<void>;
  isThemeAvailable: (themeKey: string) => boolean;
  
  // Language toggles
  availableLanguages: string[];
  toggleLanguage: (languageCode: string, enabled: boolean) => Promise<void>;
  isLanguageAvailable: (languageCode: string) => boolean;
  
  // Bulk operations
  bulkToggle: (category: string, enabled: boolean) => Promise<void>;
  resetToDefaults: () => Promise<void>;
  
  // State
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export const useComponentToggles = (): UseComponentTogglesReturn => {
  const [visibleCharts, setVisibleCharts] = useState<string[]>([]);
  const [availableExportFormats, setAvailableExportFormats] = useState<string[]>([]);
  const [availableThemes, setAvailableThemes] = useState<string[]>([]);
  const [availableLanguages, setAvailableLanguages] = useState<string[]>([]);
  const [formFieldsCache, setFormFieldsCache] = useState<Record<string, string[]>>({});
  const [calculationOptionsCache, setCalculationOptionsCache] = useState<Record<string, string[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch all toggle data
  const fetchToggles = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch visible charts
      const chartsResponse = await api.get('/api/v1/component-toggles/charts/visible');
      setVisibleCharts(chartsResponse.data.charts);
      
      // Fetch available export formats
      const formatsResponse = await api.get('/api/v1/component-toggles/export-formats/available');
      setAvailableExportFormats(formatsResponse.data.formats);
      
      // Fetch available themes
      const themesResponse = await api.get('/api/v1/component-toggles/themes/available');
      setAvailableThemes(themesResponse.data.themes);
      
      // Fetch available languages
      const languagesResponse = await api.get('/api/v1/component-toggles/languages/available');
      setAvailableLanguages(languagesResponse.data.languages);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch component toggles');
      console.error('Error fetching component toggles:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchToggles();
  }, [fetchToggles]);

  // Chart toggles
  const toggleChart = async (chartType: string, enabled: boolean) => {
    try {
      await api.post('/api/v1/component-toggles/charts/toggle', {
        chart_type: chartType,
        enabled
      });
      
      // Update local state
      if (enabled) {
        setVisibleCharts(prev => [...prev, chartType]);
      } else {
        setVisibleCharts(prev => prev.filter(c => c !== chartType));
      }
    } catch (err: any) {
      setError(err.message || 'Failed to toggle chart');
      throw err;
    }
  };

  const isChartVisible = (chartType: string): boolean => {
    return visibleCharts.includes(chartType);
  };

  // Form field toggles
  const getEnabledFormFields = async (formName: string): Promise<string[]> => {
    if (formFieldsCache[formName]) {
      return formFieldsCache[formName];
    }
    
    try {
      const response = await api.get(`/api/v1/component-toggles/form-fields/enabled/${formName}`);
      const fields = response.data.fields;
      setFormFieldsCache(prev => ({ ...prev, [formName]: fields }));
      return fields;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch form fields');
      throw err;
    }
  };

  const toggleFormField = async (formName: string, fieldKey: string, enabled: boolean) => {
    try {
      await api.post('/api/v1/component-toggles/form-fields/toggle', {
        form_name: formName,
        field_key: fieldKey,
        enabled
      });
      
      // Update cache
      const currentFields = formFieldsCache[formName] || [];
      if (enabled) {
        setFormFieldsCache(prev => ({
          ...prev,
          [formName]: [...currentFields, fieldKey]
        }));
      } else {
        setFormFieldsCache(prev => ({
          ...prev,
          [formName]: currentFields.filter(f => f !== fieldKey)
        }));
      }
    } catch (err: any) {
      setError(err.message || 'Failed to toggle form field');
      throw err;
    }
  };

  const isFormFieldEnabled = (formName: string, fieldKey: string): boolean => {
    const fields = formFieldsCache[formName] || [];
    return fields.includes(fieldKey);
  };

  // Calculation option toggles
  const getEnabledCalculationOptions = async (calculatorType: string): Promise<string[]> => {
    if (calculationOptionsCache[calculatorType]) {
      return calculationOptionsCache[calculatorType];
    }
    
    try {
      const response = await api.get(
        `/api/v1/component-toggles/calculation-options/enabled/${calculatorType}`
      );
      const options = response.data.options;
      setCalculationOptionsCache(prev => ({ ...prev, [calculatorType]: options }));
      return options;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch calculation options');
      throw err;
    }
  };

  const toggleCalculationOption = async (
    calculatorType: string,
    optionKey: string,
    enabled: boolean
  ) => {
    try {
      await api.post('/api/v1/component-toggles/calculation-options/toggle', {
        calculator_type: calculatorType,
        option_key: optionKey,
        enabled
      });
      
      // Update cache
      const currentOptions = calculationOptionsCache[calculatorType] || [];
      if (enabled) {
        setCalculationOptionsCache(prev => ({
          ...prev,
          [calculatorType]: [...currentOptions, optionKey]
        }));
      } else {
        setCalculationOptionsCache(prev => ({
          ...prev,
          [calculatorType]: currentOptions.filter(o => o !== optionKey)
        }));
      }
    } catch (err: any) {
      setError(err.message || 'Failed to toggle calculation option');
      throw err;
    }
  };

  const isCalculationOptionEnabled = (calculatorType: string, optionKey: string): boolean => {
    const options = calculationOptionsCache[calculatorType] || [];
    return options.includes(optionKey);
  };

  // Export format toggles
  const toggleExportFormat = async (formatKey: string, enabled: boolean) => {
    try {
      await api.post('/api/v1/component-toggles/export-formats/toggle', {
        format_key: formatKey,
        enabled
      });
      
      // Update local state
      if (enabled) {
        setAvailableExportFormats(prev => [...prev, formatKey]);
      } else {
        setAvailableExportFormats(prev => prev.filter(f => f !== formatKey));
      }
    } catch (err: any) {
      setError(err.message || 'Failed to toggle export format');
      throw err;
    }
  };

  const isExportFormatAvailable = (formatKey: string): boolean => {
    return availableExportFormats.includes(formatKey);
  };

  // Theme toggles
  const toggleTheme = async (themeKey: string, enabled: boolean) => {
    try {
      await api.post('/api/v1/component-toggles/themes/toggle', {
        theme_key: themeKey,
        enabled
      });
      
      // Update local state
      if (enabled) {
        setAvailableThemes(prev => [...prev, themeKey]);
      } else {
        setAvailableThemes(prev => prev.filter(t => t !== themeKey));
      }
    } catch (err: any) {
      setError(err.message || 'Failed to toggle theme');
      throw err;
    }
  };

  const isThemeAvailable = (themeKey: string): boolean => {
    return availableThemes.includes(themeKey);
  };

  // Language toggles
  const toggleLanguage = async (languageCode: string, enabled: boolean) => {
    try {
      await api.post('/api/v1/component-toggles/languages/toggle', {
        language_code: languageCode,
        enabled
      });
      
      // Update local state
      if (enabled) {
        setAvailableLanguages(prev => [...prev, languageCode]);
      } else {
        setAvailableLanguages(prev => prev.filter(l => l !== languageCode));
      }
    } catch (err: any) {
      setError(err.message || 'Failed to toggle language');
      throw err;
    }
  };

  const isLanguageAvailable = (languageCode: string): boolean => {
    return availableLanguages.includes(languageCode);
  };

  // Bulk operations
  const bulkToggle = async (category: string, enabled: boolean) => {
    try {
      await api.post('/api/v1/component-toggles/bulk-toggle', {
        category,
        enabled
      });
      
      // Refresh all data
      await fetchToggles();
    } catch (err: any) {
      setError(err.message || 'Failed to bulk toggle');
      throw err;
    }
  };

  const resetToDefaults = async () => {
    try {
      await api.post('/api/v1/component-toggles/reset');
      
      // Refresh all data
      await fetchToggles();
    } catch (err: any) {
      setError(err.message || 'Failed to reset to defaults');
      throw err;
    }
  };

  return {
    // Chart toggles
    visibleCharts,
    toggleChart,
    isChartVisible,
    
    // Form field toggles
    getEnabledFormFields,
    toggleFormField,
    isFormFieldEnabled,
    
    // Calculation option toggles
    getEnabledCalculationOptions,
    toggleCalculationOption,
    isCalculationOptionEnabled,
    
    // Export format toggles
    availableExportFormats,
    toggleExportFormat,
    isExportFormatAvailable,
    
    // Theme toggles
    availableThemes,
    toggleTheme,
    isThemeAvailable,
    
    // Language toggles
    availableLanguages,
    toggleLanguage,
    isLanguageAvailable,
    
    // Bulk operations
    bulkToggle,
    resetToDefaults,
    
    // State
    loading,
    error,
    refresh: fetchToggles
  };
};
