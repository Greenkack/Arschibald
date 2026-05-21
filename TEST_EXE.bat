@echo off
chcp 65001 >nul
title ARSCHIBALD - Test der erstellten EXE

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  ARSCHIBALD - EXE Tester                       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

set EXE_PATH=dist\ARSCHIBALD\ARSCHIBALD.exe
set SETUP_PATH=ARSCHIBALD_Setup_v2.0.0.exe
set ZIP_PATH=ARSCHIBALD_Portable_v2.0.0.zip

echo Prüfe Build-Ergebnisse...
echo.

REM Prüfe EXE
if exist "%EXE_PATH%" (
    echo ✓ EXE gefunden: %EXE_PATH%
    for %%A in ("%EXE_PATH%") do (
        set SIZE=%%~zA
    )
    call :formatSize %SIZE%
) else (
    echo ❌ EXE nicht gefunden: %EXE_PATH%
    echo.
    echo Bitte erst BUILD_EXE.bat ausführen!
    pause
    exit /b 1
)

echo.

REM Prüfe Setup-Installer
if exist "%SETUP_PATH%" (
    echo ✓ Setup-Installer gefunden: %SETUP_PATH%
    for %%A in ("%SETUP_PATH%") do (
        set SIZE=%%~zA
    )
    call :formatSize %SIZE%
) else (
    echo ⚠ Setup-Installer nicht gefunden: %SETUP_PATH%
    echo   (Optional - benötigt Inno Setup)
)

echo.

REM Prüfe Portable ZIP
if exist "%ZIP_PATH%" (
    echo ✓ Portable ZIP gefunden: %ZIP_PATH%
    for %%A in ("%ZIP_PATH%") do (
        set SIZE=%%~zA
    )
    call :formatSize %SIZE%
) else (
    echo ⚠ Portable ZIP nicht gefunden: %ZIP_PATH%
)

echo.
echo ════════════════════════════════════════════════════════════════
echo.

REM Menü
:menu
echo Was möchtest du testen?
echo.
echo [1] Starte EXE (Entwicklermodus mit Console)
echo [2] Starte EXE (Produktionsmodus ohne Console)
echo [3] Prüfe EXE-Abhängigkeiten
echo [4] Teste Setup-Installer (Installation)
echo [5] Entpacke Portable ZIP
echo [6] Alle Tests durchführen
echo [7] Öffne dist-Verzeichnis
echo [0] Beenden
echo.

set /p choice="Wähle Option (0-7): "

if "%choice%"=="1" goto test_exe_console
if "%choice%"=="2" goto test_exe_production
if "%choice%"=="3" goto test_dependencies
if "%choice%"=="4" goto test_installer
if "%choice%"=="5" goto test_portable
if "%choice%"=="6" goto test_all
if "%choice%"=="7" goto open_dist
if "%choice%"=="0" goto end

echo Ungültige Auswahl!
echo.
goto menu

:test_exe_console
echo.
echo Starte EXE im Entwicklermodus...
echo Console bleibt offen für Debugging.
echo.
echo Drücke Strg+C im neuen Fenster zum Beenden.
echo.
start cmd /k "cd /d dist\ARSCHIBALD && ARSCHIBALD.exe"
echo.
echo ✓ EXE gestartet in neuem Fenster
echo.
pause
goto menu

:test_exe_production
echo.
echo Starte EXE im Produktionsmodus...
echo Browser sollte sich automatisch öffnen.
echo.
cd /d dist\ARSCHIBALD
start ARSCHIBALD.exe
cd /d "%~dp0"
echo.
echo ✓ EXE gestartet
echo ✓ Browser sollte http://localhost:8501 öffnen
echo.
pause
goto menu

:test_dependencies
echo.
echo Prüfe EXE-Abhängigkeiten...
echo.

