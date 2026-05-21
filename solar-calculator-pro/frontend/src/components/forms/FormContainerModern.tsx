/**
 * Form Container Component - Modern (shadcn/ui)
 * 
 * Wrapper component for forms with consistent styling and behavior.
 * Includes auto-save indicator, submit button, and form actions.
 * Migrated from PrimeReact to shadcn/ui.
 */

import React, { ReactNode } from 'react';
import { Button } from '../ui/button';
import { Loader2, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface FormContainerModernProps {
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

export function FormContainerModern({
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
}: FormContainerModernProps) {
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
    <div className={cn('space-y-6', className)}>
      {(title || description) && (
        <div className="space-y-1">
          {title && <h2 className="text-2xl font-bold tracking-tight">{title}</h2>}
          {description && <p className="text-muted-foreground">{description}</p>}
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-6">
        {children}

        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center gap-2">
            {isAutoSaving && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Speichert...</span>
              </div>
            )}
            {!isAutoSaving && lastSaved && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span>{formatLastSaved(lastSaved)}</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {actions}
            
            {showCancelButton && onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={disabled || isSubmitting}
              >
                {cancelLabel}
              </Button>
            )}
            
            {showSubmitButton && (
              <Button
                type="submit"
                disabled={disabled || isSubmitting}
              >
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {submitLabel}
              </Button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}
