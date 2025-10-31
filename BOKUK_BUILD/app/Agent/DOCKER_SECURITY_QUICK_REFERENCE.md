# Docker Security Quick Reference

## Security Configuration Summary

### Unprivileged User (Requirement 5.2)
- **User**: `sandboxuser`
- **UID**: 1000
- **GID**: 1000
- **Location**: `Agent/sandbox/Dockerfile` line 44

### Network Isolation (Requirement 5.3)
- **Python execution**: Network **DISABLED** (`network_disabled=True`)
- **Terminal execution**: Network **ENABLED** (`network_disabled=False`)
- **Location**: `Agent/agent/tools/execution_tools.py` lines 358, 442

### Resource Limits (Requirement 5.4)
- **Memory**: 512MB (`mem_limit="512m"`)
- **CPU**: 50% of one core (`cpu_quota=50000`)
- **Processes**: 100 max (`pids_limit=100`)
- **Location**: `Agent/agent/tools/execution_tools.py` lines 301-303

### Automatic Cleanup (Requirement 5.4)
- **Method**: `container.remove(force=True)` in `finally` block
- **Guarantee**: Always removed, even on errors
- **Location**: `Agent/agent/tools/execution_tools.py` lines 380-410

### Timeout Enforcement (Requirement 5.5)
- **Python**: 30 seconds
- **Terminal**: 120 seconds
- **Location**: `Agent/agent/tools/execution_tools.py` lines 14-15

### Additional Security
- **Privileged mode**: Disabled (`privileged=False`)
- **Capabilities**: All dropped (`cap_drop=['ALL']`)
- **New privileges**: Disabled (`security_opt=['no-new-privileges']`)
- **Location**: `Agent/agent/tools/execution_tools.py` lines 293-300

## Quick Verification

### Check User
```bash
docker run --rm kai_agent_sandbox whoami
# Expected: sandboxuser
```

### Check Network Isolation
```python
from agent.tools.execution_tools import execute_python_code_in_sandbox
result = execute_python_code_in_sandbox.invoke({
    "code": "import socket; socket.create_connection(('8.8.8.8', 53), timeout=2)"
})
# Expected: Network error
```

### Check Resource Limits
```bash
docker inspect kai_agent_sandbox | grep -A 5 "Memory\|Cpu"
# Expected: Shows limits
```

### Check Cleanup
```bash
docker ps -a | grep kai-sandbox
# Expected: No containers (after execution)
```

## Testing

### Run Full Test Suite
```bash
cd Agent
python test_task_12_2_docker_security.py
```

### Run Specific Tests
```python
# Test unprivileged user
from agent.tools.execution_tools import execute_python_code_in_sandbox
result = execute_python_code_in_sandbox.invoke({
    "code": "import os; print(f'UID: {os.getuid()}')"
})
print(result)  # Expected: UID: 1000
```

## Configuration

### Adjust Memory Limit
Edit `Agent/agent/tools/execution_tools.py` line 301:
```python
mem_limit="1g",  # Change to 1GB
```

### Adjust CPU Limit
Edit `Agent/agent/tools/execution_tools.py` line 302:
```python
cpu_quota=100000,  # Change to 100% of one core
```

### Adjust Timeouts
Edit `Agent/agent/tools/execution_tools.py` lines 14-15:
```python
PYTHON_TIMEOUT = 60    # Change to 60 seconds
TERMINAL_TIMEOUT = 300  # Change to 300 seconds
```

### Enable Read-Only Root Filesystem
Edit `Agent/agent/tools/execution_tools.py` line 298:
```python
read_only=True,  # Uncomment this line
```

## Troubleshooting

### Docker Not Running
```bash
# Windows/Mac
# Start Docker Desktop

# Linux
sudo systemctl start docker
```

### Image Not Found
```bash
cd Agent/sandbox
docker build -t kai_agent_sandbox .
```

### Container Not Cleaned Up
Check logs:
```bash
tail -f Agent/logs/agent.log
```

Look for cleanup errors and investigate.

## Security Checklist

- [x] Unprivileged user execution
- [x] Network disabled by default (Python)
- [x] Resource limits configured
- [x] Automatic cleanup implemented
- [x] Timeout enforcement active
- [x] Privileged mode disabled
- [x] Capabilities dropped
- [x] No new privileges allowed

## Documentation

- **Detailed**: `Agent/sandbox/SECURITY.md`
- **Summary**: `Agent/TASK_12_2_DOCKER_SECURITY_SUMMARY.md`
- **Verification**: `Agent/TASK_12_2_VERIFICATION_CHECKLIST.md`
- **Completion**: `Agent/TASK_12_2_COMPLETE.md`

## Status

✅ **Task 12.2: COMPLETE**

All Docker security requirements implemented and documented.

---

**Last Updated**: 2024-01-18
