"""
pdf_template_engine/dynamic_overlay.py

Erzeugt Text-Overlays für sieben statische Template-Seiten anhand von Koordinaten
aus coords/seite1.yml … seite7.yml und verschmilzt sie mit den Dateien
pdf_templates_static/notext/nt_nt_01.pdf … nt_nt_07.pdf.
"""

from __future__ import annotations

import base64
import io
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib import colors  # für add_page3_elements (colors.black)
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

try:
    # PageObject ist optional (ältere pypdf-Versionen können es anders
    # exportieren)
    from pypdf import PageObject  # type: ignore
except Exception:  # pragma: no cover
    PageObject = None  # type: ignore

from .placeholders import PLACEHOLDER_MAPPING

# Optional: Admin-Settings laden, um Overlay-Verhalten dynamisch zu steuern
try:
    from database import load_admin_setting  # type: ignore
except Exception:  # Fallback, wenn DB nicht verfügbar ist (z. B. Tests)
    def load_admin_setting(key: str, default=None):  # type: ignore
        return default


def _to_bool(val: Any, default: bool = False) -> bool:
    try:
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return bool(val)
        if isinstance(val, str):
            return val.strip().lower() in {"1", "true", "yes", "on"}
    except Exception:
        pass
    return default


def _as_image_reader(val: Any) -> Any:
    """Erzeugt einen ImageReader aus Base64, Data-URL oder lokalem Dateipfad.
    Gibt None zurück, wenn nicht lesbar."""
    try:
        if not val:
            return None
        s = str(val).strip()

        # Data-URL -> Base64 extrahieren
        if ";base64," in s:
            s = s.split(";base64,", 1)[1]

        # Versuche Base64-Decode
        try:
            raw = base64.b64decode(s)

            # Prüfe Bildformat - nur PNG/JPEG unterstützt
            if raw.startswith(b'<?xml') or raw.startswith(b'<svg'):
                return None  # SVG nicht unterstützt

            return ImageReader(io.BytesIO(raw))
        except Exception:
            pass

        # Falls Dateipfad existiert, Datei laden
        try:
            p = Path(s)
            if p.exists() and p.is_file():
                with p.open("rb") as f:
                    data = f.read()
                return ImageReader(io.BytesIO(data))
        except Exception:
            pass

        return None
    except Exception:
        return None


def _draw_global_watermark(
        c: canvas.Canvas,
        page_width: float,
        page_height: float) -> None:
    """Zeichnet optional ein globales Wasserzeichen (aus Admin-Settings) diagonal über die Seite."""
    enabled = _to_bool(
        load_admin_setting(
            "pdf_global_watermark_enabled",
            False),
        False)
    if not enabled:
        return
    text = load_admin_setting(
        "pdf_global_watermark_text",
        "VERTRAULICH") or "VERTRAULICH"
    # Opazität optional (0..1); wenn nicht unterstützt, dann sehr helle Farbe
    opacity = load_admin_setting("pdf_global_watermark_opacity", 0.10)
    try:
        opacity = float(opacity)
    except Exception:
        opacity = 0.10

    c.saveState()
    try:
        # Sehr helle graublaue Farbe, ggf. mit Alpha
        col = Color(0.6, 0.65, 0.75)
        try:
            c.setFillAlpha(max(0.02, min(0.3, opacity)))  # ReportLab 3.6+
        except Exception:
            pass
        c.setFillColor(col)
        c.setFont("Helvetica-Bold", 64)
        # Diagonal drehen und wiederholt zeichnen
        c.translate(page_width * 0.15, page_height * 0.25)
        c.rotate(30)
        # Kacheln über die Seite verteilen
        step_x = 380
        step_y = 260
        for iy in range(0, int(page_height * 1.2), step_y):
            for ix in range(0, int(page_width * 1.2), step_x):
                try:
                    c.drawString(ix, iy, text)
                except Exception:
                    pass
    finally:
        c.restoreState()


