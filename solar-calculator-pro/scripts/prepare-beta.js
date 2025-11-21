/**
 * Beta Preparation Script
 * 
 * Prepares the project for beta release
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CHECKS = {
  code: [],
  documentation: [],
  infrastructure: [],
  build: [],
};

/**
 * Run a check and record result
 */
function runCheck(category, name, checkFn) {
  try {
    const result = checkFn();
    CHECKS[category].push({
      name,
      passed: result.passed,
      message: result.message,
    });
    
    if (result.passed) {
      console.log(`✓ ${name}`);
    } else {
      console.log(`✗ ${name}: ${result.message}`);
    }
    
    return result.passed;
  } catch (error) {
    CHECKS[category].push({
      name,
      passed: false,
      message: error.message,
    });
    console.log(`✗ ${name}: ${error.message}`);
    return false;
  }
}

/**
 * Check if git is clean
 */
function checkGitClean() {
  try {
    const status = execSync('git status --porcelain', { encoding: 'utf-8' });
    return {
      passed: status.trim() === '',
      message: status.trim() ? 'Uncommitted changes exist' : 'Git is clean',
    };
  } catch (error) {
    return { passed: false, message: 'Git check failed' };
  }
}

/**
 * Check if tests pass
 */
function checkTests() {
  try {
    // Check if test command exists
    const packageJson = require('../package.json');
    if (!packageJson.scripts || !packageJson.scripts.test) {
      return { passed: true, message: 'No test script defined' };
    }
    
    execSync('npm test', { stdio: 'ignore' });
    return { passed: true, message: 'All tests passing' };
  } catch (error) {
    return { passed: false, message: 'Tests failing' };
  }
}

/**
 * Check if dependencies are up to date
 */
function checkDependencies() {
  try {
    const outdated = execSync('npm outdated --json', { encoding: 'utf-8' });
    const packages = JSON.parse(outdated || '{}');
    const count = Object.keys(packages).length;
    
    return {
      passed: count === 0,
      message: count > 0 ? `${count} outdated packages` : 'All dependencies up to date',
    };
  } catch (error) {
    return { passed: true, message: 'Dependencies check completed' };
  }
}

/**
 * Check if documentation exists
 */
function checkDocumentation() {
  const requiredDocs = [
    'docs/BETA_TESTING_GUIDE.md',
    'docs/BETA_RELEASE_CHECKLIST.md',
    'README.md',
  ];
  
  const missing = requiredDocs.filter(doc => {
    return !fs.existsSync(path.join(__dirname, '..', doc));
  });
  
  return {
    passed: missing.length === 0,
    message: missing.length > 0 ? `Missing: ${missing.join(', ')}` : 'All documentation present',
  };
}

/**
 * Check if release notes exist
 */
function checkReleaseNotes() {
  const releaseNotesPath = path.join(__dirname, '../docs/RELEASE_NOTES.md');
  const exists = fs.existsSync(releaseNotesPath);
  
  return {
    passed: exists,
    message: exists ? 'Release notes exist' : 'Release notes missing',
  };
}

/**
 * Check if beta config exists
 */
function checkBetaConfig() {
  const configPath = path.join(__dirname, '../build/beta-config.js');
  const exists = fs.existsSync(configPath);
  
  if (!exists) {
    return { passed: false, message: 'Beta config missing' };
  }
  
  try {
    const config = require(configPath);
    const required = ['isBeta', 'betaChannel', 'crashReporting', 'feedback'];
    const missing = required.filter(key => !(key in config));
    
    return {
      passed: missing.length === 0,
      message: missing.length > 0 ? `Missing config: ${missing.join(', ')}` : 'Beta config valid',
    };
  } catch (error) {
    return { passed: false, message: 'Beta config invalid' };
  }
}

/**
 * Check if Sentry is configured
 */
function checkSentry() {
  const hasDsn = !!process.env.SENTRY_DSN_BETA;
  
  return {
    passed: hasDsn,
    message: hasDsn ? 'Sentry DSN configured' : 'Sentry DSN not configured (set SENTRY_DSN_BETA)',
  };
}

