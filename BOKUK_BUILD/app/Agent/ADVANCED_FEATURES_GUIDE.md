# KAI Agent - Advanced Features Guide

## Introduction

This guide covers advanced features and capabilities of the KAI Agent system. If you're new to the agent, start with the [Basic Usage Tutorial](BASIC_USAGE_TUTORIAL.md) first.

## Table of Contents

1. [Multi-Step Workflows](#multi-step-workflows)
2. [Code Execution in Sandbox](#code-execution-in-sandbox)
3. [Knowledge Base Management](#knowledge-base-management)
4. [Telephony Simulation](#telephony-simulation)
5. [Project Generation](#project-generation)
6. [Testing Workflows](#testing-workflows)
7. [Advanced Prompting Techniques](#advanced-prompting-techniques)
8. [Performance Optimization](#performance-optimization)

## Multi-Step Workflows

### Chaining Tasks

The agent maintains conversation memory, allowing you to build on previous interactions:

**Step 1:**
```
Erstelle eine Klasse SolarPanel mit Attributen für Leistung, Hersteller und Preis
```

**Step 2:**
```
Füge eine Methode hinzu, die den Ertrag pro Jahr berechnet
```

**Step 3:**
```
Schreibe Unit-Tests für die SolarPanel Klasse
```

The agent remembers the context from previous steps.

### Complex Consulting Workflow

**Example: Complete Customer Consultation**

```
Ich habe einen Kunden mit einem Jahresverbrauch von 4500 kWh. 
Das Dach hat 50 m² Südausrichtung. 
Erstelle eine vollständige Beratung mit:
1. Empfohlener Anlagengröße
2. Geschätzten Kosten
3. Amortisationszeit
4. CO2-Einsparung
5. Fördermöglichkeiten
```

The agent will:
1. Search knowledge base for relevant data
2. Perform calculations
3. Structure a comprehensive consultation
4. Provide data-backed recommendations

## Code Execution in Sandbox

### Understanding the Sandbox

All code execution happens in isolated Docker containers:
- **Security**: No access to your system
- **Clean Environment**: Fresh Python installation
- **Automatic Cleanup**: Containers removed after execution
- **Timeout Protection**: 30s for Python, 120s for terminal commands

### Running Python Code

**Example: Testing a Complex Algorithm**

```
Schreibe und teste einen Algorithmus zur Optimierung der Modulplatzierung auf einem Dach mit Hindernissen.
Führe den Code aus und zeige die Ergebnisse.
```

The agent will:
1. Write the algorithm
2. Create test data
3. Execute in sandbox
4. Show results

### Installing Packages

The agent can install packages in the sandbox:

```
Installiere pandas und erstelle eine Analyse der PV-Ertragsdaten aus einer CSV-Datei
```

The agent will:
1. Run `pip install pandas` in sandbox
2. Write the analysis code
3. Execute and show results

### Debugging in Sandbox

```
Der folgende Code hat einen Fehler. Finde und behebe ihn:

def calculate_roi(investment, annual_savings):
    return investment / annual_savings * 100

# Test
print(calculate_roi(15000, 0))  # Division by zero!
```

The agent will:
1. Identify the error
2. Suggest a fix (error handling)
3. Test the corrected code

## Knowledge Base Management

### What's in the Knowledge Base

The agent has access to documents about:
- Photovoltaic systems and technology
- Heat pump systems
- Energy efficiency standards
- Economic calculations and ROI
- Government incentives and regulations

### Effective Knowledge Queries

**Specific Queries:**
```
Was ist der durchschnittliche Wirkungsgrad von monokristallinen Solarmodulen?
Welche Vorlauftemperaturen sind für Wärmepumpen optimal?
```

**Comparative Queries:**
```
Vergleiche Luft-Wasser und Sole-Wasser Wärmepumpen hinsichtlich Effizienz und Kosten
```

**Technical Queries:**
```
Erkläre den Unterschied zwischen String-Wechselrichtern und Mikro-Wechselrichtern
```

### Adding Your Own Documents

To add documents to the knowledge base:

1. Place PDF files in `Agent/knowledge_base/` directory
2. Run: `python Agent/setup_knowledge_base.py`
3. Restart the application

The agent will automatically index new documents.

### Knowledge Base Search Strategy

The agent follows this search hierarchy:
1. **First**: Search internal knowledge base
2. **Then**: Use web search if needed (Tavily API)
3. **Finally**: Apply reasoning and domain expertise

## Telephony Simulation

### Simulating Customer Calls

The agent can simulate outbound sales and consulting calls:

```
Simuliere einen Anruf bei einem Kunden, der Interesse an einer Photovoltaik-Anlage hat.
Ziel: Termin für eine Vor-Ort-Beratung vereinbaren.
```

### Call Protocol Structure

The agent follows a professional protocol:

1. **Preparation**: Searches knowledge base for relevant facts
2. **Opening**: Professional introduction
3. **Needs Analysis**: Asks about energy consumption, roof space
4. **Presentation**: Top 3 benefits with data
5. **Objection Handling**: Addresses concerns with facts
6. **Closing**: Clear next step (appointment, calculation, etc.)

### Advanced Call Scenarios

**Handling Objections:**
```
Simuliere einen Anruf, bei dem der Kunde sagt:
"Photovoltaik ist zu teuer und lohnt sich nicht"
```

The agent will:
1. Validate the concern
2. Counter with data (ROI, amortization time)
3. Provide concrete examples
4. Offer to send a personalized calculation

**Multi-Touch Campaign:**
```
Erstelle eine Strategie für 3 Anrufe:
1. Erstkontakt und Bedarfsanalyse
2. Angebotspräsentation
3. Follow-up und Abschluss
```

## Project Generation

### Generating Complete Projects

The agent can scaffold entire applications:

```
Generiere ein Flask API Projekt für Photovoltaik-Berechnungen mit:
- REST API Endpoints
- Datenbankmodellen
- Unit Tests
- Docker Support
- README und Dokumentation
```

### Project Templates

Available project types:
- `flask_api`: REST API with Flask
- `streamlit_app`: Interactive web app
- `cli_tool`: Command-line application
- `data_analysis`: Jupyter notebook project
- `microservice`: Containerized microservice

**Example:**
```
Generiere ein Streamlit-App Projekt für einen interaktiven Solarrechner
```

### Customizing Generated Projects

After generation, you can refine:

```
Füge dem generierten Projekt eine Authentifizierung hinzu
Erweitere die API um einen Endpoint für Speicherberechnungen
```

## Testing Workflows

### Test-Driven Development (TDD)

The agent follows TDD principles:

**Example:**
```
Entwickle eine Funktion zur Berechnung der optimalen Batteriegröße.
Folge dem TDD-Zyklus: Test schreiben, Test fehlschlagen sehen, Code schreiben, Test bestehen.
```

The agent will:
1. Write the test first
2. Run it (should fail)
3. Implement the function
4. Run test again (should pass)
5. Refactor if needed

### Running Tests in Sandbox

```
Führe alle Tests im Workspace aus und zeige die Ergebnisse
```

The agent will:
1. Execute `pytest -v` in sandbox
2. Parse results
3. Show pass/fail status
4. Highlight any failures

### Debugging Failed Tests

```
Der Test test_calculate_savings() schlägt fehl. Analysiere und behebe das Problem.
```

The agent will:
1. Read the test code
2. Read the implementation
3. Identify the issue
4. Suggest or implement a fix
5. Re-run the test

## Advanced Prompting Techniques

### Providing Context

**Good:**
```
Kontext: Ich arbeite an einem Projekt zur Optimierung von PV-Anlagen.
Ich habe bereits Module für Ertragsprognose und Kostenberechnung.

Aufgabe: Erstelle ein Modul für die Optimierung der Modulausrichtung.
```

### Specifying Constraints

```
Erstelle eine Funktion zur ROI-Berechnung mit folgenden Anforderungen:
- Eingabe: Investition, jährliche Einsparung, Zinssatz
- Ausgabe: ROI in Jahren
- Fehlerbehandlung für ungültige Eingaben
- Type Hints und Docstrings
- Unit Tests
```

### Iterative Refinement

**First Pass:**
```
Erstelle eine einfache Funktion zur Berechnung des PV-Ertrags
```

**Refinement:**
```
Erweitere die Funktion um:
- Berücksichtigung von Verschattung
- Temperaturkoeffizient
- Degradation über die Jahre
```

### Using Examples

```
Erstelle eine Funktion ähnlich wie diese, aber für Wärmepumpen:

def calculate_pv_yield(kwp, location, orientation):
    # Berechnet den jährlichen Ertrag
    pass
```

## Performance Optimization

### Knowledge Base Optimization

The knowledge base is automatically optimized:
- **Caching**: FAISS index is cached after first load
- **Lazy Loading**: Documents loaded only when needed
- **Efficient Search**: Vector similarity search is fast

### Docker Optimization

Tips for faster execution:
- Keep Docker running (avoid cold starts)
- The sandbox image is reused (no rebuild needed)
- Containers are cleaned up automatically

### Batch Operations

For multiple similar tasks:

```
Erstelle Unit-Tests für folgende Funktionen:
1. calculate_pv_yield()
2. calculate_roi()
3. calculate_co2_savings()
4. calculate_battery_size()
```

The agent will process them efficiently.

## Advanced Use Cases

### 1. Data Analysis Workflow

```
Analysiere die PV-Ertragsdaten aus der Datei yields.csv:
1. Lade die Daten mit pandas
2. Berechne Durchschnitt, Min, Max
3. Erstelle eine Visualisierung
4. Identifiziere Ausreißer
5. Generiere einen Bericht
```

### 2. API Integration

```
Erstelle einen API-Client für die Abfrage von Wetterdaten:
- Verwende requests Library
- Implementiere Fehlerbehandlung
- Cache Ergebnisse
- Schreibe Tests mit Mock-Daten
```

### 3. Documentation Generation

```
Generiere eine vollständige API-Dokumentation für das Modul calculations.py:
- Funktionsbeschreibungen
- Parameter und Rückgabewerte
- Beispiele
- Markdown-Format
```

### 4. Code Review and Refactoring

```
Überprüfe den folgenden Code und schlage Verbesserungen vor:
- Code-Qualität
- Performance
- Lesbarkeit
- Best Practices

[Paste your code here]
```

## Tips for Power Users

### 1. Leverage Conversation Memory

Build complex solutions step-by-step, referencing previous work.

### 2. Combine Multiple Tools

```
Suche Informationen über Wärmepumpen-COP, 
erstelle eine Berechnungsfunktion,
schreibe Tests,
und generiere eine Dokumentation.
```

### 3. Use the Agent for Learning

```
Erkläre mir das Konzept der Wärmepumpen-Jahresarbeitszahl (JAZ) 
und zeige mir, wie man sie berechnet.
```

### 4. Automate Repetitive Tasks

```
Erstelle ein Script, das automatisch:
1. Kundendaten aus einer CSV lädt
2. Für jeden Kunden eine PV-Berechnung durchführt
3. Ergebnisse in einer neuen CSV speichert
```

## Limitations and Considerations

### What the Agent Can Do

✅ Generate code and documentation
✅ Search knowledge base
✅ Execute code in sandbox
✅ Simulate phone calls
✅ Create project structures
✅ Run tests

### What the Agent Cannot Do

❌ Access your local file system (outside workspace)
❌ Make real phone calls (simulation only)
❌ Access the internet without API keys
❌ Modify the main application database
❌ Execute long-running processes (timeouts apply)

### Security Considerations

- All code runs in isolated containers
- No access to sensitive data
- API keys are never exposed
- File operations restricted to workspace

## Next Steps

- Explore [Example Tasks](EXAMPLE_TASKS.md) for inspiration
- Read [Best Practices](BEST_PRACTICES.md) for optimal usage
- Check [Troubleshooting Guide](TROUBLESHOOTING.md) if issues arise

## Getting Help

For advanced support:
- Review the [Documentation Guide](DOCUMENTATION_GUIDE.md)
- Check the [Security Checklist](SECURITY_CHECKLIST.md)
- See [Validation Guide](VALIDATION_GUIDE.md) for testing

Happy building! 🚀
