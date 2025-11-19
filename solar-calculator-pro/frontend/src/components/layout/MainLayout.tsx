/**
 * Main Layout Component
 * 
 * Layout for authenticated pages with sidebar, header, and footer
 * Includes responsive mobile drawer navigation
 */

import React from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';
import { MobileDrawer } from './MobileDrawer';
import './MainLayout.css';

const MainLayout: React.FC = () => {
  return (
    <div className="main-layout">
      {/* Mobile Drawer - visible only on mobile */}
      <MobileDrawer />

      {/* Desktop Sidebar - visible only on desktop */}
      <div className="desktop-sidebar">
        <Sidebar />
      </div>

      {/* Main Content Area */}
      <div className="main-content-wrapper">
        <Header />

        <main className="main-content">
          <div className="content-container">
            <Outlet />
          </div>
        </main>

        <Footer />
      </div>
    </div>
  );
};

export default MainLayout;
