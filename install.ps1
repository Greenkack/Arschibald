# ============================================================================
# BOKUK2 SOLAR CALCULATOR - WINDOWS INSTALLER SCRIPT
# ============================================================================
# Automatische Installation auf Windows mit PowerShell
# Führt alle notwendigen Schritte aus, um die App lauffähig zu machen
# ============================================================================

param(
    [string]$InstallPath = "$env:LOCALAPPDATA\Bokuk2",
    [switch]$SkipPythonCheck,
    [switch]$CreateDesktopShortcut
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "BOKUK2 SOLAR CALCULATOR - INSTALLATION" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# SCHRITT 1: Python Version prüfen
# ============================================================================
Write-Host "[1/8] Python Installation prüfen..." -ForegroundColor Yellow

if (-not $SkipPythonCheck) {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python gefunden: $pythonVersion" -ForegroundColor Green
        
        # Version extrahieren
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
                Write-Host "✗ Python 3.10 oder höher erforderlich!" -ForegroundColor Red
                Write-Host "  Bitte installieren Sie Python von: https://www.python.org/downloads/" -ForegroundColor Yellow
                exit 1
            }
        }
    }
    catch {
        Write-Host "✗ Python nicht gefunden!" -ForegroundColor Red
        Write-Host "  Bitte installieren Sie Python 3.10 oder höher von:" -ForegroundColor Yellow
        Write-Host "  https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
}

# ============================================================================
# SCHRITT 2: Installations-Verzeichnis erstellen
# ============================================================================
Write-Host ""
Write-Host "[2/8] Installations-Verzeichnis erstellen..." -ForegroundColor Yellow

if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-Host "✓ Verzeichnis erstellt: $InstallPath" -ForegroundColor Green
} else {
    Write-Host "✓ Verzeichnis existiert: $InstallPath" -ForegroundColor Green
}

# ============================================================================
# SCHRITT 3: Dateien kopieren
# ============================================================================
Write-Host ""
Write-Host "[3/8] Anwendungsdateien kopieren..." -ForegroundColor Yellow

$sourceDir = $PSScriptRoot
$filesToCopy = @(
    "*.py",
    "requirements.txt",
    ".env.example",
    "README.md"
)

$directoriesToCopy = @(
    "pdf_templates_static",
    "coords",
    "coords_multi",
    "coords_wp",
    "assets",
    "static",
    "json",
    ".streamlit",
    "pricing",
    "pdf_template_engine",
    "components",
    "core",
    "utils",
    "pages",
    "widgets",
    "theming"
)

# Python Dateien kopieren
foreach ($pattern in $filesToCopy) {
    $files = Get-ChildItem -Path $sourceDir -Filter $pattern -File
    foreach ($file in $files) {
        Copy-Item -Path $file.FullName -Destination $InstallPath -Force
    }
}
Write-Host "✓ Python Dateien kopiert" -ForegroundColor Green

# Verzeichnisse kopieren
foreach ($dir in $directoriesToCopy) {
    $sourcePath = Join-Path $sourceDir $dir
    if (Test-Path $sourcePath) {
        $destPath = Join-Path $InstallPath $dir
        Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
        Write-Host "✓ $dir kopiert" -ForegroundColor Green
    }
}

# ============================================================================
# SCHRITT 4: .env Datei erstellen
# ============================================================================
Write-Host ""
Write-Host "[4/8] Konfigurationsdatei erstellen..." -ForegroundColor Yellow

$envFile = Join-Path $InstallPath ".env"
$envExample = Join-Path $InstallPath ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item -Path $envExample -Destination $envFile
        Write-Host "✓ .env Datei erstellt aus .env.example" -ForegroundColor Green
    } else {
        # Erstelle minimale .env
        @"
# Bokuk2 Configuration
DATABASE_URL=sqlite:///./product_database.db
SECRET_KEY=$(New-Guid)
ENVIRONMENT=production
"@ | Out-File -FilePath $envFile -Encoding utf8
        Write-Host "✓ Standard .env Datei erstellt" -ForegroundColor Green
    }
} else {
    Write-Host "✓ .env Datei existiert bereits" -ForegroundColor Green
}

# ============================================================================
# SCHRITT 5: Virtuelle Umgebung erstellen
# ============================================================================
Write-Host ""
Write-Host "[5/8] Virtuelle Python-Umgebung erstellen..." -ForegroundColor Yellow

$venvPath = Join-Path $InstallPath ".venv"

if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
    Write-Host "✓ Virtuelle Umgebung erstellt" -ForegroundColor Green
} else {
    Write-Host "✓ Virtuelle Umgebung existiert" -ForegroundColor Green
}

# Aktiviere venv
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript

