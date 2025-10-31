# Docker Sandbox Usage Guide

Quick reference for using the KAI Agent Docker sandbox for secure code execution.

## Quick Start

### 1. Build the Image

**Windows**:
```powershell
cd Agent\sandbox
.\build.ps1
```

**Linux/Mac**:
```bash
cd Agent/sandbox
./build.sh
```

### 2. Verify the Build

```bash
python Agent/verify_docker_build.py
```

### 3. Use the Tools

```python
from Agent.agent.tools.execution_tools import (
    execute_python_code_in_sandbox,
    run_terminal_command_in_sandbox
)

# Execute Python code
result = execute_python_code_in_sandbox.invoke({
    "code": "print('Hello from sandbox!')"
})

# Run terminal command
result = run_terminal_command_in_sandbox.invoke({
    "command": "pip list"
})
```

## Common Use Cases

### Execute Python Code

```python
code = """
import math

def calculate_area(radius):
    return math.pi * radius ** 2

print(f"Area of circle with radius 5: {calculate_area(5):.2f}")
"""

result = execute_python_code_in_sandbox.invoke({"code": code})
print(result)
```

### Install and Use Packages

```python
command = """
pip install requests &&
python -c "import requests; r = requests.get('https://api.github.com'); print(r.status_code)"
"""

result = run_terminal_command_in_sandbox.invoke({"command": command})
print(result)
```

### Run Tests

```python
# First, write test file
from Agent.agent.tools.coding_tools import write_file

write_file.invoke({
    "path": "test_example.py",
    "content": """
def test_addition():
    assert 1 + 1 == 2

def test_multiplication():
    assert 2 * 3 == 6
"""
})

# Then run tests
result = run_terminal_command_in_sandbox.invoke({
    "command": "pytest test_example.py -v"
})
print(result)
```

### File Operations

```python
command = """
echo 'Hello World' > test.txt &&
cat test.txt &&
ls -la
"""

result = run_terminal_command_in_sandbox.invoke({"command": command})
print(result)
```

## Security Features

### Network Isolation

**Python execution** - Network disabled:
```python
# This will fail (no network)
code = "import requests; requests.get('https://google.com')"
result = execute_python_code_in_sandbox.invoke({"code": code})
```

**Terminal commands** - Network enabled:
```python
# This will work (network enabled)
command = "curl https://api.github.com"
result = run_terminal_command_in_sandbox.invoke({"command": command})
```

### Timeouts

- **Python**: 30 seconds
- **Terminal**: 120 seconds

```python
# This will timeout after 30 seconds
code = "import time; time.sleep(60)"
result = execute_python_code_in_sandbox.invoke({"code": code})
# Output: "Execution timed out after 30 seconds..."
```

### Resource Limits

- **Memory**: 512MB
- **CPU**: 50% of one core
- **Processes**: Maximum 100

### Unprivileged User

All code runs as `sandboxuser` (not root):
```python
command = "whoami"
result = run_terminal_command_in_sandbox.invoke({"command": command})
# Output: "sandboxuser"
```

## Performance Monitoring

### Get Metrics

```python
from Agent.agent.tools.execution_tools import get_docker_metrics

metrics = get_docker_metrics()
print(f"Containers created: {metrics['containers_created']}")
print(f"Total execution time: {metrics['total_execution_time']:.2f}s")
print(f"Total cleanup time: {metrics['total_cleanup_time']:.2f}s")
```

### Monitor Resources

```python
from Agent.agent.tools.execution_tools import monitor_docker_resources

resources = monitor_docker_resources()
print(f"Running containers: {resources['running_containers']}")
for container in resources['containers']:
    print(f"  {container['name']}: {container['memory_mb']:.2f}MB")
```

### Reset Metrics

```python
from Agent.agent.tools.execution_tools import reset_docker_metrics

reset_docker_metrics()
```

## Error Handling

### Docker Not Available

```python
try:
    result = execute_python_code_in_sandbox.invoke({"code": "print('test')"})
except Exception as e:
    print(f"Error: {e}")
    # Check if Docker is running
```

### Image Not Found

```bash
# Build the image
cd Agent/sandbox
docker build -t kai_agent_sandbox .
```

### Execution Errors

```python
# Syntax error in code
code = "print('missing quote)"
result = execute_python_code_in_sandbox.invoke({"code": code})
# Output will contain error message
```

## Troubleshooting

### Problem: Docker daemon not running

**Solution**:
- Windows/Mac: Start Docker Desktop
- Linux: `sudo systemctl start docker`

### Problem: Image not found

**Solution**:
```bash
cd Agent/sandbox
docker build -t kai_agent_sandbox .
```

### Problem: Permission denied (Linux)

**Solution**:
```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

### Problem: Timeout

**Solution**:
- Optimize your code
- Break into smaller chunks
- Check for infinite loops

### Problem: Out of memory

**Solution**:
- Reduce memory usage in code
- Process data in chunks
- Use generators instead of lists

## Best Practices

### 1. Keep Code Simple

```python
# Good - simple and fast
code = "print(sum(range(100)))"

# Avoid - complex and slow
code = "print(sum([i**2 for i in range(1000000)]))"
```

### 2. Handle Errors

```python
code = """
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
"""
```

### 3. Use Timeouts Wisely

```python
# For long-running tasks, use terminal commands (120s timeout)
command = "python long_running_script.py"
result = run_terminal_command_in_sandbox.invoke({"command": command})
```

### 4. Clean Up Resources

```python
# The sandbox automatically cleans up containers
# No manual cleanup needed
```

### 5. Monitor Performance

```python
# Check metrics periodically
metrics = get_docker_metrics()
if metrics['total_execution_time'] > 60:
    print("Warning: High execution time")
```

## Advanced Usage

### Custom Timeout

Modify `execution_tools.py`:
```python
PYTHON_TIMEOUT = 60  # Increase to 60 seconds
TERMINAL_TIMEOUT = 300  # Increase to 5 minutes
```

### Enable Network for Python

Modify the tool call:
```python
# In execution_tools.py, change:
network_disabled=False  # Enable network
```

### Add More Packages

Edit `Agent/sandbox/requirements.txt`:
```
pytest>=7.4.0
requests>=2.31.0
numpy>=1.24.0  # Add numpy
pandas>=2.0.0  # Add pandas
```

Then rebuild:
```bash
docker build -t kai_agent_sandbox Agent/sandbox
```

## Integration with Agent

The sandbox tools are automatically available in the agent:

```python
from Agent.agent.agent_core import AgentCore

agent = AgentCore(vector_store=None)

# Agent can use the tools automatically
result = agent.run("Write a Python function to calculate factorial and test it")
```

## Testing

### Unit Tests

```bash
python Agent/test_execution_tools.py
```

### Complete Tests

```bash
python Agent/test_sandbox_complete.py
```

### Verification

```bash
python Agent/verify_docker_build.py
```

## Documentation

- **README.md** - Comprehensive guide
- **SECURITY.md** - Security documentation
- **TASK_4_COMPLETE.md** - Implementation details
- **TROUBLESHOOTING.md** - Common issues

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the documentation
3. Check Docker logs: `docker logs <container_id>`
4. Verify Docker is running: `docker ps`

## Summary

The Docker sandbox provides:
- ✅ Secure code execution
- ✅ Automatic cleanup
- ✅ Network isolation
- ✅ Resource limits
- ✅ Timeout protection
- ✅ Performance monitoring
- ✅ Error handling
- ✅ Easy integration

Use it to safely execute untrusted code in the KAI Agent system!
