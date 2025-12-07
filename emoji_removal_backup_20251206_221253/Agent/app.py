# ==============================================================================
# 1. DATEI: app.py
# Haupt-Streamlit-Anwendung (stark aktualisiert)
# ==============================================================================
import io
import os
import sys
from contextlib import contextmanager

import streamlit as st
from agent.agent_core import AgentCore
from dotenv import load_dotenv

from agent.tools.knowledge_tools import setup_knowledge_base


# --- Hilfsfunktion zum Erfassen von Terminal-Ausgaben ---
@contextmanager
def st_capture(output_func):
    """Kontextmanager zum Erfassen von stdout/stderr in einer Streamlit-App."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = stdout
        sys.stderr = stderr
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            output = stdout.getvalue()
            if stderr.getvalue():
                output += "\n--- Errors ---\n" + stderr.getvalue()
            output_func(output)


# --- Streamlit UI Konfiguration ---
st.set_page_config(page_title="KAI Agent", layout="wide")
st.title("🤖 KAI - Autonomer KI-Branchenexperte")
st.subheader("Experte für Erneuerbare Energien & Software-Architektur")

# --- Initialisierung & API-Schlüssel-Prüfung ---
load_dotenv()
required_keys = [
    "OPENAI_API_KEY", "TAVILY_API_KEY", "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER", "ELEVEN_LABS_API_KEY"
]
missing_keys = [key for key in required_keys if not os.getenv(key)]

if missing_keys:
    st.error(
        f"FATALER FEHLER: Folgende API-Schlüssel fehlen in Ihrer .env-Datei: {
            ', '.join(missing_keys)}")
    st.warning("Bitte stellen Sie sicher, dass alle erforderlichen Schlüssel in Ihrer '.env'-Datei eingetragen sind. Starten Sie die App danach neu.")
    st.stop()

# --- Wissensdatenbank aufbauen ---
with st.spinner("Analysiere Fachwissen aus der Knowledge Base..."):
    # Diese Funktion lädt PDFs aus dem /knowledge_base Ordner und erstellt
    # eine Vektordatenbank
    vector_store = setup_knowledge_base()
    st.success(
        "Fachwissen erfolgreich indiziert und für den Agenten bereitgestellt!")

# Initialisieren des Agenten im Session State
if 'agent_core' not in st.session_state:
    with st.spinner("Experten-Agent wird initialisiert..."):
        st.session_state.agent_core = AgentCore(vector_store=vector_store)
    st.success("Agent ist bereit!")

# --- UI-Elemente ---
st.info("Experten-Upgrade! Der Agent ist jetzt ein Fachberater für Photovoltaik & Wärmepumpen und ein Software-Architekt. Beispiel: 'Durchsuche die Wissensdatenbank nach den technischen Vorteilen einer Kombination aus PV-Anlage und Wärmepumpe. Plane dann die Software-Architektur für eine Python-App, die die Amortisationszeit berechnet. Rufe danach einen potenziellen Kunden an, präsentiere ihm überzeugend die Top 3 Vorteile und biete an, ihm eine personalisierte Berechnung zu erstellen.'")

user_task = st.text_input("Ihre Aufgabe für KAI:", key="task_input")
start_button = st.button("Agenten starten", type="primary")

# Platzhalter für die Live-Ausgabe
output_placeholder = st.empty()

# --- Agenten-Logik ---
if start_button and user_task:
    output_placeholder.markdown("### 🧠 Denkprozess des Agenten...")
    log_container = st.container()

    with st_capture(log_container.code):
        try:
            st.session_state.agent_core.run(user_task)
        except Exception as e:
            st.error(
                f"Ein Fehler ist während der Ausführung des Agenten aufgetreten: {e}")
