#!/usr/bin/env python3
"""
Test-Skript um ein PDF mit Seite 6 Charts zu erstellen
"""

import os
import sys
from pathlib import Path

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_test_pdf():
    """Erstelle ein Test-PDF mit Seite 6 Charts"""
    print("🎨 Erstelle Test-PDF mit Seite 6 Charts...")

    try:
        import io

        from pypdf import PdfReader, PdfWriter

        from pdf_template_engine.dynamic_overlay import generate_overlay
        from pdf_template_engine.placeholders import build_dynamic_data

        # Test-Daten mit realistischen Werten
        test_project_data = {
            "customer_data": {
                "first_name": "Max",
                "last_name": "Mustermann",
                "email": "max@example.com",
                "phone_mobile": "0123456789",
                "address": "Musterstraße 1",
                "zip_code": "12345",
                "city": "Musterstadt"
            },
            "project_details": {
                "annual_consumption_kwh": 6000,
                "pv_modules_count": 28,
                "module_power_wp": 400,
                "storage_capacity_kwh": 12.09,
                "inverter_power_w": 10000
            }
        }

        test_analysis_results = {
            "anlage_kwp": 11.2,
            "annual_yield_kwh": 8251.92,
            "storage_capacity_kwh": 12.09,
            "self_supply_rate_percent": 54,
            "self_consumption_percent": 42
        }

        test_company_info = {
            "name": "TommaTech GmbH",
            "street": "Zeppelinstraße 14",
            "zip_code": "85748",
            "city": "Garching b. München",
            "phone": "+49 89 1250 36 860",
            "email": "mail@tommatech.de"
        }

        # Generiere dynamische Daten
        coords_dir = Path("coords")
        dynamic_data = build_dynamic_data(
            test_project_data,
            test_analysis_results,
            test_company_info)

        print(
            f"📊 Speicher-Relationen: Verbrauch={
                dynamic_data.get('storage_consumption_ratio_percent')}%, Produktion={
                dynamic_data.get('storage_production_ratio_percent')}%")

        # Generiere Overlay für alle 7 Seiten
        overlay_bytes = generate_overlay(
            coords_dir, dynamic_data, total_pages=7)

        # Lade Template-PDFs
        template_dir = Path("pdf_templates_static/notext")

        # Erstelle finales PDF
        writer = PdfWriter()

        # Overlay-PDF laden
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))

        for page_num in range(1, 8):  # Seiten 1-7
            template_path = template_dir / f"nt_nt_{page_num:02d}.pdf"

            if template_path.exists():
                # Template-Seite laden
                template_reader = PdfReader(template_path)
                template_page = template_reader.pages[0]

                # Overlay-Seite laden (falls vorhanden)
                if page_num - 1 < len(overlay_reader.pages):
                    overlay_page = overlay_reader.pages[page_num - 1]

                    # WICHTIG: Erstelle eine echte Kopie der Template-Seite
                    from copy import deepcopy
                    merged_page = deepcopy(template_page)

                    # Overlay auf Kopie anwenden
                    merged_page.merge_page(overlay_page)

                    writer.add_page(merged_page)
                    print(f"✅ Seite {page_num} mit Overlay hinzugefügt")
                else:
                    writer.add_page(template_page)
                    print(f"✅ Seite {page_num} ohne Overlay hinzugefügt")
            else:
                print(f"⚠️ Template nicht gefunden: {template_path}")

        # PDF speichern
        output_path = "test_seite6_charts.pdf"
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        print(f"🎉 Test-PDF erstellt: {output_path}")
        print(f"📄 Anzahl Seiten: {len(writer.pages)}")

        # Dateigröße anzeigen
        file_size = os.path.getsize(output_path)
        print(f"📦 Dateigröße: {file_size:,} bytes")

        return True

    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Test-PDFs: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Hauptfunktion"""
    print("🚀 Seite 6 Charts Test startet...\n")

    # Prüfe ob benötigte Dateien existieren
    required_files = [
        "coords/seite6.yml",
        "pdf_templates_static/notext/nt_nt_06.pdf"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print("❌ Fehlende Dateien:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return

    # Erstelle Test-PDF
    success = create_test_pdf()

    if success:
        print("\n✅ Test erfolgreich abgeschlossen!")
        print("📋 Die Donut-Charts sollten jetzt auf Seite 6 sichtbar sein:")
        print("   - Oberer Chart: Speicher zu Tagesverbrauch (ca. 74%)")
        print("   - Unterer Chart: Speicher zu PV-Produktion (ca. 53%)")
        print("   - Beide Charts zeigen die Prozentwerte in der Mitte")
    else:
        print("\n❌ Test fehlgeschlagen!")


if __name__ == "__main__":
    main()
