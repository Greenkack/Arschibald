/**
 * Keyboard Shortcuts Help Component
 * Displays available keyboard shortcuts to users
 */

import React, { useState, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import './KeyboardShortcutsHelp.css';

export interface KeyboardShortcut {
  keys: string[];
  description: string;
  category: string;
}

const shortcuts: KeyboardShortcut[] = [
  // Navigation
  { keys: ['Ctrl', 'K'], description: 'Open command palette', category: 'Navigation' },
  { keys: ['Ctrl', '/'], description: 'Open search', category: 'Navigation' },
  { keys: ['Alt', '1'], description: 'Go to Dashboard', category: 'Navigation' },
  { keys: ['Alt', '2'], description: 'Go to Solar Calculator', category: 'Navigation' },
  { keys: ['Alt', '3'], description: 'Go to Projects', category: 'Navigation' },
  { keys: ['Alt', '4'], description: 'Go to CRM', category: 'Navigation' },
  { keys: ['Alt', '5'], description: 'Go to Settings', category: 'Navigation' },
  
  // General
  { keys: ['Ctrl', 'S'], description: 'Save current work', category: 'General' },
  { keys: ['Ctrl', 'Z'], description: 'Undo', category: 'General' },
  { keys: ['Ctrl', 'Y'], description: 'Redo', category: 'General' },
  { keys: ['Ctrl', 'P'], description: 'Print', category: 'General' },
  { keys: ['Ctrl', 'N'], description: 'New item', category: 'General' },
  { keys: ['Escape'], description: 'Close dialog/Cancel', category: 'General' },
  
  // Editing
  { keys: ['Ctrl', 'C'], description: 'Copy', category: 'Editing' },
  { keys: ['Ctrl', 'X'], description: 'Cut', category: 'Editing' },
  { keys: ['Ctrl', 'V'], description: 'Paste', category: 'Editing' },
  { keys: ['Ctrl', 'A'], description: 'Select all', category: 'Editing' },
  { keys: ['Delete'], description: 'Delete selected', category: 'Editing' },
  
  // Forms
  { keys: ['Tab'], description: 'Next field', category: 'Forms' },
  { keys: ['Shift', 'Tab'], description: 'Previous field', category: 'Forms' },
  { keys: ['Enter'], description: 'Submit form', category: 'Forms' },
  { keys: ['Space'], description: 'Toggle checkbox/radio', category: 'Forms' },
  
  // Tables
  { keys: ['↑'], description: 'Previous row', category: 'Tables' },
  { keys: ['↓'], description: 'Next row', category: 'Tables' },
  { keys: ['Home'], description: 'First row', category: 'Tables' },
  { keys: ['End'], description: 'Last row', category: 'Tables' },
  { keys: ['Enter'], description: 'Open selected row', category: 'Tables' },
  
  // Help
  { keys: ['?'], description: 'Show keyboard shortcuts', category: 'Help' },
  { keys: ['F1'], description: 'Open help', category: 'Help' },
];

export const KeyboardShortcutsHelp: React.FC = () => {
  const [visible, setVisible] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredShortcuts, setFilteredShortcuts] = useState(shortcuts);

  // Listen for ? key to open help
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '?' && e.shiftKey && !e.ctrlKey && !e.altKey && !e.metaKey) {
        e.preventDefault();
        setVisible(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Filter shortcuts based on search
  useEffect(() => {
    if (!searchTerm) {
      setFilteredShortcuts(shortcuts);
      return;
    }

    const term = searchTerm.toLowerCase();
    const filtered = shortcuts.filter(
      (shortcut) =>
        shortcut.description.toLowerCase().includes(term) ||
        shortcut.category.toLowerCase().includes(term) ||
        shortcut.keys.some((key) => key.toLowerCase().includes(term))
    );

    setFilteredShortcuts(filtered);
  }, [searchTerm]);

  // Group shortcuts by category
  const groupedShortcuts = filteredShortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {} as Record<string, KeyboardShortcut[]>);

  const renderKeys = (keys: string[]) => {
    return (
      <div className="shortcut-keys">
        {keys.map((key, index) => (
          <React.Fragment key={index}>
            {index > 0 && <span className="key-separator">+</span>}
            <kbd className="key">{key}</kbd>
          </React.Fragment>
        ))}
      </div>
    );
  };

  const footer = (
    <div className="shortcuts-footer">
      <Button
        label="Close"
        icon="pi pi-times"
        onClick={() => setVisible(false)}
        className="p-button-text"
      />
    </div>
  );

  return (
    <>
      <Button
        icon="pi pi-question-circle"
        className="p-button-rounded p-button-text"
        onClick={() => setVisible(true)}
        aria-label="Show keyboard shortcuts"
        tooltip="Keyboard Shortcuts (Shift + ?)"
        tooltipOptions={{ position: 'left' }}
      />

      <Dialog
        header="Keyboard Shortcuts"
        visible={visible}
        style={{ width: '700px' }}
        onHide={() => setVisible(false)}
        footer={footer}
        modal
        dismissableMask
        className="shortcuts-dialog"
      >
        <div className="shortcuts-content">
          <div className="shortcuts-search">
            <span className="p-input-icon-left">
              <i className="pi pi-search" />
              <InputText
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search shortcuts..."
                className="w-full"
                aria-label="Search keyboard shortcuts"
              />
            </span>
          </div>

          {Object.keys(groupedShortcuts).length === 0 ? (
            <div className="no-results">
              <p>No shortcuts found matching "{searchTerm}"</p>
            </div>
          ) : (
            <div className="shortcuts-list">
              {Object.entries(groupedShortcuts).map(([category, categoryShortcuts]) => (
                <div key={category} className="shortcuts-category">
                  <h3>{category}</h3>
                  <div className="shortcuts-items">
                    {categoryShortcuts.map((shortcut, index) => (
                      <div key={index} className="shortcut-item">
                        <div className="shortcut-description">{shortcut.description}</div>
                        {renderKeys(shortcut.keys)}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="shortcuts-tip">
            <i className="pi pi-info-circle" />
            <span>
              Press <kbd>Shift</kbd> + <kbd>?</kbd> anytime to view this help
            </span>
          </div>
        </div>
      </Dialog>
    </>
  );
};
