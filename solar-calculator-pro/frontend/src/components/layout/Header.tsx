/**
 * Header Component
 * 
 * Responsive header with user menu, notifications, and mobile menu toggle
 */

import React, { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from 'primereact/button';
import { Menu } from 'primereact/menu';
import { Badge } from 'primereact/badge';
import { Avatar } from 'primereact/avatar';
import { useAuthStore } from '@/store/authStore';
import { useUIStore } from '@/store/uiStore';
import './Header.css';

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { sidebarVisible, setSidebarVisible } = useUIStore();
  const userMenuRef = useRef<Menu>(null);

  const userMenuItems = [
    {
      label: 'Profile',
      icon: 'pi pi-user',
      command: () => navigate('/settings/profile'),
    },
    {
      label: 'Settings',
      icon: 'pi pi-cog',
      command: () => navigate('/settings'),
    },
    {
      separator: true,
    },
    {
      label: 'Logout',
      icon: 'pi pi-sign-out',
      command: () => {
        logout();
        navigate('/login');
      },
    },
  ];

  return (
    <header className="app-header">
      <div className="header-left">
        <Button
          icon="pi pi-bars"
          className="p-button-text p-button-rounded menu-toggle"
          onClick={() => setSidebarVisible(!sidebarVisible)}
          aria-label="Toggle Menu"
        />
        <div className="app-logo">
          <i className="pi pi-sun" style={{ fontSize: '1.5rem', color: 'var(--primary-color)' }} />
          <span className="app-title">Solar Calculator Pro</span>
        </div>
      </div>

      <div className="header-center">
        <div className="search-bar">
          <span className="p-input-icon-left">
            <i className="pi pi-search" />
            <input
              type="text"
              placeholder="Search projects, customers..."
              className="p-inputtext p-component"
            />
          </span>
        </div>
      </div>

      <div className="header-right">
        <Button
          icon="pi pi-bell"
          className="p-button-text p-button-rounded"
          aria-label="Notifications"
        >
          <Badge value="3" severity="danger" />
        </Button>

        <Button
          icon="pi pi-question-circle"
          className="p-button-text p-button-rounded"
          aria-label="Help"
          onClick={() => navigate('/help')}
        />

        <div className="user-menu">
          <Button
            className="p-button-text user-menu-button"
            onClick={(e) => userMenuRef.current?.toggle(e)}
            aria-label="User Menu"
          >
            <Avatar
              label={user?.username?.charAt(0).toUpperCase() || 'U'}
              shape="circle"
              style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}
            />
            <span className="user-name">{user?.username || 'User'}</span>
            <i className="pi pi-angle-down" />
          </Button>
          <Menu model={userMenuItems} popup ref={userMenuRef} />
        </div>
      </div>
    </header>
  );
};
