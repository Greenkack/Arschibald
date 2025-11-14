"""
Test-Skript zur Überprüfung der CRM-Integration in gui.py
Datum: 2025-11-07
"""

import importlib
import sys
from pathlib import Path

# Workspace-Pfad hinzufügen
workspace_path = Path(__file__).parent
sys.path.insert(0, str(workspace_path))

class CRMIntegrationTest:
    """Testet die CRM-Integration in der Hauptanwendung"""
    
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def test_module_imports(self):
        """Test 1: Prüft ob alle CRM-Module importierbar sind"""
        print("\n" + "="*60)
        print("TEST 1: CRM-Module Import-Test")
        print("="*60)
        
        modules_to_test = [
            ('crm', 'Hauptmodul Kundenverwaltung'),
            ('crm_dashboard_ui', 'Dashboard UI'),
            ('crm_pipeline_ui', 'Pipeline UI'),
            ('crm_calendar_ui', 'Kalender UI'),
        ]
        
        for module_name, description in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                print(f"[OK] {module_name:20s} - {description}")
                self.results['passed'].append(f"Import: {module_name}")
            except ImportError as e:
                print(f"[ERROR] {module_name:20s} - FEHLER: {e}")
                self.results['failed'].append(f"Import: {module_name} - {e}")
            except Exception as e:
                print(f"[WARNING]  {module_name:20s} - WARNUNG: {e}")
                self.results['warnings'].append(f"Import: {module_name} - {e}")
    
    def test_render_functions(self):
        """Test 2: Prüft ob alle render-Funktionen existieren"""
        print("\n" + "="*60)
        print("TEST 2: Render-Funktionen Verfügbarkeit")
        print("="*60)
        
        functions_to_test = [
            ('crm', 'render_crm', 'Kundenverwaltung Render-Funktion'),
            ('crm_dashboard_ui', 'render_crm_dashboard', 'Dashboard Render-Funktion'),
            ('crm_pipeline_ui', 'render_crm_pipeline', 'Pipeline Render-Funktion'),
            ('crm_calendar_ui', 'render_crm_calendar', 'Kalender Render-Funktion'),
        ]
        
        for module_name, func_name, description in functions_to_test:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, func_name):
                    func = getattr(module, func_name)
                    if callable(func):
                        print(f"[OK] {module_name}.{func_name:25s} - {description}")
                        self.results['passed'].append(f"Funktion: {module_name}.{func_name}")
                    else:
                        print(f"[ERROR] {module_name}.{func_name:25s} - NICHT CALLABLE")
                        self.results['failed'].append(f"Funktion: {module_name}.{func_name} nicht callable")
                else:
                    print(f"[ERROR] {module_name}.{func_name:25s} - NICHT GEFUNDEN")
                    self.results['failed'].append(f"Funktion: {module_name}.{func_name} fehlt")
            except Exception as e:
                print(f"[WARNING]  {module_name}.{func_name:25s} - FEHLER: {e}")
                self.results['warnings'].append(f"Funktion: {module_name}.{func_name} - {e}")
    
    def test_gui_integration(self):
        """Test 3: Prüft die Integration in gui.py"""
        print("\n" + "="*60)
        print("TEST 3: GUI.py Integration")
        print("="*60)
        
        try:
            # gui.py Inhalt lesen
            gui_path = workspace_path / 'gui.py'
            with open(gui_path, 'r', encoding='utf-8') as f:
                gui_content = f.read()
            
            # Prüfungen
            checks = [
                ('crm_module: Any | None = None', 'CRM-Modul Variable deklariert'),
                ('crm_dashboard_ui_module: Any | None = None', 'Dashboard-Modul Variable deklariert'),
                ('crm_pipeline_ui_module: Any | None = None', 'Pipeline-Modul Variable deklariert'),
                ('crm_calendar_ui_module: Any | None = None', 'Kalender-Modul Variable deklariert'),
                ('crm_module = import_module_with_fallback("crm"', 'CRM-Modul wird importiert'),
                ('crm_dashboard_ui_module = import_module_with_fallback("crm_dashboard_ui"', 'Dashboard-Modul wird importiert'),
                ('crm_pipeline_ui_module = import_module_with_fallback("crm_pipeline_ui"', 'Pipeline-Modul wird importiert'),
                ('crm_calendar_ui_module = import_module_with_fallback("crm_calendar_ui"', 'Kalender-Modul wird importiert'),
                ('elif selected_page_key == "crm":', 'CRM-Menüpunkt existiert'),
                ('render_crm(', 'render_crm() wird aufgerufen'),
                ('render_crm_dashboard(', 'render_crm_dashboard() wird aufgerufen'),
                ('render_crm_pipeline(', 'render_crm_pipeline() wird aufgerufen'),
                ('render_crm_calendar(', 'render_crm_calendar() wird aufgerufen'),
            ]
            
            for search_string, description in checks:
                if search_string in gui_content:
                    print(f"[OK] {description}")
                    self.results['passed'].append(f"GUI: {description}")
                else:
                    print(f"[ERROR] {description} - NICHT GEFUNDEN")
                    self.results['failed'].append(f"GUI: {description} fehlt")
        
        except Exception as e:
            print(f"[ERROR] Fehler beim Lesen von gui.py: {e}")
            self.results['failed'].append(f"GUI-Datei: {e}")
    
    def test_tab_structure(self):
        """Test 4: Prüft die Tab-Struktur im CRM-Bereich"""
        print("\n" + "="*60)
        print("TEST 4: Tab-Struktur")
        print("="*60)
        
        try:
            gui_path = workspace_path / 'gui.py'
            with open(gui_path, 'r', encoding='utf-8') as f:
                gui_content = f.read()
            
            # Prüfe ob alle 4 Tabs definiert sind
            tabs = [
                ('tab_customers', 'Kunden-Tab'),
                ('tab_dashboard', 'Dashboard-Tab'),
                ('tab_pipeline', 'Pipeline-Tab'),
                ('tab_calendar', 'Kalender-Tab'),
            ]
            
            for tab_var, description in tabs:
                if f'{tab_var}' in gui_content:
                    print(f"[OK] {description} definiert")
                    self.results['passed'].append(f"Tab: {description}")
                else:
                    print(f"[ERROR] {description} - FEHLT")
                    self.results['failed'].append(f"Tab: {description} fehlt")
            
            # Prüfe ob st.tabs() mit 4 Tabs aufgerufen wird
            if 'tab_customers, tab_dashboard, tab_pipeline, tab_calendar = st.tabs(' in gui_content:
                print(f"[OK] 4 Tabs werden korrekt erstellt")
                self.results['passed'].append("Tab-Erstellung: 4 Tabs")
            else:
                print(f"[ERROR] Tab-Erstellung inkorrekt")
                self.results['failed'].append("Tab-Erstellung: Falsche Anzahl oder Struktur")
        
        except Exception as e:
            print(f"[ERROR] Fehler beim Tab-Test: {e}")
            self.results['failed'].append(f"Tab-Test: {e}")
    
    def test_text_keys(self):
        """Test 5: Prüft ob alle Text-Keys in gui.py definiert sind"""
        print("\n" + "="*60)
        print("TEST 5: Text-Keys Definitionen")
        print("="*60)
        
        try:
            gui_path = workspace_path / 'gui.py'
            with open(gui_path, 'r', encoding='utf-8') as f:
                gui_content = f.read()
            
            text_keys = [
                ('menu_item_crm', 'Haupt-Menüpunkt'),
                ('menu_item_crm_dashboard', 'Dashboard-Menü'),
                ('menu_item_crm_pipeline', 'Pipeline-Menü'),
                ('menu_item_crm_calendar', 'Kalender-Menü'),
                ('crm_tab_customers', 'Kunden-Tab-Label'),
                ('crm_tab_dashboard', 'Dashboard-Tab-Label'),
                ('crm_tab_pipeline', 'Pipeline-Tab-Label'),
                ('crm_tab_calendar', 'Kalender-Tab-Label'),
            ]
            
            for key, description in text_keys:
                if f'"{key}"' in gui_content:
                    print(f"[OK] Text-Key: {key:30s} - {description}")
                    self.results['passed'].append(f"Text-Key: {key}")
                else:
                    print(f"[ERROR] Text-Key: {key:30s} - FEHLT")
                    self.results['failed'].append(f"Text-Key: {key} fehlt")
        
        except Exception as e:
            print(f"[ERROR] Fehler beim Text-Key-Test: {e}")
            self.results['failed'].append(f"Text-Keys: {e}")
    
    def test_menu_icon(self):
        """Test 6: Prüft ob CRM-Icon im Menü vorhanden ist"""
        print("\n" + "="*60)
        print("TEST 6: Menü-Icon")
        print("="*60)
        
        try:
            gui_path = workspace_path / 'gui.py'
            with open(gui_path, 'r', encoding='utf-8') as f:
                gui_content = f.read()
            
            # Suche nach CRM-Menüeintrag mit Icon
            if '"icon": "👥"' in gui_content and '"key": "crm"' in gui_content:
                print(f"[OK] CRM-Menüpunkt mit Icon 👥 gefunden")
                self.results['passed'].append("Menü: CRM-Icon vorhanden")
            else:
                print(f"[WARNING]  CRM-Menüpunkt oder Icon nicht gefunden")
                self.results['warnings'].append("Menü: Icon möglicherweise fehlend")
        
        except Exception as e:
            print(f"[ERROR] Fehler beim Menü-Test: {e}")
            self.results['failed'].append(f"Menü-Test: {e}")
    
    def print_summary(self):
        """Gibt eine Zusammenfassung der Test-Ergebnisse aus"""
        print("\n" + "="*60)
        print("ZUSAMMENFASSUNG")
        print("="*60)
        
        total = len(self.results['passed']) + len(self.results['failed']) + len(self.results['warnings'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        warnings = len(self.results['warnings'])
        
        print(f"\n[OK] Erfolgreich: {passed}/{total}")
        print(f"[ERROR] Fehlgeschlagen: {failed}/{total}")
        print(f"[WARNING]  Warnungen: {warnings}/{total}")
        
        if failed > 0:
            print("\n[ERROR] FEHLGESCHLAGENE TESTS:")
            for fail in self.results['failed']:
                print(f"   • {fail}")
        
        if warnings > 0:
            print("\n[WARNING]  WARNUNGEN:")
            for warn in self.results['warnings']:
                print(f"   • {warn}")
        
        # Gesamtergebnis
        print("\n" + "="*60)
        if failed == 0 and warnings == 0:
            print("🎉 ALLE TESTS BESTANDEN - CRM VOLLSTÄNDIG INTEGRIERT!")
        elif failed == 0:
            print("[OK] TESTS BESTANDEN - Mit Warnungen")
        else:
            print("[ERROR] TESTS FEHLGESCHLAGEN - Bitte Fehler beheben")
        print("="*60)
        
        return failed == 0

def main():
    """Hauptfunktion - Führt alle Tests aus"""
    print("\n" + "="*60)
    print("CRM INTEGRATION TEST SUITE")
    print("Testet die Verknüpfung aller CRM-Bereiche mit gui.py")
    print("="*60)
    
    tester = CRMIntegrationTest()
    
    # Alle Tests ausführen
    tester.test_module_imports()
    tester.test_render_functions()
    tester.test_gui_integration()
    tester.test_tab_structure()
    tester.test_text_keys()
    tester.test_menu_icon()
    
    # Zusammenfassung
    success = tester.print_summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
