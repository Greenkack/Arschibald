# Design Document - KAI Agent Integration

## Overview

The KAI Agent integration adds an autonomous AI expert system to the Bokuk2 application, providing dual expertise in renewable energy consulting and software architecture. The system is designed as a modular, isolated component that integrates seamlessly with the existing application without disrupting current functionality.

### Key Design Principles

1. **Modularity**: Agent system is self-contained in its own module structure
2. **Security**: All code execution happens in isolated Docker containers
3. **Isolation**: Agent operations don't interfere with existing application state
4. **Extensibility**: Easy to add new tools and capabilities
5. **User-Friendly**: Clear UI with real-time feedback and transparent reasoning

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Bokuk2 Application                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Main Application Menu                    │  │
│  │  [Solar] [CRM] [Admin] [PDF] [A.G.E.N.T.] ← New     │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Agent UI Module (agent_ui.py)              │  │
│  │  - Task Input Interface                              │  │
│  │  - Real-time Status Display                          │  │
│  │  - Results Visualization                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Agent Core (agent/agent_core.py)             │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  LangChain Agent Executor (ReAct Pattern)      │  │  │
│  │  │  - GPT-4 LLM                                    │  │  │
│  │  │  - Conversation Memory                          │  │  │
│  │  │  - Tool Orchestration                           │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│              ┌────────────┴────────────┐                    │
│              ▼                         ▼                    │
│  ┌─────────────────────┐   ┌─────────────────────┐        │
│  │   Tool Categories   │   │  External Services  │        │
│  │  - Knowledge Base   │   │  - OpenAI API       │        │
│  │  - File Operations  │   │  - Tavily Search    │        │
│  │  - Code Execution   │   │  - Twilio Phone     │        │
│  │  - Telephony        │   │  - ElevenLabs Voice │        │
│  │  - Testing          │   │  - Docker Engine    │        │
│  └─────────────────────┘   └─────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
agent/
├── __init__.py
├── agent_core.py              # Main agent orchestration
├── agent_ui.py                # Streamlit UI integration
├── config.py                  # Configuration management
└── tools/
    ├── __init__.py
    ├── knowledge_tools.py     # Vector DB & knowledge search
    ├── coding_tools.py        # File system operations
    ├── execution_tools.py     # Docker sandbox execution
    ├── telephony_tools.py     # Outbound calling
    ├── search_tools.py        # Web search
    └── testing_tools.py       # Pytest execution
```

## Components and Interfaces

### 1. Agent UI Module (`agent_ui.py`)

**Purpose**: Provides the Streamlit interface for agent interaction

**Key Functions**:

- `render_agent_menu()`: Main entry point, renders the agent interface
- `check_api_keys()`: Validates required API keys
- `display_agent_status()`: Shows real-time agent thinking process
- `format_agent_output()`: Formats and displays agent results

**Interface**:

```python
def render_agent_menu():
    """
    Renders the A.G.E.N.T. menu interface.
    
    Returns:
        None (renders Streamlit UI)
    
    Raises:
        ConfigurationError: If required API keys are missing
    """
    pass
```

**Integration Point**: Called from main application menu (e.g., `admin_panel.py` or main app file)

### 2. Agent Core (`agent/agent_core.py`)

**Purpose**: Orchestrates the agent's reasoning and action loop

**Key Classes**:

```python
class AgentCore:
    """
    Main agent orchestration class using LangChain's ReAct pattern.
    
    Attributes:
        llm: ChatOpenAI instance (GPT-4)
        tools: List of available tools
        prompt: System prompt template
        agent_executor: LangChain AgentExecutor
        memory: Conversation buffer
    """
    
    def __init__(self, vector_store):
        """
        Initialize agent with knowledge base.
        
        Args:
            vector_store: FAISS vector store for knowledge retrieval
        """
        pass
    
    def run(self, user_input: str) -> dict:
        """
        Execute agent task.
        
        Args:
            user_input: User's task description
            
        Returns:
            dict: {
                'output': str,  # Final response
                'intermediate_steps': list,  # Reasoning trace
                'success': bool
            }
        """
        pass
```

**System Prompt Design**:
The agent has a dual-expertise persona:

1. **Renewable Energy Expert**: Uses knowledge base first, then web search
2. **Software Architect**: Follows TDD, SOLID principles, generates clean code

### 3. Knowledge Base Tools (`agent/tools/knowledge_tools.py`)

**Purpose**: Manage and search domain-specific knowledge

**Key Functions**:

```python
def setup_knowledge_base(
    path: str = "knowledge_base",
    db_path: str = "faiss_index"
) -> FAISS:
    """
    Load PDFs, create embeddings, build vector store.
    
    Args:
        path: Directory containing PDF documents
        db_path: Path to save/load FAISS index
        
    Returns:
        FAISS vector store instance
        
    Process:
        1. Check if index exists (skip if yes)
        2. Load all PDFs from directory
        3. Split into chunks (1000 chars, 100 overlap)
        4. Create embeddings with OpenAI
        5. Build and save FAISS index
    """
    pass

