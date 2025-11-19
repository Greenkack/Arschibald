const { Tray, Menu, app, nativeImage } = require('electron');
const path = require('path');

let tray = null;

function createTray(mainWindow) {
  // Create tray icon
  const iconPath = path.join(__dirname, '../assets/tray-icon.png');
  let icon;
  
  try {
    icon = nativeImage.createFromPath(iconPath);
    // Resize for tray (16x16 on Windows, 22x22 on macOS)
    if (process.platform === 'darwin') {
      icon = icon.resize({ width: 22, height: 22 });
    } else {
      icon = icon.resize({ width: 16, height: 16 });
    }
  } catch (error) {
    console.warn('Tray icon not found, using default');
    // Create a simple colored square as fallback
    icon = nativeImage.createEmpty();
  }

  tray = new Tray(icon);

  // Set tooltip
  tray.setToolTip('Solar Calculator Pro');

  // Create context menu
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Dashboard',
      click: () => {
        showWindow(mainWindow);
        mainWindow.webContents.send('navigate', '/dashboard');
      }
    },
    {
      label: 'New Calculation',
      click: () => {
        showWindow(mainWindow);
        mainWindow.webContents.send('action', 'new-project');
      }
    },
    { type: 'separator' },
    {
      label: 'Quick Actions',
      submenu: [
        {
          label: 'Solar Calculator',
          click: () => {
            showWindow(mainWindow);
            mainWindow.webContents.send('navigate', '/solar');
          }
        },
        {
          label: 'Heat Pump',
          click: () => {
            showWindow(mainWindow);
            mainWindow.webContents.send('navigate', '/heatpump');
          }
        },
        {
          label: 'CRM',
          click: () => {
            showWindow(mainWindow);
            mainWindow.webContents.send('navigate', '/crm');
          }
        }
      ]
    },
    { type: 'separator' },
    {
      label: 'Show Window',
      click: () => {
        showWindow(mainWindow);
      }
    },
    {
      label: 'Hide Window',
      click: () => {
        if (mainWindow) {
          mainWindow.hide();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Settings',
      click: () => {
        showWindow(mainWindow);
        mainWindow.webContents.send('navigate', '/settings');
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.quit();
      }
    }
  ]);

  tray.setContextMenu(contextMenu);

  // Handle tray click
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        showWindow(mainWindow);
      }
    }
  });

  // Handle double click (Windows/Linux)
  tray.on('double-click', () => {
    showWindow(mainWindow);
  });

  return tray;
}

function showWindow(mainWindow) {
  if (mainWindow) {
    if (mainWindow.isMinimized()) {
      mainWindow.restore();
    }
    mainWindow.show();
    mainWindow.focus();
  }
}

function updateTrayMenu(mainWindow, recentProjects = []) {
  if (!tray) return;

  const recentProjectsMenu = recentProjects.length > 0
    ? recentProjects.map(project => ({
        label: project.name,
        click: () => {
          showWindow(mainWindow);
          mainWindow.webContents.send('action', 'open-project', project.id);
        }
      }))
    : [{ label: 'No recent projects', enabled: false }];

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Dashboard',
      click: () => {
        showWindow(mainWindow);
        mainWindow.webContents.send('navigate', '/dashboard');
      }
    },
    {
      label: 'New Calculation',
      click: () => {
        showWindow(mainWindow);
        mainWindow.webContents.send('action', 'new-project');
      }
    },
    { type: 'separator' },
    {
      label: 'Recent Projects',
      submenu: recentProjectsMenu
    },
    { type: 'separator' },
    {
      label: 'Quick Actions',
      submenu: [
        {
          label: 'Solar Calculator',
          click: () => {
            showWindow(mainWindow);
            mainWindow.webContents.send('navigate', '/solar');
          }
        },
        {
          label: 'Heat Pump',
          click: () => {
            showWindow(mainWindow);
            mainWindow.webContents.send('navigate', '/heatpump');
          }
        },
        {
          label: 'CRM',
          click: () => {
            showWindow(mainWindow);
            mainWindow.webContents.send('navigate', '/crm');
          }
        }
      ]
    },
    { type: 'separator' },
    {
      label: 'Show Window',
      click: () => {
        showWindow(mainWindow);
      }
    },
    {
      label: 'Hide Window',
      click: () => {
        if (mainWindow) {
          mainWindow.hide();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Settings',
      click: () => {
        showWindow(mainWindow);
        mainWindow.webContents.send('navigate', '/settings');
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.quit();
      }
    }
  ]);

  tray.setContextMenu(contextMenu);
}

function showNotification(title, body) {
  if (tray) {
    tray.displayBalloon({
      title,
      content: body,
      icon: path.join(__dirname, '../assets/icon.png')
    });
  }
}

function destroyTray() {
  if (tray) {
    tray.destroy();
    tray = null;
  }
}

module.exports = {
  createTray,
  updateTrayMenu,
  showNotification,
  destroyTray
};
