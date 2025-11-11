#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tiefgehende Modul-Prüfung für alle Python-Dateien in der App
"""

import ast
import sys
from pathlib import Path
from collections import defaultdict
import importlib

def extract_imports(file_path: Path):
    """Extrahiert alle Imports aus einer Python-Datei"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        return imports
    except Exception as e:
        return set()

def check_import(module_name: str) -> bool:
    """Prüft ob ein Modul importierbar ist"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False
    except Exception:
        return False

def main():
    print("=" * 80)
    print("🔬 TIEFGEHENDE IMPORT-ANALYSE")
    print("=" * 80)
    
    # Finde alle Python-Dateien
    root = Path('.')
    python_files = list(root.glob('*.py'))
    
    print(f"\n📂 Gefundene Python-Dateien: {len(python_files)}")
    
    # Sammle alle Imports
    all_imports = defaultdict(list)
    
    for py_file in sorted(python_files):
        # Überspringe __pycache__ und versteckte Dateien
        if '__pycache__' in str(py_file) or py_file.name.startswith('.'):
            continue
        
        # Skip system_check.py selbst
        if py_file.name == 'deep_module_check.py':
            continue
            
        imports = extract_imports(py_file)
        
        for imp in imports:
            all_imports[imp].append(py_file.name)
    
    # Gruppiere nach Standard Library, Third-Party, und Local
    print("\n" + "=" * 80)
    print("📦 IMPORT-KATEGORIEN")
    print("=" * 80)
    
    std_lib = set()
    third_party = set()
    local_modules = set()
    missing = set()
    
    for module in sorted(all_imports.keys()):
        # Überspringe relative Imports und leere
        if not module or module.startswith('_'):
            continue
        
        # Prüfe ob verfügbar
        is_available = check_import(module)
        
        # Kategorisiere
        if module in sys.stdlib_module_names:
            std_lib.add(module)
        elif is_available:
            # Prüfe ob lokal
            if (Path(f"{module}.py").exists() or 
                Path(module).is_dir()):
                local_modules.add(module)
            else:
                third_party.add(module)
        else:
            missing.add(module)
    
    # Ausgabe
    print(f"\n🐍 STANDARD LIBRARY ({len(std_lib)} Module)")
    print("-" * 80)
    for mod in sorted(std_lib):
        files_using = ', '.join(all_imports[mod][:3])
        if len(all_imports[mod]) > 3:
            files_using += f" (+{len(all_imports[mod])-3} mehr)"
        print(f"  ✅ {mod:30s} verwendet in: {files_using}")
    
    print(f"\n📚 THIRD-PARTY PACKAGES ({len(third_party)} Pakete)")
    print("-" * 80)
    for mod in sorted(third_party):
        files_using = ', '.join(all_imports[mod][:3])
        if len(all_imports[mod]) > 3:
            files_using += f" (+{len(all_imports[mod])-3} mehr)"
        print(f"  ✅ {mod:30s} verwendet in: {files_using}")
    
    print(f"\n🏠 LOKALE MODULE ({len(local_modules)} Module)")
    print("-" * 80)
    for mod in sorted(local_modules):
        files_using = ', '.join(all_imports[mod][:3])
        if len(all_imports[mod]) > 3:
            files_using += f" (+{len(all_imports[mod])-3} mehr)"
        print(f"  ✅ {mod:30s} verwendet in: {files_using}")
    
    if missing:
        print(f"\n❌ FEHLENDE MODULE ({len(missing)} Module)")
        print("-" * 80)
        for mod in sorted(missing):
            files_using = ', '.join(all_imports[mod][:3])
            if len(all_imports[mod]) > 3:
                files_using += f" (+{len(all_imports[mod])-3} mehr)"
            print(f"  ⚠️  {mod:30s} FEHLT! Verwendet in: {files_using}")
    
    # Zusammenfassung
    print("\n" + "=" * 80)
    print("📊 IMPORT-ZUSAMMENFASSUNG")
    print("=" * 80)
    total = len(std_lib) + len(third_party) + len(local_modules) + len(missing)
    available = len(std_lib) + len(third_party) + len(local_modules)
    
    print(f"✅ Verfügbar:      {available}/{total} Module ({available/total*100:.1f}%)")
    print(f"🐍 Standard Lib:   {len(std_lib)} Module")
    print(f"📚 Third-Party:    {len(third_party)} Pakete")
    print(f"🏠 Lokal:          {len(local_modules)} Module")
    print(f"❌ Fehlend:        {len(missing)} Module")
    
    if missing:
        print("\n⚠️  KRITISCHE FEHLER: Fehlende Module müssen installiert werden!")
        print(f"   pip install {' '.join(sorted(missing))}")
    else:
        print("\n🎉 ALLE IMPORTS SIND VERFÜGBAR!")

if __name__ == "__main__":
    main()
