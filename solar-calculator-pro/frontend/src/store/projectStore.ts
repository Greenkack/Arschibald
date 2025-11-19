/**
 * Project Store
 * 
 * Manages project data state using Zustand
 */

import { create } from 'zustand';

export interface Project {
  id: number;
  name: string;
  customerName: string;
  customerEmail?: string;
  projectType: 'solar' | 'heatpump' | 'combined';
  status: 'draft' | 'active' | 'completed' | 'archived';
  createdAt: string;
  updatedAt: string;
  data: Record<string, any>;
}

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  addProject: (project: Project) => void;
  updateProject: (id: number, updates: Partial<Project>) => void;
  deleteProject: (id: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

/**
 * Project store
 */
export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  currentProject: null,
  isLoading: false,
  error: null,

  setProjects: (projects) =>
    set({ projects, error: null }),

  setCurrentProject: (project) =>
    set({ currentProject: project }),

  addProject: (project) =>
    set((state) => ({
      projects: [...state.projects, project],
      error: null,
    })),

  updateProject: (id, updates) =>
    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === id ? { ...p, ...updates, updatedAt: new Date().toISOString() } : p
      ),
      currentProject:
        state.currentProject?.id === id
          ? { ...state.currentProject, ...updates, updatedAt: new Date().toISOString() }
          : state.currentProject,
      error: null,
    })),

  deleteProject: (id) =>
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== id),
      currentProject: state.currentProject?.id === id ? null : state.currentProject,
      error: null,
    })),

  setLoading: (loading) =>
    set({ isLoading: loading }),

  setError: (error) =>
    set({ error }),

  clearError: () =>
    set({ error: null }),
}));
