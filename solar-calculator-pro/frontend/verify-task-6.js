/**
 * Task 6 Verification Script
 * 
 * Verifies that state management setup is complete:
 * - Zustand is installed and configured
 * - Auth store for user authentication state
 * - UI store for global UI state
 * - Project store for project data
 * - Store persistence with localStorage
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const results = {
  passed: [],
  failed: [],
  warnings: []
};

function checkFile(filePath, description) {
  const fullPath = path.join(__dirname, filePath);
  if (fs.existsSync(fullPath)) {
    results.passed.push(`✓ ${description}`);
    return true;
  } else {
    results.failed.push(`✗ ${description} - File not found: ${filePath}`);
    return false;
  }
}

function checkFileContent(filePath, searchStrings, description) {
  const fullPath = path.join(__dirname, filePath);
  if (!fs.existsSync(fullPath)) {
    results.failed.push(`✗ ${description} - File not found: ${filePath}`);
    return false;
  }

  const content = fs.readFileSync(fullPath, 'utf-8');
  const missingStrings = searchStrings.filter(str => !content.includes(str));

  if (missingStrings.length === 0) {
    results.passed.push(`✓ ${description}`);
    return true;
  } else {
    results.failed.push(`✗ ${description} - Missing: ${missingStrings.join(', ')}`);
    return false;
  }
}

function checkPackageJson() {
  const packagePath = path.join(__dirname, 'package.json');
  if (!fs.existsSync(packagePath)) {
    results.failed.push('✗ package.json not found');
    return false;
  }

  const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf-8'));
  const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };

  // Check for Zustand
  if (dependencies['zustand']) {
    results.passed.push(`✓ Zustand installed (${dependencies['zustand']})`);
  } else {
    results.failed.push('✗ Zustand not installed');
  }

  return true;
}

console.log('\n🔍 Verifying Task 6: State Management Setup\n');
console.log('='.repeat(60));

// 1. Check package.json for Zustand
console.log('\n📦 Checking Dependencies...');
checkPackageJson();

// 2. Check store files exist
console.log('\n📁 Checking Store Files...');
checkFile('src/store/authStore.ts', 'Auth store file exists');
checkFile('src/store/uiStore.ts', 'UI store file exists');
checkFile('src/store/projectStore.ts', 'Project store file exists');
checkFile('src/store/index.ts', 'Store index file exists');

// 3. Check auth store implementation
console.log('\n🔐 Checking Auth Store Implementation...');
checkFileContent(
  'src/store/authStore.ts',
  [
    'import { create } from \'zustand\'',
    'import { persist } from \'zustand/middleware\'',
    'interface AuthState',
    'user:',
    'isAuthenticated:',
    'setUser:',
    'logout:',
    'useAuthStore'
  ],
  'Auth store has required structure'
);

checkFileContent(
  'src/store/authStore.ts',
  ['persist(', 'name: \'auth-storage\''],
  'Auth store has persistence configured'
);

// 4. Check UI store implementation
console.log('\n🎨 Checking UI Store Implementation...');
checkFileContent(
  'src/store/uiStore.ts',
  [
    'import { create } from \'zustand\'',
    'import { persist } from \'zustand/middleware\'',
    'interface UIState',
    'sidebarCollapsed:',
    'theme:',
    'globalLoading:',
    'notifications:',
    'useUIStore'
  ],
  'UI store has required structure'
);

checkFileContent(
  'src/store/uiStore.ts',
  ['persist(', 'name: \'ui-storage\''],
  'UI store has persistence configured'
);

// 5. Check project store implementation
console.log('\n📊 Checking Project Store Implementation...');
checkFileContent(
  'src/store/projectStore.ts',
  [
    'import { create } from \'zustand\'',
    'interface Project',
    'interface ProjectState',
    'projects:',
    'currentProject:',
    'setProjects:',
    'addProject:',
    'updateProject:',
    'deleteProject:',
    'useProjectStore'
  ],
  'Project store has required structure'
);

// 6. Check store exports
console.log('\n📤 Checking Store Exports...');
checkFileContent(
  'src/store/index.ts',
  [
    'export { useAuthStore }',
    'export { useUIStore }',
    'export { useProjectStore }'
  ],
  'All stores are exported from index'
);

// 7. Check TypeScript types
console.log('\n📝 Checking TypeScript Types...');
checkFileContent(
  'src/store/authStore.ts',
  ['interface AuthState', 'User'],
  'Auth store has proper TypeScript types'
);

checkFileContent(
  'src/store/projectStore.ts',
  ['export interface Project', 'interface ProjectState'],
  'Project store has proper TypeScript types'
);

// 8. Check persistence configuration
console.log('\n💾 Checking Persistence Configuration...');
checkFileContent(
  'src/store/authStore.ts',
  ['partialize:', 'user:', 'isAuthenticated:'],
  'Auth store has selective persistence (partialize)'
);

checkFileContent(
  'src/store/uiStore.ts',
  ['partialize:', 'sidebarCollapsed:', 'theme:'],
  'UI store has selective persistence (partialize)'
);

// 9. Check store actions
console.log('\n⚡ Checking Store Actions...');
checkFileContent(
  'src/store/authStore.ts',
  ['setUser:', 'setLoading:', 'setError:', 'logout:'],
  'Auth store has all required actions'
);

checkFileContent(
  'src/store/uiStore.ts',
  [
    'toggleSidebar:',
    'setSidebarCollapsed:',
    'setTheme:',
    'setGlobalLoading:',
    'addNotification:',
    'removeNotification:'
  ],
  'UI store has all required actions'
);

checkFileContent(
  'src/store/projectStore.ts',
  [
    'setProjects:',
    'setCurrentProject:',
    'addProject:',
    'updateProject:',
    'deleteProject:',
    'setLoading:',
    'setError:'
  ],
  'Project store has all required actions'
);

// Print results
console.log('\n' + '='.repeat(60));
console.log('\n📊 VERIFICATION RESULTS\n');

if (results.passed.length > 0) {
  console.log('✅ PASSED CHECKS:');
  results.passed.forEach(msg => console.log(`   ${msg}`));
}

if (results.warnings.length > 0) {
  console.log('\n⚠️  WARNINGS:');
  results.warnings.forEach(msg => console.log(`   ${msg}`));
}

if (results.failed.length > 0) {
  console.log('\n❌ FAILED CHECKS:');
  results.failed.forEach(msg => console.log(`   ${msg}`));
}

console.log('\n' + '='.repeat(60));
console.log(`\n📈 Summary: ${results.passed.length} passed, ${results.failed.length} failed, ${results.warnings.length} warnings\n`);

if (results.failed.length === 0) {
  console.log('✅ Task 6: State Management Setup - COMPLETE\n');
  process.exit(0);
} else {
  console.log('❌ Task 6: State Management Setup - INCOMPLETE\n');
  process.exit(1);
}
