const { Menu, shell, app, dialog } = require('electron');
const Store = require('electron-store');

// Store for recent files and menu state
const store = new Store({
  name: 'menu-state',
  defaults: {
    recentProjects: [],
    recentFiles: [],
    maxRecentItems: 10
  }
});

// Menu state manager
class MenuStateManager {
  constructor() {
    this.recentProjects = store.get('recentProjects', []);
    this.recentFiles = store.get('recentFiles', []);
    this.maxRecentItems = store.get('maxRecentItems', 10);
  }

  addRecentProject(projectPath, projectName) {
    const item = { path: projectPath, name: projectName, timestamp: Date.now() };
    this.recentProjects = [
      item,
      ...this.recentProjects.filter(p => p.path !== projectPath)
    ].slice(0, this.maxRecentItems);
    store.set('recentProjects', this.recentProjects);
  }

  addRecentFile(filePath, fileName) {
    const item = { path: filePath, name: fileName, timestamp: Date.now() };
    this.recentFiles = [
      item,
      ...this.recentFiles.filter(f => f.path !== filePath)
    ].slice(0, this.maxRecentItems);
    store.set('recentFiles', this.recentFiles);
  }

  clearRecentProjects() {
    this.recentProjects = [];
    store.set('recentProjects', []);
  }

  clearRecentFiles() {
    this.recentFiles = [];
    store.set('recentFiles', []);
  }

  getRecentProjects() {
    return this.recentProjects;
  }

  getRecentFiles() {
    return this.recentFiles;
  }
}

const menuState = new MenuStateManager();