if exist "dist\ARSCHIBALD\_internal" (
    echo ✓ _internal Verzeichnis gefunden
    dir /s /b "dist\ARSCHIBALD\_internal\*.pyd" 2>nul | find /c ".pyd"
    echo   Python Extensions gefunden
    echo.
    
    if exist "dist\ARSCHIBALD\_internal\streamlit" (
        echo ✓ Streamlit eingebunden
    ) else (
        echo ❌ Streamlit fehlt!
    )
    
    if exist "dist\ARSCHIBALD\_internal\pandas" (
        echo ✓ Pandas eingebunden
    ) else (
        echo ⚠ Pandas möglicherweise nicht gefunden
    )
    
    if exist "dist\ARSCHIBALD\_internal\reportlab" (
        echo ✓ ReportLab eingebunden
    ) else (
        echo ⚠ ReportLab möglicherweise nicht gefunden
    )
) else (
    echo ❌ _internal Verzeichnis nicht gefunden!
    echo    EXE möglicherweise beschädigt.
)

echo.
echo Weitere Dateien:
if exist "dist\ARSCHIBALD\data" (
    echo ✓ data\ Verzeichnis
) else (
    echo ⚠ data\ fehlt
)

if exist "dist\ARSCHIBALD\pdf_templates_static" (
    echo ✓ pdf_templates_static\ Verzeichnis
) else (
    echo ⚠ pdf_templates_static\ fehlt
)

if exist "dist\ARSCHIBALD\.streamlit" (
    echo ✓ .streamlit\ Verzeichnis
) else (
    echo ⚠ .streamlit\ fehlt
)

echo.
pause
goto menu

:test_installer
echo.
if not exist "%SETUP_PATH%" (
    echo ❌ Setup-Installer nicht gefunden!
    echo    Inno Setup erforderlich für Installer-Erstellung.
    echo.
    pause
    goto menu
)

echo ⚠ WARNUNG: Dies startet den echten Installer!
echo.
echo Der Installer wird die App nach C:\Program Files\ARSCHIBALD installieren.
echo Fortfahren? (J/N)
set /p confirm=
if /i not "%confirm%"=="J" goto menu

echo.
echo Starte Setup-Installer...
start %SETUP_PATH%
echo.
echo ✓ Installer gestartet
echo   Folge dem Installationsassistenten
echo.
pause
goto menu

:test_portable
echo.
if not exist "%ZIP_PATH%" (
    echo ❌ Portable ZIP nicht gefunden!
    echo.
    pause
    goto menu
)

echo Entpacke Portable Version...
echo.

set EXTRACT_DIR=test_portable
if exist "%EXTRACT_DIR%" (
    echo Lösche altes Test-Verzeichnis...
    rmdir /s /q "%EXTRACT_DIR%"
)

mkdir "%EXTRACT_DIR%"

echo Entpacke %ZIP_PATH% nach %EXTRACT_DIR%\...
powershell -command "Expand-Archive -Path '%ZIP_PATH%' -DestinationPath '%EXTRACT_DIR%' -Force"

if exist "%EXTRACT_DIR%\ARSCHIBALD" (
    echo ✓ Erfolgreich entpackt
    echo.
    echo Starte Portable Version...
    cd /d "%EXTRACT_DIR%\ARSCHIBALD"
    start ARSCHIBALD.exe
    cd /d "%~dp0"
    echo.
    echo ✓ Portable Version gestartet
) else (
    echo ❌ Entpacken fehlgeschlagen
)

echo.
pause
goto menu

:test_all
echo.
echo Führe alle Tests durch...
echo.
call :test_dependencies
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo Alle automatischen Tests abgeschlossen.
echo.
echo Manuelle Tests:
echo   - Starte EXE mit Option [1] oder [2]
echo   - Teste alle Funktionen der App
echo   - Prüfe ob Datenbank korrekt angelegt wird
echo   - Teste PDF-Generierung
echo   - Prüfe CRM-Funktionen
echo.
pause
goto menu

:open_dist
echo.
echo Öffne dist-Verzeichnis...
start explorer dist
echo.
goto menu

:formatSize
set SIZE=%1
if %SIZE% GEQ 1073741824 (
    set /a SIZE_GB=%SIZE:~0,-9%
    echo   Größe: %SIZE_GB% GB
) else if %SIZE% GEQ 1048576 (
    set /a SIZE_MB=%SIZE:~0,-6%
    echo   Größe: %SIZE_MB% MB
) else (
    set /a SIZE_KB=%SIZE:~0,-3%
    echo   Größe: %SIZE_KB% KB
)
goto :eof

:end
echo.
echo Auf Wiedersehen!
echo.
pause
