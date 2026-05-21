import React, { useRef, useImperativeHandle, forwardRef } from 'react';
import { Toast, ToastMessage } from 'primereact/toast';
import './ToastNotification.css';

export interface ToastNotificationRef {
  show: (message: ToastMessage) => void;
  showSuccess: (summary: string, detail?: string) => void;
  showInfo: (summary: string, detail?: string) => void;
  showWarn: (summary: string, detail?: string) => void;
  showError: (summary: string, detail?: string) => void;
  clear: () => void;
}

export interface ToastNotificationProps {
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right' | 'center';
  autoZIndex?: boolean;
  baseZIndex?: number;
  className?: string;
}

export const ToastNotification = forwardRef<ToastNotificationRef, ToastNotificationProps>(
  ({ position = 'top-right', autoZIndex = true, baseZIndex = 0, className = '' }, ref) => {
    const toastRef = useRef<Toast>(null);

    useImperativeHandle(ref, () => ({
      show: (message: ToastMessage) => {
        toastRef.current?.show(message);
      },
      showSuccess: (summary: string, detail?: string) => {
        toastRef.current?.show({
          severity: 'success',
          summary,
          detail,
          life: 3000,
        });
      },
      showInfo: (summary: string, detail?: string) => {
        toastRef.current?.show({
          severity: 'info',
          summary,
          detail,
          life: 3000,
        });
      },
      showWarn: (summary: string, detail?: string) => {
        toastRef.current?.show({
          severity: 'warn',
          summary,
          detail,
          life: 4000,
        });
      },
      showError: (summary: string, detail?: string) => {
        toastRef.current?.show({
          severity: 'error',
          summary,
          detail,
          life: 5000,
        });
      },
      clear: () => {
        toastRef.current?.clear();
      },
    }));

    return (
      <Toast
        ref={toastRef}
        position={position}
        autoZIndex={autoZIndex}
        baseZIndex={baseZIndex}
        className={`custom-toast ${className}`}
      />
    );
  }
);

ToastNotification.displayName = 'ToastNotification';

// Hook for using toast notifications
export const useToast = () => {
  const toastRef = useRef<ToastNotificationRef>(null);

  return {
    toast: toastRef,
    showSuccess: (summary: string, detail?: string) => {
      toastRef.current?.showSuccess(summary, detail);
    },
    showInfo: (summary: string, detail?: string) => {
      toastRef.current?.showInfo(summary, detail);
    },
    showWarn: (summary: string, detail?: string) => {
      toastRef.current?.showWarn(summary, detail);
    },
    showError: (summary: string, detail?: string) => {
      toastRef.current?.showError(summary, detail);
    },
    show: (message: ToastMessage) => {
      toastRef.current?.show(message);
    },
    clear: () => {
      toastRef.current?.clear();
    },
  };
};
