#!/usr/bin/env node

/**
 * Setup Verification Script
 * Checks if all required tools and configurations are in place
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkCommand(command, name, minVersion = null) {
  try {
    const output = execSync(command, { encoding: 'utf8', stdio: 'pipe' });
    const version = output.trim().split('\n')[0];
    log(`✓ ${name}: ${version}`, 'green');
    return true;
  } catch (error) {
    log(`✗ ${name}: Not found`, 'red');
    return false;
  }
}

function checkFile(filePath, description) {
  if (fs.existsSync(filePath)) {
    log(`✓ ${description}`, 'green');
    return true;
  } else {
    log(`✗ ${description}`, 'red');
    return false;
  }
}

function checkDirectory(dirPath, description) {
  if (fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory()) {
    log(`✓ ${description}`, 'green');
    return true;
  } else {
    log(`✗ ${description}`, 'red');
    return false;
  }
}

async function main() {
  log('\n=== Solar Calculator Pro - Setup Verification ===\n', 'blue');

  let allChecks = true;

  // Check system requirements
  log('Checking System Requirements:', 'yellow');
  allChecks &= checkCommand('node --version', 'Node.js');
  allChecks &= checkCommand('npm --version', 'npm');
  allChecks &= checkCommand('python --version || python3 --version', 'Python');
  allChecks &= checkCommand('git --version', 'Git');
  console.log();

  // Check project structure
  log('Checking Project Structure:', 'yellow');
  allChecks &= checkDirectory('frontend', 'Frontend directory');
  allChecks &= checkDirectory('backend', 'Backend directory');
  allChecks &= checkDirectory('electron', 'Electron directory');
  allChecks &= checkDirectory('docs', 'Documentation directory');
  console.log();

  // Check configuration files
  log('Checking Configuration Files:', 'yellow');
  allChecks &= checkFile('package.json', 'Root package.json');
  allChecks &= checkFile('frontend/package.json', 'Frontend package.json');
  allChecks &= checkFile('frontend/tsconfig.json', 'TypeScript config');
  allChecks &= checkFile('frontend/vite.config.ts', 'Vite config');
  allChecks &= checkFile('frontend/.eslintrc.cjs', 'ESLint config');
  allChecks &= checkFile('frontend/.prettierrc', 'Prettier config');
  allChecks &= checkFile('backend/requirements.txt', 'Backend requirements');
  allChecks &= checkFile('backend/pyproject.toml', 'Python project config');
  allChecks &= checkFile('backend/.flake8', 'Flake8 config');
  allChecks &= checkFile('backend/main.py', 'Backend entry point');
  console.log();

  // Check source directories
  log('Checking Source Directories:', 'yellow');
  allChecks &= checkDirectory('frontend/src', 'Frontend source');
  allChecks &= checkDirectory('frontend/src/components', 'Components directory');
  allChecks &= checkDirectory('frontend/src/pages', 'Pages directory');
  allChecks &= checkDirectory('frontend/src/hooks', 'Hooks directory');
  allChecks &= checkDirectory('frontend/src/services', 'Services directory');
  allChecks &= checkDirectory('frontend/src/store', 'Store directory');
  allChecks &= checkDirectory('backend/api', 'Backend API directory');
  allChecks &= checkDirectory('backend/services', 'Backend services directory');
  allChecks &= checkDirectory('backend/tests', 'Backend tests directory');
  console.log();

  // Check Git hooks
  log('Checking Git Hooks:', 'yellow');
  allChecks &= checkDirectory('.husky', 'Husky directory');
  allChecks &= checkFile('.husky/pre-commit', 'Pre-commit hook');
  console.log();

  // Check documentation
  log('Checking Documentation:', 'yellow');
  allChecks &= checkFile('README.md', 'Main README');
  allChecks &= checkFile('QUICK_START.md', 'Quick start guide');
  allChecks &= checkFile('docs/SETUP_GUIDE.md', 'Setup guide');
  allChecks &= checkFile('docs/PROJECT_OVERVIEW.md', 'Project overview');
  console.log();

  // Check if dependencies are installed
  log('Checking Dependencies:', 'yellow');
  const nodeModulesExists = fs.existsSync('node_modules');
  const frontendNodeModulesExists = fs.existsSync('frontend/node_modules');
  const backendVenvExists = fs.existsSync('backend/venv') || fs.existsSync('backend/.venv');

  if (nodeModulesExists) {
    log('✓ Root dependencies installed', 'green');
  } else {
    log('✗ Root dependencies not installed (run: npm install)', 'yellow');
  }

  if (frontendNodeModulesExists) {
    log('✓ Frontend dependencies installed', 'green');
  } else {
    log('✗ Frontend dependencies not installed (run: cd frontend && npm install)', 'yellow');
  }

  if (backendVenvExists) {
    log('✓ Backend virtual environment exists', 'green');
  } else {
    log('✗ Backend virtual environment not created (run: cd backend && python -m venv venv)', 'yellow');
  }
  console.log();

  // Final summary
  log('=== Summary ===\n', 'blue');
  if (allChecks) {
    log('✓ All checks passed! Setup is complete.', 'green');
    log('\nNext steps:', 'blue');
    log('1. Install dependencies if not already done:', 'reset');
    log('   npm install', 'reset');
    log('   cd frontend && npm install', 'reset');
    log('   cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt', 'reset');
    log('\n2. Start development:', 'reset');
    log('   npm run electron:dev', 'reset');
    log('\n3. Read QUICK_START.md for detailed instructions', 'reset');
  } else {
    log('✗ Some checks failed. Please review the output above.', 'red');
    log('\nRefer to SETUP_GUIDE.md for detailed setup instructions.', 'yellow');
  }
  console.log();
}

main().catch(console.error);
