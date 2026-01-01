"""
gui_runner.py
Startet die Streamlit-App korrekt mit allen Parametern
"""
import sys
import os
from pathlib import Path

# Setze Arbeitsverzeichnis
if getattr(sys, 'frozen', False):
    # Wenn als EXE ausgeführt
    application_path = Path(sys.executable).parent
else:
    application_path = Path(__file__).parent

os.chdir(application_path)

# Umgebungsvariablen setzen
os.environ['STREAMLIT_SERVER_PORT'] = '8501'
os.environ['STREAMLIT_SERVER_ADDRESS'] = 'localhost'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Importiere und starte Streamlit
try:
    from streamlit.web import cli as stcli
    import streamlit
    
    print(f"Streamlit Version: {streamlit.__version__}")
    print(f"Working Directory: {os.getcwd()}")
    print("Starte {APP_NAME}...")
    
    # Starte mit gui.py
    sys.argv = ["streamlit", "run", "gui.py", 
                "--server.port=8501",
                "--server.headless=true",
                "--browser.gatherUsageStats=false"]
    
    sys.exit(stcli.main())
    
except Exception as e:
    print(f"FEHLER beim Start: {e}")
    import traceback
    traceback.print_exc()
    input("Drücken Sie Enter zum Beenden...")
    sys.exit(1)
