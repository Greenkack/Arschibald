# Docker Sandbox for KAI Agent

This directory contains the Docker configuration for the secure code execution sandbox used by the KAI Agent.

## Overview

The sandbox provides a secure, isolated environment for executing Python code and terminal commands with:

- **Unprivileged user**: Runs as `sandboxuser` (not root)
- **Network isolation**: Network disabled by default
- **Resource limits**: Memory and CPU limits enforced
- **Automatic cleanup**: Containers removed after execution
- **Timeout protection**: 30s for Python, 120s for terminal commands

## Building the Image

### Windows (PowerShell)

```powershell
cd Agent\sandbox
.\build.ps1
```

### Linux/Mac

```bash
cd Agent/sandbox
chmod +x build.sh
./build.sh
```

### Manual Build

```bash
docker build -t kai_agent_sandbox .
```

## Testing

After building the image, test it with:

```bash
python Agent/test_execution_tools.py
```

## Dockerfile Structure

```dockerfile
FROM python:3.11-slim          # Base Python image
RUN useradd sandboxuser        # Create unprivileged user
COPY requirements.txt          # Copy dependencies
RUN pip install -r requirements.txt  # Install packages
USER sandboxuser               # Switch to unprivileged user
WORKDIR /app/workspace         # Set working directory
```

## Security Features

1. **Unprivileged Execution**: All code runs as `sandboxuser`, not root
2. **Network Isolation**: Network disabled by default (can be enabled if needed)
3. **Resource Limits**: 512MB memory, 50% CPU quota
4. **No Privilege Escalation**: `no-new-privileges` security option
5. **Automatic Cleanup**: Containers removed after execution
6. **Timeout Protection**: Prevents infinite loops

## Installed Packages

The sandbox includes common Python packages:

- pytest (testing)
- requests (HTTP)
- numpy (numerical computing)
- pandas (data analysis)
- flask (web framework)
- beautifulsoup4 (web scraping)
- lxml (XML/HTML parsing)

## Adding Packages

To add more packages to the sandbox:

1. Edit `requirements.txt`
2. Rebuild the image: `docker build -t kai_agent_sandbox .`

## Troubleshooting

### Docker not found

Make sure Docker Desktop is installed and running:

- Windows: <https://docs.docker.com/desktop/install/windows-install/>
- Mac: <https://docs.docker.com/desktop/install/mac-install/>
- Linux: <https://docs.docker.com/engine/install/>

### Permission denied

On Linux, you may need to add your user to the docker group:

```bash
sudo usermod -aG docker $USER
```

Then log out and log back in.

### Image build fails

Check that you're in the correct directory:

```bash
cd Agent/sandbox
ls  # Should show Dockerfile and requirements.txt
```

### Container timeout

If code takes too long:

- Python code: 30 second timeout
- Terminal commands: 120 second timeout

Optimize your code or increase timeouts in `execution_tools.py`.

## Usage Examples

### Execute Python Code

```python
from Agent.tools.execution_tools import execute_python_code_in_sandbox

code = "print('Hello from sandbox!')"
result = execute_python_code_in_sandbox.invoke({"code": code})
print(result)
```

### Run Terminal Command

```python
from Agent.tools.execution_tools import run_terminal_command_in_sandbox

command = "pip list"
result = run_terminal_command_in_sandbox.invoke({"command": command})
print(result)
```

### Execute with Network Access

```python
from Agent.tools.execution_tools import execute_python_code_with_network

code = """
import requests
response = requests.get('https://api.github.com')
print(response.status_code)
"""
result = execute_python_code_with_network.invoke({"code": code})
print(result)
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Agent Core                      │
│  (execution_tools.py)                   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│         Docker Engine                   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│    Isolated Container                   │
│  ┌─────────────────────────────────┐   │
│  │  sandboxuser (unprivileged)     │   │
│  │  /app/workspace                 │   │
│  │  - Python 3.11                  │   │
│  │  - Installed packages           │   │
│  │  - No network (default)         │   │
│  │  - Resource limits              │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Security Considerations

⚠️ **Important**: While the sandbox provides multiple layers of security, it's not a replacement for proper security practices:

- Always validate user input before execution
- Monitor resource usage
- Keep Docker and base images updated
- Review code before execution when possible
- Use network isolation unless explicitly needed

## License

Part of the KAI Agent system.
