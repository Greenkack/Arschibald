# Docker Sandbox Quick Start Guide

## Prerequisites

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker ps`

## Build the Sandbox (One-Time Setup)

### Option 1: Python Script (Recommended)

```bash
python Agent/build_sandbox.py
```

### Option 2: Platform-Specific Scripts

**Windows (PowerShell):**
```powershell
cd Agent\sandbox
.\build.ps1
```

**Linux/Mac (Bash):**
```bash
cd Agent/sandbox
chmod +x build.sh
./build.sh
```

### Option 3: Manual Build

```bash
cd Agent/sandbox
docker build -t kai_agent_sandbox .
```

## Verify the Build

```bash
python Agent/verify_docker_build.py
```

Expected output:
```
✓ Docker Available
✓ Image Exists
✓ Python Version
✓ Unprivileged User
✓ Workspace Directory
✓ Installed Packages
✓ Security Features
✓ Basic Execution
```

## Test the Sandbox

### Quick Test

```bash
python Agent/test_execution_tools.py
```

### Comprehensive Test

```bash
python Agent/test_sandbox_complete.py
```

## Usage Examples

### Execute Python Code

```python
from agent.tools.execution_tools import execute_python_code_in_sandbox

code = """
print('Hello from sandbox!')
x = 10 + 20
print(f'Result: {x}')
"""

result = execute_python_code_in_sandbox.invoke({"code": code})
print(result)
# Output: Hello from sandbox!
#         Result: 30
```

### Run Terminal Commands

```python
from agent.tools.execution_tools import run_terminal_command_in_sandbox

command = "pip list"
result = run_terminal_command_in_sandbox.invoke({"command": command})
print(result)
# Output: (list of installed packages)
```

### Execute with Network Access

```python
from agent.tools.execution_tools import execute_python_code_with_network

code = """
import requests
response = requests.get('https://api.github.com')
print(f'Status: {response.status_code}')
"""

result = execute_python_code_with_network.invoke({"code": code})
print(result)
# Output: Status: 200
```

## Security Features

- ✓ Runs as unprivileged user (sandboxuser)
- ✓ Network isolated by default
- ✓ Cannot access host files
- ✓ Cannot escalate privileges
- ✓ Automatic cleanup after execution
- ✓ Timeout protection (30s Python, 120s terminal)
- ✓ Resource limits (512MB memory, 50% CPU)

## Troubleshooting

### Docker not running
```bash
# Windows/Mac: Start Docker Desktop
# Linux: sudo systemctl start docker
```

### Image not found
```bash
python Agent/build_sandbox.py
```

### Permission denied (Linux)
```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

### Container timeout
- Optimize code to run faster
- Or modify timeout in `agent/tools/execution_tools.py`

## File Locations

- **Dockerfile**: `Agent/sandbox/Dockerfile`
- **Requirements**: `Agent/sandbox/requirements.txt`
- **Build Scripts**: `Agent/sandbox/build.sh`, `Agent/sandbox/build.ps1`
- **Tests**: `Agent/test_sandbox_complete.py`
- **Verification**: `Agent/verify_docker_build.py`

## Next Steps

1. Build the image (if not done)
2. Verify the build
3. Run tests
4. Use in agent tasks

## Support

For more details, see:
- `Agent/sandbox/README.md` - Full documentation
- `Agent/TASK_14_DOCKER_SANDBOX_COMPLETE.md` - Implementation details
- `Agent/TROUBLESHOOTING.md` - Troubleshooting guide
