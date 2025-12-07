"""
Test-Script: Prüft welche Produktverwaltungs-Version geladen wird
"""
import sys
import os

print("=" * 60)
print("🔍 IMPORT-TEST: Produktverwaltung")
print("=" * 60)

# Test 1: Optimierte Version
try:
    from admin_product_database_ui_optimized import render_product_admin_ui_optimized
    print("✅ admin_product_database_ui_optimized.py IMPORTIERT")
    print(f"   Funktion: {render_product_admin_ui_optimized.__name__}")
    print(f"   Modul: {render_product_admin_ui_optimized.__module__}")
    OPTIMIZED_AVAILABLE = True
except ImportError as e:
    print(f"❌ admin_product_database_ui_optimized.py FEHLER: {e}")
    OPTIMIZED_AVAILABLE = False

# Test 2: Alte Version
try:
    from admin_product_database_ui import render_product_admin_ui
    print("✅ admin_product_database_ui.py IMPORTIERT (Original)")
    print(f"   Funktion: {render_product_admin_ui.__name__}")
    print(f"   Modul: {render_product_admin_ui.__module__}")
    ORIGINAL_AVAILABLE = True
except ImportError as e:
    print(f"❌ admin_product_database_ui.py FEHLER: {e}")
    ORIGINAL_AVAILABLE = False

# Test 3: Was lädt admin_panel.py?
print("\n" + "=" * 60)
print("🔍 ADMIN_PANEL.PY IMPORT-TEST")
print("=" * 60)

try:
    # Simuliere admin_panel.py Import-Logik
    try:
        from admin_product_database_ui_optimized import render_product_admin_ui_optimized as render_product_admin_ui
        PRODUCT_DB_OPTIMIZED = True
        print("✅ admin_panel.py würde OPTIMIERTE Version laden")
    except ImportError:
        from admin_product_database_ui import render_product_admin_ui
        PRODUCT_DB_OPTIMIZED = False
        print("⚠️  admin_panel.py würde ALTE Version laden")
    
    print(f"   Flag PRODUCT_DB_OPTIMIZED: {PRODUCT_DB_OPTIMIZED}")
    print(f"   Geladene Funktion: {render_product_admin_ui.__name__}")
    print(f"   Modul-Quelle: {render_product_admin_ui.__module__}")
    
except Exception as e:
    print(f"❌ admin_panel.py Import-Simulation FEHLER: {e}")

# Test 4: Wärmepumpen-Version
print("\n" + "=" * 60)
print("🔍 WÄRMEPUMPEN-VERWALTUNG TEST")
print("=" * 60)

try:
    from admin_heatpump_products_optimized import render_heatpump_admin_ui
    print("✅ admin_heatpump_products_optimized.py IMPORTIERT")
    HEATPUMP_AVAILABLE = True
except ImportError as e:
    print(f"❌ admin_heatpump_products_optimized.py FEHLER: {e}")
    HEATPUMP_AVAILABLE = False

# Test 5: Migration-Script
try:
    from migrate_heatpump_to_db import HeatpumpDatabaseMigrator
    print("✅ migrate_heatpump_to_db.py IMPORTIERT")
    MIGRATOR_AVAILABLE = True
except ImportError as e:
    print(f"❌ migrate_heatpump_to_db.py FEHLER: {e}")
    MIGRATOR_AVAILABLE = False

# Zusammenfassung
print("\n" + "=" * 60)
print("📊 ZUSAMMENFASSUNG")
print("=" * 60)
print(f"Optimierte Produktverwaltung: {'✅ OK' if OPTIMIZED_AVAILABLE else '❌ FEHLT'}")
print(f"Original Produktverwaltung:   {'✅ OK' if ORIGINAL_AVAILABLE else '❌ FEHLT'}")
print(f"Wärmepumpen-Verwaltung:       {'✅ OK' if HEATPUMP_AVAILABLE else '❌ FEHLT'}")
print(f"Migrations-Script:            {'✅ OK' if MIGRATOR_AVAILABLE else '❌ FEHLT'}")
print("=" * 60)

if OPTIMIZED_AVAILABLE:
    print("\n✅ EMPFEHLUNG: Streamlit neu starten für optimierte Version")
    print("   Befehl: streamlit run gui.py")
else:
    print("\n❌ PROBLEM: Optimierte Module nicht verfügbar!")
    print("   Prüfen Sie die Datei-Existenz in diesem Verzeichnis.")