def knowledge_base_search(vector_store) -> Tool:
    """
    Create search tool with vector store access.
    
    Args:
        vector_store: FAISS instance
        
    Returns:
        LangChain Tool for knowledge search
    """
    pass
```

**Data Flow**:

```
PDF Documents → PyPDFLoader → Text Chunks → OpenAI Embeddings → FAISS Index
                                                                      ↓
User Query → Embedding → Similarity Search → Top 3 Chunks → Agent
```

### 4. Telephony Tools (`agent/tools/telephony_tools.py`)

**Purpose**: Enable outbound calling with voice synthesis

**Key Functions**:

```python
@tool
def start_interactive_call(
    phone_number: str,
    opening_statement: str,
    call_goal: str
) -> str:
    """
    Initiate outbound call with ElevenLabs voice.
    
    Args:
        phone_number: Target phone number
        opening_statement: Initial message
        call_goal: Objective of the call
        
    Returns:
        Call transcript summary
        
    Process:
        1. Initialize ElevenLabs client
        2. Generate audio stream for opening
        3. Simulate conversation flow
        4. Handle objections with knowledge-based responses
        5. Generate transcript summary
    """
    pass

@tool
def update_call_summary(new_information: str) -> str:
    """
    Add notes to ongoing call transcript.
    
    Args:
        new_information: Information to append
        
    Returns:
        Confirmation message
    """
    pass
```

**Call Protocol**:

1. **Preparation**: Search knowledge base for relevant facts
2. **Opening**: Confident, professional introduction
3. **Presentation**: Top 3 benefits with data backing
4. **Objection Handling**: Validate concern, counter with facts
5. **Closing**: Clear next step (e.g., send calculation)

### 5. Code Execution Tools (`agent/tools/execution_tools.py`)

**Purpose**: Safely execute code in isolated Docker containers

**Key Functions**:

```python
@tool
def execute_python_code_in_sandbox(code: str) -> str:
    """
    Run Python code in isolated Docker container.
    
    Args:
        code: Python code string
        
    Returns:
        Combined stdout and stderr
        
    Security:
        - Runs as unprivileged user
        - Network disabled
        - 30-second timeout
        - Auto-cleanup after execution
    """
    pass

@tool
def run_terminal_command_in_sandbox(command: str) -> str:
    """
    Execute shell command in sandbox.
    
    Args:
        command: Shell command string
        
    Returns:
        Command output
        
    Use Cases:
        - Install packages (pip install)
        - Run tests (pytest)
        - File operations (ls, cat)
    """
    pass
```

**Docker Sandbox Specification**:

```dockerfile
FROM python:3.11-slim
RUN useradd --create-home sandboxuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
USER sandboxuser
RUN mkdir /app/workspace
WORKDIR /app/workspace
```

### 6. File System Tools (`agent/tools/coding_tools.py`)

**Purpose**: Manage files in agent workspace

**Key Functions**:

```python
@tool
def write_file(path: str, content: str) -> str:
    """
    Write content to file in agent_workspace.
    
    Security:
        - Path validation (no directory traversal)
        - Auto-create parent directories
        - UTF-8 encoding
    """
    pass

@tool
def read_file(path: str) -> str:
    """Read file from agent_workspace."""
    pass

@tool
def list_files(path: str = ".") -> str:
    """List files in workspace directory."""
    pass

@tool
def generate_project_structure(
    project_name: str,
    project_type: str,
    features: list
) -> str:
    """
    Generate complete project scaffold.
    
    Args:
        project_name: Name of project
        project_type: e.g., "flask_api", "streamlit_app"
        features: List of features to include
        
    Returns:
        Summary of created files
        
    Generates:
        - Directory structure
        - Configuration files
        - Main application files
        - Test files
        - README.md
        - requirements.txt
    """
    pass
```

### 7. Testing Tools (`agent/tools/testing_tools.py`)

**Purpose**: Execute automated tests

**Key Functions**:

```python
@tool
def execute_pytest_in_sandbox() -> str:
    """
    Run pytest in Docker sandbox.
    
    Returns:
        Test results with pass/fail status
        
    Process:
        1. Execute 'pytest -v' in sandbox
        2. Capture output
        3. Parse results
        4. Return formatted summary
    """
    pass
