/**
 * Feature Toggle Demo Component
 * 
 * Demonstrates various ways to use the feature toggle system
 */

import React from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Badge } from 'primereact/badge';
import { useFeatureToggle, useFeatureToggles, withFeatureToggle } from '../hooks/useFeatureToggle';
import { FeatureGate, useFeatureToggleContext } from '../providers/FeatureToggleProvider';
import './FeatureToggleDemo.css';

/**
 * Example 1: Using the useFeatureToggle hook
 */
const Example1: React.FC = () => {
  const { isEnabled, isLoading, reason, refresh } = useFeatureToggle('solar-calculator-advanced');

  return (
    <Card title="Example 1: Single Feature Check" className="mb-3">
      <div className="flex flex-column gap-2">
        <p>Feature: solar-calculator-advanced</p>
        <div className="flex align-items-center gap-2">
          <span>Status:</span>
          {isLoading ? (
            <Badge value="Loading..." severity="info" />
          ) : (
            <Badge
              value={isEnabled ? 'Enabled' : 'Disabled'}
              severity={isEnabled ? 'success' : 'danger'}
            />
          )}
        </div>
        <p className="text-sm text-color-secondary">Reason: {reason}</p>
        <Button
          label="Refresh"
          icon="pi pi-refresh"
          onClick={refresh}
          className="p-button-sm"
        />
      </div>
    </Card>
  );
};

/**
 * Example 2: Using the useFeatureToggles hook for multiple features
 */
const Example2: React.FC = () => {
  const { features, isLoading, refresh } = useFeatureToggles([
    'solar-calculator-advanced',
    'heat-pump-calculator',
    'pdf-generation-v2',
    '3d-visualization',
  ]);

  return (
    <Card title="Example 2: Multiple Feature Checks" className="mb-3">
      <div className="flex flex-column gap-2">
        {isLoading ? (
          <p>Loading features...</p>
        ) : (
          Object.entries(features).map(([key, enabled]) => (
            <div key={key} className="flex justify-content-between align-items-center">
              <span>{key}</span>
              <Badge
                value={enabled ? 'Enabled' : 'Disabled'}
                severity={enabled ? 'success' : 'danger'}
              />
            </div>
          ))
        )}
        <Button
          label="Refresh All"
          icon="pi pi-refresh"
          onClick={refresh}
          className="p-button-sm mt-2"
        />
      </div>
    </Card>
  );
};

/**
 * Example 3: Using FeatureGate component
 */
const Example3: React.FC = () => {
  return (
    <Card title="Example 3: Feature Gate Component" className="mb-3">
      <FeatureGate
        featureKey="solar-calculator-advanced"
        fallback={
          <div className="p-message p-message-warn">
            <div className="p-message-wrapper">
              <span className="p-message-icon pi pi-exclamation-triangle"></span>
              <div className="p-message-text">
                Advanced solar calculator is not available for your account.
              </div>
            </div>
          </div>
        }
        loadingFallback={<p>Checking feature availability...</p>}
      >
        <div className="p-message p-message-success">
          <div className="p-message-wrapper">
            <span className="p-message-icon pi pi-check"></span>
            <div className="p-message-text">
              Advanced solar calculator is enabled! You can access all premium features.
            </div>
          </div>
        </div>
      </FeatureGate>
    </Card>
  );
};

/**
 * Example 4: Using context directly
 */
const Example4: React.FC = () => {
  const { features, isFeatureEnabled, refreshFeatures } = useFeatureToggleContext();

  return (
    <Card title="Example 4: Using Context Directly" className="mb-3">
      <div className="flex flex-column gap-2">
        <p>Total features loaded: {Object.keys(features).length}</p>
        <div className="flex flex-column gap-1">
          <div className="flex align-items-center gap-2">
            <span>Solar Calculator Advanced:</span>
            <Badge
              value={isFeatureEnabled('solar-calculator-advanced') ? 'Yes' : 'No'}
              severity={isFeatureEnabled('solar-calculator-advanced') ? 'success' : 'danger'}
            />
          </div>
          <div className="flex align-items-center gap-2">
            <span>Heat Pump Calculator:</span>
            <Badge
              value={isFeatureEnabled('heat-pump-calculator') ? 'Yes' : 'No'}
              severity={isFeatureEnabled('heat-pump-calculator') ? 'success' : 'danger'}
            />
          </div>
        </div>
        <Button
          label="Refresh Context"
          icon="pi pi-refresh"
          onClick={refreshFeatures}
          className="p-button-sm mt-2"
        />
      </div>
    </Card>
  );
};

