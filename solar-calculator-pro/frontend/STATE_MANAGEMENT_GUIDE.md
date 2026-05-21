# State Management Guide

## Overview

This application uses **Zustand** for state management, providing a simple, lightweight, and performant solution for managing global application state. Zustand is configured with persistence middleware to save state to localStorage.

## Architecture

### Store Structure

```
src/store/
├── authStore.ts      # Authentication state
├── uiStore.ts        # UI/UX state
├── projectStore.ts   # Project data state
└── index.ts          # Central exports
```

## Stores

### 1. Auth Store (`authStore.ts`)

Manages user authentication state.

#### State

```typescript
interface AuthState {
  user: User | null;              // Current user object
  isAuthenticated: boolean;       // Authentication status
  isLoading: boolean;             // Loading state for auth operations
  error: string | null;           // Error message if any
}
```

#### Actions

- `setUser(user: User | null)` - Set the current user
- `setLoading(loading: boolean)` - Set loading state
- `setError(error: string | null)` - Set error message
- `logout()` - Clear user and authentication state

#### Usage Example

```typescript
import { useAuthStore } from '@/store';

function MyComponent() {
  const { user, isAuthenticated, setUser, logout } = useAuthStore();

  const handleLogin = async (credentials) => {
    const user = await loginAPI(credentials);
    setUser(user);
  };

  return (
    <div>
      {isAuthenticated ? (
        <>
          <p>Welcome, {user?.username}!</p>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  );
}
```

#### Persistence

The auth store persists the following to localStorage:
- `user` - User object
- `isAuthenticated` - Authentication status

Storage key: `auth-storage`

---

### 2. UI Store (`uiStore.ts`)

Manages global UI state including sidebar, theme, loading states, and notifications.

#### State

```typescript
interface UIState {
  // Sidebar
  sidebarCollapsed: boolean;      // Sidebar collapsed state
  sidebarVisible: boolean;        // Sidebar visibility
  
  // Theme
  theme: 'light' | 'dark' | 'auto'; // Current theme
  
  // Loading
  globalLoading: boolean;         // Global loading overlay
  loadingMessage: string | null;  // Loading message
  
  // Notifications
  notifications: Notification[];  // Active notifications
}
```

#### Actions

- `toggleSidebar()` - Toggle sidebar collapsed state
- `setSidebarCollapsed(collapsed: boolean)` - Set sidebar collapsed state
- `setSidebarVisible(visible: boolean)` - Set sidebar visibility
- `setTheme(theme: 'light' | 'dark' | 'auto')` - Set application theme
- `setGlobalLoading(loading: boolean, message?: string)` - Set global loading state
- `addNotification(notification)` - Add a notification (auto-removes after 5s)
- `removeNotification(id: string)` - Remove a specific notification
- `clearNotifications()` - Clear all notifications

#### Usage Example

```typescript
import { useUIStore } from '@/store';

function MyComponent() {
  const { 
    theme, 
    setTheme, 
    addNotification,
    sidebarCollapsed,
    toggleSidebar 
  } = useUIStore();

  const handleSave = async () => {
    try {
      await saveData();
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Data saved successfully!'
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to save data'
      });
    }
  };

  return (
    <div>
      <button onClick={toggleSidebar}>
        {sidebarCollapsed ? 'Expand' : 'Collapse'} Sidebar
      </button>
      <select value={theme} onChange={(e) => setTheme(e.target.value)}>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
        <option value="auto">Auto</option>
      </select>
    </div>
  );
}
```

#### Notifications

Notifications are automatically removed after 5 seconds. Each notification has:

```typescript
interface Notification {
  id: string;                              // Auto-generated
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: number;                       // Auto-generated
}
```

#### Persistence

The UI store persists the following to localStorage:
- `sidebarCollapsed` - Sidebar state
- `theme` - Theme preference

Storage key: `ui-storage`

---

### 3. Project Store (`projectStore.ts`)

Manages project data and operations.

#### State

```typescript
interface ProjectState {
  projects: Project[];            // List of all projects
  currentProject: Project | null; // Currently selected project
  isLoading: boolean;             // Loading state
  error: string | null;           // Error message
}

interface Project {
  id: number;
  name: string;
  customerName: string;
  customerEmail?: string;
  projectType: 'solar' | 'heatpump' | 'combined';
  status: 'draft' | 'active' | 'completed' | 'archived';
  createdAt: string;
  updatedAt: string;
  data: Record<string, any>;      // Project-specific data
}
```

#### Actions

- `setProjects(projects: Project[])` - Set the projects list
- `setCurrentProject(project: Project | null)` - Set current project
- `addProject(project: Project)` - Add a new project
- `updateProject(id: number, updates: Partial<Project>)` - Update a project
- `deleteProject(id: number)` - Delete a project
- `setLoading(loading: boolean)` - Set loading state
- `setError(error: string | null)` - Set error message
- `clearError()` - Clear error message

#### Usage Example

```typescript
import { useProjectStore } from '@/store';

function ProjectList() {
  const { 
    projects, 
    currentProject,
    setCurrentProject,
    updateProject,
    deleteProject,
    isLoading 
  } = useProjectStore();

  const handleSelectProject = (project: Project) => {
    setCurrentProject(project);
  };

  const handleUpdateProject = async (id: number, updates: Partial<Project>) => {
    updateProject(id, updates);
    // Sync with backend
    await api.put(`/projects/${id}`, updates);
  };

  const handleDeleteProject = async (id: number) => {
    if (confirm('Are you sure?')) {
      deleteProject(id);
      await api.delete(`/projects/${id}`);
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {projects.map(project => (
        <div key={project.id}>
          <h3>{project.name}</h3>
          <p>{project.customerName}</p>
          <button onClick={() => handleSelectProject(project)}>
            Select
          </button>
          <button onClick={() => handleDeleteProject(project.id)}>
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}
```

