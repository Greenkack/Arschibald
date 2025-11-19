/**
 * Mobile Drawer Component
 * 
 * Mobile-responsive drawer navigation using PrimeReact Sidebar
 */

import React from 'react';
import { Sidebar as PrimeSidebar } from 'primereact/sidebar';
import { useUIStore } from '@/store/uiStore';
import { Sidebar } from './Sidebar';
import './MobileDrawer.css';

export const MobileDrawer: React.FC = () => {
  const { sidebarVisible, setSidebarVisible } = useUIStore();

  return (
    <PrimeSidebar
      visible={sidebarVisible}
      onHide={() => setSidebarVisible(false)}
      position="left"
      className="mobile-drawer"
      showCloseIcon={true}
      modal={true}
      dismissable={true}
    >
      <Sidebar />
    </PrimeSidebar>
  );
};
