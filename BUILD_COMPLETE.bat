3@echo off
chcp 65001 >nul
cls
echo ========================================
echo   Ömers All in One DingsBums
echo   Kompletter Build-Prozess
echo ========================================
echo.

echo [1/3] Bereinige alte Builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo ✓ Bereinigung abgeschlossen
echo.

echo [2/3] Starte PyInstaller Build...
echo Dies kann 10-20 Minuten dauern...
echo.
pyinstaller --clean --noconfirm "ARSCHIBALD_COMPLETE.spec"

if %errorlevel% neq 0 (
    echo.
    echo ✗ FEHLER beim PyInstaller Build!
    pause
    exit /b 1
)

echo.
echo ✓ PyInstaller Build erfolgreich!
echo.

echo [3/3] Prüfe ob Inno Setup verfügbar ist...
where iscc >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Inno Setup gefunden - erstelle Setup.exe...
    echo.
    
    if not exist "setup_output" mkdir "setup_output"
    
    iscc "ARSCHIBALD_COMPLETE_SETUP.iss"
    
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo   ✓ SETUP ERFOLGREICH ERSTELLT!
        echo ========================================
        echo.
        echo Die Setup.exe befindet sich in: setup_output\
        echo.
        explorer "setup_output"
    ) else (
        echo ✗ Fehler beim Erstellen der Setup.exe
    )
) else (
    echo ⚠ Inno Setup nicht gefunden
    echo Download: https://jrsoftware.org/isdl.php
    echo.
    echo Die App befindet sich in: dist\Ömers All in One Dingsbums\
    echo Sie können die App direkt ausführen: dist\Ömers All in One Dingsbums\Ömers All in One Dingsbums.exe
    echo.
    explorer "dist\Ömers All in One Dingsbums"
)

echo.
echo Build-Prozess abgeschlossen!
pause
