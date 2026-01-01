"""
build_exe_setup.py
Erstellt eine vollständige EXE-Setup-Datei mit PyInstaller + Inno Setup
Inkludiert: Python Runtime, alle Dependencies, Daten, Configs

VERWENDUNG:
    python build_exe_setup.py

ERGEBNIS:
    dist/ARSCHIBALD_Setup.exe - Vollständiger Windows Installer
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import json

# Konfiguration
APP_NAME = "Ömers All in One Dingsbums"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Ömer"
APP_DESCRIPTION = "PV- und Wärmepumpen-Konfigurationssoftware"
MAIN_SCRIPT = "gui.py"
ICON_FILE = "data/company_logos/app_icon.ico"  # Falls vorhanden

# Verzeichnisse
BASE_DIR = Path(__file__).parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
INSTALLER_DIR = BASE_DIR / "installer_files"

# PyInstaller Spec-Datei erstellen
SPEC_CONTENT = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Daten-Dateien sammeln
datas = []

# Basis-Verzeichnisse die eingebunden werden sollen
data_dirs = [
    'data',
    'coords_multi',
    'pdf_templates_static',
    'customer_documents',
    '.streamlit',
]

# Nur existierende Verzeichnisse hinzufügen
for dir_name in data_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists() and dir_path.is_dir():
        datas.append((str(dir_path), dir_name))

# Wichtige Einzeldateien
important_files = [
    'locales.py',
    'requirements.txt',
]

for file_name in important_files:
    file_path = Path(file_name)
    if file_path.exists() and file_path.is_file():
        datas.append((str(file_path), '.'))

# Optionale Verzeichnisse (falls vorhanden)
optional_dirs = [
    'theming',
    'components',
    'core',
    'backend',
    'crm',
    'pdf_template_engine',
    'tools',
    'tests',
    'ui',
    'static',
    'assets',
]

for dir_name in optional_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists() and dir_path.is_dir():
        datas.append((str(dir_path), dir_name))

# Hidden Imports - alle wichtigen Module
hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'pandas',
    'numpy',
    'openpyxl',
    'reportlab',
    'pypdf',
    'PyPDF2',
    'pyvista',
    'pyvistaqt',
    'matplotlib',
    'plotly',
    'sqlite3',
    'json',
    'yaml',
    'toml',
    'PIL',
    'click',
    'altair',
    'tornado',
    'watchdog',
    'validators',
    'packaging',
    'pyarrow',
    'tzlocal',
    'pytz',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'pydeck',
    'gitpython',
    'git',
]

# Binaries ausschließen (reduziert Größe)
binaries = []

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'test', 'unittest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console für Debugging, später auf False setzen
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{ICON_FILE if Path(ICON_FILE).exists() else ""}',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)
'''

# Inno Setup Script erstellen
INNO_SETUP_SCRIPT = f'''[Setup]
AppName={APP_NAME}
AppVersion={APP_VERSION}
AppPublisher={APP_AUTHOR}
AppPublisherURL=https://example.com
DefaultDirName={{autopf}}\\{APP_NAME}
DefaultGroupName={APP_NAME}
OutputDir=.
OutputBaseFilename={APP_NAME}_Setup_v{APP_VERSION}
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile={ICON_FILE if Path(ICON_FILE).exists() else ""}
UninstallDisplayIcon={{app}}\\{APP_NAME}.exe
WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=admin
LicenseFile=LICENSE.txt

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"
Name: "quicklaunchicon"; Description: "Verknüpfung in Schnellstartleiste"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "dist\\{APP_NAME}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"
Name: "{{autodesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\{APP_NAME}.exe"; Description: "{{cm:LaunchProgram,{APP_NAME}}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('Installation von {APP_NAME} v{APP_VERSION}' + #13#10 + 
         'Diese Software installiert alle benötigten Komponenten.' + #13#10#13#10 +
         'Klicken Sie auf Weiter um fortzufahren.', 
         mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Erstelle data Verzeichnis falls nicht vorhanden
    CreateDir(ExpandConstant('{{app}}\\data'));
    CreateDir(ExpandConstant('{{app}}\\customer_documents'));
    CreateDir(ExpandConstant('{{app}}\\logs'));
  end;
end;
'''

# Startup Batch-Script für die EXE
STARTUP_SCRIPT = f'''@echo off
title {APP_NAME} - Starte Anwendung...

echo.
echo ====================================
echo  {APP_NAME} v{APP_VERSION}
echo ====================================
echo.
echo Starte Anwendung...
echo.

cd /d "%~dp0"

REM Prüfe ob Datenbank existiert
if not exist "data\\app_data.db" (
    echo Erstelle Datenbank...
    mkdir data 2>nul
)

REM Starte Streamlit App
echo Öffne Browser...
start http://localhost:8501

REM Starte Hauptanwendung
"{APP_NAME}.exe"

if errorlevel 1 (
    echo.
    echo FEHLER: Anwendung konnte nicht gestartet werden!
    echo Bitte prüfen Sie die Logs unter logs\\app.log
    echo.
    pause
)
'''

# Python Runner Script (gui_runner.py)
RUNNER_SCRIPT = '''"""
gui_runner.py
Startet die Streamlit-App korrekt mit allen Parametern
"""
import sys
import os
from pathlib import Path

# Setze Arbeitsverzeichnis
if getattr(sys, 'frozen', False):
    # Wenn als EXE ausgeführt
    application_path = Path(sys.executable).parent
else:
    application_path = Path(__file__).parent

os.chdir(application_path)

# Umgebungsvariablen setzen
os.environ['STREAMLIT_SERVER_PORT'] = '8501'
os.environ['STREAMLIT_SERVER_ADDRESS'] = 'localhost'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Importiere und starte Streamlit
try:
    from streamlit.web import cli as stcli
    import streamlit
    
    print(f"Streamlit Version: {streamlit.__version__}")
    print(f"Working Directory: {os.getcwd()}")
    print("Starte {APP_NAME}...")
    
    # Starte mit gui.py
    sys.argv = ["streamlit", "run", "gui.py", 
                "--server.port=8501",
                "--server.headless=true",
                "--browser.gatherUsageStats=false"]
    
    sys.exit(stcli.main())
    
except Exception as e:
    print(f"FEHLER beim Start: {e}")
    import traceback
    traceback.print_exc()
    input("Drücken Sie Enter zum Beenden...")
    sys.exit(1)
'''


def print_section(title):
    """Druckt formatierten Section-Header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def check_requirements():
    """Prüft ob alle Build-Tools installiert sind"""
    print_section("1. Prüfe Build-Voraussetzungen")
    
    # Prüfe PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} gefunden")
    except ImportError:
        print("✗ PyInstaller nicht gefunden - installiere...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installiert")
    
    # Prüfe alle Dependencies aus requirements.txt
    req_file = BASE_DIR / "requirements.txt"
    if req_file.exists():
        print(f"✓ requirements.txt gefunden")
        print("  Installiere alle Dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
        print("✓ Alle Dependencies installiert")
    else:
        print("⚠ requirements.txt nicht gefunden - erstelle Basis-Version...")
        create_requirements_file()
    
    # Prüfe Inno Setup (optional)
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    
    inno_found = False
    for path in inno_paths:
        if Path(path).exists():
            print(f"✓ Inno Setup gefunden: {path}")
            inno_found = True
            break
    
    if not inno_found:
        print("⚠ Inno Setup nicht gefunden")
        print("  Download: https://jrsoftware.org/isdl.php")
        print("  (Optional - für professionellen Installer)")
    
    return True


def create_requirements_file():
    """Erstellt requirements.txt falls nicht vorhanden"""
    requirements = """streamlit==1.49.1
pandas==2.2.3
numpy==1.26.4
openpyxl==3.1.5
reportlab==4.4.3
pypdf==5.1.0
PyPDF2==3.0.1
pyvista==0.43.10
matplotlib==3.9.2
plotly==5.24.1
pyyaml==6.0.2
pillow==10.4.0
altair==5.4.1
"""
    
    req_file = BASE_DIR / "requirements.txt"
    req_file.write_text(requirements, encoding='utf-8')
    print(f"✓ requirements.txt erstellt: {req_file}")


def clean_build_dirs():
    """Löscht alte Build-Verzeichnisse"""
    print_section("2. Bereite Build-Verzeichnisse vor")
    
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if dir_path.exists():
            print(f"  Lösche altes Verzeichnis: {dir_path}")
            shutil.rmtree(dir_path, ignore_errors=True)
    
    DIST_DIR.mkdir(exist_ok=True)
    BUILD_DIR.mkdir(exist_ok=True)
    
    print("✓ Build-Verzeichnisse bereit")


def create_spec_file():
    """Erstellt PyInstaller .spec Datei"""
    print_section("3. Erstelle PyInstaller Spezifikation")
    
    spec_file = BASE_DIR / f"{APP_NAME}.spec"
    spec_file.write_text(SPEC_CONTENT, encoding='utf-8')
    
    print(f"✓ Spec-Datei erstellt: {spec_file}")
    return spec_file


def create_runner_files():
    """Erstellt Launcher-Scripts"""
    print_section("4. Erstelle Launcher-Scripts")
    
    # GUI Runner
    runner_file = BASE_DIR / "gui_runner.py"
    runner_file.write_text(RUNNER_SCRIPT, encoding='utf-8')
    print(f"✓ Runner-Script: {runner_file}")
    
    # Batch-Datei
    batch_file = BASE_DIR / f"Start_{APP_NAME}.bat"
    batch_file.write_text(STARTUP_SCRIPT, encoding='utf-8')
    print(f"✓ Batch-Script: {batch_file}")


def build_exe(spec_file):
    """Führt PyInstaller Build aus"""
    print_section("5. Baue EXE mit PyInstaller")
    
    print("  Dies kann einige Minuten dauern...")
    print(f"  Spec-Datei: {spec_file}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            str(spec_file),
            "--clean",
            "--noconfirm"
        ])
        
        print("\n✓ EXE erfolgreich erstellt!")
        
        exe_path = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"  Größe: {size_mb:.1f} MB")
            print(f"  Pfad: {exe_path}")
            return exe_path
        else:
            print(f"✗ EXE nicht gefunden: {exe_path}")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Fehler beim Build: {e}")
        return None


