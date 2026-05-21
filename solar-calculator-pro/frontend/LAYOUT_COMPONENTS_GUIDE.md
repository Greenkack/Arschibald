# Layout Components Guide

## Overview

This guide documents the layout components implemented for the Solar Calculator Pro application. These components provide a responsive, professional layout structure with navigation, header, footer, and mobile support.

## Components

### 1. MainLayout

The main application layout that wraps authenticated pages.

**Features:**
- Responsive design with desktop sidebar and mobile drawer
- Integrated header, content area, and footer
- Automatic layout switching based on screen size
- Print-friendly styles

**Usage:**
```tsx
import { MainLayout } from '@/components/layout';

// In routes configuration
<Route element={<MainLayout />}>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/solar" element={<SolarCalculator />} />
  {/* Other routes */}
</Route>
```

**Responsive Breakpoints:**
- Desktop: > 992px (sidebar visible)
- Tablet: 768px - 992px (drawer navigation)
- Mobile: < 768px (drawer navigation, compact header)

---

### 2. Header

Responsive header with user menu, search, and notifications.

**Features:**
- Mobile menu toggle button
- Application logo and title
- Global search bar (desktop only)
- Notification bell with badge
- Help button
- User menu with avatar and dropdown

**User Menu Items:**
- Profile
- Settings
- Logout

**Responsive Behavior:**
- Desktop: Full header with search bar
- Tablet: Compact header, search hidden
- Mobile: Minimal header, only essential buttons

---

### 3. Sidebar

Navigation sidebar with hierarchical menu structure.

**Features:**
- Organized menu sections (Main, Calculators, Business, Tools, System)
- Active route highlighting
- Icon support for all menu items
- Version information in footer
- Smooth scrolling for long menus

**Menu Structure:**
```
Main
  - Dashboard

Calculators
  - Solar Calculator
  - Heat Pump

Business
  - Price Matrix
  - Products
  - CRM

Tools
  - PDF Generator
  - 3D Visualization

System
  - Admin Panel
  - Settings
```

**Customization:**
Edit the `menuItems` array in `Sidebar.tsx` to add/remove menu items.

---

### 4. Footer

Application footer with copyright, links, and build information.

**Features:**
- Copyright notice with dynamic year
- Quick links (About, Privacy, Terms, Help)
- Build version display
- Responsive layout

**Responsive Behavior:**
- Desktop: Horizontal layout with three sections
- Tablet/Mobile: Vertical stacked layout

---

### 5. MobileDrawer

Mobile-responsive drawer navigation using PrimeReact Sidebar.

**Features:**
- Slide-in animation from left
- Modal overlay
- Touch-friendly close gestures
- Automatic visibility management
- Contains full Sidebar component

**Behavior:**
- Visible only on screens < 993px
- Controlled by `sidebarVisible` state in UIStore
- Closes on route navigation
- Closes on overlay click

---

## State Management

### UIStore

The layout components use the `useUIStore` hook for state management:

```tsx
interface UIState {
  sidebarVisible: boolean;
  setSidebarVisible: (visible: boolean) => void;
  // ... other UI state
}
```

**Usage:**
```tsx
const { sidebarVisible, setSidebarVisible } = useUIStore();

// Toggle sidebar
setSidebarVisible(!sidebarVisible);
```

### AuthStore

The Header component uses the `useAuthStore` hook for user information:

```tsx
interface AuthState {
  user: User | null;
  logout: () => void;
  // ... other auth state
}
```

---

## Styling

### CSS Variables

The layout components use CSS custom properties for theming:

```css
--surface-card: Background color for cards/surfaces
--surface-border: Border color
--surface-ground: Page background
--surface-hover: Hover state background
--text-color: Primary text color
--text-color-secondary: Secondary text color
--primary-color: Primary brand color
--primary-color-text: Text color on primary background
```

### Responsive Design

All components follow mobile-first responsive design principles:

1. **Mobile (< 576px)**
   - Minimal padding
   - Compact spacing
   - Essential features only

2. **Tablet (576px - 992px)**
   - Moderate padding
   - Drawer navigation
   - Some features hidden

3. **Desktop (> 992px)**
   - Full padding
   - Static sidebar
   - All features visible

---

## Accessibility

### Keyboard Navigation

- All interactive elements are keyboard accessible
- Proper focus management
- ARIA labels on icon-only buttons

### Screen Readers

- Semantic HTML structure
- ARIA labels for icon buttons
- Proper heading hierarchy

### Color Contrast

- All text meets WCAG AA standards
- Focus indicators visible
- High contrast mode support

---

## Customization

### Adding Menu Items

Edit `Sidebar.tsx`:

```tsx
const menuItems: MenuItem[] = [
  {
    label: 'My Section',
    items: [
      {
        label: 'My Page',
        icon: 'pi pi-star',
        command: () => navigate('/my-page'),
        className: location.pathname === '/my-page' ? 'active-menu-item' : '',
      },
    ],
  },
];
```

### Changing Header Logo

Edit `Header.tsx`:

```tsx
<div className="app-logo">
  <img src="/path/to/logo.png" alt="Logo" />
  <span className="app-title">Your App Name</span>
</div>
```

### Customizing Footer Links

Edit `Footer.tsx`:

```tsx
<button
  className="footer-link"
  onClick={() => navigate('/your-page')}
>
  Your Link
</button>
```

---

## Performance Considerations

### Code Splitting

Layout components are loaded with the main bundle since they're used on every page.

### CSS Optimization

- Minimal CSS with efficient selectors
- CSS custom properties for theming
- No inline styles (except dynamic values)

### State Management

- Zustand for lightweight state management
- Persistent state for user preferences
- Minimal re-renders

---

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Android

---

## Testing

### Manual Testing Checklist

- [ ] Desktop sidebar navigation works
- [ ] Mobile drawer opens/closes correctly
- [ ] Header user menu functions properly
- [ ] Footer links navigate correctly
- [ ] Active route highlighting works
- [ ] Responsive breakpoints trigger correctly
- [ ] Keyboard navigation works
- [ ] Screen reader announces properly

### Automated Testing

Create tests for:
- Component rendering
- Navigation functionality
- Responsive behavior
- State management
- Accessibility

---

## Troubleshooting

### Sidebar Not Showing

Check:
1. `sidebarVisible` state in UIStore
2. Screen width (desktop vs mobile)
3. CSS z-index conflicts

### Menu Items Not Highlighting

Check:
1. Route path matches exactly
2. `location.pathname` is correct
3. `active-menu-item` class is applied

### Mobile Drawer Not Closing

Check:
1. `setSidebarVisible(false)` is called
2. PrimeReact Sidebar props are correct
3. No JavaScript errors in console

---

## Future Enhancements

Potential improvements:
- [ ] Breadcrumb navigation
- [ ] Collapsible sidebar on desktop
- [ ] Customizable menu order
- [ ] User-specific menu items
- [ ] Notification center
- [ ] Quick actions menu
- [ ] Theme switcher in header
- [ ] Multi-language support

---

## Related Documentation

- [PrimeReact Documentation](https://primereact.org/)
- [React Router Documentation](https://reactrouter.com/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)

---

## Support

For issues or questions:
1. Check this documentation
2. Review component source code
3. Check PrimeReact documentation
4. Contact development team
