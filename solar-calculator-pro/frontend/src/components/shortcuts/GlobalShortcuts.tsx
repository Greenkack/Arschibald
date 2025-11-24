/**
 * Global Shortcuts Component
 * 
 * Defines and registers global keyboard shortcuts for the application
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useKeyboardShortcuts, ShortcutConfig } from '../../hooks/useKeyboardShortcuts';
import { useShortcutStore } from '../../store/shortcutStore';

export const GlobalShortcuts: React.FC = () => {
  const navigate = useNavigate();
  const { setEnabled } = useShortcutStore();

  // Define global shortcuts
  const globalShortcuts: ShortcutConfig[] = [
    // Navigation
    {
      key: 'h',
      ctrl: true,
      description: 'Go to Home/Dashboard',
      category: 'Navigation',
      handler: () => navigate('/'),
    },
    {
      key: 's',
      ctrl: true,
      shift: true,
      description: 'Go to Solar Calculator',
      category: 'Navigation',
      handler: () => navigate('/solar'),
    },
    {
      key: 'h',
      ctrl: true,
      shift: true,
      description: 'Go to Heat Pump Calculator',
      category: 'Navigation',
      handler: () => navigate('/heatpump'),
    },
    {
      key: 'p',
      ctrl: true,
      shift: true,
      description: 'Go to Price Matrix',
      category: 'Navigation',
      handler: () => navigate('/pricing'),
    },
    {
      key: 'd',
      ctrl: true,
      shift: true,
      description: 'Go to PDF Generation',
      category: 'Navigation',
      handler: () => navigate('/pdf'),
    },
    {
      key: 'c',
      ctrl: true,
      shift: true,
      description: 'Go to CRM',
      category: 'Navigation',
      handler: () => navigate('/crm'),
    },
    {
      key: 'u',
      ctrl: true,
      shift: true,
      description: 'Go to Products',
      category: 'Navigation',
      handler: () => navigate('/products'),
    },
    {
      key: ',',
      ctrl: true,
      description: 'Open Settings',
      category: 'Navigation',
      handler: () => navigate('/settings'),
    },

    // Application
    {
      key: 'k',
      ctrl: true,
      description: 'Open Command Palette',
      category: 'Application',
      handler: () => {
        // Trigger command palette
        window.dispatchEvent(new CustomEvent('open-command-palette'));
      },
    },
    {
      key: '/',
      ctrl: true,
      description: 'Open Search',
      category: 'Application',
      handler: () => {
        // Trigger global search
        window.dispatchEvent(new CustomEvent('open-search'));
      },
    },
    {
      key: '?',
      ctrl: true,
      shift: true,
      description: 'Show Keyboard Shortcuts',
      category: 'Application',
      handler: () => {
        navigate('/settings/shortcuts');
      },
    },
    {
      key: 'r',
      ctrl: true,
      description: 'Refresh Current Page',
      category: 'Application',
      handler: () => {
        window.location.reload();
      },
    },
    {
      key: 'q',
      ctrl: true,
      description: 'Quit Application',
      category: 'Application',
      handler: () => {
        if (window.electronAPI) {
          window.electronAPI.close();
        }
      },
    },

    // View
    {
      key: 'b',
      ctrl: true,
      description: 'Toggle Sidebar',
      category: 'View',
      handler: () => {
        window.dispatchEvent(new CustomEvent('toggle-sidebar'));
      },
    },
    {
      key: '+',
      ctrl: true,
      description: 'Zoom In',
      category: 'View',
      handler: () => {
        document.body.style.zoom = `${parseFloat(document.body.style.zoom || '1') + 0.1}`;
      },
    },
    {
      key: '-',
      ctrl: true,
      description: 'Zoom Out',
      category: 'View',
      handler: () => {
        document.body.style.zoom = `${parseFloat(document.body.style.zoom || '1') - 0.1}`;
      },
    },
    {
      key: '0',
      ctrl: true,
      description: 'Reset Zoom',
      category: 'View',
      handler: () => {
        document.body.style.zoom = '1';
      },
    },
    {
      key: 'f11',
      description: 'Toggle Fullscreen',
      category: 'View',
      handler: () => {
        if (document.fullscreenElement) {
          document.exitFullscreen();
        } else {
          document.documentElement.requestFullscreen();
        }
      },
    },

    // Help
    {
      key: 'F1',
      description: 'Open Help',
      category: 'Help',
      handler: () => {
        navigate('/help');
      },
    },
  ];

  // Register global shortcuts
  useKeyboardShortcuts(globalShortcuts, 'global');

  return null; // This component doesn't render anything
};
