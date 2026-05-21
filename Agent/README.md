# O.M.I Agent - Autonomous AI Expert System

## Overview

O.M.I (Künstliche Intelligenz) is an autonomous AI agent with dual expertise in renewable energy consulting and software architecture. It uses the ReAct (Reasoning + Acting) pattern to autonomously execute complex tasks.

## Features

- 🧠 **Autonomous Reasoning**: ReAct pattern for complex task execution
- 📚 **Knowledge Base**: FAISS vector search over PDF documents
- 📞 **Outbound Calling**: Voice synthesis with ElevenLabs
- 🐳 **Secure Execution**: Isolated Docker sandbox
- 📁 **File Operations**: Secure workspace access
- 🔍 **Web Search**: Tavily API integration
- 🧪 **Automated Testing**: pytest integration with TDD
- 💬 **Conversation Memory**: Context-aware interactions

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker** (installed and running)
- **OpenAI API Key** (required)

### Installation

1. **Install Dependencies**:
   ```bash
   cd Agent
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   ```bash
   # Copy example file
   cp ../.env.example ../.env
   # Edit and add your OPENAI_API_KEY
   ```

3. **Build Docker Sandbox**:
   ```bash
   docker build -t O.M.I_agent_sandbox -f sandbox/Dockerfile sandbox/
   ```

4. **Add Knowledge Base** (Optional):
   - Place PDF documents in `knowledge_base/` directory

5. **Verify Installation**:
   ```bash
   python validate_config.py
   ```

## Configuration

### Required API Keys

Edit `.env` file in the root directory:

```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
TAVILY_API_KEY=tvly-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
ELEVEN_LABS_API_KEY=...
```

### Agent Settings

Edit `agent/config.py` to customize:
- LLM model and temperature
- Docker timeout settings
- Knowledge base parameters
- Logging levels

## Usage

### Accessing the Agent

1. Start the main application
2. Navigate to **A.G.E.N.T.** menu
3. Enter your task
4. Click "Start Agent"
5. Watch real-time execution

### Example Tasks

**Renewable Energy Consulting**:
```
Durchsuche die Wissensdatenbank nach den Vorteilen einer PV-Anlage 
mit Wärmepumpe. Erstelle eine Präsentation mit den Top 3 Vorteilen.
```

**Software Development**:
```
Erstelle eine Flask-API für Amortisationsberechnungen mit Tests.
```

**Sales Call Simulation**:
```
Simuliere einen Anruf bei einem Kunden. Präsentiere die Vorteile 
einer PV-Anlage und behandle Einwände.
```

## Architecture

```
agent/
├── agent_core.py           # Main orchestration
├── agent_ui.py             # Streamlit interface
├── config.py               # Configuration
├── errors.py               # Custom exceptions
├── logging_config.py       # Logging setup
├── security.py             # Security utilities
└── tools/
    ├── knowledge_tools.py  # Vector search
    ├── coding_tools.py     # File operations
    ├── execution_tools.py  # Docker sandbox
    ├── telephony_tools.py  # Calling
    ├── search_tools.py     # Web search
    └── testing_tools.py    # pytest
```

## Security

- **Docker Isolation**: Unprivileged containers
- **Path Validation**: Restricted to workspace
- **API Key Protection**: Never logged or exposed
- **Network Isolation**: Disabled by default
- **Resource Limits**: Timeouts and cleanup

## Troubleshooting

### Docker Image Not Found
```bash
docker build -t O.M.I_agent_sandbox -f sandbox/Dockerfile sandbox/
```

### API Key Errors
Check `.env` file exists and contains `OPENAI_API_KEY=sk-...`

### Knowledge Base Empty
Add PDF files to `Agent/knowledge_base/` directory

### Container Cleanup
```bash
docker ps -a | grep O.M.I-sandbox | awk '{print $1}' | xargs docker rm -f
```

## Development

### Adding New Tools

1. Create tool in `agent/tools/`:
```python
from langchain.tools import tool

@tool
def my_tool(param: str) -> str:
    """Tool description for the agent."""
    return "result"
```

2. Add to `agent_core.py`:
```python
from agent.tools.my_tools import my_tool
self.tools = [..., my_tool]
```

### Running Tests
```bash
pytest Agent/tests/ -v
```

## Performance

- **Agent Response**: < 2 seconds
- **Knowledge Search**: < 1 second
- **Docker Creation**: < 5 seconds
- **Code Execution**: 1-30 seconds

## Documentation

- `AGENT_CORE_QUICK_START.md` - Agent core guide
- `EXECUTION_TOOLS_QUICK_START.md` - Sandbox guide
- `API_KEY_SECURITY_GUIDE.md` - Security guide
- `LOGGING_QUICK_REFERENCE.md` - Logging guide
- `DOCUMENTATION_GUIDE.md` - Code documentation
- `sandbox/README.md` - Docker sandbox details

## Support

1. Check [Troubleshooting](#troubleshooting)
2. Review `logs/agent.log`
3. Run `python validate_config.py`
4. Check existing documentation

## License

Proprietary - Bokuk2 Development Team

## Version

1.0.0 - Initial Release
