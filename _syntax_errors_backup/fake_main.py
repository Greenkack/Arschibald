# ==============================================================================
# main.py (Aktualisiert für den ersten Testlauf)
# Haupt-Einstiegspunkt zum Starten und Interagieren mit dem Agenten.
# ==============================================================================
import os
import sys
from dotenv import load_dotenv
from agent.agent_core import AgentCore


def main():
    """
    Hauptfunktion zum Initialisieren und Starten des KAI-Agenten.
    """
    # Lädt API-Schlüssel und andere Konfigurationen aus einer .env-Datei.
    load_dotenv()

    print("KAI Agent wird initialisiert...")

    # Überprüfen, ob der OpenAI API-Schlüssel vorhanden ist.
    # Ohne diesen kann der Agent nicht funktionieren.
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "\nFATALER FEHLER: Der OPENAI_API_KEY wurde nicht in Ihrer .env-Datei gefunden.")
        print("Bitte erstellen Sie eine '.env'-Datei (durch Kopieren von '.env.example') und fügen Sie Ihren API-Schlüssel ein.")
        sys.exit(1)  # Beendet das Skript, wenn der Schlüssel fehlt.

    # 1. Instanziieren des Agenten-Kerns
    kai_agent = AgentCore()

    # 2. Definieren der ersten Aufgabe für den Agenten
    # Dies ist eine einfache Aufgabe, um den gesamten Arbeitsablauf zu testen:
    # Datei schreiben -> Code ausführen -> Ergebnis beobachten.
    initial_task = "Schreibe ein Python-Skript in eine Datei namens 'hallo.py', das den Text 'Hallo von KAI!' ausgibt. Führe dieses Skript anschließend aus, um zu bestätigen, dass es funktioniert."

    # 3. Starten der Agenten-Ausführungsschleife
    kai_agent.run(initial_task)


if __name__ == "__main__":
    main()

# ==============================================================================
# README.md (Neue Datei mit Anleitungen)
# ==============================================================================
```markdown
# KAI Agent - Schnellstart-Anleitung

Folgen Sie diesen Schritten, um den KAI - Agenten zu testen. Führen Sie die Befehle in Ihrem Terminal im Hauptverzeichnis des Projekts(`kai_agent / `) aus.

# Schritt 1: Erstellen der .env-Datei

Wenn Sie es noch nicht getan haben, kopieren Sie die Vorlage und fügen Sie Ihren OpenAI API - Schlüssel ein.

```bash
# Diesen Befehl nur einmal ausführen
cp .env.example .env
```

Öffnen Sie die neue `.env`-Datei und tragen Sie Ihren Schlüssel ein:
`OPENAI_API_KEY = "sk-..."`

# Schritt 2: Bauen der Docker-Sandbox

Dieser Befehl erstellt das isolierte Docker - Image, in dem der Agent Code sicher ausführen wird. Sie müssen Docker auf Ihrem System installiert und gestartet haben.

```bash
# Diesen Befehl nur einmal ausführen (oder wenn Sie das Dockerfile ändern)
docker build - t kai_agent - sandbox . -f sandbox / Dockerfile
```

# Schritt 3: Installieren der Python-Abhängigkeiten

Installieren Sie die notwendigen Python - Pakete für das Hauptprojekt.

```bash
pip install - r requirements.txt
```

# Schritt 4: Starten des Agenten

Führen Sie diesen Befehl aus, um den Agenten mit seiner ersten Aufgabe zu starten. Sie werden nun den "Denkprozess" des Agenten live im Terminal sehen.

```bash
python main.py