function createApplicationMenu(mainWindow) {
  const isMac = process.platform === 'darwin';

  const template = [
    // App Menu (macOS only)
    ...(isMac ? [{
      label: app.name,
      submenu: [
        { 
          role: 'about',
          label: `About ${app.name}`
        },
        { type: 'separator' },
        {
          label: 'Preferences...',
          accelerator: 'Cmd+,',
          click: () => {
            mainWindow.webContents.send('navigate', '/settings');
          }
        },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    }] : []),

    // File Menu
    {
      label: 'File',
      submenu: [
        {
          label: 'New Project',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('action', 'new-project');
          }
        },
        {
          label: 'Open Project...',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog(mainWindow, {
              properties: ['openFile'],
              filters: [
                { name: 'Project Files', extensions: ['json', 'scp'] },
                { name: 'All Files', extensions: ['*'] }
              ]
            });
            if (!result.canceled && result.filePaths.length > 0) {
              mainWindow.webContents.send('action', 'open-project', result.filePaths[0]);
              menuState.addRecentProject(result.filePaths[0], result.filePaths[0].split(/[\\/]/).pop());
              updateMenu(mainWindow);
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Save Project',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            mainWindow.webContents.send('action', 'save-project');
          }
        },
        {
          label: 'Save As...',
          accelerator: 'CmdOrCtrl+Shift+S',
          click: async () => {
            const result = await dialog.showSaveDialog(mainWindow, {
              defaultPath: 'project.json',
              filters: [
                { name: 'Project Files', extensions: ['json', 'scp'] },
                { name: 'All Files', extensions: ['*'] }
              ]
            });
            if (!result.canceled && result.filePath) {
              mainWindow.webContents.send('action', 'save-project-as', result.filePath);
            }
          }
        },
        {
          label: 'Save All',
          accelerator: 'CmdOrCtrl+Alt+S',
          click: () => {
            mainWindow.webContents.send('action', 'save-all');
          }
        },
        { type: 'separator' },
        {
          label: 'Close Project',
          accelerator: 'CmdOrCtrl+W',
          click: () => {
            mainWindow.webContents.send('action', 'close-project');
          }
        },
        { type: 'separator' },
        {
          label: 'Import',
          submenu: [
            {
              label: 'Import Excel...',
              accelerator: 'CmdOrCtrl+Shift+I',
              click: async () => {
                const result = await dialog.showOpenDialog(mainWindow, {
                  properties: ['openFile'],
                  filters: [
                    { name: 'Excel Files', extensions: ['xlsx', 'xls'] }
                  ]
                });
                if (!result.canceled && result.filePaths.length > 0) {
                  mainWindow.webContents.send('action', 'import-excel', result.filePaths[0]);
                  menuState.addRecentFile(result.filePaths[0], result.filePaths[0].split(/[\\/]/).pop());
                  updateMenu(mainWindow);
                }
              }
            },
            {
              label: 'Import CSV...',
              click: async () => {
                const result = await dialog.showOpenDialog(mainWindow, {
                  properties: ['openFile'],
                  filters: [
                    { name: 'CSV Files', extensions: ['csv'] }
                  ]
                });
                if (!result.canceled && result.filePaths.length > 0) {
                  mainWindow.webContents.send('action', 'import-csv', result.filePaths[0]);
                  menuState.addRecentFile(result.filePaths[0], result.filePaths[0].split(/[\\/]/).pop());
                  updateMenu(mainWindow);
                }
              }
            },
            {
              label: 'Import Price Matrix...',
              click: async () => {
                const result = await dialog.showOpenDialog(mainWindow, {
                  properties: ['openFile'],
                  filters: [
                    { name: 'Excel Files', extensions: ['xlsx', 'xls'] },
                    { name: 'CSV Files', extensions: ['csv'] }
                  ]
                });
                if (!result.canceled && result.filePaths.length > 0) {
                  mainWindow.webContents.send('action', 'import-price-matrix', result.filePaths[0]);
                  menuState.addRecentFile(result.filePaths[0], result.filePaths[0].split(/[\\/]/).pop());
                  updateMenu(mainWindow);
                }
              }
            },
            {
              label: 'Import Product Database...',
              click: async () => {
                const result = await dialog.showOpenDialog(mainWindow, {
                  properties: ['openFile'],
                  filters: [
                    { name: 'Database Files', extensions: ['db', 'sqlite', 'sqlite3'] },
                    { name: 'Excel Files', extensions: ['xlsx', 'xls'] }
                  ]
                });
                if (!result.canceled && result.filePaths.length > 0) {
                  mainWindow.webContents.send('action', 'import-products', result.filePaths[0]);
                }
              }
            }
          ]
        },
        {
          label: 'Export',
          submenu: [
            {
              label: 'Export PDF...',
              accelerator: 'CmdOrCtrl+P',
              click: () => {
                mainWindow.webContents.send('action', 'export-pdf');
              }
            },
            {
              label: 'Export Excel...',
              accelerator: 'CmdOrCtrl+E',
              click: () => {
                mainWindow.webContents.send('action', 'export-excel');
              }
            },
            {
              label: 'Export 3D Model...',
              submenu: [
                {
                  label: 'Export as STL...',
                  click: () => {
                    mainWindow.webContents.send('action', 'export-3d', 'stl');
                  }
                },
                {
                  label: 'Export as OBJ...',
                  click: () => {
                    mainWindow.webContents.send('action', 'export-3d', 'obj');
                  }
                },
                {
                  label: 'Export as GLTF...',
                  click: () => {
                    mainWindow.webContents.send('action', 'export-3d', 'gltf');
                  }
                }
              ]
            },
            {
              label: 'Export Report...',
              click: () => {
                mainWindow.webContents.send('action', 'export-report');
              }
            }
          ]
        },
        { type: 'separator' },
        {
          label: 'Recent Projects',
          submenu: buildRecentProjectsMenu(mainWindow)
        },
        {
          label: 'Recent Files',
          submenu: buildRecentFilesMenu(mainWindow)
        },
        { type: 'separator' },
        {
          label: 'Page Setup...',
          click: () => {
            mainWindow.webContents.send('action', 'page-setup');
          }
        },
        {
          label: 'Print...',
          accelerator: 'CmdOrCtrl+Shift+P',
          click: () => {
            mainWindow.webContents.print();
          }
        },
        { type: 'separator' },
        isMac ? { role: 'close' } : { role: 'quit' }
      ]
    },

    // Edit Menu
    {
      label: 'Edit',
      submenu: [
        { 
          role: 'undo',
          accelerator: 'CmdOrCtrl+Z'
        },
        { 
          role: 'redo',
          accelerator: isMac ? 'Cmd+Shift+Z' : 'Ctrl+Y'
        },
        { type: 'separator' },
        { 
          role: 'cut',
          accelerator: 'CmdOrCtrl+X'
        },
        { 
          role: 'copy',
          accelerator: 'CmdOrCtrl+C'
        },
        { 
          role: 'paste',
          accelerator: 'CmdOrCtrl+V'
        },
        ...(isMac ? [
          { 
            role: 'pasteAndMatchStyle',
            accelerator: 'Cmd+Shift+V'
          },
          { role: 'delete' },
          { 
            role: 'selectAll',
            accelerator: 'Cmd+A'
          },
          { type: 'separator' },
          {
            label: 'Speech',
            submenu: [
              { role: 'startSpeaking' },
              { role: 'stopSpeaking' }
            ]
          }
        ] : [
          { role: 'delete' },
          { type: 'separator' },
          { 
            role: 'selectAll',
            accelerator: 'Ctrl+A'
          }
        ]),
        { type: 'separator' },
        {
          label: 'Find',
          accelerator: 'CmdOrCtrl+F',
          click: () => {
            mainWindow.webContents.send('action', 'find');
          }
        },
        {
          label: 'Find Next',
          accelerator: isMac ? 'Cmd+G' : 'F3',
          click: () => {
            mainWindow.webContents.send('action', 'find-next');
          }
        },
        {
          label: 'Find Previous',
          accelerator: isMac ? 'Cmd+Shift+G' : 'Shift+F3',
          click: () => {
            mainWindow.webContents.send('action', 'find-previous');
          }
        },
        {
          label: 'Replace',
          accelerator: 'CmdOrCtrl+H',
          click: () => {
            mainWindow.webContents.send('action', 'replace');
          }
        },
        { type: 'separator' },
        {
          label: 'Preferences...',
          accelerator: isMac ? 'Cmd+,' : 'Ctrl+,',
          click: () => {
            mainWindow.webContents.send('navigate', '/settings');
          }
        }
      ]
    },

    // View Menu
    {
      label: 'View',
      submenu: [
        {
          label: 'Dashboard',
          accelerator: 'CmdOrCtrl+1',
          click: () => {
            mainWindow.webContents.send('navigate', '/dashboard');
          }
        },
        {
          label: 'Solar Calculator',
          accelerator: 'CmdOrCtrl+2',
          click: () => {
            mainWindow.webContents.send('navigate', '/solar');
          }
        },
        {
          label: 'Heat Pump',
          accelerator: 'CmdOrCtrl+3',
          click: () => {
            mainWindow.webContents.send('navigate', '/heatpump');
          }
        },
        {
          label: 'Combined System',
          accelerator: 'CmdOrCtrl+4',
          click: () => {
            mainWindow.webContents.send('navigate', '/combined');
          }
        },
        {
          label: 'CRM',
          accelerator: 'CmdOrCtrl+5',
          click: () => {
            mainWindow.webContents.send('navigate', '/crm');
          }
        },
        {
          label: 'Products',
          accelerator: 'CmdOrCtrl+6',
          click: () => {
            mainWindow.webContents.send('navigate', '/products');
          }
        },
        {
          label: 'Price Matrix',
          accelerator: 'CmdOrCtrl+7',
          click: () => {
            mainWindow.webContents.send('navigate', '/price-matrix');
          }
        },
        {
          label: 'PDF Generation',
          accelerator: 'CmdOrCtrl+8',
          click: () => {
            mainWindow.webContents.send('navigate', '/pdf');
          }
        },
        {
          label: '3D Visualization',
          accelerator: 'CmdOrCtrl+9',
          click: () => {
            mainWindow.webContents.send('navigate', '/3d');
          }
        },
        { type: 'separator' },
        {
          label: 'Go Back',
          accelerator: 'CmdOrCtrl+[',
          click: () => {
            mainWindow.webContents.goBack();
          }
        },
        {
          label: 'Go Forward',
          accelerator: 'CmdOrCtrl+]',
          click: () => {
            mainWindow.webContents.goForward();
          }
        },
        { type: 'separator' },
        {
          label: 'Reload',
          accelerator: 'CmdOrCtrl+R',
          role: 'reload'
        },
        {
          label: 'Force Reload',
          accelerator: 'CmdOrCtrl+Shift+R',
          role: 'forceReload'
        },
        {
          label: 'Toggle Developer Tools',
          accelerator: isMac ? 'Alt+Cmd+I' : 'Ctrl+Shift+I',
          role: 'toggleDevTools'
        },
        { type: 'separator' },
        {
          label: 'Actual Size',
          accelerator: 'CmdOrCtrl+0',
          role: 'resetZoom'
        },
        {
          label: 'Zoom In',
          accelerator: 'CmdOrCtrl+Plus',
          role: 'zoomIn'
        },
        {
          label: 'Zoom Out',
          accelerator: 'CmdOrCtrl+-',
          role: 'zoomOut'
        },
        { type: 'separator' },
        {
          label: 'Toggle Full Screen',
          accelerator: isMac ? 'Ctrl+Cmd+F' : 'F11',
          role: 'togglefullscreen'
        },
        {
          label: 'Toggle Sidebar',
          accelerator: 'CmdOrCtrl+B',
          click: () => {
            mainWindow.webContents.send('action', 'toggle-sidebar');
          }
        },
        {
          label: 'Toggle Theme',
          accelerator: 'CmdOrCtrl+T',
          click: () => {
            mainWindow.webContents.send('action', 'toggle-theme');
          }
        }
      ]
    },

    // Window Menu
    {
      label: 'Window',
      submenu: [
        {
          label: 'Minimize',
          accelerator: 'CmdOrCtrl+M',
          role: 'minimize'
        },
        {
          label: 'Zoom',
          role: 'zoom'
        },
        ...(isMac ? [
          { type: 'separator' },
          {
            label: 'Bring All to Front',
            role: 'front'
          },
          { type: 'separator' },
          { role: 'window' }
        ] : [
          {
            label: 'Close',
            accelerator: 'Alt+F4',
            role: 'close'
          }
        ]),
        { type: 'separator' },
        {
          label: 'Always on Top',
          type: 'checkbox',
          checked: false,
          click: (menuItem) => {
            mainWindow.setAlwaysOnTop(menuItem.checked);
          }
        }
      ]
    },

    // Help Menu
    {
      role: 'help',
      submenu: [
        {
          label: 'Documentation',
          accelerator: 'F1',
          click: async () => {
            await shell.openExternal('https://docs.example.com');
          }
        },
        {
          label: 'Getting Started Guide',
          click: () => {
            mainWindow.webContents.send('action', 'show-getting-started');
          }
        },
        {
          label: 'Video Tutorials',
          click: async () => {
            await shell.openExternal('https://tutorials.example.com');
          }
        },
        {
          label: 'Keyboard Shortcuts',
          accelerator: 'CmdOrCtrl+/',
          click: () => {
            mainWindow.webContents.send('action', 'show-shortcuts');
          }
        },
        { type: 'separator' },
        {
          label: 'Search Help',
          accelerator: 'CmdOrCtrl+Shift+H',
          click: () => {
            mainWindow.webContents.send('action', 'search-help');
          }
        },
        {
          label: 'FAQ',
          click: () => {
            mainWindow.webContents.send('action', 'show-faq');
          }
        },
        { type: 'separator' },
        {
          label: 'Report Issue',
          click: async () => {
            await shell.openExternal('https://github.com/example/issues');
          }
        },
        {
          label: 'Send Feedback',
          click: () => {
            mainWindow.webContents.send('action', 'send-feedback');
          }
        },
        { type: 'separator' },
        {
          label: 'Check for Updates...',
          click: () => {
            mainWindow.webContents.send('action', 'check-updates');
          }
        },
        {
          label: 'Release Notes',
          click: async () => {
            await shell.openExternal('https://releases.example.com');
          }
        },
        { type: 'separator' },
        {
          label: 'View License',
          click: () => {
            mainWindow.webContents.send('action', 'show-license');
          }
        },
        {
          label: 'Privacy Policy',
          click: async () => {
            await shell.openExternal('https://privacy.example.com');
          }
        },
        { type: 'separator' },
        {
          label: `About ${app.name}`,
          click: () => {
            mainWindow.webContents.send('action', 'show-about');
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  return menu;
}

// Build recent projects submenu
function buildRecentProjectsMenu(mainWindow) {
  const recentProjects = menuState.getRecentProjects();
  
  if (recentProjects.length === 0) {
    return [
      { label: 'No recent projects', enabled: false }
    ];
  }

  const projectItems = recentProjects.map((project, index) => ({
    label: `${index + 1}. ${project.name}`,
    accelerator: index < 9 ? `CmdOrCtrl+Alt+${index + 1}` : undefined,
    click: () => {
      mainWindow.webContents.send('action', 'open-project', project.path);
    }
  }));

  return [
    ...projectItems,
    { type: 'separator' },
    {
      label: 'Clear Recent Projects',
      click: () => {
        menuState.clearRecentProjects();
        updateMenu(mainWindow);
      }
    }
  ];
}

// Build recent files submenu
function buildRecentFilesMenu(mainWindow) {
  const recentFiles = menuState.getRecentFiles();
  
  if (recentFiles.length === 0) {
    return [
      { label: 'No recent files', enabled: false }
    ];
  }

  const fileItems = recentFiles.map((file, index) => ({
    label: `${index + 1}. ${file.name}`,
    click: () => {
      mainWindow.webContents.send('action', 'open-file', file.path);
    }
  }));

  return [
    ...fileItems,
    { type: 'separator' },
    {
      label: 'Clear Recent Files',
      click: () => {
        menuState.clearRecentFiles();
        updateMenu(mainWindow);
      }
    }
  ];
}

// Update menu (rebuild with current state)
function updateMenu(mainWindow) {
  createApplicationMenu(mainWindow);
}

// Context menu for text inputs
function createContextMenu(params = {}) {
  const { selectionText, editFlags } = params;
  const hasSelection = selectionText && selectionText.length > 0;

  return Menu.buildFromTemplate([
    {
      label: 'Undo',
      role: 'undo',
      enabled: editFlags && editFlags.canUndo,
      accelerator: 'CmdOrCtrl+Z'
    },
    {
      