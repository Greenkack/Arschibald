# ============================================================================
# ÖMER'S CALCULATOR - 100% VOLLSTÄNDIGER SETUP BUILDER
# ============================================================================
# Erstellt eine vollständige, eigenständige Setup.exe mit ALLEN Abhängigkeiten
# Version: 2.0.0
# Datum: 2025-10-30
# ============================================================================

param(
    [switch]$SkipWheelBuild = $false,
    [switch]$SkipAppSync = $false,
    [switch]$SkipCompilation = $false,
    [switch]$Verbose = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$START_TIME = Get-Date

# ============================================================================
# KONFIGURATION
# ============================================================================

$SCRIPT_DIR = $PSScriptRoot
$ROOT_DIR = Split-Path $SCRIPT_DIR -Parent
$BUILD_DIR = $SCRIPT_DIR
$APP_SRC = Join-Path $ROOT_DIR ""
$APP_DEST = Join-Path $BUILD_DIR "app"
$WHEELHOUSE = Join-Path $BUILD_DIR "wheelhouse"
$PYTHON_EMBED_ZIP = Join-Path $BUILD_DIR "python-embed.zip"
$PYTHON_EMBED_DIR = Join-Path $BUILD_DIR "python_embed"
$OUTPUT_DIR = Join-Path $BUILD_DIR "Output"
$INNO_SETUP = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$LOG_FILE = Join-Path $BUILD_DIR "complete_build.log"

# Python Version
$PYTHON_VERSION = "3.11.9"
$PYTHON_EMBED_URL = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-embed-amd64.zip"

# App Metadaten
$APP_NAME = "Ömer's Calculator All in One"
$APP_VERSION = "2.0.0"
$APP_PUBLISHER = "Ömer's Software Solutions"
$APP_ICON = Join-Path $APP_DEST "assets\Kakerlack.ico"

# ============================================================================
# LOGGING
# ============================================================================

function Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = "[$timestamp] [$Level] $Message"
    
    Write-Host $logLine -ForegroundColor $(
        switch ($Level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "SUCCESS" { "Green" }
            "HEADER" { "Cyan" }
            default { "White" }
        }
    )
    
    Add-Content -Path $LOG_FILE -Value $logLine
}

function Log-Header {
    param([string]$Message)
    Log "" "HEADER"
    Log "============================================================================" "HEADER"
    Log $Message "HEADER"
    Log "============================================================================" "HEADER"
    Log "" "HEADER"
}

function Log-Step {
    param([string]$Message)
    Log "" "INFO"
    Log ">>> $Message" "INFO"
}

# ============================================================================
# HELPER FUNKTIONEN
# ============================================================================

function Test-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Log "Ordner erstellt: $Path"
    }
}

function Remove-DirectoryForce {
    param([string]$Path)
    
    if (Test-Path $Path) {
        Log "Entferne: $Path"
        try {
            # Reset attributes
            Get-ChildItem -Path $Path -Recurse -Force -ErrorAction SilentlyContinue | 
                ForEach-Object { 
                    try { $_.Attributes = 'Normal' } catch {}
                }
            
            # Take ownership
            $takeArgs = @('/F', $Path, '/R', '/D', 'Y')
            Start-Process -FilePath 'takeown.exe' -ArgumentList $takeArgs -NoNewWindow -Wait -ErrorAction SilentlyContinue
            
            # Grant permissions
            $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
            $icaclsArgs = @($Path, '/grant', "$($user):(F)", '/T', '/C')
            Start-Process -FilePath 'icacls.exe' -ArgumentList $icaclsArgs -NoNewWindow -Wait -ErrorAction SilentlyContinue
            
            # Remove
            Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
            Log "Erfolgreich entfernt: $Path" "SUCCESS"
        }
        catch {
            Log "WARNUNG: Konnte $Path nicht vollständig entfernen: $($_.Exception.Message)" "WARN"
        }
    }
}

