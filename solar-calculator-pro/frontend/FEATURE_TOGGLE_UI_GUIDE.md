# Feature Toggle UI Guide

## Overview

The Feature Toggle UI system provides a comprehensive admin interface for managing feature flags, including toggle switches, preview mode, rollout scheduling, usage analytics, and dependency management.

## Components

### 1. FeatureToggleManager

The main admin interface for managing feature flags.

**Location:** `src/components/admin/FeatureToggleManager.tsx`

**Features:**
- Create, read, update, and delete feature flags
- Toggle features on/off with a single click
- Support for multiple flag types (global, user-based, role-based, percentage rollout)
- Real-time preview mode
- Rollout scheduling
- Usage analytics
- Dependency management

**Usage:**
```tsx
import FeatureToggleManager from './components/admin/FeatureToggleManager';

function AdminPanel() {
  return (
    <div>
      <h1>Admin Panel</h1>
      <FeatureToggleManager />
    </div>
  );
}
```

### 2. useFeatureToggle Hook

Custom hook for checking individual feature flags.

**Location:** `src/hooks/useFeatureToggle.ts`

**Usage:**
```tsx
import { useFeatureToggle } from './hooks/useFeatureToggle';

function MyComponent() {
  const { isEnabled, isLoading, reason, refresh } = useFeatureToggle('my-feature');

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {isEnabled ? (
        <PremiumFeature />
      ) : (
        <div>Feature not available</div>
      )}
    </div>
  );
}
```

**Options:**
```tsx
const { isEnabled } = useFeatureToggle('my-feature', {
  userId: 123,              // Optional: Check for specific user
  autoRefresh: true,        // Optional: Auto-refresh flag status
  refreshInterval: 60000,   // Optional: Refresh interval in ms (default: 60000)
});
```

### 3. useFeatureToggles Hook

Custom hook for checking multiple feature flags at once.

**Location:** `src/hooks/useFeatureToggle.ts`

**Usage:**
```tsx
import { useFeatureToggles } from './hooks/useFeatureToggle';

function MyComponent() {
  const { features, isLoading, isFeatureEnabled } = useFeatureToggles([
    'feature-a',
    'feature-b',
    'feature-c',
  ]);

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {isFeatureEnabled('feature-a') && <FeatureA />}
      {isFeatureEnabled('feature-b') && <FeatureB />}
      {isFeatureEnabled('feature-c') && <FeatureC />}
    </div>
  );
}
```

### 4. FeatureToggleProvider

Global context provider for feature toggle state management.

**Location:** `src/providers/FeatureToggleProvider.tsx`

**Usage:**
```tsx
import { FeatureToggleProvider } from './providers/FeatureToggleProvider';

function App() {
  return (
    <FeatureToggleProvider
      userId={currentUser?.id}
      preloadKeys={['feature-a', 'feature-b']}
      autoRefresh={true}
      refreshInterval={300000}
    >
      <YourApp />
    </FeatureToggleProvider>
  );
}
```

**Props:**
- `userId`: Optional user ID for user-specific feature checks
- `preloadKeys`: Array of feature keys to preload on mount
- `autoRefresh`: Enable automatic refresh of feature flags
- `refreshInterval`: Refresh interval in milliseconds (default: 300000 = 5 minutes)

### 5. FeatureGate Component

Declarative component for feature gating with fallback UI.

**Location:** `src/providers/FeatureToggleProvider.tsx`

**Usage:**
```tsx
import { FeatureGate } from './providers/FeatureToggleProvider';

function MyComponent() {
  return (
    <FeatureGate
      featureKey="premium-feature"
      fallback={<div>This feature is not available</div>}
      loadingFallback={<div>Checking availability...</div>}
    >
      <PremiumFeature />
    </FeatureGate>
  );
}
```

### 6. withFeatureToggle HOC

Higher-order component for wrapping components with feature gating.

**Location:** `src/hooks/useFeatureToggle.ts`

**Usage:**
```tsx
import { withFeatureToggle } from './hooks/useFeatureToggle';

const PremiumComponent = () => <div>Premium Content</div>;

const GatedPremiumComponent = withFeatureToggle(
  PremiumComponent,
  'premium-feature',
  <div>Feature not available</div>
);

// Use the wrapped component
<GatedPremiumComponent />
```

## Feature Flag Types

### 1. Global Flags
Simple on/off flags that apply to all users.

```tsx
{
  key: 'new-ui',
  name: 'New UI',
  flag_type: 'global',
  enabled: true
}
```

### 2. User-Based Flags
Flags that are enabled for specific users.

```tsx
{
  key: 'beta-features',
  name: 'Beta Features',
  flag_type: 'user',
  enabled: true,
  user_ids: [1, 2, 3]
}
```

### 3. Role-Based Flags
Flags that are enabled for users with specific roles.

```tsx
{
  key: 'admin-panel',
  name: 'Admin Panel',
  flag_type: 'role',
  enabled: true,
  role_ids: [1] // Admin role
}
```

### 4. Percentage Rollout
Gradual rollout to a percentage of users.

```tsx
{
  key: 'new-calculator',
  name: 'New Calculator',
  flag_type: 'percentage',
  enabled: true,
  rollout_percentage: 25 // 25% of users
}
```

## Admin Features

### Feature Toggle Switches
- Quick enable/disable with a single click
- Visual feedback with InputSwitch component
- Immediate effect on all users

### Feature Preview Mode
- Test feature flags as different users
- See which features would be enabled for a specific user
- Useful for debugging and testing

