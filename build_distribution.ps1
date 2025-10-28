# ============================================================================
# BOKUK2 SOLAR CALCULATOR - DISTRIBUTION BUILDER
# ============================================================================
# Erstellt ein vollständiges Installations-Paket
# ============================================================================

param(
    [string]$OutputDir = ".\dist",
    [switch]$CreateZip,
    [switch]$CreateInstaller,
    [switch]$BuildExe
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "BOKUK2 SOLAR CALCULATOR - DISTRIBUTION BUILDER" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# SCHRITT 1: Output-Verzeichnis vorbereiten
# ============================================================================
Write-Host "[1/6] Output-Verzeichnis vorbereiten..." -ForegroundColor Yellow

if (Test-Path $OutputDir) {
    Write-Host "⚠ Output-Verzeichnis existiert bereits - wird gelöscht" -ForegroundColor Yellow
    Remove-Item -Path $OutputDir -Recurse -Force
}

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
Write-Host "✓ Output-Verzeichnis erstellt: $OutputDir" -ForegroundColor Green

# ============================================================================
# SCHRITT 2: Erforderliche Dateien sammeln
# ============================================================================
Write-Host ""
Write-Host "[2/6] Erforderliche Dateien sammeln..." -ForegroundColor Yellow

$sourceDir = $PSScriptRoot
$stagingDir = Join-Path $OutputDir "staging"
New-Item -ItemType Directory -Path $stagingDir -Force | Out-Null

# Python Dateien
$pythonFiles = @(
    "*.py"
)

# Konfigurationsdateien
$configFiles = @(
    "requirements.txt",
    ".env.example",
    "README.md",
    "setup.py",
    "install.ps1"
)

# Verzeichnisse
$directories = @(
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
    "theming",
    "data",
    "locales",
    "cli",
    "tools"
)

# Kopiere Python Dateien (außer Test/Debug Dateien)
foreach ($pattern in $pythonFiles) {
    $files = Get-ChildItem -Path $sourceDir -Filter $pattern -File | 
             Where-Object { $_.Name -notmatch "^(test_|debug_|analyse_|check_|demo_|verify_)" }
    
    foreach ($file in $files) {
        Copy-Item -Path $file.FullName -Destination $stagingDir -Force
    }
}
Write-Host "✓ Python Dateien kopiert" -ForegroundColor Green

# Kopiere Konfigurationsdateien
foreach ($file in $configFiles) {
    $filePath = Join-Path $sourceDir $file
    if (Test-Path $filePath) {
        Copy-Item -Path $filePath -Destination $stagingDir -Force
    }
}
Write-Host "✓ Konfigurationsdateien kopiert" -ForegroundColor Green

# Kopiere Verzeichnisse
foreach ($dir in $directories) {
    $sourcePath = Join-Path $sourceDir $dir
    if (Test-Path $sourcePath) {
        $destPath = Join-Path $stagingDir $dir
        Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
        Write-Host "✓ $dir kopiert" -ForegroundColor Green
    }
}

# ============================================================================
# SCHRITT 3: README für Distribution erstellen
# ============================================================================
Write-Host ""
Write-Host "[3/6] README erstellen..." -ForegroundColor Yellow

$readmeContent = @"
# Bokuk2 Solar Calculator - Installation

## Systemanforderungen

- Windows 10 oder höher
- Python 3.10 oder höher
- Mindestens 2 GB freier Festplattenspeicher
- Internetverbindung für die Installation

## Schnellstart

### Option 1: Automatische Installation (Empfohlen)

1. Doppelklick auf ``install.bat``
2. Folgen Sie den Anweisungen auf dem Bildschirm
3. Nach erfolgreicher Installation: Doppelklick auf ``start.bat``

### Option 2: Manuelle Installation

1. Python 3.10 oder höher installieren von: https://www.python.org/downloads/
2. PowerShell als Administrator öffnen
3. Zum Installations-Verzeichnis navigieren
4. Ausführen: ``powershell -ExecutionPolicy Bypass -File install.ps1``
5. Nach Installation: ``powershell -ExecutionPolicy Bypass -File start.ps1``

## Erste Schritte

1. Nach dem Start öffnet sich die App automatisch im Browser
2. Standard-URL: http://localhost:8501
3. Beim ersten Start wird die Datenbank automatisch initialisiert
4. Standard-Admin-Login: admin / admin (bitte ändern!)

## Fehlerbehebung

### Port 8501 bereits belegt
``````
streamlit run gui.py --server.port 8502
``````

### Datenbank-Fehler
``````
python init_database.py
``````

### Fehlende Pakete
``````
pip install -r requirements.txt
``````

## Support

- GitHub: https://github.com/Greenkack/Arschibald
- Email: support@bokuk2.com

## Lizenz

MIT License - Siehe LICENSE Datei für Details
"@

$readmePath = Join-Path $stagingDir "INSTALLATION.md"
$readmeContent | Out-File -FilePath $readmePath -Encoding utf8
Write-Host "✓ INSTALLATION.md erstellt" -ForegroundColor Green

# ============================================================================
# SCHRITT 4: Batch-Installer erstellen
# ============================================================================
Write-Host ""
Write-Host "[4/6] Batch-Installer erstellen..." -ForegroundColor Yellow

$batchInstaller = @"
@echo off
echo ============================================================================
echo BOKUK2 SOLAR CALCULATOR - INSTALLATION
echo ============================================================================
echo.

REM Admin-Rechte prüfen
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Admin-Rechte: OK
) else (
    echo WARNUNG: Keine Admin-Rechte
    echo Einige Funktionen koennen eingeschraenkt sein
)

