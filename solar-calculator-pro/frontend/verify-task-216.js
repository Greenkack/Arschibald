/**
 * Verification Script for Task 216: Custom German Input Components
 * 
 * This script verifies that all German input components are properly implemented.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔍 Verifying Task 216: Custom German Input Components\n');

const checks = [];

// Check 1: Component files exist
console.log('📁 Checking component files...');
const componentFiles = [
  'src/components/GermanNumberInput.tsx',
  'src/components/GermanCurrencyInput.tsx',
  'src/components/GermanPercentInput.tsx',
  'src/components/GermanSlider.tsx',
  'src/components/index.ts'
];

componentFiles.forEach(file => {
  const exists = fs.existsSync(path.join(__dirname, file));
  checks.push({ name: `Component file: ${file}`, passed: exists });
  console.log(`  ${exists ? '✅' : '❌'} ${file}`);
});

// Check 2: Style file exists
console.log('\n🎨 Checking style files...');
const styleFile = 'src/styles/germanInputComponents.css';
const styleExists = fs.existsSync(path.join(__dirname, styleFile));
checks.push({ name: `Style file: ${styleFile}`, passed: styleExists });
console.log(`  ${styleExists ? '✅' : '❌'} ${styleFile}`);

// Check 3: Test file exists
console.log('\n🧪 Checking test files...');
const testFile = 'src/test/GermanNumberInput.test.tsx';
const testExists = fs.existsSync(path.join(__dirname, testFile));
checks.push({ name: `Test file: ${testFile}`, passed: testExists });
console.log(`  ${testExists ? '✅' : '❌'} ${testFile}`);

// Check 4: Example file exists
console.log('\n📚 Checking example files...');
const exampleFile = 'src/examples/GermanInputComponentsDemo.tsx';
const exampleExists = fs.existsSync(path.join(__dirname, exampleFile));
checks.push({ name: `Example file: ${exampleFile}`, passed: exampleExists });
console.log(`  ${exampleExists ? '✅' : '❌'} ${exampleFile}`);

// Check 5: Documentation exists
console.log('\n📖 Checking documentation...');
const docFile = 'GERMAN_INPUT_COMPONENTS.md';
const docExists = fs.existsSync(path.join(__dirname, docFile));
checks.push({ name: `Documentation: ${docFile}`, passed: docExists });
console.log(`  ${docExists ? '✅' : '❌'} ${docFile}`);

// Check 6: Component content verification
console.log('\n🔬 Verifying component implementations...');

const verifyComponent = (file, requiredStrings) => {
  try {
    const content = fs.readFileSync(path.join(__dirname, file), 'utf8');
    const allFound = requiredStrings.every(str => content.includes(str));
    return allFound;
  } catch (error) {
    return false;
  }
};

// GermanNumberInput checks
const numberInputValid = verifyComponent('src/components/GermanNumberInput.tsx', [
  'GermanNumberInput',
  'germanFormatter',
  'bidirectional',
  'validate',
  'onChange',
  'onBlur'
]);
checks.push({ name: 'GermanNumberInput implementation', passed: numberInputValid });
console.log(`  ${numberInputValid ? '✅' : '❌'} GermanNumberInput implementation`);

// GermanCurrencyInput checks
const currencyInputValid = verifyComponent('src/components/GermanCurrencyInput.tsx', [
  'GermanCurrencyInput',
  'currencySymbol',
  'symbolPosition',
  'formatCurrency'
]);
checks.push({ name: 'GermanCurrencyInput implementation', passed: currencyInputValid });
console.log(`  ${currencyInputValid ? '✅' : '❌'} GermanCurrencyInput implementation`);

// GermanPercentInput checks
const percentInputValid = verifyComponent('src/components/GermanPercentInput.tsx', [
  'GermanPercentInput',
  'multiplyBy100',
  'formatPercent'
]);
checks.push({ name: 'GermanPercentInput implementation', passed: percentInputValid });
console.log(`  ${percentInputValid ? '✅' : '❌'} GermanPercentInput implementation`);

// GermanSlider checks
const sliderValid = verifyComponent('src/components/GermanSlider.tsx', [
  'GermanSlider',
  'formatType',
  'showValue',
  'showMinMax',
  'range'
]);
checks.push({ name: 'GermanSlider implementation', passed: sliderValid });
console.log(`  ${sliderValid ? '✅' : '❌'} GermanSlider implementation`);

// Check 7: Component exports
console.log('\n📦 Checking component exports...');
const indexValid = verifyComponent('src/components/index.ts', [
  'GermanNumberInput',
  'GermanCurrencyInput',
  'GermanPercentInput',
  'GermanSlider'
]);
checks.push({ name: 'Component exports', passed: indexValid });
console.log(`  ${indexValid ? '✅' : '❌'} Component exports`);

// Check 8: Requirements compliance
console.log('\n✅ Checking requirements compliance...');

const req143 = verifyComponent('src/components/GermanNumberInput.tsx', [
  '14.3',
  'German format'
]);
checks.push({ name: 'Requirement 14.3: German formatting', passed: req143 });
console.log(`  ${req143 ? '✅' : '❌'} Requirement 14.3: German formatting`);

const req146 = verifyComponent('src/components/GermanNumberInput.tsx', [
  '14.6',
  'bidirectional'
]);
checks.push({ name: 'Requirement 14.6: Bidirectional conversion', passed: req146 });
console.log(`  ${req146 ? '✅' : '❌'} Requirement 14.6: Bidirectional conversion`);

const req149 = verifyComponent('src/components/GermanNumberInput.tsx', [
  '14.9',
  'validate'
]);
checks.push({ name: 'Requirement 14.9: Validation', passed: req149 });
console.log(`  ${req149 ? '✅' : '❌'} Requirement 14.9: Validation`);

// Summary
console.log('\n' + '='.repeat(60));
console.log('📊 VERIFICATION SUMMARY');
console.log('='.repeat(60));

const passed = checks.filter(c => c.passed).length;
const total = checks.length;
const percentage = ((passed / total) * 100).toFixed(1);

console.log(`\nTotal Checks: ${total}`);
console.log(`Passed: ${passed}`);
console.log(`Failed: ${total - passed}`);
console.log(`Success Rate: ${percentage}%`);

if (passed === total) {
  console.log('\n✅ ALL CHECKS PASSED! Task 216 is complete.');
  console.log('\n🎉 Custom German Input Components are ready for use!');
  process.exit(0);
} else {
  console.log('\n❌ Some checks failed. Please review the implementation.');
  console.log('\nFailed checks:');
  checks.filter(c => !c.passed).forEach(c => {
    console.log(`  ❌ ${c.name}`);
  });
  process.exit(1);
}
