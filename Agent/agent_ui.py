"""
Agent UI Module
===============

Streamlit interface for the O.M.I Agent system.
Provides task input, real-time status display, and results visualization.

Performance Optimizations (Task 15.3):
- Async agent execution: Non-blocking task execution with threading
- Streaming output: Real-time display of agent reasoning
- Optimized rendering: Efficient UI updates with minimal reruns
- Progress indicators: Clear feedback during execution
- Lazy loading: Defer heavy operations until needed
- Caching: Reuse expensive computations
"""

import os
import queue
import sys
import threading
import time
from typing import Any

import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Lazy imports with error handling
try:
    from agent.tools.knowledge_tools import lazy_load_knowledge_base
except ImportError as e:
    def lazy_load_knowledge_base():
        """Fallback wenn langchain fehlt"""
        return None
    st.warning(f"Knowledge Tools nicht verfügbar: {e}")

try:
    from config import check_api_keys, get_missing_keys, get_setup_instructions
except ImportError as e:
    def check_api_keys():
        return True
    def get_missing_keys():
        return []
    def get_setup_instructions(keys):
        return ""
    st.warning(f"Config nicht verfügbar: {e}")

try:
    from agent.security import InputValidationError, sanitize_user_input
except ImportError as e:
    class InputValidationError(Exception):
        pass
    def sanitize_user_input(text):
        return text
    st.warning(f"Security Module nicht verfügbar: {e}")


# Import error handling
# Import security utilities (Task 12.1)


# Async execution state with progress tracking
class AsyncExecutionState:
    """
    Manages async agent execution state with progress tracking.

    Performance optimizations:
    - Non-blocking execution with threading
    - Progress queue for real-time updates
    - Efficient state management
    """

    def __getstate__(self):
        """Ermöglicht Pickle-Serialisierung für Session State"""
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        """Ermöglicht Pickle-Deserialisierung für Session State"""
        self.__dict__.update(state)

    def __init__(self):
        self.running = False
        self.result = None
        self.error = None
        self.progress_queue = queue.Queue()
        self.thread = None
        self.start_time = None
        self.progress = 0

    def start(self, agent_core, user_input):
        """Start async execution with progress tracking."""
        self.running = True
        self.result = None
        self.error = None
        self.start_time = time.time()
        self.progress = 0

        def execute():
            try:
                # Update progress periodically
                def progress_callback(step):
                    self.progress = min(90, self.progress + 10)
                    self.progress_queue.put({
                        'type': 'progress',
                        'value': self.progress
                    })

                result = agent_core.run(user_input)
                self.result = result
                self.progress = 100
            except Exception as e:
                self.error = str(e)
            finally:
                self.running = False

        self.thread = threading.Thread(target=execute, daemon=True)
        self.thread.start()

    def is_running(self):
        """Check if execution is still running."""
        return self.running

    def get_result(self):
        """Get execution result."""
        return self.result

    def get_error(self):
        """Get execution error."""
        return self.error

    def get_elapsed_time(self):
        """Get elapsed execution time."""
        if self.start_time:
            return time.time() - self.start_time
        return 0

    def get_progress(self):
        """Get current progress percentage."""
        return self.progress


@st.cache_data(ttl=300)  # Cache for 5 minutes
def check_api_keys_ui() -> dict[str, bool]:
    """
    Check and validate all required API keys.

    Performance optimization: Cached to avoid repeated checks.

    Returns:
        Dictionary with key names and their availability status

    Displays:
        - Success message if all keys are configured
        - Error message with missing keys and setup instructions
    """
    keys_status = check_api_keys()
    missing = get_missing_keys()

    if not missing:
        st.success("Alle API-Keys sind konfiguriert!")
        return keys_status

    # Display missing keys
    st.error("API-Keys fehlen")

    st.markdown("### Fehlende erforderliche API-Keys:")
    for key in missing:
        st.markdown(f"- **{key}**")

    # Show setup instructions - styled mit weißem Hintergrund und orangenen Akzenten
    with st.expander("Setup-Anleitung", expanded=False):
        instructions_text = get_setup_instructions()
        instructions_html = (
            "<div style=\"background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);"
            " border-left: 4px solid #ff8c00;"
            " border-radius: 8px;"
            " padding: 20px;"
            " box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15), 0 2px 6px rgba(0, 0, 0, 0.1);"
            " font-family: 'Courier New', monospace;"
            " color: #2d3748;"
            " white-space: pre-wrap;"
            " line-height: 1.6;\">"
            f"{instructions_text}"
            "</div>"
        )
        st.markdown(instructions_html, unsafe_allow_html=True)

    return keys_status


def display_agent_status(
    status: str,
    intermediate_steps: list | None = None,
    streaming: bool = False,
    progress: int = 0
):
    """
    Display real-time agent status and thinking process.

    Performance optimizations (Task 15.3):
    - Streaming mode for real-time updates
    - Efficient rendering with minimal DOM updates
    - Progressive disclosure of information
    - Lazy rendering of detailed information

    Args:
        status: Current status message
        intermediate_steps: List of intermediate reasoning steps
        streaming: Whether to use streaming mode
        progress: Progress percentage (0-100)

    Displays:
        - Progress indicator
        - Agent thinking process
        - Intermediate steps with tool usage
    """
    # Show status with optimized progress indicator
    if streaming:
        st.info(status)
        # Use progress bar for streaming (efficient updates)
        if progress > 0:
            st.progress(progress / 100.0)
        st.markdown(f" **{status}**")
    else:
        # Use spinner for non-streaming
        with st.spinner(status):
            st.markdown(f"**Status:** {status}")

    if not intermediate_steps:
        return

    max_display_steps = 10
    display_steps = intermediate_steps[-max_display_steps:]
    total_steps = len(intermediate_steps)

    for idx, step in enumerate(display_steps, 1):
        step_num = total_steps - len(display_steps) + idx
        st.markdown(f"**Schritt {step_num}**")

        if isinstance(step, tuple) and len(step) >= 2:
            action, observation = step[0], step[1]

            if hasattr(action, "tool"):
                st.markdown(f"Tool: `{action.tool}`")

            if hasattr(action, "tool_input"):
                st.markdown("**Input:**")
                st.write(action.tool_input)

            obs_str = str(observation)
            truncated = len(obs_str) > 500
            with st.expander("Ausgabe (gekürzt)" if truncated else "Ausgabe", expanded=False):
                st.code(obs_str[:500] + "..." if truncated else obs_str, language="text")
        else:
            st.write(step)

        if idx < len(display_steps):
            st.markdown("---")


