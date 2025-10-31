#!/usr/bin/env python3
"""
Test nur für das Wasserfall-Diagramm auf Seite 3
"""

import os
import sys
from pathlib import Path

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_waterfall_test():
    """Erstelle ein Test-PDF nur mit dem Wasserfall-Diagramm"""
    print("📊 Erstelle Wasserfall-Diagramm Test...")

    try:
        from reportlab.lib.colors import Color
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        # Erstelle PDF direkt
        c = canvas.Canvas("waterfall_test.pdf", pagesize=A4)
        page_width, page_height = A4

        print(f"📐 Seitengröße: {page_width} x {page_height}")

        # Zeichne Hintergrund
        c.setFillColorRGB(0.98, 0.98, 0.98)
        c.rect(0, 0, page_width, page_height, stroke=0, fill=1)

        # Titel
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, page_height - 50, "WASSERFALL-DIAGRAMM TEST")

        # Test-Werte (wie aus der Debug-Ausgabe)
        # Direkt, Einspeisung, Steuer, Gesamt
        values = [0.0, 561.96, 236.02, 797.98]
        labels = [
            "Direktverbrauch",
            "Einspeisevergütung",
            "Steuervorteile",
            "Gesamt"]

        # Chart-Position (basierend auf deinen Angaben)
        # Linker Rand: "Neigung des Daches" Position (ca. X=300)
        # Rechter Rand: "Art" Position (ca. X=547)
        # Oben: 10 Punkte oberhalb "Direkt" (Y ca. 516 - 10 = 506)
        # Unten: 10 Punkte oberhalb "Berechnungsgrundlagen" (Y ca. 645 - 10 =
        # 635)

        chart_left = 300.0
        chart_right = 547.0
        chart_top = page_height - 506.0 + 10  # +10 für oberhalb
        chart_bottom = page_height - 635.0 + 10  # +10 für oberhalb

        chart_width = chart_right - chart_left
        chart_height = chart_top - chart_bottom

        print(
            f"📊 Chart-Bereich: Links={chart_left}, Rechts={chart_right}, Oben={chart_top}, Unten={chart_bottom}")
        print(f"📏 Chart-Größe: Breite={chart_width}, Höhe={chart_height}")

        # Zeichne Chart-Rahmen zur Orientierung
        c.setStrokeColorRGB(1, 0, 0)  # Roter Rahmen
        c.setLineWidth(2)
        c.rect(
            chart_left,
            chart_bottom,
            chart_width,
            chart_height,
            stroke=1,
            fill=0)

        # Wasserfall-Balken zeichnen
        max_value = max(values)
        if max_value <= 0:
            max_value = 1000

        # Balken-Parameter
        num_bars = len([v for v in values if v > 0])  # Nur positive Werte
        bar_spacing = chart_width / (num_bars + 1)
        bar_width = bar_spacing * 0.6

        # Farbe: Blau wie in der PDF
        bar_color = Color(0.07, 0.34, 0.60)  # PDF-Blau
        text_color = Color(0.0, 0.0, 0.0)    # Schwarz für Text

        bar_index = 0
        for i, (value, label) in enumerate(zip(values, labels, strict=False)):
            if value <= 0:
                continue  # Überspringe 0-Werte

            bar_index += 1

            # Balken-Position
            bar_x = chart_left + bar_index * bar_spacing - bar_width / 2
            bar_height = (value / max_value) * chart_height * \
                0.7  # 70% der Höhe nutzen
            bar_y = chart_bottom + (chart_height - bar_height) / 2

            print(
                f"📊 Balken {bar_index} ({label}): X={
                    bar_x:.1f}, Y={
                    bar_y:.1f}, Breite={
                    bar_width:.1f}, Höhe={
                    bar_height:.1f}, Wert={value}€")

            # Zeichne Balken
            c.setFillColor(bar_color)
            c.rect(bar_x, bar_y, bar_width, bar_height, stroke=0, fill=1)

            # Wert über dem Balken
            c.setFillColor(text_color)
            c.setFont("Helvetica-Bold", 10)
            value_text = f"{value:,.0f} €".replace(',', '.')
            text_width = c.stringWidth(value_text, "Helvetica-Bold", 10)
            c.drawString(bar_x + (bar_width - text_width) / 2,
                         bar_y + bar_height + 5, value_text)

            # Label unter dem Balken (mehrzeilig wenn nötig)
            c.setFont("Helvetica", 8)
            if len(label) > 12:  # Lange Labels umbrechen
                words = label.split()
                line1 = " ".join(words[:2])
                line2 = " ".join(words[2:]) if len(words) > 2 else ""

                line1_width = c.stringWidth(line1, "Helvetica", 8)
                c.drawString(bar_x + (bar_width - line1_width) /
                             2, bar_y - 20, line1)

                if line2:
                    line2_width = c.stringWidth(line2, "Helvetica", 8)
                    c.drawString(
                        bar_x + (bar_width - line2_width) / 2, bar_y - 30, line2)
            else:
                label_width = c.stringWidth(label, "Helvetica", 8)
                c.drawString(bar_x + (bar_width - label_width) /
                             2, bar_y - 20, label)

        # Zusätzliche Markierungen
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 12)
        c.drawString(
            50, 200, f"Test-Werte: Einspeisung={
                values[1]}€, Steuer={
                values[2]}€, Gesamt={
                values[3]}€")
        c.drawString(
            50,
            180,
            f"Chart-Position: X={chart_left}-{chart_right}, Y={chart_bottom}-{chart_top}")

        c.showPage()
        c.save()

        print("✅ Wasserfall-Test PDF erstellt: waterfall_test.pdf")
        return True

    except Exception as e:
        print(f"❌ Fehler beim Wasserfall-Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_real_system():
    """Teste mit dem echten System"""
    print("\n🎯 Teste mit echtem System...")

    try:
        import io

        from pypdf import PdfReader, PdfWriter

        from pdf_template_engine.dynamic_overlay import generate_overlay
        from pdf_template_engine.placeholders import build_dynamic_data

        # Test-Daten mit realistischen Werten
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

        test_company_info = {
            "name": "TommaTech GmbH"
        }

        # Generiere dynamische Daten
        coords_dir = Path("coords")
        dynamic_data = build_dynamic_data(
            test_project_data,
            test_analysis_results,
            test_company_info)

        # Prüfe die Wasserfall-Werte
        print("📊 Wasserfall-Werte:")
        print(
            f"  Direktverbrauch: {
                dynamic_data.get(
                    'self_consumption_without_battery_eur',
                    '0')}€")
        print(
            f"  Einspeisevergütung: {
                dynamic_data.get(
                    'annual_feed_in_revenue_eur',
                    '0')}€")
        print(
            f"  Steuervorteile: {
                dynamic_data.get(
                    'tax_benefits_eur',
                    '0')}€")
        print(
            f"  Gesamt: {
                dynamic_data.get(
                    'total_annual_savings_eur',
                    '0')}€")

        # Generiere nur Seite 3 Overlay
        overlay_bytes = generate_overlay(
            coords_dir, dynamic_data, total_pages=7)

        # Extrahiere nur Seite 3
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
        if len(overlay_reader.pages) >= 3:
            page3_overlay = overlay_reader.pages[2]  # Index 2 = Seite 3

            # Lade Template für Seite 3
            template_path = Path("pdf_templates_static/notext/nt_nt_03.pdf")
            if template_path.exists():
                template_reader = PdfReader(template_path)
                template_page = template_reader.pages[0]

                # Merge
                from copy import deepcopy
                merged_page = deepcopy(template_page)
                merged_page.merge_page(page3_overlay)

                # Speichere nur Seite 3
                writer = PdfWriter()
                writer.add_page(merged_page)

                with open("seite3_waterfall_test.pdf", "wb") as f:
                    writer.write(f)

                print("✅ Seite 3 Wasserfall-Test erstellt: seite3_waterfall_test.pdf")

                # Analysiere das Ergebnis
                test_reader = PdfReader("seite3_waterfall_test.pdf")
                test_page = test_reader.pages[0]

                try:
                    text = test_page.extract_text()
                    waterfall_indicators = [
                        "561", "236", "797", "Direktverbrauch", "Einspeisevergütung"]
                    found = [
                        ind for ind in waterfall_indicators if ind in text]
                    print(f"🔍 Gefundene Wasserfall-Indikatoren: {found}")

                    if len(found) >= 3:
                        print("✅ Wasserfall-Diagramm im PDF gefunden!")
                        return True
                    print("❌ Wasserfall-Diagramm nicht im PDF gefunden!")
                    return False

                except Exception as e:
                    print(f"⚠️ Text-Extraktion fehlgeschlagen: {e}")
                    return False
            else:
                print(f"❌ Template nicht gefunden: {template_path}")
                return False
        else:
            print("❌ Nicht genügend Overlay-Seiten")
            return False

    except Exception as e:
        print(f"❌ Fehler beim System-Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Hauptfunktion"""
    print("🚀 WASSERFALL-DIAGRAMM TEST")
    print("=" * 50)

    tests = [
        ("Direktes Wasserfall-PDF", create_waterfall_test),
        ("Echtes System Test", test_with_real_system)
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
    print("📄 waterfall_test.pdf - Direktes Wasserfall-Diagramm")
    print("📄 seite3_waterfall_test.pdf - Seite 3 mit Wasserfall-Diagramm")
    print("\n🎯 Öffne beide PDFs um die Diagramme zu sehen!")


if __name__ == "__main__":
    main()
