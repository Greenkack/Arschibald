#!/usr/bin/env python3
"""
Einfacher Test des Wasserfall-Diagramms mit direkter Overlay-Generierung
"""

from pdf_template_engine.dynamic_overlay import generate_overlay
from pypdf import PdfReader, PdfWriter
import io
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_wasserfall_overlay():
    """Testet das Wasserfall-Diagramm durch direkte Overlay-Generierung"""

    print("🔧 Test des Wasserfall-Diagramms mit Overlay")
    print("=" * 45)

    # Test-Daten für das Wasserfall-Diagramm
    dynamic_data = {
        # Wasserfall-Diagramm Daten (verschiedene Keys für Robustheit)
        "einsparung_direktverbrauch_eur": "1450.75",
        "einnahmen_einspeisung_eur": "920.50",
        "vorteile_steuerfrei_eur": "380.25",
        "gesamt_ertraege_jahr_eur": "2751.50",

        # Alternative Keys
        "self_consumption_without_battery_eur": "1450.75",
        "annual_feed_in_revenue_eur": "920.50",
        "tax_benefits_eur": "380.25",
        "total_annual_savings_eur": "2751.50",

        # Weitere Keys für andere Seiten
        "company_name": "TommaTech GmbH",
        "customer_name": "Max Mustermann",
        "page_number": "3",
        "total_pages": "7",
        "storage_consumption_ratio_percent": "74",
        "storage_production_ratio_percent": "53"
    }

    try:
        # Generiere Overlay
        print("📄 Generiere Overlay mit Wasserfall-Diagramm...")

        coords_dir = Path("coords")
        if not coords_dir.exists():
            print(f"❌ Koordinaten-Verzeichnis nicht gefunden: {coords_dir}")
            return False

        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=dynamic_data,
            total_pages=7
        )

        if overlay_bytes:
            # Speichere Overlay als PDF
            output_file = "test_wasserfall_overlay.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(f"✅ Overlay-PDF erfolgreich erstellt: {output_file}")
            print(f"📦 Dateigröße: {len(overlay_bytes):,} bytes")
            print("📋 Das Wasserfall-Diagramm sollte auf Seite 3 sichtbar sein")
            print("📊 Daten:")
            print(
                f"   - Direktverbrauch: {dynamic_data['einsparung_direktverbrauch_eur']}€")
            print(
                f"   - Einspeisevergütung: {dynamic_data['einnahmen_einspeisung_eur']}€")
            print(
                f"   - Steuervorteile: {dynamic_data['vorteile_steuerfrei_eur']}€")
            print(f"   - Gesamt: {dynamic_data['gesamt_ertraege_jahr_eur']}€")

            # Zusätzlich: Prüfe PDF-Struktur
            try:
                reader = PdfReader(io.BytesIO(overlay_bytes))
                print(f"📄 PDF-Info: {len(reader.pages)} Seiten")

                # Prüfe Seite 3 (Index 2)
                if len(reader.pages) >= 3:
                    page3 = reader.pages[2]
                    print(f"📍 Seite 3 Größe: {page3.mediabox}")

            except Exception as e:
                print(f"⚠️ PDF-Struktur-Prüfung fehlgeschlagen: {e}")

            return True
        print("❌ Overlay-Generierung fehlgeschlagen - keine Bytes erhalten")
        return False

    except Exception as e:
        print(f"❌ Fehler bei der Overlay-Generierung: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wasserfall_with_template():
    """Testet das Wasserfall-Diagramm mit Template-Hintergrund"""

    print("\n🔧 Test mit Template-Hintergrund")
    print("=" * 35)

    # Prüfe ob Template-Dateien existieren
    template_dir = Path("pdf_templates_static/notext")
    template_files = [
        "nt_nt_01.pdf", "nt_nt_02.pdf", "nt_nt_03.pdf",
        "nt_nt_04.pdf", "nt_nt_05.pdf", "nt_nt_06.pdf", "nt_nt_07.pdf"
    ]

    missing_templates = []
    for template_file in template_files:
        template_path = template_dir / template_file
        if not template_path.exists():
            missing_templates.append(str(template_path))

    if missing_templates:
        print("⚠️ Template-Dateien fehlen:")
        for missing in missing_templates:
            print(f"   - {missing}")
        print("📋 Test wird nur mit Overlay durchgeführt")
        return test_wasserfall_overlay()

    print("✅ Alle Template-Dateien gefunden")

    try:
        # Generiere Overlay
        coords_dir = Path("coords")
        dynamic_data = {
            "einsparung_direktverbrauch_eur": "1850.00",
            "einnahmen_einspeisung_eur": "1200.00",
            "vorteile_steuerfrei_eur": "450.00",
            "gesamt_ertraege_jahr_eur": "3500.00",
            "company_name": "TommaTech GmbH",
            "storage_consumption_ratio_percent": "74",
            "storage_production_ratio_percent": "53"
        }

        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=dynamic_data,
            total_pages=7
        )

        if not overlay_bytes:
            print("❌ Overlay-Generierung fehlgeschlagen")
            return False

        # Lade Template-PDFs und kombiniere mit Overlay
        print("📄 Kombiniere mit Template-Hintergründen...")

        writer = PdfWriter()
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))

        for i in range(7):
            template_path = template_dir / f"nt_nt_{i + 1:02d}.pdf"

            # Lade Template
            template_reader = PdfReader(template_path)
            template_page = template_reader.pages[0]

            # Lade Overlay-Seite
            if i < len(overlay_reader.pages):
                overlay_page = overlay_reader.pages[i]
                # Kombiniere Template mit Overlay
                template_page.merge_page(overlay_page)

            writer.add_page(template_page)

        # Speichere kombinierte PDF
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        combined_bytes = output_buffer.getvalue()

        output_file = "test_wasserfall_with_template.pdf"
        with open(output_file, "wb") as f:
            f.write(combined_bytes)

        print(f"✅ Kombinierte PDF erstellt: {output_file}")
        print(f"📦 Dateigröße: {len(combined_bytes):,} bytes")
        print(
            "📋 Das Wasserfall-Diagramm sollte auf Seite 3 über dem Template sichtbar sein")

        return True

    except Exception as e:
        print(f"❌ Fehler bei Template-Kombination: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Einfacher Test des Wasserfall-Diagramms")
    print("=" * 50)

    # Test 1: Nur Overlay
    success1 = test_wasserfall_overlay()

    # Test 2: Mit Template (falls verfügbar)
    success2 = test_wasserfall_with_template()

    if success1 or success2:
        print("\n🎉 Test erfolgreich abgeschlossen!")
        print("📋 Überprüfen Sie die generierten PDF-Dateien:")
        if success1:
            print("   - test_wasserfall_overlay.pdf (Nur Overlay)")
        if success2:
            print("   - test_wasserfall_with_template.pdf (Mit Template-Hintergrund)")
        print("📍 Das Wasserfall-Diagramm sollte auf Seite 3 sichtbar sein")
        print("📊 Position: Zwischen 'Neigung des Daches' und 'Art' Spalten")
    else:
        print("\n❌ Alle Tests fehlgeschlagen")
