# Responsive Design Quick Reference

## Breakpoints

```
xs:  320px  (Extra small phones)
sm:  576px  (Small phones landscape)
md:  768px  (Tablets)
lg:  992px  (Desktops)
xl:  1200px (Large desktops)
xxl: 1400px (Extra large desktops)
```

## Components

### ResponsiveContainer
```tsx
<ResponsiveContainer>...</ResponsiveContainer>
<ResponsiveContainer fluid>...</ResponsiveContainer>
```

### ResponsiveGrid
```tsx
<ResponsiveGrid cols={{ xs: 1, sm: 2, md: 3, lg: 4 }}>
  ...
</ResponsiveGrid>
```

### ResponsiveImage
```tsx
<ResponsiveImage src="..." alt="..." fit="cover|contain|auto" />
```

### MobileNavigation
```tsx
<MobileNavigation items={[
  { label: 'Home', onClick: () => {} }
]} />
```

### TouchGestures
```tsx
<TouchGestures
  onSwipeLeft={() => {}}
  onSwipeRight={() => {}}
  onPinch={(scale) => {}}
>
  ...
</TouchGestures>
```

### AdaptiveCard
```tsx
<AdaptiveCard title="..." mobileLayout="stack|compact">
  ...
</AdaptiveCard>
```

### ResponsiveTable
```tsx
<ResponsiveTable
  data={data}
  columns={columns}
  mobileCardTemplate={(item) => <div>...</div>}
/>
```

## Hooks

### useResponsive
```tsx
const { 
  isMobile, 
  isTablet, 
  isDesktop, 
  width, 
  height, 
  orientation 
} = useResponsive();
```

### useBreakpoint
```tsx
const isLarge = useBreakpoint('lg');
```

### useDeviceType
```tsx
const deviceType = useDeviceType(); // 'mobile' | 'tablet' | 'desktop'
```

## CSS Classes

### Grid
```css
.grid-cols-1, .grid-cols-2, .grid-cols-3, .grid-cols-4
.sm:grid-cols-2, .md:grid-cols-3, .lg:grid-cols-4
```

### Visibility
```css
.hide-mobile, .show-mobile
.hide-tablet, .show-tablet
.hide-desktop, .show-desktop
.hide-print
```

### Spacing
```css
.p-responsive, .px-responsive, .py-responsive
.m-responsive, .mx-responsive, .my-responsive
```

### Touch
```css
.touch-target  /* Min 44x44px */
```

### Flex
```css
.flex-responsive
.flex-col-mobile
```

## Common Patterns

### Conditional Rendering
```tsx
const { isMobile } = useResponsive();
return isMobile ? <MobileView /> : <DesktopView />;
```

### Responsive Form
```tsx
<ResponsiveGrid cols={{ xs: 1, md: 2 }}>
  <FormField />
  <FormField />
</ResponsiveGrid>
```

### Responsive Modal
```tsx
const { isMobile } = useResponsive();
<Dialog 
  style={{ width: isMobile ? '95vw' : '50vw' }}
  position={isMobile ? 'bottom' : 'center'}
/>
```

### Responsive Navigation
```tsx
{isMobile ? (
  <MobileNavigation items={items} />
) : (
  <DesktopNavigation items={items} />
)}
```

## Best Practices

1. **Mobile-First**: Design for mobile, enhance for desktop
2. **Touch Targets**: Minimum 44x44px for interactive elements
3. **Lazy Loading**: Use `loading="lazy"` for images
4. **Flexible Layouts**: Use flexbox/grid instead of fixed widths
5. **Test Real Devices**: Don't rely only on browser DevTools

## Testing

```tsx
// Mock window size
Object.defineProperty(window, 'innerWidth', {
  value: 375 // Mobile width
});

// Test component
render(<MyComponent />);
```

## Performance Tips

- Use `ResponsiveImage` with `srcSet` and `sizes`
- Lazy load off-screen components
- Code split by device type
- Optimize images (WebP, compression)
- Use CSS containment for complex layouts

## Accessibility

- Ensure keyboard navigation works
- Provide ARIA labels
- Manage focus for modals/menus
- Test with screen readers
- Support reduced motion preferences
