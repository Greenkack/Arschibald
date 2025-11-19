/**
 * Form Container Component
 * 
 * Wrapper component for forms with consistent styling and behavior.
 * Includes auto-save indicator, submit button, and form actions.
 */

import React, { ReactNode } from 'react';
import { Button } from 'primereact/button';
import { ProgressSpinner } from 'primereact/progressspinner';
import { classNames } from 'primereact/utils';
import './FormContainer.css';

export interface FormContainerProps {
  children: ReactNode;
  onSubmit: (e: React.FormEvent) => void;
  title?: string;
  description?: string;
  submitLabel?: string;
  cancelLabel?: string;
  onCancel?: () => void;
  isSubmitting?: boolean;
  isAutoSaving?: boolean;
  lastSaved?: Date | null;
  disabled?: boolean;
  showSubmitButton?: boolean;
  showCancelButton?: boolean;
  className?: string;
  actions?: ReactNode;
}

export function FormContainer({
  children,
  onSubmit,
  title,
  description,
  submitLabel = 'Speichern',
  cancelLabel = 'Abbrechen',
  onCancel,
  isSubmitting = false,
  isAutoSaving = false,
  lastSaved = null,
  disabled = false,
  showSubmitButton = true,
  showCancelButton = false,
  className,
  actions,
}: FormContainerProps) {
  const formatLastSaved = (date: Date | null): string => {
    if (!date) return '';
    
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    
    if (diffSec < 60) {
      return 'Gerade eben gespeichert';
    } else if (diffMin < 60) {
      return `Vor ${diffMin} Minute${diffMin > 1 ? 'n' : ''} gespeichert`;
    } else if (diffHour < 24) {
      return `Vor ${diffHour} Stunde${diffHour > 1 ? 'n' : ''} gespeichert`;
    } else {
      return `Gespeichert am ${date.toLocaleDateString('de-DE')} um ${date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })}`;
    }
  };

  return (
    <div className={classNames('form-container', className)}>
      {(title || description) && (
        <div className="form-header">
          {title && <h2 className="form-title">{title}</h2>}
          {description && <p className="form-description">{description}</p>}
        </div>
      )}

      <form onSubmit={onSubmit} className="form-content">
        {children}

        <div className="form-footer">
          <div className="form-status">
            {isAutoSaving && (
              <div className="auto-save-indicator">
                <ProgressSpinner
                  style={{ width: '20px', height: '20px' }}
                  strokeWidth="4"
                />
                <span>Speichert...</span>
              </div>
            )}
            {!isAutoSaving && lastSaved && (
              <div className="last-saved">
                <i className="pi pi-check-circle" />
                <span>{formatLastSaved(lastSaved)}</span>
              </div>
            )}
          </div>

          <div className="form-actions">
            {actions}
            
            {showCancelButton && onCancel && (
              <Button
                type="button"
                label={cancelLabel}
                severity="secondary"
                outlined
                onClick={onCancel}
                disabled={disabled || isSubmitting}
              />
            )}
            
            {showSubmitButton && (
              <Button
                type="submit"
                label={submitLabel}
                loading={isSubmitting}
                disabled={disabled || isSubmitting}
                icon={isSubmitting ? undefined : 'pi pi-check'}
              />
            )}
          </div>
        </div>
      </form>
    </div>
  );
}
