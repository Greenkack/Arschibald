/**
 * Context-Specific Shortcuts
 * 
 * Provides shortcuts that are specific to certain pages or contexts
 */

import React from 'react';
import { useLocation } from 'react-router-dom';
import { useKeyboardShortcuts, ShortcutConfig } from '../../hooks/useKeyboardShortcuts';

export const ContextShortcuts: React.FC = () => {
  const location = useLocation();

  // Determine current context from route
  const context = React.useMemo(() => {
    const path = location.pathname;
    if (path.startsWith('/solar')) return 'solar';
    if (path.startsWith('/heatpump')) return 'heatpump';
    if (path.startsWith('/pricing')) return 'pricing';
    if (path.startsWith('/pdf')) return 'pdf';
    if (path.startsWith('/crm')) return 'crm';
    if (path.startsWith('/products')) return 'products';
    return null;
  }, [location.pathname]);

  // Solar Calculator shortcuts
  const solarShortcuts: ShortcutConfig[] = [
    {
      key: 'n',
      ctrl: true,
      description: 'New Solar Project',
      category: 'Solar Calculator',
      context: 'solar',
      handler: () => {
        window.dispatchEvent(new CustomEvent('solar-new-project'));
      },
    },
    {
      key: 's',
      ctrl: true,
      description: 'Save Solar Project',
      category: 'Solar Calculator',
      context: 'solar',
      handler: () => {
        window.dispatchEvent(new CustomEvent('solar-save-project'));
      },
    },
    {
      key: 'Enter',
      ctrl: true,
      description: 'Calculate Solar System',
      category: 'Solar Calculator',
      context: 'solar',
      handler: () => {
        window.dispatchEvent(new CustomEvent('solar-calculate'));
      },
    },
    {
      key: 'e',
      ctrl: true,
      description: 'Export Solar Results',
      category: 'Solar Calculator',
      context: 'solar',
      handler: () => {
        window.dispatchEvent(new CustomEvent('solar-export'));
      },
    },
    {
      key: '3',
      ctrl: true,
      description: 'Toggle 3D View',
      category: 'Solar Calculator',
      context: 'solar',
      handler: () => {
        window.dispatchEvent(new CustomEvent('solar-toggle-3d'));
      },
    },
  ];

  // Heat Pump shortcuts
  const heatpumpShortcuts: ShortcutConfig[] = [
    {
      key: 'n',
      ctrl: true,
      description: 'New Heat Pump Project',
      category: 'Heat Pump',
      context: 'heatpump',
      handler: () => {
        window.dispatchEvent(new CustomEvent('heatpump-new-project'));
      },
    },
    {
      key: 's',
      ctrl: true,
      description: 'Save Heat Pump Project',
      category: 'Heat Pump',
      context: 'heatpump',
      handler: () => {
        window.dispatchEvent(new CustomEvent('heatpump-save-project'));
      },
    },
    {
      key: 'Enter',
      ctrl: true,
      description: 'Calculate Heat Pump',
      category: 'Heat Pump',
      context: 'heatpump',
      handler: () => {
        window.dispatchEvent(new CustomEvent('heatpump-calculate'));
      },
    },
  ];

  // Price Matrix shortcuts
  const pricingShortcuts: ShortcutConfig[] = [
    {
      key: 'u',
      ctrl: true,
      description: 'Upload Price Matrix',
      category: 'Price Matrix',
      context: 'pricing',
      handler: () => {
        window.dispatchEvent(new CustomEvent('pricing-upload'));
      },
    },
    {
      key: 'p',
      ctrl: true,
      description: 'Preview Price Matrix',
      category: 'Price Matrix',
      context: 'pricing',
      handler: () => {
        window.dispatchEvent(new CustomEvent('pricing-preview'));
      },
    },
    {
      key: 'v',
      ctrl: true,
      description: 'Validate Price Matrix',
      category: 'Price Matrix',
      context: 'pricing',
      handler: () => {
        window.dispatchEvent(new CustomEvent('pricing-validate'));
      },
    },
  ];

  // PDF Generation shortcuts
  const pdfShortcuts: ShortcutConfig[] = [
    {
      key: 'g',
      ctrl: true,
      description: 'Generate PDF',
      category: 'PDF Generation',
      context: 'pdf',
      handler: () => {
        window.dispatchEvent(new CustomEvent('pdf-generate'));
      },
    },
    {
      key: 'p',
      ctrl: true,
      description: 'Preview PDF',
      category: 'PDF Generation',
      context: 'pdf',
      handler: () => {
        window.dispatchEvent(new CustomEvent('pdf-preview'));
      },
    },
    {
      key: 'd',
      ctrl: true,
      description: 'Download PDF',
      category: 'PDF Generation',
      context: 'pdf',
      handler: () => {
        window.dispatchEvent(new CustomEvent('pdf-download'));
      },
    },
    {
      key: 'e',
      ctrl: true,
      description: 'Email PDF',
      category: 'PDF Generation',
      context: 'pdf',
      handler: () => {
        window.dispatchEvent(new CustomEvent('pdf-email'));
      },
    },
  ];

  // CRM shortcuts
  const crmShortcuts: ShortcutConfig[] = [
    {
      key: 'n',
      ctrl: true,
      description: 'New Customer',
      category: 'CRM',
      context: 'crm',
      handler: () => {
        window.dispatchEvent(new CustomEvent('crm-new-customer'));
      },
    },
    {
      key: 'o',
      ctrl: true,
      description: 'New Offer',
      category: 'CRM',
      context: 'crm',
      handler: () => {
        window.dispatchEvent(new CustomEvent('crm-new-offer'));
      },
    },
    {
      key: 't',
      ctrl: true,
      description: 'New Task',
      category: 'CRM',
      context: 'crm',
      handler: () => {
        window.dispatchEvent(new CustomEvent('crm-new-task'));
      },
    },
    {
      key: 'f',
      ctrl: true,
      description: 'Search Customers',
      category: 'CRM',
      context: 'crm',
      handler: () => {
        window.dispatchEvent(new CustomEvent('crm-search'));
      },
    },
  ];

  // Products shortcuts
  const productsShortcuts: ShortcutConfig[] = [
    {
      key: 'n',
      ctrl: true,
      description: 'New Product',
      category: 'Products',
      context: 'products',
      handler: () => {
        window.dispatchEvent(new CustomEvent('products-new'));
      },
    },
    {
      key: 'f',
      ctrl: true,
      description: 'Search Products',
      category: 'Products',
      context: 'products',
      handler: () => {
        window.dispatchEvent(new CustomEvent('products-search'));
      },
    },
    {
      key: 'i',
      ctrl: true,
      description: 'Import Products',
      category: 'Products',
      context: 'products',
      handler: () => {
        window.dispatchEvent(new CustomEvent('products-import'));
      },
    },
    {
      key: 'e',
      ctrl: true,
      description: 'Export Products',
      category: 'Products',
      context: 'products',
      handler: () => {
        window.dispatchEvent(new CustomEvent('products-export'));
      },
    },
  ];

  // Register shortcuts based on context
  useKeyboardShortcuts(solarShortcuts, 'solar', context === 'solar');
  useKeyboardShortcuts(heatpumpShortcuts, 'heatpump', context === 'heatpump');
  useKeyboardShortcuts(pricingShortcuts, 'pricing', context === 'pricing');
  useKeyboardShortcuts(pdfShortcuts, 'pdf', context === 'pdf');
  useKeyboardShortcuts(crmShortcuts, 'crm', context === 'crm');
  useKeyboardShortcuts(productsShortcuts, 'products', context === 'products');

  return null;
};