```

### 8. Search Tools (`agent/tools/search_tools.py`)

**Purpose**: Web search for current information

**Key Functions**:

```python
@tool
def tavily_search(query: str) -> str:
    """
    Search web with Tavily API.
    
    Args:
        query: Search query
        
    Returns:
        JSON string with results (URLs + content)
        
    Configuration:
        - search_depth: "advanced"
        - Returns top results with snippets
    """
    pass
```

## Data Models

### Agent Task Model

```python
@dataclass
class AgentTask:
    task_id: str
    user_input: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    created_at: datetime
    completed_at: Optional[datetime]
    result: Optional[dict]
    error: Optional[str]
```

### Knowledge Document Model

```python
@dataclass
class KnowledgeDocument:
    doc_id: str
    filename: str
    content: str
    chunks: List[str]
    embeddings: np.ndarray
    metadata: dict
```

### Call Transcript Model

```python
@dataclass
class CallTranscript:
    call_id: str
    phone_number: str
    goal: str
    transcript: List[dict]  # [{'speaker': 'KAI'|'USER', 'text': str}]
    summary: str
    outcome: str
    duration: int
```

## Error Handling

### Error Categories

1. **Configuration Errors**
   - Missing API keys
   - Invalid environment variables
   - Solution: Display clear setup instructions

2. **Docker Errors**
   - Image not found
   - Container creation failure
   - Solution: Provide build/troubleshooting commands

3. **API Errors**
   - Rate limits
   - Authentication failures
   - Solution: Retry with exponential backoff, fallback options

4. **Execution Errors**
   - Code syntax errors
   - Runtime exceptions
   - Solution: Agent analyzes error, attempts fix

5. **Resource Errors**
   - Disk space
   - Memory limits
   - Solution: Cleanup, resource monitoring

### Error Handling Strategy

```python
class AgentError(Exception):
    """Base exception for agent errors."""
    pass

class ConfigurationError(AgentError):
    """Configuration or setup error."""
    pass

class ExecutionError(AgentError):
    """Code execution error."""
    pass

class APIError(AgentError):
    """External API error."""
    pass

# Error handling in agent_core.py
try:
    result = self.agent_executor.invoke({"input": user_input})
except ConfigurationError as e:
    return {
        'success': False,
        'error': str(e),
        'solution': 'Check .env file and ensure all API keys are set'
    }
except ExecutionError as e:
    return {
        'success': False,
        'error': str(e),
        'solution': 'Review code for syntax errors or runtime issues'
    }
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return {
        'success': False,
        'error': 'An unexpected error occurred',
        'solution': 'Check logs for details'
    }
```

## Testing Strategy

### Unit Tests

**Test Coverage**:

- Each tool function
- Agent core initialization
- Configuration loading
- Error handling paths

**Example Test**:

```python
def test_write_file_security():
    """Test that write_file prevents directory traversal."""
    result = write_file("../../../etc/passwd", "malicious")
    assert "nicht erlaubt" in result
    
def test_knowledge_base_search():
    """Test knowledge base returns relevant results."""
    vector_store = setup_test_knowledge_base()
    search_tool = knowledge_base_search(vector_store)
    result = search_tool("Photovoltaik Vorteile")
    assert len(result) > 0
    assert "Photovoltaik" in result or "PV" in result
```

### Integration Tests

**Test Scenarios**:

1. End-to-end task execution
2. Docker sandbox creation and cleanup
3. Knowledge base loading and search
4. API integration (with mocks)

**Example Test**:

```python
def test_agent_complete_workflow():
    """Test agent can complete a full task."""
    agent = AgentCore(vector_store=mock_vector_store)
    result = agent.run("Schreibe eine Funktion, die 1+1 berechnet")
    assert result['success'] == True
    assert 'def' in result['output']