function Test-Command {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Download-File {
    param(
        [string]$Url,
        [string]$Destination
    )
    
    Log "Download: $Url"
    Log "Ziel: $Destination"
    
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $Destination -UseBasicParsing
        Log "Download erfolgreich" "SUCCESS"
        return $true
    }
    catch {
        Log "Download fehlgeschlagen: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# ============================================================================
# HAUPTFUNKTIONEN
# ============================================================================

function Step1-CheckPrerequisites {
    Log-Header "SCHRITT 1: VORAUSSETZUNGEN PRÜFEN"
    
    # Administrator-Rechte
    if (-not (Test-Administrator)) {
        Log "FEHLER: Dieses Skript muss als Administrator ausgeführt werden!" "ERROR"
        exit 1
    }
    Log "✓ Administrator-Rechte vorhanden" "SUCCESS"
    
    # Python prüfen
    if (-not (Test-Command "python")) {
        Log "FEHLER: Python nicht im PATH gefunden!" "ERROR"
        Log "Bitte installieren Sie Python $PYTHON_VERSION oder höher" "ERROR"
        exit 1
    }
    
    $pythonVersion = & python --version 2>&1
    Log "✓ Python gefunden: $pythonVersion" "SUCCESS"
    
    # pip prüfen
    if (-not (Test-Command "pip")) {
        Log "FEHLER: pip nicht gefunden!" "ERROR"
        exit 1
    }
    Log "✓ pip vorhanden" "SUCCESS"
    
    # Inno Setup prüfen
    if (-not (Test-Path $INNO_SETUP)) {
        Log "WARNUNG: Inno Setup nicht gefunden: $INNO_SETUP" "WARN"
        Log "Setup.exe kann nicht kompiliert werden. Bitte Inno Setup 6 installieren:" "WARN"
        Log "https://jrsoftware.org/isdl.php" "WARN"
    }
    else {
        Log "✓ Inno Setup gefunden" "SUCCESS"
    }
    
    # Quellcode prüfen
    if (-not (Test-Path (Join-Path $ROOT_DIR "gui.py"))) {
        Log "FEHLER: gui.py nicht gefunden in $ROOT_DIR" "ERROR"
        exit 1
    }
    Log "✓ App-Quellcode gefunden" "SUCCESS"
    
    # requirements.txt prüfen
    $reqFile = Join-Path $ROOT_DIR "requirements.txt"
    if (-not (Test-Path $reqFile)) {
        Log "FEHLER: requirements.txt nicht gefunden: $reqFile" "ERROR"
        exit 1
    }
    Log "✓ requirements.txt gefunden" "SUCCESS"
}

function Step2-DownloadPythonEmbed {
    Log-Header "SCHRITT 2: EMBEDDED PYTHON HERUNTERLADEN"
    
    if (Test-Path $PYTHON_EMBED_ZIP) {
        Log "Embedded Python bereits vorhanden: $PYTHON_EMBED_ZIP"
        
        # Validiere ZIP
        try {
            $zip = [System.IO.Compression.ZipFile]::OpenRead($PYTHON_EMBED_ZIP)
            $zip.Dispose()
            Log "✓ ZIP-Datei ist gültig" "SUCCESS"
            return
        }
        catch {
            Log "ZIP-Datei ist beschädigt, lade neu herunter..." "WARN"
            Remove-Item $PYTHON_EMBED_ZIP -Force
        }
    }
    
    Log "Lade Embedded Python $PYTHON_VERSION herunter..."
    $success = Download-File -Url $PYTHON_EMBED_URL -Destination $PYTHON_EMBED_ZIP
    
    if (-not $success) {
        Log "FEHLER: Download fehlgeschlagen!" "ERROR"
        exit 1
    }
    
    # Validiere Download
    if ((Get-Item $PYTHON_EMBED_ZIP).Length -lt 1MB) {
        Log "FEHLER: Heruntergeladene Datei ist zu klein!" "ERROR"
        exit 1
    }
    
    Log "✓ Embedded Python erfolgreich heruntergeladen" "SUCCESS"
}

function Step3-SyncAppFiles {
    Log-Header "SCHRITT 3: APP-DATEIEN SYNCHRONISIEREN"
    
    if ($SkipAppSync) {
        Log "App-Sync wird übersprungen (-SkipAppSync)" "WARN"
        return
    }
    
    # Bereinige alte app-Ordner
    if (Test-Path $APP_DEST) {
        Log "Entferne alten app-Ordner..."
        Remove-DirectoryForce -Path $APP_DEST
    }
    
    Ensure-Directory -Path $APP_DEST
    
    # Kopiere ALLE Dateien und Ordner
    Log "Kopiere App-Dateien von $ROOT_DIR nach $APP_DEST..."
    
    $excludeFolders = @(
        'venv', 'venv_*', '.venv', '__pycache__', '.pytest_cache', 
        '.git', '.github', 'BOKUK_BUILD', 'dist', 'build', 
        'installer_output', 'Output', '*.egg-info', '.ruff_cache',
        'wheelhouse', 'python_embed', 'KOPIE', 'backups'
    )
    
    $excludeFiles = @(
        '*.pyc', '*.pyo', '*.pyd', '.DS_Store', 'Thumbs.db',
        '*.log', '.coverage', '*.spec'
    )
    
    # Robocopy für effizientes Kopieren
    $robocopyArgs = @(
        $ROOT_DIR,
        $APP_DEST,
        '/E',  # Include subdirectories (including empty)
        '/NP', # No progress
        '/NFL', # No file list
        '/NDL', # No directory list
        '/NJH', # No job header
        '/NJS', # No job summary
        '/R:3', # Retry 3 times
        '/W:5'  # Wait 5 seconds between retries
    )
    
    # Exclude Ordner
    foreach ($folder in $excludeFolders) {
        $robocopyArgs += "/XD"
        $robocopyArgs += $folder
    }
    
    # Exclude Dateien
    foreach ($file in $excludeFiles) {
        $robocopyArgs += "/XF"
        $robocopyArgs += $file
    }
    
    Log "Führe Robocopy aus..."
    & robocopy @robocopyArgs | Out-Null
    
    # Robocopy Exit Codes: 0-7 sind Erfolg, >7 ist Fehler
    if ($LASTEXITCODE -gt 7) {
        Log "FEHLER: Robocopy fehlgeschlagen mit Exit Code $LASTEXITCODE" "ERROR"
        exit 1
    }
    
    Log "✓ App-Dateien erfolgreich synchronisiert" "SUCCESS"
    
    # Zähle Dateien
    $fileCount = (Get-ChildItem -Path $APP_DEST -Recurse -File).Count
    $dirCount = (Get-ChildItem -Path $APP_DEST -Recurse -Directory).Count
    $totalSize = [math]::Round((Get-ChildItem -Path $APP_DEST -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    
    Log "Statistik: $fileCount Dateien, $dirCount Ordner, $totalSize MB"
}

function Step4-BuildWheels {
    Log-Header "SCHRITT 4: PYTHON WHEELS ERSTELLEN"
    
    if ($SkipWheelBuild) {
        Log "Wheel-Build wird übersprungen (-SkipWheelBuild)" "WARN"
        return
    }
    
    Ensure-Directory -Path $WHEELHOUSE
    
    $reqFile = Join-Path $APP_DEST "requirements.txt"
    if (-not (Test-Path $reqFile)) {
        Log "FEHLER: requirements.txt nicht gefunden: $reqFile" "ERROR"
        exit 1
    }
    
    Log "Erstelle Wheels aus requirements.txt..."
    Log "Dies kann 10-30 Minuten dauern..."
    
    # Wheel-Build mit detailliertem Logging
    $pipArgs = @(
        'wheel',
        '--wheel-dir', $WHEELHOUSE,
        '--no-cache-dir',
        '--prefer-binary',
        '-r', $reqFile
    )
    
    Log "Befehl: pip $($pipArgs -join ' ')"
    
    & pip @pipArgs 2>&1 | Tee-Object -FilePath $LOG_FILE -Append | ForEach-Object {
        if ($Verbose) { Write-Host $_ }
    }
    
    if ($LASTEXITCODE -ne 0) {
        Log "WARNUNG: Einige Wheels konnten nicht erstellt werden (Exit Code: $LASTEXITCODE)" "WARN"
        Log "Setup wird trotzdem fortgesetzt..." "WARN"
    }
    
    # Zähle Wheels
    $wheelCount = (Get-ChildItem -Path $WHEELHOUSE -Filter "*.whl").Count
    $wheelSize = [math]::Round((Get-ChildItem -Path $WHEELHOUSE -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    
    if ($wheelCount -eq 0) {
        Log "FEHLER: Keine Wheels erstellt!" "ERROR"
        exit 1
    }
    
    Log "✓ $wheelCount Wheels erstellt ($wheelSize MB)" "SUCCESS"
}

function Step5-CreateRunScripts {
    Log-Header "SCHRITT 5: START-SKRIPTE ERSTELLEN"
    
    # PowerShell-Startskript
    $runPs1 = @'
# run_app_embed.ps1
$ErrorActionPreference = 'Stop'

$APPDIR = $PSScriptRoot
$PYDIR = Join-Path $APPDIR 'python_embed'
$PY = Join-Path $PYDIR 'python.exe'
$GUI = Join-Path $APPDIR 'app\gui.py'

if (-not (Test-Path $PY)) {
    Write-Host "FEHLER: Python nicht gefunden: $PY" -ForegroundColor Red
    Write-Host "Bitte Installation mit install.ps1 durchführen!" -ForegroundColor Yellow
    pause
    exit 1
}

if (-not (Test-Path $GUI)) {
    Write-Host "FEHLER: gui.py nicht gefunden: $GUI" -ForegroundColor Red
    pause
    exit 1
}

# Setze Working Directory
Set-Location (Join-Path $APPDIR 'app')

# Starte App
Write-Host "Starte Ömer's Calculator..." -ForegroundColor Green
& "$PY" -m streamlit run "$GUI" --server.port=8501 --server.headless=true

pause
'@
    
    Set-Content -Path (Join-Path $BUILD_DIR "run_app_embed.ps1") -Value $runPs1 -Encoding UTF8
    Log "✓ run_app_embed.ps1 erstellt"
    
    # Batch-Startskript
    $runCmd = @'
@echo off
title Omer's Calculator
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0run_app_embed.ps1"
'@
    
    Set-Content -Path (Join-Path $BUILD_DIR "run_app_embed.cmd") -Value $runCmd -Encoding ASCII
    Log "✓ run_app_embed.cmd erstellt"
    
    # install.bat für Rückwärtskompatibilität
    $installBat = @'
@echo off
title Installation - Omer's Calculator
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0install.ps1"
pause
'@
    
    Set-Content -Path (Join-Path $BUILD_DIR "install.bat") -Value $installBat -Encoding ASCII
    Log "✓ install.bat erstellt"
    
    Log "✓ Start-Skripte erfolgreich erstellt" "SUCCESS"
}

function Step6-UpdateInnoSetupScript {
    Log-Header "SCHRITT 6: INNO SETUP SCRIPT AKTUALISIEREN"
    
    $issFile = Join-Path $BUILD_DIR "OemersCalculator_installer.iss"
    
    # Erweiterte Inno Setup Konfiguration
    $issContent = @"
; ============================================================================
; ÖMER'S CALCULATOR - COMPLETE INSTALLER
; Erstellt von: COMPLETE_SETUP_BUILDER.ps1
; Datum: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
; ============================================================================

[Setup]
; App-Informationen
AppName=$APP_NAME
AppVersion=$APP_VERSION
AppPublisher=$APP_PUBLISHER
AppPublisherURL=https://github.com/Greenkack/Arschibald
AppSupportURL=https://github.com/Greenkack/Arschibald/issues
AppUpdatesURL=https://github.com/Greenkack/Arschibald/releases

; Installation
DefaultDirName={autopf}\OemersCalculatorAllInOne
DefaultGroupName=Ömer's Calculator
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\app\assets\Kakerlack.ico

; Optionen
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273

; Output
OutputDir=$OUTPUT_DIR
OutputBaseFilename=OemersCalculator_Complete_Setup_v$APP_VERSION
SetupIconFile=$APP_ICON

; Uninstall
Uninstallable=yes
UninstallDisplayName=$APP_NAME

; Wizard
WizardStyle=modern
DisableWelcomePage=no
DisableDirPage=no
DisableReadyPage=no
DisableFinishedPage=no

; Sprache
ShowLanguageDialog=auto

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
german.WelcomeLabel2=Dies installiert [name/ver] auf Ihrem Computer.%n%nDie Installation umfasst:%n• Python 3.11.9 (Embedded)%n• Alle Abhängigkeiten (offline)%n• Vollständige App-Dateien%n• Desktop-Verknüpfung
english.WelcomeLabel2=This will install [name/ver] on your computer.%n%nThe installation includes:%n• Python 3.11.9 (Embedded)%n• All dependencies (offline)%n• Complete app files%n• Desktop shortcut

[Files]
; App-Dateien (REKURSIV - ALLES!)
Source: "app\*"; DestDir: "{app}\app"; Flags: recursesubdirs createallsubdirs ignoreversion

; Python Embedded ZIP
Source: "python-embed.zip"; DestDir: "{app}"; Flags: ignoreversion

; Alle Wheels
Source: "wheelhouse\*"; DestDir: "{app}\wheelhouse"; Flags: recursesubdirs createallsubdirs ignoreversion

; Installations- und Start-Skripte
Source: "install.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "install.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "run_app_embed.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "run_app_embed.cmd"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Startmenü
Name: "{group}\$APP_NAME"; Filename: "{app}\run_app_embed.cmd"; WorkingDir: "{app}"; IconFilename: "{app}\app\assets\Kakerlack.ico"; Comment: "Starte $APP_NAME"
Name: "{group}\Abhängigkeiten installieren"; Filename: "{cmd}"; Parameters: "/K powershell -ExecutionPolicy Bypass -NoProfile -File ""{app}\install.ps1"""; WorkingDir: "{app}"; Comment: "Python-Pakete installieren"
Name: "{group}\Deinstallieren"; Filename: "{uninstallexe}"; Comment: "Deinstalliere $APP_NAME"

; Desktop
Name: "{commondesktop}\$APP_NAME"; Filename: "{app}\run_app_embed.cmd"; WorkingDir: "{app}"; IconFilename: "{app}\app\assets\Kakerlack.ico"; Comment: "Starte $APP_NAME"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Verknüpfungen:"; Flags: checked

[Run]
; Automatische Installation der Python-Pakete
Filename: "{cmd}"; Parameters: "/C ""{app}\install.bat"""; StatusMsg: "Installiere Python-Pakete..."; Flags: waituntilterminated runascurrentuser

[UninstallDelete]
; Bereinige alle erzeugten Dateien
Type: filesandordirs; Name: "{app}\python_embed"
Type: filesandordirs; Name: "{app}\app\__pycache__"
Type: filesandordirs; Name: "{app}\app\.streamlit"
Type: filesandordirs; Name: "{app}\app\logs"
Type: filesandordirs; Name: "{app}\app\data"
Type: files; Name: "{app}\install.log"

[Code]
procedure InitializeWizard;
begin
  WizardForm.LicenseAcceptedRadio.Checked := True;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not IsAdminLoggedOn then
  begin
    MsgBox('Diese Installation erfordert Administrator-Rechte!', mbError, MB_OK);
    Result := False;
  end;
end;

procedure DeinitializeSetup();
var
  ResultCode: Integer;
begin
  // Öffne README oder Dokumentation nach Installation
  // Exec('notepad.exe', ExpandConstant('{app}\README.md'), '', SW_SHOW, ewNoWait, ResultCode);
end;
"@
    
    Set-Content -Path $issFile -Value $issContent -Encoding UTF8
    Log "✓ Inno Setup Script aktualisiert: $issFile" "SUCCESS"
}

function Step7-CompileInstaller {
    Log-Header "SCHRITT 7: SETUP.EXE KOMPILIEREN"
    
    if ($SkipCompilation) {
        Log "Kompilierung wird übersprungen (-SkipCompilation)" "WARN"
        return
    }
    
    if (-not (Test-Path $INNO_SETUP)) {
        Log "FEHLER: Inno Setup nicht gefunden: $INNO_SETUP" "ERROR"
        Log "Bitte Inno Setup 6 installieren: https://jrsoftware.org/isdl.php" "ERROR"
        return
    }
    
    Ensure-Directory -Path $OUTPUT_DIR
    
    $issFile = Join-Path $BUILD_DIR "OemersCalculator_installer.iss"
    
    Log "Kompiliere Installer..."
    Log "Dies kann 5-15 Minuten dauern (Kompression)..."
    
    & "$INNO_SETUP" "$issFile" /Q | Tee-Object -FilePath $LOG_FILE -Append
    
    if ($LASTEXITCODE -ne 0) {
        Log "FEHLER: Inno Setup Kompilierung fehlgeschlagen (Exit Code: $LASTEXITCODE)" "ERROR"
        return
    }
    
    # Finde Setup.exe
    $setupExe = Get-ChildItem -Path $OUTPUT_DIR -Filter "*.exe" | Select-Object -First 1
    
    if ($setupExe) {
        $setupSize = [math]::Round($setupExe.Length / 1MB, 2)
        Log "✓ Setup.exe erfolgreich erstellt!" "SUCCESS"
        Log "Datei: $($setupExe.FullName)" "SUCCESS"
        Log "Größe: $setupSize MB" "SUCCESS"
    }
    else {
        Log "WARNUNG: Setup.exe nicht gefunden in $OUTPUT_DIR" "WARN"
    }
}

function Step8-CreateReadme {
    Log-Header "SCHRITT 8: DOKUMENTATION ERSTELLEN"
    
    $readmeContent = @"
# Ömer's Calculator All in One - Installation

## 📦 Setup-Inhalt

Diese Setup.exe enthält:

- ✅ **Python 3.11.9 (Embedded)** - Vollständig integriert, keine separate Installation nötig
- ✅ **Alle Python-Pakete** (194 Pakete) - Offline installierbar
- ✅ **Vollständige App** - Alle Dateien, Bilder, Datenbanken, Einstellungen
- ✅ **Core-Module** - Phase 1-12 Integration (31 Module)
- ✅ **Agent-System** - KI-Assistent mit allen Tools
- ✅ **PDF-System** - Erweiterte PDF-Generierung
- ✅ **Chart-System** - 55+ Diagrammtypen
- ✅ **CRM-System** - Kundenverwaltung
- ✅ **Datenbanken** - SQLite mit allen Daten

## 🚀 Installation

### Schritt 1: Setup ausführen
Doppelklick auf `OemersCalculator_Complete_Setup_v$APP_VERSION.exe`

### Schritt 2: Installation durchführen
- Wählen Sie Installationsordner (Standard: C:\Program Files\OemersCalculatorAllInOne)
- Bestätigen Sie Administrator-Rechte
- Warten Sie, bis alle Dateien kopiert sind
- Python-Pakete werden automatisch installiert (dauert ~5 Minuten)

### Schritt 3: App starten
- Desktop-Verknüpfung: **Ömer's Calculator All in One**
- Oder: Startmenü → Ömer's Calculator → Ömer's Calculator All in One

## 📁 Installationsverzeichnis

Nach Installation:
``````
C:\Program Files\OemersCalculatorAllInOne\
├── app\                    # Vollständige App (alle .py, .json, .db)
│   ├── gui.py             # Hauptdatei
│   ├── core\              # Core-Module (Phase 1-12)
│   ├── Agent\             # KI-Agent
│   ├── data\              # Datenbanken
│   ├── assets\            # Bilder, Icons
│   ├── .streamlit\        # Streamlit Config
│   └── ...                # Alle anderen Dateien
├── python_embed\          # Python 3.11.9 (nach install.ps1)
├── wheelhouse\            # Alle Python-Wheels (536 MB)
├── python-embed.zip       # Python ZIP
├── install.ps1            # Installations-Script
├── run_app_embed.ps1      # Start-Script
└── run_app_embed.cmd      # Start-Batch
``````

## 🔧 Manuelle Installation (falls automatisch fehlschlägt)

``````powershell
cd "C:\Program Files\OemersCalculatorAllInOne"
powershell -ExecutionPolicy Bypass -File install.ps1
``````

## 🌐 App starten

Nach erfolgreicher Installation öffnet sich automatisch der Browser mit:
``````
http://localhost:8501
``````

## ❓ Problembehandlung

### Problem: "Python nicht gefunden"
**Lösung:** Manuelle Installation ausführen (siehe oben)

### Problem: "Streamlit nicht gefunden"
**Lösung:** 
``````powershell
cd "C:\Program Files\OemersCalculatorAllInOne"
.\python_embed\python.exe -m pip install streamlit
``````

### Problem: "Port 8501 bereits belegt"
**Lösung:** In run_app_embed.ps1 den Port ändern:
``````powershell
--server.port=8502
``````

### Problem: Administrator-Rechte fehlen
**Lösung:** Rechtsklick auf run_app_embed.cmd → "Als Administrator ausführen"

## 📊 Systemanforderungen

- **OS:** Windows 10/11 (64-bit)
- **RAM:** Mindestens 4 GB (empfohlen: 8 GB)
- **Festplatte:** ~3 GB freier Speicher
- **Prozessor:** Intel/AMD x64
- **Browser:** Chrome, Firefox, Edge (für Streamlit-UI)

## 🔐 Deinstallation

1. **Windows-Einstellungen** → Apps → "Ömer's Calculator All in One" → Deinstallieren
2. **Oder:** Startmenü → Ömer's Calculator → Deinstallieren

## 📞 Support

Bei Problemen:
- GitHub Issues: https://github.com/Greenkack/Arschibald/issues
- Email: support@example.com

## 📝 Version

- **App Version:** $APP_VERSION
- **Build Datum:** $(Get-Date -Format 'yyyy-MM-dd')
- **Python Version:** 3.11.9
- **Streamlit Version:** 1.49.1

---

**Erstellt mit COMPLETE_SETUP_BUILDER.ps1**
"@
    
    $readmePath = Join-Path $OUTPUT_DIR "README_INSTALLATION.md"
    Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8
    Log "✓ README erstellt: $readmePath" "SUCCESS"
    
    # Kurze Installationsanleitung
    $quickGuide = @"
SCHNELLSTART - Ömer's Calculator

1. Setup ausführen: OemersCalculator_Complete_Setup_v$APP_VERSION.exe
2. Installation durchführen (Administrator-Rechte erforderlich)
3. Warten (Python-Pakete werden automatisch installiert)
4. Desktop-Icon doppelklicken: "Ömer's Calculator All in One"
5. Browser öffnet sich automatisch mit http://localhost:8501

Fertig! 🎉

Bei Problemen: README_INSTALLATION.md lesen
"@
    
    $quickGuidePath = Join-Path $OUTPUT_DIR "SCHNELLSTART.txt"
    Set-Content -Path $quickGuidePath -Value $quickGuide -Encoding UTF8
    Log "✓ Schnellstart-Anleitung erstellt: $quickGuidePath" "SUCCESS"
}

function Step9-FinalValidation {
    Log-Header "SCHRITT 9: FINALE VALIDIERUNG"
    
    $errors = @()
    $warnings = @()
    
    # Prüfe app-Ordner
    if (-not (Test-Path $APP_DEST)) {
        $errors += "app-Ordner fehlt: $APP_DEST"
    }
    else {
        $appFiles = (Get-ChildItem -Path $APP_DEST -Recurse -File).Count
        if ($appFiles -lt 100) {
            $warnings += "Zu wenige Dateien im app-Ordner: $appFiles"
        }
        Log "✓ app-Ordner: $appFiles Dateien"
    }
    
    # Prüfe wheelhouse
    if (-not (Test-Path $WHEELHOUSE)) {
        $errors += "wheelhouse-Ordner fehlt: $WHEELHOUSE"
    }
    else {
        $wheelFiles = (Get-ChildItem -Path $WHEELHOUSE -Filter "*.whl").Count
        if ($wheelFiles -lt 50) {
            $warnings += "Zu wenige Wheels: $wheelFiles"
        }
        Log "✓ wheelhouse: $wheelFiles Wheels"
    }
    
    # Prüfe Python Embed
    if (-not (Test-Path $PYTHON_EMBED_ZIP)) {
        $errors += "python-embed.zip fehlt: $PYTHON_EMBED_ZIP"
    }
    else {
        Log "✓ python-embed.zip vorhanden"
    }
    
    # Prüfe Skripte
    $scripts = @('install.ps1', 'run_app_embed.ps1', 'run_app_embed.cmd', 'install.bat')
    foreach ($script in $scripts) {
        $scriptPath = Join-Path $BUILD_DIR $script
        if (-not (Test-Path $scriptPath)) {
            $errors += "Script fehlt: $script"
        }
    }
    Log "✓ Alle Start-Skripte vorhanden"
    
    # Prüfe Setup.exe
    $setupExe = Get-ChildItem -Path $OUTPUT_DIR -Filter "*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($setupExe) {
        $setupSize = [math]::Round($setupExe.Length / 1MB, 2)
        Log "✓ Setup.exe erstellt: $setupSize MB" "SUCCESS"
    }
    else {
        $warnings += "Setup.exe nicht gefunden (möglicherweise Kompilierung übersprungen)"
    }
    
    # Ausgabe
    if ($errors.Count -gt 0) {
        Log "" "ERROR"
        Log "FEHLER GEFUNDEN:" "ERROR"
        foreach ($error in $errors) {
            Log "  ✗ $error" "ERROR"
        }
        Log "" "ERROR"
        return $false
    }
    
    if ($warnings.Count -gt 0) {
        Log "" "WARN"
        Log "WARNUNGEN:" "WARN"
        foreach ($warning in $warnings) {
            Log "  ⚠ $warning" "WARN"
        }
        Log "" "WARN"
    }
    
    Log "✓ Validierung erfolgreich" "SUCCESS"
    return $true
}

# ============================================================================
# HAUPTAUSFÜHRUNG
# ============================================================================

try {
    Log-Header "ÖMER'S CALCULATOR - 100% VOLLSTÄNDIGER SETUP BUILDER"
    Log "Start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Log "Build-Verzeichnis: $BUILD_DIR"
    Log ""
    
    # Schritt für Schritt
    Step1-CheckPrerequisites
    Step2-DownloadPythonEmbed
    Step3-SyncAppFiles
    Step4-BuildWheels
    Step5-CreateRunScripts
    Step6-UpdateInnoSetupScript
    Step7-CompileInstaller
    Step8-CreateReadme
    $valid = Step9-FinalValidation
    
    # Zusammenfassung
    $END_TIME = Get-Date
    $DURATION = $END_TIME - $START_TIME
    
    Log-Header "BUILD ABGESCHLOSSEN"
    
    if ($valid) {
        Log "✅ BUILD ERFOLGREICH!" "SUCCESS"
    }
    else {
        Log "⚠️ BUILD MIT FEHLERN!" "WARN"
    }
    
    Log ""
    Log "Dauer: $($DURATION.ToString('hh\:mm\:ss'))"
    Log "Log-Datei: $LOG_FILE"
    Log ""
    
    if (Test-Path $OUTPUT_DIR) {
        Log "Output-Verzeichnis: $OUTPUT_DIR"
        $setupExe = Get-ChildItem -Path $OUTPUT_DIR -Filter "*.exe" | Select-Object -First 1
        if ($setupExe) {
            Log "Setup.exe: $($setupExe.FullName)" "SUCCESS"
            Log "Größe: $([math]::Round($setupExe.Length / 1MB, 2)) MB" "SUCCESS"
        }
    }
    
    Log ""
    Log "Zum Testen:" "HEADER"
    Log "  1. Setup.exe ausführen" "HEADER"
    Log "  2. Installation durchführen" "HEADER"
    Log "  3. Desktop-Icon starten" "HEADER"
    Log ""
    
    # Öffne Output-Ordner
    if (Test-Path $OUTPUT_DIR) {
        Start-Process explorer.exe $OUTPUT_DIR
    }
}
catch {
    Log "" "ERROR"
    Log "KRITISCHER FEHLER:" "ERROR"
    Log $_.Exception.Message "ERROR"
    Log $_.ScriptStackTrace "ERROR"
    exit 1
}
finally {
    Log ""
    Log "Build-Log gespeichert: $LOG_FILE"
}
