/**
 * Toast Hook for shadcn/ui (using sonner)
 * 
 * Provides a React hook interface for showing toast notifications
 * Compatible with the existing useToast() pattern
 */

import { toast as sonnerToast } from 'sonner';

export interface ToastProps {
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive';
  duration?: number;
}

export function useToast() {
  const toast = ({ title, description, variant, duration = 3000 }: ToastProps) => {
    const message = title || '';
    const desc = description || '';
    
    if (variant === 'destructive') {
      sonnerToast.error(message, {
        description: desc,
        duration,
      });
    } else {
      sonnerToast.success(message, {
        description: desc,
        duration,
      });
    }
  };

  return { toast };
}

// Export sonner toast directly for advanced usage
export { toast as sonnerToast } from 'sonner';
