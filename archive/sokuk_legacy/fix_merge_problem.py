#!/usr/bin/env python3
"""
Behebt das Merge-Problem zwischen Template und Overlay
"""

import io
import os
import sys
from pathlib import Path

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_simple_merge():
    """Teste einen einfachen Merge zwischen Template und Overlay"""
    print("🔄 Teste einfachen Merge...")

    try:
        from pypdf import PdfReader, PdfWriter

        # Lade Template
        template_path = Path("pdf_templates_static/notext/nt_nt_06.pdf")
        if not template_path.exists():
            print(f"❌ Template nicht gefunden: {template_path}")
            return False

        # Lade Overlay
        overlay_path = Path("overlay_only.pdf")
        if not overlay_path.exists():
            print(f"❌ Overlay nicht gefunden: {overlay_path}")
            return False

        template_reader = PdfReader(template_path)
        overlay_reader = PdfReader(overlay_path)

        print(f"📄 Template: {len(template_reader.pages)} Seiten")
        print(f"🎨 Overlay: {len(overlay_reader.pages)} Seiten")

        # Hole Seiten
        template_page = template_reader.pages[0]
        overlay_page6 = overlay_reader.pages[5]  # Seite 6 des Overlays

        print("🔄 Führe Merge durch...")

        # Erstelle eine Kopie der Template-Seite
        merged_page = template_page

        # Merge das Overlay
        merged_page.merge_page(overlay_page6)

        # Erstelle neues PDF
        writer = PdfWriter()
        writer.add_page(merged_page)

        # Speichere
        with open("simple_merge_test.pdf", "wb") as f:
            writer.write(f)

        print("✅ Einfacher Merge erstellt: simple_merge_test.pdf")

        # Teste das Ergebnis
        test_reader = PdfReader("simple_merge_test.pdf")
        test_page = test_reader.pages[0]

        try:
            text = test_page.extract_text()
            print(f"📝 Merge-Ergebnis Text: {len(text)} Zeichen")

            if "74%" in text and "53%" in text:
                print("✅ Charts im Merge-Ergebnis gefunden!")
                return True
            print("❌ Charts NICHT im Merge-Ergebnis!")
            return False

        except Exception as e:
            print(f"⚠️ Text-Extraktion fehlgeschlagen: {e}")
            return False

    except Exception as e:
        print(f"❌ Fehler beim Merge-Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_working_seite6():
    """Erstelle eine funktionierende Seite 6 mit Template + Overlay"""
    print("\n🎯 Erstelle funktionierende Seite 6...")

    try:
        from pypdf import PdfReader, PdfWriter

        from pdf_template_engine.dynamic_overlay import generate_overlay
        from pdf_template_engine.placeholders import build_dynamic_data

        # Test-Daten
        test_project_data = {
            "project_details": {
                "annual_consumption_kwh": 6000,
                "storage_capacity_kwh": 12.09
            }
        }

        test_analysis_results = {
            "annual_yield_kwh": 8251.92,
            "storage_capacity_kwh": 12.09
        }

        # Generiere frisches Overlay
        coords_dir = Path("coords")
        dynamic_data = build_dynamic_data(
            test_project_data, test_analysis_results, {})

        print(
            f"📊 Daten: Verbrauch={
                dynamic_data.get('storage_consumption_ratio_percent')}%, Produktion={
                dynamic_data.get('storage_production_ratio_percent')}%")

        overlay_bytes = generate_overlay(
            coords_dir, dynamic_data, total_pages=7)
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))

        # Lade Template
        template_path = Path("pdf_templates_static/notext/nt_nt_06.pdf")
        template_reader = PdfReader(template_path)

        # Erstelle finales PDF
        writer = PdfWriter()

        # Merge Template + Overlay für Seite 6
        template_page = template_reader.pages[0]
        overlay_page6 = overlay_reader.pages[5]  # Seite 6

        print("🔄 Merge Template + Overlay...")

        # WICHTIG: Erstelle eine echte Kopie der Template-Seite
        from copy import deepcopy
        merged_page = deepcopy(template_page)

        # Merge Overlay
        merged_page.merge_page(overlay_page6)

        writer.add_page(merged_page)

        # Speichere
        with open("working_seite6.pdf", "wb") as f:
            writer.write(f)

        print("✅ Funktionierende Seite 6 erstellt: working_seite6.pdf")

        # Verifikation
        verify_reader = PdfReader("working_seite6.pdf")
        verify_page = verify_reader.pages[0]

        try:
            text = verify_page.extract_text()
            print(f"📝 Verifikation: {len(text)} Zeichen")

            chart_indicators = [
                "74%",
                "53%",
                "Tagesverbrauch",
                "PV-Produktion"]
            found = [ind for ind in chart_indicators if ind in text]

            if len(found) >= 3:
                print(f"✅ Charts erfolgreich: {found}")
                return True
            print(f"❌ Charts fehlen: nur {found} gefunden")
            return False

        except Exception as e:
            print(f"⚠️ Verifikation fehlgeschlagen: {e}")
            return False

    except Exception as e:
        print(f"❌ Fehler bei Seite 6 Erstellung: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_complete_pdf_with_charts():
    """Erstelle ein komplettes 7-Seiten PDF mit funktionierenden Charts"""
    print("\n🎯 Erstelle komplettes PDF mit Charts...")

    try:
        from pypdf import PdfReader, PdfWriter

        from pdf_template_engine.dynamic_overlay import generate_overlay
        from pdf_template_engine.placeholders import build_dynamic_data

        # Test-Daten
        test_project_data = {
            "customer_data": {
                "first_name": "Max",
                "last_name": "Mustermann"
            },
            "project_details": {
                "annual_consumption_kwh": 6000,
                "storage_capacity_kwh": 12.09
            }
        }

        test_analysis_results = {
            "annual_yield_kwh": 8251.92,
            "storage_capacity_kwh": 12.09
        }

        # Generiere Overlay
        coords_dir = Path("coords")
        dynamic_data = build_dynamic_data(
            test_project_data, test_analysis_results, {})

        overlay_bytes = generate_overlay(
            coords_dir, dynamic_data, total_pages=7)
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))

        # Erstelle finales PDF
        writer = PdfWriter()
        template_dir = Path("pdf_templates_static/notext")

        for page_num in range(1, 8):  # Seiten 1-7
            template_path = template_dir / f"nt_nt_{page_num:02d}.pdf"

            if template_path.exists():
                template_reader = PdfReader(template_path)
                template_page = template_reader.pages[0]

                # Overlay hinzufügen (falls vorhanden)
                if page_num - 1 < len(overlay_reader.pages):
                    overlay_page = overlay_reader.pages[page_num - 1]

                    # Erstelle Kopie und merge
                    from copy import deepcopy
                    merged_page = deepcopy(template_page)
                    merged_page.merge_page(overlay_page)

                    writer.add_page(merged_page)
                    print(f"✅ Seite {page_num} mit Overlay hinzugefügt")
                else:
                    writer.add_page(template_page)
                    print(f"✅ Seite {page_num} ohne Overlay hinzugefügt")
            else:
                print(f"⚠️ Template für Seite {page_num} nicht gefunden")

        # Speichere komplettes PDF
        with open("complete_pdf_with_charts.pdf", "wb") as f:
            writer.write(f)

        print("✅ Komplettes PDF erstellt: complete_pdf_with_charts.pdf")

        # Verifikation von Seite 6
        complete_reader = PdfReader("complete_pdf_with_charts.pdf")
        if len(complete_reader.pages) >= 6:
            page6 = complete_reader.pages[5]  # Index 5 = Seite 6

            try:
                text = page6.extract_text()
                chart_indicators = [
                    "74%", "53%", "Tagesverbrauch", "PV-Produktion"]
                found = [ind for ind in chart_indicators if ind in text]

                print(f"📊 Seite 6 Verifikation: {found}")

                if len(found) >= 3:
                    print("✅ Charts in komplettem PDF erfolgreich!")
                    return True
                print("❌ Charts in komplettem PDF fehlen!")
                return False

            except Exception as e:
                print(f"⚠️ Seite 6 Verifikation fehlgeschlagen: {e}")
                return False

        return True

    except Exception as e:
        print(f"❌ Fehler bei komplettem PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Hauptfunktion"""
    print("🔧 MERGE-PROBLEM BEHEBUNG")
    print("=" * 50)

    tests = [
        ("Einfacher Merge", test_simple_merge),
        ("Funktionierende Seite 6", create_working_seite6),
        ("Komplettes PDF", create_complete_pdf_with_charts)
    ]

    for test_name, test_func in tests:
        print(f"\n{'=' * 50}")
        print(f"TEST: {test_name}")
        print('=' * 50)

        try:
            result = test_func()
            status = "✅ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n❌ {test_name} FEHLER: {e}")

    print(f"\n{'=' * 50}")
    print("ERGEBNISSE")
    print('=' * 50)
    print("📄 direct_charts.pdf - Reine ReportLab Charts")
    print("📄 overlay_only.pdf - Nur das Overlay (Seite 6 hat Charts)")
    print("📄 simple_merge_test.pdf - Einfacher Template+Overlay Merge")
    print("📄 working_seite6.pdf - Nur Seite 6 mit Charts")
    print("📄 complete_pdf_with_charts.pdf - Komplettes 7-Seiten PDF")
    print("\n🎯 Öffne 'complete_pdf_with_charts.pdf' und gehe zu Seite 6!")


if __name__ == "__main__":
    main()
