@echo off
REM install.bat - wrapper to run install.ps1 with elevation handled inside the PS script
setlocal
chcp 65001 >nul
echo Starte Installer (powershell)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
echo.
echo Druecken Sie eine Taste, um dieses Fenster zu schliessen...
pause >nul
endlocal
