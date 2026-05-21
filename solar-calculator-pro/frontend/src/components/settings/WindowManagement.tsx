/**
 * Window Management Settings Component
 * 
 * Provides UI for managing window state persistence, fullscreen mode,
 * always-on-top, and multi-window preferences.
 */

import React, { useState, useEffect } from 'react';
import { useWindowManager } from '../../hooks/useWindowManager';
import './WindowManagement.css';

export const WindowManagement: React.FC = () => {
  const {
    windowInfo,
    preferences,
    allWindows,
    loading,
    error,
    isElectron,
    toggleFullscreen,
    toggleAlwaysOnTop,
    minimizeWindow,
    maximizeWindow,
    restoreWindow,
    updatePreferences,
    clearWindowState,
    clearAllWindowStates,
    refresh,
    refreshAll
  } = useWindowManager();

  const [localPreferences, setLocalPreferences] = useState(preferences);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  useEffect(() => {
    setLocalPreferences(preferences);
  }, [preferences]);

  if (!isElectron) {
    return (
      <div className="window-management not-electron">
        <p>Window management features are only available in the desktop application.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="window-management loading">
        <div className="spinner"></div>
        <p>Loading window management settings...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="window-management error">
        <p className="error-message">Error: {error}</p>
        <button onClick={refresh}>Retry</button>
      </div>
    );
  }

  const handlePreferenceChange = (key: string, value: any) => {
    setLocalPreferences(prev => prev ? { ...prev, [key]: value } : null);
  };

  const handleSavePreferences = async () => {
    if (!localPreferences) return;

    setSaveStatus('saving');
    const result = await updatePreferences(localPreferences);
    
    if (result.success) {
      setSaveStatus('success');
      setTimeout(() => setSaveStatus(null), 3000);
    } else {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  const handleClearWindowState = async () => {
    if (confirm('Are you sure you want to clear the saved state for this window?')) {
      const result = await clearWindowState();
      if (result.success) {
        alert('Window state cleared successfully');
        refresh();
      }
    }
  };

  const handleClearAllStates = async () => {
    if (confirm('Are you sure you want to clear all saved window states? This cannot be undone.')) {
      const result = await clearAllWindowStates();
      if (result.success) {
        alert('All window states cleared successfully');
        refreshAll();
      }
    }
  };

  return (
    <div className="window-management">
      <h2>Window Management</h2>

      {/* Current Window Info */}
      <section className="window-info-section">
        <h3>Current Window</h3>
        {windowInfo && (
          <div className="window-info-grid">
            <div className="info-item">
              <label>Position:</label>
              <span>{windowInfo.bounds.x}, {windowInfo.bounds.y}</span>
            </div>
            <div className="info-item">
              <label>Size:</label>
              <span>{windowInfo.bounds.width} × {windowInfo.bounds.height}</span>
            </div>
            <div className="info-item">
              <label>Maximized:</label>
              <span className={windowInfo.isMaximized ? 'status-yes' : 'status-no'}>
                {windowInfo.isMaximized ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="info-item">
              <label>Fullscreen:</label>
              <span className={windowInfo.isFullScreen ? 'status-yes' : 'status-no'}>
                {windowInfo.isFullScreen ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="info-item">
              <label>Always on Top:</label>
              <span className={windowInfo.isAlwaysOnTop ? 'status-yes' : 'status-no'}>
                {windowInfo.isAlwaysOnTop ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="info-item">
              <label>Focused:</label>
              <span className={windowInfo.isFocused ? 'status-yes' : 'status-no'}>
                {windowInfo.isFocused ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        )}

        <div className="window-actions">
          <button onClick={() => toggleFullscreen()} className="action-button">
            Toggle Fullscreen
          </button>
          <button onClick={() => toggleAlwaysOnTop()} className="action-button">
            Toggle Always on Top
          </button>
          <button onClick={() => minimizeWindow()} className="action-button">
            Minimize
          </button>
          <button onClick={() => maximizeWindow()} className="action-button">
            Maximize/Restore
          </button>
          <button onClick={() => restoreWindow()} className="action-button">
            Restore
          </button>
        </div>
      </section>

      {/* Preferences */}
      <section className="preferences-section">
        <h3>Window Preferences</h3>
        {localPreferences && (
          <div className="preferences-form">
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={localPreferences.rememberWindowState}
                  onChange={(e) => handlePreferenceChange('rememberWindowState', e.target.checked)}
                />
                <span>Remember window state (position, size, etc.)</span>
              </label>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={localPreferences.restoreWindowsOnStartup}
                  onChange={(e) => handlePreferenceChange('restoreWindowsOnStartup', e.target.checked)}
                />
                <span>Restore windows on startup</span>
              </label>
            </div>

            <div className="form-group">
              <label>Default Width:</label>
              <input
                type="number"
                value={localPreferences.defaultWidth}
                onChange={(e) => handlePreferenceChange('defaultWidth', parseInt(e.target.value))}
                min="400"
                max="3840"
              />
            </div>

            <div className="form-group">
              <label>Default Height:</label>
              <input
                type="number"
                value={localPreferences.defaultHeight}
                onChange={(e) => handlePreferenceChange('defaultHeight', parseInt(e.target.value))}
                min="300"
                max="2160"
              />
            </div>

            <div className="form-group">
              <label>Minimum Width:</label>
              <input
                type="number"
                value={localPreferences.defaultMinWidth}
                onChange={(e) => handlePreferenceChange('defaultMinWidth', parseInt(e.target.value))}
                min="400"
                max="1920"
              />
            </div>

            <div className="form-group">
              <label>Minimum Height:</label>
              <input
                type="number"
                value={localPreferences.defaultMinHeight}
                onChange={(e) => handlePreferenceChange('defaultMinHeight', parseInt(e.target.value))}
                min="300"
                max="1080"
              />
            </div>

            <div className="form-actions">
              <button 
                onClick={handleSavePreferences} 
                className="save-button"
                disabled={saveStatus === 'saving'}
              >
                {saveStatus === 'saving' ? 'Saving...' : 'Save Preferences'}
              </button>
              {saveStatus === 'success' && (
                <span className="save-status success">✓ Saved successfully</span>
              )}
              {saveStatus === 'error' && (
                <span className="save-status error">✗ Failed to save</span>
              )}
            </div>
          </div>
        )}
      </section>

      {/* All Windows */}
      <section className="all-windows-section">
        <h3>All Windows ({allWindows.length})</h3>
        <div className="windows-list">
          {allWindows.map((window) => (
            <div key={window.id} className="window-item">
              <div className="window-item-header">
                <h4>{window.title || window.id}</h4>
                <span className="window-id">{window.id}</span>
              </div>
              <div className="window-item-info">
                <span>Size: {window.bounds.width} × {window.bounds.height}</span>
                <span>Position: ({window.bounds.x}, {window.bounds.y})</span>
              </div>
              <div className="window-item-status">
                {window.isMaximized && <span className="badge">Maximized</span>}
                {window.isFullScreen && <span className="badge">Fullscreen</span>}
                {window.isAlwaysOnTop && <span className="badge">Always on Top</span>}
                {window.isFocused && <span className="badge focused">Focused</span>}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Advanced Actions */}
      <section className="advanced-section">
        <h3>Advanced</h3>
        <div className="advanced-actions">
          <button onClick={handleClearWindowState} className="danger-button">
            Clear Current Window State
          </button>
          <button onClick={handleClearAllStates} className="danger-button">
            Clear All Window States
          </button>
          <button onClick={refreshAll} className="action-button">
            Refresh Window List
          </button>
        </div>
      </section>
    </div>
  );
};

export default WindowManagement;
