# KAI Agent - Basic Usage Tutorial

## Welcome to KAI Agent!

KAI (Künstliche Intelligenz) Agent is your AI-powered assistant with dual expertise in renewable energy consulting and software development. This tutorial will guide you through the basics of using the agent.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Your First Task](#your-first-task)
3. [Understanding Agent Responses](#understanding-agent-responses)
4. [Common Use Cases](#common-use-cases)
5. [Tips for Success](#tips-for-success)

## Getting Started

### Accessing the Agent

1. Open the Bokuk2 application
2. Look for the **A.G.E.N.T.** menu option in the main navigation
3. Click on it to open the agent interface

### First-Time Setup Check

When you first access the agent, it will check if all required API keys are configured. If you see any warnings:

- Follow the instructions to add missing keys to your `.env` file
- Restart the application after adding keys
- See the [Installation Guide](AGENT_INSTALLATION_GUIDE.md) for detailed setup instructions

## Your First Task

Let's start with a simple task to get familiar with the agent.

### Example 1: Ask About Photovoltaics

**Task Input:**
```
Was sind die wichtigsten Vorteile von Photovoltaik-Anlagen?
```

**What Happens:**
1. The agent will search its knowledge base for information about photovoltaics
2. You'll see the agent's "thinking process" in real-time
3. The agent will provide a comprehensive answer with specific benefits

**Expected Response:**
The agent will list key benefits such as:
- Cost savings on electricity bills
- Environmental benefits (CO2 reduction)
- Energy independence
- Government incentives
- Long-term investment value

### Example 2: Simple Code Generation

**Task Input:**
```
Schreibe eine Python-Funktion, die prüft, ob eine Zahl eine Primzahl ist.
```

**What Happens:**
1. The agent will generate the code
2. It may write a test first (following TDD principles)
3. You'll see the complete function with documentation

**Expected Response:**
```python
def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    
    Args:
        n: Integer to check
        
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
```

## Understanding Agent Responses

### The Thinking Process

When the agent works on your task, you'll see its reasoning process:

```
🤔 Agent Thinking...

Thought: I need to search the knowledge base for information about photovoltaics
Action: knowledge_base_search
Action Input: "Photovoltaik Vorteile"

Observation: [Search results from knowledge base]

Thought: I now have enough information to answer the question
Final Answer: [Comprehensive response]
```

### Response Components

1. **Intermediate Steps**: Shows what tools the agent used
2. **Final Answer**: The complete response to your task
3. **Generated Files**: If the agent created files, you'll see them listed
4. **Code Blocks**: Syntax-highlighted code with copy buttons

## Common Use Cases

### 1. Knowledge Queries

Ask the agent about renewable energy topics:

```
Wie funktioniert eine Wärmepumpe?
Was ist der Unterschied zwischen monokristallinen und polykristallinen Solarmodulen?
Welche Förderungen gibt es für Photovoltaik in Deutschland?
```

### 2. Quick Calculations

```
Berechne die jährliche Ersparnis einer 10 kWp PV-Anlage bei einem Strompreis von 0,35 €/kWh
```

### 3. Code Generation

```
Erstelle eine Funktion zur Berechnung des ROI einer Solaranlage
Schreibe einen Unit-Test für die Funktion calculate_savings()
```

### 4. File Operations

```
Erstelle eine README.md Datei für ein Python-Projekt zur Solaranlagen-Berechnung
Liste alle Dateien im Workspace auf
```

### 5. Project Scaffolding

```
Generiere eine Flask API Struktur für ein Photovoltaik-Berechnungstool
```

## Tips for Success

### 1. Be Specific

❌ **Vague:** "Schreibe Code"
✅ **Specific:** "Schreibe eine Python-Funktion, die den Ertrag einer PV-Anlage basierend auf kWp und Standort berechnet"

### 2. Break Down Complex Tasks

Instead of:
```
Erstelle eine komplette Webanwendung für Solarberechnungen
```

Try:
```
1. Erstelle die Projektstruktur für eine Flask-App
2. Implementiere die Berechnungslogik
3. Erstelle die API-Endpoints
4. Schreibe Tests
```

### 3. Use the Knowledge Base

The agent has access to domain-specific knowledge about:
- Photovoltaics systems
- Heat pumps
- Energy efficiency
- Economic calculations

Always let the agent search its knowledge base first for accurate information.

### 4. Review Generated Code

While the agent generates high-quality code:
- Always review it before using in production
- Test thoroughly
- Adapt to your specific needs

### 5. Provide Context

If you're working on a multi-step task, provide context:

```
Ich habe bereits eine Funktion calculate_pv_yield() erstellt. 
Jetzt brauche ich eine Funktion, die die Amortisationszeit berechnet.
```

## What to Do If Something Goes Wrong

### Agent Not Responding

1. Check your internet connection
2. Verify API keys are configured correctly
3. Look for error messages in the interface
4. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)

### Unexpected Results

1. Rephrase your task more clearly
2. Break down complex tasks into smaller steps
3. Provide more context or examples

### Docker Errors

If you see Docker-related errors:
1. Ensure Docker is installed and running
2. Check if the sandbox image is built: `docker images | grep kai_agent-sandbox`
3. Rebuild if needed: `python Agent/build_sandbox.py`

## Next Steps

Now that you understand the basics:

1. Try the examples in this tutorial
2. Explore the [Advanced Features Guide](ADVANCED_FEATURES_GUIDE.md)
3. Check out [Example Tasks](EXAMPLE_TASKS.md) for more inspiration
4. Read the [Best Practices Document](BEST_PRACTICES.md)

## Getting Help

- **In-App Help**: Look for tooltips and help icons in the interface
- **Documentation**: Check the `Agent/` directory for detailed guides
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **API Reference**: See [DOCUMENTATION_GUIDE.md](DOCUMENTATION_GUIDE.md)

## Quick Reference Card

| Task Type | Example Command |
|-----------|----------------|
| Knowledge Query | `Was sind die Vorteile von Photovoltaik?` |
| Code Generation | `Schreibe eine Funktion zur Berechnung von X` |
| File Operations | `Erstelle eine README.md Datei` |
| Testing | `Schreibe Tests für die Funktion calculate_roi()` |
| Project Setup | `Generiere eine Flask API Struktur` |
| Calculations | `Berechne den ROI einer 10 kWp Anlage` |

Happy automating! 🚀
