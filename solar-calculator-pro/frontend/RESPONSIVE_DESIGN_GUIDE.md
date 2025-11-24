# Responsive Design Guide

## Overview

This guide covers the responsive design system implemented for the Solar Calculator Pro application. The system provides mobile-first, adaptive layouts that work seamlessly across all device sizes.

## Breakpoints

The responsive system uses the following breakpoints:

| Breakpoint | Min Width | Device Type |
|------------|-----------|-------------|
| xs         | 320px     | Extra small phones |
| sm         | 576px     | Small phones (landscape) |
| md         | 768px     | Tablets |
| lg         | 992px     | Desktops |
| xl         | 1200px    | Large desktops |
| xxl        | 1400px    | Extra large desktops |

## Core Components

### 1. ResponsiveContainer

Provides consistent max-width and padding across breakpoints.

```tsx
import { ResponsiveContainer } from '@/components/responsive';

<ResponsiveContainer>
  <YourContent />
</ResponsiveContainer>

// Fluid container (full width)
<ResponsiveContainer fluid>
  <YourContent />
</ResponsiveContainer>
```

### 2. ResponsiveGrid

Automatically adjusts columns based on screen size.

```tsx
import { ResponsiveGrid } from '@/components/responsive';

<ResponsiveGrid 
  cols={{ xs: 1, sm: 2, md: 3, lg: 4 }}
  gap="md"
>
  <Item1 />
  <Item2 />
  <Item3 />
</ResponsiveGrid>
```

### 3. ResponsiveImage

Optimized images that scale properly on all devices.

```tsx
import { ResponsiveImage } from '@/components/responsive';

<ResponsiveImage
  src="/path/to/image.jpg"
  alt="Description"
  fit="cover"
  loading="lazy"
/>
```

### 4. MobileNavigation

Touch-friendly navigation for mobile devices.

```tsx
import { MobileNavigation } from '@/components/responsive';

const navItems = [
  { label: 'Dashboard', onClick: () => navigate('/dashboard'), active: true },
  { label: 'Projects', onClick: () => navigate('/projects') },
];

<MobileNavigation items={navItems} />
```

### 5. TouchGestures

Gesture detection for mobile interactions.

```tsx
import { TouchGestures } from '@/components/responsive';

<TouchGestures
  onSwipeLeft={() => console.log('Swiped left')}
  onSwipeRight={() => console.log('Swiped right')}
  onPinch={(scale) => console.log('Pinch scale:', scale)}
  onDoubleTap={() => console.log('Double tapped')}
>
  <YourContent />
</TouchGestures>
```

### 6. AdaptiveCard

Cards that adjust layout based on screen size.

```tsx
import { AdaptiveCard } from '@/components/responsive';

<AdaptiveCard
  title="Card Title"
  subtitle="Card Subtitle"
  mobileLayout="stack"
>
  <CardContent />
</AdaptiveCard>
```

### 7. ResponsiveTable

Tables that switch to card layout on mobile.

```tsx
import { ResponsiveTable } from '@/components/responsive';

const columns = [
  { field: 'name', header: 'Name' },
  { field: 'price', header: 'Price', hideOnMobile: true },
  { field: 'stock', header: 'Stock', hideOnTablet: true },
];

const mobileCardTemplate = (item) => (
  <div>
    <h3>{item.name}</h3>
    <p>Price: ${item.price}</p>
  </div>
);

<ResponsiveTable
  data={products}
  columns={columns}
  mobileCardTemplate={mobileCardTemplate}
/>
```

## Custom Hooks

### useResponsive

Get current responsive state and breakpoint information.

```tsx
import { useResponsive } from '@/hooks/useResponsive';

const MyComponent = () => {
  const responsive = useResponsive();

  return (
    <div>
      <p>Width: {responsive.width}px</p>
      <p>Is Mobile: {responsive.isMobile ? 'Yes' : 'No'}</p>
      <p>Is Tablet: {responsive.isTablet ? 'Yes' : 'No'}</p>
      <p>Is Desktop: {responsive.isDesktop ? 'Yes' : 'No'}</p>
      <p>Orientation: {responsive.orientation}</p>
    </div>
  );
};
```

### useBreakpoint

Check if current viewport matches a specific breakpoint.

```tsx
import { useBreakpoint } from '@/hooks/useResponsive';

const MyComponent = () => {
  const isLargeScreen = useBreakpoint('lg');

  return (
    <div>
      {isLargeScreen ? <DesktopView /> : <MobileView />}
    </div>
  );
};
```

### useDeviceType

Get simplified device type.

```tsx
import { useDeviceType } from '@/hooks/useResponsive';

const MyComponent = () => {
  const deviceType = useDeviceType(); // 'mobile' | 'tablet' | 'desktop'

  return <div>Device: {deviceType}</div>;
};
```

## CSS Utilities

### Grid Classes

```css
/* Mobile-first grid */
.grid-cols-1  /* 1 column */
.grid-cols-2  /* 2 columns */
.grid-cols-3  /* 3 columns */
.grid-cols-4  /* 4 columns */

/* Responsive grid */
.sm:grid-cols-2  /* 2 columns on small screens and up */
.md:grid-cols-3  /* 3 columns on medium screens and up */
.lg:grid-cols-4  /* 4 columns on large screens and up */
```

### Visibility Classes

