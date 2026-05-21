import React, { useRef, useImperativeHandle, forwardRef, useState } from 'react';
import { ConfirmDialog as PrimeConfirmDialog } from 'primereact/confirmdialog';
import { confirmDialog } from 'primereact/confirmdialog';
import { Button } from 'primereact/button';
import './ConfirmDialog.css';

export interface ConfirmDialogOptions {
  message: string;
  header?: string;
  icon?: string;
  acceptLabel?: string;
  rejectLabel?: string;
  acceptClassName?: string;
  rejectClassName?: string;
  acceptIcon?: string;
  rejectIcon?: string;
  onAccept?: () => void;
  onReject?: () => void;
  defaultFocus?: 'accept' | 'reject';
}

export interface ConfirmDialogRef {
  confirm: (options: ConfirmDialogOptions) => void;
  confirmDelete: (itemName: string, onConfirm: () => void) => void;
  confirmSave: (onConfirm: () => void, onReject?: () => void) => void;
  confirmDiscard: (onConfirm: () => void, onReject?: () => void) => void;
}

export const ConfirmDialog = forwardRef<ConfirmDialogRef, {}>((props, ref) => {
  useImperativeHandle(ref, () => ({
    confirm: (options: ConfirmDialogOptions) => {
      confirmDialog({
        message: options.message,
        header: options.header || 'Confirmation',
        icon: options.icon || 'pi pi-exclamation-triangle',
        acceptLabel: options.acceptLabel || 'Yes',
        rejectLabel: options.rejectLabel || 'No',
        acceptClassName: options.acceptClassName || 'p-button-success',
        rejectClassName: options.rejectClassName || 'p-button-secondary',
        acceptIcon: options.acceptIcon || 'pi pi-check',
        rejectIcon: options.rejectIcon || 'pi pi-times',
        accept: options.onAccept,
        reject: options.onReject,
        defaultFocus: options.defaultFocus || 'reject',
      });
    },
    confirmDelete: (itemName: string, onConfirm: () => void) => {
      confirmDialog({
        message: `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
        header: 'Delete Confirmation',
        icon: 'pi pi-trash',
        acceptLabel: 'Delete',
        rejectLabel: 'Cancel',
        acceptClassName: 'p-button-danger',
        rejectClassName: 'p-button-secondary',
        acceptIcon: 'pi pi-trash',
        rejectIcon: 'pi pi-times',
        accept: onConfirm,
        defaultFocus: 'reject',
      });
    },
    confirmSave: (onConfirm: () => void, onReject?: () => void) => {
      confirmDialog({
        message: 'Do you want to save your changes?',
        header: 'Save Changes',
        icon: 'pi pi-save',
        acceptLabel: 'Save',
        rejectLabel: 'Cancel',
        acceptClassName: 'p-button-success',
        rejectClassName: 'p-button-secondary',
        acceptIcon: 'pi pi-check',
        rejectIcon: 'pi pi-times',
        accept: onConfirm,
        reject: onReject,
        defaultFocus: 'accept',
      });
    },
    confirmDiscard: (onConfirm: () => void, onReject?: () => void) => {
      confirmDialog({
        message: 'You have unsaved changes. Do you want to discard them?',
        header: 'Unsaved Changes',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Discard',
        rejectLabel: 'Keep Editing',
        acceptClassName: 'p-button-danger',
        rejectClassName: 'p-button-secondary',
        acceptIcon: 'pi pi-trash',
        rejectIcon: 'pi pi-times',
        accept: onConfirm,
        reject: onReject,
        defaultFocus: 'reject',
      });
    },
  }));

  return <PrimeConfirmDialog className="custom-confirm-dialog" />;
});

ConfirmDialog.displayName = 'ConfirmDialog';

// Hook for using confirmation dialogs
export const useConfirmDialog = () => {
  const confirmRef = useRef<ConfirmDialogRef>(null);

  return {
    confirmDialog: confirmRef,
    confirm: (options: ConfirmDialogOptions) => {
      confirmRef.current?.confirm(options);
    },
    confirmDelete: (itemName: string, onConfirm: () => void) => {
      confirmRef.current?.confirmDelete(itemName, onConfirm);
    },
    confirmSave: (onConfirm: () => void, onReject?: () => void) => {
      confirmRef.current?.confirmSave(onConfirm, onReject);
    },
    confirmDiscard: (onConfirm: () => void, onReject?: () => void) => {
      confirmRef.current?.confirmDiscard(onConfirm, onReject);
    },
  };
};

// Standalone confirmation dialog component (alternative approach)
export interface StandaloneConfirmDialogProps {
  visible: boolean;
  onHide: () => void;
  message: string;
  header?: string;
  icon?: string;
  onConfirm: () => void;
  onCancel?: () => void;
  confirmLabel?: string;
  cancelLabel?: string;
  severity?: 'success' | 'info' | 'warning' | 'danger';
}

export const StandaloneConfirmDialog: React.FC<StandaloneConfirmDialogProps> = ({
  visible,
  onHide,
  message,
  header = 'Confirmation',
  icon = 'pi pi-exclamation-triangle',
  onConfirm,
  onCancel,
  confirmLabel = 'Yes',
  cancelLabel = 'No',
  severity = 'warning',
}) => {
  const handleConfirm = () => {
    onConfirm();
    onHide();
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
    onHide();
  };

  const severityMap = {
    success: 'p-button-success',
    info: 'p-button-info',
    warning: 'p-button-warning',
    danger: 'p-button-danger',
  };

  return (
    <PrimeConfirmDialog
      visible={visible}
      onHide={onHide}
      message={message}
      header={header}
      icon={icon}
      accept={handleConfirm}
      reject={handleCancel}
      acceptLabel={confirmLabel}
      rejectLabel={cancelLabel}
      acceptClassName={severityMap[severity]}
      rejectClassName="p-button-secondary"
      className="custom-confirm-dialog"
    />
  );
};
