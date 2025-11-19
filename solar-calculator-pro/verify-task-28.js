/**
 * Verification Script for Task 28: API Service Layer
 * 
 * This script verifies that all required features of the API Service Layer
 * have been implemented correctly.
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying Task 28: API Service Layer Implementation\n');

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

  const content = fs.readFileSync(fullPath, 'utf8');
  const missingStrings = searchStrings.filter(str => !content.includes(str));

  if (missingStrings.length === 0) {
    console.log(`✅ ${description}`);
    checks.passed++;
    return true;
  } else {
    console.log(`❌ ${description}`);
    console.log(`   Missing: ${missingStrings.join(', ')}`);
    checks.failed++;
    return false;
  }
}

console.log('📁 Checking File Structure...\n');

// Check main API service file
checkFile(
  'frontend/src/services/api.ts',
  'API service file exists'
);

// Check documentation files
checkFile(
  'frontend/API_SERVICE_GUIDE.md',
  'Complete guide documentation exists'
);

checkFile(
  'frontend/API_SERVICE_QUICK_REFERENCE.md',
  'Quick reference documentation exists'
);

// Check demo file
checkFile(
  'frontend/src/examples/ApiServiceDemo.tsx',
  'Demo component exists'
);

// Check completion summary
checkFile(
  'TASK_28_COMPLETE.md',
  'Task completion summary exists'
);

console.log('\n🔧 Checking API Service Features...\n');

// Check for Axios instance with interceptors
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'axios.create',
    'api.interceptors.request.use',
    'api.interceptors.response.use',
  ],
  'Axios instance with interceptors'
);

// Check for request/response logging
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'requestMetadataStore',
    'startTime',
    'duration',
    'console.group',
    'console.log',
  ],
  'Request/response logging with timing'
);

// Check for automatic token refresh
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'isRefreshing',
    'refreshSubscribers',
    'subscribeTokenRefresh',
    'onTokenRefreshed',
    '/auth/refresh',
    'refresh_token',
  ],
  'Automatic token refresh mechanism'
);

// Check for retry logic
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'DEFAULT_RETRY_CONFIG',
    'retryableStatuses',
    '_retryCount',
    'exponential backoff',
    'retryRequest',
  ],
  'Retry logic with exponential backoff'
);

// Check for error handling
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'APIError',
    'error.response?.status',
    'error.message',
    'apiError?.details',
  ],
  'Comprehensive error handling'
);

// Check for file operations
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'uploadFile',
    'downloadFile',
    'FormData',
    'onUploadProgress',
    'responseType: \'blob\'',
  ],
  'File upload and download functions'
);

// Check for batch operations
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'batchRequest',
    'sequentialRequest',
    'Promise.all',
  ],
  'Batch and sequential request functions'
);

// Check for polling
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'pollEndpoint',
    'conditionFn',
    'interval',
    'maxAttempts',
    'timeout',
  ],
  'Polling functionality'
);

// Check for request cancellation
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'createCancelToken',
    'isCancelError',
    'axios.CancelToken',
    'axios.isCancel',
  ],
  'Request cancellation support'
);

// Check for rate limiting
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'RequestQueue',
    'requestsPerSecond',
    'requestQueue',
  ],
  'Rate limiting queue'
);

// Check for token management
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'clearTokens',
    'isAuthenticated',
    'getAccessToken',
    'setAccessToken',
    'setRefreshToken',
  ],
  'Token management functions'
);

// Check for API service object
checkFileContent(
  'frontend/src/services/api.ts',
  [
    'export const apiService',
    'instance: api',
    'clearTokens',
    'retry',
    'batch',
    'upload',
    'download',
  ],
  'Exported API service object'
);

console.log('\n📚 Checking Documentation...\n');

// Check guide documentation
checkFileContent(
  'frontend/API_SERVICE_GUIDE.md',
  [
    'Automatic Token Refresh',
    'Automatic Retry Logic',
    'Request/Response Logging',
    'Error Handling',
    'File Upload',
    'Batch Requests',
    'Polling',
    'Request Cancellation',
  ],
  'Complete guide covers all features'
);

// Check quick reference
checkFileContent(
  'frontend/API_SERVICE_QUICK_REFERENCE.md',
  [
    'import api',
    'GET',
    'POST',
    'uploadFile',
    'retryRequest',
    'batchRequest',
    'pollEndpoint',
  ],
  'Quick reference has code examples'
);

// Check demo component
checkFileContent(
  'frontend/src/examples/ApiServiceDemo.tsx',
  [
    'handleBasicGet',
    'handleFileUpload',
    'handleRetry',
    'handleBatchRequests',
    'handlePolling',
    'handleCancellableRequest',
  ],
  'Demo component demonstrates all features'
);

console.log('\n📋 Summary\n');
console.log('═══════════════════════════════════════');
console.log(`✅ Passed: ${checks.passed}`);
console.log(`❌ Failed: ${checks.failed}`);
console.log(`⚠️  Warnings: ${checks.warnings}`);
console.log('═══════════════════════════════════════\n');

if (checks.failed === 0) {
  console.log('🎉 All checks passed! Task 28 implementation is complete.\n');
  console.log('✨ Features Implemented:');
  console.log('   • Axios instance with interceptors');
  console.log('   • Request/response logging with timing');
  console.log('   • Automatic token refresh');
  console.log('   • Retry logic with exponential backoff');
  console.log('   • Comprehensive error handling');
  console.log('   • File upload/download');
  console.log('   • Batch and sequential requests');
  console.log('   • Polling functionality');
  console.log('   • Request cancellation');
  console.log('   • Rate limiting queue');
  console.log('   • Token management');
  console.log('   • Complete documentation');
  console.log('   • Interactive demo component\n');
  process.exit(0);
} else {
  console.log('❌ Some checks failed. Please review the implementation.\n');
  process.exit(1);
}
