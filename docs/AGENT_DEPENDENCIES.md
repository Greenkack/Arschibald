# KAI Agent Dependencies Documentation

## Overview

This document describes the dependencies required for the KAI Agent integration and provides guidance on installation, version management, and conflict resolution.

## Required Dependencies

### Core Agent Framework

- **langchain** (>=0.3.21): Framework for building LLM-powered applications
- **langchain-openai** (>=0.3.0): OpenAI integration for LangChain
- **langchain-community** (>=0.3.21): Community tools and integrations for LangChain

### AI Services

- **openai** (via langchain-openai): GPT-4 language model access
- **tavily-python** (>=0.5.0): Web search API integration
- **elevenlabs** (>=1.96.0): Voice synthesis for telephony features

### Telephony

- **twilio** (>=9.4.0): Phone call integration (optional)
- **websockets** (>=14.1): WebSocket support for real-time communication

### Knowledge Base

- **faiss-cpu** (>=1.9.0): Vector similarity search for knowledge retrieval
- **pypdf** (included in main requirements): PDF document loading

### Infrastructure

- **docker** (>=7.1.0): Container management for code execution sandbox
- **python-dotenv** (>=1.1.1): Environment variable management

### Testing

- **pytest** (>=8.4.2): Testing framework (already in main requirements)

## Installation

### Standard Installation

Install all dependencies from the main requirements.txt:

```bash
pip install -r requirements.txt
```

### Agent-Only Installation

If you only want to install agent-specific dependencies:

```bash
pip install langchain>=0.3.21 langchain-openai>=0.3.0 langchain-community>=0.3.21
pip install tavily-python>=0.5.0 twilio>=9.4.0 elevenlabs>=1.96.0
pip install faiss-cpu>=1.9.0 websockets>=14.1
```

### Docker Requirement

The agent requires Docker to be installed and running on your system:

- **Windows**: Docker Desktop for Windows
- **Linux**: Docker Engine
- **macOS**: Docker Desktop for Mac

Verify Docker installation:

```bash
docker --version
docker ps
```

## Version Compatibility

### Python Version

- **Required**: Python 3.10 or higher
- **Recommended**: Python 3.11
- **Tested**: Python 3.11

### Key Compatibility Notes

1. **LangChain Ecosystem**
   - All langchain packages should use compatible versions
   - langchain-openai and langchain-community should match langchain major version
   - Current stable: 0.3.x series

2. **OpenAI API**
   - Requires openai>=1.0.0 (installed via langchain-openai)
   - Compatible with GPT-4 and GPT-3.5-turbo models

3. **FAISS**
   - faiss-cpu is used for CPU-only systems
   - For GPU acceleration, replace with faiss-gpu (requires CUDA)
   - Version 1.9.0+ recommended for stability

4. **Docker SDK**
   - docker>=7.0.0 required for modern API support
   - Compatible with Docker Engine 20.10+

5. **Streamlit**
   - Agent UI requires streamlit>=1.49.0 (already in main requirements)
   - Compatible with all streamlit extensions in main requirements

## Known Conflicts and Resolutions

### No Known Conflicts

The agent dependencies have been tested with the existing Bokuk2 application dependencies and no conflicts were found:

- ✅ **pydantic**: Both langchain and existing app use pydantic 2.x
- ✅ **requests**: Compatible versions across all packages
- ✅ **numpy**: faiss-cpu compatible with numpy 2.x
- ✅ **python-dotenv**: Already in main requirements
- ✅ **pytest**: Already in main requirements

### Potential Issues

1. **FAISS Memory Usage**
   - Large knowledge bases (>1000 documents) may require significant RAM
   - Solution: Use index caching and lazy loading (already implemented)

2. **Docker Availability**
   - Agent requires Docker daemon to be running
   - Solution: Clear error messages guide users to start Docker

3. **API Rate Limits**
   - OpenAI, Tavily, and ElevenLabs have rate limits
   - Solution: Implement retry logic with exponential backoff (already implemented)

## Dependency Groups

### Minimal Installation (Core Features Only)

