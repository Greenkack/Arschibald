#!/usr/bin/env python3
"""
Test-Skript zur Überprüfung der Produktbild-Integration in PDF Seite 4
"""
from pdf_template_engine.placeholders import build_dynamic_data
from pdf_template_engine.dynamic_overlay import generate_overlay
from pathlib import Path
import tempfile
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_product_images():
    # Beispiel-Daten für Test - Verwende Produkte mit PNG-Bildern
    project_data = {
        "project_details": {
            "selected_module_name": "BetaSun 400W",           # Hat jetzt PNG-Bild
            # Hat kein Bild (falls nicht aktualisiert)
            "selected_inverter_name": "PowerMax 5K",
            # Hat kein Bild (falls nicht aktualisiert)
            "selected_storage_name": "EnergyCell 10kWh",
            "module_quantity": 20,
            "installation_location": "Test-Location",
            "customer_name": "Test Kunde",
            "projekt_name": "Test Projekt"
        }
    }

    analysis_results = {
        "anlage_kwp": 8.8,
        "annual_pv_production_kwh": 8500,
        "final_price": 25000.0
    }

    company_info = {
        "company_name": "Test Solar GmbH",
        "street": "Teststraße 1",
        "plz": "12345",
        "city": "Teststadt"
    }

    print("Erstelle dynamic_data...")
    dynamic_data = build_dynamic_data(
        project_data, analysis_results, company_info)

    print(f"Dynamic data erstellt mit {len(dynamic_data)} Einträgen")

    # Überprüfe Bildschłüssel
    image_keys = [
        "module_image_b64",
        "inverter_image_b64",
        "storage_image_b64"]
    for key in image_keys:
        value = dynamic_data.get(key, "")
        print(f"{key}: {len(value) if value else 0} Zeichen")
        if value:
            print(f"  Erste 50 Zeichen: {value[:50]}...")

    # Teste PDF-Generation mit Bildern
    print("\nGeneriere Test-PDF...")
    try:
        coords_dir = Path("coords")
        overlay_bytes = generate_overlay(
            coords_dir, dynamic_data, total_pages=7)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(overlay_bytes)
            pdf_path = tmp.name

        print(f"PDF erstellt: {pdf_path}")
        print(f"Dateigröße: {len(overlay_bytes)} Bytes")
    except Exception as e:
        print(f"Fehler bei PDF-Erstellung: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_product_images()
