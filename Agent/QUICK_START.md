# KAI Agent - Quick Start Guide

Get up and running with the KAI Agent in 5 minutes!

## Prerequisites

- Python 3.11+
- Docker (installed and running)
- OpenAI API Key

## Installation (5 Steps)

### 1. Install Dependencies

```bash
cd Agent
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy example file
cp ../.env.example ../.env

# Edit and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 3. Build Docker Sandbox

```bash
docker build -t kai_agent_sandbox -f sandbox/Dockerfile sandbox/
```

### 4. Verify Installation

```bash
python validate_config.py
```

### 5. Start Using

1. Run your main application
2. Navigate to **A.G.E.N.T.** menu
3. Enter a task
4. Click "Start Agent"

## First Task

Try this simple task:

```
Schreibe eine Python-Funktion, die zwei Zahlen addiert. 
Schreibe auch einen Test dafür und führe ihn aus.
```

The agent will:
1. Write the function
2. Create a test
3. Execute the test in the sandbox
4. Show you the results

## What's Next?

- **Add Knowledge Base**: Place PDFs in `knowledge_base/` directory
- **Read Documentation**: Check `README.md` for detailed info
- **Try Advanced Tasks**: Explore telephony, web search, and more

## Need Help?

- Run: `python validate_config.py`
- Check: `logs/agent.log`
- Read: `DEPLOYMENT_GUIDE.md`

## Common Issues

**Docker not found?**
```bash
# Install Docker Desktop
# Windows/Mac: https://www.docker.com/products/docker-desktop/
```

**API key error?**
```bash
# Check .env file exists and has:
# OPENAI_API_KEY=sk-...
```

**Module not found?**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

That's it! You're ready to use the KAI Agent. 🚀
