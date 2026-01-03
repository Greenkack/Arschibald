"""
Electron-Backend Process Management Tests
Task 237: Electron-Backend Process Management Testing

Tests for:
- Backend auto-start on application launch
- Backend health check and monitoring
- Backend graceful shutdown
- Backend restart on failure
- Backend port configuration
- Backend process isolation
- Backend error recovery
- Backend logging integration
"""

import pytest
import asyncio
import time
import os
import signal
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ProcessState(str, Enum):
    """Backend process states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    RESTARTING = "restarting"


@dataclass
class HealthCheckResult:
    """Health check result"""
    healthy: bool
    status_code: int
    response_time_ms: float
    message: str
    timestamp: float


@dataclass
class ProcessConfig:
    """Backend process configuration"""
    port: int = 8000
    host: str = "127.0.0.1"
    auto_restart: bool = True
    max_restart_attempts: int = 3
    health_check_interval: int = 5
    startup_timeout: int = 30
    shutdown_timeout: int = 10
    log_level: str = "INFO"


class MockBackendProcess:
    """Mock backend process for testing"""
    
    def __init__(self, config: ProcessConfig):
        self.config = config
        self.state = ProcessState.STOPPED
        self.pid: Optional[int] = None
        self.start_time: Optional[float] = None
        self.restart_count = 0
        self.logs: list = []
        self._health_check_responses: list = []
        self._should_fail_start = False
        self._should_crash = False
    
    def start(self) -> bool:
        """Start the backend process"""
        if self._should_fail_start:
            self.state = ProcessState.ERROR
            self.logs.append("ERROR: Failed to start backend")
            return False
        
        self.state = ProcessState.STARTING
        self.logs.append(f"INFO: Starting backend on {self.config.host}:{self.config.port}")
        
        # Simulate startup
        time.sleep(0.1)
        
        self.state = ProcessState.RUNNING
        self.pid = 12345
        self.start_time = time.time()
        self.logs.append(f"INFO: Backend started with PID {self.pid}")
        return True
    
    def stop(self, graceful: bool = True) -> bool:
        """Stop the backend process"""
        if self.state != ProcessState.RUNNING:
            return False
        
        self.state = ProcessState.STOPPING
        self.logs.append("INFO: Stopping backend...")
        
        if graceful:
            # Simulate graceful shutdown
            time.sleep(0.1)
            self.logs.append("INFO: Graceful shutdown completed")
        else:
            self.logs.append("WARNING: Forced shutdown")
        
        self.state = ProcessState.STOPPED
        self.pid = None
        return True
    
    def restart(self) -> bool:
        """Restart the backend process"""
        self.state = ProcessState.RESTARTING
        self.restart_count += 1
        self.logs.append(f"INFO: Restarting backend (attempt {self.restart_count})")
        
        self.stop(graceful=True)
        return self.start()
    
    def health_check(self) -> HealthCheckResult:
        """Perform health check"""
        if self.state != ProcessState.RUNNING:
            return HealthCheckResult(
                healthy=False,
                status_code=503,
                response_time_ms=0,
                message="Backend not running",
                timestamp=time.time()
            )
        
        if self._should_crash:
            self.state = ProcessState.ERROR
            return HealthCheckResult(
                healthy=False,
                status_code=500,
                response_time_ms=0,
                message="Backend crashed",
                timestamp=time.time()
            )
        
        return HealthCheckResult(
            healthy=True,
            status_code=200,
            response_time_ms=15.5,
            message="OK",
            timestamp=time.time()
        )
    
    def get_logs(self, lines: int = 100) -> list:
        """Get recent logs"""
        return self.logs[-lines:]
    
    def simulate_crash(self):
        """Simulate a backend crash"""
        self._should_crash = True
        self.state = ProcessState.ERROR
        self.logs.append("ERROR: Backend crashed unexpectedly")
    
    def simulate_start_failure(self):
        """Simulate start failure"""
        self._should_fail_start = True


class BackendProcessManager:
    """Manager for backend process lifecycle"""
    
    def __init__(self, config: ProcessConfig):
        self.config = config
        self.process: Optional[MockBackendProcess] = None
        self._monitoring = False
        self._restart_attempts = 0
    
    def initialize(self) -> bool:
        """Initialize and start the backend"""
        self.process = MockBackendProcess(self.config)
        return self.process.start()
    
    def shutdown(self, graceful: bool = True) -> bool:
        """Shutdown the backend"""
        if self.process:
            return self.process.stop(graceful)
        return False
    
    def is_healthy(self) -> bool:
        """Check if backend is healthy"""
        if not self.process:
            return False
        result = self.process.health_check()
        return result.healthy
    
    def handle_failure(self) -> bool:
        """Handle backend failure with auto-restart"""
        if not self.config.auto_restart:
            return False
        
        if self._restart_attempts >= self.config.max_restart_attempts:
            return False
        
        self._restart_attempts += 1
        if self.process:
            return self.process.restart()
        return False
    
    def reset_restart_counter(self):
        """Reset restart counter after successful recovery"""
        self._restart_attempts = 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "state": self.process.state.value if self.process else "not_initialized",
            "pid": self.process.pid if self.process else None,
            "port": self.config.port,
            "restart_attempts": self._restart_attempts,
            "uptime": time.time() - self.process.start_time if self.process and self.process.start_time else 0
        }


# ============================================================================
# Test Classes
# ============================================================================

class TestBackendAutoStart:
    """Tests for backend auto-start on application launch"""
    
    def test_backend_starts_automatically(self):
        """Test that backend starts automatically"""
        config = ProcessConfig(port=8000)
        manager = BackendProcessManager(config)
        
        result = manager.initialize()
        
        assert result is True
        assert manager.process.state == ProcessState.RUNNING
        assert manager.process.pid is not None
    
    def test_backend_starts_on_configured_port(self):
        """Test that backend starts on configured port"""
        config = ProcessConfig(port=8080)
        manager = BackendProcessManager(config)
        
        manager.initialize()
        
        assert manager.config.port == 8080
        status = manager.get_status()
        assert status["port"] == 8080
    
    def test_backend_logs_startup(self):
        """Test that backend logs startup events"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        
        manager.initialize()
        
        logs = manager.process.get_logs()
        assert any("Starting backend" in log for log in logs)
        assert any("Backend started" in log for log in logs)


