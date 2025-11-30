/**
 * Application Routes Configuration
 * 
 * This file defines all the routes for the application using React Router v6.
 * Uses optimized lazy loading with retry logic and prefetching.
 */

import React, { Suspense } from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { lazyWithRetry, prefetchOnIdle } from '@utils/lazyLoad';

// Lazy load pages with retry logic for better reliability
const Dashboard = lazyWithRetry(() => import('@pages/Dashboard'));
const DashboardModern = lazyWithRetry(() => import('@pages/DashboardModern'));
const SolarCalculator = lazyWithRetry(() => import('@pages/SolarCalculator'));
const SolarCalculatorModern = lazyWithRetry(() => import('@pages/SolarCalculatorModern'));
const SolarProjects = lazyWithRetry(() => import('@pages/SolarProjects'));
const SolarProjectsModern = lazyWithRetry(() => import('@pages/SolarProjectsModern'));
const SolarProjectDetails = lazyWithRetry(() => import('@pages/SolarProjectDetails'));
const SolarProjectDetailsModern = lazyWithRetry(() => import('@pages/SolarProjectDetailsModern'));
const Visualization3D = lazyWithRetry(() => import('@pages/Visualization3D'));
const Visualization3DModern = lazyWithRetry(() => import('@pages/Visualization3DModern'));
const HeatPump = lazyWithRetry(() => import('@pages/HeatPump'));
const HeatPumpModern = lazyWithRetry(() => import('@pages/HeatPumpModern'));
const PriceMatrix = lazyWithRetry(() => import('@pages/PriceMatrix'));
const PriceMatrixModern = lazyWithRetry(() => import('@pages/PriceMatrixModern'));
const CRM = lazyWithRetry(() => import('@pages/CRM'));
const CRMModern = lazyWithRetry(() => import('@pages/CRMModern'));
const Products = lazyWithRetry(() => import('@pages/Products'));
const ProductManagement = lazyWithRetry(() => import('@pages/ProductManagement'));
const ProductManagementModern = lazyWithRetry(() => import('@pages/ProductManagementModern'));
const Admin = lazyWithRetry(() => import('@pages/Admin'));
const AdminModern = lazyWithRetry(() => import('@pages/AdminModern'));
const Settings = lazyWithRetry(() => import('@pages/Settings'));
const SettingsModern = lazyWithRetry(() => import('@pages/SettingsModern'));
const Login = lazyWithRetry(() => import('@pages/Login'));
const LoginModern = lazyWithRetry(() => import('@pages/LoginModern'));
const ProjectWizard = lazyWithRetry(() => import('@pages/ProjectWizard'));
const ProjectWizardModern = lazyWithRetry(() => import('@pages/ProjectWizardModern'));
const CombinedSystem = lazyWithRetry(() => import('@pages/CombinedSystem'));
const CombinedSystemModern = lazyWithRetry(() => import('@pages/CombinedSystemModern'));
const PDFGeneration = lazyWithRetry(() => import('@pages/PDFGeneration'));
const PDFGenerationModern = lazyWithRetry(() => import('@pages/PDFGenerationModern'));
const Migration = lazyWithRetry(() => import('@pages/Migration'));
const Profile = lazyWithRetry(() => import('@pages/Profile'));
const ProfileModern = lazyWithRetry(() => import('@pages/ProfileModern'));
const UserManagement = lazyWithRetry(() => import('@pages/UserManagement'));
const UserManagementModern = lazyWithRetry(() => import('@pages/UserManagementModern'));
const CommunicationHistory = lazyWithRetry(() => import('@pages/CommunicationHistory'));
const CommunicationHistoryModern = lazyWithRetry(() => import('@pages/CommunicationHistoryModern'));

