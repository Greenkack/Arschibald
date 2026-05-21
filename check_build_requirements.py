"""
check_build_requirements.py
Prüft alle Voraussetzungen für den EXE-Build

Verwendung:
    python check_build_requirements.py
"""

import sys
import subprocess
from pathlib import Path
import importlib.util

def print_header(text):
    """Formatierter Header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def check_python_version():
    """Prüft Python-Version"""
    print_header("Python-Version")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 10):
        print("❌ Python 3.10 oder höher erforderlich!")
        print(f"   Aktuell: {version.major}.{version.minor}.{version.micro}")
        print("   Download: https://www.python.org/downloads/")
        return False
    
    print("✓ Python-Version OK")
    return True

def check_pip():
    """Prüft pip"""
    print_header("pip (Package Manager)")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout.strip())
        print("✓ pip verfügbar")
        return True
    except:
        print("❌ pip nicht gefunden!")
        return False

def check_module(module_name, package_name=None):
    """Prüft ob Python-Modul installiert ist"""
    if package_name is None:
        package_name = module_name
    
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            # Versuche Version zu ermitteln
            try:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', 'unbekannt')
                print(f"  ✓ {package_name:20s} {version}")
            except:
                print(f"  ✓ {package_name:20s} (installiert)")
            return True
        else:
            print(f"  ✗ {package_name:20s} FEHLT")
            return False
    except:
        print(f"  ✗ {package_name:20s} FEHLT")
        return False

def check_dependencies():
    """Prüft alle Python-Dependencies"""
    print_header("Python-Dependencies")
    
    # Kritische Dependencies
    critical = [
        ('streamlit', 'streamlit'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('PyInstaller', 'pyinstaller'),
    ]
    
    # Optionale Dependencies
    optional = [
        ('reportlab', 'reportlab'),
        ('pypdf', 'pypdf'),
        ('PyPDF2', 'PyPDF2'),
        ('pyvista', 'pyvista'),
        ('matplotlib', 'matplotlib'),
        ('plotly', 'plotly'),
        ('yaml', 'pyyaml'),
        ('PIL', 'Pillow'),
        ('openpyxl', 'openpyxl'),
    ]
    
    print("KRITISCHE Packages:")
    critical_ok = True
    for module_name, package_name in critical:
        if not check_module(module_name, package_name):
            critical_ok = False
    
    print("\nOPTIONALE Packages:")
    for module_name, package_name in optional:
        check_module(module_name, package_name)
    
    return critical_ok

def check_project_structure():
    """Prüft Projekt-Struktur"""
    print_header("Projekt-Struktur")
    
    required_files = [
        'gui.py',
        'requirements.txt',
    ]
    
    optional_dirs = [
        'data',
        'pdf_templates_static',
        'coords_multi',
        '.streamlit',
    ]
    
    all_ok = True
    
    print("Erforderliche Dateien:")
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} FEHLT!")
            all_ok = False
    
    print("\nOptionale Verzeichnisse:")
    for dir_name in optional_dirs:
        if Path(dir_name).exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ⚠ {dir_name}/ nicht gefunden")
    
    return all_ok

def check_inno_setup():
    """Prüft Inno Setup Installation"""
    print_header("Inno Setup (Optional)")
    
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    
    for path in inno_paths:
        if Path(path).exists():
            print(f"✓ Inno Setup gefunden: {path}")
            return True
    
    print("⚠ Inno Setup nicht installiert")
    print("  → Setup-Installer kann nicht erstellt werden")
    print("  → Portable ZIP ist trotzdem verfügbar")
    print("  Download: https://jrsoftware.org/isdl.php")
    return False

def estimate_build_time():
    """Schätzt Build-Zeit"""
    print_header("Geschätzte Build-Zeit")
    
    import multiprocessing
    cores = multiprocessing.cpu_count()
    
    # Basis: 10 Minuten auf 4 Kernen
    base_time = 10
    estimated = base_time * (4 / cores)
    
    print(f"CPU-Kerne: {cores}")
    print(f"Geschätzte Dauer: {int(estimated)} Minuten")
    
    if cores >= 8:
        print("✓ Schneller Build erwartet")
    elif cores >= 4:
        print("✓ Normale Build-Geschwindigkeit")
    else:
        print("⚠ Langsamer Build - mehr Kerne empfohlen")

def install_missing():
    """Bietet Installation fehlender Packages an"""
    print_header("Fehlende Packages installieren")
    
    print("Möchtest du alle fehlenden Packages jetzt installieren? (j/n)")
    response = input("> ").strip().lower()
    
    if response == 'j':
        req_file = Path("requirements.txt")
        if req_file.exists():
            print("\nInstalliere aus requirements.txt...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "-r", str(req_file), "--upgrade"
                ])
                print("\n✓ Installation abgeschlossen")
                return True
            except:
                print("\n✗ Installation fehlgeschlagen")
                return False
        else:
            print("\n⚠ requirements.txt nicht gefunden")
            print("  Installiere nur PyInstaller...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "pyinstaller", "--upgrade"
                ])
                print("\n✓ PyInstaller installiert")
                return True
            except:
                print("\n✗ Installation fehlgeschlagen")
                return False
    
    return False

def main():
    """Hauptfunktion"""
    print("\n" + "=" * 70)
    print("  ARSCHIBALD - Build Requirements Checker")
    print("=" * 70)
    
    results = {
        'python': check_python_version(),
        'pip': check_pip(),
        'dependencies': check_dependencies(),
        'structure': check_project_structure(),
        'inno': check_inno_setup(),
    }
    
    estimate_build_time()
    
    # Zusammenfassung
    print_header("Zusammenfassung")
    
    all_critical_ok = all([
        results['python'],
        results['pip'],
        results['dependencies'],
        results['structure']
    ])
    
    if all_critical_ok:
        print("✅ ALLE KRITISCHEN ANFORDERUNGEN ERFÜLLT!")
        print("\nBereit für Build:")
        print("  → python build_exe_setup.py")
        print("  → oder: BUILD_EXE.bat")
        
        if not results['inno']:
            print("\n⚠ Hinweis: Setup-Installer wird übersprungen (Inno Setup fehlt)")
            print("  Portable ZIP wird trotzdem erstellt")
        
        return 0
    else:
        print("❌ KRITISCHE ANFORDERUNGEN FEHLEN!")
        print("\nProbleme:")
        
        if not results['python']:
            print("  ✗ Python-Version zu alt")
        if not results['pip']:
            print("  ✗ pip nicht verfügbar")
        if not results['dependencies']:
            print("  ✗ Dependencies fehlen")
        if not results['structure']:
            print("  ✗ Projekt-Struktur unvollständig")
        
        # Angebot: Installation
        if not results['dependencies']:
            print()
            if install_missing():
                print("\n✓ Bitte prüfe erneut:")
                print("  python check_build_requirements.py")
        
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAbgebrochen durch Benutzer.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