```
langchain>=0.3.21
langchain-openai>=0.3.0
langchain-community>=0.3.21
docker>=7.1.0
python-dotenv>=1.1.1
faiss-cpu>=1.9.0
pypdf
```

### Full Installation (All Features)

Add to minimal:

```
tavily-python>=0.5.0
twilio>=9.4.0
elevenlabs>=1.96.0
websockets>=14.1
```

## Environment Variables

Required API keys (see .env.example):

### Required

- `OPENAI_API_KEY`: OpenAI API key for GPT-4 access

### Optional (enables additional features)

- `TAVILY_API_KEY`: Web search capability
- `TWILIO_ACCOUNT_SID`: Telephony features
- `TWILIO_AUTH_TOKEN`: Telephony features
- `TWILIO_PHONE_NUMBER`: Telephony features
- `ELEVEN_LABS_API_KEY`: Voice synthesis

## Testing Installation

### Verify Core Dependencies

```python
# Test in Python REPL
import langchain
import langchain_openai
import langchain_community
import docker
import faiss
print("✓ Core dependencies installed")
```

### Verify Optional Dependencies

```python
# Test optional features
try:
    import tavily
    print("✓ Tavily search available")
except ImportError:
    print("✗ Tavily not installed (web search disabled)")

try:
    import twilio
    print("✓ Twilio available")
except ImportError:
    print("✗ Twilio not installed (telephony disabled)")

try:
    import elevenlabs
    print("✓ ElevenLabs available")
except ImportError:
    print("✗ ElevenLabs not installed (voice synthesis disabled)")
```

### Verify Docker

```bash
docker run --rm hello-world
```

## Troubleshooting

### Installation Errors

**Problem**: `pip install faiss-cpu` fails

- **Solution**: Install build tools (Visual C++ on Windows, gcc on Linux)
- **Alternative**: Use pre-built wheels from conda-forge

**Problem**: `docker` package import fails

- **Solution**: Ensure Docker Desktop/Engine is installed and running
- **Verify**: Run `docker ps` in terminal

**Problem**: LangChain version conflicts

- **Solution**: Upgrade all langchain packages together:

  ```bash
  pip install --upgrade langchain langchain-openai langchain-community
  ```

### Runtime Errors

**Problem**: "Docker daemon not running"

- **Solution**: Start Docker Desktop or Docker service
- **Windows**: Start Docker Desktop application
- **Linux**: `sudo systemctl start docker`

**Problem**: "OpenAI API key not found"

- **Solution**: Create .env file from .env.example and add your API key

**Problem**: FAISS index creation fails

- **Solution**: Check available memory, reduce chunk size in knowledge_tools.py

## Maintenance

### Updating Dependencies

To update agent dependencies to latest compatible versions:

```bash
pip install --upgrade langchain langchain-openai langchain-community
pip install --upgrade tavily-python twilio elevenlabs faiss-cpu
```

### Security Updates

Monitor security advisories for:

- langchain ecosystem (check GitHub security tab)
- docker SDK (check PyPI)
- API client libraries (twilio, elevenlabs)

### Version Pinning

Current requirements.txt uses minimum version constraints (>=) to allow flexibility. For production deployments, consider pinning exact versions:

```
langchain==0.3.21
langchain-openai==0.3.0
langchain-community==0.3.21
```

## Performance Considerations

### Memory Usage

- **Base agent**: ~200MB
- **With knowledge base (100 docs)**: ~500MB
- **With knowledge base (1000 docs)**: ~2GB

### Disk Space

- **Python packages**: ~500MB
- **Docker sandbox image**: ~200MB
- **FAISS index cache**: Varies by document count

### Network Usage

- **OpenAI API**: ~1KB per request (input) + variable (output)
- **Tavily API**: ~5KB per search
- **ElevenLabs**: ~50KB per voice synthesis request

## Support

For dependency-related issues:

1. Check this documentation
2. Review error messages in agent UI
3. Check Docker logs: `docker logs <container_id>`
4. Verify API keys in .env file
5. Test individual imports in Python REPL

## Changelog

### Version 1.0 (Current)

- Initial agent integration
- LangChain 0.3.x support
- Docker sandbox execution
- FAISS knowledge base
- Optional telephony and search features
