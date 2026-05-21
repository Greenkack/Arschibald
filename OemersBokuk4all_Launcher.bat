@echo off
REM OemersBokuk4all Launcher - Wechselt ins richtige Verzeichnis
REM Verhindert PermissionError bei Ordner-Erstellung

cd /d "%~dp0"

REM Streamlit Config überschreiben
set STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false
set STREAMLIT_SERVER_PORT=8501

echo Starte OemersBokuk4all...
echo Working Directory: %CD%
echo.
OemersBokuk4all.exe
pause
