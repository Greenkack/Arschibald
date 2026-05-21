@echo off
chcp 65001 >nul
title ARSCHIBALD - EXE Setup Builder

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║         🚀 ARSCHIBALD - EXE Setup Builder v2.0                ║
echo ║                                                                ║
echo ║  Erstellt eine vollständige Windows-Installation mit:          ║
echo ║  ✓ Python Runtime eingebettet                                 ║
echo ║  ✓ Alle Dependencies                                          ║
echo ║  ✓ Setup-Installer (.exe)                                     ║
echo ║  ✓ Portable Version (.zip)                                    ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Prüfe Python
echo [1/5] Prüfe Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ FEHLER: Python nicht gefunden!
    echo.
    echo Bitte installieren Sie Python 3.10 oder höher:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python --version
echo ✓ Python gefunden
echo.

REM Prüfe pip
echo [2/5] Prüfe pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip nicht gefunden!
    pause
    exit /b 1
)
echo ✓ pip verfügbar
echo.

REM Installiere Dependencies
echo [3/5] Installiere Dependencies...
echo   Dies kann einige Minuten dauern...
echo.

if exist requirements.txt (
    python -m pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo ❌ Fehler bei Installation der Dependencies
        pause
        exit /b 1
    )
    echo ✓ Dependencies installiert
) else (
    echo ⚠ requirements.txt nicht gefunden
    echo   Installiere nur PyInstaller...
    python -m pip install pyinstaller --quiet
)

echo.

REM Installiere PyInstaller
echo [4/5] Prüfe PyInstaller...
python -m pip install pyinstaller --upgrade --quiet
echo ✓ PyInstaller bereit
echo.

REM Starte Build
echo [5/5] Starte Build-Prozess...
echo.
echo ════════════════════════════════════════════════════════════════
echo.

python build_exe_setup.py

if errorlevel 1 (
    echo.
    echo ════════════════════════════════════════════════════════════════
    echo.
    echo ❌ Build fehlgeschlagen!
    echo.
    echo Mögliche Ursachen:
    echo   - Fehlende Module (siehe Fehlerausgabe oben)
    echo   - Datei-Zugriffsfehler
    echo   - Unvollständige Installation
    echo.
    echo Tipps:
    echo   1. Prüfe die Fehlerausgabe oben
    echo   2. Stelle sicher dass requirements.txt vollständig ist
    echo   3. Führe aus: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo ✅ Build erfolgreich abgeschlossen!
echo.
echo Erstellte Dateien findest du unter:
echo   📁 dist\
echo.
echo Nächste Schritte:
echo   1. Teste die EXE: dist\ARSCHIBALD\ARSCHIBALD.exe
echo   2. Verteile Setup: ARSCHIBALD_Setup_v2.0.0.exe
echo   3. Oder nutze Portable: ARSCHIBALD_Portable_v2.0.0.zip
echo.
echo ════════════════════════════════════════════════════════════════
echo.

REM Öffne dist Verzeichnis
echo Öffne dist-Verzeichnis...
start explorer dist

echo.
echo Fertig! Drücke eine Taste zum Beenden...
pause >nul
