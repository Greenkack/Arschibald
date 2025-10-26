"""
Script zum Übersetzen der Agent UI von Englisch auf Deutsch und Entfernen von Emojis
"""

import re


def translate_agent_ui():
    file_path = r"C:\Users\win10\Desktop\Bokuk2\Agent\agent_ui.py"

    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    # Translations Dictionary (Englisch -> Deutsch)
    translations = {
        # Buttons
        "Close Help": "Hilfe schließen",
        "Copy Example": "Beispiel kopieren",
        "Clear Memory": "Speicher löschen",
        "Start Agent": "Agent starten",
        "Stop Agent": "Agent stoppen",
        "Got it!": "Verstanden",
        "Help": "Hilfe",

        # Titles and Headers
        "Configuration Check": "Konfigurationsprüfung",
        "Knowledge Base Initialization": "Wissensdatenbank-Initialisierung",
        "Task Input": "Aufgabeneingabe",
        "Agent Execution": "Agent-Ausführung",
        "Complete Help Guide": "Vollständige Hilfe-Anleitung",
        "Example Task Suggestions": "Beispiel-Aufgabenvorschläge",
        "Quick Usage Instructions": "Schnellanleitung",
        "Required API Keys Not Found": "Erforderliche API-Schlüssel nicht gefunden",
        "Setup Instructions": "Einrichtungsanleitung",
        "Missing API Keys": "Fehlende API-Schlüssel",
        "All API keys are configured!": "Alle API-Schlüssel sind konfiguriert!",

        # Status Messages
        "Task completed successfully!": "Aufgabe erfolgreich abgeschlossen!",
        "Task failed": "Aufgabe fehlgeschlagen",
        "Agent initialized successfully!": "Agent erfolgreich initialisiert!",
        "Knowledge base loaded successfully!": "Wissensdatenbank erfolgreich geladen!",
        "Memory cleared!": "Speicher gelöscht!",
        "Failed to initialize agent": "Fehler bei Agent-Initialisierung",
        "Failed to load knowledge base": "Fehler beim Laden der Wissensdatenbank",
        "Cannot proceed without OPENAI_API_KEY": "Kann ohne OPENAI_API_KEY nicht fortfahren",
        "Please configure it and restart the application": "Bitte konfigurieren Sie ihn und starten Sie die Anwendung neu",

        # Content
        "Result:": "Ergebnis:",
        "Generated Files": "Generierte Dateien",
        "Suggested Solution:": "Lösungsvorschlag:",
        "Error Type:": "Fehlertyp:",
        "Error:": "Fehler:",
        "Status:": "Status:",
        "Step": "Schritt",
        "Input validation failed": "Eingabevalidierung fehlgeschlagen",
        "Unexpected error": "Unerwarteter Fehler",

        # Info messages
        "Knowledge base is empty": "Wissensdatenbank ist leer",
        "Add PDF files to": "Fügen Sie PDF-Dateien hinzu zu",
        "How to Add Documents": "Anleitung: Dokumente hinzufügen",
        "How to Configure API Keys": "Anleitung: API-Schlüssel konfigurieren",
        "The agent can now search PDF documents": "Der Agent kann jetzt PDF-Dokumente durchsuchen",
        "domain-specific information about renewable energy systems": "nach fachspezifischen Informationen über erneuerbare Energiesysteme",
        "The agent will continue without knowledge base": "Der Agent wird ohne Wissensdatenbank fortfahren",

        # Tab names
        "Energy Consulting": "Energieberatung",
        "Software Development": "Software-Entwicklung",
        "Combined Tasks": "Kombinierte Aufgaben",

        # Long texts
        "Welcome to KAI Agent!": "Willkommen beim KAI Agent!",
        "This AI assistant can help you with": "Dieser KI-Assistent kann Ihnen helfen bei",
        "Renewable energy consulting": "Beratung zu erneuerbaren Energien",
        "PV systems, heat pumps": "PV-Anlagen, Wärmepumpen",
        "Software development": "Software-Entwicklung",
        "code generation, testing, project setup": "Code-Generierung, Tests, Projekt-Setup",
        "Complex multi-step workflows": "Komplexen mehrstufigen Arbeitsabläufen",
        "Quick Start:": "Schnellstart:",
        "Enter a task below and click": "Geben Sie unten eine Aufgabe ein und klicken Sie auf",
        "Click the": "Klicken Sie auf",
        "for detailed instructions and examples": "für detaillierte Anweisungen und Beispiele",

        # Help content
        "How to Use the KAI Agent": "Verwendung des KAI Agent",
        "What is KAI Agent?": "Was ist KAI Agent?",
        "is an autonomous AI assistant with dual expertise": "ist ein autonomer KI-Assistent mit Doppel-Expertise",
        "Renewable Energy Consulting": "Erneuerbare-Energien-Beratung",
        "Photovoltaics, heat pumps, economic analysis": "Photovoltaik, Wärmepumpen, Wirtschaftlichkeitsanalyse",
        "Software Architecture": "Software-Architektur",
        "Code generation, testing, project scaffolding": "Code-Generierung, Tests, Projekt-Gerüst",
        "How It Works": "Funktionsweise",
        "Enter your task": "Geben Sie Ihre Aufgabe ein",
        "in the text area below": "im Textfeld unten",
        "to begin execution": "um die Ausführung zu beginnen",
        "Watch the agent think": "Beobachten Sie den Denkprozess des Agenten",
        "see its reasoning process in real-time": "sehen Sie seinen Argumentationsprozess in Echtzeit",
        "Review results": "Ergebnisse prüfen",
        "get comprehensive answers, code, or analysis": "erhalten Sie umfassende Antworten, Code oder Analysen",

        # Expander titles
        "Tip:": "Tipp:",
        "Be specific about what you want": "Seien Sie konkret, was Sie wollen",
        "Include parameters, requirements, and expected output": "Geben Sie Parameter, Anforderungen und erwartete Ausgabe an",
        "Describe what you want the agent to do": "Beschreiben Sie, was der Agent tun soll",
    }

    # Ersetze alle Übersetzungen
    for english, german in translations.items():
        # Ersetze in verschiedenen Kontexten
        content = content.replace(f'"{english}"', f'"{german}"')
        content = content.replace(f"'{english}'", f"'{german}'")
        content = content.replace(f'**{english}**', f'**{german}**')
        content = content.replace(f'### {english}', f'###{german}')
        content = content.replace(f'## {english}', f'## {german}')

    # Entferne Emojis aus Streamlit-Calls (aber nicht aus print statements)
    # Pattern für st.markdown, st.title, st.success, etc. mit Emojis
    emoji_pattern = r'(st\.\w+\(["\'])([\U0001F300-\U0001F9FF]|\u2600-\u26FF|\u2700-\u27BF|[\u2B50]|[\u231A-\u231B]|[\u23E9-\u23F3]|[\u25AA-\u25AB]|[\u25B6]|[\u25C0]|[\u25FB-\u25FE]|[\u2614-\u2615]|[\u2648-\u2653]|[\u267F]|[\u2693]|[\u26A1]|[\u26AA-\u26AB]|[\u26BD-\u26BE]|[\u26C4-\u26C5]|[\u26CE]|[\u26D4]|[\u26EA]|[\u26F2-\u26F3]|[\u26F5]|[\u26FA]|[\u26FD]|[\u2705]|[\u270A-\u270B]|[\u2728]|[\u274C]|[\u274E]|[\u2753-\u2755]|[\u2757]|[\u2795-\u2797]|[\u27B0]|[\u27BF]|[\u2B1B-\u2B1C]|[\u2B55]|[\u2934-\u2935]|[\u2B05-\u2B07])\s*'

    # Entferne Emojis, aber behalte den Text
    def remove_emoji(match):
        return match.group(1)

    content = re.sub(emoji_pattern, remove_emoji, content)

    # Speichere die übersetzte Datei
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Übersetzung abgeschlossen!")
    print(f"Datei gespeichert: {file_path}")


if __name__ == "__main__":
    translate_agent_ui()