#### Note on Persistence

The project store does **not** persist to localStorage by default. Projects are loaded from the backend API on application start. This ensures data consistency and prevents stale data issues.

---

## Best Practices

### 1. Selective State Access

Only subscribe to the state you need to prevent unnecessary re-renders:

```typescript
// ❌ Bad - subscribes to entire store
const store = useAuthStore();

// ✅ Good - subscribes only to needed values
const { user, isAuthenticated } = useAuthStore();

// ✅ Even better - use selectors for derived state
const username = useAuthStore(state => state.user?.username);
```

### 2. Actions Over Direct State Mutation

Always use actions to update state:

```typescript
// ❌ Bad - direct mutation (won't work with Zustand anyway)
store.user = newUser;

// ✅ Good - use actions
setUser(newUser);
```

### 3. Error Handling

Always handle errors in your actions:

```typescript
const handleLogin = async (credentials) => {
  const { setUser, setError, setLoading } = useAuthStore.getState();
  
  setLoading(true);
  setError(null);
  
  try {
    const user = await loginAPI(credentials);
    setUser(user);
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
};
```

### 4. Optimistic Updates

For better UX, update the UI optimistically and rollback on error:

```typescript
const handleUpdateProject = async (id: number, updates: Partial<Project>) => {
  const { updateProject, projects } = useProjectStore.getState();
  
  // Save original state
  const originalProject = projects.find(p => p.id === id);
  
  // Optimistic update
  updateProject(id, updates);
  
  try {
    await api.put(`/projects/${id}`, updates);
  } catch (error) {
    // Rollback on error
    if (originalProject) {
      updateProject(id, originalProject);
    }
    throw error;
  }
};
```

### 5. Computed Values

Use selectors for computed values:

```typescript
// Create a selector
const selectActiveProjects = (state: ProjectState) => 
  state.projects.filter(p => p.status === 'active');

// Use in component
const activeProjects = useProjectStore(selectActiveProjects);
```

### 6. Middleware

Zustand supports middleware for logging, persistence, etc.:

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export const useMyStore = create(
  devtools(
    persist(
      (set) => ({
        // state and actions
      }),
      { name: 'my-storage' }
    )
  )
);
```

---

## Testing

### Testing Stores

```typescript
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '@/store';

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  it('should set user', () => {
    const { result } = renderHook(() => useAuthStore());
    
    act(() => {
      result.current.setUser({ id: 1, username: 'test' });
    });

    expect(result.current.user).toEqual({ id: 1, username: 'test' });
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('should logout', () => {
    const { result } = renderHook(() => useAuthStore());
    
    act(() => {
      result.current.setUser({ id: 1, username: 'test' });
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
});
```

---

## Performance Considerations

### 1. Avoid Large Objects in State

Store only what you need. For large datasets, consider:
- Pagination
- Virtual scrolling
- Lazy loading

### 2. Use Shallow Comparison

Zustand uses shallow comparison by default, which is efficient for most cases.

### 3. Split Large Stores

If a store becomes too large, split it into multiple stores:

```typescript
// Instead of one large store
useAppStore()

// Split into focused stores
useAuthStore()
useUIStore()
useProjectStore()
useSettingsStore()
```

### 4. Memoize Selectors

For expensive computations, memoize selectors:

```typescript
import { useMemo } from 'react';

const MyComponent = () => {
  const projects = useProjectStore(state => state.projects);
  
  const sortedProjects = useMemo(() => {
    return [...projects].sort((a, b) => 
      a.name.localeCompare(b.name)
    );
  }, [projects]);
  
  return <div>{/* render sortedProjects */}</div>;
};
```

---

## Migration from Other State Management

### From Redux

Zustand is simpler than Redux:

```typescript
// Redux
const mapStateToProps = (state) => ({
  user: state.auth.user,
  isAuthenticated: state.auth.isAuthenticated,
});

const mapDispatchToProps = {
  setUser,
  logout,
};

export default connect(mapStateToProps, mapDispatchToProps)(MyComponent);

// Zustand
const { user, isAuthenticated, setUser, logout } = useAuthStore();
```

### From Context API

Zustand is more performant:

```typescript
// Context API
const AuthContext = createContext();

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // ... more state and logic
  
  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

// Zustand
export const useAuthStore = create((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}));
```

---

## Troubleshooting

### State Not Persisting

Check that:
1. Persistence middleware is configured
2. localStorage is available
3. The storage key is unique
4. The state is included in `partialize`

### State Not Updating

Check that:
1. You're using the action functions, not direct mutation
2. The component is subscribed to the correct state
3. React DevTools shows the state changing

### Performance Issues

Check that:
1. You're not subscribing to the entire store
2. You're using selectors for derived state
3. You're not storing large objects unnecessarily

---

## Additional Resources

- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Zustand Best Practices](https://github.com/pmndrs/zustand/wiki/Best-Practices)
- [React State Management Comparison](https://react-state-management.com/)

---

## Summary

✅ **Zustand** is installed and configured  
✅ **Auth Store** manages authentication state with persistence  
✅ **UI Store** manages global UI state with persistence  
✅ **Project Store** manages project data  
✅ **Persistence** configured with localStorage  
✅ **TypeScript** types for all stores  
✅ **Best practices** documented  

The state management system is ready for use throughout the application!
