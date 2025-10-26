# KAI Agent - User Troubleshooting Guide

## Quick Start Troubleshooting

This guide helps you solve common problems when using the KAI Agent. For technical details, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Table of Contents

1. [Agent Won't Start](#agent-wont-start)
2. [Agent Not Responding](#agent-not-responding)
3. [Code Execution Errors](#code-execution-errors)
4. [Knowledge Base Issues](#knowledge-base-issues)
5. [Unexpected Results](#unexpected-results)
6. [Performance Problems](#performance-problems)

## Agent Won't Start

### Problem: "API Keys Missing" Error

**What you see:**
```
⚠️ Missing API Keys:
- OPENAI_API_KEY
```

**Quick Fix:**
1. Find the `.env` file in your project folder
2. Open it with a text editor
3. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
4. Save and restart the application

**Where to get API keys:**
- OpenAI: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Tavily: [tavily.com](https://tavily.com/)
- ElevenLabs: [elevenlabs.io](https://elevenlabs.io/)

### Problem: "Docker Not Running" Error

**What you see:**
```
❌ Docker Error: Cannot connect to Docker daemon
```

**Quick Fix:**
1. **Windows/Mac**: Open Docker Desktop application
2. Wait for Docker to start (whale icon in system tray)
3. Refresh the agent page

**Don't have Docker?**
- Download from [docker.com](https://www.docker.com/products/docker-desktop/)
- Install and restart your computer
- Start Docker Desktop

### Problem: "Docker Image Not Found"

**What you see:**
```
❌ Docker image 'kai_agent_sandbox' not found
```

**Quick Fix:**
1. Open a terminal/command prompt
2. Navigate to your project folder
3. Run:
   ```bash
   python Agent/build_sandbox.py
   ```
4. Wait for the build to complete (2-5 minutes)
5. Refresh the agent page

## Agent Not Responding

### Problem: Agent Stuck on "Thinking..."

**Possible Causes:**

1. **Slow Internet Connection**
   - Check your internet connection
   - Try a simpler task first
   - Wait a bit longer (complex tasks take time)

2. **API Rate Limit**
   - You may have exceeded your OpenAI usage limit
   - Check usage at [platform.openai.com/usage](https://platform.openai.com/usage)
   - Wait a few minutes and try again

3. **Task Too Complex**
   - Break down your task into smaller steps
   - Try a simpler version first

**Quick Fix:**
1. Refresh the page (F5)
2. Try a simpler task:
   ```
   Was ist Photovoltaik?
   ```
3. If it works, gradually increase complexity

### Problem: No Response at All

**Quick Fix:**
1. Check the browser console for errors (F12)
2. Refresh the page
3. Restart the application
4. Check if Docker is running

## Code Execution Errors

### Problem: "Timeout Error"

**What you see:**
```
❌ TimeoutError: Container execution timed out after 30 seconds
```

**What it means:**
Your code is taking too long to run.

**Quick Fix:**
1. Simplify your code
2. Remove infinite loops
3. Reduce data size
4. Ask the agent to optimize the code:
   ```
   Der Code ist zu langsam. Bitte optimiere ihn.
   ```

### Problem: "Syntax Error" in Generated Code

**What you see:**
```
SyntaxError: invalid syntax
```

**Quick Fix:**
1. Copy the error message
2. Ask the agent to fix it:
   ```
   Der Code hat einen Syntax-Fehler. Bitte behebe ihn:
   [paste error message]
   ```

### Problem: "Module Not Found" in Sandbox

**What you see:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Quick Fix:**
Ask the agent to install the package first:
```
Installiere pandas im Sandbox und führe dann den Code aus
```

## Knowledge Base Issues

### Problem: "No Documents Found" Warning

**What you see:**
```
⚠️ Warning: No documents found in knowledge_base/
```

**What it means:**
The agent has no domain-specific knowledge to search.

**Quick Fix:**
1. Add PDF documents to `Agent/knowledge_base/` folder
2. Run:
   ```bash
   python Agent/setup_knowledge_base.py
   ```
3. Restart the application

**Don't have documents?**
The agent can still work using web search and general knowledge.

### Problem: Agent Can't Find Information

**What you see:**
Agent says "I couldn't find information about..."

**Quick Fix:**
1. **Rephrase your question:**
   - ❌ "Sag mir was über Solar"
   - ✅ "Was sind die Vorteile von Photovoltaik-Anlagen?"

2. **Be more specific:**
   - ❌ "Wie funktioniert das?"
   - ✅ "Wie funktioniert eine Luft-Wasser-Wärmepumpe?"

3. **Check if information is in knowledge base:**
   - List your PDF files in `Agent/knowledge_base/`
   - Make sure they contain relevant information

## Unexpected Results

### Problem: Agent Gives Wrong Answer

**Possible Causes:**
1. Question was unclear
2. Information not in knowledge base
3. Agent misunderstood the context

**Quick Fix:**
1. **Clarify your question:**
   ```
   Ich meinte: [rephrase more clearly]
   ```

2. **Provide context:**
   ```
   Kontext: Ich plane eine 10 kWp PV-Anlage in München.
   Frage: Wie hoch ist der erwartete Jahresertrag?
   ```

3. **Ask for sources:**
   ```
   Woher hast du diese Information? Kannst du die Quelle nennen?
   ```

### Problem: Generated Code Doesn't Work

**Quick Fix:**
1. **Review the code carefully**
2. **Test in small steps**
3. **Ask for corrections:**
   ```
   Der Code funktioniert nicht wie erwartet. 
   Erwartetes Verhalten: [describe]
   Tatsächliches Verhalten: [describe]
   Bitte korrigiere den Code.
   ```

### Problem: Agent Ignores Instructions

**Possible Causes:**
1. Instructions were unclear
2. Instructions conflicted with each other
3. Task was too complex

**Quick Fix:**
1. **Simplify instructions:**
   - Break into steps
   - One requirement at a time

2. **Be explicit:**
   ```
   Erstelle eine Funktion mit GENAU folgenden Anforderungen:
   1. Name: calculate_roi
   2. Parameter: investment (float), savings (float)
   3. Rückgabe: float (Jahre bis ROI)
   4. Fehlerbehandlung: ValueError bei negativen Werten
   ```

## Performance Problems

### Problem: Agent is Very Slow

**Possible Causes:**
1. Large knowledge base
2. Complex task
3. Slow internet connection
4. Docker resource limits

**Quick Fix:**
1. **For knowledge base:**
   - Remove unnecessary PDF files
   - Keep only relevant documents

2. **For complex tasks:**
   - Break into smaller steps
   - Process one step at a time

3. **For Docker:**
   - Close other applications
   - Increase Docker memory in Docker Desktop settings
   - Restart Docker

### Problem: High Memory Usage

**Quick Fix:**
1. Restart the application
2. Close other browser tabs
3. Restart Docker Desktop
4. Reduce knowledge base size

## Common Error Messages Explained

### "ConfigurationError"
**Meaning:** Something is wrong with your setup (usually API keys)
**Fix:** Check your `.env` file

### "DockerError"
**Meaning:** Problem with Docker
**Fix:** Make sure Docker Desktop is running

### "AuthenticationError"
**Meaning:** Your API key is invalid
**Fix:** Check your API key is correct and active

### "RateLimitError"
**Meaning:** You've made too many API requests
**Fix:** Wait a few minutes, then try again

### "TimeoutError"
**Meaning:** Operation took too long
**Fix:** Simplify your task or optimize your code

## Step-by-Step Troubleshooting

If you're stuck, follow these steps:

### Step 1: Check the Basics
- [ ] Is Docker running?
- [ ] Are API keys configured?
- [ ] Is your internet working?
- [ ] Did you restart after making changes?

### Step 2: Try a Simple Task
Try this simple task:
```
Schreibe eine Funktion, die 1 + 1 berechnet
```

If this works, your setup is fine. The problem is with your specific task.

### Step 3: Simplify Your Task
- Break complex tasks into steps
- Remove optional requirements
- Test with minimal example

### Step 4: Check Logs
Look for error messages in:
- The agent interface
- Browser console (F12)
- `Agent/logs/agent.log` file

### Step 5: Run Validation
```bash
python Agent/validate_config.py
```

This will check your setup and report problems.

### Step 6: Restart Everything
1. Close the application
2. Restart Docker Desktop
3. Restart the application
4. Try again

## Getting Help

### Before Asking for Help

Collect this information:
1. What were you trying to do?
2. What did you expect to happen?
3. What actually happened?
4. Any error messages (copy the full text)
5. What have you tried already?

### Where to Get Help

1. **Check Documentation:**
   - [Basic Usage Tutorial](BASIC_USAGE_TUTORIAL.md)
   - [Advanced Features Guide](ADVANCED_FEATURES_GUIDE.md)
   - [Technical Troubleshooting](TROUBLESHOOTING.md)

2. **Run Diagnostics:**
   ```bash
   python Agent/validate_config.py
   ```

3. **Check Logs:**
   ```bash
   # Windows
   type Agent\logs\agent.log
   
   # Mac/Linux
   cat Agent/logs/agent.log
   ```

## Prevention Tips

### Avoid Common Problems

1. **Keep Docker Running**
   - Start Docker Desktop when you start your computer
   - Don't close it while using the agent

2. **Maintain Your .env File**
   - Keep API keys up to date
   - Don't share your .env file
   - Back it up securely

3. **Organize Your Workspace**
   - Keep `agent_workspace/` clean
   - Delete old test files
   - Use clear file names

4. **Update Regularly**
   - Keep Docker updated
   - Update Python packages periodically
   - Refresh knowledge base documents

5. **Start Simple**
   - Test with simple tasks first
   - Build complexity gradually
   - Save working examples

## Quick Reference

### Most Common Issues

| Problem | Quick Fix |
|---------|-----------|
| API key missing | Add to `.env` file |
| Docker not running | Start Docker Desktop |
| Agent not responding | Refresh page, check internet |
| Code timeout | Simplify code |
| Wrong answer | Rephrase question, add context |
| Slow performance | Reduce knowledge base size |

### Essential Commands

```bash
# Validate setup
python Agent/validate_config.py

# Build Docker image
python Agent/build_sandbox.py

# Setup knowledge base
python Agent/setup_knowledge_base.py

# Check Docker
docker ps

# View logs
cat Agent/logs/agent.log
```

## Still Stuck?

If you've tried everything and still have problems:

1. Check the [Technical Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review the [Deployment Guide](DEPLOYMENT_GUIDE.md)
3. Run all validation tests:
   ```bash
   python Agent/run_final_validation.py
   ```

Remember: Most problems have simple solutions. Take a deep breath, check the basics, and try again! 🚀