```

### Manual Testing Checklist

- [ ] Agent menu appears in main application
- [ ] API key validation works correctly
- [ ] Knowledge base loads without errors
- [ ] Agent can search knowledge base
- [ ] Agent can write and read files
- [ ] Docker sandbox executes code safely
- [ ] Telephony simulation works
- [ ] Web search returns results
- [ ] Error messages are clear and actionable
- [ ] Agent reasoning is visible in UI
- [ ] Results are formatted properly
- [ ] No interference with existing app features

## Security Considerations

### 1. Code Execution Isolation

- All code runs in Docker containers
- Containers use unprivileged users
- Network access disabled by default
- Automatic container cleanup

### 2. File System Security

- Strict path validation
- Operations limited to agent_workspace
- No symbolic link following
- Input sanitization

### 3. API Key Management

- Keys stored in .env file (not in code)
- .env file in .gitignore
- Keys never logged or displayed
- Validation on startup

### 4. Input Validation

- User input sanitized before processing
- File paths validated
- Command injection prevention
- SQL injection not applicable (no direct DB access)

### 5. Resource Limits

- Docker container timeouts
- Memory limits on containers
- Disk space monitoring
- Rate limiting on API calls

## Performance Optimization

### 1. Knowledge Base

- Cache FAISS index (don't rebuild on every start)
- Lazy loading of embeddings
- Batch processing for multiple queries
- Index optimization for large document sets

### 2. Docker Operations

- Reuse base images
- Minimize container startup time
- Parallel container execution for independent tasks
- Efficient cleanup strategies

### 3. API Calls

- Batch requests where possible
- Implement caching for repeated queries
- Use streaming for long responses
- Connection pooling

### 4. UI Responsiveness

- Async agent execution
- Progress indicators
- Streaming output display
- Background task processing

## Deployment Considerations

### Prerequisites

1. Docker installed and running
2. Python 3.11+
3. Required API keys configured
4. Sufficient disk space for Docker images

### Installation Steps

1. Install Python dependencies: `pip install -r requirements.txt`
2. Build Docker sandbox: `docker build -t kai_agent-sandbox -f sandbox/Dockerfile .`
3. Create .env file with API keys
4. Place knowledge PDFs in `knowledge_base/` directory
5. Run application

### Configuration Files

**.env.example**:

```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
ELEVEN_LABS_API_KEY=...
```

**sandbox/requirements.txt**:

```
pytest
requests
numpy
pandas
```

### Monitoring and Logging

**Logging Strategy**:

- Agent reasoning steps logged to console
- Errors logged with full stack traces
- API calls logged (without sensitive data)
- Docker operations logged

**Log Levels**:

- DEBUG: Detailed agent reasoning
- INFO: Task start/completion
- WARNING: Recoverable errors
- ERROR: Failures requiring attention

## Integration with Existing Application

### Menu Integration

Add to main application menu (e.g., in `admin_panel.py` or main app file):

```python
import streamlit as st
from agent.agent_ui import render_agent_menu

# In main menu
menu_options = ["Solar Calculator", "CRM", "Admin", "PDF", "A.G.E.N.T."]
choice = st.sidebar.selectbox("Menu", menu_options)

if choice == "A.G.E.N.T.":
    render_agent_menu()
```

### Dependency Management

**New Dependencies**:

- langchain
- langchain-openai
- langchain-community
- docker
- tavily-python
- twilio
- elevenlabs
- faiss-cpu
- pypdf

**Conflict Resolution**:

- Check for version conflicts with existing packages
- Use virtual environment if needed
- Pin versions in requirements.txt

### Database Considerations

**Agent does NOT**:

- Access existing application database
- Modify user data
- Interfere with solar calculations
- Touch CRM records

**Agent DOES**:

- Use its own workspace directory
- Maintain separate conversation memory
- Store knowledge base index separately

### State Management

- Agent state stored in Streamlit session_state
- No shared state with other modules
- Clean initialization on menu switch
- Memory cleared on session end

## Future Enhancements

### Phase 2 Features

1. **Real Telephony Integration**: Replace simulation with actual Twilio calls
2. **Multi-Agent Collaboration**: Multiple agents working together
3. **Persistent Task Queue**: Save and resume tasks
4. **Advanced Analytics**: Track agent performance metrics
5. **Custom Tool Creation**: UI for adding new tools
6. **Voice Input**: Speech-to-text for task input
7. **Multi-Language Support**: Extend beyond German/English
8. **Integration with CRM**: Auto-log calls and interactions
9. **Scheduled Tasks**: Cron-like agent task scheduling
10. **Agent Training**: Fine-tune on company-specific data

### Scalability Improvements

- Distributed task execution
- Load balancing for multiple agents
- Cloud-based knowledge base
- Horizontal scaling of Docker workers

## Conclusion

This design provides a comprehensive, secure, and extensible architecture for integrating the KAI Agent into the Bokuk2 application. The modular design ensures isolation from existing functionality while providing powerful AI-driven capabilities for renewable energy consulting and software development.

The system prioritizes:

- **Security**: Isolated execution environments
- **Usability**: Clear UI and transparent reasoning
- **Reliability**: Robust error handling
- **Extensibility**: Easy to add new tools and capabilities
- **Performance**: Optimized for responsive user experience

The agent is ready to handle complex tasks autonomously, from conducting expert sales calls to generating complete software projects with tests.
