# Layout Components - Quick Reference

## Import

```tsx
import {
  MainLayout,
  Header,
  Sidebar,
  Footer,
  MobileDrawer,
} from '@/components/layout';
```

## MainLayout

```tsx
// Wrap authenticated routes
<Route element={<MainLayout />}>
  <Route path="/dashboard" element={<Dashboard />} />
</Route>
```

## Sidebar State

```tsx
const { sidebarVisible, setSidebarVisible } = useUIStore();

// Toggle
setSidebarVisible(!sidebarVisible);

// Open
setSidebarVisible(true);

// Close
setSidebarVisible(false);
```

## Add Menu Item

```tsx
// In Sidebar.tsx
{
  label: 'My Page',
  icon: 'pi pi-star',
  command: () => navigate('/my-page'),
  className: location.pathname === '/my-page' ? 'active-menu-item' : '',
}
```

## User Menu

```tsx
const { user, logout } = useAuthStore();

// Access user
console.log(user?.username);

// Logout
logout();
navigate('/login');
```

## Responsive Breakpoints

- **Desktop**: > 992px (static sidebar)
- **Tablet**: 768px - 992px (drawer)
- **Mobile**: < 768px (drawer, compact)

## CSS Variables

```css
--surface-card
--surface-border
--surface-ground
--text-color
--text-color-secondary
--primary-color
```

## Common Tasks

### Hide Element on Mobile
```css
@media (max-width: 768px) {
  .my-element {
    display: none;
  }
}
```

### Add Footer Link
```tsx
<button
  className="footer-link"
  onClick={() => navigate('/my-page')}
>
  My Link
</button>
```

### Change App Title
```tsx
// In Header.tsx
<span className="app-title">Your App Name</span>
```

## File Structure

```
components/layout/
├── MainLayout.tsx       # Main wrapper
├── MainLayout.css
├── Header.tsx          # Top header
├── Header.css
├── Sidebar.tsx         # Navigation menu
├── Sidebar.css
├── Footer.tsx          # Bottom footer
├── Footer.css
├── MobileDrawer.tsx    # Mobile drawer
├── MobileDrawer.css
└── index.ts            # Exports
```

## Key Features

✅ Responsive design
✅ Mobile drawer navigation
✅ User menu with avatar
✅ Active route highlighting
✅ Search bar (desktop)
✅ Notifications badge
✅ Version display
✅ Keyboard accessible
✅ Print-friendly

## Testing Checklist

- [ ] Desktop sidebar works
- [ ] Mobile drawer opens/closes
- [ ] User menu functions
- [ ] Active routes highlight
- [ ] Responsive breakpoints work
- [ ] Keyboard navigation works
