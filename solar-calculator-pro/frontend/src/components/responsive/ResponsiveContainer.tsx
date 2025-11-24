import React from 'react';
import '../../styles/responsive.css';

interface ResponsiveContainerProps {
  children: React.ReactNode;
  className?: string;
  fluid?: boolean;
}

/**
 * Responsive container component
 * Provides consistent max-width and padding across breakpoints
 */
export const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  className = '',
  fluid = false,
}) => {
  const containerClass = fluid ? 'w-full' : 'responsive-container';
  
  return (
    <div className={`${containerClass} ${className}`}>
      {children}
    </div>
  );
};
