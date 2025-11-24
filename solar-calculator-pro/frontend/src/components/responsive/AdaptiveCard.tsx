import React from 'react';
import { Card } from 'primereact/card';
import { useResponsive } from '../../hooks/useResponsive';
import '../../styles/responsive.css';

interface AdaptiveCardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  mobileLayout?: 'stack' | 'compact';
}

/**
 * Adaptive card component
 * Adjusts layout and spacing based on screen size
 */
export const AdaptiveCard: React.FC<AdaptiveCardProps> = ({
  title,
  subtitle,
  children,
  className = '',
  header,
  footer,
  mobileLayout = 'stack',
}) => {
  const { isMobile, isTablet } = useResponsive();

  const cardStyle: React.CSSProperties = {
    padding: isMobile ? 'var(--spacing-sm)' : isTablet ? 'var(--spacing-md)' : 'var(--spacing-lg)',
    marginBottom: 'var(--spacing-md)',
  };

  const titleStyle: React.CSSProperties = {
    fontSize: isMobile ? 'var(--font-size-lg)' : 'var(--font-size-xl)',
    marginBottom: 'var(--spacing-sm)',
  };

  const contentClass = isMobile && mobileLayout === 'stack' ? 'flex-col-mobile' : '';

  return (
    <Card
      title={title}
      subTitle={subtitle}
      header={header}
      footer={footer}
      className={`${className} ${contentClass}`}
      style={cardStyle}
      pt={{
        title: { style: titleStyle },
        content: { className: 'p-responsive' },
      }}
    >
      {children}
    </Card>
  );
};
