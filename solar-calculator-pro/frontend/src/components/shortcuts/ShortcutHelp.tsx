/**
 * Shortcut Help Dialog
 * 
 * Quick reference dialog for keyboard shortcuts
 */

import React, { useState, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { useShortcutStore } from '../../store/shortcutStore';
import { formatShortcut, ShortcutConfig } from '../../hooks/useKeyboardShortcuts';
import './ShortcutHelp.css';

export const ShortcutHelp: React.FC = () => {
  const [visible, setVisible] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const { getAllShortcuts } = useShortcutStore();

  // Listen for help shortcut
  useEffect(() => {
    const handleOpenHelp = () => setVisible(true);
    window.addEventListener('open-shortcut-help' as any, handleOpenHelp);
    
    return () => {
      window.removeEventListener('open-shortcut-help' as any, handleOpenHelp);
    };
  }, []);

  const allShortcuts = getAllShortcuts();

  // Filter shortcuts by search term
  const filteredShortcuts = searchTerm
    ? allShortcuts.filter(s =>
        s.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        formatShortcut(s).toLowerCase().includes(searchTerm.toLowerCase())
      )
    : allShortcuts;

  // Group by category
  const groupedShortcuts = filteredShortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {} as Record<string, ShortcutConfig[]>);

  return (
    <Dialog
      header="⌨️ Keyboard Shortcuts"
      visible={visible}
      style={{ width: '700px', maxHeight: '80vh' }}
      onHide={() => setVisible(false)}
      dismissableMask
      className="shortcut-help-dialog"
    >
      <div className="shortcut-help-content">
        <div className="shortcut-help-search">
          <span className="p-input-icon-left w-full">
            <i className="pi pi-search" />
            <InputText
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search shortcuts..."
              className="w-full"
              autoFocus
            />
          </span>
        </div>

        <div className="shortcut-help-list">
          {Object.entries(groupedShortcuts).map(([category, shortcuts]) => (
            <div key={category} className="shortcut-help-category">
              <h3>{category}</h3>
              <div className="shortcut-help-items">
                {shortcuts.map((shortcut, index) => (
                  <div key={index} className="shortcut-help-item">
                    <span className="shortcut-help-description">
                      {shortcut.description}
                    </span>
                    <kbd className="shortcut-help-keys">
                      {formatShortcut(shortcut)}
                    </kbd>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {filteredShortcuts.length === 0 && (
          <div className="shortcut-help-empty">
            <i className="pi pi-search" style={{ fontSize: '3rem', opacity: 0.3 }} />
            <p>No shortcuts found</p>
          </div>
        )}

        <div className="shortcut-help-footer">
          <small>
            Press <kbd>Ctrl+Shift+?</kbd> to open this dialog anytime
          </small>
        </div>
      </div>
    </Dialog>
  );
};

/**
 * Hook to trigger shortcut help
 */
export const useShortcutHelp = () => {
  const open = () => {
    window.dispatchEvent(new CustomEvent('open-shortcut-help'));
  };

  return { open };
};
