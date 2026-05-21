/**
 * Module Feature Manager Component
 * 
 * Admin interface for managing module-level feature toggles
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { InputSwitch } from 'primereact/inputswitch';
import { Message } from 'primereact/message';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Accordion, AccordionTab } from 'primereact/accordion';
import { Divider } from 'primereact/divider';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import { useModuleFeatures, ModulesStatus } from '../../hooks/useModuleFeatures';
import './ModuleFeatureManager.css';

interface ModuleFeatureManagerProps {
  userId?: number;
}

export const ModuleFeatureManager: React.FC<ModuleFeatureManagerProps> = ({ userId }) => {
  const { modules, isLoading, error, refresh } = useModuleFeatures({ userId });
  const [isInitializing, setIsInitializing] = useState(false);
  const [isToggling, setIsToggling] = useState<string | null>(null);
  const toastRef = React.useRef<Toast>(null);

  const handleInitialize = async () => {
    try {
      setIsInitializing(true);
      const response = await api.post('/api/v1/module-features/initialize');
      
      toastRef.current?.show({
        severity: 'success',
        summary: 'Initialization Complete',
        detail: `Created: ${response.data.created}, Existing: ${response.data.existing}, Errors: ${response.data.errors}`,
        life: 5000,
      });
      
      await refresh();
    } catch (err: any) {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Initialization Failed',
        detail: err.response?.data?.detail || 'Failed to initialize module features',
        life: 5000,
      });
    } finally {
      setIsInitializing(false);
    }
  };

  const handleToggleModule = async (moduleKey: string, enabled: boolean) => {
    try {
      setIsToggling(moduleKey);
      await api.post('/api/v1/module-features/toggle-module', {
        module_key: moduleKey,
        enabled,
      });
      
      toastRef.current?.show({
        severity: 'success',
        summary: 'Module Updated',
        detail: `Module ${enabled ? 'enabled' : 'disabled'} successfully`,
        life: 3000,
      });
      
      await refresh();
    } catch (err: any) {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Toggle Failed',
        detail: err.response?.data?.detail || 'Failed to toggle module',
        life: 5000,
      });
    } finally {
      setIsToggling(null);
    }
  };

  const handleToggleSubFeature = async (subFeatureKey: string, enabled: boolean) => {
    try {
      setIsToggling(subFeatureKey);
      await api.post('/api/v1/module-features/toggle-sub-feature', {
        sub_feature_key: subFeatureKey,
        enabled,
      });
      
      toastRef.current?.show({
        severity: 'success',
        summary: 'Sub-Feature Updated',
        detail: `Sub-feature ${enabled ? 'enabled' : 'disabled'} successfully`,
        life: 3000,
      });
      
      await refresh();
    } catch (err: any) {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Toggle Failed',
        detail: err.response?.data?.detail || 'Failed to toggle sub-feature',
        life: 5000,
      });
    } finally {
      setIsToggling(null);
    }
  };

  const getModuleIcon = (moduleName: string): string => {
    const icons: Record<string, string> = {
      solar_calculator: 'pi-sun',
      heat_pump: 'pi-bolt',
      price_matrix: 'pi-dollar',
      pdf_generation: 'pi-file-pdf',
      crm: 'pi-users',
      '3d_visualization': 'pi-box',
    };
    return icons[moduleName] || 'pi-cog';
  };

  const getModuleTitle = (moduleName: string): string => {
    const titles: Record<string, string> = {
      solar_calculator: 'Solar Calculator',
      heat_pump: 'Heat Pump',
      price_matrix: 'Price Matrix',
      pdf_generation: 'PDF Generation',
      crm: 'CRM',
      '3d_visualization': '3D Visualization',
    };
    return titles[moduleName] || moduleName;
  };

  const getSubFeatureLabel = (key: string): string => {
    const parts = key.split('.');
    const label = parts[parts.length - 1];
    return label
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (isLoading) {
    return (
      <div className="module-feature-manager-loading">
        <ProgressSpinner />
        <p>Loading module features...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="module-feature-manager-error">
        <Message severity="error" text={error} />
        <Button
          label="Retry"
          icon="pi pi-refresh"
          onClick={refresh}
          className="p-mt-2"
        />
      </div>
    );
  }

  if (!modules) {
    return (
      <div className="module-feature-manager-empty">
        <Message
          severity="info"
          text="No module features found. Initialize the system to create default features."
        />
        <Button
          label="Initialize Module Features"
          icon="pi pi-plus"
          onClick={handleInitialize}
          loading={isInitializing}
          className="p-mt-3"
        />
      </div>
    );
  }

  return (
    <div className="module-feature-manager">
      <Toast ref={toastRef} />
      
      <Card title="Module Feature Management" className="module-feature-card">
        <div className="module-feature-header">
          <p className="module-feature-description">
            Manage module-level feature toggles for the application. Enable or disable entire
            modules and their sub-features.
          </p>
          <div className="module-feature-actions">
            <Button
              label="Refresh"
              icon="pi pi-refresh"
              onClick={refresh}
              className="p-button-outlined"
            />
            <Button
              label="Initialize Features"
              icon="pi pi-plus"
              onClick={handleInitialize}
              loading={isInitializing}
              className="p-button-outlined"
            />
          </div>
        </div>

        <Divider />

        <Accordion multiple>
          {Object.entries(modules).map(([moduleName, moduleData]) => {
            const moduleKey = `module.${moduleName}`;
            const isModuleToggling = isToggling === moduleKey;

            return (
              <AccordionTab
                key={moduleName}
                header={
                  <div className="module-header">
                    <i className={`pi ${getModuleIcon(moduleName)} module-icon`} />
                    <span className="module-title">{getModuleTitle(moduleName)}</span>
                    <InputSwitch
                      checked={moduleData.enabled}
                      onChange={(e) => handleToggleModule(moduleKey, e.value)}
                      disabled={isModuleToggling}
                      className="module-switch"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                }
              >
                <div className="sub-features-container">
                  {Object.entries(moduleData.sub_features).map(([subFeatureKey, enabled]) => {
                    const isSubFeatureToggling = isToggling === subFeatureKey;
                    const isDisabled = !moduleData.enabled || isSubFeatureToggling;

                    return (
                      <div key={subFeatureKey} className="sub-feature-item">
                        <div className="sub-feature-info">
                          <span className="sub-feature-label">
                            {getSubFeatureLabel(subFeatureKey)}
                          </span>
                          <span className="sub-feature-key">{subFeatureKey}</span>
                        </div>
                        <InputSwitch
                          checked={enabled && moduleData.enabled}
                          onChange={(e) => handleToggleSubFeature(subFeatureKey, e.value)}
                          disabled={isDisabled}
                          className="sub-feature-switch"
                        />
                      </div>
                    );
                  })}
                </div>
              </AccordionTab>
            );
          })}
        </Accordion>
      </Card>
    </div>
  );
};

export default ModuleFeatureManager;
