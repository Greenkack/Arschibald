# ============================================================================
# POST-INSTALL VALIDATOR
# ============================================================================
# Überprüft nach der Installation, ob ALLES korrekt installiert ist
# ============================================================================

param(
    [string]$InstallDir = "C:\Program Files\OemersCalculatorAllInOne"
)

$ErrorActionPreference = 'Stop'

Write-Host "`n============================================================================" -ForegroundColor Cyan
Write-Host "POST-INSTALL VALIDATOR - Ömer's Calculator" -ForegroundColor Cyan
Write-Host "============================================================================`n" -ForegroundColor Cyan

$success = $true
$errors = @()
$warnings = @()

# ============================================================================
# VALIDIERUNGEN
# ============================================================================

Write-Host "[1/10] Prüfe Installationsverzeichnis..." -ForegroundColor Yellow

if (-not (Test-Path $InstallDir)) {
    $errors += "Installationsverzeichnis nicht gefunden: $InstallDir"
    $success = $false
}
else {
    Write-Host "  ✓ Installationsverzeichnis gefunden" -ForegroundColor Green
}

# ============================================================================

Write-Host "[2/10] Prüfe Python Embedded..." -ForegroundColor Yellow

$pyExe = Join-Path $InstallDir "python_embed\python.exe"
if (-not (Test-Path $pyExe)) {
    $errors += "Python nicht gefunden: $pyExe"
    $success = $false
}
else {
    $pyVersion = & "$pyExe" --version 2>&1
    Write-Host "  ✓ Python gefunden: $pyVersion" -ForegroundColor Green
}

# ============================================================================

Write-Host "[3/10] Prüfe App-Dateien..." -ForegroundColor Yellow

$appDir = Join-Path $InstallDir "app"
if (-not (Test-Path $appDir)) {
    $errors += "app-Verzeichnis nicht gefunden: $appDir"
    $success = $false
}
else {
    $guiPy = Join-Path $appDir "gui.py"
    if (-not (Test-Path $guiPy)) {
        $errors += "gui.py nicht gefunden"
        $success = $false
    }
    else {
        Write-Host "  ✓ gui.py gefunden" -ForegroundColor Green
    }
    
    # Zähle Dateien
    $fileCount = (Get-ChildItem -Path $appDir -Recurse -File).Count
    Write-Host "  ✓ $fileCount App-Dateien gefunden" -ForegroundColor Green
}

# ============================================================================

Write-Host "[4/10] Prüfe Core-Module..." -ForegroundColor Yellow

$coreDir = Join-Path $appDir "core"
if (-not (Test-Path $coreDir)) {
    $errors += "core-Verzeichnis nicht gefunden"
    $success = $false
}
else {
    $coreModules = @(
        'config.py', 'logging_config.py', 'logging_system.py', 'cache.py',
        'session.py', 'session_manager.py', 'session_persistence.py',
        'database.py', 'security.py', 'router.py', 'form_manager.py',
        'widgets.py', 'navigation_history.py', 'jobs.py', 'migrations.py',
        'cache_invalidation.py', 'cache_monitoring.py', 'cache_warming.py',
        'db_performance_monitor.py', 'db_query_builder.py'
    )
    
    $foundModules = 0
    $missingModules = @()
    
    foreach ($module in $coreModules) {
        $modulePath = Join-Path $coreDir $module
        if (Test-Path $modulePath) {
            $foundModules++
        }
        else {
            $missingModules += $module
        }
    }
    
    Write-Host "  ✓ $foundModules/$($coreModules.Count) Core-Module gefunden" -ForegroundColor Green
    
    if ($missingModules.Count -gt 0) {
        $warnings += "Fehlende Core-Module: $($missingModules -join ', ')"
    }
}

# ============================================================================

Write-Host "[5/10] Prüfe Python-Pakete..." -ForegroundColor Yellow

if (Test-Path $pyExe) {
    $criticalPackages = @(
        'streamlit', 'pandas', 'numpy', 'plotly', 'altair',
        'sqlalchemy', 'alembic', 'cryptography', 'PyMuPDF',
        'reportlab', 'openpyxl', 'Pillow'
    )
    
    $installedPackages = & "$pyExe" -m pip list 2>&1 | Out-String
    
    $foundPackages = 0
    $missingPackages = @()
    
    foreach ($pkg in $criticalPackages) {
        if ($installedPackages -match $pkg) {
            $foundPackages++
        }
        else {
            $missingPackages += $pkg
        }
    }
    
    Write-Host "  ✓ $foundPackages/$($criticalPackages.Count) kritische Pakete installiert" -ForegroundColor Green
    
    if ($missingPackages.Count -gt 0) {
        $errors += "Fehlende Pakete: $($missingPackages -join ', ')"
        $success = $false
    }
}

