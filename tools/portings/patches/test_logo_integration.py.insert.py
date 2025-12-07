# === AUTO-GENERATED INSERT PATCH ===
# target_module: test_logo_integration.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import os


# --- DEF BLOCK START: func test_logo_database ---
def test_logo_database():
    """Testet die Logo-Datenbank-Funktionalität"""
    print("=== TESTE LOGO-DATENBANK ===")

    try:
        from brand_logo_db import (
            add_brand_logo,
            create_brand_logos_table,
            get_brand_logo,
            get_logos_for_brands,
            list_all_brand_logos,
        )
        from database import get_db_connection

        # Verbindung testen
        conn = get_db_connection()
        if conn:
            print("Datenbankverbindung erfolgreich")

            # Tabelle erstellen
            create_brand_logos_table(conn)
            print("Logo-Tabelle erstellt/überprüft")

            conn.close()
        else:
            print("Keine Datenbankverbindung")
            return False

        # Beispiel-Logo hinzufügen (Base64-encoded 1x1 PNG)
        test_logo_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAHdl6v5ygAAAABJRU5ErkJggg=="

        success = add_brand_logo("TestHersteller", test_logo_b64, "PNG")
        if success:
            print("Test-Logo hinzugefügt")
        else:
            print("Fehler beim Hinzufügen des Test-Logos")
            return False

        # Logo abrufen
        logo = get_brand_logo("TestHersteller")
        if logo:
            print(f"Logo abgerufen: {logo['brand_name']}")
        else:
            print("Logo konnte nicht abgerufen werden")
            return False

        # Alle Logos auflisten
        logos = list_all_brand_logos()
        print(f"Gesamt {len(logos)} Logos in der Datenbank")

        # Logos für mehrere Hersteller abrufen
        logos_dict = get_logos_for_brands(["TestHersteller"])
        if "TestHersteller" in logos_dict:
            print("Bulk-Logo-Abruf funktioniert")
        else:
            print("Bulk-Logo-Abruf fehlgeschlagen")
            return False

        return True

    except Exception as e:
        print(f"Logo-Datenbank-Test fehlgeschlagen: {e}")
        return False
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func test_logo_integration ---
def test_logo_integration():
    """Testet die neue YAML-basierte Logo-Integration über build_dynamic_data"""
    print("\n=== TESTE YAML-LOGO-INTEGRATION ===")
    try:
        from brand_logo_db import add_brand_logo
        from pdf_template_engine.placeholders import build_dynamic_data
        # Mini-Setup: Dummy-Logos hinzufügen
        dummy_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAHdl6v5ygAAAABJRU5ErkJggg=="
        add_brand_logo("SolarTech", dummy_png, "PNG")
        add_brand_logo("InvertCorp", dummy_png, "PNG")
        add_brand_logo("BatteryPro", dummy_png, "PNG")
        project = {
            "project_details": {
                "module_manufacturer": "SolarTech",
                "inverter_manufacturer": "InvertCorp",
                "storage_manufacturer": "BatteryPro"
            }
        }
        data = build_dynamic_data(project, {}, {})
        keys = [
            "module_brand_logo_b64",
            "inverter_brand_logo_b64",
            "storage_brand_logo_b64"]
        ok = True
        for k in keys:
            if k in data and data.get(k):
                print(f"{k} gesetzt (len={len(data.get(k))})")
            else:
                print(f"{k} fehlt")
                ok = False
        return ok
    except Exception as e:
        print(f"YAML-Logo-Integration Fehler: {e}")
        return False
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func test_placeholder_integration ---
def test_placeholder_integration():
    """Testet Platzhalter-Mapping für Logo-Keys (ohne alte Dummy-Placeholder)"""
    print("\n=== TESTE PLATZHALTER-MAPPING ===")
    try:
        from pdf_template_engine.placeholders import PLACEHOLDER_MAPPING
        needed = {
            "Logomodul": "module_brand_logo_b64",
            "Logoricht": "inverter_brand_logo_b64",
            "Logoakkus": "storage_brand_logo_b64"}
        ok = True
        for yaml_key, data_key in needed.items():
            mapped = PLACEHOLDER_MAPPING.get(yaml_key)
            if mapped == data_key:
                print(f"Mapping {yaml_key} -> {data_key}")
            else:
                print(
                    f"Mapping für {yaml_key} falsch oder fehlt (gefunden: {mapped})")
                ok = False
        return ok
    except Exception as e:
        print(f"Platzhalter-Mapping-Test Fehler: {e}")
        return False
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func test_coords_update ---
def test_coords_update():
    """Testet die Koordinaten-Datei-Aktualisierung"""
    print("\n=== TESTE KOORDINATEN-AKTUALISIERUNG ===")

    try:
        # Prüfe ob coords/seite4.yml Logo-Platzhalter enthält
        coords_file = "coords/seite4.yml"

        if os.path.exists(coords_file):
            with open(coords_file, encoding='utf-8') as f:
                content = f.read()

            # Neue YAML-basierten Texte (Keys in PLACEHOLDER_MAPPING)
            yaml_texts = ["Logomodul", "Logoricht", "Logoakkus"]
            found = sum(1 for t in yaml_texts if t in content)
            if found == len(yaml_texts):
                print(
                    f"Alle {found} Logo-Texte in coords/seite4.yml vorhanden")
                return True
            print(f"Nur {found}/{len(yaml_texts)} Logo-Texte gefunden")
            return False
        print("coords/seite4.yml nicht gefunden")
        return False

    except Exception as e:
        print(f"Koordinaten-Test fehlgeschlagen: {e}")
        return False
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func run_all_tests ---
def run_all_tests():
    """Führt alle Tests aus"""
    print(" LOGO-INTEGRATION VOLLTEST")
    print("=" * 50)

    tests = [
        ("Logo-Datenbank", test_logo_database),
        ("PDF-Logo-Integration", test_logo_integration),
        ("Platzhalter-Integration", test_placeholder_integration),
        ("Koordinaten-Update", test_coords_update)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"{test_name} - Kritischer Fehler: {e}")
            results[test_name] = False

    print("\n" + "=" * 50)
    print("TEST-ZUSAMMENFASSUNG:")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results.items():
        status = "BESTANDEN" if result else "FEHLGESCHLAGEN"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1

    print(f"\nErgebnis: {passed}/{total} Tests bestanden")

    if passed == total:
        print(" ALLE TESTS BESTANDEN! Logo-Integration ist bereit.")
    else:
        print("EINIGE TESTS FEHLGESCHLAGEN. Überprüfung erforderlich.")

    return passed == total
# --- DEF BLOCK END ---
