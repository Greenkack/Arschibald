# install.ps1
param(
    [switch]$NoPause
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Log($msg) {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$t  $msg" | Tee-Object -FilePath (Join-Path $PSScriptRoot 'install.log') -Append
}

function IsElevated {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($id)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

### Pruefe fruehzeitig, ob Elevation wirklich noetig ist (bei per-user Pfad NICHT erforderlich)
$APPDIR = $PSScriptRoot
$LocalPrograms = Join-Path $env:LOCALAPPDATA 'Programs'
if (-not (IsElevated)) {
    if ($APPDIR -like "$LocalPrograms*") {
        Log "Nicht elevated, per-user Pfad erkannt ($APPDIR) - fahre ohne UAC fort."
    } else {
        Log "Nicht elevated: Neustart mit Administrator-Rechten..."
        $pwsh = (Get-Command powershell -ErrorAction SilentlyContinue).Source
        if (-not $pwsh) { throw "PowerShell nicht gefunden - bitte Skript als Administrator starten." }
        Start-Process -FilePath $pwsh -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-File","`"$PSCommandPath`"" -Verb RunAs
        exit 0
    }
}

Log "=== INSTALL START ($(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) ==="
$PYEMBZIP = Join-Path $APPDIR 'python-embed.zip'
$PYDIR = Join-Path $APPDIR 'python_embed'
$WHDIR = Join-Path $APPDIR 'wheelhouse'
$REQ = Join-Path $APPDIR 'app\requirements.txt'
$LOG = Join-Path $APPDIR 'install.log'

try {
    if (-not (Test-Path $PYEMBZIP)) { Log "FEHLER: python-embed.zip nicht gefunden: $PYEMBZIP"; throw "python-embed.zip fehlt" }
    if (-not (Test-Path $WHDIR)) { Log "FEHLER: wheelhouse nicht gefunden: $WHDIR"; throw "wheelhouse fehlt" }
    if (-not (Test-Path $REQ)) { Log "FEHLER: requirements.txt nicht gefunden: $REQ"; throw "requirements.txt fehlt" }

    if (Test-Path $PYDIR) {
        Log "Vorhandenes python_embed gefunden: $PYDIR - versuche zu entfernen..."
        try {
            # Attribute normalisieren und loeschen ohne externe Tools
            Get-ChildItem -Path $PYDIR -Recurse -Force -ErrorAction SilentlyContinue |
                ForEach-Object { try { $_.Attributes = 'Normal' } catch {} }

            Remove-Item -LiteralPath $PYDIR -Recurse -Force -ErrorAction Stop
            Log "Altes python_embed entfernt."
        } catch {
            Log "WARN: Entfernen python_embed fehlgeschlagen: $($_.Exception.Message). Versuche Umbenennen und erneutes Loeschen..."
            try {
                $tmp = "$PYDIR._old_$(Get-Random)"
                Rename-Item -LiteralPath $PYDIR -NewName (Split-Path $tmp -Leaf) -ErrorAction Stop
                Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction Stop
                Log "Umbenennen+Loeschen erfolgreich."
            } catch {
                Log "WARN: Auch Umbenennen+Loeschen fehlgeschlagen: $($_.Exception.Message)"
            }
        }
    }

    Log "[1/6] Entpacke Embeddable Python..."
    Expand-Archive -Path $PYEMBZIP -DestinationPath $PYDIR -Force

    $PY = Join-Path $PYDIR 'python.exe'
    if (-not (Test-Path $PY)) { Log "FEHLER: python.exe nicht gefunden in $PYDIR"; throw "python.exe fehlt" }

    # ._pth konfigurieren: import site aktivieren und relevante Pfade hinzufügen
    $pth = Get-ChildItem -Path $PYDIR -Filter 'python*._pth' -File | Select-Object -First 1
    if (-not $pth) { Log "FEHLER: *._pth nicht gefunden in $PYDIR"; throw "pth fehlt" }
    $PTHFILE = $pth.FullName
    $SITEPKG_TOP = Join-Path $PYDIR 'site-packages'
    $SITEPKG_LIB = Join-Path $PYDIR 'Lib\\site-packages'
    if (-not (Test-Path $SITEPKG_TOP)) { New-Item -ItemType Directory -Path $SITEPKG_TOP | Out-Null }

    $pthText = Get-Content -Raw -Path $PTHFILE
    $origPthText = $pthText
    # 1) import site: Zeile ggf. einkommentieren oder hinzufügen
    if ($pthText -match '(?im)^[ \t]*#\s*import\s+site\s*$') {
        $pthText = $pthText -replace '(?im)^[ \t]*#\s*import\s+site\s*$', 'import site'
    } elseif ($pthText -notmatch '(?im)^[ \t]*import\s+site\s*$') {
        if ($pthText -notmatch "`n$") { $pthText += "`r`n" }
        $pthText += "import site`r`n"
    }
    # 2) Pfade sicherstellen
    # Stelle sicher, dass am Ende ein Zeilenumbruch vorhanden ist, bevor wir neue Zeilen anfuegen
    if ($pthText -notmatch "(\r?\n)$") { $pthText += "`r`n" }
    if ($pthText -notmatch '(?im)^[ \t]*\.\\site-packages\s*$') {
        $pthText += ".\\site-packages`r`n"
    }
    if ($pthText -notmatch '(?im)^[ \t]*Lib\s*$') {
        $pthText += "Lib`r`n"
    }
    if ($pthText -notmatch '(?im)^[ \t]*\.\\Lib\\site-packages\s*$') {
        $pthText += ".\\Lib\\site-packages`r`n"
    }
    if ($pthText -ne $origPthText) {
        Set-Content -Path $PTHFILE -Value $pthText -Encoding ASCII
        Log "_pth aktualisiert: import site + site-packages-Pfade gesetzt"
    }

    # pip wheel extrahieren
    $pipWheel = Get-ChildItem -Path $WHDIR -Filter 'pip-*.whl' -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $pipWheel) { Log "FEHLER: Kein pip-*.whl im wheelhouse gefunden."; throw "pip wheel fehlt" }
    Log "[2/6] Extrahiere pip: $($pipWheel.Name)"
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    # Korrigiere Zielverzeichnis: in das Top-Level site-packages entpacken
    [System.IO.Compression.ZipFile]::ExtractToDirectory($pipWheel.FullName, $SITEPKG_TOP)

    # Ensure Scripts dir exists
    $ScriptsDir = Join-Path $PYDIR 'Scripts'
    if (-not (Test-Path $ScriptsDir)) { New-Item -ItemType Directory -Path $ScriptsDir | Out-Null }

    # Update PATH for this process so pip tool scripts are found
    $env:PATH = "$ScriptsDir;$env:PATH"

    Log "[3/6] Installiere setuptools/wheel (offline, falls vorhanden)"
    $setwhl = Get-ChildItem -Path $WHDIR -Filter 'setuptools-*.whl' -File -ErrorAction SilentlyContinue | Select-Object -First 1
    $wheelwhl = Get-ChildItem -Path $WHDIR -Filter 'wheel-*.whl' -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($setwhl) { & "$PY" -m pip install --no-index --find-links "$WHDIR" "$($setwhl.FullName)" 2>&1 | Tee-Object -FilePath $LOG -Append }
    if ($wheelwhl) { & "$PY" -m pip install --no-index --find-links "$WHDIR" "$($wheelwhl.FullName)" 2>&1 | Tee-Object -FilePath $LOG -Append }

    Log "[4/6] Stelle Build-Tools bereit (build, packaging, pyproject_hooks) - falls vorhanden"
    foreach ($n in @('build','packaging','pyproject_hooks')) {
        $w = Get-ChildItem -Path $WHDIR -Filter "$n*.whl" -File -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($w) { & "$PY" -m pip install --no-index --find-links "$WHDIR" "$($w.FullName)" 2>&1 | Tee-Object -FilePath $LOG -Append }
    }

    Log "[5/6] Installiere App-Abhaengigkeiten offline aus wheelhouse (Versuch 1: --no-build-isolation)"
    $installSucceeded = $false
    try {
        & "$PY" -m pip install --no-index --find-links "$WHDIR" --no-build-isolation -r "$REQ" 2>&1 | Tee-Object -FilePath $LOG -Append
        $installSucceeded = $true
        Log "[6/6] Abhaengigkeiten installiert (no-build-isolation)."
    } catch {
        Log "WARN: Installation mit --no-build-isolation fehlgeschlagen: $($_.Exception.Message)"
        Log "Versuche Versuch 2: ohne --no-build-isolation"
        try {
            & "$PY" -m pip install --no-index --find-links "$WHDIR" -r "$REQ" 2>&1 | Tee-Object -FilePath $LOG -Append
            $installSucceeded = $true
            Log "[6/6] Abhaengigkeiten installiert (ohne no-build-isolation)."
        } catch {
            Log "FEHLER: pip Offline-Installation fehlgeschlagen (beide Strategien)."
            # Sammle Hinweise auf fehlende Wheels
            $tail = Get-Content -Path $LOG -Raw | Select-String -Pattern "No matching distribution found|Requires-Python|ERROR: Could not find" -AllMatches
            if ($tail) {
                Log "Fehlende / inkompatible Pakete (Auszug):"
                $tail.Matches | ForEach-Object { Log $_.Value }
            }
            New-Item -Path (Join-Path $APPDIR 'install.FAIL') -ItemType File -Force | Out-Null
            throw $_
        }
    }

    # mark success
    if ($installSucceeded) {
        New-Item -Path (Join-Path $APPDIR 'install.OK') -ItemType File -Force | Out-Null
        Log "=== INSTALL DONE ($(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) ==="
    if (-not $NoPause) { Read-Host -Prompt "Installation abgeschlossen. ENTER zum Schliessen" }
        exit 0
    }

} catch {
    Log "=== INSTALL ABGEBROCHEN ($(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) ==="
    Log "Exception: $($_.Exception.Message)"
    Write-Host "FEHLER während Installation. Siehe install.log im Installationsordner."
    if (-not $NoPause) { Read-Host -Prompt "Fehler. ENTER zum Schliessen" }
    exit 1
}
