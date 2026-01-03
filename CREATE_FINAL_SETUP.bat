@echo off
chcp 65001 >nul
cls
echo ========================================
echo   Ömers All in One DingsBums
echo   Setup-Erstellung (VOLLE GRÖSSE)
echo ========================================
echo.

echo Der PyInstaller Build ist fertig!
echo Größe: 2.7 GB mit 20.753 Dateien
echo.

echo Optionen zum Erstellen der finalen Setup-Datei:
echo.
echo [1] Inno Setup installieren und Setup.exe erstellen (~2.7 GB)
echo [2] ZIP-Archiv erstellen (portable, ~2.7 GB)
echo [3] Nur dist-Ordner nutzen (direkt lauffähig)
echo.
choice /C 123 /N /M "Wählen Sie eine Option (1, 2 oder 3): "

if errorlevel 3 goto OPTION3
if errorlevel 2 goto OPTION2
if errorlevel 1 goto OPTION1

:OPTION1
echo.
echo === Option 1: Inno Setup ===
echo.
echo Inno Setup wird benötigt, um eine professionelle Setup.exe zu erstellen.
echo.
echo Download: https://jrsoftware.org/isdl.php
echo.
echo Nach der Installation von Inno Setup:
echo 1. Führen Sie dieses Script erneut aus ODER
echo 2. Öffnen Sie "SETUP_FULL_NO_COMPRESSION.iss" in Inno Setup Compiler
echo.
echo Die Setup.exe wird dann in: setup_output\
echo.
where iscc >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Inno Setup gefunden! Erstelle Setup.exe...
    echo.
    if not exist "setup_output" mkdir "setup_output"
    iscc "SETUP_FULL_NO_COMPRESSION.iss"
    if %errorlevel% equ 0 (
        echo.
        echo ✓ Setup.exe erfolgreich erstellt!
        explorer "setup_output"
    )
) else (
    echo ⚠ Inno Setup nicht gefunden. Bitte installieren Sie es von:
    echo    https://jrsoftware.org/isdl.php
    start https://jrsoftware.org/isdl.php
)
goto END

:OPTION2
echo.
echo === Option 2: ZIP-Archiv ===
echo.
echo Erstelle ZIP-Archiv von dist-Ordner...
echo Dies kann einige Minuten dauern...
echo.

if not exist "portable_release" mkdir "portable_release"

powershell -Command "Compress-Archive -Path 'dist\Ömers All in One Dingsbums' -DestinationPath 'portable_release\Oemers_All_in_One_DingsBums_Portable.zip' -Force -CompressionLevel Optimal"

if %errorlevel% equ 0 (
    echo.
    echo ✓ ZIP-Archiv erfolgreich erstellt!
    echo.
    echo Speicherort: portable_release\Oemers_All_in_One_DingsBums_Portable.zip
    echo.
    echo Zum Installieren:
    echo 1. ZIP entpacken
    echo 2. "Ömers All in One Dingsbums.exe" ausführen
    echo.
    explorer "portable_release"
) else (
    echo ✗ Fehler beim Erstellen des ZIP-Archivs
)
goto END

:OPTION3
echo.
echo === Option 3: Direkt dist-Ordner nutzen ===
echo.
echo Der dist-Ordner enthält bereits alles und ist direkt lauffähig!
echo.
echo Speicherort: dist\Ömers All in One Dingsbums\
echo Größe: 2.7 GB
echo Dateien: 20.753
echo.
echo Zum Starten: Ömers All in One Dingsbums.exe ausführen
echo.
echo Optional: Können Sie den gesamten Ordner kopieren und woanders nutzen.
echo.
explorer "dist\Ömers All in One Dingsbums"
goto END

:END
echo.
echo ========================================
echo   Fertig!
echo ========================================
pause
