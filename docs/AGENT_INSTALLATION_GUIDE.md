# KAI Agent Installation Guide

## Quick Start

Follow these steps to install and configure the KAI Agent integration:

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required dependencies including:

- LangChain framework (langchain, langchain-openai, langchain-community)
- Vector database (faiss-cpu)
- Docker SDK (docker)
- API clients (tavily-python, twilio, elevenlabs)
- Supporting libraries (python-dotenv, pypdf, websockets)

### 2. Install Docker

The agent requires Docker for secure code execution:

**Windows:**

1. Download Docker Desktop from <https://www.docker.com/products/docker-desktop>
2. Install and start Docker Desktop
3. Verify: Open PowerShell and run `docker --version`

**Linux:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Verify
docker --version
```

**macOS:**

1. Download Docker Desktop from <https://www.docker.com/products/docker-desktop>
2. Install and start Docker Desktop
3. Verify: Open Terminal and run `docker --version`

### 3. Build Docker Sandbox

```bash
cd Agent/sandbox
docker build -t kai-agent-sandbox .
cd ../..
```

### 4. Configure API Keys

1. Copy the example environment file:

   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your API keys:

   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. Optional: Add keys for additional features:

   ```
   TAVILY_API_KEY=tvly-your-key-here
   TWILIO_ACCOUNT_SID=ACyour-sid-here
   TWILIO_AUTH_TOKEN=your-token-here
   TWILIO_PHONE_NUMBER=+1234567890
   ELEVEN_LABS_API_KEY=your-key-here
   ```

### 5. Verify Installation

Run the verification script:

```bash
python test_agent_dependencies.py
```

You should see:

- ✓ All core dependencies installed
- ✓ Docker daemon running
- ✓ Required API keys configured

### 6. Test the Agent

Run the demo application:

```bash
cd Agent
streamlit run demo_agent_ui.py
```

Or integrate with the main application by accessing the "A.G.E.N.T." menu.

## Detailed Installation Steps

### Python Environment

**Recommended Setup:**

```bash
# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Dependency Installation Issues

**Problem: FAISS installation fails**

Solution 1 - Install build tools:

```bash
# Windows: Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Linux:
sudo apt-get install build-essential

# macOS:
xcode-select --install
```

Solution 2 - Use conda:

```bash
conda install -c conda-forge faiss-cpu
```

**Problem: Docker SDK import fails**

Ensure Docker Desktop/Engine is installed and running:

```bash
# Check Docker status
docker ps

# If not running, start Docker Desktop (Windows/macOS)
# Or start Docker service (Linux):
sudo systemctl start docker
```

**Problem: LangChain version conflicts**

Update all LangChain packages together:

```bash
pip install --upgrade langchain langchain-openai langchain-community
```

### API Key Setup

#### OpenAI API Key (Required)

1. Go to <https://platform.openai.com/api-keys>
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and add to `.env`:

   ```
   OPENAI_API_KEY=sk-...
   ```

#### Tavily API Key (Optional - Web Search)

1. Go to <https://tavily.com/>
2. Sign up for an account
3. Get your API key from the dashboard
4. Add to `.env`:

   ```
   TAVILY_API_KEY=tvly-...
   ```

#### Twilio Credentials (Optional - Telephony)

1. Go to <https://www.twilio.com/>
2. Sign up and verify your account
3. Get credentials from console:
   - Account SID
   - Auth Token
   - Phone Number
4. Add to `.env`:

   ```
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_PHONE_NUMBER=+1...
   ```

#### ElevenLabs API Key (Optional - Voice Synthesis)

1. Go to <https://elevenlabs.io/>
2. Sign up for an account
3. Get your API key from settings
4. Add to `.env`:

   ```
   ELEVEN_LABS_API_KEY=...
   ```

## Verification Checklist

Use this checklist to ensure everything is set up correctly:

- [ ] Python 3.10+ installed
- [ ] All dependencies installed (`pip list` shows langchain, docker, faiss, etc.)
- [ ] Docker installed and running (`docker ps` works)
- [ ] Docker sandbox image built (`docker images | grep kai-agent-sandbox`)
- [ ] `.env` file created with OPENAI_API_KEY
- [ ] Test script passes (`python test_agent_dependencies.py`)
- [ ] Agent UI loads without errors
- [ ] Knowledge base directory exists (`knowledge_base/`)

