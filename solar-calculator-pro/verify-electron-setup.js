#!/usr/bin/env node

/**
 * Verification script for Electron Application Setup (Task 7)
 * 
 * This script verifies that all Electron components are properly configured:
 * - Main process with security settings
 * - Preload script with IPC bridge
 * - Application menu
 * - System tray
 * - Auto-updater
 * - Backend manager
 */

const fs = require('fs');
const path = require('path');

const COLORS = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${COLORS[color]}${message}${COLORS.reset}`);
}

function checkFileExists(filePath, description) {
  const fullPath = path.join(__dirname, filePath);
  if (fs.existsSync(fullPath)) {
    log(`✓ ${description}`, 'green');
    return true;
  } else {
    log(`✗ ${description} - File not found: ${filePath}`, 'red');
    return false;
  }
}

function checkFileContains(filePath, searchStrings, description) {
  const fullPath = path.join(__dirname, filePath);
  if (!fs.existsSync(fullPath)) {
    log(`✗ ${description} - File not found: ${filePath}`, 'red');
    return false;
  }

  const content = fs.readFileSync(fullPath, 'utf8');
  const missing = searchStrings.filter(str => !content.includes(str));

  if (missing.length === 0) {
    log(`✓ ${description}`, 'green');
    return true;
  } else {
    log(`✗ ${description} - Missing: ${missing.join(', ')}`, 'red');
    return false;
  }
}

function checkPackageJson() {
  const packagePath = path.join(__dirname, 'package.json');
  if (!fs.existsSync(packagePath)) {
    log('✗ package.json not found', 'red');
    return false;
  }

  const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  const requiredDeps = ['axios', 'electron-log', 'electron-store', 'electron-updater'];
  const missing = requiredDeps.filter(dep => !packageJson.dependencies[dep]);

  if (missing.length === 0) {
    log('✓ All required dependencies present in package.json', 'green');
    return true;
  } else {
    log(`✗ Missing dependencies: ${missing.join(', ')}`, 'red');
    return false;
  }
}

function runVerification() {
  log('\n=== Electron Application Setup Verification ===\n', 'cyan');

  let passed = 0;
  let failed = 0;

  // Check file existence
  log('Checking file structure...', 'blue');
  const files = [
    ['electron/main.js', 'Main process file'],
    ['electron/preload.js', 'Preload script'],
    ['electron/backend-manager.js', 'Backend manager'],
    ['electron/menu.js', 'Application menu'],
    ['electron/tray.js', 'System tray'],
    ['electron/updater.js', 'Auto-updater']
  ];

  files.forEach(([file, desc]) => {
    if (checkFileExists(file, desc)) {
      passed++;
    } else {
      failed++;
    }
  });

  log('\nChecking main.js configuration...', 'blue');
  const mainChecks = [
    ['electron/main.js', ['contextIsolation: true', 'nodeIntegration: false', 'sandbox: true'], 'Security settings'],
    ['electron/main.js', ['Content-Security-Policy'], 'CSP implementation'],
    ['electron/main.js', ['createApplicationMenu', 'createTray', 'setupAutoUpdater'], 'Component integrations'],
    ['electron/main.js', ['ipcMain.handle', 'ipcMain.on'], 'IPC handlers']
  ];

  mainChecks.forEach(([file, strings, desc]) => {
    if (checkFileContains(file, strings, desc)) {
      passed++;
    } else {
      failed++;
    }
  });

  log('\nChecking preload.js configuration...', 'blue');
  const preloadChecks = [
    ['electron/preload.js', ['contextBridge.exposeInMainWorld', 'electronAPI'], 'Context bridge'],
    ['electron/preload.js', ['selectFile', 'saveFile', 'selectDirectory'], 'File operations'],
    ['electron/preload.js', ['getBackendUrl', 'checkBackendHealth'], 'Backend communication'],
    ['electron/preload.js', ['onUpdateAvailable', 'onUpdateDownloaded', 'onUpdateProgress'], 'Update events'],
    ['electron/preload.js', ['onNavigate', 'onAction'], 'Menu/tray events']
  ];

  preloadChecks.forEach(([file, strings, desc]) => {
    if (checkFileContains(file, strings, desc)) {
      passed++;
    } else {
      failed++;
    }
  });

  log('\nChecking menu.js configuration...', 'blue');
  const menuChecks = [
    ['electron/menu.js', ['Menu.buildFromTemplate', 'createApplicationMenu'], 'Menu creation'],
    ['electron/menu.js', ['File', 'Edit', 'View', 'Window', 'Help'], 'Menu structure'],
    ['electron/menu.js', ['accelerator', 'CmdOrCtrl'], 'Keyboard shortcuts']
  ];

  menuChecks.forEach(([file, strings, desc]) => {
    if (checkFileContains(file, strings, desc)) {
      passed++;
    } else {
      failed++;
    }
  });

  log('\nChecking tray.js configuration...', 'blue');
  const trayChecks = [
    ['electron/tray.js', ['new Tray', 'setContextMenu'], 'Tray creation'],
    ['electron/tray.js', ['updateTrayMenu', 'showNotification'], 'Tray functions'],
    ['electron/tray.js', ['click', 'double-click'], 'Tray events']
  ];

  trayChecks.forEach(([file, strings, desc]) => {
    if (checkFileContains(file, strings, desc)) {
      passed++;
    } else {
      failed++;
    }
  });

  log('\nChecking updater.js configuration...', 'blue');
  const updaterChecks = [
    ['electron/updater.js', ['autoUpdater', 'electron-updater'], 'Auto-updater import'],
    ['electron/updater.js', ['update-available', 'update-downloaded', 'download-progress'], 'Update events'],
    ['electron/updater.js', ['checkForUpdates', 'downloadUpdate'], 'Update functions'],
    ['electron/updater.js', ['electron-log'], 'Logging']
  ];

  updaterChecks.forEach(([file, strings, desc]) => {
    if (checkFileContains(file, strings, desc)) {
      passed++;
    } else {
      failed++;
    }
  });

  log('\nChecking package.json...', 'blue');
  if (checkPackageJson()) {
    passed++;
  } else {
    failed++;
  }

  log('\nChecking documentation...', 'blue');
  const docFiles = [
    ['TASK_7_COMPLETE.md', 'Task completion documentation'],
    ['docs/ELECTRON_SETUP_QUICK_REFERENCE.md', 'Quick reference guide']
  ];

  docFiles.forEach(([file, desc]) => {
    if (checkFileExists(file, desc)) {
      passed++;
    } else {
      failed++;
    }
  });

  // Summary
  log('\n=== Verification Summary ===\n', 'cyan');
  log(`Passed: ${passed}`, 'green');
  log(`Failed: ${failed}`, failed > 0 ? 'red' : 'green');
  log(`Total: ${passed + failed}`, 'blue');

  const percentage = ((passed / (passed + failed)) * 100).toFixed(1);
  log(`\nCompletion: ${percentage}%`, percentage === '100.0' ? 'green' : 'yellow');

  if (failed === 0) {
    log('\n✓ All checks passed! Electron setup is complete.', 'green');
    log('\nNext steps:', 'cyan');
    log('1. Install dependencies: npm install', 'blue');
    log('2. Create icon files in assets/ directory', 'blue');
    log('3. Test the application: npm run electron:dev', 'blue');
    log('4. Configure auto-updater with your update server', 'blue');
    return 0;
  } else {
    log('\n✗ Some checks failed. Please review the errors above.', 'red');
    return 1;
  }
}

// Run verification
const exitCode = runVerification();
process.exit(exitCode);
