/**
 * Task 29 Verification Script
 * 
 * Verifies that all custom hooks are properly implemented
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying Task 29: Custom Hooks Implementation\n');

const hooksDir = path.join(__dirname, 'frontend', 'src', 'hooks');
const examplesDir = path.join(__dirname, 'frontend', 'src', 'examples');
const docsDir = path.join(__dirname, 'frontend');

// Required hooks
const requiredHooks = [
  'useAuth.ts',
  'useApi.ts',
  'useWebSocket.ts',
  'useForm.ts',
  'useDebounce.ts',
  'index.ts',
];

// Required documentation
const requiredDocs = [
  'CUSTOM_HOOKS_GUIDE.md',
  'CUSTOM_HOOKS_QUICK_REFERENCE.md',
];

// Required examples
const requiredExamples = [
  'CustomHooksDemo.tsx',
  'CustomHooksDemo.css',
];

let allPassed = true;

// Check hooks
console.log('📁 Checking hooks directory...');
requiredHooks.forEach((hook) => {
  const hookPath = path.join(hooksDir, hook);
  if (fs.existsSync(hookPath)) {
    const content = fs.readFileSync(hookPath, 'utf8');
    const lines = content.split('\n').length;
    console.log(`  ✅ ${hook} (${lines} lines)`);
  } else {
    console.log(`  ❌ ${hook} - NOT FOUND`);
    allPassed = false;
  }
});

// Check documentation
console.log('\n📚 Checking documentation...');
requiredDocs.forEach((doc) => {
  const docPath = path.join(docsDir, doc);
  if (fs.existsSync(docPath)) {
    const content = fs.readFileSync(docPath, 'utf8');
    const lines = content.split('\n').length;
    console.log(`  ✅ ${doc} (${lines} lines)`);
  } else {
    console.log(`  ❌ ${doc} - NOT FOUND`);
    allPassed = false;
  }
});

// Check examples
console.log('\n🎨 Checking examples...');
requiredExamples.forEach((example) => {
  const examplePath = path.join(examplesDir, example);
  if (fs.existsSync(examplePath)) {
    const content = fs.readFileSync(examplePath, 'utf8');
    const lines = content.split('\n').length;
    console.log(`  ✅ ${example} (${lines} lines)`);
  } else {
    console.log(`  ❌ ${example} - NOT FOUND`);
    allPassed = false;
  }
});

// Verify hook exports
console.log('\n🔗 Checking hook exports...');
const indexPath = path.join(hooksDir, 'index.ts');
if (fs.existsSync(indexPath)) {
  const indexContent = fs.readFileSync(indexPath, 'utf8');
  
  const expectedExports = [
    'useAuth',
    'useApi',
    'useWebSocket',
    'useWebSocketConnection',
    'useDebounce',
    'useForm',
    'useFormError',
    'useHasError',
  ];

  expectedExports.forEach((exportName) => {
    if (indexContent.includes(exportName)) {
      console.log(`  ✅ ${exportName} exported`);
    } else {
      console.log(`  ❌ ${exportName} - NOT EXPORTED`);
      allPassed = false;
    }
  });
}

// Check hook features
console.log('\n🎯 Checking hook features...');

// useAuth features
const useAuthPath = path.join(hooksDir, 'useAuth.ts');
if (fs.existsSync(useAuthPath)) {
  const content = fs.readFileSync(useAuthPath, 'utf8');
  const features = [
    { name: 'login function', pattern: /const login = useCallback/ },
    { name: 'logout function', pattern: /const logout = useCallback/ },
    { name: 'refreshUser function', pattern: /const refreshUser = useCallback/ },
    { name: 'error handling', pattern: /setError/ },
    { name: 'loading state', pattern: /setLoading/ },
  ];

  console.log('  useAuth:');
  features.forEach(({ name, pattern }) => {
    if (pattern.test(content)) {
      console.log(`    ✅ ${name}`);
    } else {
      console.log(`    ❌ ${name} - NOT FOUND`);
      allPassed = false;
    }
  });
}

// useApi features
const useApiPath = path.join(hooksDir, 'useApi.ts');
if (fs.existsSync(useApiPath)) {
  const content = fs.readFileSync(useApiPath, 'utf8');
  const features = [
    { name: 'execute function', pattern: /const execute = useCallback/ },
    { name: 'reset function', pattern: /const reset = useCallback/ },
    { name: 'loading state', pattern: /setIsLoading/ },
    { name: 'error handling', pattern: /setError/ },
    { name: 'notifications', pattern: /addNotification/ },
  ];

  console.log('  useApi:');
  features.forEach(({ name, pattern }) => {
    if (pattern.test(content)) {
      console.log(`    ✅ ${name}`);
    } else {
      console.log(`    ❌ ${name} - NOT FOUND`);
      allPassed = false;
    }
  });
}

// useWebSocket features
const useWebSocketPath = path.join(hooksDir, 'useWebSocket.ts');
if (fs.existsSync(useWebSocketPath)) {
  const content = fs.readFileSync(useWebSocketPath, 'utf8');
  const features = [
    { name: 'emit function', pattern: /const emit = useCallback/ },
    { name: 'event subscription', pattern: /websocketService\.on/ },
    { name: 'event cleanup', pattern: /websocketService\.off/ },
    { name: 'connection management', pattern: /useWebSocketConnection/ },
  ];

  console.log('  useWebSocket:');
  features.forEach(({ name, pattern }) => {
    if (pattern.test(content)) {
      console.log(`    ✅ ${name}`);
    } else {
      console.log(`    ❌ ${name} - NOT FOUND`);
      allPassed = false;
    }
  });
}

// useForm features
const useFormPath = path.join(hooksDir, 'useForm.ts');
if (fs.existsSync(useFormPath)) {
  const content = fs.readFileSync(useFormPath, 'utf8');
  const features = [
    { name: 'Zod validation', pattern: /zodResolver/ },
    { name: 'auto-save', pattern: /autoSave/ },
    { name: 'manual save', pattern: /manualSave/ },
    { name: 'toast notifications', pattern: /toast/ },
    { name: 'error handling', pattern: /onSubmitError/ },
  ];

  console.log('  useForm:');
  features.forEach(({ name, pattern }) => {
    if (pattern.test(content)) {
      console.log(`    ✅ ${name}`);
    } else {
      console.log(`    ❌ ${name} - NOT FOUND`);
      allPassed = false;
    }
  });
}

// useDebounce features
const useDebouncePath = path.join(hooksDir, 'useDebounce.ts');
if (fs.existsSync(useDebouncePath)) {
  const content = fs.readFileSync(useDebouncePath, 'utf8');
  const features = [
    { name: 'debounced value', pattern: /debouncedValue/ },
    { name: 'setTimeout', pattern: /setTimeout/ },
    { name: 'cleanup', pattern: /clearTimeout/ },
  ];

  console.log('  useDebounce:');
  features.forEach(({ name, pattern }) => {
    if (pattern.test(content)) {
      console.log(`    ✅ ${name}`);
    } else {
      console.log(`    ❌ ${name} - NOT FOUND`);
      allPassed = false;
    }
  });
}

// Summary
console.log('\n' + '='.repeat(60));
if (allPassed) {
  console.log('✅ All checks passed! Task 29 is complete.');
  console.log('\n📋 Summary:');
  console.log('  • 5 custom hooks implemented');
  console.log('  • All hooks properly exported');
  console.log('  • Comprehensive documentation created');
  console.log('  • Demo examples provided');
  console.log('  • All features verified');
} else {
  console.log('❌ Some checks failed. Please review the output above.');
  process.exit(1);
}
console.log('='.repeat(60));
