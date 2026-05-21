/**
 * Shortcut Manager Component
 * 
 * Provides UI for managing keyboard shortcuts:
 * - View all shortcuts
 * - Customize shortcuts
 * - Detect conflicts
 * - Reset to defaults
 */

import React, { useState, useMemo } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dialog } from 'primereact/dialog';
import { Message } from 'primereact/message';
import { TabView, TabPanel } from 'primereact/tabview';
import { Checkbox } from 'primereact/checkbox';
import { useShortcutStore } from '../../store/shortcutStore';
import { ShortcutConfig, formatShortcut, parseShortcut } from '../../hooks/useKeyboardShortcuts';
import './ShortcutManager.css';

export const ShortcutManager: React.FC = () => {
  const {
    enabled,
    setEnabled,
    getAllShortcuts,
    getShortcutsByContext,
    customizeShortcut,
    resetShortcut,
    resetAllShortcuts,
    conflicts,
    detectConflicts,
  } = useShortcutStore();

  const [editingShortcut, setEditingShortcut] = useState<ShortcutConfig | null>(null);
  const [newShortcutString, setNewShortcutString] = useState('');
  const [filterText, setFilterText] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const allShortcuts = getAllShortcuts();

  // Group shortcuts by category
  const categories = useMemo(() => {
    const cats = new Set<string>();
    allShortcuts.forEach(s => cats.add(s.category));
    return ['all', ...Array.from(cats).sort()];
  }, [allShortcuts]);

  // Filter shortcuts
  const filteredShortcuts = useMemo(() => {
    return allShortcuts.filter(shortcut => {
      const matchesCategory = selectedCategory === 'all' || shortcut.category === selectedCategory;
      const matchesFilter = !filterText || 
        shortcut.description.toLowerCase().includes(filterText.toLowerCase()) ||
        formatShortcut(shortcut).toLowerCase().includes(filterText.toLowerCase());
      
      return matchesCategory && matchesFilter;
    });
  }, [allShortcuts, selectedCategory, filterText]);

  // Handle shortcut edit
  const handleEditShortcut = (shortcut: ShortcutConfig) => {
    setEditingShortcut(shortcut);
    setNewShortcutString(formatShortcut(shortcut));
  };

  // Handle shortcut save
  const handleSaveShortcut = () => {
    if (!editingShortcut) return;

    const parsed = parseShortcut(newShortcutString);
    const id = `${editingShortcut.context || 'global'}-${editingShortcut.key}-${editingShortcut.ctrl}-${editingShortcut.alt}-${editingShortcut.shift}-${editingShortcut.meta}`;
    
    customizeShortcut(id, parsed);
    setEditingShortcut(null);
    setNewShortcutString('');
    detectConflicts();
  };

  // Handle shortcut reset
  const handleResetShortcut = (shortcut: ShortcutConfig) => {
    const id = `${shortcut.context || 'global'}-${shortcut.key}-${shortcut.ctrl}-${shortcut.alt}-${shortcut.shift}-${shortcut.meta}`;
    resetShortcut(id);
    detectConflicts();
  };

  // Columns for shortcuts table
  const shortcutColumn = (rowData: ShortcutConfig) => (
    <span className="shortcut-badge">{formatShortcut(rowData)}</span>
  );

  const categoryColumn = (rowData: ShortcutConfig) => (
    <span className="category-badge">{rowData.category}</span>
  );

  const contextColumn = (rowData: ShortcutConfig) => (
    <span className="context-badge">{rowData.context || 'Global'}</span>
  );

  const actionsColumn = (rowData: ShortcutConfig) => (
    <div className="shortcut-actions">
      <Button
        icon="pi pi-pencil"
        className="p-button-sm p-button-text"
        onClick={() => handleEditShortcut(rowData)}
        tooltip="Edit shortcut"
      />
      <Button
        icon="pi pi-refresh"
        className="p-button-sm p-button-text"
        onClick={() => handleResetShortcut(rowData)}
        tooltip="Reset to default"
      />
    </div>
  );

  return (
    <div className="shortcut-manager">
      <div className="shortcut-manager-header">
        <h2>⌨️ Keyboard Shortcuts</h2>
        <div className="header-actions">
          <Checkbox
            inputId="shortcuts-enabled"
            checked={enabled}
            onChange={(e) => setEnabled(e.checked || false)}
          />
          <label htmlFor="shortcuts-enabled">Enable Shortcuts</label>
          
          <Button
            label="Reset All"
            icon="pi pi-refresh"
            className="p-button-sm p-button-outlined"
            onClick={resetAllShortcuts}
          />
        </div>
      </div>

      {conflicts.length > 0 && (
        <Message
          severity="warn"
          text={`${conflicts.length} shortcut conflict(s) detected. Please review and resolve.`}
          className="shortcut-conflicts-warning"
        />
      )}

      <TabView>
        <TabPanel header="All Shortcuts">
          <div className="shortcut-filters">
            <span className="p-input-icon-left">
              <i className="pi pi-search" />
              <InputText
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
                placeholder="Search shortcuts..."
              />
            </span>

            <div className="category-filters">
              {categories.map(cat => (
                <Button
                  key={cat}
                  label={cat}
                  className={`p-button-sm ${selectedCategory === cat ? '' : 'p-button-outlined'}`}
                  onClick={() => setSelectedCategory(cat)}
                />
              ))}
            </div>
          </div>

          <DataTable
            value={filteredShortcuts}
            paginator
            rows={20}
            className="shortcuts-table"
            emptyMessage="No shortcuts found"
          >
            <Column field="description" header="Description" sortable />
            <Column body={shortcutColumn} header="Shortcut" sortable />
            <Column body={categoryColumn} header="Category" sortable />
            <Column body={contextColumn} header="Context" sortable />
            <Column body={actionsColumn} header="Actions" style={{ width: '120px' }} />
          </DataTable>
        </TabPanel>

        <TabPanel header="Conflicts">
          {conflicts.length === 0 ? (
            <Message severity="success" text="No conflicts detected" />
          ) : (
            <div className="conflicts-list">
              {conflicts.map((conflict, index) => (
                <div key={index} className="conflict-item">
                  <Message severity="warn" text={
                    <div>
                      <strong>Conflict:</strong> {formatShortcut(conflict.shortcut1)} is used by:
                      <ul>
                        <li>{conflict.shortcut1.description} ({conflict.shortcut1.category})</li>
                        <li>{conflict.shortcut2.description} ({conflict.shortcut2.category})</li>
                      </ul>
                      {conflict.context && <em>Context: {conflict.context}</em>}
                    </div>
                  } />
                </div>
              ))}
            </div>
          )}
        </TabPanel>

        <TabPanel header="Cheat Sheet">
          <ShortcutCheatSheet shortcuts={allShortcuts} />
        </TabPanel>
      </TabView>

      {/* Edit Dialog */}
      <Dialog
        header="Edit Shortcut"
        visible={!!editingShortcut}
        style={{ width: '450px' }}
        onHide={() => setEditingShortcut(null)}
        footer={
          <div>
            <Button
              label="Cancel"
              icon="pi pi-times"
              onClick={() => setEditingShortcut(null)}
              className="p-button-text"
            />
            <Button
              label="Save"
              icon="pi pi-check"
              onClick={handleSaveShortcut}
              autoFocus
            />
          </div>
        }
      >
        {editingShortcut && (
          <div className="edit-shortcut-dialog">
            <div className="field">
              <label>Description</label>
              <p>{editingShortcut.description}</p>
            </div>
            
            <div className="field">
              <label>Category</label>
              <p>{editingShortcut.category}</p>
            </div>
            
            <div className="field">
              <label htmlFor="new-shortcut">New Shortcut</label>
              <InputText
                id="new-shortcut"
                value={newShortcutString}
                onChange={(e) => setNewShortcutString(e.target.value)}
                placeholder="e.g., Ctrl+S"
                className="w-full"
              />
              <small>Format: Ctrl+Alt+Shift+Key (e.g., Ctrl+S, Ctrl+Shift+P)</small>
            </div>
          </div>
        )}
      </Dialog>
    </div>
  );
};

/**
 * Shortcut Cheat Sheet Component
 */
const ShortcutCheatSheet: React.FC<{ shortcuts: ShortcutConfig[] }> = ({ shortcuts }) => {
  // Group by category
  const groupedShortcuts = useMemo(() => {
    const groups: Record<string, ShortcutConfig[]> = {};
    
    shortcuts.forEach(shortcut => {
      if (!groups[shortcut.category]) {
        groups[shortcut.category] = [];
      }
      groups[shortcut.category].push(shortcut);
    });
    
    return groups;
  }, [shortcuts]);

  return (
    <div className="shortcut-cheat-sheet">
      {Object.entries(groupedShortcuts).map(([category, categoryShortcuts]) => (
        <div key={category} className="cheat-sheet-category">
          <h3>{category}</h3>
          <div className="cheat-sheet-items">
            {categoryShortcuts.map((shortcut, index) => (
              <div key={index} className="cheat-sheet-item">
                <span className="cheat-sheet-description">{shortcut.description}</span>
                <span className="cheat-sheet-shortcut">{formatShortcut(shortcut)}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
