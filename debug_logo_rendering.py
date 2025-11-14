#!/usr/bin/env python3
"""
Logo Debug Test - Spezifischer Test für Logo-Rendering in PDF
"""

from pdf_template_engine.placeholders import build_dynamic_data
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_logo_debug():
    """Debuggt das Logo-Rendering im Detail"""
    print("[SEARCH] LOGO DEBUG TEST")
    print("=" * 60)

    # 1. Test-Daten vorbereiten
    project_data = {
        "customer_data": {
            "first_name": "Max",
            "last_name": "Mustermann"
        },
        "selected_products": {
            "module": {"brand_name": "Huawei", "product_name": "Test Module"},
            "inverter": {"brand_name": "GoodWe", "product_name": "Test Inverter"},
            "storage": {"brand_name": "BYD", "product_name": "Test Storage"}
        }
    }

    analysis_results = {"total_investment_netto": 15000}
    company_info = {"name": "Test GmbH"}

    # 2. Dynamic Data erstellen
    print("\n[CHART] Erstelle Dynamic Data...")
    dynamic_data = build_dynamic_data(
        project_data, analysis_results, company_info)

    # Logo-Keys prüfen
    logo_keys = [
        "module_brand_logo_b64",
        "inverter_brand_logo_b64",
        "storage_brand_logo_b64"]
    print("Logo-Daten verfügbar:")
    for key in logo_keys:
        if key in dynamic_data and dynamic_data[key]:
            print(f"  [OK] {key}: {len(dynamic_data[key])} Zeichen")
        else:
            print(f"  [ERROR] {key}: FEHLT")

    # 3. Koordinaten aus seite4.yml laden
    print("\n[DESIGN] Lade Koordinaten...")
    try:
        with open("coords/seite4.yml", encoding="utf-8") as f:
            coords_content = f.read()

        # Parse YAML manually für Logo-Platzhalter
        logo_coords = {}
        lines = coords_content.split('\n')
        current_text = None

        for line in lines:
            if line.startswith('Text: Logo'):
                current_text = line.split(': ')[1]
            elif line.startswith('Position: ') and current_text:
                pos_str = line.split(': ')[1]
                # Parse "(x0, y0, x1, y1)" format
                pos_str = pos_str.strip('()')
                coords = [float(x.strip()) for x in pos_str.split(',')]
                logo_coords[current_text] = coords
                print(f"  {current_text}: {coords}")
                current_text = None

    except Exception as e:
        print(f"Fehler beim Laden der Koordinaten: {e}")
        return False

    # 4. Teste Logo-Rendering-Logik simuliert
    print("\n[DESIGN] Simuliere Logo-Rendering...")
    for logo_name, coords in logo_coords.items():
        x0, y0, x1, y1 = coords
        width_from_coords = abs(x1 - x0)
        height_from_coords = abs(y1 - y0)

        print(f"\n{logo_name}:")
        print(f"  Koordinaten: ({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f})")
        print(
            f"  Berechnet: Breite={
                width_from_coords:.1f}, Höhe={
                height_from_coords:.1f}")

        if width_from_coords < 1 or height_from_coords < 1:
            print("  [WARNING]  PROBLEM: Zu kleine Dimensionen für Logo!")
        else:
            print("  [OK] Dimensionen OK")

        # Passender Logo-Key
        logo_key_map = {
            "Logomodul": "module_brand_logo_b64",
            "Logoricht": "inverter_brand_logo_b64",
            "Logoakkus": "storage_brand_logo_b64"
        }

        logo_key = logo_key_map.get(logo_name)
        if logo_key and logo_key in dynamic_data and dynamic_data[logo_key]:
            print(f"  [OK] Logo-Daten für {logo_key} verfügbar")
        else:
            print(f"  [ERROR] Logo-Daten für {logo_key} FEHLEN")

    return True


if __name__ == "__main__":
    test_logo_debug()