def create_inno_setup():
    """Erstellt Inno Setup Installer"""
    print_section("6. Erstelle Windows Installer (Optional)")
    
    # Prüfe ob dist/{APP_NAME} existiert
    app_dir = DIST_DIR / APP_NAME
    if not app_dir.exists():
        print(f"✗ App-Verzeichnis nicht gefunden: {app_dir}")
        return None
    
    # Erstelle Inno Setup Script
    iss_file = BASE_DIR / f"{APP_NAME}_setup.iss"
    iss_file.write_text(INNO_SETUP_SCRIPT, encoding='utf-8')
    print(f"✓ Inno Setup Script: {iss_file}")
    
    # Erstelle LICENSE.txt falls nicht vorhanden
    license_file = BASE_DIR / "LICENSE.txt"
    if not license_file.exists():
        license_file.write_text(f"""
{APP_NAME} Software Lizenz

Copyright (c) 2025 {APP_AUTHOR}

Diese Software wird "wie besehen" zur Verfügung gestellt.
Alle Rechte vorbehalten.
""", encoding='utf-8')
        print(f"✓ Lizenz-Datei erstellt: {license_file}")
    
    # Versuche Inno Setup auszuführen
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    
    for inno_path in inno_paths:
        if Path(inno_path).exists():
            print(f"\n  Führe Inno Setup aus...")
            try:
                subprocess.check_call([inno_path, str(iss_file)])
                
                setup_exe = BASE_DIR / f"{APP_NAME}_Setup_v{APP_VERSION}.exe"
                if setup_exe.exists():
                    size_mb = setup_exe.stat().st_size / (1024 * 1024)
                    print(f"\n✓ Setup-Installer erstellt!")
                    print(f"  Größe: {size_mb:.1f} MB")
                    print(f"  Pfad: {setup_exe}")
                    return setup_exe
                    
            except subprocess.CalledProcessError as e:
                print(f"✗ Fehler bei Inno Setup: {e}")
            break
    else:
        print("⚠ Inno Setup nicht installiert")
        print(f"  Manuelle Kompilierung: Öffne {iss_file} mit Inno Setup")
    
    return None


