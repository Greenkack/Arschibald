@echo off
title ARSCHIBALD - Starte Anwendung...

echo.
echo ====================================
echo  ARSCHIBALD v2.0.0
echo ====================================
echo.
echo Starte Anwendung...
echo.

cd /d "%~dp0"

REM Prüfe ob Datenbank existiert
if not exist "data\app_data.db" (
    echo Erstelle Datenbank...
    mkdir data 2>nul
)

REM Starte Streamlit App
echo Öffne Browser...
start http://localhost:8501

REM Starte Hauptanwendung
"ARSCHIBALD.exe"

if errorlevel 1 (
    echo.
    echo FEHLER: Anwendung konnte nicht gestartet werden!
    echo Bitte prüfen Sie die Logs unter logs\app.log
    echo.
    pause
)