def format_agent_output(result: dict, streaming: bool = False):
    """Format and display agent execution results."""

    intermediate_steps = result.get("intermediate_steps", [])

    col1, col2, col3 = st.columns(3)
    with col1:
        if "execution_time" in result:
            st.metric("⏱ Dauer", f"{result['execution_time']:.2f}s")

    with col2:
        if result.get("retry_count", 0) > 0:
            st.metric(" Wiederholungen", result["retry_count"])

    with col3:
        if intermediate_steps:
            st.metric(" Schritte", len(intermediate_steps))

    if result.get("success", False):
        st.success("Aufgabe erfolgreich abgeschlossen!")
        output = result.get("output", "")

        if output:
            st.markdown("### Ergebnis:")
            if len(output) > 5000:
                with st.expander("Gesamtausgabe anzeigen", expanded=False):
                    st.markdown(output[:5000] + "\n\n... (gekürzt)")
                    st.download_button(
                        "Komplette Ausgabe herunterladen",
                        output,
                        file_name="agent_output.txt",
                        mime="text/plain",
                    )
            else:
                st.markdown(output)

        if intermediate_steps:
            display_agent_status(
                "Verarbeitung abgeschlossen",
                intermediate_steps,
                streaming=streaming,
            )

        if output and ("agent_workspace" in output.lower() or "file" in output.lower()):
            st.markdown("### Generierte Dateien")
            st.info(
                "Dateien wurden im Verzeichnis `agent_workspace` erzeugt. "
                "Du kannst sie im Dateisystem öffnen."
            )

    else:
        st.error("Aufgabe fehlgeschlagen")
        error_msg = result.get("error", "Unbekannter Fehler")

        if len(error_msg) > 1000:
            st.markdown(f"**Fehler:** {error_msg[:1000]}...")
            with st.expander("Komplette Fehlermeldung", expanded=False):
                st.code(error_msg, language="text")
        else:
            st.markdown(f"**Fehler:** {error_msg}")

        if "error_type" in result:
            st.caption(f"Fehlertyp: {result['error_type']}")

        if "solution" in result:
            st.markdown("### Vorgeschlagene Lösung:")
            st.info(result["solution"])

        if intermediate_steps:
            with st.expander("Debug-Informationen", expanded=False):
                display_agent_status(
                    "Fehler während der Ausführung",
                    intermediate_steps,
                    streaming=streaming,
                )


