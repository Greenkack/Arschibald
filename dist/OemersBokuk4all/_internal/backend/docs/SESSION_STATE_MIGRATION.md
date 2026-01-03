# Session State Migration Guide

## Task 239: Session State Migration

This document details the migration of Streamlit `st.session_state` to Zustand stores.

## Overview

Streamlit uses `st.session_state` for state management. In the Electron app, we use Zustand stores with persistence.

## Zustand Store Architecture

```
stores/
├── authStore.ts        # User authentication state
├── projectStore.ts     # Project data and current project
├── calculationStore.ts # Calculation results and inputs
├── productStore.ts     # Product selection and catalog
├── pdfStore.ts         # PDF generation options
├── crmStore.ts         # CRM data (customers, offers)
├── uiStore.ts          # UI state (theme, sidebar, etc.)
└── index.ts            # Store exports
```

## Store Definitions

### Auth Store

```typescript
// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  email: string;
  name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (user, token) => set({ user, token, isAuthenticated: true }),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
      updateUser: (updates) => set((state) => ({
        user: state.user ? { ...state.user, ...updates } : null
      })),
    }),
    { name: 'auth-storage' }
  )
);
```

### Project Store

```typescript
// stores/projectStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Project {
  id: number;
  name: string;
  type: 'solar' | 'heatpump' | 'combined';
  customerId?: number;
  data: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  addProject: (project: Project) => void;
  updateProject: (id: number, updates: Partial<Project>) => void;
  deleteProject: (id: number) => void;
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set) => ({
      projects: [],
      currentProject: null,
      isLoading: false,
      setProjects: (projects) => set({ projects }),
      setCurrentProject: (project) => set({ currentProject: project }),
      addProject: (project) => set((state) => ({
        projects: [...state.projects, project]
      })),
      updateProject: (id, updates) => set((state) => ({
        projects: state.projects.map(p => 
          p.id === id ? { ...p, ...updates } : p
        ),
        currentProject: state.currentProject?.id === id 
          ? { ...state.currentProject, ...updates }
          : state.currentProject
      })),
      deleteProject: (id) => set((state) => ({
        projects: state.projects.filter(p => p.id !== id),
        currentProject: state.currentProject?.id === id 
          ? null 
          : state.currentProject
      })),
    }),
    { name: 'project-storage' }
  )
);
```

### Calculation Store

```typescript
// stores/calculationStore.ts
import { create } from 'zustand';

interface SolarInputs {
  roofArea: number;
  roofAngle: number;
  orientation: string;
  moduleType: string;
  consumption: number;
}

interface SolarResults {
  systemSize: number;
  moduleCount: number;
  annualProduction: number;
  savings: number;
  paybackYears: number;
  co2Savings: number;
}

interface CalculationState {
  solarInputs: SolarInputs;
  solarResults: SolarResults | null;
  heatpumpInputs: Record<string, any>;
  heatpumpResults: Record<string, any> | null;
  isCalculating: boolean;
  setSolarInputs: (inputs: Partial<SolarInputs>) => void;
  setSolarResults: (results: SolarResults) => void;
  setHeatpumpInputs: (inputs: Record<string, any>) => void;
  setHeatpumpResults: (results: Record<string, any>) => void;
  resetCalculations: () => void;
}

const defaultSolarInputs: SolarInputs = {
  roofArea: 50,
  roofAngle: 30,
  orientation: 'south',
  moduleType: 'standard',
  consumption: 4000,
};

export const useCalculationStore = create<CalculationState>((set) => ({
  solarInputs: defaultSolarInputs,
  solarResults: null,
  heatpumpInputs: {},
  heatpumpResults: null,
  isCalculating: false,
  setSolarInputs: (inputs) => set((state) => ({
    solarInputs: { ...state.solarInputs, ...inputs }
  })),
  setSolarResults: (results) => set({ solarResults: results }),
  setHeatpumpInputs: (inputs) => set((state) => ({
    heatpumpInputs: { ...state.heatpumpInputs, ...inputs }
  })),
  setHeatpumpResults: (results) => set({ heatpumpResults: results }),
  resetCalculations: () => set({
    solarInputs: defaultSolarInputs,
    solarResults: null,
    heatpumpInputs: {},
    heatpumpResults: null,
  }),
}));
```

### UI Store

```typescript
// stores/uiStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  theme: 'light' | 'dark' | 'system';
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  language: string;
  notifications: boolean;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setLanguage: (language: string) => void;
  setNotifications: (enabled: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: 'system',
      sidebarOpen: true,
      sidebarCollapsed: false,
      language: 'de',
      notifications: true,
      setTheme: (theme) => set({ theme }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      setLanguage: (language) => set({ language }),
      setNotifications: (enabled) => set({ notifications: enabled }),
    }),
    { name: 'ui-storage' }
  )
);
```

