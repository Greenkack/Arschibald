# Agent Core Quick Start Guide

## Overview

The AgentCore is the heart of the KAI Agent system, implementing an autonomous AI expert with dual expertise in renewable energy consulting and software architecture.

## Basic Usage

### 1. Initialize the Agent

```python
from Agent.agent.agent_core import AgentCore
from Agent.agent.tools.knowledge_tools import setup_knowledge_base

# Set up knowledge base
vector_store = setup_knowledge_base()

# Initialize agent
agent = AgentCore(vector_store)
```

### 2. Run a Task

```python
# Simple task
result = agent.run("List all files in the workspace")

# Check result
if result['success']:
    print(result['output'])
    print(f"Completed in {result['execution_time']:.2f}s")
else:
    print(f"Error: {result['error']}")
    print(f"Solution: {result['solution']}")
```

### 3. Advanced Configuration

```python
# Custom configuration
agent = AgentCore(
    vector_store=vector_store,
    model="gpt-4o",           # OpenAI model
    temperature=0.7,          # Creativity (0.0-1.0)
    max_retries=2,            # Retry attempts
    verbose=True              # Show reasoning
)
```

## Result Structure

Every `agent.run()` call returns a dictionary:

```python
{
    'success': bool,              # True if task completed
    'output': str,                # Agent's final response
    'intermediate_steps': list,   # Reasoning trace (ReAct steps)
    'error': Optional[str],       # Error message if failed
    'solution': Optional[str],    # Suggested solution if failed
    'execution_time': float       # Time taken in seconds
}
```

## Available Tools

The agent has access to 11 tools across 5 categories:

### File System Tools

- `write_file(path, content)` - Write file to workspace
- `read_file(path)` - Read file from workspace
- `list_files(path)` - List directory contents
- `generate_project_structure(name, type, features)` - Generate project scaffold

### Code Execution Tools

- `execute_python_code_in_sandbox(code)` - Run Python code safely
- `run_terminal_command_in_sandbox(command)` - Execute shell commands

### Testing Tools

- `execute_pytest_in_sandbox()` - Run pytest in sandbox

### Search Tools

- `knowledge_base_search(query)` - Search internal knowledge base
- `tavily_search(query)` - Search the web

### Telephony Tools

- `start_interactive_call(phone, opening, goal)` - Make outbound call
- `update_call_summary(info)` - Add to call transcript

## Example Tasks

### Software Development

```python
# Generate a project
result = agent.run("""
Create a Flask REST API project with the following features:
- User authentication
- Database integration
- API documentation
Follow TDD principles and include tests.
""")
```

### Renewable Energy Consulting

```python
# Research and call
result = agent.run("""
Research the benefits of photovoltaic systems for residential customers.
Then prepare a sales call script highlighting the top 3 advantages.
""")
```

### Code Execution

```python
# Write and test code
result = agent.run("""
Write a Python function that calculates the ROI for a solar installation.
Include unit tests and run them to verify correctness.
""")
```

## Memory Management

### Clear Conversation History

```python
# Start fresh conversation
agent.clear_memory()
```

### Get Conversation History

```python
# Retrieve message history
history = agent.get_conversation_history()
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

## Status and Monitoring

### Get Agent Status

```python
status = agent.get_status()
print(f"Model: {status['model']}")
print(f"Tools: {status['tool_count']}")
print(f"Memory messages: {status['memory_messages']}")
```

### Get Available Tools

```python
tools = agent.get_tool_names()
print(f"Available tools: {', '.join(tools)}")
```

## Error Handling

The agent automatically handles errors and retries when appropriate:

### Configuration Errors

- **No retry** - Fail immediately with solution
- Example: Missing API key

```python
try:
    agent = AgentCore(vector_store)
except ConfigurationError as e:
    print(f"Setup error: {e.message}")
    print(f"Solution: {e.solution}")