class TestHealthCheckMonitoring:
    """Tests for backend health check and monitoring"""
    
    def test_health_check_returns_healthy(self):
        """Test health check returns healthy when running"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        manager.initialize()
        
        result = manager.process.health_check()
        
        assert result.healthy is True
        assert result.status_code == 200
        assert result.response_time_ms > 0
    
    def test_health_check_returns_unhealthy_when_stopped(self):
        """Test health check returns unhealthy when stopped"""
        config = ProcessConfig()
        process = MockBackendProcess(config)
        
        result = process.health_check()
        
        assert result.healthy is False
        assert result.status_code == 503
    
    def test_is_healthy_method(self):
        """Test is_healthy convenience method"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        manager.initialize()
        
        assert manager.is_healthy() is True
        
        manager.shutdown()
        assert manager.is_healthy() is False


class TestGracefulShutdown:
    """Tests for backend graceful shutdown"""
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        manager.initialize()
        
        result = manager.shutdown(graceful=True)
        
        assert result is True
        assert manager.process.state == ProcessState.STOPPED
        logs = manager.process.get_logs()
        assert any("Graceful shutdown" in log for log in logs)
    
    def test_forced_shutdown(self):
        """Test forced shutdown"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        manager.initialize()
        
        result = manager.shutdown(graceful=False)
        
        assert result is True
        assert manager.process.state == ProcessState.STOPPED
        logs = manager.process.get_logs()
        assert any("Forced shutdown" in log for log in logs)
    
    def test_shutdown_clears_pid(self):
        """Test that shutdown clears PID"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        manager.initialize()
        
        assert manager.process.pid is not None
        
        manager.shutdown()
        
        assert manager.process.pid is None


class TestRestartOnFailure:
    """Tests for backend restart on failure"""
    
    def test_auto_restart_on_crash(self):
        """Test automatic restart on crash"""
        config = ProcessConfig(auto_restart=True, max_restart_attempts=3)
        manager = BackendProcessManager(config)
        manager.initialize()
        
        # Simulate crash
        manager.process.simulate_crash()
        
        # Handle failure
        result = manager.handle_failure()
        
        assert result is True
        assert manager.process.state == ProcessState.RUNNING
    
    def test_restart_counter_increments(self):
        """Test that restart counter increments"""
        config = ProcessConfig(auto_restart=True, max_restart_attempts=3)
        manager = BackendProcessManager(config)
        manager.initialize()
        
        manager.handle_failure()
        assert manager._restart_attempts == 1
        
        manager.handle_failure()
        assert manager._restart_attempts == 2
    
    def test_max_restart_attempts_respected(self):
        """Test that max restart attempts is respected"""
        config = ProcessConfig(auto_restart=True, max_restart_attempts=2)
        manager = BackendProcessManager(config)
        manager.initialize()
        
        # First two restarts should succeed
        assert manager.handle_failure() is True
        assert manager.handle_failure() is True
        
        # Third should fail
        assert manager.handle_failure() is False
    
    def test_restart_counter_reset(self):
        """Test restart counter can be reset"""
        config = ProcessConfig(auto_restart=True, max_restart_attempts=3)
        manager = BackendProcessManager(config)
        manager.initialize()
        
        manager.handle_failure()
        manager.handle_failure()
        assert manager._restart_attempts == 2
        
        manager.reset_restart_counter()
        assert manager._restart_attempts == 0
    
    def test_no_restart_when_disabled(self):
        """Test no restart when auto_restart is disabled"""
        config = ProcessConfig(auto_restart=False)
        manager = BackendProcessManager(config)
        manager.initialize()
        
        result = manager.handle_failure()
        
        assert result is False