def render_agent_menu():
    """
    Main entry point for the A.G.E.N.T. menu interface.

    Renders:
        - Page configuration
        - API key validation
        - Task input interface
        - Start button and controls
        - Real-time status display
        - Results visualization

    Raises:
        ConfigurationError: If required API keys are missing
    """
    # Page configuration
    st.title(" A.G.E.N.T. - Autonomes KI-Expertensystem")
    st.markdown(
        "**Künstliche Intelligenz** mit Doppelkompetenz in "
        "Erneuerbare-Energien-Beratung und Softwarearchitektur"
    )

    # Welcome message for first-time users (Task 13.2)
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True

    if st.session_state.first_visit:
        st.info(
            "**Willkommen beim O.M.I Agent!**\n\n"
            "Dieser KI-Assistent unterstützt Dich bei:\n"
            "- Beratung zu erneuerbaren Energien (PV-Anlagen, Wärmepumpen)\n"
            "- Softwareentwicklung (Code-Generierung, Tests, Projekt-Setup)\n"
            "- Komplexen mehrstufigen Workflows\n\n"
            "**Schnellstart:** Gib unten eine Aufgabe ein und klicke auf \"Agent starten\".\n"
            "Über den Button \"Hilfe\" findest Du ausführliche Anleitungen und Beispiele."
        )

        col_dismiss1, col_dismiss2, col_dismiss3 = st.columns([2, 1, 2])
        with col_dismiss2:
            if st.button("Verstanden! ", use_container_width=True):
                st.session_state.first_visit = False
                st.rerun()

    st.markdown("---")

    # API key validation with help (Task 13.2)
    col_config1, col_config2 = st.columns([6, 1])
    with col_config1:
        st.markdown("###  Konfigurationsprüfung")
    with col_config2:
        st.markdown(
            "<div style=\"margin-top: 10px;\">"
            "<span title=\"API keys are required for the agent to function. OpenAI key is mandatory, others are optional for additional features.\"></span>"
            "</div>",
            unsafe_allow_html=True,
        )

    keys_status = check_api_keys_ui()

    # Check if OpenAI key is available (optional warning, but don't block)
    if not keys_status.get('OPENAI_API_KEY', False):
        st.warning(
            "OPENAI_API_KEY nicht konfiguriert. "
            "Agent-Funktionalität ist eingeschränkt, aber Du kannst alle Bereiche erkunden."
        )
        with st.expander("Wie API Keys konfigurieren (optional)", expanded=False):
            st.markdown("""
            ### Quick Setup

            1. **Erstelle/Bearbeite `.env` Datei** im Projektverzeichnis
            2. **Füge deinen OpenAI API Key hinzu**:
            """)
            
            # Gestyltes Code-Feld mit weißem Hintergrund und orangen Akzenten
            code_block_html = (
                "<div style=\"background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);"
                " border: 2px solid rgba(200, 210, 220, 0.5); border-left: 4px solid #ff8c00;"
                " border-radius: 8px; padding: 12px; margin: 10px 0;"
                " box-shadow: 0 10px 12px rgba(0, 0, 0, 0.15), 0 10px 10px rgba(0, 0, 0, 0.1);"
                " font-family: 'Courier New', monospace;\">"
                "<code style=\"color: #ffffff; font-size: 14px; font-weight: 600;\">"
                "OPENAI_API_KEY=sk-your-key-here"
                "</code>"
                "</div>"
            )
            st.markdown(code_block_html, unsafe_allow_html=True)
            
            st.markdown("""
            3. **Hole deinen API Key** von [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
            4. **Starte die Anwendung neu**

            ### Optionale Keys (für zusätzliche Features)

            - **TAVILY_API_KEY**: Web-Suche
            - **TWILIO_***: Telefonie-Features
            - **ELEVEN_LABS_API_KEY**: Voice Synthesis

            Siehe `AGENT_INSTALLATION_GUIDE.md` für Details.
            """)
        # Don't stop - let the owner explore all areas!

    st.markdown("---")

    # Initialize knowledge base and agent (optimized with lazy loading)
    col_kb1, col_kb2 = st.columns([6, 1])
    with col_kb1:
        st.markdown("### Knowledge Base initialisieren")
    with col_kb2:
        st.markdown(
            "<div style=\"margin-top: 10px;\">"
            "<span title=\"Die Knowledge Base enthält domänenspezifische PDFs, die der Agent durchsuchen kann.\"></span>"
            "</div>",
            unsafe_allow_html=True,
        )

    if 'vector_store' not in st.session_state:
        # Use lazy loading for faster startup
        with st.spinner("Knowledge Base wird geladen..."):
            try:
                # Lazy load: defer actual loading until first search
                st.session_state.vector_store = lazy_load_knowledge_base()
                if st.session_state.vector_store is not None:
                    st.success("Knowledge Base erfolgreich geladen!")
                    st.caption(
                        "Der Agent kann nun PDF-Dokumente nach fachspezifischen Informationen zu Energiesystemen durchsuchen.")
                else:
                    st.info(
                        " Knowledge Base ist leer. "
                        "Lege PDF-Dateien im Ordner `Agent/knowledge_base/` ab."
                    )
                    with st.expander(" So fügst du Dokumente hinzu", expanded=False):
                        st.markdown("""
                        ### Dokumente für die Knowledge Base hinzufügen

                        1. **PDF-Dateien** in den Ordner `Agent/knowledge_base/` legen
                        2. **Anwendung neu starten**, damit die Dokumente indiziert werden
                        3. **Der Agent erstellt automatisch** einen durchsuchbaren Index

                        **Empfohlene Dokumente:**
                        - Technische Spezifikationen für PV-Anlagen
                        - Wärmepumpen-Dokumentation
                        - Wirtschaftlichkeits-Leitfäden
                        - Installationshandbücher
                        - Produktdatenblätter

                        **Hinweis:** Der Agent funktioniert auch ohne Knowledge Base, hat dann aber weniger domänenspezifische Informationen.
                        """)
            except Exception as e:
                st.error(f"Knowledge Base konnte nicht geladen werden: {e}")
                st.info(
                    "Der Agent läuft ohne Knowledge Base weiter. "
                    "Lege PDFs in den Ordner `Agent/knowledge_base/` und starte neu."
                )
                st.session_state.vector_store = None

    # Initialize agent (cached in session state)
    if 'agent_core' not in st.session_state:
        with st.spinner("Agent wird initialisiert..."):
            try:
                # Lazy import to avoid heavy dependencies at app startup
                from agent.agent_core import AgentCore
                st.session_state.agent_core = AgentCore(
                    vector_store=st.session_state.vector_store
                )
                st.success("Agent erfolgreich initialisiert!")
            except Exception as e:
                st.error(f"Agent konnte nicht initialisiert werden: {e}")
                # Helpful hint if a known optional dependency is missing
                if isinstance(e, ModuleNotFoundError) and 'langchain_classic' in str(e):
                    st.info(
                        "Optionales Paket 'langchain_classic' fehlt. "
                        "Bitte das passende Wheel in den Ordner 'BOKUK_BUILD/wheelhouse' legen "
                        "und offline installieren, damit die Agent-Funktionalität aktiv wird."
                    )
                # Don't stop - let the owner explore all areas!
                st.session_state.agent_core = None  # Mark as not initialized

    st.markdown("---")

    # Task input interface
    st.markdown("### Aufgaben-Eingabe")
    
    # Voice input option
    if st.session_state.get('voice_mode'):
        st.info(" **Sprachsteuerung aktiviert!**")
        try:
            from voice_command import render_voice_input_ui, integrate_voice_with_agent
            
            voice_result = render_voice_input_ui()
            voice_text = integrate_voice_with_agent(voice_result)
            
            if voice_text:
                st.success(f"Erkannt: {voice_text}")
                st.session_state['task_input'] = voice_text
                st.session_state['voice_mode'] = False
                st.rerun()
        except ImportError:
            st.warning("Sprachmodul nicht verfügbar.")
            st.session_state['voice_mode'] = False

    # Help button and dialog (Task 13.2)
    col_help1, col_help2 = st.columns([6, 1])
    with col_help2:
        if st.button(" Hilfe", use_container_width=True):
            st.session_state.show_help_dialog = True

    # Help dialog (Task 13.2)
    if st.session_state.get('show_help_dialog', False):
        with st.expander(" Vollständige Hilfe", expanded=False):
            st.markdown("""
            ## So nutzt du den O.M.I Agent

            ### Was ist der O.M.I Agent?
            O.M.I (Künstliche Intelligenz) ist ein autonomer KI-Assistent mit zwei Kernkompetenzen:
            - **Erneuerbare Energien**: Photovoltaik, Wärmepumpen, Wirtschaftlichkeits-Analysen
            - **Software-Architektur**: Code-Generierung, Tests, Projekt-Gerüste

            ### So funktioniert es
            1. **Gib deine Aufgabe** unten im Textfeld ein
            2. **Klicke auf "Agent starten"**, um die Ausführung zu beginnen
            3. **Sieh dem Agenten beim Denken zu** - Nachvollziehbares Reasoning in Echtzeit
            4. **Ergebnisse prüfen** - fundierte Antworten, Code oder Analysen

            ### Welche Aufgaben du stellen kannst

            ####  Beratung Erneuerbare Energien
            - Knowledge Base nach technischen Infos durchsuchen
            - ROI und Amortisationszeit berechnen
            - Kundenpräsentationen vorbereiten
            - Systemkonfigurationen vergleichen
            - Verkaufsgespräche simulieren

            ####  Software-Entwicklung
            - Python-Funktionen mit Tests erzeugen
            - Komplette Projektstrukturen anlegen
            - Unit-Tests schreiben und ausführen
            - Code debuggen und Fehler beheben
            - API-Endpunkte generieren

            ####  Kombinierte Workflows
            - Recherche -> Code -> Test -> Dokumentation
            - Knowledge-Suche -> Berechnung -> Präsentation
            - Mehrschrittige komplexe Aufgaben

            ### Tipps für beste Ergebnisse

            **Sei präzise**: "Erstelle eine Python-Funktion zur Berechnung des PV-ROI mit Parametern: investment, annual_savings, years"

            **Gib Kontext**: "Ich baue ein Kundenberatungstool. Erstelle eine Funktion, die..."

            **Zerlege komplexe Aufgaben**: Statt "Baue eine komplette App" lieber:
            1. "Projektstruktur anlegen"
            2. "Kernberechnungen implementieren"
            3. "Tests hinzufügen"

            **Nutze Beispiele**: "Erstelle eine Funktion ähnlich dieser: [Beispiel einfügen]"

            **Vermeide Unklarheiten**: "Mach irgendwas mit Solar" -> zu vage

            ### Verfügbare Tools

            Der Agent hat Zugriff auf:
            -  **Knowledge Base**: Domänenspezifische PDFs
            - **Websuche**: Aktuelle Infos via Tavily API
            -  **Code-Ausführung**: Sichere Docker-Sandbox
            - **Dateizugriffe**: Lesen/Schreiben im Workspace
            -  **Telefonie**: Simulierte Verkaufsgespräche
            -  **Testing**: Automatisiertes pytest

            ### Häufige Anwendungsfälle

            **Schnelle Infos**: "Welche Vorteile haben Wärmepumpen?"

            **Berechnungen**: "Berechne den ROI für eine 10 kWp PV-Anlage mit 15.000 € Invest"

            **Code-Generierung**: "Schreibe eine Funktion für den jährlichen Solarertrag"

            **Projekt-Setup**: "Erzeuge eine Flask-API-Struktur für Solarkalkulationen"

            **Testing**: "Schreibe Unit-Tests für calculate_roi"

            ### Troubleshooting

            **Agent reagiert nicht?**
            - Internetverbindung prüfen
            - API-Keys korrekt hinterlegt?
            - Zunächst einfachere Aufgabe probieren

            **Unerwartete Ergebnisse?**
            - Anfrage klarer formulieren
            - Mehr Kontext oder Beispiele geben
            - In kleinere Schritte aufteilen

            **Docker-Fehler?**
            - Läuft Docker?
            - Ist das Sandbox-Image gebaut?
            - Siehe Troubleshooting-Guide

            ### Noch mehr Hilfe?

             **Dokumentation**: Im Ordner `Agent/`
            - `README.md` - Überblick & Quickstart
            - `BASIC_USAGE_TUTORIAL.md` - Einsteiger-Guide
            - `EXAMPLE_TASKS.md` - 20+ Beispielaufgaben
            - `TROUBLESHOOTING.md` - Fehlersuche
            - `ADVANCED_FEATURES_GUIDE.md` - Fortgeschrittene Nutzung

            **Validierung**: `python Agent/validate_config.py`

             **Installation**: `AGENT_INSTALLATION_GUIDE.md`
            """)

            if st.button("Hilfe schließen", use_container_width=True):
                st.session_state.show_help_dialog = False
                st.rerun()

    # Example tasks with categories (Task 13.2)
    with st.expander("Beispielaufgaben", expanded=False):
        # CSS für Tabs mit weißem Hintergrund und orangenen Akzenten - VOLLSTÄNDIG
        css_example_tabs = (
            "<style>\n"
            "/* Example Tasks Tabs - Alle schwarzen Hintergründe entfernen */\n"
            "div[data-baseweb=\"tab-list\"] {\n"
            "    background: transparent !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-list\"] button {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;\n"
            "    color: #4a5568 !important;\n"
            "    border-radius: 8px 8px 0 0 !important;\n"
            "    border: 1px solid rgba(200, 210, 220, 0.5) !important;\n"
            "    border-bottom: none !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-list\"] button:hover {\n"
            "    transform: translateY(-2px) !important;\n"
            "    box-shadow: 0 10px 12px rgba(255, 140, 0, 0.3) !important;\n"
            "    color: #2d3748 !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-list\"] button[aria-selected=\"true\"] {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #fff8f0 100%) !important;\n"
            "    color: #1a202c !important;\n"
            "    border-bottom: 4px solid #ff8c00 !important;\n"
            "    font-weight: 600 !important;\n"
            "    box-shadow: 0 10px 12px rgba(255, 140, 0, 0.2) !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-panel\"] {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;\n"
            "    border-radius: 0 0 8px 8px !important;\n"
            "    border: 1px solid rgba(200, 210, 220, 0.5) !important;\n"
            "    border-top: none !important;\n"
            "    padding: 20px !important;\n"
            "    box-shadow: 0 10px 12px rgba(0, 0, 0, 0.1) !important;\n"
            "}\n"
            "/* Alle verschachtelten Container weiß/transparent */\n"
            "div[data-baseweb=\"tab-panel\"] * {\n"
            "    background-color: transparent !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-panel\"] div[data-testid=\"stVerticalBlock\"],\n"
            "div[data-baseweb=\"tab-panel\"] div[data-testid=\"column\"],\n"
            "div[data-baseweb=\"tab-panel\"] div[data-testid=\"stHorizontalBlock\"] {\n"
            "    background: transparent !important;\n"
            "}\n"
            "/* Code-Blöcke in Tabs weiß stylen */\n"
            "div[data-baseweb=\"tab-panel\"] pre {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;\n"
            "    border-left: 4px solid #ff8c00 !important;\n"
            "    border-radius: 8px !important;\n"
            "    padding: 15px !important;\n"
            "    box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1) !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-panel\"] code {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;\n"
            "    color: #2d3748 !important;\n"
            "    font-family: 'Courier New', monospace !important;\n"
            "}\n"
            "/* Markdown Container */\n"
            "div[data-baseweb=\"tab-panel\"] .stMarkdown {\n"
            "    background: transparent !important;\n"
            "}\n"
            "</style>\n"
        )
        st.markdown(css_example_tabs, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs([
            " Energieberatung",
            " Software-Entwicklung",
            " Kombiniert"
        ])

        with tab1:
            st.markdown("""
            **Schnelle Info-Abfragen:**
            ```
            Was sind die wichtigsten Vorteile von Photovoltaik-Anlagen?
            ```
            ```
            Wie funktioniert eine Luft-Wasser-Wärmepumpe?
            ```

            **Wirtschaftlichkeits-Berechnungen:**
            ```
            Berechne den ROI für eine 10 kWp PV-Anlage:
            - Investition: 15.000 EUR
            - Jahresverbrauch: 4.500 kWh
            - Strompreis: 0,35 EUR/kWh
            - Eigenverbrauch: 30%
            ```

            **Kundenberatung:**
            ```
            Erstelle eine Beratung für einen Kunden mit:
            - Einfamilienhaus, 150 m^2
            - Jahresverbrauch: 5.000 kWh
            - Budget: 20.000 EUR
            - Interesse: PV + Speicher
            ```

            **Verkaufsgespräch simulieren:**
            ```
            Simuliere einen Beratungsanruf für Photovoltaik.
            Präsentiere die Top 3 Vorteile mit Daten.
            ```
            """)

            if st.button(" Beispiel 1 übernehmen", key="copy_energy_1"):
                st.session_state.agent_task_input = "Was sind die wichtigsten Vorteile von Photovoltaik-Anlagen?"
                st.rerun()

        with tab2:
            st.markdown("""
            **Einfache Funktion:**
            ```
            Schreibe eine Python-Funktion zur Berechnung des ROI:
            - Parameter: investment, annual_savings, years
            - Mit Type Hints und Docstring
            - Inkl. Fehlerbehandlung
            - Mit Unit Tests
            ```

            **Klasse mit TDD:**
            ```
            Entwickle eine Klasse SolarPanel mit TDD:
            - Attribute: manufacturer, model, power_wp, efficiency
            - Methode: calculate_annual_yield(location)
            - Folge dem TDD-Zyklus
            ```

            **API-Endpunkt:**
            ```
            Erstelle einen Flask REST API Endpoint:
            POST /api/calculate-yield
            Request: {kwp, location, orientation}
            Response: {annual_yield_kwh, monthly_breakdown}
            Mit Validierung und Tests
            ```

            **Projektgerüst:**
            ```
            Generiere ein Flask API Projekt für PV-Berechnungen:
            - REST API mit Flask
            - SQLite Datenbank
            - Unit Tests
            - README mit Setup
            ```
            """)

            if st.button(" Beispiel 2 übernehmen", key="copy_dev_1"):
                st.session_state.agent_task_input = "Schreibe eine Python-Funktion zur Berechnung des ROI mit Type Hints, Docstring und Unit Tests"
                st.rerun()

        with tab3:
            tab3_content = (
                "**Recherche -> Code -> Test:**\n"
                "```\n"
                "1. Suche in der Wissensdatenbank nach PV-Ertragsdaten\n"
                "2. Erstelle eine Funktion zur Ertragsberechnung\n"
                "3. Schreibe Tests für die Funktion\n"
                "4. Führe die Tests im Sandbox aus\n"
                "```\n\n"
                "**Beratungstool:**\n"
                "```\n"
                "Erstelle ein Beratungstool:\n"
                "1. Recherchiere durchschnittliche PV-Erträge\n"
                "2. Erstelle Ertragsfunktion\n"
                "3. Erstelle ROI-Funktion\n"
                "4. Schreibe Tests\n"
                "5. Erstelle CLI-Tool\n"
                "6. Generiere Beispiel-Beratung\n"
                "```\n\n"
                "**Kompletter Workflow:**\n"
                "```\n"
                "Entwickle eine Lösung für Amortisationsberechnung:\n"
                "- Suche relevante Formeln in der Wissensdatenbank\n"
                "- Implementiere die Berechnung in Python\n"
                "- Erstelle Unit Tests\n"
                "- Generiere Beispielberechnungen\n"
                "- Erstelle eine Dokumentation\n"
                "```"
            )
            st.markdown(tab3_content)

            if st.button(" Beispiel 3 übernehmen", key="copy_combined_1"):
                st.session_state.agent_task_input = "Suche in der Wissensdatenbank nach PV-Vorteilen, erstelle dann eine Python-Funktion zur Ertragsberechnung mit Tests"
                st.rerun()

    # Usage instructions (Task 13.2)
    with st.expander("Kurzanleitung", expanded=False):
        quickstart_text = (
            "### In 3 Schritten starten\n\n"
            "**Schritt 1: Aufgabe eingeben**\n"
            "- Schreibe unten, was der Agent erledigen soll\n"
            "- So konkret wie möglich\n"
            "- Alle benötigten Details angeben\n\n"
            "**Schritt 2: Agent starten**\n"
            "- Auf \"Agent starten\" klicken\n"
            "- Der Agent verarbeitet die Anfrage\n"
            "- Das Reasoning wird in Echtzeit angezeigt\n\n"
            "**Schritt 3: Ergebnisse prüfen**\n"
            "- Antwort lesen\n"
            "- Generierten Code kopieren\n"
            "- Erzeugte Dateien bei Bedarf herunterladen\n\n"
            "### Gute Aufgaben formulieren\n\n"
            "**Gute Beispiele:**\n"
            "- \"Erstelle eine Python-Funktion calculate_roi mit Parametern investment und annual_savings\"\n"
            "- \"Durchsuche die Knowledge Base nach Infos zur Wärmepumpen-Effizienz (JAZ)\"\n"
            "- \"Generiere eine Flask-Projektstruktur mit Modellen, Routen und Tests\"\n\n"
            "**Vermeide:**\n"
            "- \"Mach irgendwas\" (zu vage)\n"
            "- \"Hilf mir\" (kein konkreter Auftrag)\n"
            "- \"Fix alles\" (kein Kontext)\n\n"
            "### Fähigkeiten des Agents\n\n"
            "**Kann:**\n"
            "- Knowledge Base durchsuchen\n"
            "- Python-Code generieren\n"
            "- Tests schreiben und ausführen\n"
            "- Projektstrukturen erstellen\n"
            "- Berechnungen durchführen\n"
            "- Gespräche simulieren\n"
            "- Im Web suchen (falls API-Key hinterlegt)\n\n"
            "**Kann nicht:**\n"
            "- Lokale Dateien außerhalb des Workspace lesen\n"
            "- Echte Anrufe tätigen (nur Simulation)\n"
            "- Direkt auf Datenbanken zugreifen\n"
            "- Bestehenden Anwendungscode ändern\n"
            "- Befehle auf deinem System ausführen\n\n"
            "### Tipps & Tricks\n\n"
            "**Erst Knowledge Base nutzen**: Der Agent durchsucht zuerst seine Knowledge Base, bevor er ins Web geht.\n\n"
            "**Komplexes aufteilen**: Mehrschrittige Aufgaben in Phasen aufsplitten.\n\n"
            "**Beispiele geben**: Zeig, was du willst, mit kurzen Beispielen.\n\n"
            "**Iterieren**: Einfach starten, dann verfeinern.\n\n"
            "**Reasoning prüfen**: Beobachte den Denkprozess, um den Ansatz zu verstehen."
        )
        st.markdown(quickstart_text)

    # ====================================================================
    # TELEPHONY MEGA EXTENSION - ALL NEW FEATURES
    # ====================================================================
    
    with st.expander(" Telephony System - Bria Softphone & Advanced Features", expanded=False):
        st.markdown("### Telephony Management Console")
        st.markdown("Vollständiges Telefonsystem mit 36 Tools für professionelle Anrufverwaltung")
        
        # CSS für Telephony-Tabs - ALLE SCHWARZEN HINTERGRÜNDE ENTFERNEN
        css_telephony_tabs = (
            "<style>\n"
            "/* Telephony Tabs - Komplett weiß ohne schwarze Hintergründe */\n"
            "div[data-baseweb=\"tab-list\"] {\n"
            "    background: transparent !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-list\"] button {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;\n"
            "    color: #4a5568 !important;\n"
            "    border-radius: 8px 8px 0 0 !important;\n"
            "    border: 1px solid rgba(200, 210, 220, 0.5) !important;\n"
            "    border-bottom: none !important;\n"
            "    padding: 10px 20px !important;\n"
            "    margin: 0 2px !important;\n"
            "    box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1) !important;\n"
            "    transition: all 0.3s ease !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-list\"] button:hover {\n"
            "    transform: translateY(-2px) !important;\n"
            "    box-shadow: 0 10px 12px rgba(255, 140, 0, 0.3) !important;\n"
            "    color: #2d3748 !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-list\"] button[aria-selected=\"true\"] {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #fff8f0 100%) !important;\n"
            "    color: #1a202c !important;\n"
            "    border-bottom: 4px solid #ff8c00 !important;\n"
            "    font-weight: 600 !important;\n"
            "    box-shadow: 0 10px 12px rgba(255, 140, 0, 0.2) !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-panel\"] {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;\n"
            "    border-radius: 0 0 8px 8px !important;\n"
            "    border: 1px solid rgba(200, 210, 220, 0.5) !important;\n"
            "    border-top: none !important;\n"
            "    padding: 20px !important;\n"
            "    box-shadow: 0 10px 12px rgba(0, 0, 0, 0.1) !important;\n"
            "}\n"
            "/* KRITISCH: Alle verschachtelten Elemente transparent/weiß */\n"
            "div[data-baseweb=\"tab-panel\"] * {\n"
            "    background-color: transparent !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-panel\"] div[data-testid=\"stVerticalBlock\"],\n"
            "div[data-baseweb=\"tab-panel\"] div[data-testid=\"column\"],\n"
            "div[data-baseweb=\"tab-panel\"] div[data-testid=\"stHorizontalBlock\"],\n"
            "div[data-baseweb=\"tab-panel\"] .stMarkdown,\n"
            "div[data-baseweb=\"tab-panel\"] .element-container {\n"
            "    background: transparent !important;\n"
            "}\n"
            "/* Expander innerhalb der Tabs weiß */\n"
            "div[data-baseweb=\"tab-panel\"] details {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-panel\"] details summary {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;\n"
            "    color: #2d3748 !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-panel\"] details[open] {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #fff8f0 100%) !important;\n"
            "    border-left: 4px solid #ff8c00 !important;\n"
            "}\n"
            "/* Code-Blöcke weiß stylen */\n"
            "div[data-baseweb=\"tab-panel\"] pre {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;\n"
            "    border-left: 4px solid #ff8c00 !important;\n"
            "    border-radius: 8px !important;\n"
            "    padding: 15px !important;\n"
            "    box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1) !important;\n"
            "}\n"
            "div[data-baseweb=\"tab-panel\"] code {\n"
            "    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%) !important;\n"
            "    color: #2d3748 !important;\n"
            "    font-family: 'Courier New', monospace !important;\n"
            "}\n"
            "</style>\n"
        )
        st.markdown(css_telephony_tabs, unsafe_allow_html=True)
        
        # Tabs für verschiedene Bereiche
        phone_tab1, phone_tab2, phone_tab3, phone_tab4, phone_tab5 = st.tabs([
            " Bria Softphone",
            " Kontakte",
            " Analysen",
            " Wissensbasis",
            " Erweiterte Features"
        ])
        
        # TAB 1: Bria Softphone
        with phone_tab1:
            with st.expander(" SIP Verbindung", expanded=False):
                st.markdown("**Bria Softphone Verbindung konfigurieren**")
                
                col1, col2 = st.columns(2)
                with col1:
                    sip_server = st.text_input("SIP Server", placeholder="sip.example.com", key="sip_server")
                    sip_user = st.text_input("Benutzername", placeholder="user123", key="sip_user")
                with col2:
                    sip_pass = st.text_input("Passwort", type="password", key="sip_pass")
                    
                if st.button("Verbinden", key="bria_connect"):
                    if sip_server and sip_user and sip_pass:
                        st.code(f"bria_connect('{sip_server}', '{sip_user}', '***')")
                        st.info("Führe diesen Befehl im Agent-Chat aus")
                    else:
                        st.warning("Bitte alle Felder ausfüllen")
                
                if st.button("Trennen", key="bria_disconnect"):
                    st.code("bria_disconnect()")
            
            with st.expander(" Ausgehende Anrufe", expanded=False):
                st.markdown("**Anruf starten**")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    out_phone = st.text_input("Telefonnummer", placeholder="+49301234567", key="out_phone")
                    out_goal = st.text_input("Anrufziel", placeholder="Beratungstermin vereinbaren", key="out_goal")
                with col2:
                    st.markdown("**Schnellwahl**")
                    fav_contact = st.selectbox("Favorit", ["", "Max Mustermann", "Firma ABC", "VIP Kunde"], key="fav")
                    if st.button("Anrufen", key="quick_dial"):
                        if fav_contact:
                            st.code(f"quick_dial_favorite('{fav_contact}')")
                
                if st.button("Anruf starten", key="make_call"):
                    if out_phone:
                        st.code(f"bria_make_call('{out_phone}', '{out_goal}')")
                    else:
                        st.warning("Bitte Telefonnummer eingeben")
            
            with st.expander(" Anrufsteuerung", expanded=False):
                st.markdown("**Aktiven Anruf verwalten**")
                
                call_id_control = st.text_input("Call ID", placeholder="CALL-12345678", key="call_id_control")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("⏸ Halten", key="hold_call"):
                        st.code(f"bria_hold_call('{call_id_control}')")
                with col2:
                    if st.button(" Fortsetzen", key="resume_call"):
                        st.code(f"bria_resume_call('{call_id_control}')")
                with col3:
                    if st.button(" Weiterleiten", key="transfer_btn"):
                        target = st.text_input("Ziel", key="transfer_target")
                        if target:
                            st.code(f"bria_transfer_call('{call_id_control}', '{target}')")
                with col4:
                    if st.button("Auflegen", key="hangup_call"):
                        st.code(f"bria_hangup('{call_id_control}')")
        
        # TAB 2: Kontakte
        with phone_tab2:
            with st.expander(" Kontakt hinzufügen", expanded=False):
                st.markdown("**Neuen Kontakt anlegen**")
                
                col1, col2 = st.columns(2)
                with col1:
                    contact_name = st.text_input("Name", placeholder="Max Mustermann", key="contact_name")
                    contact_phone = st.text_input("Telefon", placeholder="+49301234567", key="contact_phone")
                    contact_email = st.text_input("E-Mail", placeholder="max@example.com", key="contact_email")
                with col2:
                    contact_company = st.text_input("Firma", placeholder="Musterfirma GmbH", key="contact_company")
                    contact_tags = st.text_input("Tags", placeholder="lead,vip,interessiert", key="contact_tags")
                    contact_notes = st.text_area("Notizen", placeholder="Weitere Informationen...", key="contact_notes", height=100)
                
                if st.button("Kontakt speichern", key="save_contact"):
                    if contact_name and contact_phone:
                        contact_snippet = (
                            "add_phone_contact(\n"
                            f"    name='{contact_name}',\n"
                            f"    phone_number='{contact_phone}',\n"
                            f"    email='{contact_email}',\n"
                            f"    company='{contact_company}',\n"
                            f"    tags='{contact_tags}',\n"
                            f"    notes='{contact_notes}'\n"
                            ")"
                        )
                        st.code(contact_snippet)
                    else:
                        st.warning("Name und Telefonnummer sind Pflichtfelder")
            
            with st.expander("Kontakte suchen", expanded=False):
                st.markdown("**Kontaktdatenbank durchsuchen**")
                
                search_query = st.text_input("Suche nach Name, Nummer oder Firma", key="contact_search")
                if st.button("Suchen", key="search_contacts"):
                    if search_query:
                        st.code(f"search_phone_contacts('{search_query}')")
                    else:
                        st.warning("Bitte Suchbegriff eingeben")
            
            with st.expander("Bulk Import (CSV/XLSX)", expanded=False):
                st.markdown("**Mehrere Kontakte auf einmal importieren**")
                bulk_columns = (
                    "**Erforderliche Spalten:**\n"
                    "- `name` - Kontaktname (Pflicht)\n"
                    "- `phone_number` - Telefonnummer (Pflicht)\n"
                    "- `email` - E-Mail Adresse (optional)\n"
                    "- `company` - Firmenname (optional)\n"
                    "- `tags` - Tags kommagetrennt (optional)\n"
                    "- `notes` - Notizen (optional)"
                )
                st.markdown(bulk_columns)
                
                import_file = st.text_input("Dateipfad", placeholder="C:/contacts.xlsx", key="import_file")
                if st.button("Import starten", key="bulk_import"):
                    if import_file:
                        st.code(f"bulk_import_phone_numbers('{import_file}')")
                    else:
                        st.warning("Bitte Dateipfad angeben")
        
        # TAB 3: Analytics
        with phone_tab3:
            with st.expander("Anruf-Statistiken", expanded=False):
                st.markdown("**Auswertung der Anrufaktivitäten**")
                
                analytics_days = st.slider("Zeitraum (Tage)", min_value=1, max_value=90, value=30, key="analytics_days")
                
                if st.button("Statistiken abrufen", key="get_analytics"):
                    st.code(f"get_call_analytics(days={analytics_days})")

                analytics_metrics = (
                    "**Metriken:**\n"
                    "- Gesamtanzahl Anrufe\n"
                    "- Erfolgreiche vs. fehlgeschlagene Anrufe\n"
                    "- Conversion Rate\n"
                    "- Durchschnittliche Anrufdauer\n"
                    "- Gesamte Gesprächszeit\n"
                    "- Durchschnittliche Stimmung"
                )
                st.markdown(analytics_metrics)
            
            with st.expander("Anruf-Historie durchsuchen", expanded=False):
                st.markdown("**Vergangene Anrufe finden**")
                
                col1, col2 = st.columns(2)
                with col1:
                    history_phone = st.text_input("Nach Nummer filtern", placeholder="+49301234567", key="history_phone")
                    history_days = st.number_input("Tage zurück", min_value=1, max_value=365, value=30, key="history_days")
                with col2:
                    history_outcome = st.text_input("Nach Ergebnis filtern", placeholder="success, scheduled, ...", key="history_outcome")
                
                if st.button("Historie durchsuchen", key="search_history"):
                    filters = []
                    if history_phone:
                        filters.append(f"phone_number='{history_phone}'")
                    filters.append(f"days={history_days}")
                    if history_outcome:
                        filters.append(f"outcome_filter='{history_outcome}'")
                    
                    st.code(f"search_call_history({', '.join(filters)})")
            
            with st.expander(" Sentiment-Analyse", expanded=False):
                st.markdown("**Stimmungsanalyse eines Anrufs**")
                
                sentiment_call_id = st.text_input("Call ID", placeholder="CALL-12345678", key="sentiment_call_id")
                
                if st.button("Stimmung analysieren", key="analyze_sentiment"):
                    if sentiment_call_id:
                        st.code(f"analyze_call_sentiment('{sentiment_call_id}')")
                    else:
                        st.warning("Bitte Call ID eingeben")
                
                sentiment_info = (
                    "**Analysiert:**\n"
                    "- Positive/Negative Schlüsselwörter\n"
                    "- Stimmungs-Score (-1 bis +1)\n"
                    "- Stimmungskategorie (Positiv/Neutral/Negativ)"
                )
                st.markdown(sentiment_info)
        
        # TAB 4: Wissensbasis
        with phone_tab4:
            with st.expander(" Call-Skript speichern", expanded=False):
                st.markdown("**Neues Anruf-Skript in Knowledge Base ablegen**")
                
                col1, col2 = st.columns(2)
                with col1:
                    script_name = st.text_input("Skriptname", placeholder="PV-Beratung Standard", key="script_name")
                    script_category = st.selectbox("Kategorie", ["Verkauf", "Support", "Beratung", "Follow-up"], key="script_category")
                    script_opening = st.text_area("Eröffnungssatz", placeholder="Guten Tag, hier ist O.M.I von...", key="script_opening", height=100)
                with col2:
                    script_keypoints = st.text_input("Kernpunkte (kommagetrennt)", placeholder="Kostenersparnis,Umweltschutz,Unabhängigkeit", key="script_keypoints")
                    script_objections = st.text_area("Einwandbehandlung", placeholder="JSON-Format", key="script_objections", height=80)
                    script_closing = st.text_area("Abschlusssatz", placeholder="Vielen Dank für das Gespräch...", key="script_closing", height=80)
                
                if st.button("Skript speichern", key="save_script"):
                    if script_name and script_category and script_opening:
                        script_snippet = (
                            "save_call_script(\n"
                            f"    name='{script_name}',\n"
                            f"    category='{script_category}',\n"
                            f"    opening_statement='{script_opening}',\n"
                            f"    key_points='{script_keypoints}',\n"
                            f"    objection_responses='{script_objections}',\n"
                            f"    closing_statement='{script_closing}'\n"
                            ")"
                        )
                        st.code(script_snippet)
                    else:
                        st.warning("Name, Kategorie und Eröffnung sind Pflichtfelder")
            
            with st.expander(" Call-Skripte abrufen", expanded=False):
                st.markdown("**Gespeicherte Skripte anzeigen**")
                
                script_filter = st.selectbox("Kategorie filtern", ["", "Verkauf", "Support", "Beratung", "Follow-up"], key="script_filter")
                
                if st.button("Skripte laden", key="load_scripts"):
                    if script_filter:
                        st.code(f"get_call_script(category='{script_filter}')")
                    else:
                        st.code("get_call_script()")
        
        # TAB 5: Erweiterte Features
        with phone_tab5:
            with st.expander(" Anrufaufzeichnung", expanded=False):
                st.markdown("**Anrufaufnahme starten & transkribieren**")
                
                col1, col2 = st.columns(2)
                with col1:
                    rec_call_id = st.text_input("Call ID", placeholder="CALL-12345678", key="rec_call_id")
                    rec_path = st.text_input("Aufnahmepfad (optional)", placeholder="C:/recordings/call.wav", key="rec_path")
                    
                    if st.button("Aufnahme starten", key="start_recording"):
                        if rec_call_id:
                            if rec_path:
                                st.code(f"start_call_recording('{rec_call_id}', '{rec_path}')")
                            else:
                                st.code(f"start_call_recording('{rec_call_id}')")
                        else:
                            st.warning("Bitte Call ID eingeben")
                
                with col2:
                    trans_path = st.text_input("Audiodatei transkribieren", placeholder="C:/recordings/call.wav", key="trans_path")
                    
                    if st.button("Transkribieren (Whisper)", key="transcribe"):
                        if trans_path:
                            st.code(f"transcribe_call_recording('{trans_path}')")
                        else:
                            st.warning("Bitte Dateipfad angeben")
            
            with st.expander(" CRM-Integration", expanded=False):
                st.markdown("**Anruf ins CRM-System protokollieren**")
                
                col1, col2 = st.columns(2)
                with col1:
                    crm_call_id = st.text_input("Call ID", placeholder="CALL-12345678", key="crm_call_id")
                with col2:
                    crm_customer_id = st.text_input("CRM Kunden-ID (optional)", placeholder="CRM-001", key="crm_customer_id")
                
                if st.button("Ins CRM protokollieren", key="log_crm"):
                    if crm_call_id:
                        if crm_customer_id:
                            st.code(f"log_call_to_crm('{crm_call_id}', '{crm_customer_id}')")
                        else:
                            st.code(f"log_call_to_crm('{crm_call_id}')")
                    else:
                        st.warning("Bitte Call ID eingeben")
            
            with st.expander(" Follow-up planen", expanded=False):
                st.markdown("**Wiedervorlage nach Anruf setzen**")
                
                col1, col2 = st.columns(2)
                with col1:
                    followup_call_id = st.text_input("Call ID", placeholder="CALL-12345678", key="followup_call_id")
                    followup_date = st.date_input("Follow-up Datum", key="followup_date")
                with col2:
                    followup_action = st.text_area("Geplante Aktion", placeholder="Angebot nachfassen", key="followup_action", height=100)
                
                if st.button("Wiedervorlage setzen", key="schedule_followup"):
                    if followup_call_id and followup_action:
                        follow_up_snippet = (
                            "schedule_follow_up(\n"
                            f"    call_id='{followup_call_id}',\n"
                            f"    follow_up_date='{followup_date}',\n"
                            f"    follow_up_action='{followup_action}'\n"
                            ")"
                        )
                        st.code(follow_up_snippet)
                    else:
                        st.warning("Call ID und Aktion sind Pflichtfelder")
            
            with st.expander("Auto-Dialer-Kampagne", expanded=False):
                st.markdown("**Automatische Anrufkampagne für Kontakte mit Tag**")

                col1, col2 = st.columns(2)
                with col1:
                    dialer_tag = st.text_input("Kontakt-Tag", placeholder="lead", key="dialer_tag")
                    dialer_goal = st.text_input("Kampagnenziel", placeholder="Beratungstermin vereinbaren", key="dialer_goal")
                with col2:
                    dialer_max = st.number_input("Max. Anrufe", min_value=1, max_value=100, value=10, key="dialer_max")

                if st.button("Kampagne starten", key="start_campaign"):
                    if dialer_tag and dialer_goal:
                        dialer_snippet = (
                            "auto_dialer_campaign(\n"
                            f"    contact_tag='{dialer_tag}',\n"
                            f"    call_goal='{dialer_goal}',\n"
                            f"    max_calls={dialer_max}\n"
                            ")"
                        )
                        st.code(dialer_snippet)
                    else:
                        st.warning("Tag und Ziel sind Pflichtfelder")
            
            with st.expander(" Weitere Features", expanded=False):
                st.markdown("**Zusätzliche Telefonie-Tools**")
                
                # Call Tags
                st.markdown("**Anruf-Tags hinzufügen:**")
                col1, col2 = st.columns(2)
                with col1:
                    tag_call_id = st.text_input("Call ID", placeholder="CALL-12345678", key="tag_call_id")
                with col2:
                    call_tags = st.text_input("Tags", placeholder="wichtig,hot-lead", key="call_tags")
                if st.button("Tags hinzufügen", key="add_tags"):
                    if tag_call_id and call_tags:
                        st.code(f"add_call_tags('{tag_call_id}', '{call_tags}')")
                
                st.markdown("---")
                
                # Conference Call
                st.markdown("**Konferenzschaltung:**")
                col1, col2 = st.columns(2)
                with col1:
                    conf_call_id = st.text_input("Konferenz-Anruf-ID", placeholder="CALL-12345678", key="conf_call_id")
                with col2:
                    conf_participant = st.text_input("Teilnehmer hinzufügen", placeholder="+49301234567", key="conf_participant")
                if st.button("Teilnehmer hinzufügen", key="add_participant"):
                    if conf_call_id and conf_participant:
                        st.code(f"conference_call_add_participant('{conf_call_id}', '{conf_participant}')")
                
                st.markdown("---")
                
                # DND Mode
                st.markdown("**Bitte nicht stören:**")
                col1, col2 = st.columns(2)
                with col1:
                    dnd_enabled = st.checkbox("Aktivieren", key="dnd_enabled")
                with col2:
                    dnd_until = st.text_input("Bis (YYYY-MM-DD HH:MM)", placeholder="2024-01-15 17:00", key="dnd_until")
                if st.button("DND setzen", key="set_dnd"):
                    if dnd_until:
                        st.code(f"set_do_not_disturb({str(dnd_enabled)}, '{dnd_until}')")
                    else:
                        st.code(f"set_do_not_disturb({str(dnd_enabled)})")
                
                st.markdown("---")
                
                # Call Routing
                st.markdown("**Anruf-Routing konfigurieren:**")
                routing_rules = st.text_area("Routing-Regeln (JSON)", 
                    placeholder='{"vip": "agent1", "support": "agent2", "sales": "agent3"}',
                    key="routing_rules", height=100)
                if st.button("Routing aktivieren", key="enable_routing"):
                    if routing_rules:
                        st.code(f"enable_call_routing('{routing_rules}')")
                
                st.markdown("---")
                
                # Voicemail
                st.markdown("**Voicemail prüfen:**")
                voicemail_box = st.text_input("Mailbox", placeholder="default", key="voicemail_box")
                if st.button("Voicemail abrufen", key="check_voicemail"):
                    if voicemail_box:
                        st.code(f"check_voicemail('{voicemail_box}')")
                    else:
                        st.code("check_voicemail()")

    # Task input with tooltip (Task 13.2)
    tooltip_html = (
        "<div style=\"margin-bottom: 5px;\">\n"
        "    <span style=\"font-size: 14px; color: #666;\">\n"
        "     <b>Hinweis:</b> Beschreiben Sie konkret, was Sie möchten. Nennen Sie Parameter, Anforderungen und das erwartete Ergebnis.\n"
        "    </span>\n"
        "</div>\n"
    )
    st.markdown(tooltip_html, unsafe_allow_html=True)

    # Task input
    user_task = st.text_area(
        "Aufgabe eingeben:",
        height=100,
        placeholder="Beschreiben Sie, was der Agent tun soll...",
        key="agent_task_input"
    )

    # Control buttons with tooltips (Task 13.2)
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        start_button = st.button(
            "Agent starten",
            type="primary",
            use_container_width=True,
            help="Führt die oben eingegebene Aufgabe aus. Der Agent nutzt seine Tools, um Ihre Anfrage zu erledigen."
        )

    with col2:
        clear_memory = st.button(
            "Speicher leeren",
            use_container_width=True,
            help="Löscht den Gesprächsspeicher des Agents. Nutzen Sie dies, um mit neuem Kontext zu starten."
        )

    with col3:
        show_status = st.button(
            "Status anzeigen",
            use_container_width=True,
            help="Zeigt den aktuellen Agent-Status und die Konfiguration an.")

    # Handle clear memory
    if clear_memory:
        if st.session_state.agent_core is not None and hasattr(st.session_state.agent_core, 'clear_memory'):
            st.session_state.agent_core.clear_memory()
            st.success("Speicher geleert!")
        else:
            st.warning("Agent nicht initialisiert - kann Memory nicht löschen.")
        st.rerun()

    # Handle show status
    if show_status:
        if st.session_state.agent_core is not None:
            status = st.session_state.agent_core.get_status()
            st.json(status)
        else:
            st.warning("Agent nicht initialisiert - kein Status verfügbar.")

    st.markdown("---")

    # Execute agent task (optimized execution loop)
    if start_button and user_task:
        # Check if agent is initialized
        if st.session_state.agent_core is None:
            st.error("Agent nicht initialisiert. Bitte OpenAI API Key konfigurieren.")
            st.stop()
        
        # Validate user input (Task 12.1)
        try:
            sanitize_user_input(user_task, max_length=10000)
        except InputValidationError as e:
            st.error(f"Input validation failed: {str(e)}")
            st.stop()

        st.markdown("###  Agent Execution")

        # Initialize async execution state if not exists
        if 'async_state' not in st.session_state:
            st.session_state.async_state = AsyncExecutionState()

        # Start async execution
        if not st.session_state.async_state.is_running():
            st.session_state.async_state.start(
                st.session_state.agent_core,
                user_task
            )

        # Create containers for real-time updates (efficient rendering)
        status_container = st.container()
        result_container = st.container()

        # Show progress while running (optimized with fewer reruns)
        with status_container:
            if st.session_state.async_state.is_running():
                # Efficient progress display
                progress_bar = st.progress(0)
                status_text = st.empty()
                elapsed_text = st.empty()

                # Update progress with adaptive rerun frequency
                max_iterations = 50  # Reduced from 100 for fewer reruns
                for i in range(max_iterations):
                    if not st.session_state.async_state.is_running():
                        break

                    # Get current progress
                    progress = st.session_state.async_state.get_progress()
                    elapsed = st.session_state.async_state.get_elapsed_time()

                    # Update UI
                    progress_bar.progress(progress / 100.0)
                    status_text.markdown(
                        f" Agent is thinking... ({progress}%)"
                    )
                    elapsed_text.caption(f"⏱ Elapsed: {elapsed:.1f}s")

                    # Adaptive sleep (longer sleep = fewer reruns)
                    time.sleep(0.2)

                    # Rerun only every 5 iterations (reduce rerun frequency)
                    if i % 5 == 0:
                        st.rerun()

                # Clear progress when done
                if not st.session_state.async_state.is_running():
                    progress_bar.empty()
                    status_text.empty()
                    elapsed_text.empty()

        # Check if execution completed
        if not st.session_state.async_state.is_running():
            result = st.session_state.async_state.get_result()
            error = st.session_state.async_state.get_error()

            if error:
                st.error(f"Unexpected error: {error}")
            elif result:
                # Display results with streaming mode
                with result_container:
                    format_agent_output(result, streaming=True)

            # Reset state for next execution
            st.session_state.async_state = AsyncExecutionState()
        else:
            # Still running, trigger rerun with longer delay
            time.sleep(1.0)  # Increased from 0.5s
            st.rerun()

    # Footer
    st.markdown("---")
    st.caption(
        "Telefonagent O.M.I powered von Ömer"
    )


# Main execution
if __name__ == "__main__":
    render_agent_menu()
