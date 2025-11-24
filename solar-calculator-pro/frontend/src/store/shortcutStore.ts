/**
 * Keyboard Shortcuts Store
 * 
 * Manages global keyboard shortcuts state with:
 * - Shortcut registration
 * - Conflict detection
 * - Customization persistence
 * - Context management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ShortcutConfig, shortcutsConflict } from '../hooks/useKeyboardShortcuts';

interface ShortcutState {
  // Global shortcuts enabled/disabled
  enabled: boolean;
  
  // Registered shortcuts by context
  shortcuts: Map<string, ShortcutConfig[]>;
  
  // Custom shortcut overrides
  customShortcuts: Map<string, Partial<ShortcutConfig>>;
  
  // Active context
  activeContext: string | null;
  
  // Conflict warnings
  conflicts: Array<{
    shortcut1: ShortcutConfig;
    shortcut2: ShortcutConfig;
    context?: string;
  }>;
  
  // Actions
  setEnabled: (enabled: boolean) => void;
  registerShortcuts: (shortcuts: ShortcutConfig[], context?: string) => void;
  unregisterShortcuts: (shortcuts: ShortcutConfig[], context?: string) => void;
  setActiveContext: (context: string | null) => void;
  customizeShortcut: (id: string, config: Partial<ShortcutConfig>) => void;
  resetShortcut: (id: string) => void;
  resetAllShortcuts: () => void;
  detectConflicts: () => void;
  hasConflict: (shortcut: ShortcutConfig, context?: string) => boolean;
  isEnabled: () => boolean;
  getShortcutById: (id: string) => ShortcutConfig | undefined;
  getShortcutsByContext: (context: string) => ShortcutConfig[];
  getAllShortcuts: () => ShortcutConfig[];
}

export const useShortcutStore = create<ShortcutState>()(
  persist(
    (set, get) => ({
      enabled: true,
      shortcuts: new Map(),
      customShortcuts: new Map(),
      activeContext: null,
      conflicts: [],

      setEnabled: (enabled) => set({ enabled }),

      registerShortcuts: (shortcuts, context = 'global') => {
        set((state) => {
          const newShortcuts = new Map(state.shortcuts);
          const existing = newShortcuts.get(context) || [];
          
          // Merge with existing, avoiding duplicates
          const merged = [...existing];
          for (const shortcut of shortcuts) {
            const exists = merged.some(s => 
              s.key === shortcut.key &&
              s.ctrl === shortcut.ctrl &&
              s.alt === shortcut.alt &&
              s.shift === shortcut.shift &&
              s.meta === shortcut.meta
            );
            
            if (!exists) {
              merged.push(shortcut);
            }
          }
          
          newShortcuts.set(context, merged);
          
          return { shortcuts: newShortcuts };
        });
        
        // Detect conflicts after registration
        get().detectConflicts();
      },

      unregisterShortcuts: (shortcuts, context = 'global') => {
        set((state) => {
          const newShortcuts = new Map(state.shortcuts);
          const existing = newShortcuts.get(context) || [];
          
          // Remove specified shortcuts
          const filtered = existing.filter(existing => 
            !shortcuts.some(toRemove => 
              existing.key === toRemove.key &&
              existing.ctrl === toRemove.ctrl &&
              existing.alt === toRemove.alt &&
              existing.shift === toRemove.shift &&
              existing.meta === toRemove.meta
            )
          );
          
          if (filtered.length > 0) {
            newShortcuts.set(context, filtered);
          } else {
            newShortcuts.delete(context);
          }
          
          return { shortcuts: newShortcuts };
        });
      },

      setActiveContext: (context) => set({ activeContext: context }),

      customizeShortcut: (id, config) => {
        set((state) => {
          const newCustomShortcuts = new Map(state.customShortcuts);
          newCustomShortcuts.set(id, config);
          return { customShortcuts: newCustomShortcuts };
        });
        
        get().detectConflicts();
      },

      resetShortcut: (id) => {
        set((state) => {
          const newCustomShortcuts = new Map(state.customShortcuts);
          newCustomShortcuts.delete(id);
          return { customShortcuts: newCustomShortcuts };
        });
      },

      resetAllShortcuts: () => {
        set({ customShortcuts: new Map(), conflicts: [] });
      },

      detectConflicts: () => {
        const state = get();
        const allShortcuts = state.getAllShortcuts();
        const conflicts: typeof state.conflicts = [];
        
        // Check for conflicts
        for (let i = 0; i < allShortcuts.length; i++) {
          for (let j = i + 1; j < allShortcuts.length; j++) {
            const a = allShortcuts[i];
            const b = allShortcuts[j];
            
            if (shortcutsConflict(a, b)) {
              conflicts.push({
                shortcut1: a,
                shortcut2: b,
                context: a.context || b.context,
              });
            }
          }
        }
        
        set({ conflicts });
      },

      hasConflict: (shortcut, context) => {
        const state = get();
        return state.conflicts.some(conflict => 
          (shortcutsConflict(conflict.shortcut1, shortcut) ||
           shortcutsConflict(conflict.shortcut2, shortcut)) &&
          (!context || conflict.context === context)
        );
      },

      isEnabled: () => get().enabled,

      getShortcutById: (id) => {
        const state = get();
        for (const shortcuts of state.shortcuts.values()) {
          const found = shortcuts.find(s => 
            `${s.context || 'global'}-${s.key}-${s.ctrl}-${s.alt}-${s.shift}-${s.meta}` === id
          );
          if (found) return found;
        }
        return undefined;
      },

      getShortcutsByContext: (context) => {
        return get().shortcuts.get(context) || [];
      },

      getAllShortcuts: () => {
        const state = get();
        const all: ShortcutConfig[] = [];
        
        for (const shortcuts of state.shortcuts.values()) {
          all.push(...shortcuts);
        }
        
        return all;
      },
    }),
    {
      name: 'keyboard-shortcuts-storage',
      partialize: (state) => ({
        enabled: state.enabled,
        customShortcuts: Array.from(state.customShortcuts.entries()),
      }),
      onRehydrateStorage: () => (state) => {
        if (state && Array.isArray(state.customShortcuts)) {
          state.customShortcuts = new Map(state.customShortcuts as any);
        }
      },
    }
  )
);
