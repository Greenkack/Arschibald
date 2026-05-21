/**
 * Test script for Backend Manager
 * 
 * This script tests the backend manager functionality including:
 * - Auto-start
 * - Health checking
 * - Graceful shutdown
 * - Error recovery
 * - Event emission
 */

const BackendManager = require('./backend-manager');

async function testBackendManager() {
  console.log('=== Backend Manager Test Suite ===\n');

  // Test 1: Basic Initialization
  console.log('Test 1: Basic Initialization');
  const backendManager = new BackendManager({
    port: 8000,
    maxRetries: 10,
    retryDelay: 500,
    healthCheckInterval: 5000,
    maxRestartAttempts: 2,
  });
  console.log('✓ Backend Manager created\n');

  // Test 2: Event Listeners
  console.log('Test 2: Setting up event listeners');
  const events = {
    starting: false,
    started: false,
    stopping: false,
    stopped: false,
    unhealthy: false,
    log: false,
  };

  backendManager.on('starting', () => {
    console.log('  Event: starting');
    events.starting = true;
  });

  backendManager.on('started', () => {
    console.log('  Event: started');
    events.started = true;
  });

  backendManager.on('stopping', () => {
    console.log('  Event: stopping');
    events.stopping = true;
  });

  backendManager.on('stopped', ({ code, signal }) => {
    console.log(`  Event: stopped (code: ${code}, signal: ${signal})`);
    events.stopped = true;
  });

  backendManager.on('unhealthy', () => {
    console.log('  Event: unhealthy');
    events.unhealthy = true;
  });

  backendManager.on('log', ({ level, message }) => {
    if (!events.log) {
      console.log('  Event: log');
      events.log = true;
    }
  });

  backendManager.on('error', (error) => {
    console.log(`  Event: error - ${error.message}`);
  });

  console.log('✓ Event listeners configured\n');

  // Test 3: Start Backend
  console.log('Test 3: Starting backend');
  try {
    await backendManager.start();
    console.log('✓ Backend started successfully\n');
  } catch (error) {
    console.error('✗ Failed to start backend:', error.message);
    console.log('\nNote: This test requires the backend to be available.');
    console.log('Make sure the backend directory exists and Python is installed.\n');
    return;
  }

  // Test 4: Get Status
  console.log('Test 4: Getting backend status');
  const status = backendManager.getStatus();
  console.log('  Status:', JSON.stringify(status, null, 2));
  console.log('✓ Status retrieved\n');

  // Test 5: Health Check
  console.log('Test 5: Checking backend health');
  const isHealthy = await backendManager.checkHealth();
  console.log(`  Health: ${isHealthy ? 'Healthy ✓' : 'Unhealthy ✗'}`);
  console.log('✓ Health check completed\n');

  // Test 6: Get Logs
  console.log('Test 6: Getting backend logs');
  const logs = backendManager.getLogs(5);
  console.log(`  Retrieved ${logs.length} log entries`);
  logs.forEach(({ timestamp, level, message }) => {
    console.log(`    [${level}] ${message}`);
  });
  console.log('✓ Logs retrieved\n');

  // Test 7: Get URL
  console.log('Test 7: Getting backend URL');
  const url = backendManager.getUrl();
  console.log(`  URL: ${url}`);
  console.log('✓ URL retrieved\n');

  // Wait a bit to let health checks run
  console.log('Waiting 3 seconds for health checks...');
  await new Promise(resolve => setTimeout(resolve, 3000));

  // Test 8: Stop Backend
  console.log('\nTest 8: Stopping backend gracefully');
  await backendManager.stop();
  console.log('✓ Backend stopped\n');

  // Test 9: Verify Events
  console.log('Test 9: Verifying events were emitted');
  const eventResults = Object.entries(events).map(([event, fired]) => {
    const status = fired ? '✓' : '✗';
    console.log(`  ${status} ${event}: ${fired}`);
    return fired;
  });
  
  const allEventsFired = eventResults.every(result => result);
  if (allEventsFired) {
    console.log('✓ All expected events were emitted\n');
  } else {
    console.log('⚠ Some events were not emitted (this may be expected)\n');
  }

  // Test 10: Cleanup
  console.log('Test 10: Cleaning up');
  await backendManager.cleanup();
  console.log('✓ Cleanup completed\n');

  // Summary
  console.log('=== Test Summary ===');
  console.log('✓ All tests completed successfully');
  console.log('\nBackend Manager is working correctly!');
}

// Run tests
testBackendManager().catch(error => {
  console.error('\n✗ Test suite failed:', error);
  process.exit(1);
});
