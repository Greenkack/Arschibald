/**
 * Application Routes Configuration
 * 
 * This file defines all the routes for the application using React Router v6.
 * Uses optimized lazy loading with retry logic and prefetching.
 */

import React, { Suspense } from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { ProgressSpinner } from 'primereact/progressspinner';
import { lazyWithRetry, prefetchOnIdle } from '@utils/lazyLoad';

// Lazy load pages with retry logic for better reliability
const Dashboard = lazyWithRetry(() => import('@pages/Dashboard'));
const SolarCalculator = lazyWithRetry(() => import('@pages/SolarCalculator'));
const SolarProjects = lazyWithRetry(() => import('@pages/SolarProjects'));
const SolarProjectDetails = lazyWithRetry(() => import('@pages/SolarProjectDetails'));
const Visualization3D = lazyWithRetry(() => import('@pages/Visualization3D'));
const HeatPump = lazyWithRetry(() => import('@pages/HeatPump'));
const PriceMatrix = lazyWithRetry(() => import('@pages/PriceMatrix'));
const CRM = lazyWithRetry(() => import('@pages/CRM'));
const Products = lazyWithRetry(() => import('@pages/Products'));
const ProductManagement = lazyWithRetry(() => import('@pages/ProductManagement'));
const Admin = lazyWithRetry(() => import('@pages/Admin'));
const Settings = lazyWithRetry(() => import('@pages/Settings'));
const Login = lazyWithRetry(() => import('@pages/Login'));

// Layout components
const MainLayout = lazyWithRetry(() => import('@components/layout/MainLayout'));
const AuthLayout = lazyWithRetry(() => import('@components/layout/AuthLayout'));

// Prefetch commonly used pages on idle
if (typeof window !== 'undefined') {
  prefetchOnIdle([
    () => import('@pages/Dashboard'),
    () => import('@pages/SolarCalculator'),
    () => import('@pages/Settings'),
  ]);
}

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
