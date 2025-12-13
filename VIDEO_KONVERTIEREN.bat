@echo off
echo.
echo ======================================
echo VIDEO-KONVERTIERUNG STARTEN
echo ======================================
echo.
echo Starte PowerShell mit FFmpeg...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "convert_video_for_web.ps1" -Quality medium
echo.
echo Konvertierung abgeschlossen!
echo.
pause
