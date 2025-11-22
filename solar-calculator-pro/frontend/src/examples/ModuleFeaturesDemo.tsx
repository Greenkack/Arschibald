/**
 * Module Features Demo Component
 * 
 * Demonstrates usage of module-level feature toggles in React
 */

import React from 'react';
import { Card } from 'primereact/card';
import { Badge } from 'primereact/badge';
import { Divider } from 'primereact/divider';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Message } from 'primereact/message';
import {
  useModuleFeatures,
  useModule,
  useSubFeature,
  MODULE_KEYS,
  SOLAR_SUB_FEATURES,
  HEAT_PUMP_SUB_FEATURES,
  PRICE_MATRIX_SUB_FEATURES,
  PDF_SUB_FEATURES,
  CRM_SUB_FEATURES,
  VIZ_3D_SUB_FEATURES,
} from '../hooks/useModuleFeatures';

export const ModuleFeaturesDemo: React.FC = () => {
  return (
    <div className="module-features-demo" style={{ padding: '2rem' }}>
      <h1>Module Features Demo</h1>
      <p>This page demonstrates how to use module-level feature toggles in React.</p>

      <Divider />

      <h2>Example 1: Check All Modules</h2>
      <AllModulesExample />

      <Divider />

      <h2>Example 2: Check Specific Module</h2>
      <SpecificModuleExample />

      <Divider />

      <h2>Example 3: Check Sub-Feature</h2>
      <SubFeatureExample />

      <Divider />

      <h2>Example 4: Conditional Rendering</h2>
      <ConditionalRenderingExample />

      <Divider />

      <h2>Example 5: Feature-Gated Component</h2>
      <FeatureGatedExample />
    </div>
  );
};

/**
 * Example 1: Check all modules
 */
