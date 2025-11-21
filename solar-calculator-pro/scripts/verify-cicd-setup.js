#!/usr/bin/env node

/**
 * CI/CD Pipeline Setup Verification Script
 * 
 * This script verifies that all CI/CD pipeline components are properly configured.
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

function checkFileExists(filePath) {
  const fullPath = path.join(__dirname, '..', filePath);
  return fs.existsSync(fullPath);
}

function checkWorkflowFile(workflowName, filePath) {
  log(`\nChecking ${workflowName}...`, 'cyan');
  
  if (!checkFileExists(filePath)) {
    log(`  ✗ Workflow file not found: ${filePath}`, 'red');
    return false;
  }
  
  const content = fs.readFileSync(path.join(__dirname, '..', filePath), 'utf8');
  
  // Check for required sections
  const checks = [
    { name: 'name', pattern: /^name:/m },
    { name: 'on triggers', pattern: /^on:/m },
    { name: 'jobs', pattern: /^jobs:/m }
  ];
  
  let allPassed = true;
  checks.forEach(check => {
    if (check.pattern.test(content)) {
      log(`  ✓ ${check.name} defined`, 'green');
    } else {
      log(`  ✗ ${check.name} missing`, 'red');
      allPassed = false;
    }
  });
  
  return allPassed;
}

function checkDocumentation() {
  log('\nChecking Documentation...', 'cyan');
  
  const docs = [
    '.github/workflows/ci.yml',
    '.github/workflows/build.yml',
    '.github/workflows/release.yml',
    '.github/workflows/performance.yml',
    '.github/workflows/security.yml',
    'docs/CI_CD_PIPELINE_GUIDE.md',
    'docs/CI_CD_QUICK_REFERENCE.md'
  ];
  
  let allExist = true;
  docs.forEach(doc => {
    if (checkFileExists(doc)) {
      log(`  ✓ ${doc}`, 'green');
    } else {
      log(`  ✗ ${doc} not found`, 'red');
      allExist = false;
    }
  });
  
  return allExist;
}

function checkPackageJson() {
  log('\nChecking package.json scripts...', 'cyan');
  
  const packageJsonPath = path.join(__dirname, '..', 'package.json');
  if (!fs.existsSync(packageJsonPath)) {
    log('  ✗ package.json not found', 'red');
    return false;
  }
  
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  const requiredScripts = [
    'electron:build',
    'electron:build:win',
    'electron:build:mac',
    'electron:build:linux'
  ];
  
  let allPresent = true;
  requiredScripts.forEach(script => {
    if (packageJson.scripts && packageJson.scripts[script]) {
      log(`  ✓ Script "${script}" defined`, 'green');
    } else {
      log(`  ✗ Script "${script}" missing`, 'red');
      allPresent = false;
    }
  });
  
  return allPresent;
}

function checkGitHubDirectory() {
  log('\nChecking .github directory structure...', 'cyan');
  
  const workflowsDir = path.join(__dirname, '..', '.github', 'workflows');
  if (!fs.existsSync(workflowsDir)) {
    log('  ✗ .github/workflows directory not found', 'red');
    return false;
  }
  
  log('  ✓ .github/workflows directory exists', 'green');
  
  const workflowFiles = fs.readdirSync(workflowsDir);
  log(`  ✓ Found ${workflowFiles.length} workflow files`, 'green');
  
  return true;
}

function generateReport(results) {
  log('\n' + '='.repeat(60), 'blue');
  log('CI/CD PIPELINE VERIFICATION REPORT', 'blue');
  log('='.repeat(60), 'blue');
  
  const totalChecks = Object.keys(results).length;
  const passedChecks = Object.values(results).filter(v => v).length;
  const failedChecks = totalChecks - passedChecks;
  
  log(`\nTotal Checks: ${totalChecks}`, 'cyan');
  log(`Passed: ${passedChecks}`, 'green');
  log(`Failed: ${failedChecks}`, failedChecks > 0 ? 'red' : 'green');
  
  log('\nDetailed Results:', 'cyan');
  Object.entries(results).forEach(([check, passed]) => {
    const status = passed ? '✓' : '✗';
    const color = passed ? 'green' : 'red';
    log(`  ${status} ${check}`, color);
  });
  
  if (failedChecks === 0) {
    log('\n✓ All checks passed! CI/CD pipeline is properly configured.', 'green');
    return true;
  } else {
    log('\n✗ Some checks failed. Please review the issues above.', 'red');
    return false;
  }
}

function main() {
  log('='.repeat(60), 'blue');
  log('CI/CD PIPELINE SETUP VERIFICATION', 'blue');
  log('='.repeat(60), 'blue');
  
  const results = {
    'GitHub Directory': checkGitHubDirectory(),
    'CI Workflow': checkWorkflowFile('CI Workflow', '.github/workflows/ci.yml'),
    'Build Workflow': checkWorkflowFile('Build Workflow', '.github/workflows/build.yml'),
    'Release Workflow': checkWorkflowFile('Release Workflow', '.github/workflows/release.yml'),
    'Performance Workflow': checkWorkflowFile('Performance Workflow', '.github/workflows/performance.yml'),
    'Security Workflow': checkWorkflowFile('Security Workflow', '.github/workflows/security.yml'),
    'Documentation': checkDocumentation(),
    'Package.json Scripts': checkPackageJson()
  };
  
  const allPassed = generateReport(results);
  
  if (allPassed) {
    log('\nNext Steps:', 'cyan');
    log('1. Configure required secrets in GitHub repository settings', 'yellow');
    log('2. Set up branch protection rules', 'yellow');
    log('3. Test workflows by creating a pull request', 'yellow');
    log('4. Review CI/CD_PIPELINE_GUIDE.md for detailed instructions', 'yellow');
  } else {
    log('\nPlease fix the issues above before proceeding.', 'yellow');
  }
  
  process.exit(allPassed ? 0 : 1);
}

// Run verification
main();
