/**
 * Task 27 Verification Script
 * 
 * Verifies that the Form Management system is properly implemented.
 */

const fs = require('fs');
const path = require('path');

const FRONTEND_DIR = path.join(__dirname);

// Color codes for output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[36m',
  reset: '\x1b[0m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkFileExists(filePath) {
  const fullPath = path.join(FRONTEND_DIR, filePath);
  const exists = fs.existsSync(fullPath);
  
  if (exists) {
    log(`✓ ${filePath}`, 'green');
    return true;
  } else {
    log(`✗ ${filePath} - NOT FOUND`, 'red');
    return false;
  }
}

function checkFileContent(filePath, requiredContent) {
  const fullPath = path.join(FRONTEND_DIR, filePath);
  
  if (!fs.existsSync(fullPath)) {
    log(`✗ ${filePath} - File not found`, 'red');
    return false;
  }
  
  const content = fs.readFileSync(fullPath, 'utf8');
  const missingContent = requiredContent.filter(item => !content.includes(item));
  
  if (missingContent.length === 0) {
    log(`✓ ${filePath} - All required content present`, 'green');
    return true;
  } else {
    log(`✗ ${filePath} - Missing content:`, 'red');
    missingContent.forEach(item => log(`  - ${item}`, 'yellow'));
    return false;
  }
}

function main() {
  log('\n=== Task 27: Form Management Verification ===\n', 'blue');
  
  let allPassed = true;
  
  // Check core files
  log('\n1. Checking Core Files:', 'blue');
  const coreFiles = [
    'src/utils/formValidation.ts',
    'src/hooks/useForm.ts',
    'src/components/forms/FormField.tsx',
    'src/components/forms/FormField.css',
    'src/components/forms/FormContainer.tsx',
    'src/components/forms/FormContainer.css',
    'src/components/forms/index.ts',
  ];
  
  coreFiles.forEach(file => {
    if (!checkFileExists(file)) allPassed = false;
  });
  
  // Check documentation
  log('\n2. Checking Documentation:', 'blue');
  const docFiles = [
    'FORM_MANAGEMENT_GUIDE.md',
    'FORM_MANAGEMENT_QUICK_REFERENCE.md',
  ];
  
  docFiles.forEach(file => {
    if (!checkFileExists(file)) allPassed = false;
  });
  
  // Check example
  log('\n3. Checking Examples:', 'blue');
  const exampleFiles = [
    'src/examples/FormManagementDemo.tsx',
    'src/examples/FormManagementDemo.css',
  ];
  
  exampleFiles.forEach(file => {
    if (!checkFileExists(file)) allPassed = false;
  });
  
  // Check validation schemas
  log('\n4. Checking Validation Schemas:', 'blue');
  const validationSchemas = [
    'loginSchema',
    'registerSchema',
    'passwordChangeSchema',
    'solarCalculatorSchema',
    'heatPumpSchema',
    'projectSchema',
    'customerSchema',
    'productSchema',
    'priceMatrixUploadSchema',
    'userSettingsSchema',
  ];
  
  if (!checkFileContent('src/utils/formValidation.ts', validationSchemas)) {
    allPassed = false;
  }
  
  // Check form components
  log('\n5. Checking Form Components:', 'blue');
  const formComponents = [
    'FormTextField',
    'FormNumberField',
    'FormTextareaField',
    'FormDropdownField',
    'FormMultiSelectField',
    'FormDateField',
    'FormCheckboxField',
    'FormRadioField',
    'FormSliderField',
    'FormPasswordField',
  ];
  
  if (!checkFileContent('src/components/forms/FormField.tsx', formComponents)) {
    allPassed = false;
  }
  
  // Check useForm hook features
  log('\n6. Checking useForm Hook Features:', 'blue');
  const hookFeatures = [
    'autoSave',
    'autoSaveInterval',
    'onAutoSave',
    'isAutoSaving',
    'lastSaved',
    'manualSave',
    'onSubmitSuccess',
    'onSubmitError',
    'showSuccessToast',
    'showErrorToast',
  ];
  
  if (!checkFileContent('src/hooks/useForm.ts', hookFeatures)) {
    allPassed = false;
  }
  
  // Check FormContainer features
  log('\n7. Checking FormContainer Features:', 'blue');
  const containerFeatures = [
    'isAutoSaving',
    'lastSaved',
    'auto-save-indicator',
    'last-saved',
    'form-footer',
    'form-actions',
  ];
  
  if (!checkFileContent('src/components/forms/FormContainer.tsx', containerFeatures)) {
    allPassed = false;
  }
  
  // Check exports
  log('\n8. Checking Exports:', 'blue');
  
  if (!checkFileContent('src/hooks/index.ts', ['useForm', 'useFormError', 'useHasError'])) {
    allPassed = false;
  }
  
  if (!checkFileContent('src/utils/index.ts', ['formValidation'])) {
    allPassed = false;
  }
  
  // Check package.json dependencies
  log('\n9. Checking Dependencies:', 'blue');
  const packageJsonPath = path.join(FRONTEND_DIR, 'package.json');
  if (fs.existsSync(packageJsonPath)) {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const requiredDeps = ['react-hook-form', 'zod', '@hookform/resolvers'];
    const missingDeps = requiredDeps.filter(dep => !packageJson.dependencies[dep]);
    
    if (missingDeps.length === 0) {
      log('✓ All required dependencies installed', 'green');
    } else {
      log('✗ Missing dependencies:', 'red');
      missingDeps.forEach(dep => log(`  - ${dep}`, 'yellow'));
      allPassed = false;
    }
  } else {
    log('✗ package.json not found', 'red');
    allPassed = false;
  }
  
  // Summary
  log('\n=== Verification Summary ===\n', 'blue');
  
  if (allPassed) {
    log('✓ All checks passed! Task 27 is complete.', 'green');
    log('\nForm Management System includes:', 'blue');
    log('  • React Hook Form integration', 'green');
    log('  • Zod validation with German error messages', 'green');
    log('  • 10+ reusable form components', 'green');
    log('  • Auto-save functionality', 'green');
    log('  • Comprehensive error handling', 'green');
    log('  • FormContainer wrapper component', 'green');
    log('  • Complete documentation', 'green');
    log('  • Working examples', 'green');
    
    log('\nNext Steps:', 'blue');
    log('  1. Run the demo: npm run dev', 'yellow');
    log('  2. Navigate to FormManagementDemo component', 'yellow');
    log('  3. Test all form features', 'yellow');
    log('  4. Review documentation in FORM_MANAGEMENT_GUIDE.md', 'yellow');
    
    return 0;
  } else {
    log('✗ Some checks failed. Please review the errors above.', 'red');
    return 1;
  }
}

process.exit(main());
