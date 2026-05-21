"""test_build_completeness.py - Schneller Build-Vollständigkeitstest"""
import sys
import importlib
from pathlib import Path

def test_module_import(module_name, description):
    """Teste ob ein Modul importiert werden kann"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {description}: {module_name}")
        return True
    except Exception as e:
        print(f"✗ {description}: {module_name} - {str(e)[:50]}")
        return False

def test_file_exists(file_path, description):
    """Teste ob eine Datei existiert"""
    path = Path(file_path)
    if path.exists():
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path}")
        return False

print("="*70)
print("BUILD VOLLSTÄNDIGKEITSTEST - Kritische Komponenten")
print("="*70)

success_count = 0
total_count = 0

# Core Modules
print("\n[1] CORE MODULES")
core_modules = [
    ("gui", "Hauptanwendung"),
    ("database", "Datenbank-Layer"),
    ("calculations", "PV-Berechnungen"),
    ("calculations_heatpump", "WP-Berechnungen"),
    ("pdf_generator", "PDF-Generator"),
    ("crm", "CRM-System"),
]

for mod, desc in core_modules:
    total_count += 1
    if test_module_import(mod, desc):
        success_count += 1

# Neue Module (Session)
print("\n[2] NEU ERSTELLTE MODULE")
new_modules = [
    ("excel_processing", "Excel-Verarbeitung"),
    ("data_grid", "Data Grid"),
    ("grid_controller", "Grid Controller"),
    ("heating_cost_calculator", "Heizkosten-Rechner"),
    ("heating_calculator_ui", "Heizkosten UI"),
    ("authentication", "Authentifizierung"),
    ("password_manager", "Passwort-Manager"),
    ("session_security", "Session-Sicherheit"),
    ("job_scheduler", "Job Scheduler"),
    ("background_tasks", "Background Tasks"),
    ("task_queue", "Task Queue"),
    ("csv_importer", "CSV Import"),
    ("excel_exporter", "Excel Export"),
    ("data_migration", "Daten-Migration"),
    ("report_generator", "Report Generator"),
    ("chart_builder", "Chart Builder"),
    ("statistics_engine", "Statistics Engine"),
]

for mod, desc in new_modules:
    total_count += 1
    if test_module_import(mod, desc):
        success_count += 1

# WP Implementation
print("\n[3] WÄRMEPUMPEN-IMPLEMENTATION")
wp_modules = [
    ("wp_implements.heat_pump_calculator", "WP Calculator"),
    ("wp_implements.heat_pump_ui", "WP UI"),
    ("wp_implements.wp_bridge", "WP Bridge"),
]

for mod, desc in wp_modules:
    total_count += 1
    if test_module_import(mod, desc):
        success_count += 1

# PDF System
print("\n[4] PDF-SYSTEM")
pdf_modules = [
    ("pdf_template_engine.dynamic_overlay", "PDF Overlay Engine"),
    ("pdf_template_engine.placeholders", "PDF Placeholders"),
    ("product_rotation_engine", "Produkt-Rotation"),
    ("price_modification_engine", "Preis-Modifikation"),
    ("multi_pdf_positioning.coordinate_extractor", "Koordinaten-Extraktor"),
]

for mod, desc in pdf_modules:
    total_count += 1
    if test_module_import(mod, desc):
        success_count += 1

# Critical Dependencies
print("\n[5] KRITISCHE DEPENDENCIES")
dependencies = [
    ("streamlit", "Streamlit"),
    ("pandas", "Pandas"),
    ("numpy", "NumPy"),
    ("reportlab", "ReportLab"),
    ("PIL", "Pillow"),
    ("yaml", "PyYAML"),
    ("pymupdf", "PyMuPDF"),
    ("openpyxl", "OpenPyXL"),
    ("matplotlib", "Matplotlib"),
    ("plotly", "Plotly"),
    ("pyvista", "PyVista"),
]

for mod, desc in dependencies:
    total_count += 1
    if test_module_import(mod, desc):
        success_count += 1

# Critical Files
print("\n[6] KRITISCHE DATEIEN")
critical_files = [
    ("data/app_data.db", "Datenbank"),
    (".streamlit/config.toml", "Streamlit Config"),
    (".streamlit/secrets.toml", "Secrets"),
    ("config.json", "App Config"),
    ("settings.json", "App Settings"),
    ("de.json", "Lokalisierung"),
    ("app_icon.ico", "App Icon"),
]

for file_path, desc in critical_files:
    total_count += 1
    if test_file_exists(file_path, desc):
        success_count += 1

# Test Files
print("\n[7] TEST-DATEIEN")
test_files = [
    ("tests/test_pdf_generation.py", "PDF Tests"),
    ("tests/test_database.py", "Database Tests"),
    ("tests/test_pricing.py", "Pricing Tests"),
    ("tests/test_calculations.py", "Calculations Tests"),
]

for file_path, desc in test_files:
    total_count += 1
    if test_file_exists(file_path, desc):
        success_count += 1

# Summary
print("\n" + "="*70)
print(f"ERGEBNIS: {success_count}/{total_count} Tests erfolgreich ({success_count/total_count*100:.1f}%)")
print("="*70)

if success_count == total_count:
    print("\n✅ ALLE KOMPONENTEN VOLLSTÄNDIG - BUILD BEREIT!")
    sys.exit(0)
elif success_count >= total_count * 0.9:
    print(f"\n⚠️  {total_count - success_count} Komponenten fehlen - Build fast bereit")
    sys.exit(1)
else:
    print(f"\n✗ {total_count - success_count} Komponenten fehlen - Build nicht bereit")
    sys.exit(1)
