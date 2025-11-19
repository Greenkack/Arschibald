/**
 * Electron Integration Demo Component
 * 
 * Demonstrates how to use Electron features in React components
 * using the custom hooks provided.
 */

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  useIsElectron,
  useFileDialog,
  useBackend,
  useAutoUpdater,
  useMenuActions,
  useWindow,
  useNotification,
  useAppInfo,
  useOnlineStatus
} from '../hooks/useElectron';

export const ElectronIntegrationDemo: React.FC = () => {
  const navigate = useNavigate();
  const isElectron = useIsElectron();

  // File operations
  const { selectFile, saveFile, selectDirectory } = useFileDialog();

  // Backend communication
  const { backendUrl, isHealthy } = useBackend();

  // Auto-updates
  const {
    updateAvailable,
    updateInfo,
    downloading,
    downloadProgress,
    updateReady,
    checking,
    error: updateError,
    checkForUpdates,
    downloadUpdate,
    installUpdate
  } = useAutoUpdater();

  // Window operations
  const { minimize, maximize, close } = useWindow();

  // Notifications
  const { showNotification } = useNotification();

  // App info
  const { version, platform, arch } = useAppInfo();

  // Online status
  const isOnline = useOnlineStatus();

  // Menu/tray actions
  useMenuActions(
    // Navigation handler
    (route) => {
      console.log('Navigate to:', route);
      navigate(route);
    },
    // Action handler
    (action, data) => {
      console.log('Action:', action, data);
      switch (action) {
        case 'new-project':
          handleNewProject();
          break;
        case 'save-project':
          handleSaveProject();
          break;
        case 'export-pdf':
          handleExportPDF();
          break;
        case 'import-excel':
          handleImportExcel();
          break;
        default:
          console.log('Unhandled action:', action);
      }
    }
  );

  // Handlers
  const handleNewProject = () => {
    showNotification('New Project', 'Creating new project...');
    // Your logic here
  };

  const handleSaveProject = async () => {
    const filePath = await saveFile({
      defaultPath: 'project.json',
      filters: [
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (filePath) {
      showNotification('Success', 'Project saved successfully!');
      console.log('Saved to:', filePath);
    }
  };

  const handleExportPDF = async () => {
    const filePath = await saveFile({
      defaultPath: 'report.pdf',
      filters: [{ name: 'PDF Files', extensions: ['pdf'] }]
    });

    if (filePath) {
      showNotification('Success', 'PDF exported successfully!');
      console.log('Exported to:', filePath);
    }
  };

  const handleImportExcel = async () => {
    const filePath = await selectFile();
    if (filePath) {
      showNotification('Success', 'Excel file imported!');
      console.log('Imported:', filePath);
    }
  };

  const handleSelectDirectory = async () => {
    const dirPath = await selectDirectory();
    if (dirPath) {
      console.log('Selected directory:', dirPath);
    }
  };

  if (!isElectron) {
    return (
      <div className="p-4 bg-yellow-100 border border-yellow-400 rounded">
        <h2 className="text-xl font-bold mb-2">Not Running in Electron</h2>
        <p>This demo requires the Electron environment.</p>
        <p className="mt-2">Run: <code>npm run electron:dev</code></p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Electron Integration Demo</h1>

      {/* App Info */}
      <section className="mb-6 p-4 bg-blue-50 rounded">
        <h2 className="text-xl font-semibold mb-3">App Information</h2>
        <div className="grid grid-cols-2 gap-2">
          <div>Version:</div>
          <div className="font-mono">{version}</div>
          <div>Platform:</div>
          <div className="font-mono">{platform}</div>
          <div>Architecture:</div>
          <div className="font-mono">{arch}</div>
          <div>Online Status:</div>
          <div className={isOnline ? 'text-green-600' : 'text-red-600'}>
            {isOnline ? '🟢 Online' : '🔴 Offline'}
          </div>
        </div>
      </section>

      {/* Backend Status */}
      <section className="mb-6 p-4 bg-green-50 rounded">
        <h2 className="text-xl font-semibold mb-3">Backend Status</h2>
        <div className="grid grid-cols-2 gap-2">
          <div>Backend URL:</div>
          <div className="font-mono">{backendUrl || 'Not available'}</div>
          <div>Health Status:</div>
          <div className={isHealthy ? 'text-green-600' : 'text-red-600'}>
            {isHealthy ? '✓ Healthy' : '✗ Unhealthy'}
          </div>
        </div>
      </section>

      {/* File Operations */}
      <section className="mb-6 p-4 bg-purple-50 rounded">
        <h2 className="text-xl font-semibold mb-3">File Operations</h2>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={handleImportExcel}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
          >
            Select File
          </button>
          <button
            onClick={handleSaveProject}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
          >
            Save File
          </button>
          <button
            onClick={handleSelectDirectory}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
          >
            Select Directory
          </button>
        </div>
      </section>

      {/* Window Operations */}
      <section className="mb-6 p-4 bg-gray-50 rounded">
        <h2 className="text-xl font-semibold mb-3">Window Operations</h2>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={minimize}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Minimize
          </button>
          <button
            onClick={maximize}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Maximize/Restore
          </button>
          <button
            onClick={() => showNotification('Test', 'This is a test notification!')}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Show Notification
          </button>
        </div>
      </section>

      {/* Auto-Updater */}
      <section className="mb-6 p-4 bg-orange-50 rounded">
        <h2 className="text-xl font-semibold mb-3">Auto-Updater</h2>
        
        {checking && (
          <div className="mb-3 p-3 bg-blue-100 rounded">
            Checking for updates...
          </div>
        )}

        {updateError && (
          <div className="mb-3 p-3 bg-red-100 rounded text-red-700">
            Error: {updateError}
          </div>
        )}

        {updateAvailable && !downloading && !updateReady && (
          <div className="mb-3 p-3 bg-yellow-100 rounded">
            <p className="font-semibold">Update Available: {updateInfo?.version}</p>
            {updateInfo?.releaseNotes && (
              <p className="text-sm mt-1">{updateInfo.releaseNotes}</p>
            )}
            <button
              onClick={downloadUpdate}
              className="mt-2 px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700"
            >
              Download Update
            </button>
          </div>
        )}

        {downloading && (
          <div className="mb-3 p-3 bg-blue-100 rounded">
            <p className="font-semibold">Downloading Update...</p>
            <div className="mt-2 bg-gray-200 rounded-full h-4">
              <div
                className="bg-blue-600 h-4 rounded-full transition-all"
                style={{ width: `${downloadProgress}%` }}
              />
            </div>
            <p className="text-sm mt-1">{downloadProgress.toFixed(1)}%</p>
          </div>
        )}

        {updateReady && (
          <div className="mb-3 p-3 bg-green-100 rounded">
            <p className="font-semibold">Update Ready!</p>
            <p className="text-sm mt-1">Version {updateInfo?.version} is ready to install.</p>
            <button
              onClick={installUpdate}
              className="mt-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Restart and Install
            </button>
          </div>
        )}

        {!updateAvailable && !checking && (
          <button
            onClick={checkForUpdates}
            className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700"
          >
            Check for Updates
          </button>
        )}
      </section>

      {/* Keyboard Shortcuts Info */}
      <section className="mb-6 p-4 bg-indigo-50 rounded">
        <h2 className="text-xl font-semibold mb-3">Keyboard Shortcuts</h2>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>New Project:</div>
          <div className="font-mono">Ctrl/Cmd + N</div>
          <div>Save Project:</div>
          <div className="font-mono">Ctrl/Cmd + S</div>
          <div>Export PDF:</div>
          <div className="font-mono">Ctrl/Cmd + P</div>
          <div>Find:</div>
          <div className="font-mono">Ctrl/Cmd + F</div>
          <div>Dashboard:</div>
          <div className="font-mono">Ctrl/Cmd + 1</div>
          <div>Solar Calculator:</div>
          <div className="font-mono">Ctrl/Cmd + 2</div>
        </div>
      </section>

      {/* Menu Actions Info */}
      <section className="p-4 bg-teal-50 rounded">
        <h2 className="text-xl font-semibold mb-3">Menu & Tray Actions</h2>
        <p className="text-sm mb-2">
          Try using the application menu or system tray to trigger actions.
          The handlers above will respond to menu/tray events.
        </p>
        <ul className="list-disc list-inside text-sm space-y-1">
          <li>File → New Project</li>
          <li>File → Save Project</li>
          <li>File → Export → Export PDF</li>
          <li>File → Import → Import Excel</li>
          <li>System Tray → Quick Actions</li>
        </ul>
      </section>
    </div>
  );
};

export default ElectronIntegrationDemo;