/**
 * Example 5: Component wrapped with HOC
 */
const PremiumFeatureComponent: React.FC = () => {
  return (
    <div className="p-message p-message-info">
      <div className="p-message-wrapper">
        <span className="p-message-icon pi pi-star"></span>
        <div className="p-message-text">
          This is a premium feature component that only shows when the feature is enabled!
        </div>
      </div>
    </div>
  );
};

const WrappedPremiumComponent = withFeatureToggle(
  PremiumFeatureComponent,
  'premium-features',
  <div className="p-message p-message-warn">
    <div className="p-message-wrapper">
      <span className="p-message-icon pi pi-lock"></span>
      <div className="p-message-text">
        Premium features are not available. Please upgrade your account.
      </div>
    </div>
  </div>
);

const Example5: React.FC = () => {
  return (
    <Card title="Example 5: Higher-Order Component" className="mb-3">
      <WrappedPremiumComponent />
    </Card>
  );
};

/**
 * Example 6: Conditional rendering in JSX
 */
const Example6: React.FC = () => {
  const { isEnabled: showAdvancedOptions } = useFeatureToggle('advanced-options');
  const { isEnabled: showBetaFeatures } = useFeatureToggle('beta-features');

  return (
    <Card title="Example 6: Conditional Rendering" className="mb-3">
      <div className="flex flex-column gap-2">
        <Button label="Basic Action" icon="pi pi-check" className="p-button-sm" />
        
        {showAdvancedOptions && (
          <Button
            label="Advanced Action"
            icon="pi pi-cog"
            className="p-button-sm p-button-secondary"
          />
        )}
        
        {showBetaFeatures && (
          <Button
            label="Beta Feature"
            icon="pi pi-star"
            className="p-button-sm p-button-warning"
          />
        )}
        
        <div className="mt-2">
          <p className="text-sm">
            Advanced Options: {showAdvancedOptions ? '✓ Visible' : '✗ Hidden'}
          </p>
          <p className="text-sm">
            Beta Features: {showBetaFeatures ? '✓ Visible' : '✗ Hidden'}
          </p>
        </div>
      </div>
    </Card>
  );
};

/**
 * Main Demo Component
 */
const FeatureToggleDemo: React.FC = () => {
  return (
    <div className="feature-toggle-demo">
      <div className="card">
        <h1>Feature Toggle System Demo</h1>
        <p className="text-color-secondary mb-4">
          This page demonstrates various ways to use the feature toggle system in your
          application.
        </p>

        <div className="grid">
          <div className="col-12 md:col-6">
            <Example1 />
            <Example2 />
            <Example3 />
          </div>
          <div className="col-12 md:col-6">
            <Example4 />
            <Example5 />
            <Example6 />
          </div>
        </div>

        <Card title="Usage Guidelines" className="mt-4">
          <div className="flex flex-column gap-3">
            <div>
              <h4>1. Single Feature Check</h4>
              <p className="text-sm">
                Use <code>useFeatureToggle(key)</code> when you need to check a single
                feature flag.
              </p>
            </div>
            <div>
              <h4>2. Multiple Feature Checks</h4>
              <p className="text-sm">
                Use <code>useFeatureToggles([keys])</code> when you need to check multiple
                features at once.
              </p>
            </div>
            <div>
              <h4>3. Feature Gate Component</h4>
              <p className="text-sm">
                Use <code>&lt;FeatureGate&gt;</code> for declarative feature gating with
                fallback UI.
              </p>
            </div>
            <div>
              <h4>4. Context API</h4>
              <p className="text-sm">
                Use <code>useFeatureToggleContext()</code> for global feature state access.
              </p>
            </div>
            <div>
              <h4>5. Higher-Order Component</h4>
              <p className="text-sm">
                Use <code>withFeatureToggle(Component, key, fallback)</code> to wrap entire
                components.
              </p>
            </div>
            <div>
              <h4>6. Conditional Rendering</h4>
              <p className="text-sm">
                Use feature flags directly in JSX with <code>{'{isEnabled && <Component />}'}</code>
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default FeatureToggleDemo;
