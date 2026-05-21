import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { useResponsive, useDeviceType } from '../hooks/useResponsive';
import {
  ResponsiveContainer,
  ResponsiveGrid,
  ResponsiveImage,
  MobileNavigation,
  TouchGestures,
  AdaptiveCard,
  ResponsiveTable,
} from '../components/responsive';
import '../styles/responsive.css';

/**
 * Responsive Design Demo
 * Demonstrates all responsive components and features
 */
export const ResponsiveDemo: React.FC = () => {
  const responsive = useResponsive();
  const deviceType = useDeviceType();
  const [swipeDirection, setSwipeDirection] = useState<string>('');
  const [pinchScale, setPinchScale] = useState<number>(1);

  const sampleData = [
    { id: 1, name: 'Product A', price: 99.99, stock: 50 },
    { id: 2, name: 'Product B', price: 149.99, stock: 30 },
    { id: 3, name: 'Product C', price: 199.99, stock: 20 },
  ];

  const tableColumns = [
    { field: 'id', header: 'ID', hideOnMobile: true },
    { field: 'name', header: 'Name' },
    { field: 'price', header: 'Price', body: (row: any) => `$${row.price}` },
    { field: 'stock', header: 'Stock', hideOnMobile: true },
  ];

  const mobileCardTemplate = (item: any) => (
    <div>
      <h3>{item.name}</h3>
      <p>Price: ${item.price}</p>
      <p>Stock: {item.stock}</p>
    </div>
  );

  const navItems = [
    { label: 'Dashboard', onClick: () => console.log('Dashboard'), active: true },
    { label: 'Projects', onClick: () => console.log('Projects') },
    { label: 'Settings', onClick: () => console.log('Settings') },
  ];

  return (
    <ResponsiveContainer>
      <div className="p-responsive">
        <h1>Responsive Design Demo</h1>

        {/* Device Information */}
        <AdaptiveCard title="Current Device Information">
          <div className="responsive-grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            <div>
              <strong>Device Type:</strong> {deviceType}
            </div>
            <div>
              <strong>Width:</strong> {responsive.width}px
            </div>
            <div>
              <strong>Height:</strong> {responsive.height}px
            </div>
            <div>
              <strong>Orientation:</strong> {responsive.orientation}
            </div>
            <div>
              <strong>Is Mobile:</strong> {responsive.isMobile ? 'Yes' : 'No'}
            </div>
            <div>
              <strong>Is Tablet:</strong> {responsive.isTablet ? 'Yes' : 'No'}
            </div>
          </div>
        </AdaptiveCard>

        {/* Breakpoints */}
        <AdaptiveCard title="Active Breakpoints">
          <div className="flex-responsive">
            {Object.entries(responsive).map(([key, value]) => {
              if (typeof value === 'boolean' && ['xs', 'sm', 'md', 'lg', 'xl', 'xxl'].includes(key)) {
                return (
                  <Button
                    key={key}
                    label={key.toUpperCase()}
                    severity={value ? 'success' : 'secondary'}
                    size="small"
                  />
                );
              }
              return null;
            })}
          </div>
        </AdaptiveCard>

        {/* Responsive Grid */}
        <AdaptiveCard title="Responsive Grid">
          <ResponsiveGrid cols={{ xs: 1, sm: 2, md: 3, lg: 4 }}>
            {[1, 2, 3, 4, 5, 6, 7, 8].map((num) => (
              <div
                key={num}
                style={{
                  padding: 'var(--spacing-md)',
                  backgroundColor: 'var(--primary-50)',
                  borderRadius: 'var(--border-radius)',
                  textAlign: 'center',
                }}
              >
                Item {num}
              </div>
            ))}
          </ResponsiveGrid>
        </AdaptiveCard>

        {/* Responsive Images */}
        <AdaptiveCard title="Responsive Images">
          <ResponsiveGrid cols={{ xs: 1, sm: 2, md: 3 }}>
            <ResponsiveImage
              src="https://via.placeholder.com/400x300"
              alt="Sample 1"
              fit="cover"
            />
            <ResponsiveImage
              src="https://via.placeholder.com/400x300"
              alt="Sample 2"
              fit="contain"
            />
            <ResponsiveImage
              src="https://via.placeholder.com/400x300"
              alt="Sample 3"
              fit="auto"
            />
          </ResponsiveGrid>
        </AdaptiveCard>

        {/* Mobile Navigation */}
        {responsive.isMobile && (
          <AdaptiveCard title="Mobile Navigation">
            <MobileNavigation items={navItems} />
            <p className="mt-3">Click the hamburger menu to see mobile navigation</p>
          </AdaptiveCard>
        )}

        {/* Touch Gestures */}
        <AdaptiveCard title="Touch Gestures (Mobile Only)">
          <TouchGestures
            onSwipeLeft={() => setSwipeDirection('Left')}
            onSwipeRight={() => setSwipeDirection('Right')}
            onSwipeUp={() => setSwipeDirection('Up')}
            onSwipeDown={() => setSwipeDirection('Down')}
            onPinch={(scale) => setPinchScale(scale)}
            onDoubleTap={() => alert('Double tap detected!')}
          >
            <div
              style={{
                padding: 'var(--spacing-xl)',
                backgroundColor: 'var(--surface-100)',
                borderRadius: 'var(--border-radius)',
                textAlign: 'center',
                minHeight: '200px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
              }}
            >
              <p>Swipe in any direction or pinch to zoom</p>
              {swipeDirection && <p>Last swipe: {swipeDirection}</p>}
              {pinchScale !== 1 && <p>Pinch scale: {pinchScale.toFixed(2)}</p>}
            </div>
          </TouchGestures>
        </AdaptiveCard>

        {/* Responsive Table */}
        <AdaptiveCard title="Responsive Table">
          <ResponsiveTable
            data={sampleData}
            columns={tableColumns}
            mobileCardTemplate={mobileCardTemplate}
            paginator
            rows={5}
          />
        </AdaptiveCard>

        {/* Responsive Form */}
        <AdaptiveCard title="Responsive Form">
          <form>
            <ResponsiveGrid cols={{ xs: 1, md: 2 }}>
              <div className="p-field">
                <label htmlFor="name">Name</label>
                <InputText id="name" className="w-full touch-target" />
              </div>
              <div className="p-field">
                <label htmlFor="email">Email</label>
                <InputText id="email" type="email" className="w-full touch-target" />
              </div>
              <div className="p-field">
                <label htmlFor="phone">Phone</label>
                <InputText id="phone" type="tel" className="w-full touch-target" />
              </div>
              <div className="p-field">
                <label htmlFor="company">Company</label>
                <InputText id="company" className="w-full touch-target" />
              </div>
            </ResponsiveGrid>
            <div className="flex-responsive" style={{ justifyContent: 'flex-end', marginTop: 'var(--spacing-md)' }}>
              <Button label="Cancel" severity="secondary" className="touch-target" />
              <Button label="Submit" className="touch-target" />
            </div>
          </form>
        </AdaptiveCard>

        {/* Visibility Classes */}
        <AdaptiveCard title="Visibility Classes">
          <div className="responsive-grid grid-cols-1">
            <div className="hide-mobile" style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--green-50)' }}>
              Hidden on mobile (visible on tablet and desktop)
            </div>
            <div className="show-mobile hide-tablet" style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--blue-50)' }}>
              Visible only on mobile
            </div>
            <div className="hide-desktop" style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--orange-50)' }}>
              Hidden on desktop (visible on mobile and tablet)
            </div>
            <div className="show-desktop" style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--purple-50)' }}>
              Visible only on desktop
            </div>
          </div>
        </AdaptiveCard>
      </div>
    </ResponsiveContainer>
  );
};
