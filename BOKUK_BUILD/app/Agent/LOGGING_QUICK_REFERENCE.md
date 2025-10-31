# KAI Agent Logging System - Quick Reference

## Overview

The KAI Agent includes a comprehensive logging system that tracks all operations while automatically protecting sensitive data.

## Quick Start

```python
from agent.logging_config import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Detailed debugging information")
logger.info("General information about operations")
logger.warning("Warning about potential issues")
logger.error("Error occurred", exc_info=True)  # Include stack trace
logger.critical("Critical system failure")
```

## Specialized Logging Functions

### API Call Logging

```python
from agent.logging_config import log_api_call

log_api_call(
    logger,
    api_name="OpenAI",
    endpoint="/v1/chat/completions",
    method="POST",
    status_code=200,
    duration=1.23
)
```

### Docker Operation Logging

```python
from agent.logging_config import log_docker_operation

log_docker_operation(
    logger,
    operation="execute",
    image_name="kai_agent_sandbox",
    container_id="abc123",
    success=True,
    duration=2.5
)
```

### Tool Execution Logging

```python
from agent.logging_config import log_tool_execution

log_tool_execution(
    logger,
    tool_name="write_file",
    input_summary="path=test.py, size=1234",
    success=True,
    duration=0.05
)
```

### Agent Reasoning Logging

```python
from agent.logging_config import log_agent_reasoning

log_agent_reasoning(
    logger,
    step=1,
    thought="I need to search the knowledge base",
    action="knowledge_base_search",
    observation="Found 3 relevant documents"
)
```

## Log Levels

| Level | When to Use |
|-------|-------------|
| DEBUG | Detailed information for diagnosing problems |
| INFO | General informational messages |
| WARNING | Warning messages for potentially harmful situations |
| ERROR | Error messages for serious problems |
| CRITICAL | Critical messages for very serious errors |

## Log Files

Logs are stored in `Agent/logs/`:

- `agent_YYYYMMDD.log` - All log messages
- `agent_errors_YYYYMMDD.log` - Only ERROR and CRITICAL messages

**Features**:
- Automatic daily rotation
- 10MB max file size
- 5 backup files kept
- UTF-8 encoding

## Sensitive Data Protection

The logging system automatically redacts:

- ✅ API keys (OpenAI, Tavily, ElevenLabs)
- ✅ Tokens and bearer tokens
- ✅ Passwords
- ✅ Phone numbers
- ✅ Email addresses (partial)
- ✅ Account SIDs
- ✅ Auth tokens

**Example**:
```python
logger.info("API key: sk-1234567890abcdef")
# Logged as: "API key: [REDACTED_API_KEY]"
```

## Configuration

### Default Configuration

The logging system works out of the box with sensible defaults:
- Level: INFO
- Console: Enabled (with colors)
- File: Enabled (with rotation)

### Custom Configuration

```python
from agent.logging_config import setup_logging

logger = setup_logging(
    level="DEBUG",              # Log level
    log_to_file=True,          # Enable file logging
    log_to_console=True,       # Enable console logging
    log_file_name="custom.log" # Custom log file name
)
```

## Best Practices

### 1. Use Appropriate Log Levels

```python
# Good
logger.debug(f"Processing item {i} of {total}")
logger.info("Task completed successfully")
logger.warning("API rate limit approaching")
logger.error("Failed to connect to database", exc_info=True)

# Avoid
logger.info("x = 5")  # Too verbose for INFO
logger.error("Task completed")  # Wrong level
```

### 2. Include Context

```python
# Good
logger.info(f"File written: {path} ({size} bytes) in {duration:.2f}s")

# Less helpful
logger.info("File written")
```

### 3. Use exc_info for Exceptions

```python
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
```

### 4. Don't Log Sensitive Data Directly

```python
# Good - sensitive data is automatically redacted
logger.info(f"API call with key: {api_key}")

# Even better - don't include it at all
logger.info("API call completed successfully")
```

### 5. Use Specialized Logging Functions

```python
# Good - structured logging
log_api_call(logger, api_name="OpenAI", status_code=200, duration=1.5)

# Less structured
logger.info(f"OpenAI API call: 200, 1.5s")
```

## Common Patterns

### Function Entry/Exit

```python
def my_function(arg1, arg2):
    logger.info(f"Starting my_function with arg1={arg1}, arg2={arg2}")
    try:
        result = do_work()
        logger.info("my_function completed successfully")
        return result
    except Exception as e:
        logger.error(f"my_function failed: {e}", exc_info=True)
        raise
```

### Performance Tracking

```python
import time

start_time = time.time()
result = expensive_operation()
duration = time.time() - start_time

logger.info(f"Operation completed in {duration:.2f}s")
```

### Conditional Logging

```python
if logger.isEnabledFor(logging.DEBUG):
    # Only compute expensive debug info if DEBUG is enabled
    debug_info = compute_expensive_debug_info()
    logger.debug(f"Debug info: {debug_info}")
```

## Troubleshooting

### Logs Not Appearing

1. Check log level: `setup_logging(level="DEBUG")`
2. Check if console/file logging is enabled
3. Check file permissions for `Agent/logs/` directory

### Too Many Logs

1. Increase log level: `setup_logging(level="WARNING")`
2. Disable console logging: `setup_logging(log_to_console=False)`
3. Adjust log rotation settings

### Sensitive Data in Logs

The filter should catch most patterns, but if you find sensitive data:
1. Report it as a security issue
2. Add pattern to `SensitiveDataFilter.PATTERNS` in `logging_config.py`

## Testing

Run the comprehensive test suite:

```bash
python Agent/test_logging_system.py
```

This tests:
- ✅ All log levels
- ✅ Sensitive data filtering
- ✅ API call logging
- ✅ Docker operation logging
- ✅ Tool execution logging
- ✅ Agent reasoning logging
- ✅ Error logging with stack traces
- ✅ Log file creation

## Examples from Real Code

### From agent_core.py

```python
logger.info(f"Starting agent task: {user_input[:100]}...")
logger.info("Invoking agent executor...")
logger.info(f"Agent task completed successfully in {execution_time:.2f}s")
```

### From execution_tools.py

```python
log_docker_operation(
    logger,
    operation="create",
    image_name=image,
    container_id=container_id,
    success=True
)
```

### From knowledge_tools.py

```python
logger.info(f"Found {len(pdf_files)} PDF files in {path}")
logger.info(f"Loaded {len(documents)} pages from {len(pdf_files)} PDFs")
logger.info(f"Created {len(chunks)} text chunks")
```

## Summary

The logging system provides:
- 📊 Comprehensive visibility into agent operations
- 🔒 Automatic sensitive data protection
- 📁 Organized log files with rotation
- 🎨 Color-coded console output
- ⚡ Minimal performance impact
- 🛠️ Easy to use and configure

For more details, see:
- `Agent/agent/logging_config.py` - Implementation
- `Agent/test_logging_system.py` - Test suite
- `.kiro/specs/agent-integration/TASK_11_3_LOGGING_IMPLEMENTATION_SUMMARY.md` - Full documentation
