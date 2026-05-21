import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import './MenuIntegrationDemo.css';

interface KeyboardShortcut {
  action: string;
  shortcut: string;
}

interface KeyboardShortcuts {
  [category: string]: KeyboardShortcut[];
}

/**
 * MenuIntegrationDemo Component
 * 
 * Demonstrates how to integrate with the native Electron menu system:
 * - Listening for menu navigation events
 * - Handling menu actions
 * - Managing recent files
 * - Displaying keyboard shortcuts
 */
export const MenuIntegrationDemo: React.FC = () => {
  const navigate = useNavigate();
  const [shortcuts, setShortcuts] = useState<KeyboardShortcuts>({});
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [lastAction, setLastAction] = useState<string>('');
  const [lastNavigation, setLastNavigation] = useState<string>('');

  useEffect(() => {
    // Load keyboard shortcuts
    loadKeyboardShortcuts();

    // Listen for navigation events from menu
    const unsubscribeNav = window.electronAPI.onNavigate((route: string) => {
      console.log('Menu navigation:', route);
      setLastNavigation(route);
      navigate(route);
    });

    // Listen for action events from menu
    const unsubscribeAction = window.electronAPI.onAction((action: string, data?: any) => {
      console.log('Menu action:', action, data);
      setLastAction(`${action}${data ? ` (${JSON.stringify(data)})` : ''}`);
      handleMenuAction(action, data);
    });

    return () => {
      unsubscribeNav();
      unsubscribeAction();
    };
  }, [navigate]);

  const loadKeyboardShortcuts = async () => {
    try {
      const shortcuts = await window.electronAPI.getKeyboardShortcuts();
      setShortcuts(shortcuts);
    } catch (error) {
      console.error('Failed to load keyboard shortcuts:', error);
    }
  };

  const handleMenuAction = (action: string, data?: any) => {
    switch (action) {
      case 'new-project':
        handleNewProject();
        break;
      case 'open-project':
        handleOpenProject(data);
        break;
      case 'save-project':
        handleSaveProject();
        break;
      case 'save-project-as':
        handleSaveProjectAs(data);
        break;
      case 'save-all':
        handleSaveAll();
        break;
      case 'close-project':
        handleCloseProject();
        break;
      case 'import-excel':
        handleImportExcel(data);
        break;
      case 'import-csv':
        handleImportCSV(data);
        break;
      case 'import-price-matrix':
        handleImportPriceMatrix(data);
        break;
      case 'export-pdf':
        handleExportPDF();
        break;
      case 'export-excel':
        handleExportExcel();
        break;
      case 'export-3d':
        handleExport3D(data);
        break;
      case 'find':
        handleFind();
        break;
      case 'find-next':
        handleFindNext();
        break;
      case 'find-previous':
        handleFindPrevious();
        break;
      case 'replace':
        handleReplace();
        break;
      case 'toggle-sidebar':
        handleToggleSidebar();
        break;
      case 'toggle-theme':
        handleToggleTheme();
        break;
      case 'show-shortcuts':
        setShowShortcuts(true);
        break;
      case 'show-about':
        handleShowAbout();
        break;
      case 'check-updates':
        handleCheckUpdates();
        break;
      default:
        console.log('Unhandled menu action:', action);
    }
  };

  // File operations
  const handleNewProject = () => {
    console.log('Creating new project...');
    // Implement new project logic
  };

  const handleOpenProject = (projectPath?: string) => {
    console.log('Opening project:', projectPath);
    if (projectPath) {
      // Add to recent projects
      const projectName = projectPath.split(/[\\/]/).pop() || 'Unknown';
      window.electronAPI.addRecentProject(projectPath, projectName);
    }
    // Implement open project logic
  };

  const handleSaveProject = () => {
    console.log('Saving project...');
    // Implement save project logic
    // After successful save, add to recent projects
    // window.electronAPI.addRecentProject(projectPath, projectName);
  };

  const handleSaveProjectAs = (projectPath?: string) => {
    console.log('Saving project as:', projectPath);
    // Implement save as logic
  };

  const handleSaveAll = () => {
    console.log('Saving all projects...');
    // Implement save all logic
  };

  const handleCloseProject = () => {
    console.log('Closing project...');
    // Implement close project logic
  };

  // Import operations
  const handleImportExcel = (filePath?: string) => {
    console.log('Importing Excel:', filePath);
    if (filePath) {
      const fileName = filePath.split(/[\\/]/).pop() || 'Unknown';
      window.electronAPI.addRecentFile(filePath, fileName);
    }
    // Implement Excel import logic
  };

  const handleImportCSV = (filePath?: string) => {
    console.log('Importing CSV:', filePath);
    if (filePath) {
      const fileName = filePath.split(/[\\/]/).pop() || 'Unknown';
      window.electronAPI.addRecentFile(filePath, fileName);
    }
    // Implement CSV import logic
  };

  const handleImportPriceMatrix = (filePath?: string) => {
    console.log('Importing price matrix:', filePath);
    if (filePath) {
      const fileName = filePath.split(/[\\/]/).pop() || 'Unknown';
      window.electronAPI.addRecentFile(filePath, fileName);
    }
    // Implement price matrix import logic
  };

  // Export operations
  const handleExportPDF = () => {
    console.log('Exporting PDF...');
    // Implement PDF export logic
  };

  const handleExportExcel = () => {
    console.log('Exporting Excel...');
    // Implement Excel export logic
  };

  const handleExport3D = (format?: string) => {
    console.log('Exporting 3D model as:', format);
    // Implement 3D export logic
  };

  // Edit operations
  const handleFind = () => {
    console.log('Opening find dialog...');
    // Implement find logic
  };

  const handleFindNext = () => {
    console.log('Finding next...');
    // Implement find next logic
  };

  const handleFindPrevious = () => {
    console.log('Finding previous...');
    // Implement find previous logic
  };

  const handleReplace = () => {
    console.log('Opening replace dialog...');
    // Implement replace logic
  };

  // View operations
  const handleToggleSidebar = () => {
    console.log('Toggling sidebar...');
    // Implement sidebar toggle logic
  };

  const handleToggleTheme = () => {
    console.log('Toggling theme...');
    // Implement theme toggle logic
  };

  // Help operations
  const handleShowAbout = () => {
    console.log('Showing about dialog...');
    // Implement about dialog logic
  };

  const handleCheckUpdates = () => {
    console.log('Checking for updates...');
    // Implement update check logic
  };

  // Clear recent lists
  const handleClearRecentProjects = async () => {
    try {
      await window.electronAPI.clearRecentProjects();
      console.log('Recent projects cleared');
    } catch (error) {
      console.error('Failed to clear recent projects:', error);
    }
  };

  const handleClearRecentFiles = async () => {
    try {
      await window.electronAPI.clearRecentFiles();
      console.log('Recent files cleared');
    } catch (error) {
      console.error('Failed to clear recent files:', error);
    }
  };

  return (
    <div className="menu-integration-demo">
      <h1>Native Menu Integration Demo</h1>

      <div className="demo-section">
        <h2>Menu Event Monitor</h2>
        <div className="event-monitor">
          <div className="event-item">
            <strong>Last Navigation:</strong>
            <span>{lastNavigation || 'None'}</span>
          </div>
          <div className="event-item">
            <strong>Last Action:</strong>
            <span>{lastAction || 'None'}</span>
          </div>
        </div>
      </div>

      <div className="demo-section">
        <h2>Menu Actions</h2>
        <p>Try using the application menu or keyboard shortcuts to trigger actions.</p>
        <div className="action-buttons">
          <Button
            label="Show Keyboard Shortcuts"
            icon="pi pi-keyboard"
            onClick={() => setShowShortcuts(true)}
          />
          <Button
            label="Clear Recent Projects"
            icon="pi pi-trash"
            onClick={handleClearRecentProjects}
            severity="warning"
          />
          <Button
            label="Clear Recent Files"
            icon="pi pi-trash"
            onClick={handleClearRecentFiles}
            severity="warning"
          />
        </div>
      </div>

      <div className="demo-section">
        <h2>Integration Examples</h2>
        <div className="code-examples">
          <h3>Listen for Menu Navigation</h3>
          <pre><code>{`const unsubscribe = window.electronAPI.onNavigate((route) => {
  navigate(route);
});`}</code></pre>

          <h3>Listen for Menu Actions</h3>
          <pre><code>{`const unsubscribe = window.electronAPI.onAction((action, data) => {
  handleMenuAction(action, data);
});`}</code></pre>

          <h3>Add Recent Project</h3>
          <pre><code>{`await window.electronAPI.addRecentProject(
  '/path/to/project.json',
  'My Project'
);`}</code></pre>

          <h3>Get Keyboard Shortcuts</h3>
          <pre><code>{`const shortcuts = await window.electronAPI.getKeyboardShortcuts();`}</code></pre>
        </div>
      </div>

      {/* Keyboard Shortcuts Dialog */}
      <Dialog
        header="Keyboard Shortcuts"
        visible={showShortcuts}
        style={{ width: '80vw', maxWidth: '1000px' }}
        onHide={() => setShowShortcuts(false)}
        maximizable
      >
        <div className="shortcuts-dialog">
          {Object.entries(shortcuts).map(([category, items]) => (
            <div key={category} className="shortcut-category">
              <h3>{category}</h3>
              <DataTable value={items} size="small">
                <Column field="action" header="Action" />
                <Column field="shortcut" header="Shortcut" />
              </DataTable>
            </div>
          ))}
        </div>
      </Dialog>
    </div>
  );
};

export default MenuIntegrationDemo;
