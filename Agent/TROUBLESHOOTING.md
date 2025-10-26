# KAI Agent - Troubleshooting Guide

## Quick Diagnostics

Run the validation script first:

```bash
python Agent/validate_config.py
```

This will identify most common issues.

## Common Issues

### 1. Docker Issues

#### Docker Image Not Found

**Error**: `docker.errors.ImageNotFound: 404 Client Error for url: http+docker://localhost/v1.43/images/kai_agent_sandbox/json`

**Cause**: Docker sandbox image hasn't been built

**Solution**:
```bash
# Build the image
docker build -t kai_agent_sandbox -f Agent/sandbox/Dockerfile Agent/sandbox/

# Verify
docker images | grep kai_agent_sandbox
```

#### Docker Not Running

**Error**: `Cannot connect to the Docker daemon at unix:///var/run/docker.sock`

**Cause**: Docker daemon is not running

**Solution**:
- **Windows/Mac**: Start Docker Desktop
- **Linux**: `sudo systemctl start docker`
- Verify: `docker info`

#### Permission Denied (Linux)

**Error**: `Got permission denied while trying to connect to the Docker daemon socket`

**Cause**: User not in docker group

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in
# Verify
docker ps
```

#### Container Cleanup Issues

**Error**: Containers not being removed automatically

**Cause**: Docker cleanup failed

**Solution**:
```bash
# List all kai-sandbox containers
docker ps -a | grep kai-sandbox

# Remove them manually
docker ps -a | grep kai-sandbox | awk '{print $1}' | xargs docker rm -f

# Or remove all stopped containers
docker container prune -f
```

### 2. API Key Issues

#### API Key Not Found

**Error**: `ConfigurationError: OPENAI_API_KEY not found in environment`

**Cause**: .env file missing or API key not set

**Solution**:
1. Check `.env` file exists in project root (not in Agent/)
2. Verify format:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
3. No spaces around `=`
4. No quotes around the key
5. Restart application

#### Invalid API Key Format

**Error**: `AuthenticationError: Incorrect API key provided`

**Cause**: API key is invalid or malformed

**Solution**:
1. Check key starts with `sk-`
2. Verify key is complete (no truncation)
3. Get new key from [platform.openai.com](https://platform.openai.com/api-keys)
4. Update `.env` file

#### API Rate Limit

**Error**: `RateLimitError: Rate limit reached for requests`

**Cause**: Too many API requests

**Solution**:
1. Wait a few minutes
2. Check usage at [platform.openai.com/usage](https://platform.openai.com/usage)
3. Upgrade plan if needed
4. Implement request throttling

### 3. Installation Issues

#### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'langchain'`

**Cause**: Dependencies not installed

**Solution**:
```bash
# Reinstall dependencies
cd Agent
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

#### Python Version Too Old

**Error**: `Python 3.11 or higher is required`

**Cause**: Python version is too old

**Solution**:
1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Install and verify: `python --version`
3. Reinstall dependencies

#### Pip Install Fails

**Error**: `ERROR: Could not install packages due to an OSError`

**Cause**: Permission issues or disk space

**Solution**:
```bash
# Try user installation
pip install --user -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Check disk space
df -h  # Linux/Mac
```

### 4. Knowledge Base Issues

#### Knowledge Base Empty

**Warning**: `No documents found in knowledge_base/`

**Cause**: No PDF files in knowledge base directory

**Solution**:
```bash
# Create directory if needed
mkdir -p Agent/knowledge_base

