# Execution Tools Quick Start Guide

## Overview

The KAI Agent execution tools provide secure code execution in isolated Docker containers. This guide will get you started quickly.

## Prerequisites

1. **Docker installed and running**
   - Windows/Mac: Docker Desktop
   - Linux: Docker Engine

2. **Docker image built**

   ```bash
   cd Agent
   python build_sandbox.py
   ```

## Basic Usage

### 1. Execute Python Code

```python
from agent.tools.execution_tools import execute_python_code_in_sandbox

# Simple example
code = "print('Hello, World!')"
result = execute_python_code_in_sandbox.invoke({"code": code})
print(result)
```

**Output**:

```
--- STDOUT ---
Hello, World!
```

### 2. Run Terminal Commands

```python
from agent.tools.execution_tools import run_terminal_command_in_sandbox

# Check Python version
command = "python --version"
result = run_terminal_command_in_sandbox.invoke({"command": command})
print(result)
```

**Output**:

```
--- STDOUT ---
Python 3.11.x
```

## Common Use Cases

### Install and Use a Package

```python
command = """
pip install requests && python -c '
import requests
response = requests.get("https://api.github.com")
print(f"Status: {response.status_code}")
'
"""
result = run_terminal_command_in_sandbox.invoke({"command": command})
```

### Run Tests

```python
# Assuming test file exists in workspace
command = "pytest test_file.py -v"
result = run_terminal_command_in_sandbox.invoke({"command": command})
```

### Data Processing

```python
code = """
import json

data = {'name': 'John', 'age': 30}
print(json.dumps(data, indent=2))
"""
result = execute_python_code_in_sandbox.invoke({"code": code})
```

### File Operations

```python
command = """
echo 'Hello' > test.txt
cat test.txt
ls -la
"""
result = run_terminal_command_in_sandbox.invoke({"command": command})
```

## Security Features

### Python Execution

- ✓ Network **disabled**
- ✓ 30-second timeout
- ✓ Unprivileged user
- ✓ 512MB RAM limit
- ✓ Auto cleanup

### Terminal Execution

- ✓ Network **enabled** (for pip)
- ✓ 120-second timeout
- ✓ Unprivileged user
- ✓ 512MB RAM limit
- ✓ Auto cleanup

## Error Handling

### Syntax Errors

```python
code = "print(undefined_variable)"
result = execute_python_code_in_sandbox.invoke({"code": code})
# Result contains NameError in stderr
```

### Timeout

```python
code = """
import time
time.sleep(35)  # Exceeds 30s timeout
"""
result = execute_python_code_in_sandbox.invoke({"code": code})
# Result: "Execution timed out after 30 seconds..."
```

### Docker Image Missing

```python
result = execute_python_code_in_sandbox.invoke({"code": "print('test')"})
# Result: "Docker image 'kai_agent_sandbox' not found..."
# Includes build instructions
```

## Testing

Run the test suite to verify everything works:

```bash
cd Agent
python test_execution_tools.py
```

Expected: All 9 tests pass

## Troubleshooting

### "Docker is not available"

**Solution**: Start Docker Desktop or Docker Engine

### "Docker image not found"

**Solution**: Build the image

```bash
cd Agent
python build_sandbox.py
```

### "Permission denied"

**Linux Solution**: Add user to docker group

```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### "Execution timed out"

**Solution**: Optimize code or increase timeout in `execution_tools.py`

## Advanced Usage

### Custom Timeout

Modify `Agent/agent/tools/execution_tools.py`:

```python
PYTHON_TIMEOUT = 60    # Increase to 60 seconds
TERMINAL_TIMEOUT = 300 # Increase to 5 minutes
```

### Add Packages to Sandbox

Edit `Agent/sandbox/requirements.txt`:

```txt
numpy>=1.24.0
pandas>=2.0.0
```

Then rebuild:

```bash
cd Agent
python build_sandbox.py
```

### Check Container Logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now execution tools will show detailed logs
result = execute_python_code_in_sandbox.invoke({"code": "print('test')"})
```

## Integration with Agent

The execution tools are designed to work with LangChain agents:

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from agent.tools.execution_tools import (
    execute_python_code_in_sandbox,
    run_terminal_command_in_sandbox
)

tools = [
    execute_python_code_in_sandbox,
    run_terminal_command_in_sandbox,
    # ... other tools
]

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)
```

## Best Practices

1. **Validate input**: Sanitize code before execution
2. **Use Python for calculations**: Network disabled, more secure
3. **Use terminal for packages**: Network enabled for pip
4. **Handle errors**: Check result for error messages
5. **Monitor resources**: Watch for timeout issues
6. **Keep Docker updated**: Security patches

## Performance Tips

1. **Minimize container creation**: Each execution creates new container (~1-2s overhead)
2. **Batch operations**: Combine multiple commands when possible
3. **Use efficient code**: Optimize for speed
4. **Cache results**: Don't re-execute same code

## Examples Repository

More examples in `Agent/test_execution_tools.py`:

- Simple Python execution
- Calculations
- Terminal commands
- Error handling
- Network isolation
- Timeout handling
- Package installation

## Support

- **Documentation**: See `Agent/sandbox/README.md`
- **Security**: See `Agent/sandbox/SECURITY.md`
- **Tests**: Run `python test_execution_tools.py`
- **Issues**: Check logs for detailed error messages

## Quick Reference

| Feature | Python | Terminal |
|---------|--------|----------|
| Network | Disabled | Enabled |
| Timeout | 30s | 120s |
| User | sandboxuser | sandboxuser |
| RAM | 512MB | 512MB |
| CPU | 50% | 50% |
| Cleanup | Auto | Auto |

## Next Steps

1. Build the Docker image
2. Run the test suite
3. Try the examples above
4. Integrate with your agent
5. Read the full documentation

Happy coding! 🚀
