import React from 'react';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import './Modal.css';

export interface ModalProps {
  visible: boolean;
  onHide: () => void;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  width?: string;
  height?: string;
  modal?: boolean;
  closable?: boolean;
  dismissableMask?: boolean;
  maximizable?: boolean;
  className?: string;
  headerClassName?: string;
  contentClassName?: string;
  footerClassName?: string;
}

export const Modal: React.FC<ModalProps> = ({
  visible,
  onHide,
  title,
  children,
  footer,
  width = '50vw',
  height,
  modal = true,
  closable = true,
  dismissableMask = false,
  maximizable = false,
  className = '',
  headerClassName = '',
  contentClassName = '',
  footerClassName = '',
}) => {
  return (
    <Dialog
      visible={visible}
      onHide={onHide}
      header={title}
      footer={footer}
      style={{ width, height }}
      modal={modal}
      closable={closable}
      dismissableMask={dismissableMask}
      maximizable={maximizable}
      className={`custom-modal ${className}`}
      headerClassName={headerClassName}
      contentClassName={contentClassName}
      footerClassName={footerClassName}
      draggable={false}
      resizable={false}
    >
      {children}
    </Dialog>
  );
};

// Convenience component for simple modals with OK/Cancel buttons
export interface SimpleModalProps extends Omit<ModalProps, 'footer'> {
  onConfirm?: () => void;
  onCancel?: () => void;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmIcon?: string;
  cancelIcon?: string;
  confirmDisabled?: boolean;
  showCancel?: boolean;
  showConfirm?: boolean;
  confirmSeverity?: 'success' | 'info' | 'warning' | 'danger' | 'help' | 'secondary';
}

export const SimpleModal: React.FC<SimpleModalProps> = ({
  onConfirm,
  onCancel,
  confirmLabel = 'OK',
  cancelLabel = 'Cancel',
  confirmIcon = 'pi pi-check',
  cancelIcon = 'pi pi-times',
  confirmDisabled = false,
  showCancel = true,
  showConfirm = true,
  confirmSeverity = 'success',
  ...modalProps
}) => {
  const footer = (
    <div className="flex justify-content-end gap-2">
      {showCancel && (
        <Button
          label={cancelLabel}
          icon={cancelIcon}
          onClick={onCancel || modalProps.onHide}
          severity="secondary"
          outlined
        />
      )}
      {showConfirm && (
        <Button
          label={confirmLabel}
          icon={confirmIcon}
          onClick={onConfirm}
          severity={confirmSeverity}
          disabled={confirmDisabled}
        />
      )}
    </div>
  );

  return <Modal {...modalProps} footer={footer} />;
};
