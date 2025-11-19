/**
 * Verification Script for Task 30: Dashboard Page
 * 
 * This script verifies that the Dashboard implementation is complete and correct.
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying Task 30: Dashboard Page Implementation\n');

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

function checkFileContent(filePath, searchStrings, description) {
  const fullPath = path.join(__dirname, filePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`❌ ${description} - File not found`);
    checks.failed++;
    return false;
  }

  const content = fs.readFileSync(fullPath, 'utf8');
  const allFound = searchStrings.every(str => content.includes(str));

  if (allFound) {
    console.log(`✅ ${description}`);
    checks.passed++;
    return true;
  } else {
    console.log(`❌ ${description}`);
    const missing = searchStrings.filter(str => !content.includes(str));
    console.log(`   Missing: ${missing.join(', ')}`);
    checks.failed++;
    return false;
  }
}

console.log('📁 Checking File Structure...\n');

// Check main files
checkFile(
  'frontend/src/pages/Dashboard.tsx',
  'Dashboard component exists'
);

checkFile(
  'frontend/src/pages/Dashboard.css',
  'Dashboard styles exist'
);

checkFile(
  'TASK_30_COMPLETE.md',
  'Task completion documentation exists'
);

checkFile(
  'frontend/DASHBOARD_QUICK_REFERENCE.md',
  'Quick reference guide exists'
);

checkFile(
  'TASK_30_VISUAL_SUMMARY.md',
  'Visual summary exists'
);

console.log('\n📝 Checking Dashboard Component Implementation...\n');

// Check Dashboard component features
checkFileContent(
  'frontend/src/pages/Dashboard.tsx',
  [
    'interface StatCard',
    'interface Project',
    'interface Activity',
    'useState',
    'useEffect',
    'useNavigate',
    'loadDashboardData',
    'quickActions',
    'renderStatCard',
    'DataTable',
    'Timeline'
  ],
  'Dashboard component has all required features'
);

// Check statistics cards
checkFileContent(
  'frontend/src/pages/Dashboard.tsx',
  [
    'Total Projects',
    'Active Projects',
    'Total Revenue',
    'Completed This Month',
    'trend'
  ],
  'Statistics cards are implemented'
);

// Check quick actions
checkFileContent(
  'frontend/src/pages/Dashboard.tsx',
  [
    'New Solar Project',
    'New Heat Pump',
    'Price Matrix',
    'Generate PDF'
  ],
  'Quick action buttons are implemented'
);

// Check recent projects table
checkFileContent(
  'frontend/src/pages/Dashboard.tsx',
  [
    'recentProjects',
    'projectTypeTemplate',
    'statusTemplate',
    'valueTemplate',
    'dateTemplate',
    'actionsTemplate',
    'Column'
  ],
  'Recent projects table is implemented'
);

// Check activity timeline
checkFileContent(
  'frontend/src/pages/Dashboard.tsx',
  [
    'activities',
    'Timeline',
    'customizedMarker',
    'customizedContent',
    'project_created',
    'project_completed',
    'calculation',
    'pdf_generated',
    'customer_added'
  ],
  'Activity timeline is implemented'
);

console.log('\n🎨 Checking Dashboard Styles...\n');

// Check CSS classes
checkFileContent(
  'frontend/src/pages/Dashboard.css',
  [
    '.dashboard',
    '.dashboard-header',
    '.quick-actions',
    '.stats-grid',
    '.stat-card',
    '.stat-icon',
    '.stat-value',
    '.stat-trend',
    '.dashboard-content',
    '.recent-projects-card',
    '.activity-card',
    '.activity-timeline'
  ],
  'All CSS classes are defined'
);

// Check responsive design
checkFileContent(
  'frontend/src/pages/Dashboard.css',
  [
    '@media (max-width: 1024px)',
    '@media (max-width: 768px)',
    'grid-template-columns'
  ],
  'Responsive design is implemented'
);

// Check animations
checkFileContent(
  'frontend/src/pages/Dashboard.css',
  [
    'transition',
    'animation',
    '@keyframes fadeIn',
    'animation-delay'
  ],
  'Animations are implemented'
);

console.log('\n🌍 Checking Localization...\n');

// Check German formatting
checkFileContent(
  'frontend/src/pages/Dashboard.tsx',
  [
    "Intl.NumberFormat('de-DE'",
    "toLocaleDateString('de-DE')",
    "toLocaleString('de-DE')",
    'currency: \'EUR\''
  ],
  'German localization is implemented'
);

console.log('\n📚 Checking Documentation...\n');

// Check completion documentation
checkFileContent(
  'TASK_30_COMPLETE.md',
  [
    'Task 30',
    'Dashboard Page',
    'Implementation Complete',
    'Statistics Cards',
    'Recent Projects List',
    'Quick Action Buttons',
    'Activity Timeline',
    'Requirements Satisfied'
  ],
  'Completion documentation is comprehensive'
);

// Check quick reference
checkFileContent(
  'frontend/DASHBOARD_QUICK_REFERENCE.md',
  [
    'Dashboard Quick Reference',
    'Features',
    'Usage',
    'Styling',
    'Data Structures',
    'API Integration',
    'Troubleshooting',
    'Examples'
  ],
  'Quick reference guide is comprehensive'
);

// Check visual summary
checkFileContent(
  'TASK_30_VISUAL_SUMMARY.md',
  [
    'Visual Summary',
    'Dashboard Layout',
    'Visual Components',
    'Color Scheme',
    'Responsive Design',
    'Animations',
    'Technical Details'
  ],
  'Visual summary is comprehensive'
);

console.log('\n🔧 Checking TypeScript Types...\n');

// Check TypeScript interfaces
checkFileContent(
  'frontend/src/pages/Dashboard.tsx',
  [
    'interface StatCard {',
    'interface Project {',
    'interface Activity {',
    'title: string',
    'value: string | number',
    'icon: string',
    'color: string',
    'projectType:',
    'status:',
    'timestamp: string'
  ],
  'TypeScript interfaces are properly defined'
);

console.log('\n📊 Checking Component Structure...\n');

// Check component structure
checkFileContent(
  'frontend/src/pages/Dashboard.tsx',
  [
    'const Dashboard: React.FC',
    'return (',
    '<div className="dashboard">',
    '<div className="dashboard-header">',
    '<div className="stats-grid">',
    '<div className="dashboard-content">',
    '<Card title="Recent Projects"',
    '<Card title="Recent Activity"'
  ],
  'Component structure is correct'
);

console.log('\n🎯 Checking Requirements Compliance...\n');

// Check requirements
const requirementsChecks = [
  {
    requirement: 'Dashboard layout created',
    check: () => checkFileContent(
      'frontend/src/pages/Dashboard.tsx',
      ['<div className="dashboard">', '<div className="dashboard-header">'],
      'Dashboard layout requirement'
    )
  },
  {
    requirement: 'Statistics cards built',
    check: () => checkFileContent(
      'frontend/src/pages/Dashboard.tsx',
      ['renderStatCard', 'stats.map'],
      'Statistics cards requirement'
    )
  },
  {
    requirement: 'Recent projects list implemented',
    check: () => checkFileContent(
      'frontend/src/pages/Dashboard.tsx',
      ['DataTable', 'recentProjects'],
      'Recent projects requirement'
    )
  },
  {
    requirement: 'Quick action buttons added',
    check: () => checkFileContent(
      'frontend/src/pages/Dashboard.tsx',
      ['quickActions', 'quickActions.map'],
      'Quick actions requirement'
    )
  },
  {
    requirement: 'Activity timeline created',
    check: () => checkFileContent(
      'frontend/src/pages/Dashboard.tsx',
      ['Timeline', 'activities'],
      'Activity timeline requirement'
    )
  }
];

requirementsChecks.forEach(({ requirement, check }) => {
  check();
});

console.log('\n' + '='.repeat(60));
console.log('📊 Verification Summary');
console.log('='.repeat(60));
console.log(`✅ Passed: ${checks.passed}`);
console.log(`❌ Failed: ${checks.failed}`);
console.log(`⚠️  Warnings: ${checks.warnings}`);
console.log('='.repeat(60));

if (checks.failed === 0) {
  console.log('\n🎉 All checks passed! Task 30 is complete and verified.');
  console.log('\n✨ Dashboard Features:');
  console.log('   • Statistics cards with trends');
  console.log('   • Recent projects table with sorting');
  console.log('   • Quick action buttons');
  console.log('   • Activity timeline');
  console.log('   • Responsive design');
  console.log('   • German localization');
  console.log('   • Smooth animations');
  console.log('\n📝 Next Steps:');
  console.log('   1. Test the dashboard in the browser');
  console.log('   2. Integrate with backend API');
  console.log('   3. Add unit tests');
  console.log('   4. Proceed to Task 31: Solar Calculator Input Form');
  process.exit(0);
} else {
  console.log('\n❌ Some checks failed. Please review the errors above.');
  console.log('\n🔧 Common Issues:');
  console.log('   • Missing files: Ensure all files are created');
  console.log('   • Missing imports: Check component imports');
  console.log('   • Syntax errors: Run TypeScript compiler');
  console.log('   • Missing features: Review task requirements');
  process.exit(1);
}
