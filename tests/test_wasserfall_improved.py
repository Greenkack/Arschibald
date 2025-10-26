#!/usr/bin/env python3
"""
Test-Skript für das verbesserte Wasserfall-Diagramm auf Seite 3
"""

from pdf_template_engine.dynamic_overlay import _draw_page3_waterfall_chart
import io
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_waterfall_chart():
    """Testet das Wasserfall-Diagramm mit verschiedenen Datensätzen"""

    # Test-Daten
    test_datasets = [
        {
            "name": "Reale Berechnungswerte",
            "data": {
                "einsparung_direktverbrauch_eur": "1250.50",
                "einnahmen_einspeisung_eur": "850.75",
                "vorteile_steuerfrei_eur": "320.25",
                "gesamt_ertraege_jahr_eur": "2421.50"
            }
        },
        {
            "name": "Hohe Werte",
            "data": {
                "self_consumption_without_battery_eur": "2500",
                "annual_feed_in_revenue_eur": "1800",
                "tax_benefits_eur": "650",
                "total_annual_savings_eur": "4950"
            }
        },
        {
            "name": "Niedrige Werte",
            "data": {
                "direct_consumption_savings_eur": "450",
                "feed_in_revenue_eur": "280",
                "steuerliche_vorteile_eur": "120",
                "annual_total_benefits_eur": "850"
            }
        },
        {
            "name": "Keine Daten (Fallback)",
            "data": {}
        }
    ]

    page_width, page_height = A4

    for i, dataset in enumerate(test_datasets):
        print(f"\n=== Test {i + 1}: {dataset['name']} ===")

        # Erstelle PDF-Buffer
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        # Zeichne Hintergrund-Raster für bessere Orientierung
        c.setStrokeColorRGB(0.9, 0.9, 0.9)
        c.setLineWidth(0.5)

        # Vertikale Linien alle 50 Punkte
        for x in range(0, int(page_width), 50):
            c.line(x, 0, x, page_height)
            if x % 100 == 0:
                c.setFont("Helvetica", 6)
                c.drawString(x + 2, page_height - 15, str(x))

        # Horizontale Linien alle 50 Punkte
        for y in range(0, int(page_height), 50):
            c.line(0, y, page_width, y)
            if y % 100 == 0:
                c.setFont("Helvetica", 6)
                c.drawString(5, y + 2, str(y))

        # Markiere die Chart-Grenzen
        c.setStrokeColorRGB(1, 0, 0)  # Rot für Chart-Grenzen
        c.setLineWidth(2)

        # Koordinaten aus seite3.yml
        chart_left = 300.48
        chart_right = 547.50
        chart_top = page_height - (516.11 - 10)
        chart_bottom = page_height - (645.42 - 10)

        # Zeichne Chart-Rahmen
        c.rect(
            chart_left,
            chart_bottom,
            chart_right -
            chart_left,
            chart_top -
            chart_bottom,
            stroke=1,
            fill=0)

        # Beschriftung der Grenzen
        c.setFillColorRGB(1, 0, 0)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(chart_left - 5, chart_top + 5, f"Links: {chart_left}")
        c.drawString(chart_right - 50, chart_top + 5, f"Rechts: {chart_right}")
        c.drawString(
            chart_left - 5,
            chart_bottom - 15,
            f"Unten: {chart_bottom}")
        c.drawString(chart_left - 5, chart_top - 10, f"Oben: {chart_top}")

        # Zeichne das Wasserfall-Diagramm
        try:
            _draw_page3_waterfall_chart(
                c, dataset['data'], page_width, page_height)
            print("✓ Wasserfall-Diagramm erfolgreich gezeichnet")
        except Exception as e:
            print(f"✗ Fehler beim Zeichnen: {e}")
            import traceback
            traceback.print_exc()

        # Titel für den Test
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 14)
        title = f"Test {i + 1}: {dataset['name']}"
        c.drawString(50, page_height - 50, title)

        # Daten-Info
        c.setFont("Helvetica", 10)
        y_pos = page_height - 80
        for key, value in dataset['data'].items():
            c.drawString(50, y_pos, f"{key}: {value}")
            y_pos -= 15

        c.showPage()

    # Speichere PDF
    c.save()

    # Schreibe in Datei
    output_file = "test_wasserfall_improved.pdf"
    with open(output_file, "wb") as f:
        f.write(buffer.getvalue())

    print(f"\n✓ Test-PDF erstellt: {output_file}")
    print("Öffnen Sie die Datei, um die verschiedenen Wasserfall-Diagramme zu überprüfen.")


