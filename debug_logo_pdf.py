#!/usr/bin/env python3
"""
Debug Test für Logo-Rendering in PDF
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tempfile

from pdf_template_engine.dynamic_overlay import apply_dynamic_overlay_to_pdf
from pdf_template_engine.placeholders import build_dynamic_data


def test_logo_rendering_debug():
    """Teste Logo-Rendering mit Debug-Output"""
    print("[SEARCH] DEBUG: Logo-Rendering in PDF")
    print("=" * 50)

    # Test-Daten mit bekannten Logo-Herstellern
    project_data = {
        "customer_data": {
            "first_name": "Max",
            "last_name": "Mustermann"
        },
        "project_details": {},
        "selected_products": {
            "module": {
                "product_id": 1,
                "brand_name": "Huawei",
                "product_name": "SUN2000-8KTL-M1"
            },
            "inverter": {
                "product_id": 2,
                "brand_name": "GoodWe",
                "product_name": "GW8K-ET"
            },
            "storage": {
                "product_id": 3,
                "brand_name": "BYD",
                "product_name": "Battery-Box Premium HVM"
            }
        }
    }

    analysis_results = {
        "total_investment_netto": 15000,
        "anlage_kwp": 8.5,
        "annual_pv_production_kwh": 8500
    }

    company_info = {
        "name": "Solar GmbH"
    }

    print("[CHART] Erstelle dynamic_data...")
    dynamic_data = build_dynamic_data(project_data, analysis_results, company_info)

    # Logo-Keys prüfen
    logo_keys = ["module_brand_logo_b64", "inverter_brand_logo_b64", "storage_brand_logo_b64"]
    print("\n[TARGET] Logo-Daten Check:")
    for key in logo_keys:
        if key in dynamic_data and dynamic_data[key]:
            print(f"  [OK] {key}: VORHANDEN ({len(dynamic_data[key])} Zeichen)")
        else:
            print(f"  [ERROR] {key}: FEHLT")

    # Teste nur die Overlay-Funktion (ohne vollständige PDF-Generierung)
    print("\n[TOOL] Teste apply_dynamic_overlay_to_pdf...")

    try:
        # Verwende eine der vorhandenen Template-PDFs als Test (OLD: page 4 -> NEW: page 5)
        template_path = "pdf_templates_static/notext/nt_nt_05.pdf"

        if os.path.exists(template_path):
            print(f"[FILE] Verwende Template: {template_path}")

            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                temp_output = tmp_file.name

            print(f"[TARGET] Erstelle Test-PDF: {temp_output}")

            # Overlay anwenden
            success = apply_dynamic_overlay_to_pdf(
                template_path=template_path,
                output_path=temp_output,
                dynamic_data=dynamic_data,
                page_number=4  # Nur Seite 4 testen
            )

            if success and os.path.exists(temp_output):
                file_size = os.path.getsize(temp_output)
                print(f"[OK] Test-PDF erstellt: {temp_output} ({file_size:,} Bytes)")
                print("[IDEA] Bitte öffne die PDF und prüfe Seite 4!")
                return temp_output
            print("[ERROR] Test-PDF-Erstellung fehlgeschlagen")
        else:
            print(f"[ERROR] Template nicht gefunden: {template_path}")

    except Exception as e:
        print(f"[ERROR] Fehler: {e}")
        import traceback
        traceback.print_exc()

    return None

if __name__ == "__main__":
    pdf_path = test_logo_rendering_debug()
    if pdf_path:
        print(f"\n🎉 Debug-PDF erstellt: {pdf_path}")
    else:
        print("\n[ERROR] Debug-Test fehlgeschlagen")
