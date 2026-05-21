@echo off
setlocal enabledelayedexpansion
:: ============================================================================
:: Oemers All in One - Solar & Heatpump Calculator
:: Startskript für die Streamlit-Anwendung
:: ============================================================================

title Oemers All in One wird gestartet...

:: Wechsle ins Projektverzeichnis
cd /d "%~dp0"

:: Setze Standard-Port
set STREAMLIT_SERVER_PORT=8501

echo.
echo ========================================
echo    Oemers All in One wird gestartet...
echo ========================================
echo.

:: Prüfe ob Python verfügbar ist
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH!
    echo Bitte installieren Sie Python von https://www.python.org
    pause
    exit /b 1
)

echo Python gefunden: 
python --version
echo.

:: Pruefe ob Streamlit verfuegbar ist
python -c "import streamlit" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Streamlit ist nicht installiert!
    echo Installiere Streamlit...
    pip install streamlit
    if %ERRORLEVEL% NEQ 0 (
        echo Installation fehlgeschlagen!
        pause
        exit /b 1
    )
)

echo Initialisiere Controlling-Datenbank...
python -c "import sys; sys.path.insert(0, '.'); from controlling.database import init_controlling_db; init_controlling_db()" 2>nul

echo.
echo Pruefe ob Port 8501 verfuegbar ist...

:: Pruefe ob Port 8501 bereits belegt ist
netstat -ano | findstr ":8501" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo WARNUNG: Port 8501 ist bereits belegt!
    echo Es laeuft bereits eine Streamlit-Instanz.
    echo.
    echo Moechten Sie die laufende Instanz beenden? ^(J/N^)
    set /p answer=Ihre Wahl: 
    if /i "!answer!"=="J" (
        echo Beende laufende Streamlit-Prozesse...
        taskkill /F /IM streamlit.exe 2>nul
        taskkill /F /IM python.exe /FI "WINDOWTITLE eq *streamlit*" 2>nul
        timeout /t 2 /nobreak >nul
    ) else (
        echo Starte App auf alternativem Port 8502...
        set STREAMLIT_SERVER_PORT=8502
    )
)

echo.
echo Starte Streamlit-App...
echo.
echo Die App wird in Ihrem Browser geoeffnet.
echo Zum Beenden schliessen Sie dieses Fenster oder druecken Sie STRG+C
echo.
echo ========================================
echo.

:: Starte Streamlit mit explizitem Python-Aufruf
python -m streamlit run gui.py --server.port=%STREAMLIT_SERVER_PORT%

:: Fehlerbehandlung
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo FEHLER: App konnte nicht gestartet werden!
    echo Fehlercode: %ERRORLEVEL%
    echo ========================================
    echo.
    echo Versuchen Sie:
    echo   1. pip install -r requirements.txt
    echo   2. python gui.py (direkt ohne Streamlit)
    echo.
    pause
    exit /b %ERRORLEVEL%
)

pause
