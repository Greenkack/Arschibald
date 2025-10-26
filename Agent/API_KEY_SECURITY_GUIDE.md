# API Key Security Guide

## Overview

This guide explains how the KAI Agent securely manages API keys and sensitive credentials.

**Requirements Implemented**: 12.1, 12.2, 12.3, 12.5

## Security Principles

### 1. Load Keys from .env Only ✅

**Rule**: API keys MUST be loaded from the `.env` file. Never hardcode keys in source code.

**Implementation**:

```python
# ✅ CORRECT - Load from .env
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ❌ WRONG - Hardcoded key
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
```

**Files**:

- `Agent/config.py` - Configuration management
- `.env` - API keys (NOT committed to git)
- `.env.example` - Template (safe to commit)

### 2. Never Log or Display Keys ✅

**Rule**: API keys MUST NEVER appear in logs, console output, or UI.

**Implementation**:

```python
# ✅ CORRECT - Mask sensitive data
from Agent.agent.security import mask_sensitive_data
print(f"API key: {mask_sensitive_data(api_key)}")
# Output: "API key: sk-***"

# ✅ CORRECT - Don't log keys at all
logger.info("API key configured")  # No key value

# ❌ WRONG - Logging the key
logger.info(f"Using API key: {api_key}")
print(f"API key: {api_key}")
```

**Protection Layers**:

1. **SensitiveDataFilter** - Automatically redacts keys from logs
2. **mask_sensitive_data()** - Masks keys in output
3. **Code review** - Manual checks for key exposure

**Files**:

- `Agent/agent/logging_config.py` - Sensitive data filter
- `Agent/agent/security.py` - Masking functions

### 3. Add .env to .gitignore ✅

**Rule**: The `.env` file MUST be in `.gitignore` to prevent committing secrets.

**Verification**:

```bash
# Check if .env is in .gitignore
grep "^\.env$" .gitignore

# If not found, add it
echo ".env" >> .gitignore
```

**Status**: ✅ `.env` is already in `.gitignore` at line 14

### 4. Validate Keys on Startup ✅

**Rule**: API keys MUST be validated on startup to catch configuration errors early.

**Implementation**:

```python
from Agent.config import validate_startup_security

# Validate on startup
is_valid, issues = validate_startup_security()
if not is_valid:
    for issue in issues:
        print(issue)
    sys.exit(1)
```

**Validations Performed**:

- ✅ .env file exists
- ✅ .env is in .gitignore
- ✅ OPENAI_API_KEY is present (required)
- ✅ API key formats are correct
- ✅ File permissions are secure (Unix)

**Files**:

- `Agent/config.py` - Validation functions
- `Agent/validate_config.py` - Startup validation script
- `Agent/audit_api_key_security.py` - Comprehensive audit

## Security Features

### Automatic Key Masking

The logging system automatically masks sensitive data:

```python
# Input
logger.info("API key: sk-1234567890abcdefghijklmnopqrstuvwxyz")

# Output (automatically masked)
"API key: [REDACTED_API_KEY]"
```

**Patterns Masked**:

- OpenAI keys: `sk-...` → `[REDACTED_API_KEY]`
- Tavily keys: `tvly-...` → `[REDACTED_API_KEY]`
- Tokens: `bearer ...` → `bearer [REDACTED]`
- Passwords: `password=...` → `password=[REDACTED]`
- Phone numbers: `+1-555-...` → `[REDACTED_PHONE]`

### Path Validation

File operations are restricted to the workspace:

```python
from Agent.agent.security import sanitize_file_path

# ✅ CORRECT - Within workspace
path = sanitize_file_path("myfile.txt", "agent_workspace")

# ❌ BLOCKED - Path traversal attempt
path = sanitize_file_path("../../../etc/passwd", "agent_workspace")
# Raises: PathTraversalError
```

### Command Validation

Dangerous commands are blocked:

```python
from Agent.agent.security import sanitize_command

# ✅ CORRECT - Safe command
cmd = sanitize_command("echo hello")

# ❌ BLOCKED - Dangerous command
cmd = sanitize_command("rm -rf / && echo done")
# Raises: CommandInjectionError
```

## Security Audit

Run the comprehensive security audit:

```bash
cd Agent
python audit_api_key_security.py
```

**Audits Performed**:

1. ✅ .env in .gitignore
2. ✅ .env file security
3. ✅ No hardcoded keys
4. ✅ No key logging/display
5. ✅ Valid key formats
6. ✅ Logging sensitive data filter

## Configuration Validation

Validate your configuration:

```bash
cd Agent
python validate_config.py
```

**Checks**:

- Environment file exists
- API keys are configured
- Docker is available
- Docker image is built
- File permissions are secure

## Best Practices

### DO ✅