def parse_coords_file(path: Path) -> list[dict[str, Any]]:
    """Liest eine seiteX.yml und gibt eine Liste von Einträgen zurück.

    Einträge sind durch eine Zeile beginnend mit '-' oder '---' getrennt.
    Unterstützte Felder: Text, Position(x0,y0,x1,y1), Schriftart, Schriftgröße, Farbe
    """
    elements: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    if not path.exists():
        return elements
    with path.open(encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            # Einträge sind durch Linien aus '-' getrennt (z.B.
            # "----------------------------------------")
            if (line.startswith("---") or (set(line) ==
                                           {"-"} and len(line) >= 3)) and current:
                elements.append(current)
                current = {}
                continue
            if line.startswith("Text:"):
                current["text"] = line.split(":", 1)[1].strip()
            elif line.startswith("Position:"):
                # Zahlen extrahieren (auch mit Komma als Dezimaltrenner)
                nums = re.findall(r"[-+]?[0-9]*[\.,]?[0-9]+", line)
                nums = [n.replace(",", ".") for n in nums]
                if len(nums) >= 4:
                    current["position"] = tuple(float(n) for n in nums[:4])
            elif line.startswith("Schriftart:"):
                current["font"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("schriftgröße:") or line.lower().startswith("schriftgroesse:"):
                try:
                    val = line.split(":", 1)[1].strip().replace(",", ".")
                    current["font_size"] = float(val)
                except Exception:
                    current["font_size"] = 10.0
            elif line.startswith("Farbe:"):
                try:
                    val = line.split(":", 1)[1].strip()
                    if val.lower().startswith("0x"):
                        current["color"] = int(val, 16)
                    else:
                        current["color"] = int(val)
                except Exception:
                    current["color"] = 0
        if current:
            elements.append(current)
    return elements


def int_to_color(value: int) -> Color:
    """Wandelt einen Integer (0xRRGGBB) in reportlab Color um."""
    r = ((value >> 16) & 0xFF) / 255.0
    g = ((value >> 8) & 0xFF) / 255.0
    b = (value & 0xFF) / 255.0
    return Color(r, g, b)


def _draw_company_logo(c: canvas.Canvas,
                       dynamic_data: dict[str,
                                          str],
                       page_width: float,
                       page_height: float) -> None:
    """Zeichnet das Firmenlogo links oben, wenn company_logo_b64 vorhanden ist."""
    b64 = dynamic_data.get("company_logo_b64") or ""
    if not b64:
        return
    try:
        img_bytes = base64.b64decode(b64)
        img = ImageReader(io.BytesIO(img_bytes))
        # Zielfläche: max Breite/Höhe
        max_w, max_h = 120, 50  # Punkte
        c.saveState()
        # Hintergrund-Logo-Bereich abdecken (weißes Rechteck), um falsche Logos
        # aus Templates zu maskieren
        try:
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(1, 1, 1)
            c.rect(
                15,
                page_height -
                20 -
                max_h -
                5,
                max_w +
                20,
                max_h +
                10,
                stroke=0,
                fill=1)
        except Exception:
            pass
        c.drawImage(
            img,
            20,
            page_height -
            20 -
            max_h,
            width=max_w,
            height=max_h,
            preserveAspectRatio=True,
            mask='auto')
        c.restoreState()
    except Exception:
        return


def _parse_percent(value: str | float | int) -> float:
    try:
        if isinstance(value, (int, float)):
            return max(0.0, min(100.0, float(value)))
        s = str(value).strip().replace(
            '%',
            '').replace(
            ',',
            '.').replace(
            ' ',
            '')
        return max(0.0, min(100.0, float(s)))
    except Exception:
        return 0.0


def _first_valid_percent(
        dynamic_data: dict[str, str], keys: list[str]) -> float:
    for k in keys:
        if k in dynamic_data and dynamic_data.get(k) not in (None, ""):
            v = _parse_percent(dynamic_data.get(k))
            print(
                f"DEBUG: _first_valid_percent - Key: {k}, Value: {dynamic_data.get(k)}, Parsed: {v}")
            if v > 0:
                return v
    print(
        f"DEBUG: _first_valid_percent - Keine gültigen Werte gefunden für Keys: {keys}")
    return 0.0


def _draw_donut(
        c: canvas.Canvas,
        cx: float,
        cy: float,
        pct: float,
        outer_r: float,
        inner_r: float,
        color_fg: Color,
        color_bg: Color) -> None:
    """Zeichnet einen Donut (Ring) mit farbigem Anteil pct in % (0-100)."""
    from reportlab.lib.colors import white
    # Voller Hintergrund-Ring
    c.saveState()
    # Hintergrund-Kreis (voll)
    c.setFillColor(color_bg)
    c.circle(cx, cy, outer_r, stroke=0, fill=1)
    # Vordergrund-Wedge (Anteil)
    extent = -360.0 * (pct / 100.0)  # im Uhrzeigersinn
    try:
        c.setFillColor(color_fg)
        c.wedge(
            cx - outer_r,
            cy - outer_r,
            cx + outer_r,
            cy + outer_r,
            90,
            extent,
            stroke=0,
            fill=1)
    except Exception:
        pass
    # Loch stanzen
    c.setFillColor(white)
    c.circle(cx, cy, inner_r, stroke=0, fill=1)
    c.restoreState()


def _draw_page3_waterfall_chart(c: canvas.Canvas,
                                dynamic_data: dict[str,
                                                   str],
                                page_width: float,
                                page_height: float) -> None:
    """Zeichnet ein Wasserfall-Diagramm auf Seite 3 mit den Berechnungsergebnissen.

    Positionierung basierend auf den exakten Koordinaten aus seite3.yml:
    - Linker Rand: Position der "Neigung des Daches" Spalte (X=300.48)
    - Rechter Rand: Position des letzten Buchstabens von "Art" (X=547.50)
    - Oben: 10 Punkte oberhalb von "Direkt" (Y=516.11 - 10 = 506.11)
    - Unten: 10 Punkte oberhalb von "Berechnungsgrundlagen" (Y=645.42 - 10 = 635.42)
    """

    # Extrahiere die Werte aus dynamic_data
    try:
        # DEBUG: Zeige alle verfügbaren Keys an
        print(
            f"DEBUG: Verfügbare dynamic_data Keys: {
                list(
                    dynamic_data.keys())}")

        # Werte aus den berechneten Ergebnissen - verschiedene Keys probieren
        direkt_eur = 0.0
        einspeisung_eur = 0.0
        steuer_eur = 0.0
        gesamt_eur = 0.0

        def safe_float_convert(value):
            """Sichere Konvertierung zu float mit besserer Fehlerbehandlung"""
            if value is None or value == "":
                return 0.0
            try:
                clean_value = str(value).replace(
                    '€', '').replace(' ', '').strip()

                # Bestimme das Format basierend auf der Struktur
                if ',' in clean_value and '.' in clean_value:
                    # Deutsches Format: 1.503,32 (Punkt als Tausender, Komma als Dezimal)
                    # Finde die Position von Komma und Punkt
                    comma_pos = clean_value.rfind(',')
                    dot_pos = clean_value.rfind('.')

                    if comma_pos > dot_pos:
                        # Deutsches Format: 1.503,32
                        integer_part = clean_value[:comma_pos].replace('.', '')
                        decimal_part = clean_value[comma_pos + 1:]
                        clean_value = f"{integer_part}.{decimal_part}"
                    else:
                        # Englisches Format: 1,503.32
                        integer_part = clean_value[:dot_pos].replace(',', '')
                        decimal_part = clean_value[dot_pos + 1:]
                        clean_value = f"{integer_part}.{decimal_part}"

                elif ',' in clean_value:
                    # Nur Komma vorhanden
                    # Prüfe ob es Dezimaltrennzeichen oder
                    # Tausendertrennzeichen ist
                    comma_pos = clean_value.rfind(',')
                    after_comma = clean_value[comma_pos + 1:]

                    if len(after_comma) <= 2 and after_comma.isdigit():
                        # Wahrscheinlich Dezimaltrennzeichen: 1503,32
                        clean_value = clean_value.replace(',', '.')
                    else:
                        # Wahrscheinlich Tausendertrennzeichen: 1,503
                        clean_value = clean_value.replace(',', '')

                elif '.' in clean_value:
                    # Nur Punkt vorhanden
                    dot_pos = clean_value.rfind('.')
                    after_dot = clean_value[dot_pos + 1:]

                    if len(after_dot) <= 2 and after_dot.isdigit():
                        # Wahrscheinlich Dezimaltrennzeichen: 1503.32
                        pass  # Bereits korrekt
                    else:
                        # Wahrscheinlich Tausendertrennzeichen: 1.503
                        clean_value = clean_value.replace('.', '')

                return float(clean_value)
            except Exception as e:
                print(f"DEBUG: Fehler bei Konvertierung von '{value}': {e}")
                return 0.0

        # Direktverbrauch - KORREKTE Keys basierend auf placeholders.py
        # "Direkt": "self_consumption_without_battery_eur"
        direkt_keys = [
            'self_consumption_without_battery_eur',  # Hauptkey aus placeholders.py
            'direct_consumption_savings_eur',
            'einsparung_direktverbrauch_eur',
            'direktverbrauch_einsparung_eur'
        ]

        for key in direkt_keys:
            if key in dynamic_data and dynamic_data[key] not in (
                    None, "", "0", 0):
                direkt_eur = safe_float_convert(dynamic_data[key])
                print(
                    f"DEBUG: Direktverbrauch gefunden - Key: {key}, Wert: {
                        dynamic_data[key]} -> {direkt_eur}€")
                break

        # Einspeisevergütung - KORREKTE Keys basierend auf placeholders.py
        # "Einspeisung": "annual_feed_in_revenue_eur"
        einspeisung_keys = [
            'annual_feed_in_revenue_eur',  # Hauptkey aus placeholders.py
            'direct_grid_feed_in_eur',     # Alias aus placeholders.py
            'feed_in_revenue_eur',
            'einnahmen_einspeisung_eur'
        ]

        for key in einspeisung_keys:
            if key in dynamic_data and dynamic_data[key] not in (
                    None, "", "0", 0):
                einspeisung_eur = safe_float_convert(dynamic_data[key])
                print(
                    f"DEBUG: Einspeisevergütung gefunden - Key: {key}, Wert: {
                        dynamic_data[key]} -> {einspeisung_eur}€")
                break

        # Steuervorteile - KORREKTE Keys basierend auf placeholders.py
        # "platz1": "tax_benefits_eur"  # Steuerliche Vorteile
        steuer_keys = [
            'tax_benefits_eur',  # Hauptkey aus placeholders.py
            'steuerliche_vorteile_eur',
            'vorteile_steuerfrei_eur',
            'steuervorteile_eur'
        ]

        for key in steuer_keys:
            if key in dynamic_data and dynamic_data[key] not in (
                    None, "", "0", 0):
                steuer_eur = safe_float_convert(dynamic_data[key])
                print(
                    f"DEBUG: Steuervorteile gefunden - Key: {key}, Wert: {
                        dynamic_data[key]} -> {steuer_eur}€")
                break

        # Gesamt - KORREKTE Keys basierend auf placeholders.py
        # "Gesamt": "total_annual_savings_eur"
        gesamt_keys = [
            'total_annual_savings_eur',  # Hauptkey aus placeholders.py
            'gesamt_ertraege_jahr_eur',
            'annual_total_benefits_eur',
            'total_benefits_eur'
        ]

        for key in gesamt_keys:
            if key in dynamic_data and dynamic_data[key] not in (
                    None, "", "0", 0):
                gesamt_eur = safe_float_convert(dynamic_data[key])
                print(
                    f"DEBUG: Gesamt gefunden - Key: {key}, Wert: {dynamic_data[key]} -> {gesamt_eur}€")
                break

        # Falls Gesamt nicht direkt verfügbar, berechne es
        if gesamt_eur <= 0:
            gesamt_eur = direkt_eur + einspeisung_eur + steuer_eur

        print(
            f"DEBUG: Wasserfall-Werte - Direkt: {direkt_eur}€, Einspeisung: {einspeisung_eur}€, Steuer: {steuer_eur}€, Gesamt: {gesamt_eur}€")

        # Fallback-Werte für Demo-Zwecke wenn keine Daten vorhanden
        if direkt_eur <= 0 and einspeisung_eur <= 0 and steuer_eur <= 0:
            print("DEBUG: Keine Wasserfall-Werte vorhanden - verwende Demo-Werte")
            direkt_eur = 1200.0
            einspeisung_eur = 800.0
            steuer_eur = 300.0
            gesamt_eur = 2300.0

    except Exception as e:
        print(f"DEBUG: Fehler beim Extrahieren der Wasserfall-Werte: {e}")
        # Fallback-Werte
        direkt_eur = 1200.0
        einspeisung_eur = 800.0
        steuer_eur = 300.0
        gesamt_eur = 2300.0

    # EXAKTE Positionierung basierend auf den Koordinaten aus seite3.yml
    # "Neigung des Daches" Position: (300.4767150878906, 669.0659790039062, ...)
    # "Art" Position: (510.2286071777344, 687.5770263671875, 547.504638671875, ...)
    # "Direkt" Position: (240.05039978027344, 516.1068115234375, ...)
    # "Berechnungsgrundlagen" Position: (39.64636993408203, 645.4224853515625, ...)

    chart_left = 300.48  # Exakte Position "Neigung des Daches"
    chart_right = 547.50  # Exakte Position Ende von "Art"
    # 40 Punkte oberhalb "Direkt" (10 Punkte höher als vorher)
    chart_top = page_height - (516.11 - 40)
    # 40 Punkte oberhalb "Berechnungsgrundlagen" (10 Punkte höher als vorher)
    chart_bottom = page_height - (645.42 - 40)

    chart_width = chart_right - chart_left
    chart_height = chart_top - chart_bottom

    print(
        f"DEBUG: Wasserfall-Chart EXAKTE Position - Links: {chart_left}, Rechts: {chart_right}, Oben: {chart_top}, Unten: {chart_bottom}")
    print(
        f"DEBUG: Chart-Dimensionen - Breite: {chart_width:.1f}, Höhe: {chart_height:.1f}")

    if chart_width <= 0 or chart_height <= 0:
        print("DEBUG: Ungültige Chart-Dimensionen")
        return

    c.saveState()

    # Farben: Verschiedene Blau-Töne wie in der PDF verwendet
    from reportlab.lib.colors import Color
    bar_colors = [
        Color(0.07, 0.34, 0.60),  # Dunkelblau für Direktverbrauch
        Color(0.12, 0.42, 0.68),  # Mittelblau für Einspeisevergütung
        Color(0.18, 0.50, 0.76),  # Hellblau für Steuervorteile
        Color(0.05, 0.28, 0.52),  # Sehr dunkelblau für Gesamt
    ]
    text_color = Color(0.2, 0.2, 0.2)    # Dunkelgrau für Text
    line_color = Color(0.4, 0.4, 0.4)    # Grau für Verbindungslinien

    # Daten für das Wasserfall-Diagramm
    values = [direkt_eur, einspeisung_eur, steuer_eur]
    labels = [
        "Einsparung durch\nDirektverbrauch",
        "Einnahmen aus\nEinspeisevergütung",
        "Vorteile durch\nsteuerfreie Einspeisung"]

    # Maximaler Wert für Skalierung (verwende Gesamt als Referenz)
    max_value = max(gesamt_eur, max(values)) if values else 1000
    if max_value <= 0:
        max_value = 1000

    # Balken-Layout: 3 Einzelbalken + 1 Gesamtbalken
    num_individual_bars = len(values)
    total_bars = num_individual_bars + 1  # +1 für Gesamtbalken

    # Bereich für Einzelbalken (70% der Breite) und Gesamtbalken (20% der
    # Breite)
    individual_area_width = chart_width * 0.70
    total_area_width = chart_width * 0.25
    gap_width = chart_width * 0.05

    # Balken-Breite und Abstände für Einzelbalken
    individual_bar_spacing = individual_area_width / num_individual_bars
    individual_bar_width = individual_bar_spacing * 0.7  # 70% des verfügbaren Platzes

    # Gesamtbalken-Breite
    total_bar_width = total_area_width * 0.8

    # Zeichne die Einzelbalken (Wasserfall-Komponenten)
    cumulative_height = 0
    bar_positions = []  # Speichere Positionen für Verbindungslinien

    for i, (value, label, color) in enumerate(
            zip(values, labels, bar_colors[:3], strict=False)):
        # WICHTIG: Zeige alle Balken an, auch wenn Wert 0 ist (für bessere
        # Visualisierung)
        if value < 0:  # Nur negative Werte überspringen
            continue

        # Balken-Position
        bar_x = chart_left + (i + 0.5) * \
            individual_bar_spacing - individual_bar_width / 2

        # Mindesthöhe für Balken mit Wert 0 (für bessere Sichtbarkeit)
        if value <= 0:
            bar_height = 5.0  # Minimale Höhe für 0-Werte
        else:
            bar_height = (value / max_value) * chart_height * \
                0.75  # 75% der verfügbaren Höhe nutzen

        bar_y = chart_bottom + cumulative_height

        # Zeichne Balken (auch für 0-Werte)
        c.setFillColor(color)
        c.rect(
            bar_x,
            bar_y,
            individual_bar_width,
            bar_height,
            stroke=0,
            fill=1)

        # Speichere Position für Verbindungslinien
        bar_positions.append({
            'x': bar_x + individual_bar_width / 2,
            'y_bottom': bar_y,
            'y_top': bar_y + bar_height,
            'value': value
        })

        # Wert über dem Balken (auch für 0-Werte anzeigen)
        c.setFillColor(text_color)
        c.setFont("Helvetica-Bold", 7)
        if value <= 0:
            value_text = "0 €"
        else:
            value_text = f"{value:,.0f} €".replace(',', '.')
        text_width = c.stringWidth(value_text, "Helvetica-Bold", 7)
        c.drawString(bar_x + (individual_bar_width - text_width) /
                     2, bar_y + bar_height + 3, value_text)

        # Label unter dem Balken (mehrzeilig)
        c.setFont("Helvetica", 6)
        label_lines = label.split('\n')
        for j, line in enumerate(label_lines):
            line_width = c.stringWidth(line, "Helvetica", 6)
            c.drawString(bar_x + (individual_bar_width -
                         line_width) / 2, bar_y - 12 - (j * 8), line)

        # Aktualisiere kumulative Höhe für Wasserfall-Effekt (nur für echte
        # Werte)
        if value > 0:
            cumulative_height += bar_height

        print(
            f"DEBUG: Balken {
                i +
                1} ({
                label.replace(
                    chr(10),
                    ' ')}): X={
                    bar_x:.1f}, Y={
                        bar_y:.1f}, Breite={
                            individual_bar_width:.1f}, Höhe={
                                bar_height:.1f}, Wert={value}€")

    # Zeichne Verbindungslinien zwischen den Balken (Wasserfall-Effekt)
    c.setStrokeColor(line_color)
    c.setLineWidth(1)

    # Versuche gestrichelte Linie zu setzen (falls verfügbar)
    try:
        c.setDash([2, 2])  # Gestrichelte Linie
    except AttributeError:
        pass  # Fallback auf durchgezogene Linie

    for i in range(len(bar_positions) - 1):
        current_pos = bar_positions[i]
        next_pos = bar_positions[i + 1]

        # Linie von der Oberseite des aktuellen Balkens zur Unterseite des
        # nächsten
        c.line(
            current_pos['x'] +
            individual_bar_width /
            4,
            current_pos['y_top'],
            next_pos['x'] -
            individual_bar_width /
            4,
            next_pos['y_bottom'])

    # Zeichne den Gesamtbalken (rechts)
    total_bar_x = chart_left + individual_area_width + gap_width
    total_bar_height = (gesamt_eur / max_value) * chart_height * 0.75
    total_bar_y = chart_bottom

    # Zurück zu durchgezogener Linie
    try:
        c.setDash([])
    except AttributeError:
        pass
    c.setFillColor(bar_colors[3])  # Dunkelblau für Gesamt
    c.rect(
        total_bar_x,
        total_bar_y,
        total_bar_width,
        total_bar_height,
        stroke=0,
        fill=1)

    # Wert über dem Gesamtbalken
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 8)
    total_text = f"{gesamt_eur:,.0f} €".replace(',', '.')
    total_text_width = c.stringWidth(total_text, "Helvetica-Bold", 8)
    c.drawString(total_bar_x + (total_bar_width - total_text_width) /
                 2, total_bar_y + total_bar_height + 3, total_text)

    # Label unter dem Gesamtbalken
    c.setFont("Helvetica-Bold", 7)
    total_label = "Gesamt Erträge\npro Jahr"
    total_label_lines = total_label.split('\n')
    for j, line in enumerate(total_label_lines):
        line_width = c.stringWidth(line, "Helvetica-Bold", 7)
        c.drawString(total_bar_x + (total_bar_width - line_width) /
                     2, total_bar_y - 12 - (j * 9), line)

    # Verbindungslinie vom letzten Einzelbalken zum Gesamtbalken
    if bar_positions:
        last_pos = bar_positions[-1]
        c.setStrokeColor(line_color)
        try:
            c.setDash([2, 2])  # Gestrichelte Linie
        except AttributeError:
            pass  # Fallback auf durchgezogene Linie
        c.line(last_pos['x'] + individual_bar_width / 4, last_pos['y_top'],
               total_bar_x - 5, total_bar_y + total_bar_height)

    print(
        f"DEBUG: Gesamtbalken: X={
            total_bar_x:.1f}, Y={
            total_bar_y:.1f}, Breite={
                total_bar_width:.1f}, Höhe={
                    total_bar_height:.1f}, Wert={gesamt_eur}€")

    c.restoreState()


def _draw_page6_storage_donuts(c: canvas.Canvas,
                               dynamic_data: dict[str,
                                                  str],
                               page_width: float,
                               page_height: float) -> None:
    """Zeichnet zwei Donut-Diagramme für Speicher-Relationen auf Seite 6 NEBENEINANDER wie auf Seite 1."""
    # Werte aus dynamic_data ziehen
    pct_consumption = _first_valid_percent(dynamic_data, [
        "storage_consumption_ratio_percent",
    ])
    pct_production = _first_valid_percent(dynamic_data, [
        "storage_production_ratio_percent",
    ])

    print(
        f"DEBUG: Seite 6 Donut-Charts - Consumption: {pct_consumption}%, Production: {pct_production}%")

    if pct_consumption <= 0 and pct_production <= 0:
        print("DEBUG: Keine Donut-Charts gezeichnet - beide Werte <= 0")
        return

    c.saveState()

    # SICHTBARE Positionierung - Mitte der Seite für bessere Sichtbarkeit
    # Teste erstmal in der Mitte der Seite
    chart_cy = page_height / 2.0  # Mitte der Seite

    # X-Positionen: Deutlich sichtbar nebeneinander
    left_cx = 200.0   # Links
    right_cx = 400.0  # Rechts

    print(
        f"DEBUG: Chart-Positionen - Links: ({left_cx}, {chart_cy}), Rechts: ({right_cx}, {chart_cy})")
    print(f"DEBUG: Seitengröße: {page_width} x {page_height}")

    outer_r = 40.0  # NOCH GRÖßERE Charts für bessere Sichtbarkeit
    inner_r = 25.0

    # Farben - SEHR SICHTBARE Farben für bessere Erkennung
    from reportlab.lib.colors import Color
    bg = Color(0.9, 0.9, 0.9)  # Hellgrau Hintergrund
    fg_consumption = Color(0.0, 0.0, 1.0)  # REINES BLAU für Verbrauch
    fg_production = Color(1.0, 0.0, 0.0)   # REINES ROT für Produktion

    # Linker Donut: Speicher zu Tagesverbrauch
    if pct_consumption > 0:
        print(
            f"DEBUG: Zeichne Consumption Donut bei ({left_cx}, {chart_cy}) mit {pct_consumption}%")
        _draw_donut(
            c,
            left_cx,
            chart_cy,
            pct_consumption,
            outer_r,
            inner_r,
            fg_consumption,
            bg)
        # Zentrumstext
        txt = f"{int(round(pct_consumption))}%"
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(fg_consumption)
        tw = c.stringWidth(txt, "Helvetica-Bold", 11)
        c.drawString(left_cx - tw / 2, chart_cy - 5, txt)

        # Label unter dem Chart
        label_txt = "Tagesverbrauch"
        c.setFont("Helvetica", 8)
        c.setFillColor(Color(0.2, 0.2, 0.2))
        lw = c.stringWidth(label_txt, "Helvetica", 8)
        c.drawString(left_cx - lw / 2, chart_cy - outer_r - 12, label_txt)

    # Rechter Donut: Speicher zu PV-Produktion
    if pct_production > 0:
        print(
            f"DEBUG: Zeichne Production Donut bei ({right_cx}, {chart_cy}) mit {pct_production}%")
        _draw_donut(
            c,
            right_cx,
            chart_cy,
            pct_production,
            outer_r,
            inner_r,
            fg_production,
            bg)
        # Zentrumstext
        txt = f"{int(round(pct_production))}%"
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(fg_production)
        tw = c.stringWidth(txt, "Helvetica-Bold", 11)
        c.drawString(right_cx - tw / 2, chart_cy - 5, txt)

        # Label unter dem Chart
        label_txt = "PV-Produktion"
        c.setFont("Helvetica", 8)
        c.setFillColor(Color(0.2, 0.2, 0.2))
        lw = c.stringWidth(label_txt, "Helvetica", 8)
        c.drawString(right_cx - lw / 2, chart_cy - outer_r - 12, label_txt)

    c.restoreState()


def _draw_page1_kpi_donuts(c: canvas.Canvas,
                           dynamic_data: dict[str,
                                              str],
                           page_width: float,
                           page_height: float) -> None:
    """Zeichnet zwei Donut-Diagramme (Unabhängigkeit, Eigenverbrauch) auf Seite 1 unterhalb der KPI-Überschrift."""
    # Werte aus dynamic_data ziehen (formatiert wie "54%" / "42%")
    # Robuste Ermittlung mit Fallback-Keys
    pct_autark = _first_valid_percent(dynamic_data, [
        "self_supply_rate_percent",
        "self_sufficiency_percent",
        "autarky_percent",
    ])
    pct_ev = _first_valid_percent(dynamic_data, [
        "self_consumption_percent",
        # Seite 2 abgeleiteter Wert (nur Zahl): direkter Deckungsanteil am
        # Verbrauch
        "direct_cover_consumption_percent_number",
    ])
    if pct_autark <= 0 and pct_ev <= 0:
        return
    c.saveState()
    # Positionen grob unter "KENNZAHLEN IHRES PV-SYSTEMS" (YAML liegt bei ~494pt Höhe)
    # Position: weiter links und etwas nach unten, größer
    cy = 440.0
    left_cx = 95.0
    # Rechtsen Donut weiter nach rechts, zentriert über "EIGENVERBRAUCH"
    right_cx = 210.0
    outer_r = 40.0
    inner_r = 26.0
    # Farben (beide Donuts in Blau, Hintergrund hellgrau)
    from reportlab.lib.colors import Color
    bg = Color(0.85, 0.88, 0.90)
    fg_blue = Color(0.07, 0.34, 0.60)
    if pct_autark > 0:
        _draw_donut(c, left_cx, cy, pct_autark, outer_r, inner_r, fg_blue, bg)
        # Zentrumstext
        txt = dynamic_data.get("self_supply_rate_percent",
                               f"{int(round(pct_autark))}%")
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(fg_blue)
        tw = c.stringWidth(txt, "Helvetica-Bold", 12)
        c.drawString(left_cx - tw / 2, cy - 6, txt)
    if pct_ev > 0:
        _draw_donut(c, right_cx, cy, pct_ev, outer_r, inner_r, fg_blue, bg)
        txt = dynamic_data.get("self_consumption_percent",
                               f"{int(round(pct_ev))}%")
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(fg_blue)
        tw = c.stringWidth(txt, "Helvetica-Bold", 12)
        c.drawString(right_cx - tw / 2, cy - 6, txt)
    c.restoreState()


def _draw_top_right_triangle(
        c: canvas.Canvas,
        page_width: float,
        page_height: float,
        size: float = 36.0) -> None:
    """Zeichnet ein kleines, gefülltes Dreieck oben rechts (nur Seite 1).

    Farbe: identisch zum Blau der Fußzeilen/Charts (dezentes Dunkelblau).
    Das Dreieck wird vor den Texten gezeichnet, damit Beschriftungen nicht verdeckt werden.
    """
    # Akzentfarbe wie in Fußzeilen (#1B3670)
    accent = Color(27 / 255.0, 54 / 255.0, 112 / 255.0)
    c.saveState()
    try:
        # Punkte: Ecke oben rechts und zwei Katheten entlang der Ränder
        x0, y0 = page_width, page_height
        path = c.beginPath()
        path.moveTo(x0, y0)  # oben rechts
        path.lineTo(x0 - size, y0)  # nach links
        path.lineTo(x0, y0 - size)  # nach unten
        path.close()
        c.setFillColor(accent)
        c.setStrokeColor(accent)
        c.drawPath(path, stroke=0, fill=1)
    finally:
        c.restoreState()

# pdf_template_engine/dynamic_overlay.py


def generate_overlay(coords_dir: Path,
                     dynamic_data: dict[str,
                                        str],
                     total_pages: int = 7) -> bytes:
    """Erzeugt ein Overlay-PDF für sieben Seiten anhand der coords-Dateien.

    total_pages steuert die Fußzeilen-Nummerierung als "Seite x von XX".
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4
    for i in range(1, 8):
        yml_path = coords_dir / f"seite{i}.yml"
        elements = parse_coords_file(yml_path)
        # Firmenlogo zuerst
        _draw_company_logo(c, dynamic_data, page_width, page_height)
        # Dreieck
        _draw_top_right_triangle(c, page_width, page_height, size=36.0)
        # Seite 1 Sonderdiagramme
        if i == 1:
            _draw_page1_kpi_donuts(c, dynamic_data, page_width, page_height)
        # Seite 6 Speicher-Donut-Charts
        if i == 6:
            _draw_page6_storage_donuts(
                c, dynamic_data, page_width, page_height)

        # Seite 3 Wasserfall-Diagramm
        if i == 3:
            _draw_page3_waterfall_chart(
                c, dynamic_data, page_width, page_height)
        # Seite 3 rechter Chart
        if i == 3:
            try:
                c.saveState()
                try:
                    c.setFillColorRGB(1, 1, 1)
                    c.rect(
                        350,
                        page_height -
                        170 -
                        230,
                        260,
                        250,
                        stroke=0,
                        fill=1)
                finally:
                    c.restoreState()
                _draw_page3_right_chart_and_separator(
                    c, elements, dynamic_data, page_width, page_height)
            except Exception:
                pass
        # Seite 4 Produktbilder
        if i == 4:
            _draw_page4_component_images(
                c, dynamic_data, page_width, page_height)
            # Hersteller-Brand-Logos (nach Produktbildern, vor Textlayer optional)
            # Logos werden später auch nach dem Text gerendert um Überdeckung
            # sicherzustellen

        # Keys für horizontale Zentrierung innerhalb Box
        # Keys für horizontale Zentrierung innerhalb Box
        center_keys = {
            "direct_consumption_quote_prod_percent",
            "battery_use_quote_prod_percent",
            "feed_in_quote_prod_percent_number",
            "battery_cover_consumption_percent",
            "grid_consumption_rate_percent",
            "direct_cover_consumption_percent_number",
        }

        # Seite 1: bestimmte dynamische Werte rechtsbündig ausrichten
        right_align_tokens_s1 = {
            "36.958,00 EUR*",        # anlage_kwp (tatsächlicher Beispieltext!)
            "8.251,92 kWh/Jahr",     # annual_pv_production_kwh
            "29.150,00 EUR*",        # amortization_time
        }

        # Seite 3: bestimmte Werte rechtsbündig an der rechten Boxkante (x1)
        # ausrichten
        right_align_tokens_s3 = {
            "NOSW",
            "Deckung",
            "Verbrauch 32 Cent",
            "Kredit",
            "Neigung",
            "Art",
            "EEG",
            # Berechnungswerte rechtsbündig ausrichten
            "Direkt",
            "Einspeisung",
            "platz1",  # Steuerliche Vorteile
            "Speichernutzung",
            "Überschuss",
            "Gesamt",
            "test",
        }

        # Seite 3: Positionen der (entfernten) statischen 10-Jahres-Kosten
        # einsammeln
        page3_cost_tokens: dict[str, dict[str, Any]] = {}
        if i == 3:
            _cost_token_map = {
                "46.296,00 €": "cost_10y_no_increase_number",
                "58.230,61 €": "cost_10y_with_increase_number",
            }
            for elem in elements:
                ttxt = (elem.get("text") or "").strip()
                if ttxt in _cost_token_map and isinstance(
                        elem.get("position"), tuple) and len(
                        elem.get("position")) == 4:
                    # Speichere Position + Font-Infos und referenzierten
                    # dynamischen Key
                    page3_cost_tokens[_cost_token_map[ttxt]] = {
                        "position": elem.get("position"),
                        "font": elem.get("font", "Helvetica-Bold"),
                        "font_size": float(elem.get("font_size", 10.49)),
                        "original_text": ttxt,
                    }

        # Seite 6: Dynamisches Nachrücken (Compacting) für Produkt- &
        # Dienstleistungszeilen
        if i == 6:
            try:
                elements = _compact_page6_elements(
                    elements, dynamic_data, page_height)
            except Exception as e:
                print(f"WARN: Compacting Seite6 fehlgeschlagen: {e}")

        for elem in elements:
            text = elem.get("text", "")
            key = PLACEHOLDER_MAPPING.get(text)
            if text in ["Logomodul", "Logoricht", "Logoakkus"]:
                # Platzhalter komplett überspringen (Legacy entfernt)
                continue

            # Seite 6: Speicher-Relationen Platzhalter überspringen (werden
            # durch Donut-Charts ersetzt)
            if i == 6 and text in [
                "relation_tagverbrauch_prozent",
                    "relation_pvproduktion_prozent"]:
                print(
                    f"DEBUG: Überspringe Platzhalter-Text '{text}' - wird durch Donut-Chart ersetzt")
                continue

            # Seite 4: Firmenname und TÜV-Text dynamisch behandeln
            if i == 4 and text == "firmen_name":
                company_name = dynamic_data.get("company_name", "")
                if company_name:
                    draw_text = company_name
                    print(
                        f"DEBUG: Seite 4 Firmenname ersetzt: '{text}' -> '{company_name}'")
                else:
                    draw_text = "Ihr Unternehmen"  # Fallback
            else:
                # Normale Text-Behandlung
                draw_text = (dynamic_data.get(key, "") if key else text)

            pos = elem.get("position", (0, 0, 0, 0))
            if len(pos) == 4:
                x0, y0, x1, y1 = pos
                draw_x = x0
                draw_y = page_height - y1
            else:
                draw_x = 0
                draw_y = 0
            font_name = elem.get("font", "Helvetica")
            font_size = float(elem.get("font_size", 10.0))

            # Seite 4: TÜV-Text dynamisch nach Firmennamen positionieren
            if i == 4 and text == "verwendet ausschließlich TÜV geprüfte Komponenten, die sämtlichen gängigen Normen und Zertifizierungen entsprechen.":
                company_name = dynamic_data.get(
                    "company_name", "Ihr Unternehmen")

                # Font setzen für Breitenberechnung
                try:
                    c.setFont(font_name, font_size)
                except Exception:
                    c.setFont("Helvetica", font_size)

                # Breite des Firmennamens + 1 Leertaste berechnen
                # ReportLab-kompatible Font-Namen verwenden
                safe_font_name = "Helvetica" if "Helvetica" in font_name else font_name
                company_width = c.stringWidth(
                    company_name + " ", safe_font_name, font_size)

                # Neue X-Position: Start des Firmennamens (45.0) + Breite des
                # Firmennamens + Leertaste
                draw_x = 45.0 + company_width

                print(
                    f"DEBUG: Seite 4 TÜV-Text dynamisch positioniert bei X={
                        draw_x:.1f} (nach '{company_name}')")
                draw_text = text  # Originaler TÜV-Text
            try:
                c.setFont(font_name, font_size)
            except Exception:
                c.setFont("Helvetica", font_size)
            color_int = int(elem.get("color", 0))
            # Dynamische Farblogik für Seite 6 Dienstleistungen
            if i == 6 and key:
                try:
                    # Service-Design-Farben aus dynamic_data
                    sym_color_hex = dynamic_data.get('service_symbol_color')
                    lbl_color_hex = dynamic_data.get('service_label_color')
                    hide_val_col = bool(
                        dynamic_data.get('service_value_column_hidden'))
                    is_label = text.startswith('X_LBL_')
                    is_value = text.startswith(
                        'X_SRV_') or text.startswith('X_PROD_')

                    def _hex_to_color(h):
                        from reportlab.lib.colors import Color
                        h = h.lstrip('#')
                        if len(h) == 6:
                            r = int(h[0:2], 16) / 255.0
                            g = int(h[2:4], 16) / 255.0
                            b = int(h[4:6], 16) / 255.0
                            return Color(r, g, b)
                        return int_to_color(color_int)
                    if is_label and lbl_color_hex:
                        c.setFillColor(_hex_to_color(lbl_color_hex))
                    elif is_value and sym_color_hex:
                        c.setFillColor(_hex_to_color(sym_color_hex))
                    else:
                        c.setFillColor(int_to_color(color_int))
                    # Value-Spalte ausblenden erzwingen (leer zeichnen) – wenn
                    # hide aktiv und es ist Value
                    if hide_val_col and is_value and (
                            text.startswith('X_SRV_') or text.startswith('X_PROD_')):
                        draw_text = ''
                except Exception:
                    c.setFillColor(int_to_color(color_int))
            else:
                c.setFillColor(int_to_color(color_int))

            # Seite 3: Ersetzte / entfernte statische 10-Jahres-Kosten NICHT
            # erneut zeichnen
            if i == 3 and text in {"46.296,00 €", "58.230,61 €"}:
                continue

            # ========================================================================
            # START DER KORREKTUR: Die fehlerhafte Logik wird hier entfernt
            # ========================================================================
            if i == 3 and (text or "").strip() == "EUR" and pos[0] >= 100.0:
                continue  # Spezifische "EUR" Texte ignorieren, falls nötig
            # ========================================================================
            # ENDE DER KORREKTUR
            # ========================================================================

            # Normale Text-Rendering

            if i == 3 and key == "battery_usage_savings_eur":
                c.saveState()
                c.setStrokeColor(Color(0.7, 0.7, 0.7))
                c.setLineWidth(0.5)
                separator_y = draw_y - 15
                try:
                    c.line(x0, separator_y, x1, separator_y)
                finally:
                    c.restoreState()

            if i == 1 and key in {
                "self_supply_rate_percent",
                    "self_consumption_percent"}:
                continue

            if i == 3 and text and "JAHRE SIMULATION" in text and len(
                    pos) == 4:
                c.saveState()
                try:
                    c.setFillColorRGB(1, 1, 1)
                    c.setStrokeColorRGB(1, 1, 1)
                    rect_y = page_height - pos[3] - 2
                    rect_height = pos[3] - pos[1] + 4
                    c.rect(
                        pos[0] - 2,
                        rect_y,
                        (pos[2] - pos[0]) + 4,
                        rect_height,
                        stroke=0,
                        fill=1)
                finally:
                    c.restoreState()

            try:
                raw = (text or "").strip()
                is_footer_num = (
                    not key and raw.isdigit() and int(raw) == i and
                    len(pos) == 4 and (pos[3] >= 780.0) and
                    (pos[0] >= 520.0) and
                    color_int == 0xFFFFFF
                )
            except Exception:
                is_footer_num = False

            if is_footer_num:
                page_num_text = f"Seite {i} von {
                    int(total_pages) if isinstance(
                        total_pages, (int, float)) else total_pages}"
                try:
                    c.drawRightString(x1, draw_y, page_num_text)
                except Exception:
                    c.drawString(draw_x, draw_y, page_num_text)
            else:
                if key in center_keys and len(pos) == 4:
                    try:
                        tw = c.stringWidth(
                            str(draw_text), font_name, font_size)
                        mid_x = (x0 + x1) / 2.0
                        c.drawString(mid_x - tw / 2.0, draw_y, str(draw_text))
                    except Exception:
                        c.drawString(draw_x, draw_y, str(draw_text))
                elif i == 1 and (text in right_align_tokens_s1) and len(pos) == 4:
                    # Seite 1: Rechtsbündig für dynamische Werte, 17 Punkte
                    # nach rechts verschoben
                    try:
                        c.drawRightString(x1 + 17, draw_y, str(draw_text))
                    except Exception:
                        c.drawString(draw_x, draw_y, str(draw_text))
                elif i == 3 and (text in right_align_tokens_s3) and len(pos) == 4:
                    # Seite 3: Rechtsbündig für Berechnungswerte und
                    # Bedarfsanalyse
                    try:
                        c.drawRightString(x1, draw_y, str(draw_text))
                    except Exception:
                        c.drawString(draw_x, draw_y, str(draw_text))
                else:
                    c.drawString(draw_x, draw_y, str(draw_text))

        if i == 3 and page3_cost_tokens:
            c.saveState()
            try:
                from reportlab.lib.colors import Color as _Color
                dark_blue = _Color(0.07, 0.34, 0.60)
                for dyn_key, meta in page3_cost_tokens.items():
                    pos = meta.get("position")
                    if not (isinstance(pos, tuple) and len(pos) == 4):
                        continue
                    x0, y0, x1, y1 = pos
                    draw_y = page_height - y1
                    val = dynamic_data.get(dyn_key) or meta.get(
                        "original_text") or ""
                    font_name = meta.get("font", "Helvetica-Bold")
                    font_size = float(meta.get("font_size", 10.49))
                    c.setFont(font_name, font_size)
                    bw = c.stringWidth(str(val), font_name, font_size)
                    pad_x = 2.0
                    pad_y = 1.5
                    c.saveState()
                    c.setFillColorRGB(1, 1, 1)
                    c.rect(
                        x0 - pad_x,
                        draw_y - pad_y,
                        bw + 2 * pad_x,
                        font_size + 2 * pad_y,
                        stroke=0,
                        fill=1)
                    c.restoreState()
                    c.setFillColor(colors.black)
                    c.drawString(x0, draw_y, str(val))
            finally:
                c.restoreState()

        # Seite 4: Hersteller-Logos nach den Texten zeichnen (damit sie oben
        # liegen)
        if i == 4:
            try:
                _draw_page4_brand_logos(
                    c, dynamic_data, page_width, page_height)
            except Exception as e:
                print(
                    f"WARN: Fehler beim Zeichnen der Hersteller-Logos Seite4: {e}")

        c.showPage()
    c.save()
    return buffer.getvalue()


def _compact_page6_elements(
        elements: list[dict[str, Any]], dynamic_data: dict[str, str], page_height: float) -> list[dict[str, Any]]:
    """Verdichtet Seite 6 vertikal: Entfernt deaktivierte Dienstleistungszeilen.

    Strategie:
    - Identifiziere Paare (Label + Wert) anhand ihrer Y-Position (Originalkoordinaten in YAML).
    - Ein Paar gehört zur Dienstleistungen-/Produkte-Sektion, wenn BOTH:
        * Text ist Platzhalter (beginnt mit 'X_LBL_' oder 'X_SRV_' oder 'X_PROD_') ODER bereits gemappt wurde
        * Y-Koordinate im Bereich des Dienstleistungsblocks liegt (>= ~190 und <= ~600 in Vorlage)
    - Wenn sowohl Label- als auch Value-Platzhalter leer (dynamic_data liefert "") -> Paar wird entfernt.
    - Übrige Paare werden in Originalreihenfolge neu nach unten versetzt ohne Lücken.
    - Nicht-betroffene Elemente (Header, Footer, Summary, etc.) bleiben unverändert.
    """
    # Bereich in dem Produkt + Dienstleistungszeilen liegen (aus seite6.yml
    # entnommen)
    Y_MIN = 120.0  # etwas großzügiger für Produktzeilen
    Y_MAX = 610.0

    # Hilfsfunktion: Hole Canvas-Y1 (oberer Rand) aus Positionstuple
    def _y_top(pos_tuple):
        if not (isinstance(pos_tuple, tuple) and len(pos_tuple) == 4):
            return None
        # YAML speichert (x0, y0, x1, y1) mit y1 als maxY (unten?) -> In Vorlage: (70, 200, 200, 215)
        # Wir nehmen das obere Ende als y1
        return float(
            pos_tuple[1]) if pos_tuple[1] < pos_tuple[3] else float(
            pos_tuple[3])

    # Sammle Kandidaten in Reihenfolge, wie sie im YAML stehen
    service_rows: list[dict[str, Any]] = []
    other_elements: list[dict[str, Any]] = []

    for el in elements:
        txt = (el.get("text") or "").strip()
        pos = el.get("position")
        y_top = _y_top(pos)
        if y_top is None:
            other_elements.append(el)
            continue
        if Y_MIN <= y_top <= Y_MAX and (txt.startswith(
                "X_LBL_") or txt.startswith("X_SRV_") or txt.startswith("X_PROD_")):
            service_rows.append(el)
        else:
            other_elements.append(el)

    # Gruppiere Zeilenpaare: Label (X_LBL_*) + Wert (X_SRV_* oder X_PROD_*)
    # Vorgehen: Sortiere nach y (aufsteigend) und verarbeite sequentiell
    service_rows_sorted = sorted(
        service_rows, key=lambda e: _y_top(
            e.get("position")) or 0.0)

    compacted: list[dict[str, Any]] = []
    buffer_pair: list[dict[str, Any]] = []

    def _flush_pair(pair: list[dict[str, Any]]):
        for p in pair:
            compacted.append(p)

    for el in service_rows_sorted:
        txt = (el.get("text") or "").strip()
        key = PLACEHOLDER_MAPPING.get(txt)
        dyn_val = dynamic_data.get(key, "") if key else None
        is_label = txt.startswith("X_LBL_")
        is_value = txt.startswith("X_SRV_") or txt.startswith("X_PROD_")

        if is_label:
            # Falls vorheriges Paar unvollständig -> flush
            if buffer_pair:
                _flush_pair(buffer_pair)
                buffer_pair = []
            buffer_pair.append(el)
        elif is_value:
            buffer_pair.append(el)
            # Paar komplett -> entscheiden ob behalten
            lbl_el = buffer_pair[0] if buffer_pair else None
            val_el = buffer_pair[1] if len(buffer_pair) > 1 else None
            # Prüfe dyn Werte: Wenn sowohl Label als auch Value leer ->
            # verwerfen
            lbl_key = PLACEHOLDER_MAPPING.get(
                (lbl_el.get("text") or "").strip()) if lbl_el else None
            lbl_val = dynamic_data.get(lbl_key, "") if lbl_key else ""
            val_key = PLACEHOLDER_MAPPING.get(
                (val_el.get("text") or "").strip()) if val_el else None
            val_val = dynamic_data.get(val_key, "") if val_key else ""
            if lbl_val or val_val:
                _flush_pair(buffer_pair)
            # Else: verwerfen (nicht hinzufügen)
            buffer_pair = []
        else:
            # Unbekannt im service block -> direkt flush bestehendes Pair
            if buffer_pair:
                _flush_pair(buffer_pair)
                buffer_pair = []
            compacted.append(el)

    # Rest flush
    if buffer_pair:
        _flush_pair(buffer_pair)

    # Jetzt vertikal nachrücken: Wir nehmen die ursprüngliche erste
    # Y-Top-Position aller service_rows_sorted
    if not service_rows_sorted:
        return elements

    first_top = min(
        _y_top(
            el.get("position")) for el in service_rows_sorted if _y_top(
            el.get("position")) is not None) or 0.0
    # Zeilenhöhenabschätzung: typischer Abstand zwischen aufeinanderfolgenden Label-Zeilen aus Vorlage
    # Wir lesen Mittelwert der Deltas aus originalen service_rows_sorted
    deltas = []
    prev_y = None
    for el in service_rows_sorted:
        y = _y_top(el.get("position"))
        if prev_y is not None and y is not None:
            deltas.append(abs(y - prev_y))
        prev_y = y
    default_delta = 20.0
    if deltas:
        avg_delta = sum(deltas) / len(deltas)
        # Begrenze den Bereich sinnvoll
        if 10.0 <= avg_delta <= 30.0:
            default_delta = avg_delta

    # Weise neue Positionen zu (Paare hintereinander)
    new_y_top = first_top
    new_elements_map = {id(el): el for el in elements}
    processed_ids = set()
    for el in compacted:
        txt = (el.get("text") or "").strip()
        if not (txt.startswith("X_LBL_") or txt.startswith(
                "X_SRV_") or txt.startswith("X_PROD_")):
            continue
        pos = el.get("position")
        if not (isinstance(pos, tuple) and len(pos) == 4):
            continue
        x0, y0, x1, y1 = pos
        height = abs(y1 - y0)
        # Verschiebe Block sodass obere Kante bei new_y_top liegt
        # Annahme: y0 < y1 (wie in YAML) – belasse Höhe
        new_y0 = new_y_top
        new_y1 = new_y_top + height
        el['position'] = (x0, new_y0, x1, new_y1)
        processed_ids.add(id(el))
        # Nach Value-Zeile erhöhen (wir erkennen Value-Zeile an X_SRV_/X_PROD_
        # und daran, dass vorher Label kam)
        if txt.startswith("X_SRV_") or txt.startswith("X_PROD_"):
            # etwas kompakter als Original
            new_y_top = new_y1 + (default_delta * 0.5)

    # Rekombiniere: Header/Footer/Andere + kompaktierte Service-Elemente
    # Sortiere nach ursprünglicher Reihenfolge (stabil) außer dass verschobene
    # neue Positionen gelten
    final_list = []
    for el in elements:
        final_list.append(el)
    return final_list


def _draw_page3_right_chart_and_separator(c: canvas.Canvas,
                                          elements: list[dict[str,
                                                              Any]],
                                          dynamic_data: dict[str,
                                                             str],
                                          page_width: float,
                                          page_height: float) -> None:
    """Seite 3: Rechts NUR die 20-Jahres-Gesamtergebnisse als Text + vertikale Trennlinie.

    - Linke Diagrammhöhe (aus Tick-Positionen) wird genutzt, um die Text-Vertikalmitte zu bestimmen.
    - Ausgegeben werden: cost_20y_no_increase_number, cost_20y_with_increase_number
    - Trennlinie: fest platziert (template-stabil) rechts neben dem linken Diagramm.
    """
    # Canvas-Zustand sichern, um Farben nicht zu überschreiben
    c.saveState()
    try:
        # 1) Linke Diagramm-Vertikalrange aus den Tick-Elementen entnehmen
        top_label_y1 = None
        bottom_label_y1 = None
        for el in elements:
            t = (el.get("text") or "").strip()
            if t == "25.000" and isinstance(
                    el.get("position"), tuple) and len(
                    el.get("position")) == 4:
                top_label_y1 = el["position"][3]
            if t == "0" and isinstance(
                    el.get("position"), tuple) and len(
                    el.get("position")) == 4:
                bottom_label_y1 = el["position"][3]
        # Fallbacks, falls tokens bereits dynamisch ersetzt wurden und oben
        # nicht gefunden wurden
        if top_label_y1 is None or bottom_label_y1 is None:
            # Suche nach kleinster/größter y1 bei numerischen Tick-Labels im
            # Bereich der linken Achse
            candidates = []
            for el in elements:
                t = (
                    el.get("text") or "").strip().replace(
                    ".",
                    "").replace(
                    ",",
                    ".")
                if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t):
                    pos = el.get("position")
                    if isinstance(pos, tuple) and len(
                            pos) == 4 and pos[0] < 100.0:
                        candidates.append(pos[3])
            if candidates:
                top_label_y1 = min(candidates)
                bottom_label_y1 = max(candidates)
        # Umrechnen in Canvas-Koordinaten
        if top_label_y1 is None or bottom_label_y1 is None:
            # Plausible Defaults aus der Vorlage (aus seite3.yml abgelesen)
            top_label_y1 = 192.7
            bottom_label_y1 = 326.1
        axis_top_y = page_height - float(top_label_y1)
        axis_bottom_y = page_height - float(bottom_label_y1)
        axis_height = max(10.0, axis_top_y - axis_bottom_y)

        # 2) Separator-Linie fest rechts vom linken Diagramm platzieren (template-stabil)
        # Fixe Position hat sich bewährt: ~300 pt liegt rechts neben dem linken
        # Diagramm und lässt genug Platz rechts
        sep_x = 299.0
        c.saveState()
        c.setStrokeColor(int_to_color(0x1B3670))
        c.setLineWidth(0.6)
        # Linie über die Diagrammhöhe ziehen (mit kleiner Überlappung)
        c.line(sep_x, axis_bottom_y - .0, sep_x, axis_top_y + 8.0)
        c.restoreState()

        # 3) Rechte Diagrammfläche definieren – nur ZWEI Balken (Totals 20J)
        chart_left_x = sep_x + 42.0  # weiter nach rechts verschoben
        chart_width = 230.0
        chart_right_x = chart_left_x + chart_width
        y0 = axis_bottom_y
        y1 = axis_top_y
        from reportlab.lib.colors import Color
        axis_color = int_to_color(0xB0B0B0)  # Achse in Hellgrau
        dark_blue = Color(0.07, 0.34, 0.60)
        light_blue = Color(0.63, 0.78, 0.90)

        # Totals aus Platzhaltern holen
        def _parse_money(s: str) -> float:
            try:
                ss = re.sub(
                    r"[^0-9,\.]",
                    "",
                    (s or "")).replace(
                    ".",
                    "").replace(
                    ",",
                    ".")
                return float(ss or 0.0)
            except Exception:
                return 0.0

        v_no_inc_total = _parse_money(
            dynamic_data.get("cost_20y_no_increase_number") or "0")
        v_with_inc_total = _parse_money(
            dynamic_data.get("cost_20y_with_increase_number") or "0")

        # Dynamische Obergrenze bestimmen
        import math
        max_val = max(v_no_inc_total, v_with_inc_total, 0.0)
        if max_val > 0:
            top = math.ceil(max_val / 1000.0) * 1000.0
            if top <= max_val:
                top = max(max_val + 0.02 * max_val, top + 1000.0)
            cap = max_val * 1.2
            if top > cap:
                top = cap
        else:
            top = 25000.0

        # Y-Achse und Ticks + gepunktete Gridlines
        y_axis_x = chart_left_x + 4.0
        c.saveState()
        c.setStrokeColor(axis_color)
        c.setLineWidth(1.0)
        c.line(y_axis_x, y0, y_axis_x, y1)
        try:
            c.setFont("Helvetica", 6.0)
        except Exception:
            c.setFont("Helvetica", 6)
        for i_tick in range(5, -1, -1):
            tv = top * i_tick / 5.0
            py = y0 + (y1 - y0) * (tv / top if top > 0 else 0.0)
            c.setLineWidth(0.6)
            # Tick an der Y-Achse
            c.line(y_axis_x - 3.0, py, y_axis_x, py)
            # Gepunktete horizontale Linie
            c.saveState()
            c.setDash(1, 3)
            c.setStrokeColor(int_to_color(0xC9D4E5))
            c.line(y_axis_x, py, chart_right_x, py)
            c.restoreState()
            lbl = f"{
                tv:,.2f}".replace(
                ",",
                "#").replace(
                ".",
                ",").replace(
                "#",
                ".")
            try:
                tw = c.stringWidth(lbl, "Helvetica", 6.0)
            except Exception:
                tw = c.stringWidth(lbl, "Helvetica", 6)
            c.setFillColor(colors.black)  # Schwarz statt Dunkelblau
            c.drawString(y_axis_x - 6.0 - tw, py - 2.0, lbl)
        c.restoreState()

        # Balken zeichnen
        def _h(val: float) -> float:
            return 0.0 if top <= 0 else (
                max(0.0, min(1.0, val / top)) * (y1 - y0))
        bar_w = 16.0  # halb so breit
        gap = 40.0
        # Balken leicht nach rechts verschieben
        bar_shift = 14.0  # etwas weiter rechts als zuvor
        bar1_x = y_axis_x + 22.0 + bar_shift
        # Zweiter Balken so verschieben, dass der Abstand doppelt so groß ist
        # wie vorher
        bar2_x = bar1_x + bar_w + (2 * gap)
        h1 = _h(v_no_inc_total)
        h2 = _h(v_with_inc_total)
        c.saveState()
        c.setFillColor(light_blue)
        c.rect(bar1_x, y0, bar_w, h1, stroke=0, fill=1)
        c.setFillColor(dark_blue)
        c.rect(bar2_x, y0, bar_w, h2, stroke=0, fill=1)
        c.restoreState()

        # Bodenlinie des Diagramms in Grau (keine obere Linie)
        c.saveState()
        c.setStrokeColor(int_to_color(0xB0B0B0))
        c.setLineWidth(1.0)
        c.line(y_axis_x, y0, chart_right_x, y0)
        c.restoreState()

        # Werte über den Balken anzeigen (als Orientierung)
        try:
            c.setFont("Helvetica-Bold", 10.49)
        except Exception:
            c.setFont("Helvetica-Bold", 10.49)
        c.setFillColor(colors.black)  # Schwarz statt Dunkelblau
        val1 = dynamic_data.get("cost_20y_no_increase_number") or "0,00 €"
        val2 = dynamic_data.get("cost_20y_with_increase_number") or "0,00 €"
        c.drawCentredString(bar1_x + bar_w / 2.0, y0 + h1 + 12.0, val1)
        c.drawCentredString(bar2_x + bar_w / 2.0, y0 + h2 + 12.0, val2)

        # Legende dynamisch aus YAML übernehmen (Texte mit 'strompreis' rechts
        # der Seite)
        legend_x = chart_left_x + 12.0  # Start X für Quadrate
        square_size = 6.0
        label_gap = 4.0

        try:
            c.setFont("Helvetica", 7.98)
        except Exception:
            c.setFont("Helvetica", 8)
        # Kandidaten suchen
        legend_texts: list[str] = []
        for el in elements:
            try:
                pos = el.get("position")
                if not (isinstance(pos, tuple) and len(pos) == 4):
                    continue
                if pos[0] < 300:  # nur rechter Bereich
                    continue
                t = (el.get("text") or "").strip()
                if not t:
                    continue
                if "strompreis" in t.lower():
                    if t not in legend_texts:
                        legend_texts.append(t)
            except Exception:
                continue
        # Fallback auf korrekte Legendentexte falls nichts im YAML gefunden
        if len(legend_texts) < 2:
            # Verwende die korrekten, gewünschten Texte
            legend_texts = ["", ""]
        # Höhen (an bestehende Vorlage angelehnt)
        legend1_base_y = page_height - 356.6169
        legend2_base_y = page_height - 368.60684
        # Text-Position - 2 Pixel nach rechts und 1 Pixel nach oben
        text_offset_x = 2.0
        text_offset_y = 1.0

        # Eintrag 1 (hellblau) - Quadrat an ursprünglicher Position
        c.saveState()
        c.setFillColor(light_blue)
        c.rect(
            legend_x,
            legend1_base_y,
            square_size,
            square_size,
            stroke=0,
            fill=1)
        c.restoreState()
        c.setFillColor(colors.black)  # Schwarz statt Dunkelblau
        c.drawString(
            legend_x +
            square_size +
            label_gap +
            text_offset_x,
            legend1_base_y -
            1.0 +
            text_offset_y,
            legend_texts[0])
        # Eintrag 2 (dunkelblau) - Quadrat an ursprünglicher Position
        c.saveState()
        c.setFillColor(dark_blue)
        c.rect(
            legend_x,
            legend2_base_y,
            square_size,
            square_size,
            stroke=0,
            fill=1)
        c.restoreState()
        c.setFillColor(colors.black)  # Schwarz statt Dunkelblau
        c.drawString(
            legend_x + square_size + label_gap + text_offset_x,
            legend2_base_y - 1.0 + text_offset_y,
            legend_texts[1] if len(legend_texts) > 1 else "")

    finally:
        # Canvas-Zustand wiederherstellen, damit nachfolgende Texte nicht
        # beeinflusst werden
        c.restoreState()


def _draw_page4_component_images(c: canvas.Canvas,
                                 dynamic_data: dict[str,
                                                    str],
                                 page_width: float,
                                 page_height: float) -> None:
    """Zeigt bis zu drei Produktbilder (Module, WR, Speicher) auf Seite 4 an.

    Erwartet Base64 in Keys: module_image_b64, inverter_image_b64, storage_image_b64.
    Positionierung: linke Spalte Bilderblöcke oberhalb/links der jeweiligen Textblöcke,
    sodass die bestehenden Textfelder (aus seite4.yml) nicht überlagert werden.
    """
    try:
        images = [
            (dynamic_data.get("module_image_b64"), {
                "x": 50.0, "y_top": page_height - 250.0, "max_w": 140.0, "max_h": 90.0
            }),
            (dynamic_data.get("inverter_image_b64"), {
                "x": 50.0, "y_top": page_height - 440.0, "max_w": 140.0, "max_h": 90.0
            }),
            (dynamic_data.get("storage_image_b64"), {
                "x": 50.0, "y_top": page_height - 630.0, "max_w": 140.0, "max_h": 90.0
            }),
        ]
        for img_b64, pos in images:
            img = _as_image_reader(img_b64)
            if img is None:
                continue
            max_w = float(pos.get("max_w", 140.0))
            max_h = float(pos.get("max_h", 90.0))
            x = float(pos.get("x", 50.0))
            y_top = float(pos.get("y_top", page_height - 250.0))
            try:
                iw, ih = img.getSize()  # type: ignore
                scale = min(max_w / iw, max_h / ih)
                dw, dh = iw * scale, ih * scale
            except Exception:
                dw, dh = max_w, max_h
            y = y_top - dh
            c.saveState()
            try:
                c.drawImage(
                    img,
                    x,
                    y,
                    width=dw,
                    height=dh,
                    preserveAspectRatio=True,
                    mask='auto')
            finally:
                c.restoreState()
    except Exception:
        return


def _draw_page4_brand_logos(c: canvas.Canvas,
                            dynamic_data: dict[str,
                                               str],
                            page_width: float,
                            page_height: float) -> None:
    """Zeichnet Hersteller-Logos (Module / WR / Speicher) auf Seite 4 rechts neben den Überschriften.

    Verwendet Admin-Setting 'pdf_logo_positions' (Struktur wie DEFAULT_POSITIONS in admin_logo_positions_ui.py):
    {
        "Batteriespeicher": {"x": 520, "y": 180, "width": 60, "height": 30},
        "wechselrichter": {"x": 520, "y": 370, ...},
        "modul": {"x": 520, "y": 560, ...}
    }

    Koordinatensystem (Admin-UI): X links->rechts, Y unten->oben.
    ReportLab Canvas: Ursprung links unten. Deshalb direkte Verwendung möglich.
    """
    try:
        # Logos aus dynamic_data
        logo_keys = {
            "batteriespeicher": "module_brand_logo_b64",
            "wechselrichter": "inverter_brand_logo_b64",
            "modul": "storage_brand_logo_b64",
        }

        # Admin-Positionen laden (Fallback auf Defaults falls Setting fehlt)
        # Die Default-Y Positionen sind Platzhalter, werden aber bei
        # aktivierter Titel-Ausrichtung überschrieben.
        default_positions = {
            "batteriespeicher": {
                "x": 520.0, "y": 180.0, "width": 60.0, "height": 30.0}, "wechselrichter": {
                "x": 520.0, "y": 370.0, "width": 60.0, "height": 30.0}, "modul": {
                "x": 520.0, "y": 560.0, "width": 60.0, "height": 30.0}, }
        try:
            positions = load_admin_setting(
                "pdf_logo_positions",
                default_positions) or default_positions
            if not isinstance(positions, dict):
                positions = default_positions
        except Exception:
            positions = default_positions

        # Debug-Ausgabe der rohen geladenen Admin-Positionen (vor jeglicher
        # Modifikation)
        try:
            print(f"DEBUG LOGO POSITIONS geladen (roh): {positions}")
        except Exception:
            pass

        # Manueller Modus: Admin-Positionen strikt verwenden (kein
        # Titel-Alignment)
        try:
            manual_mode = load_admin_setting("pdf_logo_manual_mode", False)
        except Exception:
            manual_mode = False

        # Titel-Ausrichtung aktiv?
        try:
            align_with_titles = load_admin_setting(
                "pdf_logo_align_with_titles", True) and not manual_mode
        except Exception:
            align_with_titles = not manual_mode

        # Erkennen ob Admin Positionen individuell angepasst wurden (Abweichung
        # von Defaults)
        admin_customized = False
        try:
            for cat, dfl in default_positions.items():
                p = positions.get(cat, {})
                dx = abs(float(p.get("x", dfl["x"])) - dfl["x"])
                dy = abs(float(p.get("y", dfl["y"])) - dfl["y"])
                if dx > 0.01 or dy > 0.01:
                    admin_customized = True
                    break
        except Exception:
            pass

        # Wenn Admin manuell angepasst hat, Alignment aber aktiviert ist, schalten wir Alignment automatisch AUS,
        # außer der Admin erzwingt es explizit mit Setting
        # 'pdf_logo_keep_alignment_when_customized'.
        if admin_customized and not manual_mode:
            try:
                keep_align = load_admin_setting(
                    "pdf_logo_keep_alignment_when_customized", False)
            except Exception:
                keep_align = False
            if align_with_titles and not keep_align:
                align_with_titles = False
                print(
                    "DEBUG LOGO AUTO-DISABLE ALIGN: Admin-Positionen weichen von Defaults ab -> benutze Admin-Y")
            else:
                if align_with_titles:
                    print(
                        "DEBUG LOGO ALIGN trotz Admin-Anpassung aktiv (keep_alignment_when_customized=True)")

        # Optionale vertikale Offsets (in pt) je Kategorie für Feintuning
        try:
            vertical_offsets = load_admin_setting(
                "pdf_logo_vertical_offsets", {}) or {}
            if not isinstance(vertical_offsets, dict):
                vertical_offsets = {}
        except Exception:
            vertical_offsets = {}

        title_y_centers: dict[str, float] = {}
        if align_with_titles:
            # Wir lesen coords/seite4.yml und suchen die Überschriften SOLARMODULE / WECHSELRICHTER / BATTERIESPEICHER.
            # Format:
            # Text: SOLARMODULE\n
            # Position: (x1, y1, x2, y2)
            import os
            import re
            coords_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(__file__)),
                "coords",
                "seite4.yml")
            try:
                with open(coords_path, encoding="utf-8") as fh:
                    lines = fh.readlines()
                current_text = None
                pattern = re.compile(r"Position:\s*\(([^)]*)\)")
                for line in lines:
                    if line.startswith("Text:"):
                        current_text = line.split("Text:", 1)[1].strip()
                    elif line.startswith("Position:") and current_text:
                        m = pattern.search(line)
                        if m:
                            parts = [
                                p.strip() for p in m.group(1).split(",") if p.strip()]
                            if len(parts) == 4:
                                try:
                                    _, y1, _, y2 = [float(p) for p in parts]
                                    y_center = (y1 + y2) / 2.0
                                    key_map = {
                                        "SOLARMODULE": "modul",
                                        "WECHSELRICHTER": "wechselrichter",
                                        "BATTERIESPEICHER": "batteriespeicher",
                                    }
                                    cat = key_map.get(current_text)
                                    if cat and cat not in title_y_centers:
                                        title_y_centers[cat] = y_center
                                except Exception:
                                    pass
                        current_text = None
            except Exception as e:
                print(f"DEBUG LOGO ALIGN Titles Laden Fehler: {e}")

        # Wenn wir valide y-Center haben, überschreiben wir die Y-Werte (nur
        # vertikal) der Position-Boxen
        if align_with_titles and title_y_centers:
            # Optional benutzerdefinierte Reihenfolge (z.B.
            # ['modul','wechselrichter','batteriespeicher'])
            try:
                custom_order = load_admin_setting(
                    "pdf_logo_custom_order", []) or []
                if not custom_order:
                    # Fallback harte Wunsch-Reihenfolge
                    custom_order = [
                        "modul", "wechselrichter", "batteriespeicher"]
                if not isinstance(custom_order, list):
                    custom_order = []
            except Exception:
                custom_order = ["modul", "wechselrichter", "batteriespeicher"]

            # Falls custom_order gesetzt ist und alle Kategorien enthält,
            # verteilen wir die Y-Center gemäß Sortierung (oben->unten) nach
            # den vorhandenen Y-Werten sortiert.
            if len(custom_order) == 3 and set(
                    custom_order) == set(title_y_centers.keys()):
                # Sortiere existierende Zentren nach Y (aufsteigend) ->
                # unterste zuerst
                centers_sorted = sorted(
                    title_y_centers.items(), key=lambda kv: kv[1])
                # Weisen von unten nach oben den gewünschten Kategorien ihre Ziel-Y zu.
                # Ziel: custom_order[0] soll ganz oben, also größtes Y
                # bekommen.
                mapping: dict[str, float] = {}
                # centers_sorted: lowest .. highest
                only_y = [c for _, c in centers_sorted]
                only_y_sorted_desc = sorted(only_y, reverse=True)
                for idx, cat in enumerate(custom_order):
                    if idx < len(only_y_sorted_desc):
                        mapping[cat] = only_y_sorted_desc[idx]
                # Ersetze title_y_centers durch mapping (nur wo zugewiesen)
                for cat, new_center in mapping.items():
                    title_y_centers[cat] = new_center
                print(f"DEBUG LOGO CUSTOM ORDER aktiv – mapping: {mapping}")

            for cat, y_center in title_y_centers.items():
                pos = positions.get(cat, {})
                box_h = float(
                    pos.get(
                        "height",
                        default_positions[cat]["height"]))
                offset = float(vertical_offsets.get(cat, 0.0))
                new_y_bottom = max(0.0, y_center - box_h / 2.0 + offset)
                pos["y"] = new_y_bottom
                positions[cat] = pos
            print(
                f"DEBUG LOGO ALIGN aktiv – Titel-Zentren genutzt: {title_y_centers}")
        else:
            if align_with_titles:
                print(
                    "DEBUG LOGO ALIGN keine Titel-Zentren gefunden – Fallback auf Admin/Default-Y")
            if manual_mode:
                print(
                    "DEBUG LOGO MANUAL MODE aktiv – verwende reine Admin-Positionen ohne Alignment")

        # Zeichnen
        for category, key in logo_keys.items():
            b64 = dynamic_data.get(key)
            if not b64:
                continue
            img = _as_image_reader(b64)
            if img is None:
                continue
            pos = positions.get(category, {})
            x = float(pos.get("x", default_positions[category]["x"]))
            y_bottom = float(pos.get("y", default_positions[category]["y"]))
            box_w = float(
                pos.get(
                    "width",
                    default_positions[category]["width"]))
            box_h = float(
                pos.get(
                    "height",
                    default_positions[category]["height"]))

            # Optional: 2cm vom rechten Rand erzwingen falls Admin-x sehr weit links (< rechte Rand - 2cm)
            # 2 cm ≈ 56.7 pt. Rechter Rand (A4 width ~595). Ziel-x = 595 - 56.7
            # - box_w
            try:
                enforce_margin = load_admin_setting(
                    "pdf_logo_right_margin_enforce", True)
            except Exception:
                enforce_margin = True
            if enforce_margin:
                right_margin_cm = 2.0
                right_margin_pt = right_margin_cm * 28.3465
                desired_x = page_width - right_margin_pt - box_w
                if x > desired_x + 40 or x < desired_x - \
                        120:  # Falls Admin versehentlich zu weit rechts (überlappt Rand), korrigieren
                    x = desired_x

            # Bildgröße an Box anpassen (Aspect Ratio beibehalten)
            try:
                iw, ih = img.getSize()  # type: ignore
                scale = min(box_w / iw, box_h / ih)
                dw, dh = iw * scale, ih * scale
            except Exception:
                dw, dh = box_w, box_h
            # Vertikal mittig innerhalb Box (Admin y = untere Kante)
            y = y_bottom
            if dh < box_h:
                y = y_bottom + (box_h - dh) / 2.0

            c.saveState()
            try:
                c.drawImage(
                    img,
                    x,
                    y,
                    width=dw,
                    height=dh,
                    preserveAspectRatio=True,
                    mask='auto')
                print(
                    f"DEBUG LOGO DRAW {category}: x={
                        x:.1f}, y={
                        y:.1f}, w={
                        dw:.1f}, h={
                        dh:.1f}")
            except Exception as e:
                print(f"Fehler beim Zeichnen Logo {category}: {e}")
            finally:
                c.restoreState()
    except Exception as e:
        print(f"Fehler _draw_page4_brand_logos: {e}")


def _remove_text_from_page(page, texts_to_remove: list[str]):
    """Entfernt spezifische Texte aus dem Content-Stream einer PDF-Seite."""
    try:
        if not hasattr(page, 'get_contents') or not texts_to_remove:
            return

        content = page.get_contents()
        if content is None:
            return

        # Content-Stream als String laden
        if hasattr(content, 'get_data'):
            content_data = content.get_data()
        else:
            content_data = content.read()

        if isinstance(content_data, bytes):
            try:
                content_str = content_data.decode('latin-1', errors='ignore')
            except Exception:
                return
        else:
            content_str = str(content_data)

        # Jeden zu entfernenden Text suchen und entfernen
        modified = False
        for text_to_remove in texts_to_remove:
            # Verschiedene PDF-Text-Encoding-Muster versuchen
            patterns = [
                f"({text_to_remove})Tj",
                f"({text_to_remove}) Tj",
                f"[{text_to_remove}]TJ",
                f"[{text_to_remove}] TJ",
            ]

            for pattern in patterns:
                if pattern in content_str:
                    # Text durch Leerzeichen ersetzen (gleiche Länge
                    # beibehalten)
                    replacement = "(" + " " * len(text_to_remove) + ")Tj"
                    content_str = content_str.replace(pattern, replacement)
                    modified = True

        if modified:
            # Modifizierten Content zurückschreiben
            new_content = io.BytesIO(
                content_str.encode(
                    'latin-1', errors='ignore'))
            if hasattr(page, '_contents'):
                page._contents = new_content

    except Exception:
        pass  # Bei Fehlern einfach ignorieren


def merge_with_background(overlay_bytes: bytes, bg_dir: Path) -> bytes:
    """Verschmilzt das Overlay mit nt_nt_01.pdf … nt_nt_07.pdf aus bg_dir."""
    overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
    writer = PdfWriter()
    for page_num in range(1, 8):
        # Unterstütze beide Muster: nt_nt_XX.pdf und nt_XX.pdf
        candidates = [
            bg_dir /
            f"nt_nt_{
                page_num:02d}.pdf",
            bg_dir /
            f"nt_{
                page_num:02d}.pdf"]
        bg_page = None
        for cand in candidates:
            if cand.exists():
                try:
                    bg_reader = PdfReader(str(cand))
                    bg_page = bg_reader.pages[0]
                    break
                except Exception:
                    continue
        # Fallback: Wenn kein Hintergrund vorhanden/lesbar ist, füge nur
        # Overlay-Seite ein
        ov_page = overlay_reader.pages[page_num - 1]

        # Optional: Auf Seite 1 zusätzlich eine weitere statische PDF (haus.pdf) mergen
        # Reihenfolge: Basis (nt_nt_01.pdf) -> haus.pdf -> Overlay
        extra_bg_page = None
        if page_num == 1:
            haus_path = bg_dir / "haus.pdf"
            if haus_path.exists():
                try:
                    haus_reader = PdfReader(str(haus_path))
                    extra_bg_page = haus_reader.pages[0]
                except Exception:
                    extra_bg_page = None

        # Falls kein Standard-Hintergrund vorhanden ist, aber haus.pdf
        # existiert, nutze diese als Basis
        base_page = bg_page
        if base_page is None and extra_bg_page is not None:
            base_page = extra_bg_page
            extra_bg_page = None  # bereits als Basis gesetzt

        if base_page is not None:
            # Seite 3: Problematische Legendentexte aus dem Hintergrund
            # entfernen
            if page_num == 3:
                texts_to_remove = [
                    "",
                    "",
                    "",
                    "",
                    ""
                ]
                _remove_text_from_page(base_page, texts_to_remove)

            # Falls eine zusätzliche Haus-Seite vorhanden ist, zuerst darüber
            # legen (skaliert 30% und zentriert)
            if extra_bg_page is not None:
                try:
                    bw = float(base_page.mediabox.width)
                    bh = float(base_page.mediabox.height)
                    hw = float(extra_bg_page.mediabox.width)
                    hh = float(extra_bg_page.mediabox.height)
                    scale = 0.3  # 70% kleiner
                    tx = (bw - hw * scale) / 2.0
                    ty = (bh - hh * scale) / 2.0
                    t = Transformation().scale(scale, scale).translate(tx, ty)
                    base_page.merge_transformed_page(extra_bg_page, t)
                except Exception:
                    # Fallback: unskaliert mergen
                    try:
                        base_page.merge_page(extra_bg_page)
                    except Exception:
                        pass
            # WICHTIG: Erstelle eine Kopie der base_page vor dem Merge
            from copy import deepcopy
            merged_page = deepcopy(base_page)

            # Overlay über den zusammengesetzten Hintergrund legen
            merged_page.merge_page(ov_page)
            writer.add_page(merged_page)
        else:
            # Kein Standard-Hintergrund: nur haus.pdf (falls vorhanden) als
            # Basis, skaliert, dann Overlay
            if extra_bg_page is not None and PageObject is not None:
                try:
                    # Erzeuge leere Basis-Seite in A4 (oder Größe des Overlay)
                    try:
                        bw = float(ov_page.mediabox.width)
                        bh = float(ov_page.mediabox.height)
                    except Exception:
                        bw, bh = A4
                    base = PageObject.create_blank_page(
                        width=bw, height=bh)  # type: ignore
                    hw = float(extra_bg_page.mediabox.width)
                    hh = float(extra_bg_page.mediabox.height)
                    scale = 0.3
                    tx = (bw - hw * scale) / 2.0
                    ty = (bh - hh * scale) / 2.0
                    t = Transformation().scale(scale, scale).translate(tx, ty)
                    base.merge_transformed_page(extra_bg_page, t)
                    # WICHTIG: Erstelle Kopie vor Overlay-Merge
                    from copy import deepcopy
                    merged_base = deepcopy(base)
                    merged_base.merge_page(ov_page)
                    writer.add_page(merged_base)
                    continue
                except Exception:
                    pass
            # Fallback: nur Overlay
            writer.add_page(ov_page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def append_additional_pages(base_pdf: bytes,
                            additional_pdf: bytes | None) -> bytes:
    """Hängt optional weitere Seiten hinten an."""
    if not additional_pdf:
        return base_pdf
    base_reader = PdfReader(io.BytesIO(base_pdf))
    add_reader = PdfReader(io.BytesIO(additional_pdf))
    writer = PdfWriter()
    for p in base_reader.pages:
        writer.add_page(p)
    for p in add_reader.pages:
        writer.add_page(p)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def generate_custom_offer_pdf(
    coords_dir: Path,
    bg_dir: Path,
    dynamic_data: dict[str, str],
    additional_pdf: bytes | None = None,
) -> bytes:
    """End-to-End-Erzeugung des Angebots: Overlay -> Merge -> Optional anhängen."""
    # Bestimme Gesamtseiten für Fußzeile (7 + ggf. Zusatzseiten)
    total_pages = 7
    if additional_pdf:
        try:
            add_reader = PdfReader(io.BytesIO(additional_pdf))
            total_pages = 7 + len(add_reader.pages)
        except Exception:
            total_pages = 7
