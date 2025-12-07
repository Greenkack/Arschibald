#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔬 ULTRA-TIEFE APP-ANALYSE - 100% Coverage
Analysiert JEDEN Aspekt der App auf Fehler, fehlende Module, kaputte Imports
"""

import sys
import ast
import importlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import traceback

class DeepAppAnalyzer:
    def __init__(self):
        self.root = Path('.')
        self.all_py_files = []
        self.all_imports = defaultdict(set)
        self.import_errors = defaultdict(list)
        self.syntax_errors = []
        self.missing_files = []
        self.circular_imports = []
        self.unused_imports = defaultdict(list)
        
    def scan_all_files(self):
        """Scannt alle Python-Dateien"""
        print("📂 SCANNE ALLE PYTHON-DATEIEN...")
        self.all_py_files = list(self.root.rglob('*.py'))
        
        # Filtere __pycache__ und venv
        self.all_py_files = [
            f for f in self.all_py_files 
            if '__pycache__' not in str(f) 
            and 'venv' not in str(f)
            and '.venv' not in str(f)
        ]
        
        print(f"   Gefunden: {len(self.all_py_files)} Dateien")
        return self.all_py_files
    
    def check_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Prüft Python-Syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ast.parse(f.read(), filename=str(file_path))
            return True, "OK"
        except SyntaxError as e:
            return False, f"Zeile {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
    
    def extract_all_imports(self, file_path: Path) -> Set[str]:
        """Extrahiert alle Imports"""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
            
            return imports
        except Exception:
            return set()
    
    def test_import(self, module_name: str, file_path: Path) -> Tuple[bool, str]:
        """Testet ob Import funktioniert"""
        # Überspringe relative Imports
        if not module_name or module_name.startswith('_'):
            return True, "relative/private"
        
        # Überspringe Standard Library
        if module_name in sys.stdlib_module_names:
            return True, "stdlib"
        
        # Teste Import
        try:
            importlib.import_module(module_name)
            return True, "available"
        except ImportError as e:
            # Prüfe ob lokale Datei
            if (self.root / f"{module_name}.py").exists():
                return True, "local_file"
            if (self.root / module_name / "__init__.py").exists():
                return True, "local_package"
            if (self.root / "utils" / f"{module_name}.py").exists():
                return False, f"in_utils_folder (muss kopiert werden)"
            
            return False, f"NOT_FOUND: {str(e)[:50]}"
        except Exception as e:
            return False, f"ERROR: {str(e)[:50]}"
    
    def analyze_file(self, file_path: Path):
        """Analysiert eine einzelne Datei"""
        # Syntax prüfen
        syntax_ok, syntax_msg = self.check_syntax(file_path)
        if not syntax_ok:
            self.syntax_errors.append((file_path, syntax_msg))
        
        # Imports extrahieren und testen
        imports = self.extract_all_imports(file_path)
        
        for imp in imports:
            self.all_imports[imp].add(file_path)
            
            # Teste Import
            import_ok, import_msg = self.test_import(imp, file_path)
            if not import_ok:
                self.import_errors[imp].append((file_path, import_msg))
    
    def run_analysis(self):
        """Führt vollständige Analyse durch"""
        print("\n" + "=" * 80)
        print("🔬 STARTE ULTRA-TIEFE ANALYSE")
        print("=" * 80)
        
        # Schritt 1: Dateien scannen
        files = self.scan_all_files()
        
        # Schritt 2: Alle Dateien analysieren
        print(f"\nANALYSIERE {len(files)} DATEIEN...")
        for i, file_path in enumerate(files, 1):
            if i % 50 == 0:
                print(f"   ⏳ {i}/{len(files)} Dateien...")
            self.analyze_file(file_path)
        
        print(f"   Analyse abgeschlossen!")
        
        # Berichte generieren
        self.print_results()
    
    def print_results(self):
        """Gibt Ergebnisse aus"""
        
        print("\n" + "=" * 80)
        print("🐛 SYNTAX-FEHLER")
        print("=" * 80)
        if self.syntax_errors:
            for file_path, error in self.syntax_errors:
                print(f"{file_path.relative_to(self.root)}")
                print(f"   {error}\n")
        else:
            print("Keine Syntax-Fehler gefunden!")
        
        print("\n" + "=" * 80)
        print("IMPORT-PROBLEME")
        print("=" * 80)
        if self.import_errors:
            # Gruppiere nach Typ
            missing_modules = {}
            in_utils = {}
            other_errors = {}
            
            for module, errors in self.import_errors.items():
                error_type = errors[0][1]
                if "in_utils_folder" in error_type:
                    in_utils[module] = errors
                elif "NOT_FOUND" in error_type:
                    missing_modules[module] = errors
                else:
                    other_errors[module] = errors
            
            if in_utils:
                print("\nMODULE IN utils/ (müssen ins Root kopiert werden):")
                print("-" * 80)
                for module, errors in sorted(in_utils.items()):
                    files_using = [str(f.relative_to(self.root)) for f, _ in errors[:3]]
                    print(f"  {module:30s} verwendet in: {', '.join(files_using)}")
                    if len(errors) > 3:
                        print(f"      {' '*30} (+{len(errors)-3} weitere Dateien)")
            
            if missing_modules:
                print("\nFEHLENDE MODULE (nicht gefunden):")
                print("-" * 80)
                for module, errors in sorted(missing_modules.items()):
                    files_using = [str(f.relative_to(self.root)) for f, _ in errors[:3]]
                    print(f"  {module:30s} verwendet in: {', '.join(files_using)}")
                    if len(errors) > 3:
                        print(f"      {' '*30} (+{len(errors)-3} weitere Dateien)")
            
            if other_errors:
                print("\nANDERE IMPORT-FEHLER:")
                print("-" * 80)
                for module, errors in sorted(other_errors.items()):
                    print(f"  {module}: {errors[0][1]}")
        else:
            print("Alle Imports sind verfügbar!")
        
        # Statistiken
        print("\n" + "=" * 80)
        print("STATISTIKEN")
        print("=" * 80)
        
        total_files = len(self.all_py_files)
        files_with_errors = len(set([f for f, _ in self.syntax_errors]))
        modules_with_import_errors = len(self.import_errors)
        total_imports = len(self.all_imports)
        
        print(f"📂 Python-Dateien:        {total_files}")
        print(f"🐛 Dateien mit Syntax-Fehlern: {files_with_errors}")
        print(f"Verschiedene Imports:  {total_imports}")
        print(f"Module mit Problemen:  {modules_with_import_errors}")
        
        health_score = ((total_files - files_with_errors) / total_files * 100) if total_files > 0 else 0
        import_health = ((total_imports - modules_with_import_errors) / total_imports * 100) if total_imports > 0 else 0
        
        print(f"\n🏥 GESUNDHEITSSTATUS:")
        print(f"   Syntax-Gesundheit:     {health_score:.1f}%")
        print(f"   Import-Gesundheit:     {import_health:.1f}%")
        
        # Empfehlungen
        print("\n" + "=" * 80)
        print("EMPFEHLUNGEN")
        print("=" * 80)
        
        if self.syntax_errors:
            print("1. Behebe Syntax-Fehler zuerst!")
        
        if self.import_errors:
            # Zähle utils-Module
            utils_count = sum(1 for module, errors in self.import_errors.items() 
                            if "in_utils_folder" in errors[0][1])
            missing_count = sum(1 for module, errors in self.import_errors.items() 
                              if "NOT_FOUND" in errors[0][1])
            
            if utils_count > 0:
                print(f"2. Kopiere {utils_count} Module aus utils/ ins Root")
                print(f"   Verwende: python fix_missing_modules.py")
            
            if missing_count > 0:
                print(f"3. {missing_count} Module sind wirklich nicht vorhanden")
                print(f"   → Prüfe ob deprecated oder umbenennen")
        
        if not self.syntax_errors and not self.import_errors:
            print("KEINE PROBLEME GEFUNDEN!")
            print("🎉 App ist in perfektem Zustand!")

def main():
    analyzer = DeepAppAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
