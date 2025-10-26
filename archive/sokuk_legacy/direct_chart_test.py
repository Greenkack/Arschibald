#!/usr/bin/env python3
"""
Direkter Test - Erstelle ein PDF NUR mit Charts ohne Template-System
"""

import os
import sys
from pathlib import Path

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_direct_chart_pdf():
    """Erstelle ein PDF direkt mit ReportLab - ohne Template-System"""
    print("🎯 Erstelle PDF DIREKT mit ReportLab...")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        # Erstelle PDF direkt
        c = canvas.Canvas("direct_charts.pdf", pagesize=A4)
        page_width, page_height = A4

        print(f"📐 Seitengröße: {page_width} x {page_height}")

        # Zeichne Hintergrund
        c.setFillColorRGB(0.95, 0.95, 0.95)
        c.rect(0, 0, page_width, page_height, stroke=0, fill=1)

        # Zeichne Titel
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, page_height - 50, "SEITE 6 CHARTS TEST")

        # Chart-Positionen
        left_cx = 200.0
        right_cx = 400.0
        chart_cy = page_height / 2.0
        outer_r = 50.0
        inner_r = 30.0

        print(
            f"🎨 Zeichne Charts bei ({left_cx}, {chart_cy}) und ({right_cx}, {chart_cy})")

        # Linker Chart - Blau
        print("🔵 Zeichne blauen Chart...")

        # Äußerer Kreis (Hintergrund)
        c.setFillColorRGB(0.8, 0.8, 0.8)
        c.circle(left_cx, chart_cy, outer_r, stroke=0, fill=1)

        # Innerer Kreis (74% Anteil)
        c.setFillColorRGB(0, 0, 1)  # Reines Blau
        extent = -360.0 * (74.0 / 100.0)
        c.wedge(left_cx - outer_r, chart_cy - outer_r,
                left_cx + outer_r, chart_cy + outer_r,
                90, extent, stroke=0, fill=1)

        # Loch in der Mitte
        c.setFillColorRGB(1, 1, 1)
        c.circle(left_cx, chart_cy, inner_r, stroke=0, fill=1)

        # Text in der Mitte
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(left_cx - 15, chart_cy - 8, "74%")

        # Label unter dem Chart
        c.setFont("Helvetica", 12)
        c.drawString(left_cx - 40, chart_cy - outer_r - 20, "Tagesverbrauch")

        # Rechter Chart - Rot
        print("🔴 Zeichne roten Chart...")

        # Äußerer Kreis (Hintergrund)
        c.setFillColorRGB(0.8, 0.8, 0.8)
        c.circle(right_cx, chart_cy, outer_r, stroke=0, fill=1)

        # Innerer Kreis (53% Anteil)
        c.setFillColorRGB(1, 0, 0)  # Reines Rot
        extent = -360.0 * (53.0 / 100.0)
        c.wedge(right_cx - outer_r, chart_cy - outer_r,
                right_cx + outer_r, chart_cy + outer_r,
                90, extent, stroke=0, fill=1)

        # Loch in der Mitte
        c.setFillColorRGB(1, 1, 1)
        c.circle(right_cx, chart_cy, inner_r, stroke=0, fill=1)

        # Text in der Mitte
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(right_cx - 15, chart_cy - 8, "53%")

        # Label unter dem Chart
        c.setFont("Helvetica", 12)
        c.drawString(right_cx - 35, chart_cy - outer_r - 20, "PV-Produktion")

        # Zusätzliche Markierungen
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 14)
        c.drawString(
            50,
            100,
            "Wenn du diese Charts siehst, funktioniert ReportLab!")
        c.drawString(
            50,
            80,
            "Wenn nicht, liegt das Problem bei ReportLab oder PDF-Viewer")

        # Zeichne Rahmen um Charts
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(2)
        c.rect(left_cx - outer_r - 10, chart_cy - outer_r - 10,
               (outer_r + 10) * 2, (outer_r + 10) * 2, stroke=1, fill=0)
        c.rect(right_cx - outer_r - 10, chart_cy - outer_r - 10,
               (outer_r + 10) * 2, (outer_r + 10) * 2, stroke=1, fill=0)

        c.showPage()
        c.save()

        print("✅ Direktes PDF erstellt: direct_charts.pdf")

        # Dateigröße prüfen
        file_size = os.path.getsize("direct_charts.pdf")
        print(f"📦 Dateigröße: {file_size:,} bytes")

        return True

    except Exception as e:
        print(f"❌ Fehler beim direkten PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_pdf_content():
    """Teste ob das Template-PDF überhaupt Inhalt hat"""
    print("\n🔍 Teste Template-PDF Inhalt...")

    try:
        template_path = Path("pdf_templates_static/notext/nt_nt_06.pdf")
        if not template_path.exists():
            print(f"❌ Template nicht gefunden: {template_path}")
            return False

        from pypdf import PdfReader
        reader = PdfReader(template_path)

        print(f"📄 Template hat {len(reader.pages)} Seiten")

        if len(reader.pages) > 0:
            page = reader.pages[0]

            # Versuche Text zu extrahieren
            try:
                text = page.extract_text()
                print(
                    f"📝 Template-Text: '{text[:100]}...' ({len(text)} Zeichen)")
            except BaseException:
                print("⚠️ Kein Text im Template extrahierbar")

            # Überprüfe MediaBox
            if hasattr(page, 'mediabox'):
                print(f"📐 Template-Größe: {page.mediabox}")

            # Überprüfe Contents
            if hasattr(page, 'get_contents'):
                contents = page.get_contents()
                if contents:
                    print(f"📋 Template hat Inhalt: {type(contents)}")
                else:
                    print("❌ Template hat keinen Inhalt!")

        return True

    except Exception as e:
        print(f"❌ Fehler beim Template-Test: {e}")
        return False


def test_overlay_only():
    """Teste das Overlay alleine ohne Template"""
    print("\n🎨 Teste Overlay alleine...")

    try:
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

        # Generiere Overlay
        coords_dir = Path("coords")
        dynamic_data = build_dynamic_data(
            test_project_data, test_analysis_results, {})

        print(
            f"📊 Daten: Verbrauch={
                dynamic_data.get('storage_consumption_ratio_percent')}%, Produktion={
                dynamic_data.get('storage_production_ratio_percent')}%")

        overlay_bytes = generate_overlay(
            coords_dir, dynamic_data, total_pages=7)

        # Speichere nur das Overlay
        with open("overlay_only.pdf", "wb") as f:
            f.write(overlay_bytes)

        print(
            f"✅ Overlay-PDF erstellt: overlay_only.pdf ({len(overlay_bytes)} bytes)")

        # Analysiere Seite 6 des Overlays
        from pypdf import PdfReader
        reader = PdfReader("overlay_only.pdf")

        if len(reader.pages) >= 6:
            page6 = reader.pages[5]  # Index 5 = Seite 6

            try:
                text = page6.extract_text()
                print(f"📝 Overlay Seite 6 Text: '{text}'")

                # Suche nach Chart-Indikatoren
                if "74%" in text and "53%" in text:
                    print("✅ Chart-Werte im Overlay gefunden!")
                else:
                    print("❌ Chart-Werte NICHT im Overlay gefunden!")

            except Exception as e:
                print(f"⚠️ Text-Extraktion fehlgeschlagen: {e}")

        return True

    except Exception as e:
        print(f"❌ Fehler beim Overlay-Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Hauptfunktion"""
    print("🚀 DIREKTER CHART TEST")
    print("=" * 50)

    tests = [
        ("Direktes ReportLab PDF", create_direct_chart_pdf),
        ("Template-PDF Inhalt", test_template_pdf_content),
        ("Overlay alleine", test_overlay_only)
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
    print("ANWEISUNGEN")
    print('=' * 50)
    print("1. Öffne 'direct_charts.pdf' - wenn du Charts siehst, funktioniert ReportLab")
    print("2. Öffne 'overlay_only.pdf' - Seite 6 sollte Charts haben")
    print("3. Vergleiche mit 'test_seite6_charts.pdf' - Seite 6")


if __name__ == "__main__":
    main()