// Layout components
const MainLayout = lazyWithRetry(() => import('@components/layout/MainLayout'));
const MainLayoutModern = lazyWithRetry(() => import('@components/layout/MainLayoutModern'));
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
  <div className="flex items-center justify-center h-screen">
    <Loader2 className="h-8 w-8 animate-spin text-primary" />
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
            <LoginModern />
          </LazyRoute>
        ),
      },
      {
        path: 'login-old',
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
        <MainLayoutModern />
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
            <DashboardModern />
          </LazyRoute>
        ),
      },
      {
        path: 'dashboard-old',
        element: (
          <LazyRoute>
            <Dashboard />
          </LazyRoute>
        ),
      },
      {
        path: 'layout-old',
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
        ],
      },
      {
        path: 'solar',
        element: (
          <LazyRoute>
            <SolarCalculatorModern />
          </LazyRoute>
        ),
      },
      {
        path: 'solar-old',
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
            <SolarProjectsModern />
          </LazyRoute>
        ),
      },
      {
        path: 'solar-projects-old',
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
            <SolarProjectDetailsModern />
          </LazyRoute>
        ),
      },
      {
        path: 'solar-projects-old/:projectId',
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
            <Visualization3DModern />
          </LazyRoute>
        ),
      },
      {
        path: '3d-visualization-old',
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
            <HeatPumpModern />
          </LazyRoute>
        ),
      },
      {
        path: 'heatpump-old',
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
            <PriceMatrixModern />
          </LazyRoute>
        ),
      },
      {
        path: 'pricing-old',
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
            <CRMModern />
          </LazyRoute>
        ),
      },
      {
        path: 'crm-old',
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
            <ProductManagementModern />
          </LazyRoute>
        ),
      },
      {
        path: 'products/manage-old',
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
            <AdminModern />
          </LazyRoute>
        ),
      },
      {
        path: 'admin-old',
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
            <SettingsModern />
          </LazyRoute>
        ),
      },
      {
        path: 'settings-old',
        element: (
          <LazyRoute>
            <Settings />
          </LazyRoute>
        ),
      },
      {
        path: 'project-wizard',
        element: (
          <LazyRoute>
            <ProjectWizardModern />
          </LazyRoute>
        ),
      },
      {
        path: 'project-wizard-old',
        element: (
          <LazyRoute>
            <ProjectWizard />
          </LazyRoute>
        ),
      },
      {
        path: 'solar-calculator',
        element: (
          <LazyRoute>
            <SolarCalculatorModern />
          </LazyRoute>
        ),
      },
      {
        path: 'heat-pump',
        element: (
          <LazyRoute>
            <HeatPumpModern />
          </LazyRoute>
        ),
      },
      {
        path: 'combined-system',
        element: (
          <LazyRoute>
            <CombinedSystemModern />
          </LazyRoute>
        ),
      },
      {
        path: 'combined-system-old',
        element: (
          <LazyRoute>
            <CombinedSystem />
          </LazyRoute>
        ),
      },
      {
        path: 'pdf-generation',
        element: (
          <LazyRoute>
            <PDFGenerationModern />
          </LazyRoute>
        ),
      },
      {
        path: 'pdf-generation-old',
        element: (
          <LazyRoute>
            <PDFGeneration />
          </LazyRoute>
        ),
      },
      {
        path: 'migration',
        element: (
          <LazyRoute>
            <Migration />
          </LazyRoute>
        ),
      },
      {
        path: 'profile',
        element: (
          <LazyRoute>
            <ProfileModern />
          </LazyRoute>
        ),
      },
      {
        path: 'profile-old',
        element: (
          <LazyRoute>
            <Profile />
          </LazyRoute>
        ),
      },
      {
        path: 'user-management',
        element: (
          <LazyRoute>
            <UserManagementModern />
          </LazyRoute>
        ),
      },
      {
        path: 'user-management-old',
        element: (
          <LazyRoute>
            <UserManagement />
          </LazyRoute>
        ),
      },
      {
        path: 'communication-history',
        element: (
          <LazyRoute>
            <CommunicationHistoryModern />
          </LazyRoute>
        ),
      },
      {
        path: 'communication-history-old',
        element: (
          <LazyRoute>
            <CommunicationHistory />
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
