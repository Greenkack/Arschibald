@echo off
setlocal
REM Startet die App innerhalb der mitgelieferten venv per Streamlit, öffnet Browser separat
set THIS=%~dp0
set VENV=%THIS%venv
set PY=%VENV%\Scripts\python.exe
set STREAMLIT=%VENV%\Scripts\streamlit.exe
set APPDIR=%THIS%app

if not exist "%PY%" (
	echo Python in venv nicht gefunden: %PY%
	pause
	exit /b 1
)

pushd "%APPDIR%"
REM Optional: eigenen Port setzen via STREAMLIT_SERVER_PORT Env var
if not defined STREAMLIT_SERVER_PORT set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set STREAMLIT_HEADLESS=true
start "" cmd /c start http://localhost:%STREAMLIT_SERVER_PORT%/
"%STREAMLIT%" run gui.py --server.headless=true --server.port=%STREAMLIT_SERVER_PORT%
popd
endlocal
