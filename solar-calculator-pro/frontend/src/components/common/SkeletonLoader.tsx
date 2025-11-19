import React from 'react';
import { Skeleton } from 'primereact/skeleton';
import './SkeletonLoader.css';

export interface SkeletonLoaderProps {
  type?: 'text' | 'rectangle' | 'circle';
  width?: string;
  height?: string;
  borderRadius?: string;
  className?: string;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  type = 'text',
  width = '100%',
  height,
  borderRadius,
  className = '',
}) => {
  const shapeMap = {
    text: undefined,
    rectangle: 'rectangle',
    circle: 'circle',
  };

  return (
    <Skeleton
      shape={shapeMap[type] as any}
      width={width}
      height={height}
      borderRadius={borderRadius}
      className={`skeleton-loader ${className}`}
    />
  );
};

// Card skeleton for loading cards
export const CardSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`card-skeleton ${className}`}>
      <Skeleton width="100%" height="150px" className="mb-3" />
      <Skeleton width="60%" height="1.5rem" className="mb-2" />
      <Skeleton width="100%" height="1rem" className="mb-2" />
      <Skeleton width="100%" height="1rem" className="mb-2" />
      <Skeleton width="80%" height="1rem" />
    </div>
  );
};

// Table skeleton for loading tables
export const TableSkeleton: React.FC<{ rows?: number; columns?: number; className?: string }> = ({
  rows = 5,
  columns = 4,
  className = '',
}) => {
  return (
    <div className={`table-skeleton ${className}`}>
      {/* Header */}
      <div className="table-skeleton-header">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={`header-${i}`} width="100%" height="2rem" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={`row-${rowIndex}`} className="table-skeleton-row">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={`cell-${rowIndex}-${colIndex}`} width="100%" height="1.5rem" />
          ))}
        </div>
      ))}
    </div>
  );
};

// Form skeleton for loading forms
export const FormSkeleton: React.FC<{ fields?: number; className?: string }> = ({
  fields = 4,
  className = '',
}) => {
  return (
    <div className={`form-skeleton ${className}`}>
      {Array.from({ length: fields }).map((_, i) => (
        <div key={`field-${i}`} className="form-skeleton-field">
          <Skeleton width="30%" height="1rem" className="mb-2" />
          <Skeleton width="100%" height="2.5rem" />
        </div>
      ))}
    </div>
  );
};

// List skeleton for loading lists
export const ListSkeleton: React.FC<{ items?: number; className?: string }> = ({
  items = 5,
  className = '',
}) => {
  return (
    <div className={`list-skeleton ${className}`}>
      {Array.from({ length: items }).map((_, i) => (
        <div key={`item-${i}`} className="list-skeleton-item">
          <Skeleton shape="circle" size="3rem" className="mr-3" />
          <div className="flex-1">
            <Skeleton width="60%" height="1rem" className="mb-2" />
            <Skeleton width="100%" height="0.875rem" />
          </div>
        </div>
      ))}
    </div>
  );
};
