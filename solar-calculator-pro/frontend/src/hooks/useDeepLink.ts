/**
 * React Hook for Deep Link Integration
 * 
 * Provides functionality to generate, handle, and test deep links
 * in the Solar Calculator Pro application
 */

import { useEffect, useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface DeepLinkParams {
  [key: string]: string | number | boolean;
}

interface DeepLinkResult {
  success: boolean;
  deepLink?: string;
  error?: string;
}

interface DeepLinkHandlers {
  handlers: string[];
  success: boolean;
}

interface DeepLinkStatus {
  isRegistered: boolean;
  success: boolean;
}

export const useDeepLink = () => {
  const navigate = useNavigate();
  const [isElectron] = useState(() => window.electronAPI !== undefined);

  /**
   * Generate a deep link URL
   */
  const generateDeepLink = useCallback(
    async (
      action: string,
      params: DeepLinkParams = {},
      pathSegments: string[] = []
    ): Promise<DeepLinkResult> => {
      if (!isElectron) {
        return { success: false, error: 'Not running in Electron' };
      }

      try {
        const result = await window.electronAPI.deepLink.generate({
          action,
          params,
          pathSegments,
        });
        return result;
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
      }
    },
    [isElectron]
  );

  /**
   * Generate and copy deep link to clipboard
   */
  const copyDeepLinkToClipboard = useCallback(
    async (
      action: string,
      params: DeepLinkParams = {},
      pathSegments: string[] = []
    ): Promise<DeepLinkResult> => {
      if (!isElectron) {
        return { success: false, error: 'Not running in Electron' };
      }

      try {
        const result = await window.electronAPI.deepLink.copyToClipboard({
          action,
          params,
          pathSegments,
        });
        return result;
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
      }
    },
    [isElectron]
  );

  /**
   * Test a deep link URL
   */
  const testDeepLink = useCallback(
    async (urlString: string): Promise<{ success: boolean; error?: string }> => {
      if (!isElectron) {
        return { success: false, error: 'Not running in Electron' };
      }

      try {
        const result = await window.electronAPI.deepLink.test(urlString);
        return result;
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
      }
    },
    [isElectron]
  );

  /**
   * Get list of registered deep link handlers
   */
  const getRegisteredHandlers = useCallback(async (): Promise<DeepLinkHandlers> => {
    if (!isElectron) {
      return { success: false, handlers: [] };
    }

    try {
      const result = await window.electronAPI.deepLink.getHandlers();
      return result;
    } catch (error) {
      return { success: false, handlers: [] };
    }
  }, [isElectron]);

  /**
   * Check if deep link protocol is registered
   */
  const isProtocolRegistered = useCallback(async (): Promise<DeepLinkStatus> => {
    if (!isElectron) {
      return { success: false, isRegistered: false };
    }

    try {
      const result = await window.electronAPI.deepLink.isRegistered();
      return result;
    } catch (error) {
      return { success: false, isRegistered: false };
    }
  }, [isElectron]);

  /**
   * Setup deep link event listeners
   */
  useEffect(() => {
    if (!isElectron || !window.electronAPI) return;

    // Handler for opening projects
    const handleOpenProject = (data: { projectId: string }) => {
      console.log('Deep link: Open project', data);
      navigate(`/projects/${data.projectId}`);
    };

    // Handler for opening project by path
    const handleOpenProjectPath = (data: { projectPath: string }) => {
      console.log('Deep link: Open project path', data);
      // Trigger import/open logic
      // This would need to be implemented in your project management system
    };

    // Handler for navigation
    const handleNavigate = (data: { page: string; params: DeepLinkParams }) => {
      console.log('Deep link: Navigate', data);
      const queryString = new URLSearchParams(
        data.params as Record<string, string>
      ).toString();
      const path = queryString ? `/${data.page}?${queryString}` : `/${data.page}`;
      navigate(path);
    };

    // Handler for solar calculator
    const handleSolarCalculator = (data: { params: DeepLinkParams }) => {
      console.log('Deep link: Solar calculator', data);
      navigate('/solar-calculator', { state: { prefillData: data.params } });
    };

    // Handler for heat pump
    const handleHeatPump = (data: { params: DeepLinkParams }) => {
      console.log('Deep link: Heat pump', data);
      navigate('/heat-pump', { state: { prefillData: data.params } });
    };

    // Handler for customer
    const handleCustomer = (data: { customerId: string }) => {
      console.log('Deep link: Customer', data);
      navigate(`/crm/customers/${data.customerId}`);
    };

    // Handler for offer
    const handleOffer = (data: { offerId: string }) => {
      console.log('Deep link: Offer', data);
      navigate(`/crm/offers/${data.offerId}`);
    };

    // Handler for PDF generation
    const handleGeneratePDF = (data: { projectId: string; templateId?: string }) => {
      console.log('Deep link: Generate PDF', data);
      navigate(`/pdf-generation`, {
        state: { projectId: data.projectId, templateId: data.templateId },
      });
    };

    // Handler for import
    const handleImport = (data: { filePath: string; importType?: string }) => {
      console.log('Deep link: Import', data);
      // Trigger import logic
      // This would need to be implemented in your import system
    };

    // Handler for email
    const handleEmail = (data: {
      to?: string;
      subject?: string;
      body?: string;
      attachmentId?: string;
    }) => {
      console.log('Deep link: Email', data);
      // Trigger email compose
      // This would need to be implemented in your email system
    };

    // Handler for share project
    const handleShareProject = (data: { projectId: string; email?: string }) => {
      console.log('Deep link: Share project', data);
      // Trigger share dialog
      // This would need to be implemented in your sharing system
    };

    // Handler for settings
    const handleSettings = (data: { section?: string }) => {
      console.log('Deep link: Settings', data);
      const path = data.section ? `/settings/${data.section}` : '/settings';
      navigate(path);
    };

    // Handler for dashboard
    const handleDashboard = (data: { params: DeepLinkParams }) => {
      console.log('Deep link: Dashboard', data);
      navigate('/dashboard');
    };

    // Handler for new project
    const handleNewProject = (data: { projectType?: string; params: DeepLinkParams }) => {
      console.log('Deep link: New project', data);
      navigate('/projects/new', {
        state: { projectType: data.projectType, prefillData: data.params },
      });
    };

    // Handler for 3D view
    const handle3DView = (data: { projectId: string }) => {
      console.log('Deep link: 3D view', data);
      navigate(`/3d-visualization/${data.projectId}`);
    };

    // Handler for price matrix
    const handlePriceMatrix = (data: { matrixId?: string }) => {
      console.log('Deep link: Price matrix', data);
      const path = data.matrixId ? `/price-matrix/${data.matrixId}` : '/price-matrix';
      navigate(path);
    };

    // Handler for products
    const handleProducts = (data: { category?: string; search?: string }) => {
      console.log('Deep link: Products', data);
      const params = new URLSearchParams();
      if (data.category) params.set('category', data.category);
      if (data.search) params.set('search', data.search);
      const queryString = params.toString();
      const path = queryString ? `/products?${queryString}` : '/products';
      navigate(path);
    };

    // Handler for login
    const handleLogin = (data: { token?: string; redirect?: string }) => {
      console.log('Deep link: Login', data);
      // Handle token-based login
      // This would need to be implemented in your auth system
      if (data.redirect) {
        navigate(data.redirect);
      } else {
        navigate('/login');
      }
    };

    // Handler for password reset
    const handleResetPassword = (data: { token: string }) => {
      console.log('Deep link: Reset password', data);
      navigate('/reset-password', { state: { token: data.token } });
    };

    // Handler for email verification
    const handleVerifyEmail = (data: { token: string }) => {
      console.log('Deep link: Verify email', data);
      navigate('/verify-email', { state: { token: data.token } });
    };

    // Register all handlers
    window.electronAPI.on('deep-link:open-project', handleOpenProject);
    window.electronAPI.on('deep-link:open-project-path', handleOpenProjectPath);
    window.electronAPI.on('deep-link:navigate', handleNavigate);
    window.electronAPI.on('deep-link:solar-calculator', handleSolarCalculator);
    window.electronAPI.on('deep-link:heat-pump', handleHeatPump);
    window.electronAPI.on('deep-link:customer', handleCustomer);
    window.electronAPI.on('deep-link:offer', handleOffer);
    window.electronAPI.on('deep-link:generate-pdf', handleGeneratePDF);
    window.electronAPI.on('deep-link:import', handleImport);
    window.electronAPI.on('deep-link:email', handleEmail);
    window.electronAPI.on('deep-link:share-project', handleShareProject);
    window.electronAPI.on('deep-link:settings', handleSettings);
    window.electronAPI.on('deep-link:dashboard', handleDashboard);
    window.electronAPI.on('deep-link:new-project', handleNewProject);
    window.electronAPI.on('deep-link:3d-view', handle3DView);
    window.electronAPI.on('deep-link:price-matrix', handlePriceMatrix);
    window.electronAPI.on('deep-link:products', handleProducts);
    window.electronAPI.on('deep-link:login', handleLogin);
    window.electronAPI.on('deep-link:reset-password', handleResetPassword);
    window.electronAPI.on('deep-link:verify-email', handleVerifyEmail);

    // Cleanup
    return () => {
      // Note: electron-api doesn't provide removeListener in the current implementation
      // This would need to be added to the preload script if needed
    };
  }, [isElectron, navigate]);

  return {
    generateDeepLink,
    copyDeepLinkToClipboard,
    testDeepLink,
    getRegisteredHandlers,
    isProtocolRegistered,
    isElectron,
  };
};

export default useDeepLink;
