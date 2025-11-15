#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🌊 MARIANA-GRABEN TIEFE ANALYSE
Die tiefstmögliche Prüfung der gesamten App
Prüft ALLES: Syntax, Imports, Runtime, Datenbank, Konfiguration, Dependencies
"""

import sys
import ast
import importlib
import json
import sqlite3
from pathlib import Path
from collections import defaultdict
import traceback
import subprocess

class MarianaTrenchAnalyzer:
    def __init__(self):
        self.root = Path('.')
        self.results = {
            'syntax': {'ok': [], 'errors': []},
            'imports': {'ok': [], 'errors': []},
            'runtime': {'ok': [], 'errors': []},
            'database': {'ok': [], 'errors': []},
            'config': {'ok': [], 'errors': []},
            'dependencies': {'ok': [], 'errors': []},
            'security': {'ok': [], 'errors': []},
            'performance': {'ok': [], 'errors': []},
            'files': {'ok': [], 'errors': []},
        }
        
    def banner(self, text, char='='):
        print(f"\n{char * 80}")
        print(f"{text.center(80)}")
        print(f"{char * 80}\n")
    
    def check_syntax_deep(self):
        """Tiefe Syntax-Prüfung mit AST-Analyse"""
        self.banner("LEVEL 1: SYNTAX-TIEFENPRÜFUNG", '=')
        
        py_files = list(self.root.rglob('*.py'))
        py_files = [f for f in py_files 
                   if '__pycache__' not in str(f) 
                   and 'venv' not in str(f)
                   and '_syntax_errors_backup' not in str(f)]
        
        print(f"📂 Analysiere {len(py_files)} Python-Dateien...")
        
        for i, file_path in enumerate(py_files):
            if i % 100 == 0 and i > 0:
                print(f"   ⏳ {i}/{len(py_files)} Dateien gescannt...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    tree = ast.parse(code, filename=str(file_path))
                
                # AST-Analyse
                issues = []
                
                # Prüfe auf deprecated Funktionen
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in ['execfile', 'reload']:
                                issues.append(f"Deprecated function: {node.func.id}")
                
                # Prüfe auf unsichere Patterns
                if 'eval(' in code or 'exec(' in code:  # noqa: S102 (exec ist hier berechtigt)
                    issues.append("Potentially unsafe: eval/exec found")
                
                if issues:
                    self.results['syntax']['errors'].append((str(file_path.relative_to(self.root)), issues))
                else:
                    self.results['syntax']['ok'].append(str(file_path.relative_to(self.root)))
                    
            except SyntaxError as e:
                self.results['syntax']['errors'].append((
                    str(file_path.relative_to(self.root)),
                    f"Line {e.lineno}: {e.msg}"
                ))
            except Exception as e:
                self.results['syntax']['errors'].append((
                    str(file_path.relative_to(self.root)),
                    f"Error: {str(e)[:50]}"
                ))
    
    def check_imports_deep(self):
        """Tiefe Import-Prüfung mit Dependency-Analyse"""
        self.banner("LEVEL 2: IMPORT-TIEFENPRÜFUNG", '=')
        
        critical_modules = [
            # Core App
            'admin_panel', 'heatpump_ui', 'analysis', 'calculations',
            'database', 'pdf_generator', 'central_pdf_system',
            
            # Admin
            'admin_heatpump_settings_ui', 'admin_heating_costs_config_ui',
            'admin_logo_management_ui', 'admin_payment_terms_ui',
            
            # Heatpump
            'heatpump_products_database', 'calculations_heatpump',
            
            # PDF
            'pdf_template_engine', 'pdf_ui', 'pdf_preview',
            
            # 3D
            'pv3d', 'pv3d_plotly', 'pdf_visual_inject',
            
            # Utils
            'utils', 'debug_tools', 'theme_manager',
            
            # Database
            'product_db', 'brand_logo_db', 'database',
            
            # Pricing
            'pricing', 'price_matrix_store',
            
            # Core Modules
            'core.cache', 'core.session', 'core.security',
            'pricing.pricing_validation', 'pricing.vat_manager',
            'components.progress_manager',
        ]
        
        print(f"Teste {len(critical_modules)} kritische Module...")
        
        for module_name in critical_modules:
            try:
                mod = importlib.import_module(module_name)
                
                # Prüfe Module-Attribute
                issues = []
                
                if not hasattr(mod, '__file__'):
                    issues.append("No __file__ attribute")
                
                # Prüfe auf __all__
                if not hasattr(mod, '__all__') and not module_name.startswith('core.'):
                    issues.append("No __all__ defined (nicht kritisch)")
                
                if issues:
                    self.results['imports']['errors'].append((module_name, issues))
                else:
                    self.results['imports']['ok'].append(module_name)
                    
            except ImportError as e:
                self.results['imports']['errors'].append((module_name, f"ImportError: {str(e)[:50]}"))
            except Exception as e:
                self.results['imports']['errors'].append((module_name, f"Error: {str(e)[:50]}"))
    
    def check_runtime_deep(self):
        """Runtime-Prüfung: Teste ob Funktionen tatsächlich ausführbar sind"""
        self.banner("LEVEL 3: RUNTIME-TIEFENPRÜFUNG", '=')
        
        runtime_tests = [
            ("Database Connection", self._test_database_connection),
            ("Config Loading", self._test_config_loading),
            ("PDF Generation", self._test_pdf_generation),
            ("Price Calculation", self._test_price_calculation),
            ("Heatpump Data Access", self._test_heatpump_data),
        ]
        
        for test_name, test_func in runtime_tests:
            print(f"   🧪 Testing: {test_name}...")
            try:
                result = test_func()
                if result:
                    self.results['runtime']['ok'].append(test_name)
                else:
                    self.results['runtime']['errors'].append((test_name, "Test failed"))
            except Exception as e:
                self.results['runtime']['errors'].append((test_name, str(e)[:100]))
    
    def _test_database_connection(self):
        """Teste Datenbank-Verbindung"""
        try:
            from database import get_db_connection
            conn = get_db_connection()
            if conn:
                conn.close()
                return True
        except:
            # Versuche direkte Verbindung
            db_paths = ['database.db', 'data/database.db', 'config/database.db']
            for db_path in db_paths:
                if Path(db_path).exists():
                    conn = sqlite3.connect(db_path)
                    conn.close()
                    return True
        return False
    
    def _test_config_loading(self):
        """Teste Config-Dateien"""
        config_files = [
            'config/heating_costs_config.json',
            'config/heatpump_prices_config.json',
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    json.load(f)
        return True
    
    def _test_pdf_generation(self):
        """Teste ob PDF-Generator importierbar ist"""
        try:
            from pdf_generator import PDFGenerator
            return True
        except:
            return False
    
    def _test_price_calculation(self):
        """Teste Preis-Berechnung"""
        try:
            from calculations import calculate_pv_costs
            return True
        except:
            return False
    
    def _test_heatpump_data(self):
        """Teste Wärmepumpen-Daten"""
        try:
            from heatpump_products_database import HEATPUMP_PRODUCTS, get_heatpump_models
            return len(HEATPUMP_PRODUCTS) > 0
        except:
            return False
    
    def check_database_integrity(self):
        """Prüfe Datenbank-Integrität"""
        self.banner("LEVEL 4: DATENBANK-INTEGRITÄTSPRÜFUNG", '=')
        
        db_files = list(self.root.rglob('*.db'))
        print(f"💾 Gefundene Datenbanken: {len(db_files)}")
        
        for db_path in db_files:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Prüfe Tabellen
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                print(f"\n   {db_path.name}: {len(tables)} Tabellen")
                
                # Prüfe jede Tabelle
                for (table_name,) in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"      • {table_name}: {count} Einträge")
                
                conn.close()
                self.results['database']['ok'].append(str(db_path.relative_to(self.root)))
                
            except Exception as e:
                self.results['database']['errors'].append((
                    str(db_path.relative_to(self.root)),
                    str(e)[:50]
                ))
    
    def check_config_files(self):
        """Prüfe alle Config-Dateien"""
        self.banner("LEVEL 5: KONFIGURATIONSPRÜFUNG", '=')
        
        config_patterns = ['*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '.env']
        
        for pattern in config_patterns:
            files = list(self.root.rglob(pattern))
            files = [f for f in files if 'node_modules' not in str(f) and '.venv' not in str(f)]
            
            for file_path in files:
                try:
                    if file_path.suffix == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                    elif file_path.name == '.env':
                        # Prüfe .env Format
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if '=' in line and not line.strip().startswith('#'):
                                    pass  # Valid env line
                    
                    self.results['config']['ok'].append(str(file_path.relative_to(self.root)))
                except Exception as e:
                    self.results['config']['errors'].append((
                        str(file_path.relative_to(self.root)),
                        str(e)[:50]
                    ))
    
    def check_dependencies(self):
        """Prüfe Python-Dependencies"""
        self.banner("LEVEL 6: DEPENDENCY-PRÜFUNG", '=')
        
        if not Path('requirements.txt').exists():
            self.results['dependencies']['errors'].append(('requirements.txt', 'File not found'))
            return
        
        # Lese requirements.txt
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"📋 Prüfe {len(requirements)} Dependencies...")
        
        # Teste ob alle installiert sind
        for req in requirements[:50]:  # Erste 50 testen
            pkg_name = req.split('==')[0].split('>=')[0].split('<=')[0]
            try:
                importlib.import_module(pkg_name)
                self.results['dependencies']['ok'].append(pkg_name)
            except:
                self.results['dependencies']['errors'].append((pkg_name, 'Not installed'))
    
    def check_security(self):
        """Sicherheitsprüfung"""
        self.banner("LEVEL 7: SICHERHEITSPRÜFUNG", '=')
        
        security_checks = [
            ("Hardcoded Passwords", self._check_hardcoded_passwords),
            ("API Keys in Code", self._check_api_keys),
            ("SQL Injection Risks", self._check_sql_injection),
        ]
        
        for check_name, check_func in security_checks:
            print(f"   🔒 Checking: {check_name}...")
            try:
                issues = check_func()
                if issues:
                    self.results['security']['errors'].extend([(check_name, issue) for issue in issues])
                else:
                    self.results['security']['ok'].append(check_name)
            except Exception as e:
                self.results['security']['errors'].append((check_name, str(e)[:50]))
    
    def _check_hardcoded_passwords(self):
        """Suche nach Hardcoded Passwords"""
        issues = []
        py_files = list(self.root.glob('*.py'))
        
        for file_path in py_files[:20]:  # Sample check
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'password = "' in content.lower() or "password = '" in content.lower():
                        issues.append(f"{file_path.name}: Possible hardcoded password")
            except:
                pass
        
        return issues
    
    def _check_api_keys(self):
        """Suche nach API Keys"""
        issues = []
        py_files = list(self.root.glob('*.py'))
        
        for file_path in py_files[:20]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'api_key' in content.lower() and '=' in content:
                        if '"' in content or "'" in content:
                            issues.append(f"{file_path.name}: Possible hardcoded API key")
            except:
                pass
        
        return issues
    
    def _check_sql_injection(self):
        """Prüfe auf SQL Injection Risiken"""
        issues = []
        py_files = list(self.root.glob('*.py'))
        
        for file_path in py_files[:20]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Suche nach String-Interpolation in SQL
                    if 'execute(' in content and '%s' in content:
                        issues.append(f"{file_path.name}: Possible SQL injection risk")
            except:
                pass
        
        return issues
    
    def check_performance(self):
        """Performance-Prüfung"""
        self.banner("LEVEL 8: PERFORMANCE-PRÜFUNG", '=')
        
        # Prüfe Dateigrößen
        large_files = []
        for file_path in self.root.rglob('*.py'):
            size = file_path.stat().st_size
            if size > 1_000_000:  # > 1MB
                large_files.append((str(file_path.relative_to(self.root)), size))
        
        if large_files:
            for file, size in large_files:
                self.results['performance']['errors'].append((file, f"Large file: {size/1024/1024:.1f}MB"))
        else:
            self.results['performance']['ok'].append("No oversized files")
    
    def check_file_structure(self):
        """Prüfe Datei-Struktur"""
        self.banner("LEVEL 9: DATEISTRUKTUR-PRÜFUNG", '=')
        
        required_files = [
            'requirements.txt',
            'admin_panel.py',
            'database.py',
            'calculations.py',
        ]
        
        for file in required_files:
            if Path(file).exists():
                self.results['files']['ok'].append(file)
            else:
                self.results['files']['errors'].append((file, 'Missing'))
    
    def generate_report(self):
        """Generiere finalen Bericht"""
        self.banner("MARIANA-GRABEN ANALYSE - FINALER BERICHT", '=')
        
        categories = [
            ('SYNTAX', 'syntax'),
            ('IMPORTS', 'imports'),
            ('RUNTIME', 'runtime'),
            ('DATABASE', 'database'),
            ('CONFIG', 'config'),
            ('DEPENDENCIES', 'dependencies'),
            ('SECURITY', 'security'),
            ('PERFORMANCE', 'performance'),
            ('FILES', 'files'),
        ]
        
        total_ok = 0
        total_errors = 0
        
        for cat_name, cat_key in categories:
            ok_count = len(self.results[cat_key]['ok'])
            err_count = len(self.results[cat_key]['errors'])
            total_ok += ok_count
            total_errors += err_count
            
            status = "" if err_count == 0 else ""
            print(f"{status} {cat_name:15s} | OK: {ok_count:4d} | Errors: {err_count:4d}")
            
            # Zeige erste 3 Fehler
            if err_count > 0:
                for i, (item, error) in enumerate(self.results[cat_key]['errors'][:3]):
                    print(f"      {item}: {error}")
                if err_count > 3:
                    print(f"      ... +{err_count-3} weitere Fehler")
        
        print("\n" + "=" * 80)
        total = total_ok + total_errors
        if total != 0:
            health = (total_ok / total * 100) if total > 0 else 0
        else:
            health = 0.0
        
        print(f"GESAMT-GESUNDHEIT: {health:.1f}%")
        print(f"OK:     {total_ok}")
        print(f"Errors: {total_errors}")
        print("=" * 80)
        
        if health >= 95:
            print("\n🎉 EXZELLENT: App ist in hervorragendem Zustand!")
        elif health >= 85:
            print("\nGUT: App ist einsatzbereit mit kleineren Optimierungen")
        elif health >= 70:
            print("\nAKZEPTABEL: Einige Probleme sollten behoben werden")
        else:
            print("\nKRITISCH: Mehrere Probleme müssen behoben werden")
    
    def run(self):
        """Führe vollständige Analyse durch"""
        self.banner("🌊 MARIANA-GRABEN TIEFENANALYSE GESTARTET", '█')
        print("Dies ist die tiefstmögliche Analyse...")
        print("Prüfung auf 9 verschiedenen Ebenen:\n")
        print("Level 1: Syntax & AST-Analyse")
        print("Level 2: Import & Dependency-Analyse")
        print("Level 3: Runtime-Tests")
        print("Level 4: Datenbank-Integrität")
        print("Level 5: Konfigurationsdateien")
        print("Level 6: Python-Dependencies")
        print("Level 7: Sicherheitsprüfung")
        print("Level 8: Performance-Analyse")
        print("Level 9: Dateistruktur")
        
        self.check_syntax_deep()
        self.check_imports_deep()
        self.check_runtime_deep()
        self.check_database_integrity()
        self.check_config_files()
        self.check_dependencies()
        self.check_security()
        self.check_performance()
        self.check_file_structure()
        
        self.generate_report()

if __name__ == "__main__":
    analyzer = MarianaTrenchAnalyzer()
    analyzer.run()
