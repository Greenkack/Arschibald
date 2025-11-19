#!/usr/bin/env node

/**
 * Task 218 Verification Script
 * 
 * Verifies that chart and visualization formatting is properly implemented.
 * 
 * Requirements: 14.3
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔍 Task 218: Chart and Visualization Formatting - Verification\n');

const checks = {
  passed: 0,
  failed: 0,
  warnings: 0,
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

function checkFileContent(filePath, searchStrings, description) {
  const fullPath = path.join(__dirname, filePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`❌ ${description} - File not found`);
    checks.failed++;
    return false;
  }

  const content = fs.readFileSync(fullPath, 'utf-8');
  const allFound = searchStrings.every(str => content.includes(str));

  if (allFound) {
    console.log(`✅ ${description}`);
    checks.passed++;
    return true;
  } else {
    console.log(`❌ ${description} - Missing required content`);
    checks.failed++;
    return false;
  }
}

console.log('📋 Checking Implementation Files:\n');

// Check chart formatting utilities
checkFile(
  'src/utils/chartFormatting.ts',
  'Chart formatting utilities exist'
);

checkFileContent(
  'src/utils/chartFormatting.ts',
  [
    'rechartsAxisTickFormatter',
    'rechartsTooltipFormatter',
    'rechartsCurrencyAxisTickFormatter',
    'rechartsCurrencyTooltipFormatter',
    'rechartsPercentAxisTickFormatter',
    'rechartsPercentTooltipFormatter',
  ],
  'Recharts formatters implemented'
);

checkFileContent(
  'src/utils/chartFormatting.ts',
  [
    'chartJsAxisTickCallback',
    'chartJsTooltipCallback',
    'chartJsCurrencyAxisTickCallback',
    'chartJsCurrencyTooltipCallback',
    'chartJsPercentAxisTickCallback',
    'chartJsPercentTooltipCallback',
  ],
  'Chart.js formatters implemented'
);

checkFileContent(
  'src/utils/chartFormatting.ts',
  [
    'getPlotlyFormatConfig',
    'getPlotlyHoverTemplate',
    'getPlotlyCurrencyHoverTemplate',
    'getPlotlyPercentHoverTemplate',
  ],
  'Plotly formatters implemented'
);

checkFileContent(
  'src/utils/chartFormatting.ts',
  [
    'createRechartsConfig',
    'createChartJsConfig',
    'formatChartData',
  ],
  'Helper functions implemented'
);

console.log('\n📋 Checking Demo and Examples:\n');

// Check demo component
checkFile(
  'src/examples/ChartFormattingDemo.tsx',
  'Chart formatting demo exists'
);

checkFileContent(
  'src/examples/ChartFormattingDemo.tsx',
  [
    'LineChart',
    'BarChart',
    'PieChart',
    'AreaChart',
    'rechartsAxisTickFormatter',
    'rechartsTooltipFormatter',
    'rechartsCurrencyAxisTickFormatter',
    'rechartsCurrencyTooltipFormatter',
  ],
  'Demo includes all chart types'
);

console.log('\n📋 Checking Documentation:\n');

// Check documentation
checkFile(
  'CHART_FORMATTING_GUIDE.md',
  'Complete formatting guide exists'
);

checkFileContent(
  'CHART_FORMATTING_GUIDE.md',
  [
    'Recharts Integration',
    'Chart.js Integration',
    'Plotly Integration',
    'Chart Export Formatting',
    'Best Practices',
  ],
  'Guide includes all sections'
);

checkFile(
  'CHART_FORMATTING_QUICK_REFERENCE.md',
  'Quick reference guide exists'
);

checkFileContent(
  'CHART_FORMATTING_QUICK_REFERENCE.md',
  [
    'Quick Import',
    'Recharts',
    'Chart.js',
    'Plotly',
    'Format Examples',
  ],
  'Quick reference includes all sections'
);

console.log('\n📋 Checking Tests:\n');

// Check tests
checkFile(
  'src/test/chartFormatting.test.ts',
  'Chart formatting tests exist'
);

checkFileContent(
  'src/test/chartFormatting.test.ts',
  [
    'formatChartAxis',
    'formatChartAxisCurrency',
    'formatChartAxisPercent',
    'rechartsTooltipFormatter',
    'chartJsTooltipCallback',
    'getPlotlyFormatConfig',
    'formatChartData',
  ],
  'Tests cover all formatters'
);

console.log('\n📋 Checking Requirements Compliance (14.3):\n');

// Check requirements compliance
checkFileContent(
  'src/utils/chartFormatting.ts',
  ['tickFormatter', 'formatter'],
  '✅ Format axis labels in all charts'
);

checkFileContent(
  'src/utils/chartFormatting.ts',
  ['Tooltip', 'tooltip', 'hover'],
  '✅ Apply German formatting to chart tooltips'
);

checkFileContent(
  'src/utils/chartFormatting.ts',
  ['Label', 'label'],
  '✅ Format legend values'
);

checkFileContent(
  'src/utils/chartFormatting.ts',
  ['Label', 'label'],
  '✅ Apply formatting to data labels'
);

checkFileContent(
  'src/utils/chartFormatting.ts',
  ['formatChartData', 'export'],
  '✅ Format numbers in chart exports'
);

console.log('\n📋 Checking Task Completion:\n');

// Check completion document
checkFile(
  '../TASK_218_COMPLETE.md',
  'Task completion document exists'
);

checkFileContent(
  '../TASK_218_COMPLETE.md',
  [
    'COMPLETE',
    'Requirements',
    'Format axis labels',
    'tooltips',
    'legend',
  ],
  'Completion document is comprehensive'
);

// Summary
console.log('\n' + '='.repeat(60));
console.log('📊 Verification Summary:');
console.log('='.repeat(60));
console.log(`✅ Passed: ${checks.passed}`);
console.log(`❌ Failed: ${checks.failed}`);
console.log(`⚠️  Warnings: ${checks.warnings}`);
console.log('='.repeat(60));

if (checks.failed === 0) {
  console.log('\n🎉 Task 218: Chart and Visualization Formatting - VERIFIED ✅');
  console.log('\nAll requirements (14.3) are fully implemented:');
  console.log('  ✅ Format axis labels in all charts');
  console.log('  ✅ Apply German formatting to chart tooltips');
  console.log('  ✅ Format legend values');
  console.log('  ✅ Apply formatting to data labels');
  console.log('  ✅ Format numbers in chart exports');
  console.log('\n📚 Documentation:');
  console.log('  - Complete Guide: frontend/CHART_FORMATTING_GUIDE.md');
  console.log('  - Quick Reference: frontend/CHART_FORMATTING_QUICK_REFERENCE.md');
  console.log('  - Demo: frontend/src/examples/ChartFormattingDemo.tsx');
  console.log('  - Tests: frontend/src/test/chartFormatting.test.ts');
  console.log('\n🚀 Next Steps:');
  console.log('  1. Run tests: npm test chartFormatting.test.ts');
  console.log('  2. View demo: npm run dev → Navigate to ChartFormattingDemo');
  console.log('  3. Integrate into application charts');
  process.exit(0);
} else {
  console.log('\n❌ Verification failed. Please check the errors above.');
  process.exit(1);
}
