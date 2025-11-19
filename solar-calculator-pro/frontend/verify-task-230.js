/**
 * Verification Script for Task 230
 * 
 * Verifies that all components of the Universal Data Service are properly implemented
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔍 Verifying Task 230: Frontend Data Service Integration\n');

const checks = [];

// Check 1: Service file exists
const servicePath = path.join(__dirname, 'src/services/UniversalDataService.ts');
checks.push({
  name: 'UniversalDataService.ts exists',
  passed: fs.existsSync(servicePath),
  path: servicePath
});

// Check 2: Hooks file exists
const hooksPath = path.join(__dirname, 'src/hooks/useUniversalData.ts');
checks.push({
  name: 'useUniversalData.ts exists',
  passed: fs.existsSync(hooksPath),
  path: hooksPath
});

// Check 3: Demo component exists
const demoPath = path.join(__dirname, 'src/examples/UniversalDataServiceDemo.tsx');
checks.push({
  name: 'UniversalDataServiceDemo.tsx exists',
  passed: fs.existsSync(demoPath),
  path: demoPath
});

// Check 4: Service index exists
const serviceIndexPath = path.join(__dirname, 'src/services/index.ts');
checks.push({
  name: 'services/index.ts exists',
  passed: fs.existsSync(serviceIndexPath),
  path: serviceIndexPath
});

// Check 5: Hooks index exists
const hooksIndexPath = path.join(__dirname, 'src/hooks/index.ts');
checks.push({
  name: 'hooks/index.ts exists',
  passed: fs.existsSync(hooksIndexPath),
  path: hooksIndexPath
});

// Check 6: Guide exists
const guidePath = path.join(__dirname, 'UNIVERSAL_DATA_SERVICE_GUIDE.md');
checks.push({
  name: 'UNIVERSAL_DATA_SERVICE_GUIDE.md exists',
  passed: fs.existsSync(guidePath),
  path: guidePath
});

// Check 7: Quick reference exists
const quickRefPath = path.join(__dirname, 'UNIVERSAL_DATA_QUICK_REFERENCE.md');
checks.push({
  name: 'UNIVERSAL_DATA_QUICK_REFERENCE.md exists',
  passed: fs.existsSync(quickRefPath),
  path: quickRefPath
});

// Check 8: Service has required methods
if (fs.existsSync(servicePath)) {
  const serviceContent = fs.readFileSync(servicePath, 'utf8');
  const requiredMethods = [
    'fetchWithPDFBytes',
    'formatAllNumbers',
    'downloadPDF',
    'subscribeToKey',
    'clearCache',
    'getCacheStats'
  ];
  
  requiredMethods.forEach(method => {
    checks.push({
      name: `Service has ${method}() method`,
      passed: serviceContent.includes(method),
      path: servicePath
    });
  });
}

// Check 9: Hooks file has required hooks
if (fs.existsSync(hooksPath)) {
  const hooksContent = fs.readFileSync(hooksPath, 'utf8');
  const requiredHooks = [
    'useUniversalData',
    'useDataByKey',
    'useDataSync',
    'useBulkPDF',
    'useDataExport',
    'useDataCache'
  ];
  
  requiredHooks.forEach(hook => {
    checks.push({
      name: `Hooks file has ${hook}`,
      passed: hooksContent.includes(`export function ${hook}`),
      path: hooksPath
    });
  });
}

// Check 10: Demo has all examples
if (fs.existsSync(demoPath)) {
  const demoContent = fs.readFileSync(demoPath, 'utf8');
  const requiredExamples = [
    'FetchWithPDFExample',
    'FetchByKeyExample',
    'FormatNumbersExample',
    'DataSyncExample',
    'BulkPDFExample',
    'DataExportExample',
    'CacheManagementExample',
    'SearchByKeyExample'
  ];
  
  requiredExamples.forEach(example => {
    checks.push({
      name: `Demo has ${example}`,
      passed: demoContent.includes(example),
      path: demoPath
    });
  });
}

// Print results
console.log('📋 Verification Results:\n');

let passedCount = 0;
let failedCount = 0;

checks.forEach((check, index) => {
  const status = check.passed ? '✅' : '❌';
  const message = check.passed ? 'PASS' : 'FAIL';
  console.log(`${index + 1}. ${status} ${check.name} - ${message}`);
  
  if (check.passed) {
    passedCount++;
  } else {
    failedCount++;
    console.log(`   Path: ${check.path}`);
  }
});

console.log(`\n📊 Summary:`);
console.log(`   Total Checks: ${checks.length}`);
console.log(`   ✅ Passed: ${passedCount}`);
console.log(`   ❌ Failed: ${failedCount}`);
console.log(`   Success Rate: ${((passedCount / checks.length) * 100).toFixed(1)}%`);

if (failedCount === 0) {
  console.log('\n🎉 All checks passed! Task 230 is complete.');
  process.exit(0);
} else {
  console.log('\n⚠️  Some checks failed. Please review the implementation.');
  process.exit(1);
}
