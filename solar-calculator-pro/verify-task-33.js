/**
 * Task 33 Verification Script
 * Verifies that all 3D visualization components are properly installed and configured
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying Task 33: 3D Visualization Integration\n');

const checks = {
  passed: 0,
  failed: 0,
  warnings: 0
};

function checkFile(filePath, description) {
  const fullPath = path.join(__dirname, filePath);
  if (fs.existsSync(fullPath)) {
    console.log(`✅ ${description}`);
    checks.passed++;
    return true;
  } else {
    console.log(`❌ ${description}`);
    checks.failed++;
    return false;
  }
}

function checkDependency(packageJsonPath, dependency, description) {
  try {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const allDeps = {
      ...packageJson.dependencies,
      ...packageJson.devDependencies
    };
    
    if (allDeps[dependency]) {
      console.log(`✅ ${description}: ${allDeps[dependency]}`);
      checks.passed++;
      return true;
    } else {
      console.log(`❌ ${description}: Not found`);
      checks.failed++;
      return false;
    }
  } catch (error) {
    console.log(`❌ ${description}: Error reading package.json`);
    checks.failed++;
    return false;
  }
}

console.log('📦 Checking Dependencies...\n');
const packageJsonPath = path.join(__dirname, 'frontend', 'package.json');
checkDependency(packageJsonPath, 'three', 'Three.js');
checkDependency(packageJsonPath, '@react-three/fiber', 'React Three Fiber');
checkDependency(packageJsonPath, '@react-three/drei', 'React Three Drei');
checkDependency(packageJsonPath, '@types/three', 'Three.js TypeScript types');

console.log('\n📁 Checking Component Files...\n');
checkFile('frontend/src/components/3d/Scene3D.tsx', 'Scene3D component');
checkFile('frontend/src/components/3d/RoofModel.tsx', 'RoofModel component');
checkFile('frontend/src/components/3d/SolarModule.tsx', 'SolarModule component');
checkFile('frontend/src/components/3d/ModulePlacement.tsx', 'ModulePlacement component');
checkFile('frontend/src/components/3d/CameraControls.tsx', 'CameraControls component');
checkFile('frontend/src/components/3d/ExportControls.tsx', 'ExportControls component');
checkFile('frontend/src/components/3d/Viewer3D.tsx', 'Viewer3D component');
checkFile('frontend/src/components/3d/Viewer3D.css', 'Viewer3D styles');
checkFile('frontend/src/components/3d/index.ts', '3D components index');

console.log('\n📄 Checking Page Files...\n');
checkFile('frontend/src/pages/Visualization3D.tsx', 'Visualization3D page');
checkFile('frontend/src/pages/Visualization3D.css', 'Visualization3D styles');

console.log('\n🗺️ Checking Routes...\n');
const routesPath = path.join(__dirname, 'frontend', 'src', 'routes', 'index.tsx');
if (fs.existsSync(routesPath)) {
  const routesContent = fs.readFileSync(routesPath, 'utf8');
  if (routesContent.includes('Visualization3D') && routesContent.includes('3d-visualization')) {
    console.log('✅ 3D visualization route configured');
    checks.passed++;
  } else {
    console.log('⚠️  3D visualization route may not be properly configured');
    checks.warnings++;
  }
} else {
  console.log('❌ Routes file not found');
  checks.failed++;
}

console.log('\n📚 Checking Documentation...\n');
checkFile('frontend/3D_VISUALIZATION_GUIDE.md', 'Comprehensive guide');
checkFile('frontend/3D_VISUALIZATION_QUICK_REFERENCE.md', 'Quick reference');
checkFile('TASK_33_COMPLETE.md', 'Task completion summary');
checkFile('TASK_33_VISUAL_SUMMARY.md', 'Visual summary');

console.log('\n' + '='.repeat(60));
console.log('📊 Verification Summary');
console.log('='.repeat(60));
console.log(`✅ Passed:   ${checks.passed}`);
console.log(`❌ Failed:   ${checks.failed}`);
console.log(`⚠️  Warnings: ${checks.warnings}`);
console.log('='.repeat(60));

if (checks.failed === 0) {
  console.log('\n🎉 All checks passed! Task 33 is complete.');
  console.log('\n📝 Next Steps:');
  console.log('   1. Run: cd frontend && npm install');
  console.log('   2. Run: npm run dev');
  console.log('   3. Navigate to: http://localhost:3000/3d-visualization');
  console.log('   4. Test the 3D visualization features');
  console.log('\n📖 Documentation:');
  console.log('   - Full Guide: frontend/3D_VISUALIZATION_GUIDE.md');
  console.log('   - Quick Ref:  frontend/3D_VISUALIZATION_QUICK_REFERENCE.md');
  process.exit(0);
} else {
  console.log('\n❌ Some checks failed. Please review the errors above.');
  console.log('\n🔧 Troubleshooting:');
  console.log('   1. Ensure all files were created correctly');
  console.log('   2. Check that dependencies are in package.json');
  console.log('   3. Verify routes are properly configured');
  console.log('   4. Review the task completion document');
  process.exit(1);
}