# ============================================================================

Write-Host "[6/10] Prüfe Datenbanken..." -ForegroundColor Yellow

$dataDir = Join-Path $appDir "data"
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    Write-Host "  ✓ data-Verzeichnis erstellt" -ForegroundColor Yellow
}
else {
    Write-Host "  ✓ data-Verzeichnis gefunden" -ForegroundColor Green
}

# ============================================================================

Write-Host "[7/10] Prüfe Streamlit-Konfiguration..." -ForegroundColor Yellow

$streamlitDir = Join-Path $appDir ".streamlit"
$streamlitConfig = Join-Path $streamlitDir "config.toml"

if (-not (Test-Path $streamlitConfig)) {
    $warnings += ".streamlit/config.toml nicht gefunden"
}
else {
    Write-Host "  ✓ Streamlit-Konfiguration gefunden" -ForegroundColor Green
}

# ============================================================================

Write-Host "[8/10] Prüfe Assets..." -ForegroundColor Yellow

$assetsDir = Join-Path $appDir "assets"
if (-not (Test-Path $assetsDir)) {
    $warnings += "assets-Verzeichnis nicht gefunden"
}
else {
    $iconFile = Join-Path $assetsDir "Kakerlack.ico"
    if (Test-Path $iconFile) {
        Write-Host "  ✓ App-Icon gefunden" -ForegroundColor Green
    }
    else {
        $warnings += "App-Icon nicht gefunden"
    }
}

# ============================================================================

Write-Host "[9/10] Prüfe Start-Skripte..." -ForegroundColor Yellow

$runCmd = Join-Path $InstallDir "run_app_embed.cmd"
$runPs1 = Join-Path $InstallDir "run_app_embed.ps1"

if (-not (Test-Path $runCmd)) {
    $errors += "run_app_embed.cmd nicht gefunden"
    $success = $false
}
elseif (-not (Test-Path $runPs1)) {
    $errors += "run_app_embed.ps1 nicht gefunden"
    $success = $false
}
else {
    Write-Host "  ✓ Start-Skripte gefunden" -ForegroundColor Green
}

# ============================================================================

Write-Host "[10/10] Teste Python-Import..." -ForegroundColor Yellow

if (Test-Path $pyExe) {
    $testImport = @"
import sys
import os
sys.path.insert(0, r'$appDir')

# Test critical imports
try:
    import streamlit
    import pandas
    import numpy
    import plotly
    print('OK')
except ImportError as e:
    print(f'ERROR: {e}')
"@
    
    $tempScript = Join-Path $env:TEMP "test_imports.py"
    Set-Content -Path $tempScript -Value $testImport
    
    $testResult = & "$pyExe" "$tempScript" 2>&1
    
    if ($testResult -match "OK") {
        Write-Host "  ✓ Python-Imports funktionieren" -ForegroundColor Green
    }
    else {
        $errors += "Python-Import-Test fehlgeschlagen: $testResult"
        $success = $false
    }
    
    Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
}

# ============================================================================
# ZUSAMMENFASSUNG
# ============================================================================

Write-Host "`n============================================================================" -ForegroundColor Cyan

if ($success) {
    Write-Host "✅ INSTALLATION VOLLSTÄNDIG UND FUNKTIONSFÄHIG!" -ForegroundColor Green
}
else {
    Write-Host "❌ INSTALLATION UNVOLLSTÄNDIG!" -ForegroundColor Red
}

if ($errors.Count -gt 0) {
    Write-Host "`nFEHLER:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  ✗ $error" -ForegroundColor Red
    }
}

if ($warnings.Count -gt 0) {
    Write-Host "`nWARNUNGEN:" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  ⚠ $warning" -ForegroundColor Yellow
    }
}

Write-Host "`n============================================================================" -ForegroundColor Cyan

if ($success) {
    Write-Host "`n🚀 Die App kann jetzt gestartet werden!" -ForegroundColor Green
    Write-Host "   Desktop-Icon: Ömer's Calculator All in One" -ForegroundColor Green
    Write-Host "   Oder: $runCmd`n" -ForegroundColor Green
}
else {
    Write-Host "`n⚠️ Bitte Installation reparieren:" -ForegroundColor Yellow
    Write-Host "   $InstallDir\install.ps1`n" -ForegroundColor Yellow
}

if (-not $success) {
    exit 1
}