```

### Execution Errors

- **Automatic retry** - Up to 2 attempts with exponential backoff
- Example: Docker container failure, code syntax error

### API Errors

- **Automatic retry** - For rate limits and server errors
- Example: OpenAI rate limit, network timeout

## Best Practices

### 1. Always Check Results

```python
result = agent.run(task)
if not result['success']:
    print(f"Task failed: {result['error']}")
    if result['solution']:
        print(f"Try: {result['solution']}")
```

### 2. Use Verbose Mode for Debugging

```python
# See agent's reasoning process
agent = AgentCore(vector_store, verbose=True)
```

### 3. Clear Memory Between Unrelated Tasks

```python
agent.run("Task 1")
agent.clear_memory()  # Start fresh
agent.run("Task 2")
```

### 4. Monitor Execution Time

```python
result = agent.run(task)
if result['execution_time'] > 60:
    print("⚠️ Task took over 1 minute")
```

### 5. Review Intermediate Steps

```python
result = agent.run(task)
for i, (action, observation) in enumerate(result['intermediate_steps']):
    print(f"Step {i+1}: {action.tool}")
```

## Configuration Requirements

### Required Environment Variables

```bash
# .env file
OPENAI_API_KEY=sk-...           # Required
TAVILY_API_KEY=tvly-...         # Optional (for web search)
ELEVEN_LABS_API_KEY=...         # Optional (for telephony)
TWILIO_ACCOUNT_SID=AC...        # Optional (for telephony)
TWILIO_AUTH_TOKEN=...           # Optional (for telephony)
TWILIO_PHONE_NUMBER=+1...       # Optional (for telephony)
```

### Docker Requirements

For code execution tools, Docker must be installed and running:

```bash
# Build sandbox image
cd Agent/sandbox
docker build -t kai_agent_sandbox .
```

## Troubleshooting

### Agent Won't Initialize

**Problem:** `ConfigurationError: OpenAI API key not configured`

**Solution:** Set `OPENAI_API_KEY` in your `.env` file

### Code Execution Fails

**Problem:** `DockerError: Image 'kai_agent_sandbox' not found`

**Solution:** Build the Docker image:

```bash
cd Agent/sandbox
docker build -t kai_agent_sandbox .
```

### Task Times Out

**Problem:** Task exceeds 5 minute limit

**Solution:** Break task into smaller sub-tasks or increase timeout:

```python
agent.agent_executor.max_execution_time = 600  # 10 minutes
```

### Memory Issues

**Problem:** Agent loses context or runs out of memory

**Solution:** Clear memory periodically:

```python
agent.clear_memory()
```

## Advanced Features

### Custom System Prompt

```python
# Modify agent's persona
agent.prompt = ChatPromptTemplate.from_messages([
    ("system", "Your custom instructions here..."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
```

### Add Custom Tools

```python
from langchain.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """Description of what the tool does."""
    return "Result"

# Add to agent
agent.tools.append(my_custom_tool)
```

### Adjust Retry Behavior

```python
# More aggressive retries
agent = AgentCore(vector_store, max_retries=5)

# No retries (fail fast)
agent = AgentCore(vector_store, max_retries=0)
```

## Performance Tips

1. **Reuse Agent Instance** - Don't create new agent for each task
2. **Use Knowledge Base** - Faster than web search
3. **Clear Memory** - Prevents context overflow
4. **Monitor Iterations** - Adjust max_iterations if needed
5. **Batch Similar Tasks** - Leverage conversation memory

## Security Notes

- All code execution happens in isolated Docker containers
- File operations restricted to agent_workspace directory
- API keys never logged or exposed
- Sandbox runs as unprivileged user
- Network disabled by default in sandbox

## Support

For issues or questions:

1. Check logs in `Agent/logs/`
2. Review error messages and solutions
3. Verify configuration in `.env`
4. Ensure Docker is running
5. Check knowledge base has PDFs

## Next Steps

- Integrate with UI (see `agent_ui.py`)
- Add custom tools for your use case
- Populate knowledge base with domain PDFs
- Configure telephony for real calls
- Set up monitoring and analytics
