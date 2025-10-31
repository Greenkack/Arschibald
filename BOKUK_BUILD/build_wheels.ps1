param(
    [string]$PythonExe = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Abort($m) { Write-Host $m -ForegroundColor Red; exit 1 }

if (-not $PythonExe) {
    $pe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($pe) { $PythonExe = $pe } else { Abort "PythonExe nicht angegeben und 'python' nicht in PATH." }
}

if (-not (Test-Path $PythonExe)) { Abort "PythonExe nicht gefunden: $PythonExe" }

Write-Host "Benutze Python: $PythonExe"

# Erzeuge wheelhouse (simple)
$req = Join-Path $PSScriptRoot 'app\requirements.txt'
$dest = Join-Path $PSScriptRoot 'wheelhouse'
if (-not (Test-Path $req)) { Abort "requirements.txt nicht gefunden: $req" }

# Erstelle wheelhouse Dir falls nötig
if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Path $dest | Out-Null }

Write-Host "Starte pip download -r ..."
& $PythonExe -m pip download -r $req -d $dest

Write-Host "Fertig. Prüfe wheelhouse auf fehlende Wheels."