# ============================================================================
# SCHRITT 6: Dependencies installieren
# ============================================================================
Write-Host ""
Write-Host "[6/8] Python-Pakete installieren (kann mehrere Minuten dauern)..." -ForegroundColor Yellow

$requirementsFile = Join-Path $InstallPath "requirements.txt"

if (Test-Path $requirementsFile) {
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -r $requirementsFile
    Write-Host "✓ Alle Pakete installiert" -ForegroundColor Green
} else {
    Write-Host "✗ requirements.txt nicht gefunden!" -ForegroundColor Red
    exit 1
}

# ============================================================================
# SCHRITT 7: Datenbank initialisieren
# ============================================================================
Write-Host ""
Write-Host "[7/8] Datenbank initialisieren..." -ForegroundColor Yellow

$initScript = Join-Path $InstallPath "init_database.py"

if (Test-Path $initScript) {
    Set-Location $InstallPath
    python $initScript
    Write-Host "✓ Datenbank initialisiert" -ForegroundColor Green
} else {
    Write-Host "⚠ init_database.py nicht gefunden - Datenbank muss manuell initialisiert werden" -ForegroundColor Yellow
}

# ============================================================================
# SCHRITT 8: Startskript erstellen
# ============================================================================
Write-Host ""
Write-Host "[8/8] Startskript erstellen..." -ForegroundColor Yellow

# PowerShell Startskript
$startScript = @"
# Bokuk2 Solar Calculator - Starter
`$ErrorActionPreference = "Stop"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "BOKUK2 SOLAR CALCULATOR" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan

# Aktiviere virtuelle Umgebung
& "$venvPath\Scripts\Activate.ps1"

# Starte Streamlit
Write-Host ""
Write-Host "Starte Anwendung..." -ForegroundColor Yellow
Write-Host "Die App öffnet sich automatisch im Browser." -ForegroundColor Green
Write-Host ""
Write-Host "Zum Beenden: STRG+C drücken" -ForegroundColor Yellow
Write-Host ""

Set-Location "$InstallPath"
streamlit run gui.py

Write-Host ""
Write-Host "Anwendung beendet." -ForegroundColor Yellow
"@

$startScriptPath = Join-Path $InstallPath "start.ps1"
$startScript | Out-File -FilePath $startScriptPath -Encoding utf8
Write-Host "✓ Startskript erstellt: start.ps1" -ForegroundColor Green

# Batch-Datei für einfacheren Start
$batchScript = @"
@echo off
powershell -ExecutionPolicy Bypass -File "$startScriptPath"
pause
"@

$batchPath = Join-Path $InstallPath "start.bat"
$batchScript | Out-File -FilePath $batchPath -Encoding ascii
Write-Host "✓ Batch-Datei erstellt: start.bat" -ForegroundColor Green

# ============================================================================
# Desktop-Verknüpfung erstellen (optional)
# ============================================================================
if ($CreateDesktopShortcut) {
    Write-Host ""
    Write-Host "[OPTIONAL] Desktop-Verknüpfung erstellen..." -ForegroundColor Yellow
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Bokuk2 Solar Calculator.lnk")
    $Shortcut.TargetPath = $batchPath
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.IconLocation = "powershell.exe,0"
    $Shortcut.Description = "Bokuk2 Solar Calculator - PV Anlagen Kalkulation"
    $Shortcut.Save()
    
    Write-Host "✓ Desktop-Verknüpfung erstellt" -ForegroundColor Green
}

# ============================================================================
# INSTALLATION ABGESCHLOSSEN
# ============================================================================
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "INSTALLATION ERFOLGREICH ABGESCHLOSSEN!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installations-Pfad: $InstallPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "So starten Sie die Anwendung:" -ForegroundColor Yellow
Write-Host "  1. Doppelklick auf: $batchPath" -ForegroundColor White
Write-Host "  2. ODER: PowerShell öffnen und ausführen: $startScriptPath" -ForegroundColor White
if ($CreateDesktopShortcut) {
    Write-Host "  3. ODER: Desktop-Verknüpfung verwenden" -ForegroundColor White
}
Write-Host ""
Write-Host "Die App öffnet sich automatisch im Browser unter: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Bei Problemen:" -ForegroundColor Yellow
Write-Host "  - Prüfen Sie die Logs im Terminal" -ForegroundColor White
Write-Host "  - Stellen Sie sicher, dass Port 8501 nicht belegt ist" -ForegroundColor White
Write-Host "  - Kontaktieren Sie den Support: support@bokuk2.com" -ForegroundColor White
Write-Host ""

# Frage ob App sofort gestartet werden soll
$response = Read-Host "Möchten Sie die App jetzt starten? (J/N)"
if ($response -eq "J" -or $response -eq "j") {
    Write-Host ""
    Write-Host "Starte Anwendung..." -ForegroundColor Green
    & $batchPath
}
