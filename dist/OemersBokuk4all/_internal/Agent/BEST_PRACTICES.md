# O.M.I Agent - Best Practices

## Introduction

This document outlines best practices for using the O.M.I Agent effectively, securely, and efficiently. Following these guidelines will help you get the most value from the agent while avoiding common pitfalls.

## Table of Contents

1. [Task Formulation](#task-formulation)
2. [Security Best Practices](#security-best-practices)
3. [Performance Optimization](#performance-optimization)
4. [Code Quality](#code-quality)
5. [Knowledge Base Usage](#knowledge-base-usage)
6. [Error Handling](#error-handling)
7. [Testing Strategies](#testing-strategies)
8. [Documentation](#documentation)
9. [Workflow Organization](#workflow-organization)
10. [Common Pitfalls](#common-pitfalls)

## Task Formulation

### Be Specific and Clear

❌ **Bad:**
```
Mach was mit Solar
```

✅ **Good:**
```
Erstelle eine Python-Funktion, die den jährlichen Ertrag einer Photovoltaik-Anlage 
basierend auf kWp-Leistung, Standort (Breitengrad) und Ausrichtung berechnet.
```

### Break Down Complex Tasks

❌ **Bad:**
```
Erstelle eine komplette Webanwendung für Solarberechnungen mit Datenbank, 
API, Frontend, Tests und Deployment
```

✅ **Good:**
```
Phase 1: Erstelle die Projektstruktur und Datenbankmodelle
Phase 2: Implementiere die Berechnungslogik
Phase 3: Erstelle REST API Endpoints
Phase 4: Schreibe Unit- und Integrationstests
Phase 5: Erstelle Deployment-Konfiguration
```

### Provide Context

✅ **Good:**
```
Kontext: Ich arbeite an einem Beratungstool für Photovoltaik-Anlagen.
Ich habe bereits eine Funktion calculate_yield() implementiert.

Aufgabe: Erstelle eine Funktion calculate_roi(), die die Amortisationszeit 
unter Berücksichtigung von Förderungen und Strompreissteigerungen berechnet.
```

### Specify Requirements

✅ **Good:**
```
Erstelle eine Funktion mit folgenden Anforderungen:
- Eingabe: Investitionssumme, jährliche Einsparung, Zinssatz
- Ausgabe: Dictionary mit ROI, Amortisationszeit, Gesamtersparnis nach 20 Jahren
- Fehlerbehandlung für negative Werte
- Type Hints und ausführliche Docstrings
- Mindestens 5 Unit-Tests
```

## Security Best Practices

### API Key Management

✅ **Do:**
- Store API keys in `.env` file only
- Never commit `.env` to version control
- Use `.env.example` as a template
- Rotate keys regularly
- Use separate keys for development and production

❌ **Don't:**
- Hardcode API keys in code
- Share keys in chat or documentation
- Use production keys for testing
- Store keys in plain text files

### Code Execution Safety

✅ **Do:**
- Review generated code before using in production
- Test thoroughly in sandbox first
- Understand what the code does
- Check for security vulnerabilities
- Validate inputs and outputs

❌ **Don't:**
- Blindly execute generated code
- Skip code review
- Disable security features
- Execute untrusted code outside sandbox

### File System Operations

✅ **Do:**
- Keep all agent work in `agent_workspace/`
- Review file operations
- Backup important files
- Use version control

❌ **Don't:**
- Attempt to access files outside workspace
- Store sensitive data in workspace
- Disable path validation

## Performance Optimization

### Knowledge Base Efficiency

✅ **Do:**
- Keep knowledge base documents relevant and organized
- Use specific search queries
- Let the agent search knowledge base first
- Update documents periodically

❌ **Don't:**
- Add irrelevant documents
- Use overly broad search queries
- Skip knowledge base and go straight to web search

### Docker Optimization

✅ **Do:**
- Keep Docker running for faster execution
- Use the pre-built sandbox image
- Clean up old containers periodically: `docker system prune`
- Monitor disk space

❌ **Don't:**
- Rebuild sandbox image unnecessarily
- Run multiple heavy tasks simultaneously
- Ignore Docker errors

### Task Efficiency

✅ **Do:**
- Batch similar operations
- Reuse previous results in conversation
- Cache frequently used calculations
- Use efficient algorithms

❌ **Don't:**
- Repeat identical tasks
- Generate the same code multiple times
- Ignore performance warnings

## Code Quality

### Follow Standards

✅ **Do:**
- Request type hints in generated code
- Ask for comprehensive docstrings
- Follow PEP 8 style guidelines
- Use meaningful variable names
- Add comments for complex logic

**Example Request:**
```
Erstelle eine Funktion mit:
- Type Hints für alle Parameter und Rückgabewerte
- Google-Style Docstrings
- PEP 8 konformer Formatierung
- Aussagekräftigen Variablennamen
```

### SOLID Principles

✅ **Do:**
- Request modular, reusable code
- Separate concerns
- Use dependency injection
- Follow single responsibility principle

**Example Request:**
```
Erstelle ein Modul für PV-Berechnungen nach SOLID-Prinzipien:
- Separate Klassen für Ertrag, Kosten, ROI
- Interfaces für verschiedene Berechnungsmethoden
- Dependency Injection für Konfiguration
```

### Error Handling

✅ **Do:**
- Request comprehensive error handling
- Validate inputs
- Provide meaningful error messages
- Log errors appropriately

**Example Request:**
```
Erstelle eine Funktion mit robuster Fehlerbehandlung:
- Validierung aller Eingabeparameter
- Spezifische Exceptions für verschiedene Fehlertypen
- Aussagekräftige Fehlermeldungen
- Logging von Fehlern
```

## Knowledge Base Usage

### Effective Queries

✅ **Do:**
- Use specific technical terms
- Ask focused questions
- Request comparisons when relevant
- Follow up for clarification

**Good Queries:**
```
Was ist der durchschnittliche Wirkungsgrad von monokristallinen Modulen?
Vergleiche Luft-Wasser und Sole-Wasser Wärmepumpen
Welche Förderungen gibt es für PV-Anlagen in Deutschland 2024?
```

### Combining Knowledge with Code

✅ **Do:**
```
Suche Informationen über typische PV-Erträge in Deutschland,
und erstelle dann eine Funktion, die basierend auf diesen Daten
realistische Ertragsprognosen berechnet.
```

### Verifying Information

✅ **Do:**
- Cross-reference important facts
- Ask for sources when needed
- Verify calculations
- Update knowledge base with new information

## Error Handling

### When Errors Occur

✅ **Do:**
1. Read the error message carefully
2. Check the troubleshooting guide
3. Verify prerequisites (Docker, API keys)
4. Try a simpler version of the task
5. Provide error details when asking for help

❌ **Don't:**
- Ignore error messages
- Repeatedly try the same failing task
- Skip error logs
- Assume the agent is broken

### Debugging Strategy

✅ **Do:**
```
Der folgende Code gibt einen Fehler. Bitte:
1. Analysiere den Fehler
2. Erkläre die Ursache
3. Schlage eine Lösung vor
4. Teste die Lösung

[Paste code and error]
```

## Testing Strategies

### Test-Driven Development

✅ **Do:**
```
Entwickle eine Funktion zur Batterieoptimierung mit TDD:
1. Schreibe zuerst die Tests
2. Implementiere die Funktion
3. Stelle sicher, dass alle Tests bestehen
4. Refaktoriere wenn nötig
```

### Comprehensive Testing

✅ **Do:**
- Test normal cases
- Test edge cases
- Test error conditions
- Test with realistic data

**Example Request:**
```
Schreibe Tests für calculate_roi() die folgende Szenarien abdecken:
- Normale Eingaben
- Grenzwerte (0, sehr große Zahlen)
- Ungültige Eingaben (negative Werte, None)
- Realistische Beispieldaten
```

### Test Maintenance

✅ **Do:**
- Keep tests up to date
- Remove obsolete tests
- Refactor tests with code
- Document test scenarios

## Documentation

### Code Documentation

✅ **Do:**
```
Erstelle eine Funktion mit vollständiger Dokumentation:
- Modul-Level Docstring
- Klassen-Docstrings
- Funktions-Docstrings mit Args, Returns, Raises
- Inline-Kommentare für komplexe Logik
- Verwendungsbeispiele
```

### Project Documentation

✅ **Do:**
- Request README files for projects
- Include setup instructions
- Document API endpoints
- Provide usage examples
- List dependencies

**Example Request:**
```
Generiere ein Projekt mit vollständiger Dokumentation:
- README.md mit Setup-Anleitung
- API-Dokumentation
- Verwendungsbeispiele
- Architektur-Übersicht
```

## Workflow Organization

### Session Planning

✅ **Do:**
1. Plan your session goals
2. Start with simple tasks
3. Build complexity gradually
4. Save important results
5. Document your progress

### File Organization

✅ **Do:**
- Use clear file names
- Organize in directories
- Keep related files together
- Clean up unused files

**Example:**
```
agent_workspace/
├── pv_calculator/
│   ├── calculations.py
│   ├── models.py
│   ├── tests/
│   └── README.md
└── heat_pump_tool/
    ├── ...
```

### Version Control

✅ **Do:**
- Use git for generated projects
- Commit frequently
- Write meaningful commit messages
- Tag important versions

## Common Pitfalls

### Pitfall 1: Vague Tasks

❌ **Problem:**
```
Mach was mit Photovoltaik
```

✅ **Solution:**
```
Erstelle eine Funktion zur Berechnung des optimalen Neigungswinkels 
für PV-Module basierend auf Breitengrad
```

### Pitfall 2: Skipping Prerequisites

❌ **Problem:**
Starting without checking Docker or API keys

✅ **Solution:**
- Verify Docker is running: `docker ps`
- Check API keys in `.env`
- Run validation: `python Agent/validate_config.py`

### Pitfall 3: Not Reviewing Generated Code

❌ **Problem:**
Blindly using generated code in production

✅ **Solution:**
- Review all generated code
- Test thoroughly
- Understand the logic
- Adapt to your needs

### Pitfall 4: Ignoring Error Messages

❌ **Problem:**
Repeatedly trying the same failing task

✅ **Solution:**
- Read error messages carefully
- Check troubleshooting guide
- Simplify the task
- Ask for help with specific error details

### Pitfall 5: Overcomplicating Tasks

❌ **Problem:**
```
Erstelle eine komplette Enterprise-Anwendung mit Microservices, 
Kubernetes, CI/CD, Monitoring, und allem drum und dran
```

✅ **Solution:**
Break it down into manageable phases

### Pitfall 6: Not Using Knowledge Base

❌ **Problem:**
Asking for information that's in the knowledge base without letting the agent search

✅ **Solution:**
```
Suche in der Knowledge Base nach Informationen über Wärmepumpen-Effizienz
und erstelle dann eine Beratung für einen Kunden
```

### Pitfall 7: Poor Error Handling

❌ **Problem:**
Requesting code without error handling

✅ **Solution:**
Always request robust error handling and input validation

### Pitfall 8: Neglecting Tests

❌ **Problem:**
Generating code without tests

✅ **Solution:**
Always request tests, preferably using TDD approach

## Quick Reference Checklist

Before starting a task:
- [ ] Docker is running
- [ ] API keys are configured
- [ ] Task is clearly defined
- [ ] Prerequisites are met
- [ ] Workspace is organized

When requesting code:
- [ ] Specify requirements clearly
- [ ] Request type hints and docstrings
- [ ] Ask for error handling
- [ ] Include tests
- [ ] Request documentation

After receiving results:
- [ ] Review generated code
- [ ] Test thoroughly
- [ ] Verify against requirements
- [ ] Document any modifications
- [ ] Save important results

## Continuous Improvement

### Learn from Experience

✅ **Do:**
- Note what works well
- Refine your prompting style
- Build a library of effective prompts
- Share successful patterns

### Stay Updated

✅ **Do:**
- Check for agent updates
- Update knowledge base documents
- Review new features
- Read updated documentation

### Provide Feedback

✅ **Do:**
- Note issues and limitations
- Suggest improvements
- Document workarounds
- Share best practices with team

## Conclusion

Following these best practices will help you:
- Get better results from the agent
- Work more efficiently
- Avoid common problems
- Maintain high code quality
- Ensure security and reliability

Remember: The agent is a powerful tool, but it's most effective when used thoughtfully and strategically.

## Additional Resources

- [Basic Usage Tutorial](BASIC_USAGE_TUTORIAL.md)
- [Advanced Features Guide](ADVANCED_FEATURES_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Example Tasks](EXAMPLE_TASKS.md)
- [Security Checklist](SECURITY_CHECKLIST.md)

Happy coding! 🚀
