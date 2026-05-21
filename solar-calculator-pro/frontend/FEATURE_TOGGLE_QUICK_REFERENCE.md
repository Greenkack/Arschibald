# Feature Toggle UI - Quick Reference

## Quick Start

### 1. Setup Provider
```tsx
import { FeatureToggleProvider } from './providers/FeatureToggleProvider';

<FeatureToggleProvider userId={user.id} preloadKeys={['feature-a']}>
  <App />
</FeatureToggleProvider>
```

### 2. Check Single Feature
```tsx
import { useFeatureToggle } from './hooks/useFeatureToggle';

const { isEnabled } = useFeatureToggle('my-feature');
```

### 3. Check Multiple Features
```tsx
import { useFeatureToggles } from './hooks/useFeatureToggle';

const { isFeatureEnabled } = useFeatureToggles(['feature-a', 'feature-b']);
```

### 4. Use Feature Gate
```tsx
import { FeatureGate } from './providers/FeatureToggleProvider';

<FeatureGate featureKey="premium" fallback={<Upgrade />}>
  <PremiumContent />
</FeatureGate>
```

## Common Patterns

### Conditional Rendering
```tsx
{isEnabled && <Component />}
```

### Ternary Operator
```tsx
{isEnabled ? <NewUI /> : <OldUI />}
```

### Early Return
```tsx
if (!isEnabled) return null;
return <Component />;
```

### HOC Wrapper
```tsx
const Wrapped = withFeatureToggle(Component, 'feature-key', <Fallback />);
```

## Admin Interface

### Access
```
/admin/feature-toggles
```

### Quick Actions
- **Toggle**: Click switch to enable/disable
- **Edit**: Click pencil icon
- **Analytics**: Click chart icon
- **Schedule**: Click calendar icon
- **Delete**: Click trash icon

## Flag Types

| Type | Description | Use Case |
|------|-------------|----------|
| `global` | All users | Simple on/off |
| `user` | Specific users | Beta testing |
| `role` | User roles | Permission-based |
| `percentage` | Gradual rollout | Canary deployment |

## API Endpoints

```
POST   /api/v1/feature-flags/check
POST   /api/v1/feature-flags/check-bulk
GET    /api/v1/feature-flags/
POST   /api/v1/feature-flags/
PUT    /api/v1/feature-flags/{id}
DELETE /api/v1/feature-flags/{id}
```

## Hook Options

```tsx
useFeatureToggle('key', {
  userId: 123,           // Optional user ID
  autoRefresh: true,     // Auto-refresh flag
  refreshInterval: 60000 // Refresh every 60s
})
```

## Provider Props

```tsx
<FeatureToggleProvider
  userId={123}                    // Current user ID
  preloadKeys={['a', 'b']}       // Preload features
  autoRefresh={true}              // Enable auto-refresh
  refreshInterval={300000}        // Refresh interval (ms)
>
```

## Common Issues

### Feature Not Updating
```tsx
const { refresh } = useFeatureToggle('key');
refresh(); // Manual refresh
```

### Check Multiple Features
```tsx
const { features } = useFeatureToggles(['a', 'b', 'c']);
// More efficient than multiple useFeatureToggle calls
```

### Performance
```tsx
// ✅ Good: Preload in provider
<FeatureToggleProvider preloadKeys={['a', 'b']} />

// ❌ Bad: Multiple individual checks
useFeatureToggle('a');
useFeatureToggle('b');
```

## Best Practices

1. **Naming**: Use kebab-case (`solar-calculator-advanced`)
2. **Preload**: Preload frequently used features
3. **Bulk**: Use bulk checks for multiple features
4. **Cache**: Enable auto-refresh for dynamic features
5. **Fallback**: Always provide fallback UI
6. **Test**: Use preview mode before enabling

## Keyboard Shortcuts (Admin)

- `Ctrl+N`: Create new feature
- `Ctrl+R`: Refresh list
- `Ctrl+P`: Open preview mode
- `Esc`: Close dialogs

## Examples

### Basic Usage
```tsx
const { isEnabled } = useFeatureToggle('new-ui');
return isEnabled ? <NewUI /> : <OldUI />;
```

### With Loading
```tsx
const { isEnabled, isLoading } = useFeatureToggle('feature');
if (isLoading) return <Spinner />;
return isEnabled ? <Feature /> : null;
```

### Multiple Features
```tsx
const { isFeatureEnabled } = useFeatureToggles(['a', 'b', 'c']);
return (
  <>
    {isFeatureEnabled('a') && <A />}
    {isFeatureEnabled('b') && <B />}
    {isFeatureEnabled('c') && <C />}
  </>
);
```

### Feature Gate
```tsx
<FeatureGate featureKey="premium" fallback={<Locked />}>
  <Premium />
</FeatureGate>
```

### Context
```tsx
const { isFeatureEnabled } = useFeatureToggleContext();
return isFeatureEnabled('feature') ? <On /> : <Off />;
```

## Cheat Sheet

| Task | Code |
|------|------|
| Check feature | `useFeatureToggle('key')` |
| Check multiple | `useFeatureToggles(['a', 'b'])` |
| Feature gate | `<FeatureGate featureKey="key">` |
| HOC wrapper | `withFeatureToggle(Comp, 'key')` |
| Context | `useFeatureToggleContext()` |
| Refresh | `refresh()` |
| Manual check | `isFeatureEnabled('key')` |

## Support

- **Demo**: `/examples/feature-toggle-demo`
- **Docs**: `FEATURE_TOGGLE_UI_GUIDE.md`
- **Backend**: `backend/docs/FEATURE_FLAGS_GUIDE.md`
