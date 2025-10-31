#!/usr/bin/env python3
"""
Überprüft ob die Charts im PDF sichtbar sind
"""

import os
import sys
from pathlib import Path

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_pdf_content():
    """Überprüfe das erstellte PDF"""
    pdf_path = "test_seite6_charts.pdf"

    if not Path(pdf_path).exists():
        print(f"❌ PDF nicht gefunden: {pdf_path}")
        return False

    try:
        from pypdf import PdfReader

        reader = PdfReader(pdf_path)
        print(f"📄 PDF geladen: {len(reader.pages)} Seiten")

        # Seite 6 (Index 5) analysieren
        if len(reader.pages) >= 6:
            page6 = reader.pages[5]  # Index 5 = Seite 6

            # Extrahiere Text von Seite 6
            try:
                text_content = page6.extract_text()
                print(f"📝 Text auf Seite 6 gefunden: {len(text_content)} Zeichen")

                # Suche nach Speicher-bezogenen Begriffen
                storage_terms = ["Speicher", "Tagesverbrauch", "PV-Produktion", "74%", "53%"]
                found_terms = []
                for term in storage_terms:
                    if term in text_content:
                        found_terms.append(term)

                if found_terms:
                    print(f"✅ Gefundene Begriffe: {found_terms}")
                else:
                    print("⚠️ Keine Speicher-Begriffe im Text gefunden")

            except Exception as e:
                print(f"⚠️ Text-Extraktion fehlgeschlagen: {e}")

            # Überprüfe Seiteninhalt (Annotations, etc.)
            if hasattr(page6, 'annotations') and page6.annotations:
                print(f"📋 Annotationen gefunden: {len(page6.annotations)}")

            # Überprüfe MediaBox/CropBox
            if hasattr(page6, 'mediabox'):
                print(f"📐 Seitengröße: {page6.mediabox}")

            return True
        print(f"❌ PDF hat nur {len(reader.pages)} Seiten, Seite 6 nicht verfügbar")
        return False

    except Exception as e:
        print(f"❌ Fehler beim PDF-Lesen: {e}")
        return False

def create_simple_test():
    """Erstelle einen einfachen Test nur für Seite 6"""
    print("🎯 Erstelle vereinfachten Seite 6 Test...")

    try:
        import io

        from pypdf import PdfReader, PdfWriter

        from pdf_template_engine.placeholders import build_dynamic_data

        # Minimale Test-Daten
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

        # Generiere nur die dynamischen Daten
        dynamic_data = build_dynamic_data(test_project_data, test_analysis_results, {})

        print("🔍 Speicher-Werte:")
        print(f"  storage_consumption_ratio_percent: {dynamic_data.get('storage_consumption_ratio_percent')}")
        print(f"  storage_production_ratio_percent: {dynamic_data.get('storage_production_ratio_percent')}")

        # Generiere nur Seite 6 Overlay
        print("🎨 Generiere Overlay nur für Seite 6...")

        # Erstelle ein Mini-Overlay nur für Seite 6
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        page_width, page_height = A4

        # Zeichne die Charts direkt (OLD: page 6 -> NEW: page 7)
        from pdf_template_engine.dynamic_overlay import _draw_page7_storage_donuts
        _draw_page7_storage_donuts(c, dynamic_data, page_width, page_height)

        # Zeichne auch einen Test-Text
        c.setFont("Helvetica-Bold", 16)
        c.setFillColorRGB(1, 0, 0)  # Rot
        c.drawString(100, 700, "TEST: Seite 7 Charts (old page 6)")
        c.drawString(100, 680, f"Verbrauch: {dynamic_data.get('storage_consumption_ratio_percent')}%")
        c.drawString(100, 660, f"Produktion: {dynamic_data.get('storage_production_ratio_percent')}%")

        c.showPage()
        c.save()

        overlay_bytes = buffer.getvalue()
        print(f"✅ Overlay erstellt: {len(overlay_bytes)} bytes")

        # Lade Template für Seite 7 (OLD: page 6 -> NEW: page 7)
        template_path = Path("pdf_templates_static/notext/nt_nt_07.pdf")
        if not template_path.exists():
            print(f"❌ Template nicht gefunden: {template_path}")
            return False

        # Kombiniere Template + Overlay
        template_reader = PdfReader(template_path)
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))

        writer = PdfWriter()

        template_page = template_reader.pages[0]
        overlay_page = overlay_reader.pages[0]

        # Overlay auf Template anwenden
        template_page.merge_page(overlay_page)
        writer.add_page(template_page)

        # Speichere Test-PDF
        output_path = "seite6_only_test.pdf"
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        print(f"🎉 Seite 6 Test-PDF erstellt: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Fehler beim Seite 6 Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Hauptfunktion"""
    print("🔍 PDF Charts Verifikation startet...\n")

    # Überprüfe existierendes PDF
    print("=" * 50)
    print("1. Überprüfe existierendes PDF")
    print("=" * 50)
    verify_pdf_content()

    # Erstelle vereinfachten Test
    print("\n" + "=" * 50)
    print("2. Erstelle vereinfachten Seite 6 Test")
    print("=" * 50)
    create_simple_test()

if __name__ == "__main__":
    main()
