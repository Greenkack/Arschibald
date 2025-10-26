# Security Quick Reference Guide

## Quick Start

### 1. Validate Your Setup

```bash
python Agent/validate_config.py
```

### 2. Run Security Tests

```bash
python Agent/run_security_tests.py
```

### 3. Check Configuration

```bash
python -c "from Agent.config import check_api_keys; print(check_api_keys())"
```

## Common Security Functions

### Path Validation

```python
from Agent.agent.security import sanitize_file_path, PathTraversalError

try:
    safe_path = sanitize_file_path(user_path, base_dir)
    # Use safe_path
except PathTraversalError as e:
    print(f"Security error: {e}")
```

### Command Validation

```python
from Agent.agent.security import sanitize_command, CommandInjectionError

try:
    safe_cmd = sanitize_command(user_command)
    # Execute safe_cmd
except CommandInjectionError as e:
    print(f"Security error: {e}")
```

### Input Validation

```python
from Agent.agent.security import sanitize_user_input, InputValidationError

try:
    safe_input = sanitize_user_input(user_input, max_length=10000)
    # Process safe_input
except InputValidationError as e:
    print(f"Security error: {e}")
```

### Mask Sensitive Data

```python
from Agent.agent.security import mask_sensitive_data

# Before logging
log_message = mask_sensitive_data(f"API key: {api_key}")
logger.info(log_message)
```

## Security Checklist

### Before Committing Code

- [ ] No hardcoded API keys
- [ ] All user input validated
- [ ] Sensitive data masked in logs
- [ ] Error messages don't expose secrets
- [ ] Tests pass

### Before Deployment

- [ ] `.env` file configured
- [ ] `.env` in `.gitignore`
- [ ] Docker image built
- [ ] Security tests pass
- [ ] Configuration validated

### During Development

- [ ] Use security functions for all input
- [ ] Never log API keys
- [ ] Validate file paths
- [ ] Sanitize commands
- [ ] Handle errors securely

## Common Patterns

### Safe File Operations

```python
from Agent.agent.tools.coding_tools import write_file, read_file

# These tools automatically validate paths
result = write_file.invoke({"path": "myfile.txt", "content": "data"})
content = read_file.invoke({"path": "myfile.txt"})
```

### Safe Command Execution

```python
from Agent.tools.execution_tools import run_terminal_command_in_sandbox

# This tool automatically validates commands
result = run_terminal_command_in_sandbox.invoke({"command": "echo hello"})
```

### Safe API Key Usage

```python
from Agent.config import AgentConfig

# Load configuration securely
config = AgentConfig.from_env()

# Keys are never logged
# Use config.openai_api_key, etc.
```

## Security Violations to Avoid

### ❌ DON'T

```python
# Don't hardcode API keys
api_key = "sk-1234567890..."

# Don't log sensitive data
logger.info(f"API key: {api_key}")

# Don't skip validation
os.system(user_command)  # Dangerous!

# Don't allow path traversal
open(user_path, 'r')  # Dangerous!
```

### ✅ DO

```python
# Load from environment
api_key = os.getenv("OPENAI_API_KEY")

# Mask before logging
logger.info(f"API key: {mask_sensitive_data(api_key)}")

# Validate commands
safe_cmd = sanitize_command(user_command)
run_terminal_command_in_sandbox.invoke({"command": safe_cmd})

# Validate paths
safe_path = sanitize_file_path(user_path, base_dir)
with open(safe_path, 'r') as f:
    content = f.read()
```

## Docker Security

### Build Secure Image

```bash
cd Agent/sandbox
docker build -t kai_agent_sandbox .
```

### Verify Security

```bash
# Check user
docker run --rm kai_agent_sandbox whoami
# Should output: sandboxuser

# Check network isolation
docker run --rm --network none kai_agent_sandbox ping -c 1 google.com
# Should fail
```

### Resource Limits

```python
# Automatically applied:
# - Memory: 512 MB
# - CPU: 50% of one core
# - Processes: 100 max
# - Timeout: 30s (Python) / 120s (terminal)
```

## Troubleshooting

### "Path traversal detected"

- User tried to access files outside workspace
- This is blocked for security
- Ensure paths are relative to workspace

### "Dangerous command pattern detected"

- Command contains dangerous patterns
- Review command for security issues
- Use safer alternatives

### "API key not found"

- Check `.env` file exists
- Verify key is on correct line
- Restart application

### "Docker not running"

- Start Docker Desktop (Windows/Mac)
- Or: `sudo systemctl start docker` (Linux)

## Resources

- **Full Documentation**: `Agent/sandbox/SECURITY.md`
- **Security Checklist**: `Agent/SECURITY_CHECKLIST.md`
- **Validation Script**: `Agent/validate_config.py`
- **Security Tests**: `Agent/test_security.py`
- **Security Module**: `Agent/agent/security.py`

## Emergency Contacts

If you discover a security vulnerability:

1. **Do not** create a public issue
2. Contact maintainers privately
3. Provide detailed reproduction steps
4. Wait for confirmation before disclosure

## Quick Commands

```bash
# Validate everything
python Agent/validate_config.py

# Run security tests
python Agent/run_security_tests.py

# Check API keys (masked)
python -c "from Agent.config import check_api_keys; print(check_api_keys())"

# Test path validation
python -c "from Agent.agent.security import validate_path; print(validate_path('../etc/passwd', '/app'))"

# Test command validation
python -c "from Agent.agent.security import validate_command; print(validate_command('rm -rf /'))"

# Mask sensitive data
python -c "from Agent.agent.security import mask_sensitive_data; print(mask_sensitive_data('sk-1234567890...'))"
```

---

**Remember**: Security is everyone's responsibility. When in doubt, ask!
