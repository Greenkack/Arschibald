/**
 * Sidebar Component
 * 
 * Navigation sidebar with PrimeReact Menu
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Menu } from 'primereact/menu';
import { MenuItem } from 'primereact/menuitem';
import './Sidebar.css';

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems: MenuItem[] = [
    {
      label: 'Main',
      items: [
        {
          label: 'Dashboard',
          icon: 'pi pi-home',
          command: () => navigate('/dashboard'),
          className: location.pathname === '/dashboard' ? 'active-menu-item' : '',
        },
      ],
    },
    {
      label: 'Calculators',
      items: [
        {
          label: 'Solar Calculator',
          icon: 'pi pi-sun',
          command: () => navigate('/solar'),
          className: location.pathname === '/solar' ? 'active-menu-item' : '',
        },
        {
          label: 'Solar Projects',
          icon: 'pi pi-folder',
          command: () => navigate('/solar-projects'),
          className: location.pathname.startsWith('/solar-projects') ? 'active-menu-item' : '',
        },
        {
          label: 'Heat Pump',
          icon: 'pi pi-bolt',
          command: () => navigate('/heatpump'),
          className: location.pathname === '/heatpump' ? 'active-menu-item' : '',
        },
      ],
    },
    {
      label: 'Business',
      items: [
        {
          label: 'Price Matrix',
          icon: 'pi pi-table',
          command: () => navigate('/price-matrix'),
          className: location.pathname === '/price-matrix' ? 'active-menu-item' : '',
        },
        {
          label: 'Products',
          icon: 'pi pi-box',
          command: () => navigate('/products'),
          className: location.pathname === '/products' ? 'active-menu-item' : '',
        },
        {
          label: 'CRM',
          icon: 'pi pi-users',
          command: () => navigate('/crm'),
          className: location.pathname === '/crm' ? 'active-menu-item' : '',
        },
      ],
    },
    {
      label: 'Tools',
      items: [
        {
          label: 'PDF Generator',
          icon: 'pi pi-file-pdf',
          command: () => navigate('/pdf'),
          className: location.pathname === '/pdf' ? 'active-menu-item' : '',
        },
        {
          label: '3D Visualization',
          icon: 'pi pi-box',
          command: () => navigate('/3d-view'),
          className: location.pathname === '/3d-view' ? 'active-menu-item' : '',
        },
      ],
    },
    {
      separator: true,
    },
    {
      label: 'System',
      items: [
        {
          label: 'Admin Panel',
          icon: 'pi pi-cog',
          command: () => navigate('/admin'),
          className: location.pathname === '/admin' ? 'active-menu-item' : '',
        },
        {
          label: 'Settings',
          icon: 'pi pi-sliders-h',
          command: () => navigate('/settings'),
          className: location.pathname === '/settings' ? 'active-menu-item' : '',
        },
      ],
    },
  ];

  return (
    <div className="app-sidebar">
      <div className="sidebar-header">
        <h3>Navigation</h3>
      </div>
      <div className="sidebar-content">
        <Menu model={menuItems} className="sidebar-menu" />
      </div>
      <div className="sidebar-footer">
        <div className="version-info">
          <span className="version-label">Version</span>
          <span className="version-number">1.0.0</span>
        </div>
      </div>
    </div>
  );
};