def test_coordinate_extraction():
    """Testet die Koordinaten-Extraktion aus seite3.yml"""

    print("\n=== Koordinaten-Test ===")

    # Lade seite3.yml und extrahiere relevante Koordinaten
    coords_file = Path("coords/seite3.yml")
    if not coords_file.exists():
        print(f"✗ Koordinaten-Datei nicht gefunden: {coords_file}")
        return

    print(f"✓ Koordinaten-Datei gefunden: {coords_file}")

    # Suche nach relevanten Platzhaltern
    relevant_placeholders = [
        "Neigung des Daches",
        "Art",
        "Direkt",
        "Berechnungsgrundlagen"
    ]

    found_coords = {}

    with open(coords_file, encoding='utf-8') as f:
        content = f.read()

        for placeholder in relevant_placeholders:
            if f"Text: {placeholder}" in content:
                # Finde die Position-Zeile nach dem Text
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip() == f"Text: {placeholder}":
                        # Suche nach Position in den nächsten Zeilen
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if lines[j].startswith("Position:"):
                                pos_line = lines[j]
                                print(f"✓ {placeholder}: {pos_line}")
                                found_coords[placeholder] = pos_line
                                break
                        break

    # Berechne Chart-Grenzen
    if found_coords:
        print("\n=== Berechnete Chart-Grenzen ===")

        # Extrahiere X-Koordinaten
        neigung_pos = found_coords.get("Neigung des Daches", "")
        art_pos = found_coords.get("Art", "")
        direkt_pos = found_coords.get("Direkt", "")
        berechnungsgrundlagen_pos = found_coords.get(
            "Berechnungsgrundlagen", "")

        import re

        def extract_coords(pos_str):
            nums = re.findall(r"[-+]?[0-9]*[\.,]?[0-9]+", pos_str)
            if len(nums) >= 4:
                return [float(n.replace(",", ".")) for n in nums[:4]]
            return None

        neigung_coords = extract_coords(neigung_pos)
        art_coords = extract_coords(art_pos)
        direkt_coords = extract_coords(direkt_pos)
        berechnungsgrundlagen_coords = extract_coords(
            berechnungsgrundlagen_pos)

        if neigung_coords and art_coords and direkt_coords and berechnungsgrundlagen_coords:
            chart_left = neigung_coords[0]  # X-Start von "Neigung des Daches"
            chart_right = art_coords[2]     # X-Ende von "Art"
            chart_top_y = direkt_coords[1] - 10  # Y von "Direkt" - 10
            # Y von "Berechnungsgrundlagen" - 10
            chart_bottom_y = berechnungsgrundlagen_coords[1] - 10

            print(f"Chart Links: {chart_left}")
            print(f"Chart Rechts: {chart_right}")
            print(f"Chart Oben (YAML-Y): {chart_top_y}")
            print(f"Chart Unten (YAML-Y): {chart_bottom_y}")
            print(f"Chart Breite: {chart_right - chart_left}")
            print(f"Chart Höhe (YAML): {chart_bottom_y - chart_top_y}")

            # Canvas-Koordinaten (Y ist invertiert)
            page_height = A4[1]
            canvas_top = page_height - chart_top_y
            canvas_bottom = page_height - chart_bottom_y

            print("\nCanvas-Koordinaten:")
            print(f"Chart Oben (Canvas-Y): {canvas_top}")
            print(f"Chart Unten (Canvas-Y): {canvas_bottom}")
            print(f"Chart Höhe (Canvas): {canvas_top - canvas_bottom}")


if __name__ == "__main__":
    print("🔧 Test des verbesserten Wasserfall-Diagramms")
    print("=" * 50)

    # Teste Koordinaten-Extraktion
    test_coordinate_extraction()

    # Teste Wasserfall-Diagramm
    test_waterfall_chart()

    print("\n✅ Alle Tests abgeschlossen!")