## Troubleshooting

### "Docker daemon not running"

**Symptoms:**

- Error when starting agent
- "Cannot connect to Docker daemon" message

**Solutions:**

1. Start Docker Desktop (Windows/macOS)
2. Start Docker service (Linux): `sudo systemctl start docker`
3. Check Docker is running: `docker ps`

### "OpenAI API key not found"

**Symptoms:**

- Agent fails to start
- "API key not configured" error

**Solutions:**

1. Ensure `.env` file exists in project root
2. Check `.env` contains `OPENAI_API_KEY=sk-...`
3. Restart the application after adding the key

### "Module not found" errors

**Symptoms:**

- Import errors when starting agent
- "No module named 'langchain'" or similar

**Solutions:**

1. Ensure virtual environment is activated (if using one)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.10+)

### FAISS index creation fails

**Symptoms:**

- Error when loading knowledge base
- "Cannot create FAISS index" message

**Solutions:**

1. Check available memory (FAISS requires RAM)
2. Reduce document count in knowledge_base/
3. Clear existing index: delete `faiss_index/` directory

### Docker sandbox timeout

**Symptoms:**

- Code execution takes too long
- "Container timeout" error

**Solutions:**

1. Increase timeout in execution_tools.py
2. Optimize code being executed
3. Check Docker resource limits in Docker Desktop settings

## Updating Dependencies

### Regular Updates

Update to latest compatible versions:

```bash
pip install --upgrade langchain langchain-openai langchain-community
pip install --upgrade tavily-python twilio elevenlabs
```

### Security Updates

Check for security advisories:

```bash
pip list --outdated
pip install --upgrade <package-name>
```

### Version Pinning for Production

For production deployments, pin exact versions in requirements.txt:

```
langchain==0.3.27
langchain-openai==0.3.0
langchain-community==0.3.21
docker==7.1.0
faiss-cpu==1.12.0
```

## Uninstallation

To remove agent dependencies:

```bash
# Remove agent-specific packages
pip uninstall langchain langchain-openai langchain-community
pip uninstall tavily-python twilio elevenlabs faiss-cpu

# Remove Docker image
docker rmi kai-agent-sandbox

# Remove agent files
# (Keep this manual to avoid accidental deletion)
```

## Next Steps

After successful installation:

1. **Add Knowledge Base Documents**
   - Place PDF files in `knowledge_base/` directory
   - Agent will automatically index them on first run

2. **Test Basic Functionality**
   - Open agent UI
   - Try a simple task: "Explain photovoltaic systems"
   - Verify agent can search knowledge base

3. **Test Code Execution**
   - Try: "Write a Python function to calculate solar panel output"
   - Verify Docker sandbox executes code

4. **Explore Advanced Features**
   - Test web search (requires Tavily API key)
   - Test telephony simulation (requires Twilio/ElevenLabs keys)
   - Test project generation

5. **Integrate with Main Application**
   - Access "A.G.E.N.T." menu from main app
   - Test menu switching
   - Verify no interference with existing features

## Support Resources

- **Documentation**: See `AGENT_DEPENDENCIES.md` for detailed dependency info
- **Test Script**: Run `python test_agent_dependencies.py` to diagnose issues
- **Example Config**: See `.env.example` for configuration template
- **Docker Guide**: See `Agent/sandbox/README.md` for sandbox details

## Minimum System Requirements

- **OS**: Windows 10+, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space
- **Docker**: Docker Desktop 4.0+ or Docker Engine 20.10+
- **Internet**: Required for API calls and package installation

## Recommended System Specifications

- **OS**: Windows 11, Ubuntu 22.04, macOS 12+
- **Python**: 3.11
- **RAM**: 16GB
- **Disk**: 10GB free space (for knowledge base and Docker images)
- **CPU**: 4+ cores
- **Docker**: Latest version
- **Internet**: Broadband connection

---

**Installation Complete!** 🎉

You're now ready to use the KAI Agent. Start by running:

```bash
streamlit run Agent/demo_agent_ui.py
```

Or access the agent through the main application's "A.G.E.N.T." menu.