def create_portable_package():
    """Erstellt portable ZIP-Version"""
    print_section("7. Erstelle Portable ZIP-Version")
    
    app_dir = DIST_DIR / APP_NAME
    if not app_dir.exists():
        print(f"✗ App-Verzeichnis nicht gefunden: {app_dir}")
        return None
    
    zip_name = f"{APP_NAME}_Portable_v{APP_VERSION}"
    zip_path = DIST_DIR / zip_name
    
    print(f"  Packe {app_dir}...")
    shutil.make_archive(str(zip_path), 'zip', app_dir.parent, app_dir.name)
    
    zip_file = Path(f"{zip_path}.zip")
    if zip_file.exists():
        size_mb = zip_file.stat().st_size / (1024 * 1024)
        print(f"\n✓ Portable ZIP erstellt!")
        print(f"  Größe: {size_mb:.1f} MB")
        print(f"  Pfad: {zip_file}")
        return zip_file
    
    return None


def create_readme():
    """Erstellt README für die Distribution"""
    readme_content = f"""
{APP_NAME} v{APP_VERSION}
{'=' * 50}

INSTALLATION
------------

Option 1: Setup-Installer (empfohlen)
   - Doppelklick auf {APP_NAME}_Setup_v{APP_VERSION}.exe
   - Folgen Sie dem Installationsassistenten
   - Starten Sie über Desktop-Icon oder Startmenü

Option 2: Portable Version
   - Entpacken Sie {APP_NAME}_Portable_v{APP_VERSION}.zip
   - Führen Sie {APP_NAME}.exe aus
   - Keine Installation erforderlich

SYSTEMANFORDERUNGEN
-------------------
- Windows 10/11 (64-bit)
- Mindestens 4 GB RAM
- 500 MB freier Festplattenspeicher
- Internetverbindung (für Updates)

ERSTE SCHRITTE
--------------
1. Starten Sie {APP_NAME}
2. Browser öffnet sich automatisch (http://localhost:8501)
3. Melden Sie sich an oder registrieren Sie sich

SUPPORT
-------
Bei Fragen oder Problemen:
- E-Mail: support@example.com
- Website: https://example.com

LIZENZ
------
Copyright (c) 2025 {APP_AUTHOR}
Alle Rechte vorbehalten.
"""
    
    readme_file = DIST_DIR / "README.txt"
    readme_file.write_text(readme_content, encoding='utf-8')
    print(f"✓ README erstellt: {readme_file}")