const AllModulesExample: React.FC = () => {
  const { modules, isLoading, error } = useModuleFeatures();

  if (isLoading) {
    return <ProgressSpinner />;
  }

  if (error) {
    return <Message severity="error" text={error} />;
  }

  if (!modules) {
    return <Message severity="info" text="No modules found" />;
  }

  return (
    <Card>
      <h3>All Modules Status</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
        {Object.entries(modules).map(([moduleName, moduleData]) => (
          <Card key={moduleName} style={{ padding: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <strong>{moduleName.replace('_', ' ').toUpperCase()}</strong>
              <Badge
                value={moduleData.enabled ? 'ENABLED' : 'DISABLED'}
                severity={moduleData.enabled ? 'success' : 'danger'}
              />
            </div>
            <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
              {Object.keys(moduleData.sub_features).length} sub-features
            </div>
          </Card>
        ))}
      </div>
    </Card>
  );
};

/**
 * Example 2: Check specific module
 */
const SpecificModuleExample: React.FC = () => {
  const { isEnabled, isLoading } = useModule(MODULE_KEYS.SOLAR_CALCULATOR);

  return (
    <Card>
      <h3>Solar Calculator Module</h3>
      {isLoading ? (
        <ProgressSpinner />
      ) : (
        <div>
          <p>
            Status:{' '}
            <Badge
              value={isEnabled ? 'ENABLED' : 'DISABLED'}
              severity={isEnabled ? 'success' : 'danger'}
            />
          </p>
          <p>
            {isEnabled
              ? '✅ Solar Calculator module is available'
              : '❌ Solar Calculator module is not available'}
          </p>
        </div>
      )}
    </Card>
  );
};

/**
 * Example 3: Check sub-feature
 */
const SubFeatureExample: React.FC = () => {
  const { isEnabled, isLoading } = useSubFeature(
    MODULE_KEYS.SOLAR_CALCULATOR,
    SOLAR_SUB_FEATURES.SHADING_ANALYSIS
  );

  return (
    <Card>
      <h3>Shading Analysis Sub-Feature</h3>
      {isLoading ? (
        <ProgressSpinner />
      ) : (
        <div>
          <p>
            Status:{' '}
            <Badge
              value={isEnabled ? 'ENABLED' : 'DISABLED'}
              severity={isEnabled ? 'success' : 'danger'}
            />
          </p>
          <p>
            {isEnabled
              ? '✅ Shading Analysis feature is available'
              : '❌ Shading Analysis feature is not available (parent module or sub-feature disabled)'}
          </p>
        </div>
      )}
    </Card>
  );
};

/**
 * Example 4: Conditional rendering based on module status
 */
const ConditionalRenderingExample: React.FC = () => {
  const { isModuleEnabled, isSubFeatureEnabled } = useModuleFeatures();

  return (
    <Card>
      <h3>Conditional Rendering</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {isModuleEnabled('solar_calculator') && (
          <Message severity="success" text="✅ Solar Calculator module is enabled - showing solar features" />
        )}

        {isModuleEnabled('heat_pump') && (
          <Message severity="success" text="✅ Heat Pump module is enabled - showing heat pump features" />
        )}

        {isModuleEnabled('crm') && (
          <Message severity="success" text="✅ CRM module is enabled - showing CRM features" />
        )}

        {isSubFeatureEnabled('solar_calculator', SOLAR_SUB_FEATURES.BATTERY_STORAGE) && (
          <Message severity="info" text="ℹ️ Battery Storage sub-feature is enabled" />
        )}

        {!isModuleEnabled('solar_calculator') && (
          <Message severity="warn" text="⚠️ Solar Calculator module is disabled" />
        )}
      </div>
    </Card>
  );
};

/**
 * Example 5: Feature-gated component
 */
const FeatureGatedExample: React.FC = () => {
  return (
    <Card>
      <h3>Feature-Gated Components</h3>
      <p>These components only render if their respective features are enabled:</p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
        <SolarCalculatorFeature />
        <HeatPumpFeature />
        <ShadingAnalysisFeature />
      </div>
    </Card>
  );
};

/**
 * Solar Calculator feature component
 */
const SolarCalculatorFeature: React.FC = () => {
  const { isEnabled } = useModule(MODULE_KEYS.SOLAR_CALCULATOR);

  if (!isEnabled) {
    return <Message severity="warn" text="Solar Calculator module is disabled" />;
  }

  return (
    <Card style={{ backgroundColor: '#e8f5e9' }}>
      <h4>☀️ Solar Calculator</h4>
      <p>This component is only visible when the Solar Calculator module is enabled.</p>
    </Card>
  );
};

/**
 * Heat Pump feature component
 */
const HeatPumpFeature: React.FC = () => {
  const { isEnabled } = useModule(MODULE_KEYS.HEAT_PUMP);

  if (!isEnabled) {
    return <Message severity="warn" text="Heat Pump module is disabled" />;
  }

  return (
    <Card style={{ backgroundColor: '#e3f2fd' }}>
      <h4>⚡ Heat Pump</h4>
      <p>This component is only visible when the Heat Pump module is enabled.</p>
    </Card>
  );
};

/**
 * Shading Analysis sub-feature component
 */
const ShadingAnalysisFeature: React.FC = () => {
  const { isEnabled } = useSubFeature(
    MODULE_KEYS.SOLAR_CALCULATOR,
    SOLAR_SUB_FEATURES.SHADING_ANALYSIS
  );

  if (!isEnabled) {
    return <Message severity="warn" text="Shading Analysis sub-feature is disabled" />;
  }

  return (
    <Card style={{ backgroundColor: '#fff3e0' }}>
      <h4>🌤️ Shading Analysis</h4>
      <p>
        This component is only visible when both the Solar Calculator module AND the Shading
        Analysis sub-feature are enabled.
      </p>
    </Card>
  );
};

/**
 * Code examples for documentation
 */
export const CodeExamples = () => {
  return (
    <div style={{ padding: '2rem' }}>
      <h2>Code Examples</h2>

      <h3>1. Check if a module is enabled</h3>
      <pre style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
        {`import { useModule, MODULE_KEYS } from '@/hooks/useModuleFeatures';

function MyComponent() {
  const { isEnabled, isLoading } = useModule(MODULE_KEYS.SOLAR_CALCULATOR);
  
  if (isLoading) return <Loading />;
  if (!isEnabled) return <ModuleDisabled />;
  
  return <SolarCalculator />;
}`}
      </pre>

      <h3>2. Check if a sub-feature is enabled</h3>
      <pre style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
        {`import { useSubFeature, MODULE_KEYS, SOLAR_SUB_FEATURES } from '@/hooks/useModuleFeatures';

function ShadingAnalysis() {
  const { isEnabled } = useSubFeature(
    MODULE_KEYS.SOLAR_CALCULATOR,
    SOLAR_SUB_FEATURES.SHADING_ANALYSIS
  );
  
  if (!isEnabled) return null;
  
  return <ShadingAnalysisComponent />;
}`}
      </pre>

      <h3>3. Check all modules at once</h3>
      <pre style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
        {`import { useModuleFeatures } from '@/hooks/useModuleFeatures';

function Dashboard() {
  const { modules, isModuleEnabled, isSubFeatureEnabled } = useModuleFeatures();
  
  return (
    <div>
      {isModuleEnabled('solar_calculator') && <SolarWidget />}
      {isModuleEnabled('heat_pump') && <HeatPumpWidget />}
      {isModuleEnabled('crm') && <CRMWidget />}
    </div>
  );
}`}
      </pre>

      <h3>4. Admin UI for managing features</h3>
      <pre style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
        {`import { ModuleFeatureManager } from '@/components/admin/ModuleFeatureManager';

function AdminPage() {
  return (
    <div>
      <h1>Module Management</h1>
      <ModuleFeatureManager />
    </div>
  );
}`}
      </pre>
    </div>
  );
};

export default ModuleFeaturesDemo;
