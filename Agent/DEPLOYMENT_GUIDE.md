# KAI Agent Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [Production Deployment](#production-deployment)
7. [Maintenance](#maintenance)

## Prerequisites

### System Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| Operating System | Windows 10/11, macOS 10.15+, Linux | Any modern OS |
| Python | 3.11 or higher | Check with `python --version` |
| Docker | Latest version | Docker Desktop or Engine |
| Memory | 4GB minimum, 8GB recommended | For Docker containers |
| Disk Space | 2GB minimum | For images and knowledge base |
| Internet | Required | For API calls and downloads |

### Required Software

#### 1. Python 3.11+

**Windows**:
```powershell
# Download from python.org
# Or use winget
winget install Python.Python.3.11
```

**macOS**:
```bash
# Using Homebrew
brew install python@3.11
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Verify Installation**:
```bash
python --version
# Should show: Python 3.11.x or higher
```

#### 2. Docker

**Windows/macOS**:
1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install and start Docker Desktop
3. Verify: `docker --version`

**Linux (Ubuntu/Debian)**:
```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in
# Verify
docker --version
```

**Verify Docker is Running**:
```bash
docker info
# Should show Docker information without errors
```

### API Keys

#### Required

- **OpenAI API Key** (REQUIRED)
  - Sign up at [platform.openai.com](https://platform.openai.com/)
  - Navigate to API Keys section
  - Create new secret key
  - Copy and save securely

#### Optional

- **Tavily API Key** (for web search)
  - Sign up at [tavily.com](https://tavily.com/)
  - Get API key from dashboard

- **Twilio Credentials** (for telephony)
  - Sign up at [twilio.com](https://www.twilio.com/)
  - Get Account SID, Auth Token, and Phone Number

- **ElevenLabs API Key** (for voice synthesis)
  - Sign up at [elevenlabs.io](https://elevenlabs.io/)
  - Get API key from profile

## Installation Steps

### Method 1: Automated Installation (Recommended)

Run the automated installation script:

```bash
# From project root
python Agent/install.py
```

This script will:
1. ✓ Check Python version
2. ✓ Check Docker installation
3. ✓ Install Python dependencies
4. ✓ Create .env file from template
5. ✓ Build Docker sandbox image
6. ✓ Set up knowledge base directory
7. ✓ Set up workspace directory
8. ✓ Set up logs directory
9. ✓ Run validation checks

**Follow the prompts** to configure API keys during installation.

### Method 2: Manual Installation

If you prefer manual installation or the automated script fails:

#### Step 1: Install Python Dependencies

```bash
cd Agent
pip install -r requirements.txt
```

**If you encounter permission errors**:
```bash
# Use user installation
pip install --user -r requirements.txt

# Or create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 2: Configure Environment Variables

```bash
# Copy example file
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=sk-your-actual-key-here
# Add other optional keys as needed
```

#### Step 3: Build Docker Sandbox

```bash
# From project root
docker build -t kai_agent_sandbox -f Agent/sandbox/Dockerfile Agent/sandbox/

# Or use the build script
# Windows
cd Agent\sandbox
.\build.ps1

# Linux/Mac
cd Agent/sandbox
chmod +x build.sh
./build.sh
```

**Verify the build**:
```bash
docker images | grep kai_agent_sandbox
```

#### Step 4: Set Up Directories

```bash
# Create required directories
mkdir -p Agent/knowledge_base
mkdir -p Agent/agent_workspace
mkdir -p Agent/logs
```

#### Step 5: Initialize Knowledge Base (Optional)

```bash
# Initialize knowledge base
python Agent/setup_knowledge_base.py init

# Add PDF documents to Agent/knowledge_base/

# Index documents
python Agent/setup_knowledge_base.py index
```

#### Step 6: Verify Installation

```bash
python Agent/validate_config.py
```

This will check:
- ✓ Environment file exists
- ✓ API keys are configured
- ✓ Docker is running
- ✓ Docker image is built
- ✓ File permissions are secure

## Configuration

### Environment Variables

Edit the `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=sk-...

# Optional - Web Search
TAVILY_API_KEY=tvly-...

# Optional - Telephony
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Optional - Voice Synthesis
ELEVEN_LABS_API_KEY=...
```

### Agent Configuration

Edit `Agent/agent/config.py` for advanced settings:

```python
# LLM Settings
LLM_MODEL = "gpt-4"  # or "gpt-4-turbo-preview"
LLM_TEMPERATURE = 0.7  # 0.0 = deterministic, 1.0 = creative

# Docker Settings
DOCKER_TIMEOUT_PYTHON = 30  # seconds
DOCKER_TIMEOUT_TERMINAL = 120  # seconds
DOCKER_IMAGE_NAME = "kai_agent_sandbox"

# Knowledge Base Settings
CHUNK_SIZE = 1000  # characters per chunk
CHUNK_OVERLAP = 100  # overlap between chunks
SIMILARITY_SEARCH_K = 3  # number of results to return

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
AGENT_VERBOSE = True  # Show agent reasoning
```

### Docker Sandbox Packages

To add Python packages available in the sandbox:

1. Edit `Agent/sandbox/requirements.txt`
2. Add your packages:
   ```txt
   pytest>=7.4.0
   requests>=2.31.0
   numpy>=1.24.0
   pandas>=2.0.0
   # Add more packages here
   ```
3. Rebuild the Docker image:
   ```bash
   docker build -t kai_agent_sandbox -f Agent/sandbox/Dockerfile Agent/sandbox/
   ```

### Knowledge Base

Add PDF documents to `Agent/knowledge_base/`:

```bash
# Copy your PDFs
cp /path/to/your/documents/*.pdf Agent/knowledge_base/

# Index them
python Agent/setup_knowledge_base.py index

# Verify
python Agent/setup_knowledge_base.py verify
```

**Best Practices**:
- Use descriptive filenames
- Keep documents focused on specific topics
- Limit to < 1000 PDFs for best performance
- Update regularly with latest information

## Verification

### Quick Verification

Run the validation script:

```bash
python Agent/validate_config.py
```

Expected output:
```
======================================================================
KAI Agent Configuration Validation
======================================================================

Checking Environment File...
✅ .env file found and properly configured

Checking API Keys...
✅ Required API keys configured

Checking Docker Installation...
✅ Docker is installed and running

Checking Docker Image...
✅ Docker sandbox image found

Checking File Permissions...
✅ .env file permissions are secure

======================================================================
✅ VALIDATION PASSED - All checks successful!
Agent is ready to run.
======================================================================
```

### Component Testing

#### Test Knowledge Base

```bash
python Agent/test_knowledge_search.py
```

#### Test Docker Sandbox

```bash
python Agent/test_execution_tools.py
```

#### Test Agent Core

```bash
python Agent/test_agent_core.py
```

#### Test API Keys

```bash
python Agent/test_api_key_security.py
```

### Integration Testing

Start the application and:

1. Navigate to **A.G.E.N.T.** menu
2. Enter a simple task: `Schreibe eine Funktion, die 1+1 berechnet`
3. Click "Start Agent"
4. Verify the agent executes successfully

## Troubleshooting

### Common Issues

#### 1. Docker Image Not Found

**Error**: `docker.errors.ImageNotFound: 404 Client Error`

**Solution**:
```bash
# Build the image
docker build -t kai_agent_sandbox -f Agent/sandbox/Dockerfile Agent/sandbox/

# Verify
docker images | grep kai_agent_sandbox
```

#### 2. API Key Not Found

**Error**: `ConfigurationError: OPENAI_API_KEY not found`

**Solution**:
1. Check `.env` file exists in project root
2. Verify key format: `OPENAI_API_KEY=sk-...`
3. No spaces around `=`
4. No quotes around the key
5. Restart application

#### 3. Docker Not Running

**Error**: `Cannot connect to the Docker daemon`

**Solution**:
- **Windows/Mac**: Start Docker Desktop
- **Linux**: `sudo systemctl start docker`
- Verify: `docker info`

#### 4. Permission Denied (Linux)

**Error**: `Permission denied while trying to connect to Docker daemon`

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in
# Verify
docker ps
```

#### 5. Module Not Found

**Error**: `ModuleNotFoundError: No module named 'langchain'`

**Solution**:
```bash
# Reinstall dependencies
pip install -r Agent/requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
pip install -r Agent/requirements.txt
```

#### 6. Knowledge Base Empty

**Warning**: `No documents found in knowledge_base/`

**Solution**:
```bash
# Add PDF files
cp /path/to/pdfs/*.pdf Agent/knowledge_base/

# Or create samples
python Agent/setup_knowledge_base.py sample

# Index them
python Agent/setup_knowledge_base.py index
```

#### 7. Container Cleanup Issues

**Error**: Containers not being removed

**Solution**:
```bash
# List containers
docker ps -a | grep kai-sandbox

# Remove manually
docker ps -a | grep kai-sandbox | awk '{print $1}' | xargs docker rm -f

# Or remove all stopped containers
docker container prune -f
```

#### 8. Port Already in Use

**Error**: `Address already in use: 8501`

**Solution**:
```bash
# Find process using port
# Windows
netstat -ano | findstr :8501

# Linux/Mac
lsof -i :8501

# Kill the process or use different port
```

### Debug Mode

Enable verbose logging:

1. Edit `Agent/agent/config.py`:
   ```python
   LOG_LEVEL = "DEBUG"
   AGENT_VERBOSE = True
   ```

2. Check logs:
   ```bash
   # Windows
   type Agent\logs\agent.log

   # Linux/Mac
   tail -f Agent/logs/agent.log
   ```

### Getting Help

1. **Check Logs**: `Agent/logs/agent.log`
2. **Run Validation**: `python Agent/validate_config.py`
3. **Check Documentation**: `Agent/README.md`
4. **Test Components**: Run individual test files

## Production Deployment

### Security Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] API keys are not committed to version control
- [ ] `.env` file has secure permissions (600 on Unix)
- [ ] Docker containers run as unprivileged user
- [ ] Network isolation is enabled
- [ ] Resource limits are configured
- [ ] Logging is configured properly
- [ ] Error messages don't expose sensitive data

### Performance Optimization

#### 1. Knowledge Base

```python
# In Agent/agent/config.py
CHUNK_SIZE = 1500  # Larger chunks for better context
CHUNK_OVERLAP = 200  # More overlap for better retrieval
SIMILARITY_SEARCH_K = 5  # More results
```

#### 2. Docker

```python
# In Agent/agent/config.py
DOCKER_TIMEOUT_PYTHON = 60  # Longer timeout for complex code
DOCKER_MEMORY_LIMIT = "1g"  # Increase memory limit
```

#### 3. Caching

The knowledge base index is automatically cached. To rebuild:

```bash
python Agent/setup_knowledge_base.py rebuild
```

### Monitoring

#### Log Monitoring

```bash
# Tail logs in real-time
tail -f Agent/logs/agent.log

# Search for errors
grep ERROR Agent/logs/agent.log

# Search for specific task
grep "task_id" Agent/logs/agent.log
```

#### Docker Monitoring

```bash
# List running containers
docker ps | grep kai-sandbox

# Check container stats
docker stats

# View container logs
docker logs <container_id>
```

#### API Usage Monitoring

Monitor API usage in respective dashboards:
- OpenAI: [platform.openai.com/usage](https://platform.openai.com/usage)
- Tavily: Check your dashboard
- Twilio: [console.twilio.com](https://console.twilio.com/)

### Backup and Recovery

#### Backup Knowledge Base

```bash
# Backup knowledge base
tar -czf kb_backup_$(date +%Y%m%d).tar.gz Agent/knowledge_base/

# Backup FAISS index
tar -czf index_backup_$(date +%Y%m%d).tar.gz Agent/faiss_index/
```

#### Restore Knowledge Base

```bash
# Restore knowledge base
tar -xzf kb_backup_20240115.tar.gz

# Rebuild index
python Agent/setup_knowledge_base.py rebuild
```

### Scaling

#### Horizontal Scaling

For multiple agent instances:

1. Use separate `.env` files per instance
2. Use different Docker image tags
3. Implement load balancing
4. Use shared knowledge base storage

#### Vertical Scaling

Increase resources:

```python
# In Agent/agent/config.py
DOCKER_MEMORY_LIMIT = "2g"
DOCKER_CPU_QUOTA = 100000  # 100% of one CPU
```

## Maintenance

### Regular Tasks

#### Daily

- [ ] Check logs for errors
- [ ] Monitor API usage
- [ ] Check Docker container cleanup

#### Weekly

- [ ] Review agent performance
- [ ] Update knowledge base documents
- [ ] Check for security updates

#### Monthly

- [ ] Update Python dependencies
- [ ] Rebuild Docker images
- [ ] Rotate API keys
- [ ] Review and optimize configuration

### Updates

#### Update Python Dependencies

```bash
# Update all packages
pip install --upgrade -r Agent/requirements.txt

# Or update specific package
pip install --upgrade langchain
```

#### Update Docker Image

```bash
# Rebuild with latest base image
docker build --no-cache -t kai_agent_sandbox -f Agent/sandbox/Dockerfile Agent/sandbox/
```

#### Update Knowledge Base

```bash
# Add new documents
cp /path/to/new/docs/*.pdf Agent/knowledge_base/

# Rebuild index
python Agent/setup_knowledge_base.py rebuild
```

### Health Checks

Create a health check script:

```python
# health_check.py
import sys
from Agent.validate_config import run_validation

if __name__ == "__main__":
    passed = run_validation(verbose=False)
    sys.exit(0 if passed else 1)
```

Run periodically:

```bash
# Linux cron job (every hour)
0 * * * * /usr/bin/python /path/to/health_check.py
```

## Appendix

### Directory Structure

```
Agent/
├── README.md                    # Main documentation
├── DEPLOYMENT_GUIDE.md          # This file
├── requirements.txt             # Python dependencies
├── install.py                   # Installation script
├── setup_knowledge_base.py      # KB setup script
├── validate_config.py           # Validation script
├── agent/
│   ├── agent_core.py           # Agent orchestration
│   ├── agent_ui.py             # Streamlit UI
│   ├── config.py               # Configuration
│   ├── errors.py               # Custom exceptions
│   ├── logging_config.py       # Logging setup
│   ├── security.py             # Security utilities
│   └── tools/                  # Agent tools
├── sandbox/
│   ├── Dockerfile              # Sandbox image
│   ├── requirements.txt        # Sandbox packages
│   ├── build.sh                # Build script (Linux/Mac)
│   └── build.ps1               # Build script (Windows)
├── knowledge_base/             # PDF documents
├── agent_workspace/            # Agent file operations
├── logs/                       # Agent logs
└── tests/                      # Test files
```

### Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (required) |
| `TAVILY_API_KEY` | - | Tavily search API key |
| `TWILIO_ACCOUNT_SID` | - | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | - | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | - | Twilio phone number |
| `ELEVEN_LABS_API_KEY` | - | ElevenLabs API key |
| `LLM_MODEL` | `gpt-4` | OpenAI model to use |
| `LLM_TEMPERATURE` | `0.7` | LLM temperature (0-1) |
| `DOCKER_TIMEOUT_PYTHON` | `30` | Python execution timeout (s) |
| `DOCKER_TIMEOUT_TERMINAL` | `120` | Terminal command timeout (s) |
| `CHUNK_SIZE` | `1000` | Knowledge base chunk size |
| `CHUNK_OVERLAP` | `100` | Chunk overlap size |
| `SIMILARITY_SEARCH_K` | `3` | Number of search results |
| `LOG_LEVEL` | `INFO` | Logging level |
| `AGENT_VERBOSE` | `True` | Show agent reasoning |

### Useful Commands

```bash
# Installation
python Agent/install.py

# Validation
python Agent/validate_config.py

# Knowledge Base
python Agent/setup_knowledge_base.py init
python Agent/setup_knowledge_base.py index
python Agent/setup_knowledge_base.py verify
python Agent/setup_knowledge_base.py rebuild

# Docker
docker build -t kai_agent_sandbox -f Agent/sandbox/Dockerfile Agent/sandbox/
docker images | grep kai_agent_sandbox
docker ps | grep kai-sandbox
docker container prune -f

# Testing
pytest Agent/tests/ -v
python Agent/test_agent_core.py
python Agent/test_execution_tools.py

# Logs
tail -f Agent/logs/agent.log
grep ERROR Agent/logs/agent.log
```

### Support Resources

- **Documentation**: `Agent/README.md`
- **Quick Start**: `Agent/AGENT_CORE_QUICK_START.md`
- **Security Guide**: `Agent/API_KEY_SECURITY_GUIDE.md`
- **Logging Guide**: `Agent/LOGGING_QUICK_REFERENCE.md`
- **Sandbox Guide**: `Agent/sandbox/README.md`

---

**Last Updated**: 2024-01-15  
**Version**: 1.0.0
