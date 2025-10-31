# KAI Agent - Example Tasks

## Introduction

This document provides practical examples of tasks you can give to the KAI Agent. Each example includes the task description, expected behavior, and tips for best results.

## Table of Contents

1. [Renewable Energy Consulting Examples](#renewable-energy-consulting-examples)
2. [Software Development Examples](#software-development-examples)
3. [Combined Workflow Examples](#combined-workflow-examples)
4. [Error Handling Examples](#error-handling-examples)

## Renewable Energy Consulting Examples

### Example 1: Basic PV Information Query

**Task:**
```
Was sind die wichtigsten Vorteile von Photovoltaik-Anlagen für Privathaushalte?
```

**Expected Behavior:**
- Agent searches knowledge base
- Returns structured list of benefits
- Includes data-backed points (cost savings, CO2 reduction, etc.)

**Tips:**
- Be specific about target audience (private, commercial, industrial)
- Ask follow-up questions for more details


### Example 2: Heat Pump Comparison

**Task:**
```
Vergleiche Luft-Wasser-Wärmepumpen und Sole-Wasser-Wärmepumpen hinsichtlich:
- Effizienz (JAZ)
- Installationskosten
- Betriebskosten
- Platzbedarf
- Vor- und Nachteile
```

**Expected Behavior:**
- Agent searches knowledge base for technical data
- Creates structured comparison table
- Provides recommendations based on use cases

**Tips:**
- Specify comparison criteria clearly
- Ask for specific use case recommendations

### Example 3: ROI Calculation

**Task:**
```
Berechne den ROI für eine 10 kWp Photovoltaik-Anlage mit folgenden Daten:
- Investition: 15.000 €
- Jahresverbrauch: 4.500 kWh
- Strompreis: 0,35 €/kWh
- Einspeisevergütung: 0,08 €/kWh
- Eigenverbrauchsquote: 30%
```

**Expected Behavior:**
- Agent performs calculation
- Shows step-by-step breakdown
- Provides amortization time
- Includes 20-year projection

**Tips:**
- Provide all necessary data points
- Ask for sensitivity analysis if needed


### Example 4: Customer Consultation Simulation

**Task:**
```
Simuliere eine Beratung für einen Kunden mit folgenden Anforderungen:
- Einfamilienhaus, 150 m² Wohnfläche
- Jahresverbrauch: 5.000 kWh
- Dach: 60 m² Südausrichtung, 30° Neigung
- Budget: 20.000 €
- Interesse an: PV-Anlage + Batteriespeicher

Erstelle eine vollständige Beratung mit Empfehlungen.
```

**Expected Behavior:**
- Agent analyzes requirements
- Searches knowledge base for relevant data
- Calculates optimal system size
- Provides cost estimate
- Includes ROI and savings projections
- Suggests next steps

**Tips:**
- Provide complete customer profile
- Specify budget constraints
- Ask for alternative scenarios

### Example 5: Technical Specification Query

**Task:**
```
Welche technischen Spezifikationen sollte ich bei der Auswahl von Solarmodulen beachten?
Erkläre: Wirkungsgrad, Temperaturkoeffizient, Degradation, Garantie.
```

**Expected Behavior:**
- Agent explains each specification
- Provides typical values
- Explains impact on performance
- Gives selection criteria

**Tips:**
- Ask for specific technical terms
- Request practical examples
- Follow up with comparison questions


### Example 6: Funding and Incentives

**Task:**
```
Welche Förderungen und steuerlichen Vorteile gibt es aktuell für Photovoltaik-Anlagen in Deutschland?
```

**Expected Behavior:**
- Agent searches knowledge base
- May use web search for current information
- Lists available programs
- Explains eligibility criteria
- Provides application process overview

**Tips:**
- Specify location (country, region)
- Ask about specific programs
- Request calculation examples

## Software Development Examples

### Example 7: Simple Function Generation

**Task:**
```
Schreibe eine Python-Funktion, die prüft, ob eine Zahl eine Primzahl ist.
Anforderungen:
- Type Hints
- Docstring
- Fehlerbehandlung für negative Zahlen
- Unit Tests
```

**Expected Behavior:**
- Agent generates function with documentation
- Includes error handling
- Writes comprehensive tests
- May execute tests in sandbox

**Tips:**
- Specify all requirements upfront
- Request specific coding standards
- Ask for test execution


### Example 8: Class Design with TDD

**Task:**
```
Entwickle eine Klasse SolarPanel mit TDD:

Anforderungen:
- Attribute: manufacturer, model, power_wp, efficiency, price
- Methoden: calculate_annual_yield(location, orientation)
- Validierung aller Eingaben
- Folge dem TDD-Zyklus: Test schreiben → Test fehlschlagen → Code schreiben → Test bestehen
```

**Expected Behavior:**
- Agent writes test first
- Runs test (should fail)
- Implements class
- Runs test again (should pass)
- Shows complete TDD cycle

**Tips:**
- Explicitly request TDD approach
- Specify all methods and attributes
- Ask to see each TDD step

### Example 9: API Endpoint Creation

**Task:**
```
Erstelle einen Flask REST API Endpoint für PV-Ertragsprognose:

POST /api/calculate-yield
Request Body:
{
  "kwp": 10.0,
  "location": "Munich",
  "orientation": "south",
  "tilt": 30
}

Response:
{
  "annual_yield_kwh": 10500,
  "monthly_breakdown": [...],
  "confidence": 0.85
}

Inkludiere: Validierung, Fehlerbehandlung, Tests
```

**Expected Behavior:**
- Agent creates Flask endpoint
- Implements request validation
- Adds error handling
- Writes API tests
- May provide curl examples

**Tips:**
- Specify request/response format
- Include validation rules
- Request example usage


### Example 10: Project Scaffolding

**Task:**
```
Generiere ein Flask API Projekt für Photovoltaik-Berechnungen:

Struktur:
- REST API mit Flask
- SQLite Datenbank für Berechnungshistorie
- Modelle: Calculation, Customer, System
- Endpoints: /calculate, /history, /customers
- Unit Tests und Integration Tests
- Docker Support
- README mit Setup-Anleitung
```

**Expected Behavior:**
- Agent creates complete project structure
- Generates all necessary files
- Includes configuration files
- Writes documentation
- Provides setup instructions

**Tips:**
- Specify technology stack
- List required features
- Request specific project structure

### Example 11: Code Review and Refactoring

**Task:**
```
Überprüfe den folgenden Code und schlage Verbesserungen vor:

def calc(a, b, c):
    x = a * b
    y = x / c
    z = y * 365
    return z

Fokus auf:
- Lesbarkeit
- Dokumentation
- Fehlerbehandlung
- Best Practices
```

**Expected Behavior:**
- Agent analyzes code
- Identifies issues
- Suggests improvements
- Provides refactored version
- Explains changes

**Tips:**
- Specify review criteria
- Provide context about code purpose
- Ask for specific improvements


### Example 12: Data Analysis Script

**Task:**
```
Erstelle ein Python-Script zur Analyse von PV-Ertragsdaten:

Eingabe: CSV-Datei mit Spalten: date, yield_kwh, irradiance, temperature
Ausgabe:
- Statistiken (Durchschnitt, Min, Max, Standardabweichung)
- Identifikation von Ausreißern
- Korrelation zwischen Einstrahlung und Ertrag
- Visualisierung (Matplotlib)
- Exportiere Ergebnisse als JSON

Führe das Script im Sandbox aus mit Testdaten.
```

**Expected Behavior:**
- Agent creates analysis script
- Generates test data
- Executes in sandbox
- Shows results
- Provides visualizations

**Tips:**
- Specify input/output format
- Request execution in sandbox
- Ask for visualization

## Combined Workflow Examples

### Example 13: End-to-End Consulting Tool

**Task:**
```
Erstelle ein vollständiges Beratungstool:

Phase 1: Suche Informationen über durchschnittliche PV-Erträge in Deutschland
Phase 2: Erstelle eine Funktion zur Ertragsberechnung basierend auf diesen Daten
Phase 3: Erstelle eine Funktion zur ROI-Berechnung
Phase 4: Schreibe Tests für beide Funktionen
Phase 5: Erstelle ein CLI-Tool, das beide Funktionen nutzt
Phase 6: Generiere eine Beispiel-Beratung für einen Testkunden
```

**Expected Behavior:**
- Agent works through phases sequentially
- Uses knowledge base for research
- Generates code with tests
- Creates working CLI tool
- Demonstrates with example

**Tips:**
- Break into clear phases
- Build on previous steps
- Test incrementally


### Example 14: Customer Outreach Campaign

**Task:**
```
Erstelle eine Outreach-Kampagne für Photovoltaik-Beratung:

1. Recherchiere die Top 5 Verkaufsargumente für PV-Anlagen
2. Erstelle ein Gesprächsleitfaden für Erstkontakt
3. Simuliere einen Anruf bei einem interessierten Kunden
4. Erstelle eine Follow-up Email basierend auf dem Gespräch
5. Generiere eine Checkliste für die Vor-Ort-Beratung
```

**Expected Behavior:**
- Agent researches from knowledge base
- Creates structured call script
- Simulates realistic conversation
- Generates professional email
- Provides practical checklist

**Tips:**
- Specify campaign goals
- Define target audience
- Request realistic scenarios

### Example 15: Technical Documentation Generator

**Task:**
```
Erstelle eine technische Dokumentation für ein PV-Berechnungsmodul:

1. Analysiere die Funktionen in calculations.py (erstelle zuerst Beispiel-Code)
2. Generiere API-Dokumentation im Markdown-Format
3. Erstelle Verwendungsbeispiele für jede Funktion
4. Schreibe einen Quickstart-Guide
5. Generiere ein Diagramm der Modul-Architektur (als Text/ASCII)
```

**Expected Behavior:**
- Agent creates example code
- Generates comprehensive documentation
- Provides practical examples
- Creates visual representations
- Structures documentation logically

**Tips:**
- Provide existing code or ask agent to create example
- Specify documentation format
- Request specific sections

## Error Handling Examples

### Example 16: Debugging Failed Code

**Task:**
```
Der folgende Code gibt einen Fehler. Finde und behebe ihn:

def calculate_roi(investment, annual_savings, years=20):
    total_savings = annual_savings * years
    roi = (total_savings - investment) / investment * 100
    return roi

# Test
result = calculate_roi(15000, 0, 20)
print(f"ROI: {roi}%")

Fehler: ZeroDivisionError und NameError
```

**Expected Behavior:**
- Agent identifies both errors
- Explains causes
- Provides corrected version
- Adds error handling
- Tests the fix

**Tips:**
- Provide complete error message
- Include context
- Ask for explanation of fix


### Example 17: Handling Invalid Input

**Task:**
```
Erstelle eine robuste Funktion zur Berechnung der Anlagengröße:

def calculate_system_size(annual_consumption_kwh, roof_area_m2, efficiency=0.17):
    # Berechne optimale kWp basierend auf Verbrauch und verfügbarer Fläche
    pass

Anforderungen:
- Validiere alle Eingaben (positive Zahlen, realistische Bereiche)
- Werfe spezifische Exceptions für verschiedene Fehlertypen
- Gebe hilfreiche Fehlermeldungen
- Schreibe Tests für alle Fehlerfälle
```

**Expected Behavior:**
- Agent creates function with comprehensive validation
- Defines custom exceptions if needed
- Provides clear error messages
- Writes tests for error cases
- Documents error handling

**Tips:**
- Specify validation rules
- Request specific exception types
- Ask for error message examples

### Example 18: API Error Handling

**Task:**
```
Erstelle einen API-Client mit robuster Fehlerbehandlung:

- Endpoint: https://api.example.com/solar-data
- Mögliche Fehler: Timeout, 404, 500, Rate Limit, Invalid Response
- Implementiere: Retry-Logik, Exponential Backoff, Logging
- Schreibe Tests mit Mock-Responses für alle Fehlerszenarien
```

**Expected Behavior:**
- Agent creates resilient API client
- Implements retry logic
- Handles all error cases
- Adds appropriate logging
- Writes comprehensive tests

**Tips:**
- List all possible error scenarios
- Specify retry strategy
- Request logging implementation

### Example 19: Data Validation Pipeline

**Task:**
```
Erstelle eine Validierungs-Pipeline für Kundendaten:

Eingabe: Dictionary mit Kundeninformationen
Validierungen:
- Email-Format
- Telefonnummer (deutsche Formate)
- PLZ (5-stellig)
- Verbrauch (1000-50000 kWh)
- Dachfläche (10-500 m²)

Bei Fehler: Sammle alle Validierungsfehler und gebe detaillierte Fehlermeldungen
Schreibe Tests für valide und invalide Daten
```

**Expected Behavior:**
- Agent creates validation pipeline
- Implements all validation rules
- Collects multiple errors
- Provides detailed feedback
- Writes comprehensive tests

**Tips:**
- Specify all validation rules
- Request batch error collection
- Ask for user-friendly messages


## Advanced Examples

### Example 20: Multi-Step Calculation Workflow

**Task:**
```
Erstelle ein komplettes Berechnungs-Workflow:

Schritt 1: Berechne optimale Anlagengröße
- Input: Jahresverbrauch, Dachfläche, Budget
- Output: Empfohlene kWp

Schritt 2: Berechne Ertragsprognose
- Input: kWp, Standort, Ausrichtung
- Output: Jahresertrag in kWh

Schritt 3: Berechne Wirtschaftlichkeit
- Input: Investition, Ertrag, Strompreis, Eigenverbrauch
- Output: ROI, Amortisationszeit, 20-Jahres-Bilanz

Schritt 4: Erstelle Beratungsdokument
- Zusammenfassung aller Berechnungen
- Empfehlungen
- Nächste Schritte

Implementiere alle Schritte mit Tests und führe ein Beispiel aus.
```

**Expected Behavior:**
- Agent creates modular functions for each step
- Chains functions together
- Writes tests for each component
- Executes complete workflow
- Generates formatted output

**Tips:**
- Break into clear steps
- Specify data flow between steps
- Request example execution

### Example 21: Performance Optimization

**Task:**
```
Optimiere die folgende Funktion für bessere Performance:

def calculate_yields_for_all_customers(customers):
    results = []
    for customer in customers:
        yield_data = calculate_annual_yield(
            customer['kwp'],
            customer['location'],
            customer['orientation']
        )
        results.append(yield_data)
    return results

Problem: Langsam bei 10.000+ Kunden
Optimiere für: Geschwindigkeit, Speichereffizienz
Behalte: Lesbarkeit, Testbarkeit
```

**Expected Behavior:**
- Agent analyzes performance bottlenecks
- Suggests optimizations (vectorization, caching, etc.)
- Implements optimized version
- Provides performance comparison
- Maintains code quality

**Tips:**
- Specify performance requirements
- Mention constraints
- Request benchmarks

## Tips for Creating Your Own Tasks

### 1. Be Specific
❌ "Mach was mit Solar"
✅ "Erstelle eine Funktion zur Berechnung des PV-Ertrags mit Parametern X, Y, Z"

### 2. Provide Context
```
Kontext: Ich entwickle ein Beratungstool für Photovoltaik
Ziel: Automatisierte Erstberatung
Aufgabe: [specific task]
```

### 3. Specify Requirements
- Input/Output format
- Error handling needs
- Testing requirements
- Documentation level
- Performance constraints

### 4. Break Down Complex Tasks
Instead of one huge task, create a sequence:
1. Research/Planning
2. Core implementation
3. Testing
4. Documentation
5. Integration

### 5. Use Examples
Show the agent what you want:
```
Erstelle eine Funktion ähnlich wie diese, aber für Wärmepumpen:
[paste example]
```

### 6. Iterate
Start simple, then refine:
1. Basic version
2. Add error handling
3. Add tests
4. Optimize
5. Document

## Task Templates

### Template 1: Function Creation
```
Erstelle eine Python-Funktion [name]:

Zweck: [description]
Parameter:
- [param1]: [type] - [description]
- [param2]: [type] - [description]

Rückgabe: [type] - [description]

Anforderungen:
- Type Hints
- Docstring (Google Style)
- Fehlerbehandlung für [cases]
- Unit Tests mit [scenarios]
```

### Template 2: API Endpoint
```
Erstelle einen [framework] API Endpoint:

[METHOD] /api/[path]

Request:
{
  [request schema]
}

Response:
{
  [response schema]
}

Anforderungen:
- Validierung
- Fehlerbehandlung
- Tests
- Dokumentation
```

### Template 3: Data Analysis
```
Analysiere Daten aus [source]:

Datenformat: [description]

Analysen:
1. [analysis 1]
2. [analysis 2]
3. [analysis 3]

Ausgabe:
- [output format]
- [visualization requirements]

Führe im Sandbox aus mit [test data description]
```

### Template 4: Consulting Task
```
Erstelle eine Beratung für:

Kunde: [profile]
Anforderungen: [requirements]
Budget: [budget]

Liefere:
1. Bedarfsanalyse
2. Systemempfehlung
3. Kostenberechnung
4. ROI-Prognose
5. Nächste Schritte
```

## Next Steps

- Try examples from this document
- Modify examples for your needs
- Create your own task templates
- Share successful patterns
- Build a library of effective prompts

## Additional Resources

- [Basic Usage Tutorial](BASIC_USAGE_TUTORIAL.md) - Getting started
- [Advanced Features Guide](ADVANCED_FEATURES_GUIDE.md) - Advanced capabilities
- [Best Practices](BEST_PRACTICES.md) - Optimization tips
- [Troubleshooting Guide](USER_TROUBLESHOOTING_GUIDE.md) - Problem solving

Happy tasking! 🚀
