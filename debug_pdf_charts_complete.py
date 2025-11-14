#!/usr/bin/env python3
"""
Vollständige Diagnose warum die Charts nicht im PDF erscheinen
"""

import io
import os
import sys
from pathlib import Path

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_donut_drawing_function():
    """Teste die _draw_donut Funktion direkt"""
    print("[TARGET] Teste _draw_donut Funktion direkt...")

    try:
        from reportlab.lib.colors import Color
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        from pdf_template_engine.dynamic_overlay import _draw_donut

        # Erstelle ein einfaches Test-PDF nur mit Donut
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        page_width, page_height = A4

        print(f"[DESIGN] Seitengröße: {page_width} x {page_height}")

        # Zeichne einen Test-Donut in der Mitte der Seite
        cx = page_width / 2
        cy = page_height / 2
        outer_r = 50.0
        inner_r = 30.0

        bg = Color(0.85, 0.88, 0.90)
        fg = Color(0.07, 0.34, 0.60)

        print(f"[DESIGN] Zeichne Test-Donut bei ({cx}, {cy})")

        # Zeichne Hintergrund-Rechteck zum Testen
        c.setFillColorRGB(1, 0, 0)  # Rot
        c.rect(cx - 60, cy - 60, 120, 120, stroke=0, fill=1)

        # Zeichne Donut
        _draw_donut(c, cx, cy, 75.0, outer_r, inner_r, fg, bg)

        # Zeichne Text
        c.setFont("Helvetica-Bold", 16)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(cx - 20, cy - 5, "75%")

        # Zeichne Beschriftung
        c.setFont("Helvetica", 12)
        c.drawString(cx - 30, cy - 80, "Test Donut")

        c.showPage()
        c.save()

        # Speichere Test-PDF
        test_bytes = buffer.getvalue()
        with open("test_donut_only.pdf", "wb") as f:
            f.write(test_bytes)

        print(f"[OK] Test-Donut PDF erstellt: test_donut_only.pdf ({len(test_bytes)} bytes)")
        return True

    except Exception as e:
        print(f"[ERROR] Fehler beim Donut-Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_page6_function_directly():
    """Teste die _draw_page7_storage_donuts Funktion direkt (OLD: page 6 -> NEW: page 7)"""
    print("\n[TARGET] Teste _draw_page7_storage_donuts direkt (old page 6)...")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        from pdf_template_engine.dynamic_overlay import _draw_page7_storage_donuts

        # Test-Daten
        dynamic_data = {
            'storage_consumption_ratio_percent': '74',
            'storage_production_ratio_percent': '53'
        }

        # Erstelle Test-PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        page_width, page_height = A4

        print(f"[CHART] Test-Daten: {dynamic_data}")

        # Zeichne Hintergrund-Markierungen
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(0, 0, page_width, page_height, stroke=0, fill=1)

        # Zeichne Koordinaten-Gitter
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setLineWidth(0.5)
        for x in range(0, int(page_width), 50):
            c.line(x, 0, x, page_height)
        for y in range(0, int(page_height), 50):
            c.line(0, y, page_width, y)

        # Zeichne die Seite 7 Charts (OLD: page 6 -> NEW: page 7)
        print("[DESIGN] Rufe _draw_page7_storage_donuts auf...")
        _draw_page7_storage_donuts(c, dynamic_data, page_width, page_height)

        # Zeichne zusätzliche Markierungen
        c.setFillColorRGB(1, 0, 0)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, page_height - 50, "TEST: Seite 7 Charts (old page 6)")
        c.drawString(50, page_height - 70, f"Data: {dynamic_data}")

        c.showPage()
        c.save()

        # Speichere Test-PDF
        test_bytes = buffer.getvalue()
        with open("test_page6_function.pdf", "wb") as f:
            f.write(test_bytes)

        print(f"[OK] Page6-Funktion PDF erstellt: test_page6_function.pdf ({len(test_bytes)} bytes)")
        return True

    except Exception as e:
        print(f"[ERROR] Fehler beim Page6-Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_overlay_generation():
    """Teste die komplette Overlay-Generierung"""
    print("\n[TARGET] Teste komplette Overlay-Generierung...")

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

        # Generiere dynamische Daten
        coords_dir = Path("coords")
        dynamic_data = build_dynamic_data(test_project_data, test_analysis_results, {})

        print("[CHART] Generierte Daten:")
        print(f"  storage_consumption_ratio_percent: {dynamic_data.get('storage_consumption_ratio_percent')}")
        print(f"  storage_production_ratio_percent: {dynamic_data.get('storage_production_ratio_percent')}")

        # Generiere Overlay
        print("[DESIGN] Generiere Overlay...")
        overlay_bytes = generate_overlay(coords_dir, dynamic_data, total_pages=8)  # MIGRATION: Changed from 7 to 8

        print(f"[OK] Overlay generiert: {len(overlay_bytes)} bytes")

        # Speichere Overlay als separates PDF
        with open("test_overlay_only.pdf", "wb") as f:
            f.write(overlay_bytes)

        print("[OK] Overlay-PDF gespeichert: test_overlay_only.pdf")

        # Analysiere Seite 6 des Overlays
        from pypdf import PdfReader
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))

        if len(overlay_reader.pages) >= 6:
            page6_overlay = overlay_reader.pages[5]  # Index 5 = Seite 6

            # Versuche Text zu extrahieren
            try:
                text = page6_overlay.extract_text()
                print(f"[NOTE] Overlay Seite 6 Text: '{text}'")
            except:
                print("[WARNING] Kein Text im Overlay extrahierbar")

            # Überprüfe Seiteninhalt
            if hasattr(page6_overlay, 'get_contents'):
                contents = page6_overlay.get_contents()
                if contents:
                    print(f"📋 Overlay Seite 6 hat Inhalt: {type(contents)}")
                else:
                    print("[ERROR] Overlay Seite 6 hat keinen Inhalt!")

        return True

    except Exception as e:
        print(f"[ERROR] Fehler bei Overlay-Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_merge():
    """Teste das Zusammenführen von Template und Overlay"""
    print("\n[TARGET] Teste Template + Overlay Merge...")

    try:
        from pypdf import PdfReader, PdfWriter

        # Lade Template (OLD: page 6 -> NEW: page 7)
        template_path = Path("pdf_templates_static/notext/nt_nt_07.pdf")
        if not template_path.exists():
            print(f"[ERROR] Template nicht gefunden: {template_path}")
            return False

        template_reader = PdfReader(template_path)
        print(f"[FILE] Template geladen: {len(template_reader.pages)} Seiten")

        # Lade Overlay
        overlay_path = Path("test_overlay_only.pdf")
        if not overlay_path.exists():
            print(f"[ERROR] Overlay nicht gefunden: {overlay_path}")
            return False

        overlay_reader = PdfReader(overlay_path)
        print(f"[DESIGN] Overlay geladen: {len(overlay_reader.pages)} Seiten")

        # Merge Seite 6
        if len(template_reader.pages) > 0 and len(overlay_reader.pages) >= 6:
            template_page = template_reader.pages[0]
            overlay_page = overlay_reader.pages[5]  # Seite 6 des Overlays

            print("🔄 Führe Template + Overlay zusammen...")

            # Erstelle Kopie der Template-Seite
            merged_page = template_page

            # Merge Overlay
            merged_page.merge_page(overlay_page)

            # Speichere Ergebnis
            writer = PdfWriter()
            writer.add_page(merged_page)

            with open("test_merged_page6.pdf", "wb") as f:
                writer.write(f)

            print("[OK] Merged PDF erstellt: test_merged_page6.pdf")

            # Analysiere das Ergebnis
            merged_reader = PdfReader("test_merged_page6.pdf")
            merged_page_content = merged_reader.pages[0]

            try:
                merged_text = merged_page_content.extract_text()
                print(f"[NOTE] Merged Text: {len(merged_text)} Zeichen")

                # Suche nach Chart-Indikatoren
                chart_indicators = ["74%", "53%", "Tagesverbrauch", "PV-Produktion"]
                found = [ind for ind in chart_indicators if ind in merged_text]
                print(f"[SEARCH] Gefundene Chart-Indikatoren: {found}")

            except Exception as e:
                print(f"[WARNING] Text-Extraktion fehlgeschlagen: {e}")

            return True
        print("[ERROR] Nicht genügend Seiten für Merge")
        return False

    except Exception as e:
        print(f"[ERROR] Fehler beim Merge-Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Hauptfunktion für vollständige Diagnose"""
    print("[SEARCH] VOLLSTÄNDIGE PDF CHARTS DIAGNOSE")
    print("=" * 60)

    tests = [
        ("Donut-Zeichnung", test_donut_drawing_function),
        ("Page6-Funktion", test_page6_function_directly),
        ("Overlay-Generierung", test_overlay_generation),
        ("Template-Merge", test_template_merge)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print('='*60)

        try:
            result = test_func()
            results.append((test_name, result))
            status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n[ERROR] {test_name} FEHLER: {e}")
            results.append((test_name, False))

    # Zusammenfassung
    print(f"\n{'='*60}")
    print("DIAGNOSE ZUSAMMENFASSUNG")
    print('='*60)

    for test_name, result in results:
        status = "[OK]" if result else "[ERROR]"
        print(f"{status} {test_name}")

    passed = sum(1 for _, result in results if result)
    print(f"\nErgebnis: {passed}/{len(results)} Tests bestanden")

    if passed < len(results):
        print("\n[TOOL] NÄCHSTE SCHRITTE:")
        print("1. Überprüfe die erstellten Test-PDFs")
        print("2. Identifiziere wo der Fehler auftritt")
        print("3. Behebe das spezifische Problem")

if __name__ == "__main__":
    main()