### Feature Rollout Scheduling
- Schedule gradual rollout over time
- Set start and end dates
- Configure increment percentage and interval
- Automatic progression from 0% to target percentage

### Feature Usage Analytics
- Track total feature checks
- Monitor enabled vs disabled checks
- View unique user count
- See last check timestamp
- Visualize data with charts

### Feature Dependency Management
- Define dependencies between features
- Ensure required features are enabled first
- Prevent circular dependencies
- Visual dependency graph

## API Endpoints

### Check Single Feature
```
POST /api/v1/feature-flags/check
{
  "key": "feature-key",
  "user_id": 123
}
```

### Check Multiple Features
```
POST /api/v1/feature-flags/check-bulk
{
  "keys": ["feature-a", "feature-b"],
  "user_id": 123
}
```

### List All Features
```
GET /api/v1/feature-flags/
```

### Create Feature
```
POST /api/v1/feature-flags/
{
  "key": "new-feature",
  "name": "New Feature",
  "description": "Description",
  "enabled": false,
  "flag_type": "global"
}
```

### Update Feature
```
PUT /api/v1/feature-flags/{id}
{
  "enabled": true
}
```

### Delete Feature
```
DELETE /api/v1/feature-flags/{id}
```

## Best Practices

### 1. Naming Conventions
- Use kebab-case for feature keys: `solar-calculator-advanced`
- Use descriptive names: "Advanced Solar Calculator"
- Include module prefix: `solar-`, `heat-pump-`, `pdf-`

### 2. Feature Organization
- Group related features together
- Use consistent naming patterns
- Document feature purpose and dependencies

### 3. Rollout Strategy
- Start with small percentage (5-10%)
- Monitor for issues before increasing
- Use scheduled rollouts for gradual deployment
- Have rollback plan ready

### 4. Testing
- Test features in preview mode before enabling
- Verify with different user roles
- Check dependency chains
- Monitor usage analytics

### 5. Performance
- Preload frequently checked features
- Use bulk checks for multiple features
- Enable auto-refresh for dynamic features
- Cache feature states appropriately

### 6. Security
- Restrict admin access to feature management
- Audit feature flag changes
- Validate user permissions
- Log feature access attempts

## Examples

### Example 1: Simple Feature Gate
```tsx
function MyComponent() {
  const { isEnabled } = useFeatureToggle('new-feature');
  
  return (
    <div>
      {isEnabled && <NewFeature />}
    </div>
  );
}
```

### Example 2: Multiple Features
```tsx
function Dashboard() {
  const { isFeatureEnabled } = useFeatureToggles([
    'advanced-charts',
    'export-pdf',
    'real-time-updates'
  ]);
  
  return (
    <div>
      {isFeatureEnabled('advanced-charts') && <AdvancedCharts />}
      {isFeatureEnabled('export-pdf') && <ExportButton />}
      {isFeatureEnabled('real-time-updates') && <LiveUpdates />}
    </div>
  );
}
```

### Example 3: Feature Gate with Fallback
```tsx
function PremiumSection() {
  return (
    <FeatureGate
      featureKey="premium-features"
      fallback={<UpgradePrompt />}
    >
      <PremiumContent />
    </FeatureGate>
  );
}
```

### Example 4: HOC Pattern
```tsx
const PremiumChart = withFeatureToggle(
  AdvancedChart,
  'premium-charts',
  <BasicChart />
);

function Dashboard() {
  return <PremiumChart data={chartData} />;
}
```

### Example 5: Context Usage
```tsx
function FeatureList() {
  const { features, refreshFeatures } = useFeatureToggleContext();
  
  return (
    <div>
      <button onClick={refreshFeatures}>Refresh</button>
      {Object.entries(features).map(([key, enabled]) => (
        <div key={key}>
          {key}: {enabled ? 'Enabled' : 'Disabled'}
        </div>
      ))}
    </div>
  );
}
```

## Troubleshooting

### Feature Not Updating
- Check if auto-refresh is enabled
- Manually call `refresh()` method
- Verify backend API is responding
- Check browser console for errors

### Preview Mode Not Working
- Ensure user ID is valid
- Check user has required roles
- Verify feature flag configuration
- Test with different users

### Performance Issues
- Reduce refresh interval
- Preload only necessary features
- Use bulk checks instead of individual
- Enable caching in provider

### Dependency Conflicts
- Review dependency chain
- Check for circular dependencies
- Verify all required features exist
- Test dependency resolution

## Migration Guide

### From Hardcoded Flags
```tsx
// Before
const ENABLE_NEW_FEATURE = true;

if (ENABLE_NEW_FEATURE) {
  // Feature code
}

// After
const { isEnabled } = useFeatureToggle('new-feature');

if (isEnabled) {
  // Feature code
}
```

### From Environment Variables
```tsx
// Before
if (process.env.REACT_APP_ENABLE_FEATURE === 'true') {
  // Feature code
}

// After
const { isEnabled } = useFeatureToggle('feature-name');

if (isEnabled) {
  // Feature code
}
```

## Support

For issues or questions:
1. Check the demo component: `src/examples/FeatureToggleDemo.tsx`
2. Review API documentation: `backend/docs/FEATURE_FLAGS_GUIDE.md`
3. Check backend logs for errors
4. Contact development team

## Version History

- **v1.0.0** - Initial release with basic feature toggle functionality
- **v1.1.0** - Added preview mode and rollout scheduling
- **v1.2.0** - Added usage analytics and dependency management
- **v1.3.0** - Performance improvements and caching