echo.
echo Starte Installation...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1" -CreateDesktopShortcut

echo.
echo Installation abgeschlossen!
echo.
pause
"@

$batchPath = Join-Path $stagingDir "install.bat"
$batchInstaller | Out-File -FilePath $batchPath -Encoding ascii
Write-Host "✓ install.bat erstellt" -ForegroundColor Green

# ============================================================================
# SCHRITT 5: PyInstaller Build (optional)
# ============================================================================
if ($BuildExe) {
    Write-Host ""
    Write-Host "[5/6] Standalone .exe erstellen (kann länger dauern)..." -ForegroundColor Yellow
    
    if (Get-Command pyinstaller -ErrorAction SilentlyContinue) {
        Set-Location $sourceDir
        pyinstaller bokuk2.spec --clean --noconfirm
        
        if (Test-Path ".\dist\Bokuk2_SolarCalculator") {
            Copy-Item -Path ".\dist\Bokuk2_SolarCalculator" -Destination $stagingDir -Recurse -Force
            Write-Host "✓ .exe Build erfolgreich" -ForegroundColor Green
        } else {
            Write-Host "⚠ .exe Build fehlgeschlagen" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠ PyInstaller nicht gefunden - .exe Build übersprungen" -ForegroundColor Yellow
        Write-Host "  Installieren mit: pip install pyinstaller" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "[5/6] .exe Build übersprungen (verwenden Sie -BuildExe zum Aktivieren)" -ForegroundColor Yellow
}

# ============================================================================
# SCHRITT 6: Distribution Package erstellen
# ============================================================================
Write-Host ""
Write-Host "[6/6] Distribution Package erstellen..." -ForegroundColor Yellow

if ($CreateZip) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $zipName = "Bokuk2_SolarCalculator_v2.0.0_$timestamp.zip"
    $zipPath = Join-Path $OutputDir $zipName
    
    Compress-Archive -Path "$stagingDir\*" -DestinationPath $zipPath -Force
    Write-Host "✓ ZIP erstellt: $zipName" -ForegroundColor Green
    
    # Größe anzeigen
    $zipSize = (Get-Item $zipPath).Length / 1MB
    Write-Host "  Größe: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan
}

# Final Package als Verzeichnis
$finalPackage = Join-Path $OutputDir "Bokuk2_SolarCalculator_Distribution"
if (Test-Path $finalPackage) {
    Remove-Item -Path $finalPackage -Recurse -Force
}
Move-Item -Path $stagingDir -Destination $finalPackage
Write-Host "✓ Distribution Package erstellt: Bokuk2_SolarCalculator_Distribution" -ForegroundColor Green

# ============================================================================
# FERTIG
# ============================================================================
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "DISTRIBUTION BUILD ERFOLGREICH!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output-Verzeichnis: $OutputDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Inhalt:" -ForegroundColor Yellow
Write-Host "  - Bokuk2_SolarCalculator_Distribution/ (Komplettes Package)" -ForegroundColor White

if ($CreateZip) {
    Write-Host "  - $zipName (ZIP Archiv)" -ForegroundColor White
}

Write-Host ""
Write-Host "Nächste Schritte:" -ForegroundColor Yellow
Write-Host "  1. Package testen: Zum Distribution-Verzeichnis navigieren" -ForegroundColor White
Write-Host "  2. install.bat ausführen" -ForegroundColor White
Write-Host "  3. start.bat ausführen" -ForegroundColor White
Write-Host ""
Write-Host "Für Distribution:" -ForegroundColor Yellow
if ($CreateZip) {
    Write-Host "  - ZIP-Datei an Benutzer verteilen" -ForegroundColor White
} else {
    Write-Host "  - Distribution-Verzeichnis als ZIP packen und verteilen" -ForegroundColor White
}
Write-Host ""
