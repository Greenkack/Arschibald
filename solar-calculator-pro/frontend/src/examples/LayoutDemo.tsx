/**
 * Layout Components Demo
 * 
 * Demonstrates the usage of layout components
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout, AuthLayout } from '@/components/layout';

// Example pages
const DashboardPage = () => (
  <div>
    <h1>Dashboard</h1>
    <p>This is the dashboard page with the main layout.</p>
  </div>
);

const SolarPage = () => (
  <div>
    <h1>Solar Calculator</h1>
    <p>This is the solar calculator page.</p>
  </div>
);

const LoginPage = () => (
  <div>
    <h1>Login</h1>
    <p>This is the login page with auth layout.</p>
  </div>
);

/**
 * Layout Demo Application
 * 
 * Shows how to structure routes with different layouts
 */
export const LayoutDemo: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth routes - use AuthLayout */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>

        {/* Authenticated routes - use MainLayout */}
        <Route element={<MainLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/solar" element={<SolarPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

/**
 * Usage Examples
 */

// Example 1: Basic Layout Usage
export const Example1_BasicUsage = () => {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
      </Route>
    </Routes>
  );
};

// Example 2: Controlling Sidebar
export const Example2_SidebarControl = () => {
  const { sidebarVisible, setSidebarVisible } = useUIStore();

  return (
    <div>
      <button onClick={() => setSidebarVisible(!sidebarVisible)}>
        Toggle Sidebar
      </button>
      <p>Sidebar is {sidebarVisible ? 'visible' : 'hidden'}</p>
    </div>
  );
};

// Example 3: User Menu Integration
export const Example3_UserMenu = () => {
  const { user, logout } = useAuthStore();

  return (
    <div>
      <p>Logged in as: {user?.username}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

// Example 4: Custom Page with Layout
export const Example4_CustomPage = () => {
  return (
    <div className="custom-page">
      <div className="page-header">
        <h1>Custom Page</h1>
        <p>This page uses the main layout automatically</p>
      </div>

      <div className="page-content">
        <div className="card">
          <h2>Content Section</h2>
          <p>Your content here...</p>
        </div>
      </div>
    </div>
  );
};

// Example 5: Responsive Layout Testing
export const Example5_ResponsiveTest = () => {
  const [windowWidth, setWindowWidth] = React.useState(window.innerWidth);

  React.useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const getLayoutMode = () => {
    if (windowWidth > 992) return 'Desktop (Static Sidebar)';
    if (windowWidth > 768) return 'Tablet (Drawer)';
    return 'Mobile (Compact Drawer)';
  };

  return (
    <div>
      <h2>Responsive Layout Test</h2>
      <p>Window Width: {windowWidth}px</p>
      <p>Layout Mode: {getLayoutMode()}</p>
      <p>Resize the window to see layout changes</p>
    </div>
  );
};

// Import statements for examples
import { useUIStore } from '@/store/uiStore';
import { useAuthStore } from '@/store/authStore';

export default LayoutDemo;
