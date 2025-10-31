# run_app_embed.ps1
$APPDIR = $PSScriptRoot
$PY = Join-Path $APPDIR 'python_embed\python.exe'
$GUI = Join-Path $APPDIR 'app\gui.py'

if (-not (Test-Path $PY)) { Write-Host "python_embed/python.exe nicht gefunden"; exit 1 }
if (-not (Test-Path $GUI)) { Write-Host "app\gui.py nicht gefunden"; exit 1 }

# Use streamlit run. Adjust port if needed.
$port = 8501
Start-Process -FilePath $PY -ArgumentList "-m","streamlit","run",$GUI,"--server.port",$port,"--server.headless","true" -NoNewWindow
Start-Sleep -Seconds 1
# open default browser to app
Start-Process "http://localhost:$port"
