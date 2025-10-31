# EINFACHER BUILD - OEMERS CALCULATOR SETUP
# Erstellt vollstaendige Setup.exe OHNE Syntax-Probleme

param(
    [switch]$SkipSync
)

$ErrorActionPreference = 'Stop'

Write-Host "`n==== OEMERS CALCULATOR - EINFACHER SETUP BUILDER ====" -ForegroundColor Cyan
Write-Host "Start: $(Get-Date)" -ForegroundColor Cyan

$BUILD_DIR = $PSScriptRoot
$ROOT_DIR = Split-Path $BUILD_DIR
$APP_DEST = Join-Path $BUILD_DIR "app"
$OUTPUT_DIR = Join-Path $BUILD_DIR "Output"
$INNO = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

# Schritt 1: App-Dateien syncen
if (-not $SkipSync) {
    Write-Host "`n[1/3] Synchronisiere App-Dateien..." -ForegroundColor Yellow
    
    if (Test-Path $APP_DEST) {
        Remove-Item $APP_DEST -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    $excludeDirs = 'venv','venv_*','.venv','__pycache__','.pytest_cache','.git','BOKUK_BUILD','dist','build','wheelhouse','python_embed','Output'
    
    $robocopyArgs = @($ROOT_DIR, $APP_DEST, '/E', '/NP', '/NFL', '/NDL', '/NJH', '/NJS', '/R:1', '/W:1')
    foreach ($dir in $excludeDirs) {
        $robocopyArgs += "/XD"
        $robocopyArgs += $dir
    }
    $robocopyArgs += "/XF"
    $robocopyArgs += "*.pyc"
    $robocopyArgs += "*.pyo"
    $robocopyArgs += "*.log"
    
    & robocopy @robocopyArgs | Out-Null
    
    if ($LASTEXITCODE -gt 7) {
        Write-Host "FEHLER: Robocopy failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Dateien synchronisiert!" -ForegroundColor Green
}

# Schritt 2: Inno Setup Script erstellen
Write-Host "`n[2/3] Erstelle Inno Setup Script..." -ForegroundColor Yellow

$issContent = @"
[Setup]
AppName=Oemers Calculator
AppVersion=2.0.0
DefaultDirName={autopf}\OemersCalculator
DefaultGroupName=Oemers Calculator
DisableProgramGroupPage=yes
PrivilegesRequired=admin
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=$OUTPUT_DIR
OutputBaseFilename=OemersCalculator_Setup_v2
Uninstallable=yes

[Files]
Source: "app\*"; DestDir: "{app}\app"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "python-embed.zip"; DestDir: "{app}"; Flags: ignoreversion
Source: "wheelhouse\*"; DestDir: "{app}\wheelhouse"; Flags: recursesubdirs ignoreversion
Source: "install.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "run_app_embed.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "run_app_embed.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "install.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Oemers Calculator"; Filename: "{app}\run_app_embed.cmd"; WorkingDir: "{app}"
Name: "{commondesktop}\Oemers Calculator"; Filename: "{app}\run_app_embed.cmd"; WorkingDir: "{app}"

[Run]
Filename: "{cmd}"; Parameters: "/C ""{app}\install.bat"""; StatusMsg: "Installiere Python-Pakete..."; Flags: waituntilterminated runascurrentuser

[UninstallDelete]
Type: filesandordirs; Name: "{app}\python_embed"
"@

$issFile = Join-Path $BUILD_DIR "OemersCalculator_SIMPLE.iss"
Set-Content -Path $issFile -Value $issContent -Encoding UTF8
Write-Host "Inno Script erstellt: $issFile" -ForegroundColor Green

# Schritt 3: Kompilieren
Write-Host "`n[3/3] Kompiliere Setup.exe..." -ForegroundColor Yellow

if (-not (Test-Path $INNO)) {
    Write-Host "WARNUNG: Inno Setup nicht gefunden!" -ForegroundColor Yellow
    Write-Host "Bitte installieren: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host "`nDas .iss Script ist bereit: $issFile" -ForegroundColor Cyan
    Write-Host "Kompiliere es manuell in Inno Setup!" -ForegroundColor Cyan
}
else {
    New-Item -ItemType Directory -Path $OUTPUT_DIR -Force | Out-Null
    
    & "$INNO" "$issFile" /Q
    
    if ($LASTEXITCODE -eq 0) {
        $setup = Get-ChildItem -Path $OUTPUT_DIR -Filter "*.exe" | Select-Object -First 1
        if ($setup) {
            $sizeMB = [math]::Round($setup.Length / 1MB, 2)
            Write-Host "`nSETUP ERFOLGREICH ERSTELLT!" -ForegroundColor Green
            Write-Host "Datei: $($setup.FullName)" -ForegroundColor Cyan
            Write-Host "Groesse: $sizeMB MB" -ForegroundColor Cyan
        }
    }
    else {
        Write-Host "`nKOMPILIERUNG FEHLGESCHLAGEN!" -ForegroundColor Red
        Write-Host "Prüfe Log in: $OUTPUT_DIR" -ForegroundColor Yellow
    }
}

Write-Host "`n==== BUILD ABGESCHLOSSEN ====" -ForegroundColor Cyan
Write-Host "Dauer: $((Get-Date) - (Get-Date).AddSeconds(-$((Get-Date).Second)))" -ForegroundColor Cyan
