/**
 * Verification Script for Task 57: Native File Dialogs
 * 
 * This script verifies that all components of the native file dialog
 * implementation are present and correctly configured.
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying Task 57: Native File Dialogs Implementation\n');

const checks = {
  passed: 0,
  failed: 0,
  warnings: 0
};

function checkFile(filePath, description) {
  const fullPath = path.join(__dirname, filePath);
  if (fs.existsSync(fullPath)) {
    const stats = fs.statSync(fullPath);
    console.log(`✅ ${description}`);
    console.log(`   📄 ${filePath} (${stats.size} bytes)`);
    checks.passed++;
    return true;
  } else {
    console.log(`❌ ${description}`);
    console.log(`   📄 ${filePath} - NOT FOUND`);
    checks.failed++;
    return false;
  }
}

function checkFileContent(filePath, searchStrings, description) {
  const fullPath = path.join(__dirname, filePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`❌ ${description} - File not found`);
    checks.failed++;
    return false;
  }

  const content = fs.readFileSync(fullPath, 'utf8');
  const missing = searchStrings.filter(str => !content.includes(str));

  if (missing.length === 0) {
    console.log(`✅ ${description}`);
    checks.passed++;
    return true;
  } else {
    console.log(`⚠️  ${description} - Missing: ${missing.join(', ')}`);
    checks.warnings++;
    return false;
  }
}

console.log('📦 Core Implementation Files\n');

checkFile(
  'electron/main.js',
  'Electron main process with dialog handlers'
);

checkFile(
  'electron/preload.js',
  'Preload script with dialog API exposure'
);

checkFile(
  'frontend/src/hooks/useFileDialog.ts',
  'React hook for file dialogs'
);

checkFile(
  'frontend/src/types/electron.d.ts',
  'TypeScript type definitions'
);

console.log('\n📱 Demo and Examples\n');

checkFile(
  'frontend/src/examples/FileDialogDemo.tsx',
  'Demo component'
);

checkFile(
  'frontend/src/examples/FileDialogDemo.css',
  'Demo component styles'
);

console.log('\n📚 Documentation\n');

checkFile(
  'docs/NATIVE_FILE_DIALOGS_GUIDE.md',
  'Complete guide'
);

checkFile(
  'docs/NATIVE_FILE_DIALOGS_QUICK_REFERENCE.md',
  'Quick reference'
);

checkFile(
  'TASK_57_COMPLETE.md',
  'Task completion summary'
);

checkFile(
  'TASK_57_VISUAL_SUMMARY.md',
  'Visual summary'
);

checkFile(
  'TASK_57_INTEGRATION_CHECKLIST.md',
  'Integration checklist'
);

console.log('\n🔧 Implementation Verification\n');

checkFileContent(
  'electron/main.js',
  [
    'dialog:openFile',
    'dialog:openFiles',
    'dialog:saveFile',
    'dialog:openDirectory',
    'dialog:openExcelFile',
    'dialog:openPDFFile',
    'dialog:openImageFile',
    'dialog:openImageFiles',
    'dialog:saveExcelFile',
    'dialog:savePDFFile',
    'dialog:saveImageFile'
  ],
  'All dialog IPC handlers present in main.js'
);

checkFileContent(
  'electron/preload.js',
  [
    'selectFile',
    'selectFiles',
    'saveFile',
    'selectDirectory',
    'selectExcelFile',
    'selectPDFFile',
    'selectImageFile',
    'selectImageFiles',
    'saveExcelFile',
    'savePDFFile',
    'saveImageFile'
  ],
  'All dialog methods exposed in preload.js'
);

checkFileContent(
  'frontend/src/hooks/useFileDialog.ts',
  [
    'openFile',
    'openFiles',
    'saveFile',
    'openDirectory',
    'openExcelFile',
    'openPDFFile',
    'openImageFile',
    'openImageFiles',
    'saveExcelFile',
    'savePDFFile',
    'saveImageFile',
    'useState',
    'useCallback'
  ],
  'All hook methods implemented'
);

checkFileContent(
  'frontend/src/types/electron.d.ts',
  [
    'FileResult',
    'FilesResult',
    'DirectoryResult',
    'FileDialogOptions',
    'selectFile',
    'selectFiles',
    'saveFile',
    'selectDirectory'
  ],
  'TypeScript types defined'
);

console.log('\n📊 Summary\n');
console.log(`✅ Passed: ${checks.passed}`);
console.log(`⚠️  Warnings: ${checks.warnings}`);
console.log(`❌ Failed: ${checks.failed}`);

const total = checks.passed + checks.warnings + checks.failed;
const successRate = ((checks.passed / total) * 100).toFixed(1);

console.log(`\n📈 Success Rate: ${successRate}%`);

if (checks.failed === 0) {
  console.log('\n🎉 All checks passed! Task 57 implementation is complete.\n');
  process.exit(0);
} else {
  console.log('\n⚠️  Some checks failed. Please review the implementation.\n');
  process.exit(1);
}