# Add PDF files
cp /path/to/your/pdfs/*.pdf Agent/knowledge_base/

# Or create samples
python Agent/setup_knowledge_base.py sample

# Index documents
python Agent/setup_knowledge_base.py index
```

#### FAISS Index Error

**Error**: `RuntimeError: Error in faiss::FileIOReader::FileIOReader`

**Cause**: Corrupted FAISS index

**Solution**:
```bash
# Rebuild index
python Agent/setup_knowledge_base.py rebuild

# Or manually delete and rebuild
rm -rf Agent/faiss_index
python Agent/setup_knowledge_base.py index
```

#### PDF Loading Error

**Error**: `PdfReadError: EOF marker not found`

**Cause**: Corrupted or invalid PDF file

**Solution**:
1. Check PDF file is valid
2. Try opening in PDF reader
3. Remove corrupted file
4. Rebuild index

### 5. Execution Issues

#### Code Execution Timeout

**Error**: `TimeoutError: Container execution timed out after 30 seconds`

**Cause**: Code takes too long to execute

**Solution**:
1. Optimize your code
2. Increase timeout in `Agent/agent/config.py`:
   ```python
   DOCKER_TIMEOUT_PYTHON = 60  # Increase to 60 seconds
   ```
3. Restart application

#### Sandbox Network Error

**Error**: `requests.exceptions.ConnectionError: Failed to establish a new connection`

**Cause**: Network is disabled in sandbox (by design)

**Solution**:
- Network is disabled for security
- If you need network access, modify `execution_tools.py`:
  ```python
  # In execute_python_code_in_sandbox
  network_disabled=False  # Enable network
  ```

#### Memory Error in Sandbox

**Error**: `MemoryError: Unable to allocate array`

**Cause**: Code uses too much memory

**Solution**:
1. Optimize code to use less memory
2. Increase memory limit in `Agent/agent/config.py`:
   ```python
   DOCKER_MEMORY_LIMIT = "1g"  # Increase to 1GB
   ```

### 6. UI Issues

#### Port Already in Use

**Error**: `OSError: [Errno 98] Address already in use: 8501`

**Cause**: Another process is using the port

**Solution**:
```bash
# Find process using port
# Windows
netstat -ano | findstr :8501

# Linux/Mac
lsof -i :8501

# Kill the process
# Windows
taskkill /PID <pid> /F

# Linux/Mac
kill -9 <pid>
```

#### Streamlit Not Found

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Cause**: Streamlit not installed

**Solution**:
```bash
pip install streamlit
```

#### UI Not Updating

**Issue**: Agent output not showing in real-time

**Cause**: Streamlit caching or state issues

**Solution**:
1. Refresh the page (F5)
2. Clear Streamlit cache: `Ctrl+Shift+R`
3. Restart application

### 7. Performance Issues

#### Slow Agent Response

**Issue**: Agent takes too long to respond

**Possible Causes & Solutions**:

1. **Large Knowledge Base**:
   ```bash
   # Optimize chunk size
   # Edit Agent/agent/config.py
   CHUNK_SIZE = 1500
   CHUNK_OVERLAP = 200
   ```

2. **Slow API Calls**:
   - Check internet connection
   - Check OpenAI status: [status.openai.com](https://status.openai.com/)
   - Try different model: `LLM_MODEL = "gpt-3.5-turbo"`

3. **Docker Overhead**:
   - Ensure Docker has enough resources
   - Increase Docker memory in Docker Desktop settings

#### High Memory Usage

**Issue**: Application uses too much memory

**Solution**:
1. Limit knowledge base size (< 1000 PDFs)
2. Clear conversation memory periodically
3. Restart application regularly
4. Monitor with: `docker stats`

### 8. Security Issues

#### .env File Exposed

**Warning**: `.env file is readable by others`

**Cause**: Incorrect file permissions

**Solution** (Linux/Mac):
```bash
chmod 600 .env
```

#### API Key in Logs

**Issue**: API key appears in logs

**Cause**: Logging configuration issue

**Solution**:
1. Check `Agent/agent/logging_config.py`
2. Ensure sensitive data is masked
3. Run security audit:
   ```bash
   python Agent/audit_api_key_security.py
   ```

### 9. Testing Issues

#### Tests Fail

**Error**: `pytest: command not found`

**Cause**: pytest not installed

**Solution**:
```bash
pip install pytest
pytest Agent/tests/ -v
```

#### Import Errors in Tests

**Error**: `ModuleNotFoundError` in tests

**Cause**: Python path issues

**Solution**:
```bash
# Run from project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest Agent/tests/ -v
```

## Debug Mode

Enable detailed logging:

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

## Diagnostic Commands

### Check Python Environment

```bash
python --version
pip list | grep langchain
pip list | grep docker
pip list | grep faiss
```

### Check Docker

```bash
docker --version
docker info
docker images | grep kai_agent_sandbox
docker ps -a | grep kai-sandbox
```

### Check Files

```bash
# Check .env exists
ls -la .env

# Check knowledge base
ls -la Agent/knowledge_base/

# Check FAISS index
ls -la Agent/faiss_index/
```

### Check Logs

```bash
# View recent logs
tail -n 50 Agent/logs/agent.log

# Search for errors
grep ERROR Agent/logs/agent.log

# Search for specific task
grep "task_id" Agent/logs/agent.log
```

## Still Having Issues?

1. **Run Full Validation**:
   ```bash
   python Agent/validate_config.py
   ```

2. **Check All Logs**:
   ```bash
   cat Agent/logs/agent.log
   ```

3. **Test Components Individually**:
   ```bash
   python Agent/test_agent_core.py
   python Agent/test_execution_tools.py
   python Agent/test_knowledge_search.py
   ```

4. **Reinstall Everything**:
   ```bash
   # Remove virtual environment
   rm -rf venv

   # Reinstall
   python -m venv venv
   source venv/bin/activate
   pip install -r Agent/requirements.txt

   # Rebuild Docker
   docker build -t kai_agent_sandbox -f Agent/sandbox/Dockerfile Agent/sandbox/
   ```

5. **Check Documentation**:
   - `Agent/README.md` - Main documentation
   - `Agent/DEPLOYMENT_GUIDE.md` - Deployment guide
   - `Agent/AGENT_CORE_QUICK_START.md` - Agent core guide

## Error Code Reference

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `ConfigurationError` | Missing or invalid configuration | Check `.env` file |
| `DockerError` | Docker-related issue | Check Docker is running |
| `APIError` | External API issue | Check API keys and status |
| `ExecutionError` | Code execution failed | Check code syntax and logic |
| `TimeoutError` | Operation timed out | Increase timeout or optimize code |
| `MemoryError` | Out of memory | Increase limits or optimize code |
| `AuthenticationError` | Invalid API key | Check API key is correct |
| `RateLimitError` | API rate limit reached | Wait or upgrade plan |

---

**Last Updated**: 2024-01-15  
**Version**: 1.0.0