/**
 * Check if build scripts exist
 */
function checkBuildScripts() {
  const requiredScripts = [
    'build/beta-build.js',
    'scripts/generate-release-notes.js',
  ];
  
  const missing = requiredScripts.filter(script => {
    return !fs.existsSync(path.join(__dirname, '..', script));
  });
  
  return {
    passed: missing.length === 0,
    message: missing.length > 0 ? `Missing: ${missing.join(', ')}` : 'All build scripts present',
  };
}

/**
 * Check if assets exist
 */
function checkAssets() {
  const requiredAssets = [
    'assets/icon-beta.ico',
    'assets/icon-beta.icns',
    'assets/icon-beta.png',
  ];
  
  const missing = requiredAssets.filter(asset => {
    return !fs.existsSync(path.join(__dirname, '..', asset));
  });
  
  return {
    passed: missing.length === 0,
    message: missing.length > 0 ? `Missing: ${missing.join(', ')}` : 'All assets present',
  };
}

/**
 * Generate report
 */
function generateReport() {
  console.log('\n=== Beta Preparation Report ===\n');
  
  const categories = Object.keys(CHECKS);
  let totalPassed = 0;
  let totalFailed = 0;
  
  for (const category of categories) {
    const checks = CHECKS[category];
    const passed = checks.filter(c => c.passed).length;
    const failed = checks.filter(c => !c.passed).length;
    
    totalPassed += passed;
    totalFailed += failed;
    
    console.log(`${category.toUpperCase()}:`);
    console.log(`  Passed: ${passed}`);
    console.log(`  Failed: ${failed}`);
    
    if (failed > 0) {
      console.log('  Failed checks:');
      checks.filter(c => !c.passed).forEach(c => {
        console.log(`    - ${c.name}: ${c.message}`);
      });
    }
    console.log('');
  }
  
  console.log('TOTAL:');
  console.log(`  Passed: ${totalPassed}`);
  console.log(`  Failed: ${totalFailed}`);
  console.log('');
  
  const readyForBeta = totalFailed === 0;
  
  if (readyForBeta) {
    console.log('✓ Ready for beta release!');
    console.log('\nNext steps:');
    console.log('1. Run: npm run build:beta');
    console.log('2. Test the beta build');
    console.log('3. Upload to beta server');
    console.log('4. Send invitations to beta testers');
  } else {
    console.log('✗ Not ready for beta release');
    console.log('\nPlease address the failed checks above.');
  }
  
  return readyForBeta;
}

/**
 * Main function
 */
function main() {
  console.log('=== Beta Preparation Check ===\n');
  console.log('Checking if project is ready for beta release...\n');
  
  // Code checks
  console.log('CODE CHECKS:');
  runCheck('code', 'Git repository clean', checkGitClean);
  runCheck('code', 'Tests passing', checkTests);
  runCheck('code', 'Dependencies up to date', checkDependencies);
  console.log('');
  
  // Documentation checks
  console.log('DOCUMENTATION CHECKS:');
  runCheck('documentation', 'Required documentation exists', checkDocumentation);
  runCheck('documentation', 'Release notes exist', checkReleaseNotes);
  console.log('');
  
  // Infrastructure checks
  console.log('INFRASTRUCTURE CHECKS:');
  runCheck('infrastructure', 'Beta configuration valid', checkBetaConfig);
  runCheck('infrastructure', 'Sentry configured', checkSentry);
  console.log('');
  
  // Build checks
  console.log('BUILD CHECKS:');
  runCheck('build', 'Build scripts exist', checkBuildScripts);
  runCheck('build', 'Beta assets exist', checkAssets);
  console.log('');
  
  // Generate report
  const ready = generateReport();
  
  // Exit with appropriate code
  process.exit(ready ? 0 : 1);
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  runCheck,
  generateReport,
};
