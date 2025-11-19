/**
 * Application Routes Configuration
 * 
 * This file defines all the routes for the application using React Router v6.
 */

import React, { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { ProgressSpinner } from 'primereact/progressspinner';

// Lazy load pages for code splitting
const Dashboard = lazy(() => import('@pages/Dashboard'));
const SolarCalculator = lazy(() => import('@pages/SolarCalculator'));
const SolarProjects = lazy(() => import('@pages/SolarProjects'));
const SolarProjectDetails = lazy(() => import('@pages/SolarProjectDetails'));
const Visualization3D = lazy(() => import('@pages/Visualization3D'));
const HeatPump = lazy(() => import('@pages/HeatPump'));
const PriceMatrix = lazy(() => import('@pages/PriceMatrix'));
const CRM = lazy(() => import('@pages/CRM'));
const Products = lazy(() => import('@pages/Products'));
const ProductManagement = lazy(() => import('@pages/ProductManagement'));
const Admin = lazy(() => import('@pages/Admin'));
const Settings = lazy(() => import('@pages/Settings'));
const Login = lazy(() => import('@pages/Login'));

// Layout components
const MainLayout = lazy(() => import('@components/layout/MainLayout'));
const AuthLayout = lazy(() => import('@components/layout/AuthLayout'));

/**
 * Loading component shown during lazy loading
 */
const LoadingFallback: React.FC = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh' 
  }}>
    <ProgressSpinner />
  </div>
);

/**
 * Wrapper component for lazy-loaded routes
 */
const LazyRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Suspense fallback={<LoadingFallback />}>
    {children}
  </Suspense>
);

/**
 * Application router configuration
 */
export const router = createBrowserRouter([
  {
    path: '/auth',
    element: (
      <LazyRoute>
        <AuthLayout />
      </LazyRoute>
    ),
    children: [
      {
        path: 'login',
        element: (
          <LazyRoute>
            <Login />
          </LazyRoute>
        ),
      },
    ],
  },
  {
    path: '/',
    element: (
      <LazyRoute>
        <MainLayout />
      </LazyRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: (
          <LazyRoute>
            <Dashboard />
          </LazyRoute>
        ),
      },
      {
        path: 'solar',
        element: (
          <LazyRoute>
            <SolarCalculator />
          </LazyRoute>
        ),
      },
      {
        path: 'solar-projects',
        element: (
          <LazyRoute>
            <SolarProjects />
          </LazyRoute>
        ),
      },
      {
        path: 'solar-projects/:projectId',
        element: (
          <LazyRoute>
            <SolarProjectDetails />
          </LazyRoute>
        ),
      },
      {
        path: '3d-visualization',
        element: (
          <LazyRoute>
            <Visualization3D />
          </LazyRoute>
        ),
      },
      {
        path: 'heatpump',
        element: (
          <LazyRoute>
            <HeatPump />
          </LazyRoute>
        ),
      },
      {
        path: 'pricing',
        element: (
          <LazyRoute>
            <PriceMatrix />
          </LazyRoute>
        ),
      },
      {
        path: 'crm',
        element: (
          <LazyRoute>
            <CRM />
          </LazyRoute>
        ),
      },
      {
        path: 'products',
        element: (
          <LazyRoute>
            <Products />
          </LazyRoute>
        ),
      },
      {
        path: 'products/manage',
        element: (
          <LazyRoute>
            <ProductManagement />
          </LazyRoute>
        ),
      },
      {
        path: 'admin',
        element: (
          <LazyRoute>
            <Admin />
          </LazyRoute>
        ),
      },
      {
        path: 'settings',
        element: (
          <LazyRoute>
            <Settings />
          </LazyRoute>
        ),
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
]);

/**
 * Router component to be used in the app
 */
export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};