class TestPortConfiguration:
    """Tests for backend port configuration"""
    
    def test_default_port(self):
        """Test default port configuration"""
        config = ProcessConfig()
        assert config.port == 8000
    
    def test_custom_port(self):
        """Test custom port configuration"""
        config = ProcessConfig(port=9000)
        manager = BackendProcessManager(config)
        manager.initialize()
        
        status = manager.get_status()
        assert status["port"] == 9000
    
    def test_port_in_logs(self):
        """Test that port appears in startup logs"""
        config = ProcessConfig(port=8080)
        manager = BackendProcessManager(config)
        manager.initialize()
        
        logs = manager.process.get_logs()
        assert any("8080" in log for log in logs)


class TestProcessIsolation:
    """Tests for backend process isolation"""
    
    def test_separate_process_instances(self):
        """Test that multiple managers have separate processes"""
        config1 = ProcessConfig(port=8000)
        config2 = ProcessConfig(port=8001)
        
        manager1 = BackendProcessManager(config1)
        manager2 = BackendProcessManager(config2)
        
        manager1.initialize()
        manager2.initialize()
        
        # Processes should be different objects
        assert manager1.process is not manager2.process
        # Both should be running
        assert manager1.process.state == ProcessState.RUNNING
        assert manager2.process.state == ProcessState.RUNNING
    
    def test_process_state_isolation(self):
        """Test that process states are isolated"""
        config1 = ProcessConfig(port=8000)
        config2 = ProcessConfig(port=8001)
        
        manager1 = BackendProcessManager(config1)
        manager2 = BackendProcessManager(config2)
        
        manager1.initialize()
        manager2.initialize()
        
        manager1.shutdown()
        
        assert manager1.process.state == ProcessState.STOPPED
        assert manager2.process.state == ProcessState.RUNNING


class TestErrorRecovery:
    """Tests for backend error recovery"""
    
    def test_recovery_from_crash(self):
        """Test recovery from crash"""
        config = ProcessConfig(auto_restart=True)
        manager = BackendProcessManager(config)
        manager.initialize()
        
        # Simulate crash
        manager.process.simulate_crash()
        assert manager.process.state == ProcessState.ERROR
        
        # Recover
        manager.handle_failure()
        assert manager.process.state == ProcessState.RUNNING
    
    def test_recovery_logs_error(self):
        """Test that recovery logs the error"""
        config = ProcessConfig(auto_restart=True)
        manager = BackendProcessManager(config)
        manager.initialize()
        
        manager.process.simulate_crash()
        manager.handle_failure()
        
        logs = manager.process.get_logs()
        assert any("crashed" in log.lower() for log in logs)
        assert any("Restarting" in log for log in logs)
    
    def test_start_failure_handling(self):
        """Test handling of start failure"""
        config = ProcessConfig()
        process = MockBackendProcess(config)
        process.simulate_start_failure()
        
        result = process.start()
        
        assert result is False
        assert process.state == ProcessState.ERROR


class TestLoggingIntegration:
    """Tests for backend logging integration"""
    
    def test_logs_captured(self):
        """Test that logs are captured"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        manager.initialize()
        
        logs = manager.process.get_logs()
        
        assert len(logs) > 0
    
    def test_log_levels(self):
        """Test different log levels"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        manager.initialize()
        
        logs = manager.process.get_logs()
        
        # Should have INFO logs
        assert any("INFO:" in log for log in logs)
    
    def test_log_limit(self):
        """Test log line limit"""
        config = ProcessConfig()
        process = MockBackendProcess(config)
        
        # Add many logs
        for i in range(200):
            process.logs.append(f"Log line {i}")
        
        # Get limited logs
        logs = process.get_logs(lines=50)
        
        assert len(logs) == 50
    
    def test_error_logs_on_failure(self):
        """Test error logs on failure"""
        config = ProcessConfig()
        process = MockBackendProcess(config)
        process.simulate_start_failure()
        process.start()
        
        logs = process.get_logs()
        
        assert any("ERROR:" in log for log in logs)


class TestStatusReporting:
    """Tests for status reporting"""
    
    def test_status_includes_state(self):
        """Test status includes state"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        manager.initialize()
        
        status = manager.get_status()
        
        assert "state" in status
        assert status["state"] == "running"
    
    def test_status_includes_pid(self):
        """Test status includes PID"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        manager.initialize()
        
        status = manager.get_status()
        
        assert "pid" in status
        assert status["pid"] is not None
    
    def test_status_includes_uptime(self):
        """Test status includes uptime"""
        config = ProcessConfig()
        manager = BackendProcessManager(config)
        manager.initialize()
        
        time.sleep(0.1)
        status = manager.get_status()
        
        assert "uptime" in status
        assert status["uptime"] > 0
    
    def test_status_includes_restart_attempts(self):
        """Test status includes restart attempts"""
        config = ProcessConfig(auto_restart=True)
        manager = BackendProcessManager(config)
        manager.initialize()
        
        manager.handle_failure()
        status = manager.get_status()
        
        assert "restart_attempts" in status
        assert status["restart_attempts"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