1. **Load keys from .env**

   ```python
   load_dotenv()
   api_key = os.getenv("OPENAI_API_KEY")
   ```

2. **Mask keys in output**

   ```python
   print(f"Key: {api_key[:4]}***")
   ```

3. **Validate on startup**

   ```python
   validate_startup_security()
   ```

4. **Use security functions**

   ```python
   from Agent.agent.security import sanitize_file_path, sanitize_command
   ```

5. **Check .gitignore**

   ```bash
   grep "^\.env$" .gitignore
   ```

### DON'T ❌

1. **Never hardcode keys**

   ```python
   # ❌ WRONG
   api_key = "sk-1234567890..."
   ```

2. **Never log keys**

   ```python
   # ❌ WRONG
   logger.info(f"API key: {api_key}")
   print(f"Token: {token}")
   ```

3. **Never commit .env**

   ```bash
   # ❌ WRONG
   git add .env
   git commit -m "Add config"
   ```

4. **Never display keys in UI**

   ```python
   # ❌ WRONG
   st.write(f"Your API key: {api_key}")
   ```

5. **Never share keys**
   - Don't paste keys in chat/email
   - Don't share screenshots with keys
   - Don't commit keys to GitHub

## File Permissions (Unix/Linux/Mac)

Secure your .env file:

```bash
# Make .env readable only by owner
chmod 600 .env

# Verify permissions
ls -la .env
# Should show: -rw------- (owner read/write only)
```

## Emergency Response

### If API Key is Exposed

1. **Immediately revoke the key**
   - OpenAI: <https://platform.openai.com/api-keys>
   - Tavily: <https://tavily.com/>
   - Twilio: <https://www.twilio.com/console>
   - ElevenLabs: <https://elevenlabs.io/>

2. **Generate new key**

3. **Update .env file**

4. **Check git history**

   ```bash
   # Search for exposed keys
   git log -p | grep "sk-"
   ```

5. **If committed to git**

   ```bash
   # Remove from history (use with caution)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

### If .env is Committed

1. **Remove from git**

   ```bash
   git rm --cached .env
   git commit -m "Remove .env from version control"
   ```

2. **Add to .gitignore**

   ```bash
   echo ".env" >> .gitignore
   git add .gitignore
   git commit -m "Add .env to .gitignore"
   ```

3. **Revoke all keys in the file**

4. **Generate new keys**

## Testing Security

### Unit Tests

```bash
cd Agent
python test_security.py
```

Tests:

- Path validation
- Command validation
- Filename validation
- Sensitive data masking

### Integration Tests

```bash
cd Agent
python run_security_tests.py
```

Tests:

- Complete security workflow
- Input validation
- Docker security
- API key management

### Manual Testing

1. **Check .gitignore**

   ```bash
   grep "^\.env$" .gitignore
   ```

2. **Run audit**

   ```bash
   python audit_api_key_security.py
   ```

3. **Validate config**

   ```bash
   python validate_config.py
   ```

4. **Check logs for keys**

   ```bash
   grep -r "sk-" logs/
   # Should find nothing or only masked keys
   ```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Security Layers                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Configuration Layer (config.py)                     │
│     - Load from .env only                               │
│     - Validate on startup                               │
│     - Check .gitignore                                  │
│                                                          │
│  2. Logging Layer (logging_config.py)                   │
│     - SensitiveDataFilter                               │
│     - Automatic key redaction                           │
│     - Separate error logs                               │
│                                                          │
│  3. Security Layer (security.py)                        │
│     - Path validation                                   │
│     - Command validation                                │
│     - Input sanitization                                │
│     - Data masking                                      │
│                                                          │
│  4. Validation Layer (validate_config.py)               │
│     - Startup checks                                    │
│     - Format validation                                 │
│     - Permission checks                                 │
│                                                          │
│  5. Audit Layer (audit_api_key_security.py)            │
│     - Comprehensive security audit                      │
│     - Codebase scanning                                 │
│     - Best practices verification                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Summary

✅ **Task 12.3 Complete**: Secure API key management

**Implemented**:

1. ✅ Load keys from .env only
2. ✅ Never log or display keys
3. ✅ Add .env to .gitignore (already present)
4. ✅ Validate keys on startup
5. ✅ Comprehensive security audit
6. ✅ Automatic key masking
7. ✅ Path and command validation
8. ✅ Security testing

**Files Created/Modified**:

- `Agent/config.py` - Enhanced with security validation
- `Agent/validate_config.py` - Updated to use new functions
- `Agent/audit_api_key_security.py` - Comprehensive audit script
- `Agent/test_search_tools.py` - Fixed key display
- `Agent/API_KEY_SECURITY_GUIDE.md` - This guide

**Requirements Met**: 12.1, 12.2, 12.3, 12.5