def main():
    """Hauptfunktion für den Build-Prozess"""
    print("\n" + "=" * 70)
    print(f"  {APP_NAME} - EXE Setup Builder v{APP_VERSION}")
    print("=" * 70)
    
    try:
        # 1. Voraussetzungen prüfen
        if not check_requirements():
            return 1
        
        # 2. Build-Verzeichnisse vorbereiten
        clean_build_dirs()
        
        # 3. Spec-Datei erstellen
        spec_file = create_spec_file()
        
        # 4. Launcher-Scripts erstellen
        create_runner_files()
        
        # 5. EXE bauen
        exe_path = build_exe(spec_file)
        if not exe_path:
            print("\n✗ Build fehlgeschlagen!")
            return 1
        
        # 6. Inno Setup Installer erstellen
        setup_exe = create_inno_setup()
        
        # 7. Portable ZIP erstellen
        zip_file = create_portable_package()
        
        # 8. README erstellen
        create_readme()
        
        # Zusammenfassung
        print_section("FERTIG - Build abgeschlossen!")
        
        print("Erstellte Dateien:")
        print(f"  ✓ EXE: {exe_path}")
        
        if setup_exe:
            print(f"  ✓ Setup-Installer: {setup_exe}")
        else:
            print(f"  ⚠ Setup-Installer: Nicht erstellt (Inno Setup erforderlich)")
        
        if zip_file:
            print(f"  ✓ Portable ZIP: {zip_file}")
        
        print(f"\n  Alle Dateien in: {DIST_DIR}")
        
        print("\n" + "=" * 70)
        print("  Build erfolgreich abgeschlossen!")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n\n✗ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