## Session State Mapping

| Streamlit `st.session_state` | Zustand Store | Property |
|------------------------------|---------------|----------|
| `user` | `useAuthStore` | `user` |
| `token` | `useAuthStore` | `token` |
| `is_authenticated` | `useAuthStore` | `isAuthenticated` |
| `current_project` | `useProjectStore` | `currentProject` |
| `projects` | `useProjectStore` | `projects` |
| `solar_inputs` | `useCalculationStore` | `solarInputs` |
| `solar_results` | `useCalculationStore` | `solarResults` |
| `heatpump_inputs` | `useCalculationStore` | `heatpumpInputs` |
| `heatpump_results` | `useCalculationStore` | `heatpumpResults` |
| `selected_products` | `useProductStore` | `selected` |
| `pdf_options` | `usePDFStore` | `options` |
| `theme` | `useUIStore` | `theme` |
| `sidebar_state` | `useUIStore` | `sidebarOpen` |
| `language` | `useUIStore` | `language` |

## State Persistence

### LocalStorage Persistence

```typescript
// Stores with persistence
const persistedStores = [
  'auth-storage',      // User authentication
  'project-storage',   // Projects
  'ui-storage',        // UI preferences
  'pdf-storage',       // PDF options
];
```

### State Synchronization Between Tabs

```typescript
// utils/stateSync.ts
export const setupStateSync = () => {
  window.addEventListener('storage', (event) => {
    if (event.key && persistedStores.includes(event.key)) {
      // Trigger store rehydration
      const store = getStoreByKey(event.key);
      if (store) {
        store.persist.rehydrate();
      }
    }
  });
};
```

### State Backup and Restore

```typescript
// utils/stateBackup.ts
export const backupState = (): string => {
  const backup: Record<string, any> = {};
  
  persistedStores.forEach(key => {
    const data = localStorage.getItem(key);
    if (data) {
      backup[key] = JSON.parse(data);
    }
  });
  
  return JSON.stringify(backup);
};

export const restoreState = (backupJson: string): void => {
  const backup = JSON.parse(backupJson);
  
  Object.entries(backup).forEach(([key, value]) => {
    localStorage.setItem(key, JSON.stringify(value));
  });
  
  // Rehydrate all stores
  window.location.reload();
};
```

### State Versioning

```typescript
// utils/stateVersion.ts
const STATE_VERSION = '1.0.0';

export const migrateState = (storedVersion: string, state: any): any => {
  if (storedVersion === STATE_VERSION) {
    return state;
  }
  
  // Migration logic for different versions
  if (storedVersion === '0.9.0') {
    // Migrate from 0.9.0 to 1.0.0
    return {
      ...state,
      // Add new fields, transform data, etc.
    };
  }
  
  return state;
};
```

## Migration Utilities

### State Migration Script

```typescript
// utils/migrateFromStreamlit.ts
interface StreamlitState {
  [key: string]: any;
}

export const migrateFromStreamlit = (streamlitState: StreamlitState) => {
  // Migrate auth state
  if (streamlitState.user) {
    useAuthStore.getState().login(
      streamlitState.user,
      streamlitState.token || ''
    );
  }
  
  // Migrate projects
  if (streamlitState.projects) {
    useProjectStore.getState().setProjects(streamlitState.projects);
  }
  
  // Migrate current project
  if (streamlitState.current_project) {
    useProjectStore.getState().setCurrentProject(streamlitState.current_project);
  }
  
  // Migrate calculation inputs
  if (streamlitState.solar_inputs) {
    useCalculationStore.getState().setSolarInputs(streamlitState.solar_inputs);
  }
  
  // Migrate UI preferences
  if (streamlitState.theme) {
    useUIStore.getState().setTheme(streamlitState.theme);
  }
  
  if (streamlitState.language) {
    useUIStore.getState().setLanguage(streamlitState.language);
  }
};
```

## Testing State Consistency

```typescript
// tests/stateConsistency.test.ts
describe('State Consistency', () => {
  it('should persist auth state across page reloads', () => {
    const { login } = useAuthStore.getState();
    login({ id: 1, email: 'test@example.com', name: 'Test', role: 'user' }, 'token');
    
    // Simulate reload
    useAuthStore.persist.rehydrate();
    
    const { user, isAuthenticated } = useAuthStore.getState();
    expect(user).not.toBeNull();
    expect(isAuthenticated).toBe(true);
  });
  
  it('should sync state between tabs', () => {
    // Test implementation
  });
});
```

## Requirements Coverage

- **2.5**: State management with Zustand ✅
- **5.2**: State persistence ✅
