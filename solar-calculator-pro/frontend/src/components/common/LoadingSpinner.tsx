import React from 'react';
import { ProgressSpinner } from 'primereact/progressspinner';
import './LoadingSpinner.css';

export interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  fullScreen?: boolean;
  message?: string;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  fullScreen = false,
  message,
  className = '',
}) => {
  const sizeMap = {
    small: '30px',
    medium: '50px',
    large: '80px',
  };

  const strokeWidthMap = {
    small: '6',
    medium: '4',
    large: '3',
  };

  const spinner = (
    <div className={`loading-spinner-content ${className}`}>
      <ProgressSpinner
        style={{ width: sizeMap[size], height: sizeMap[size] }}
        strokeWidth={strokeWidthMap[size]}
        animationDuration=".5s"
      />
      {message && <p className="loading-message">{message}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="loading-spinner-overlay">
        {spinner}
      </div>
    );
  }

  return spinner;
};

// Inline loading spinner for buttons
export interface InlineSpinnerProps {
  size?: number;
  className?: string;
}

export const InlineSpinner: React.FC<InlineSpinnerProps> = ({
  size = 16,
  className = '',
}) => {
  return (
    <i
      className={`pi pi-spin pi-spinner ${className}`}
      style={{ fontSize: `${size}px` }}
    />
  );
};
