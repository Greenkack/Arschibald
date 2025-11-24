import React, { useState } from 'react';
import { useResponsive } from '../../hooks/useResponsive';
import '../../styles/responsive.css';

interface MobileNavigationProps {
  items: Array<{
    label: string;
    icon?: React.ReactNode;
    onClick: () => void;
    active?: boolean;
  }>;
  className?: string;
}

/**
 * Mobile navigation component
 * Provides touch-friendly navigation for mobile devices
 */
export const MobileNavigation: React.FC<MobileNavigationProps> = ({
  items,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const { isMobile } = useResponsive();

  if (!isMobile) {
    return null;
  }

  return (
    <>
      {/* Hamburger Menu Button */}
      <button
        className={`touch-target mobile-menu-button ${className}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle menu"
        aria-expanded={isOpen}
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          {isOpen ? (
            <>
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </>
          ) : (
            <>
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </>
          )}
        </svg>
      </button>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <>
          <div
            className="mobile-menu-overlay"
            onClick={() => setIsOpen(false)}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              zIndex: 999,
            }}
          />
          <nav
            className="mobile-menu"
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              bottom: 0,
              width: '80%',
              maxWidth: '300px',
              backgroundColor: 'var(--surface-0)',
              zIndex: 1000,
              overflowY: 'auto',
              boxShadow: '2px 0 8px rgba(0, 0, 0, 0.15)',
            }}
          >
            <div className="p-responsive">
              {items.map((item, index) => (
                <button
                  key={index}
                  className={`touch-target w-full text-left ${
                    item.active ? 'active' : ''
                  }`}
                  onClick={() => {
                    item.onClick();
                    setIsOpen(false);
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-md)',
                    padding: 'var(--spacing-md)',
                    border: 'none',
                    background: item.active ? 'var(--primary-50)' : 'transparent',
                    color: item.active ? 'var(--primary-color)' : 'inherit',
                    cursor: 'pointer',
                    borderRadius: 'var(--border-radius)',
                    marginBottom: 'var(--spacing-xs)',
                  }}
                >
                  {item.icon && <span>{item.icon}</span>}
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          </nav>
        </>
      )}
    </>
  );
};