```css
.hide-mobile   /* Hidden on mobile */
.show-mobile   /* Visible only on mobile */
.hide-tablet   /* Hidden on tablet */
.show-tablet   /* Visible only on tablet */
.hide-desktop  /* Hidden on desktop */
.show-desktop  /* Visible only on desktop */
.hide-print    /* Hidden when printing */
```

### Spacing Classes

```css
.p-responsive   /* Responsive padding */
.px-responsive  /* Responsive horizontal padding */
.py-responsive  /* Responsive vertical padding */
.m-responsive   /* Responsive margin */
.mx-responsive  /* Responsive horizontal margin */
.my-responsive  /* Responsive vertical margin */
```

### Touch-Friendly Classes

```css
.touch-target  /* Minimum 44x44px touch target */
```

## Best Practices

### 1. Mobile-First Approach

Always design for mobile first, then enhance for larger screens:

```tsx
// Good
<div className="grid-cols-1 md:grid-cols-2 lg:grid-cols-3">

// Avoid
<div className="grid-cols-3 md:grid-cols-2 sm:grid-cols-1">
```

### 2. Touch Targets

Ensure all interactive elements are at least 44x44px:

```tsx
<Button className="touch-target" />
```

### 3. Responsive Images

Always use responsive images with proper sizing:

```tsx
<ResponsiveImage
  src="/image.jpg"
  alt="Description"
  loading="lazy"
  srcSet="/image-small.jpg 400w, /image-medium.jpg 800w, /image-large.jpg 1200w"
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
/>
```

### 4. Conditional Rendering

Use hooks for conditional rendering based on device:

```tsx
const { isMobile } = useResponsive();

return (
  <>
    {isMobile ? <MobileView /> : <DesktopView />}
  </>
);
```

### 5. Flexible Layouts

Use flexbox and grid for flexible layouts:

```tsx
<div className="flex-responsive">
  <Item1 />
  <Item2 />
  <Item3 />
</div>
```

## Testing Responsive Design

### Browser DevTools

1. Open Chrome DevTools (F12)
2. Click the device toolbar icon (Ctrl+Shift+M)
3. Select different devices or set custom dimensions
4. Test all breakpoints

### Real Device Testing

Test on actual devices:
- iPhone (various models)
- iPad
- Android phones and tablets
- Desktop browsers at different sizes

### Automated Testing

```tsx
import { render, screen } from '@testing-library/react';
import { useResponsive } from '@/hooks/useResponsive';

// Mock window.innerWidth
Object.defineProperty(window, 'innerWidth', {
  writable: true,
  configurable: true,
  value: 375, // Mobile width
});

test('renders mobile layout', () => {
  render(<MyComponent />);
  // Test mobile-specific elements
});
```

## Performance Considerations

### 1. Lazy Loading

Use lazy loading for images and components:

```tsx
<ResponsiveImage loading="lazy" />
```

### 2. Code Splitting

Split code by route and device type:

```tsx
const MobileComponent = lazy(() => import('./MobileComponent'));
const DesktopComponent = lazy(() => import('./DesktopComponent'));
```

### 3. Optimize Images

- Use appropriate image formats (WebP, AVIF)
- Provide multiple sizes with srcSet
- Compress images properly

## Accessibility

### 1. Keyboard Navigation

Ensure all interactive elements are keyboard accessible:

```tsx
<button
  onClick={handleClick}
  onKeyPress={(e) => e.key === 'Enter' && handleClick()}
  tabIndex={0}
>
  Click me
</button>
```

### 2. Screen Readers

Provide proper ARIA labels:

```tsx
<button aria-label="Close menu">
  <CloseIcon />
</button>
```

### 3. Focus Management

Manage focus for mobile navigation:

```tsx
useEffect(() => {
  if (isMenuOpen) {
    menuRef.current?.focus();
  }
}, [isMenuOpen]);
```

## Common Patterns

### Responsive Navigation

```tsx
const Navigation = () => {
  const { isMobile } = useResponsive();

  return isMobile ? (
    <MobileNavigation items={navItems} />
  ) : (
    <DesktopNavigation items={navItems} />
  );
};
```

### Responsive Forms

```tsx
<ResponsiveGrid cols={{ xs: 1, md: 2 }}>
  <FormField label="Name" />
  <FormField label="Email" />
  <FormField label="Phone" />
  <FormField label="Company" />
</ResponsiveGrid>
```

### Responsive Modals

```tsx
const { isMobile } = useResponsive();

<Dialog
  visible={visible}
  onHide={onHide}
  style={{ width: isMobile ? '95vw' : '50vw' }}
  position={isMobile ? 'bottom' : 'center'}
>
  <DialogContent />
</Dialog>
```

## Troubleshooting

### Issue: Layout breaks on specific device

**Solution**: Test at that specific breakpoint and adjust CSS accordingly.

### Issue: Touch targets too small

**Solution**: Add `touch-target` class to interactive elements.

### Issue: Images not scaling properly

**Solution**: Use `ResponsiveImage` component with proper `fit` prop.

### Issue: Horizontal scrolling on mobile

**Solution**: Ensure all containers have `max-width: 100%` and no fixed widths.

## Resources

- [MDN Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [Web.dev Responsive Design](https://web.dev/responsive-web-design-basics/)
- [PrimeReact Responsive](https://primereact.org/responsive/)
