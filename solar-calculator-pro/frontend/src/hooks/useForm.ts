/**
 * Custom Form Hook
 * 
 * Enhanced wrapper around React Hook Form with auto-save functionality,
 * error handling, and integration with our validation schemas.
 */

import { useForm as useReactHookForm, UseFormProps, UseFormReturn, FieldValues } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ZodSchema } from 'zod';
import { useEffect, useRef, useCallback } from 'react';
import { toast } from 'react-toastify';

export interface UseFormOptions<TFieldValues extends FieldValues> extends UseFormProps<TFieldValues> {
  schema?: ZodSchema;
  autoSave?: boolean;
  autoSaveInterval?: number; // in milliseconds
  onAutoSave?: (data: TFieldValues) => Promise<void> | void;
  onSubmitSuccess?: (data: TFieldValues) => void;
  onSubmitError?: (error: Error) => void;
  showSuccessToast?: boolean;
  showErrorToast?: boolean;
  successMessage?: string;
  errorMessage?: string;
}

export interface UseFormReturnExtended<TFieldValues extends FieldValues> extends UseFormReturn<TFieldValues> {
  isAutoSaving: boolean;
  lastSaved: Date | null;
  manualSave: () => Promise<void>;
}

/**
 * Enhanced form hook with validation, auto-save, and error handling
 */
export function useForm<TFieldValues extends FieldValues = FieldValues>(
  options: UseFormOptions<TFieldValues> = {}
): UseFormReturnExtended<TFieldValues> {
  const {
    schema,
    autoSave = false,
    autoSaveInterval = 5000,
    onAutoSave,
    onSubmitSuccess,
    onSubmitError,
    showSuccessToast = true,
    showErrorToast = true,
    successMessage = 'Erfolgreich gespeichert',
    errorMessage = 'Fehler beim Speichern',
    ...formOptions
  } = options;

  // Setup form with Zod resolver if schema provided
  const form = useReactHookForm<TFieldValues>({
    ...formOptions,
    resolver: schema ? zodResolver(schema) : formOptions.resolver,
  });

  const { watch, formState } = form;
  const { isDirty, isSubmitting } = formState;

  // Auto-save state
  const isAutoSavingRef = useRef(false);
  const lastSavedRef = useRef<Date | null>(null);
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const previousValuesRef = useRef<string>('');

  /**
   * Manual save function
   */
  const manualSave = useCallback(async () => {
    if (!onAutoSave || isAutoSavingRef.current) return;

    try {
      isAutoSavingRef.current = true;
      const values = form.getValues();
      await onAutoSave(values);
      lastSavedRef.current = new Date();
      
      if (showSuccessToast) {
        toast.success(successMessage, {
          position: 'bottom-right',
          autoClose: 2000,
        });
      }
    } catch (error) {
      console.error('Auto-save error:', error);
      if (showErrorToast) {
        toast.error(errorMessage, {
          position: 'bottom-right',
          autoClose: 3000,
        });
      }
    } finally {
      isAutoSavingRef.current = false;
    }
  }, [onAutoSave, form, showSuccessToast, showErrorToast, successMessage, errorMessage]);

  /**
   * Auto-save effect
   */
  useEffect(() => {
    if (!autoSave || !onAutoSave || !isDirty) return;

    // Watch for form changes
    const subscription = watch((values) => {
      const currentValues = JSON.stringify(values);
      
      // Only trigger auto-save if values actually changed
      if (currentValues === previousValuesRef.current) return;
      previousValuesRef.current = currentValues;

      // Clear existing timer
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }

      // Set new timer
      autoSaveTimerRef.current = setTimeout(() => {
        manualSave();
      }, autoSaveInterval);
    });

    return () => {
      subscription.unsubscribe();
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, [autoSave, onAutoSave, isDirty, watch, autoSaveInterval, manualSave]);

  /**
   * Enhanced submit handler with error handling
   */
  const handleSubmit = form.handleSubmit(
    async (data) => {
      try {
        if (onSubmitSuccess) {
          onSubmitSuccess(data);
        }
        
        if (showSuccessToast) {
          toast.success(successMessage, {
            position: 'bottom-right',
            autoClose: 3000,
          });
        }
      } catch (error) {
        console.error('Form submission error:', error);
        
        if (onSubmitError) {
          onSubmitError(error as Error);
        }
        
        if (showErrorToast) {
          toast.error(errorMessage, {
            position: 'bottom-right',
            autoClose: 3000,
          });
        }
      }
    },
    (errors) => {
      console.error('Form validation errors:', errors);
      
      // Show first error in toast
      const firstError = Object.values(errors)[0];
      if (firstError && showErrorToast) {
        toast.error(firstError.message || 'Validierungsfehler', {
          position: 'bottom-right',
          autoClose: 3000,
        });
      }
    }
  );

  return {
    ...form,
    handleSubmit,
    isAutoSaving: isAutoSavingRef.current,
    lastSaved: lastSavedRef.current,
    manualSave,
  };
}

/**
 * Hook for form field error messages
 */
export function useFormError(fieldName: string, errors: any): string | undefined {
  const error = errors[fieldName];
  return error?.message;
}

/**
 * Hook for checking if a field has an error
 */
export function useHasError(fieldName: string, errors: any): boolean {
  return !!errors[fieldName];
}
