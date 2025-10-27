"""
pdf_template_engine/dynamic_overlay.py

Erzeugt Text-Overlays für acht statische Template-Seiten anhand von Koordinaten
aus coords/seite1.yml … seite8.yml und verschmilzt sie mit den Dateien
pdf_templates_static/notext/nt_nt_01.pdf … nt_nt_08.pdf.
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
            if raw.startswith(b"<?xml") or raw.startswith(b"<svg"):
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
    c: canvas.Canvas, page_width: float, page_height: float
) -> None:
    """Zeichnet optional ein globales Wasserzeichen (aus Admin-Settings) diagonal über die Seite."""
    enabled = _to_bool(load_admin_setting("pdf_global_watermark_enabled", False), False)
    if not enabled:
        return
    text = (
        load_admin_setting("pdf_global_watermark_text", "VERTRAULICH") or "VERTRAULICH"
    )
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
            if (
                line.startswith("---") or (set(line) == {"-"} and len(line) >= 3)
            ) and current:
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
            elif line.lower().startswith("schriftgröße:") or line.lower().startswith(
                "schriftgroesse:"
            ):
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


def _draw_company_logo(
    c: canvas.Canvas,
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
    page_index: int | None = None,
) -> None:
    """Zeichnet das Firmenlogo links oben, wenn company_logo_b64 vorhanden ist."""
    b64 = dynamic_data.get("company_logo_b64") or ""
    if not b64:
        return
    try:
        img_bytes = base64.b64decode(b64)
        img = ImageReader(io.BytesIO(img_bytes))
        # Zielfläche: max Breite/Höhe
        is_first_page = page_index == 1
        max_w, max_h = (200, 85) if is_first_page else (120, 50)  # Punkte
        c.saveState()
        # Hintergrund-Logo-Bereich abdecken (weißes Rechteck), um falsche Logos
        # aus Templates zu maskieren
        try:
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(1, 1, 1)
            c.rect(
                15,
                page_height - 20 - max_h - 5,
                max_w + 20,
                max_h + 10,
                stroke=0,
                fill=1,
            )
        except Exception:
            pass
        if is_first_page:
            # Spezialposition: rechts oben, 50 pt vom oberen Rand, 10 pt vom
            # rechten Rand
            offset_top = 50.0 + 60.0  # zusätzlicher Versatz nach unten
            offset_right = 10.0
            x = page_width - offset_right - max_w
            y = page_height - offset_top - max_h
            c.drawImage(
                img,
                x,
                y,
                width=max_w,
                height=max_h,
                preserveAspectRatio=True,
                mask="auto",
            )
        else:
            c.drawImage(
                img,
                20,
                page_height - 20 - max_h,
                width=max_w,
                height=max_h,
                preserveAspectRatio=True,
                mask="auto",
            )
        c.restoreState()
    except Exception:
        return


def _parse_percent(value: str | float | int) -> float:
    try:
        if isinstance(value, (int, float)):
            return max(0.0, min(100.0, float(value)))
        s = str(value).strip().replace("%", "").replace(",", ".").replace(" ", "")
        return max(0.0, min(100.0, float(s)))
    except Exception:
        return 0.0


def _first_valid_percent(dynamic_data: dict[str, str], keys: list[str]) -> float:
    for k in keys:
        if k in dynamic_data and dynamic_data.get(k) not in (None, ""):
            v = _parse_percent(dynamic_data.get(k))
            print(
                f"DEBUG: _first_valid_percent - Key: {k}, Value: {dynamic_data.get(k)}, Parsed: {v}"
            )
            if v > 0:
                return v
    print(
        f"DEBUG: _first_valid_percent - Keine gültigen Werte gefunden für Keys: {keys}"
    )
    return 0.0


def _draw_donut(
    c: canvas.Canvas,
    cx: float,
    cy: float,
    pct: float,
    outer_r: float,
    inner_r: float,
    color_fg: Color,
    color_bg: Color,
) -> None:
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
            fill=1,
        )
    except Exception:
        pass
    # Loch stanzen
    c.setFillColor(white)
    c.circle(cx, cy, inner_r, stroke=0, fill=1)
    c.restoreState()


def _draw_page1_new_content(
    c: canvas.Canvas,
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
) -> None:
    """Zeichnet Inhalte für die neue Seite 1.

    TODO: Implementierung der neuen Seite 1 Inhalte.
    Diese Funktion ist ein Platzhalter für zukünftige Inhalte auf der neuen ersten Seite.
    Aktuell wird nur die Seite vorbereitet, aber keine spezifischen Inhalte gezeichnet.

    Args:
        c: ReportLab Canvas-Objekt
        dynamic_data: Dictionary mit dynamischen Daten für die PDF-Generierung
        page_width: Breite der Seite in Punkten
        page_height: Höhe der Seite in Punkten
    """
    # Platzhalter-Implementierung - keine Inhalte werden aktuell gezeichnet
    # Zukünftige Implementierung kann hier Grafiken, Text oder andere Elemente
    # hinzufügen


# OLD: page 3 -> NEW: page 4


def _draw_page4_waterfall_chart(
    c: canvas.Canvas,
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
) -> None:
    """Zeichnet ein Wasserfall-Diagramm auf Seite 4 mit den Berechnungsergebnissen.

    Positionierung basierend auf den exakten Koordinaten aus seite4.yml:
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
                    dynamic_data.keys())}"
        )

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
                clean_value = str(value).replace("€", "").replace(" ", "").strip()

                # Bestimme das Format basierend auf der Struktur
                if "," in clean_value and "." in clean_value:
                    # Deutsches Format: 1.503,32 (Punkt als Tausender, Komma als Dezimal)
                    # Finde die Position von Komma und Punkt
                    comma_pos = clean_value.rfind(",")
                    dot_pos = clean_value.rfind(".")

                    if comma_pos > dot_pos:
                        # Deutsches Format: 1.503,32
                        integer_part = clean_value[:comma_pos].replace(".", "")
                        decimal_part = clean_value[comma_pos + 1 :]
                        clean_value = f"{integer_part}.{decimal_part}"
                    else:
                        # Englisches Format: 1,503.32
                        integer_part = clean_value[:dot_pos].replace(",", "")
                        decimal_part = clean_value[dot_pos + 1 :]
                        clean_value = f"{integer_part}.{decimal_part}"

                elif "," in clean_value:
                    # Nur Komma vorhanden
                    # Prüfe ob es Dezimaltrennzeichen oder
                    # Tausendertrennzeichen ist
                    comma_pos = clean_value.rfind(",")
                    after_comma = clean_value[comma_pos + 1 :]

                    if len(after_comma) <= 2 and after_comma.isdigit():
                        # Wahrscheinlich Dezimaltrennzeichen: 1503,32
                        clean_value = clean_value.replace(",", ".")
                    else:
                        # Wahrscheinlich Tausendertrennzeichen: 1,503
                        clean_value = clean_value.replace(",", "")

                elif "." in clean_value:
                    # Nur Punkt vorhanden
                    dot_pos = clean_value.rfind(".")
                    after_dot = clean_value[dot_pos + 1 :]

                    if len(after_dot) <= 2 and after_dot.isdigit():
                        # Wahrscheinlich Dezimaltrennzeichen: 1503.32
                        pass  # Bereits korrekt
                    else:
                        # Wahrscheinlich Tausendertrennzeichen: 1.503
                        clean_value = clean_value.replace(".", "")

                return float(clean_value)
            except Exception as e:
                print(f"DEBUG: Fehler bei Konvertierung von '{value}': {e}")
                return 0.0

        # Direktverbrauch - KORREKTE Keys basierend auf placeholders.py
        # "Direkt": "self_consumption_without_battery_eur"
        direkt_keys = [
            "self_consumption_without_battery_eur",  # Hauptkey aus placeholders.py
            "direct_consumption_savings_eur",
            "einsparung_direktverbrauch_eur",
            "direktverbrauch_einsparung_eur",
        ]

        for key in direkt_keys:
            if key in dynamic_data and dynamic_data[key] not in (None, "", "0", 0):
                direkt_eur = safe_float_convert(dynamic_data[key])
                print(
                    f"DEBUG: Direktverbrauch gefunden - Key: {key}, Wert: {
                        dynamic_data[key]} -> {direkt_eur}€"
                )
                break

        # Einspeisevergütung - KORREKTE Keys basierend auf placeholders.py
        # "Einspeisung": "annual_feed_in_revenue_eur"
        einspeisung_keys = [
            "annual_feed_in_revenue_eur",  # Hauptkey aus placeholders.py
            "direct_grid_feed_in_eur",  # Alias aus placeholders.py
            "feed_in_revenue_eur",
            "einnahmen_einspeisung_eur",
        ]

        for key in einspeisung_keys:
            if key in dynamic_data and dynamic_data[key] not in (None, "", "0", 0):
                einspeisung_eur = safe_float_convert(dynamic_data[key])
                print(
                    f"DEBUG: Einspeisevergütung gefunden - Key: {key}, Wert: {
                        dynamic_data[key]} -> {einspeisung_eur}€"
                )
                break

        # Steuervorteile - KORREKTE Keys basierend auf placeholders.py
        # "platz1": "tax_benefits_eur"  # Steuerliche Vorteile
        steuer_keys = [
            "tax_benefits_eur",  # Hauptkey aus placeholders.py
            "steuerliche_vorteile_eur",
            "vorteile_steuerfrei_eur",
            "steuervorteile_eur",
        ]

        for key in steuer_keys:
            if key in dynamic_data and dynamic_data[key] not in (None, "", "0", 0):
                steuer_eur = safe_float_convert(dynamic_data[key])
                print(
                    f"DEBUG: Steuervorteile gefunden - Key: {key}, Wert: {
                        dynamic_data[key]} -> {steuer_eur}€"
                )
                break

        # Gesamt - KORREKTE Keys basierend auf placeholders.py
        # "Gesamt": "total_annual_savings_eur"
        gesamt_keys = [
            "total_annual_savings_eur",  # Hauptkey aus placeholders.py
            "gesamt_ertraege_jahr_eur",
            "annual_total_benefits_eur",
            "total_benefits_eur",
        ]

        for key in gesamt_keys:
            if key in dynamic_data and dynamic_data[key] not in (None, "", "0", 0):
                gesamt_eur = safe_float_convert(dynamic_data[key])
                print(
                    f"DEBUG: Gesamt gefunden - Key: {key}, Wert: {dynamic_data[key]} -> {gesamt_eur}€"
                )
                break

        # Falls Gesamt nicht direkt verfügbar, berechne es
        if gesamt_eur <= 0:
            gesamt_eur = direkt_eur + einspeisung_eur + steuer_eur

        print(
            f"DEBUG: Wasserfall-Werte - Direkt: {direkt_eur}€, Einspeisung: {einspeisung_eur}€, Steuer: {steuer_eur}€, Gesamt: {gesamt_eur}€"
        )

        # Nur Fallback verwenden wenn wirklich ALLE Werte fehlen
        if (
            direkt_eur <= 0
            and einspeisung_eur <= 0
            and steuer_eur <= 0
            and gesamt_eur <= 0
        ):
            print("DEBUG: Keine Wasserfall-Werte vorhanden - verwende Demo-Werte")
            direkt_eur = 1200.0
            einspeisung_eur = 800.0
            steuer_eur = 300.0
            gesamt_eur = 2300.0
        else:
            print(
                f"DEBUG: Verwende echte Wasserfall-Werte - Direkt: {direkt_eur}€, Einspeisung: {einspeisung_eur}€, Steuer: {steuer_eur}€, Gesamt: {gesamt_eur}€"
            )

    except Exception as e:
        print(f"DEBUG: Fehler beim Extrahieren der Wasserfall-Werte: {e}")
        # Nur bei echtem Fehler Fallback verwenden
        direkt_eur = 0.0
        einspeisung_eur = 0.0
        steuer_eur = 0.0
        gesamt_eur = 0.0

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
        f"DEBUG: Wasserfall-Chart EXAKTE Position - Links: {chart_left}, Rechts: {chart_right}, Oben: {chart_top}, Unten: {chart_bottom}"
    )
    print(
        f"DEBUG: Chart-Dimensionen - Breite: {chart_width:.1f}, Höhe: {chart_height:.1f}"
    )

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
    text_color = Color(0.2, 0.2, 0.2)  # Dunkelgrau für Text
    line_color = Color(0.4, 0.4, 0.4)  # Grau für Verbindungslinien

    # Daten für das Wasserfall-Diagramm
    values = [direkt_eur, einspeisung_eur, steuer_eur]
    labels = [
        "Einsparung durch\nDirektverbrauch",
        "Einnahmen aus\nEinspeisevergütung",
        "Vorteile durch\nsteuerfreie Einspeisung",
    ]

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
        zip(values, labels, bar_colors[:3], strict=False)
    ):
        # WICHTIG: Zeige alle Balken an, auch wenn Wert 0 ist (für bessere
        # Visualisierung)
        if value < 0:  # Nur negative Werte überspringen
            continue

        # Balken-Position
        bar_x = (
            chart_left + (i + 0.5) * individual_bar_spacing - individual_bar_width / 2
        )

        # Mindesthöhe für Balken mit Wert 0 (für bessere Sichtbarkeit)
        if value <= 0:
            bar_height = 5.0  # Minimale Höhe für 0-Werte
        else:
            bar_height = (
                (value / max_value) * chart_height * 0.75
            )  # 75% der verfügbaren Höhe nutzen

        bar_y = chart_bottom + cumulative_height

        # Zeichne Balken (auch für 0-Werte)
        c.setFillColor(color)
        c.rect(bar_x, bar_y, individual_bar_width, bar_height, stroke=0, fill=1)

        # Speichere Position für Verbindungslinien
        bar_positions.append(
            {
                "x": bar_x + individual_bar_width / 2,
                "y_bottom": bar_y,
                "y_top": bar_y + bar_height,
                "value": value,
            }
        )

        # Wert über dem Balken (auch für 0-Werte anzeigen)
        c.setFillColor(text_color)
        c.setFont("Helvetica-Bold", 7)
        if value <= 0:
            value_text = "0 €"
        else:
            value_text = f"{value:,.0f} €".replace(",", ".")
        text_width = c.stringWidth(value_text, "Helvetica-Bold", 7)
        c.drawString(
            bar_x + (individual_bar_width - text_width) / 2,
            bar_y + bar_height + 3,
            value_text,
        )

        # Label unter dem Balken (mehrzeilig)
        c.setFont("Helvetica", 6)
        label_lines = label.split("\n")
        for j, line in enumerate(label_lines):
            line_width = c.stringWidth(line, "Helvetica", 6)
            c.drawString(
                bar_x + (individual_bar_width - line_width) / 2,
                bar_y - 12 - (j * 8),
                line,
            )

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
                                bar_height:.1f}, Wert={value}€"
        )

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
            current_pos["x"] + individual_bar_width / 4,
            current_pos["y_top"],
            next_pos["x"] - individual_bar_width / 4,
            next_pos["y_bottom"],
        )

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
        total_bar_x, total_bar_y, total_bar_width, total_bar_height, stroke=0, fill=1
    )

    # Wert über dem Gesamtbalken
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 8)
    total_text = f"{gesamt_eur:,.0f} €".replace(",", ".")
    total_text_width = c.stringWidth(total_text, "Helvetica-Bold", 8)
    c.drawString(
        total_bar_x + (total_bar_width - total_text_width) / 2,
        total_bar_y + total_bar_height + 3,
        total_text,
    )

    # Label unter dem Gesamtbalken
    c.setFont("Helvetica-Bold", 7)
    total_label = "Gesamt Erträge\npro Jahr"
    total_label_lines = total_label.split("\n")
    for j, line in enumerate(total_label_lines):
        line_width = c.stringWidth(line, "Helvetica-Bold", 7)
        c.drawString(
            total_bar_x + (total_bar_width - line_width) / 2,
            total_bar_y - 12 - (j * 9),
            line,
        )

    # Verbindungslinie vom letzten Einzelbalken zum Gesamtbalken
    if bar_positions:
        last_pos = bar_positions[-1]
        c.setStrokeColor(line_color)
        try:
            c.setDash([2, 2])  # Gestrichelte Linie
        except AttributeError:
            pass  # Fallback auf durchgezogene Linie
        c.line(
            last_pos["x"] + individual_bar_width / 4,
            last_pos["y_top"],
            total_bar_x - 5,
            total_bar_y + total_bar_height,
        )

    print(
        f"DEBUG: Gesamtbalken: X={
            total_bar_x:.1f}, Y={
            total_bar_y:.1f}, Breite={
                total_bar_width:.1f}, Höhe={
                    total_bar_height:.1f}, Wert={gesamt_eur}€"
    )

    c.restoreState()


# OLD: page 1 -> NEW: page 2
def _draw_page2_test_donuts(
    c: canvas.Canvas,
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
) -> None:
    """Zeichnet Test-Donut-Diagramme auf Seite 2 links unten zum Testen der Sichtbarkeit."""
    # Werte aus dynamic_data ziehen
    pct_consumption = _first_valid_percent(
        dynamic_data,
        [
            "storage_consumption_ratio_percent",
        ],
    )
    pct_production = _first_valid_percent(
        dynamic_data,
        [
            "storage_production_ratio_percent",
        ],
    )

    print(
        f"DEBUG: Seite 2 Test-Donut-Charts - Consumption: {pct_consumption}%, Production: {pct_production}%"
    )

    if pct_consumption <= 0 and pct_production <= 0:
        print("DEBUG: Keine Test-Donut-Charts gezeichnet - beide Werte <= 0")
        return

    c.saveState()

    # SEHR SICHTBARE Position auf Seite 2 links unten
    # Unterhalb von "TECHNISCHE SPEZIFIKATIONEN" (Y=522) und links von
    # "Photovoltaik Module" (X=394)

    # Berechne Y-Positionen (Canvas Y = page_height - YAML Y)
    tech_specs_y = 522  # Y-Position von "TECHNISCHE SPEZIFIKATIONEN"

    # Position unterhalb der technischen Spezifikationen
    consumption_cy = page_height - (tech_specs_y + 50)  # 50 Punkte unterhalb
    production_cy = page_height - (tech_specs_y + 100)  # 100 Punkte unterhalb

    # X-Position: Links, aber sichtbar
    chart_cx = 150.0  # Links von "Photovoltaik Module" (X=394)

    print(
        f"DEBUG: Test-Chart-Positionen - Consumption: ({chart_cx}, {consumption_cy}), Production: ({chart_cx}, {production_cy})"
    )
    print(f"DEBUG: Seitengröße: {page_width} x {page_height}")

    outer_r = 40.0  # GROßE Charts für maximale Sichtbarkeit
    inner_r = 25.0

    # SEHR SICHTBARE Farben
    from reportlab.lib.colors import Color

    bg = Color(0.9, 0.9, 0.9)  # Hellgrau Hintergrund
    # REINES ROT für maximale Sichtbarkeit
    fg_consumption = Color(1.0, 0.0, 0.0)
    # REINES BLAU für maximale Sichtbarkeit
    fg_production = Color(0.0, 0.0, 1.0)

    # Oberer Donut: Speicher zu Tagesverbrauch
    if pct_consumption > 0:
        print(
            f"DEBUG: Zeichne Test-Consumption Donut bei ({chart_cx}, {consumption_cy}) mit {pct_consumption}%"
        )
        _draw_donut(
            c,
            chart_cx,
            consumption_cy,
            pct_consumption,
            outer_r,
            inner_r,
            fg_consumption,
            bg,
        )
        # Zentrumstext
        txt = f"{int(round(pct_consumption))}%"
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(fg_consumption)
        tw = c.stringWidth(txt, "Helvetica-Bold", 12)
        c.drawString(chart_cx - tw / 2, consumption_cy - 6, txt)

        # Label rechts vom Chart
        label_txt = "Test: Tagesverbrauch"
        c.setFont("Helvetica-Bold", 10)
        # Schwarz für maximale Sichtbarkeit
        c.setFillColor(Color(0.0, 0.0, 0.0))
        c.drawString(chart_cx + outer_r + 15, consumption_cy - 5, label_txt)

    # Unterer Donut: Speicher zu PV-Produktion
    if pct_production > 0:
        print(
            f"DEBUG: Zeichne Test-Production Donut bei ({chart_cx}, {production_cy}) mit {pct_production}%"
        )
        _draw_donut(
            c,
            chart_cx,
            production_cy,
            pct_production,
            outer_r,
            inner_r,
            fg_production,
            bg,
        )
        # Zentrumstext
        txt = f"{int(round(pct_production))}%"
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(fg_production)
        tw = c.stringWidth(txt, "Helvetica-Bold", 12)
        c.drawString(chart_cx - tw / 2, production_cy - 6, txt)

        # Label rechts vom Chart
        label_txt = "Test: PV-Produktion"
        c.setFont("Helvetica-Bold", 10)
        # Schwarz für maximale Sichtbarkeit
        c.setFillColor(Color(0.0, 0.0, 0.0))
        c.drawString(chart_cx + outer_r + 15, production_cy - 5, label_txt)

    c.restoreState()


# OLD: page 6 -> NEW: page 7
def _draw_page7_storage_donuts_fixed(
    c: canvas.Canvas,
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
) -> None:
    """Zeichnet Donut-Diagramme für Speicher-Relationen auf Seite 7 mit verbesserter Sichtbarkeit."""
    # Werte aus dynamic_data ziehen
    pct_consumption = _first_valid_percent(
        dynamic_data,
        [
            "storage_consumption_ratio_percent",
        ],
    )
    pct_production = _first_valid_percent(
        dynamic_data,
        [
            "storage_production_ratio_percent",
        ],
    )

    print(
        f"DEBUG: Seite 7 Donut-Charts (FIXED) - Consumption: {pct_consumption}%, Production: {pct_production}%"
    )

    if pct_consumption <= 0 and pct_production <= 0:
        print("DEBUG: Keine Donut-Charts gezeichnet - beide Werte <= 0")
        return

    c.saveState()

    # VERBESSERTE Position auf Seite 7 - sichtbarer Bereich
    # Verwende eine Position in der Mitte-rechts der Seite für bessere
    # Sichtbarkeit

    # X-Position: Rechts, aber nicht am Rand
    chart_cx = 450.0  # Rechts von den meisten Inhalten

    # Y-Positionen: Vertikal verteilt in der Mitte der Seite
    consumption_cy = page_height - 400  # Oberer Chart
    production_cy = page_height - 500  # Unterer Chart

    print(
        f"DEBUG: FIXED Chart-Positionen - Consumption: ({chart_cx}, {consumption_cy}), Production: ({chart_cx}, {production_cy})"
    )
    print(f"DEBUG: Seitengröße: {page_width} x {page_height}")

    outer_r = 35.0  # Große Charts für gute Sichtbarkeit
    inner_r = 20.0

    # SEHR SICHTBARE Farben
    from reportlab.lib.colors import Color

    bg = Color(0.9, 0.9, 0.9)  # Hellgrau Hintergrund
    fg_consumption = Color(0.0, 0.5, 1.0)  # Helles Blau für Verbrauch
    fg_production = Color(1.0, 0.3, 0.0)  # Orange für Produktion

    # Oberer Donut: Speicher zu Tagesverbrauch
    if pct_consumption > 0:
        print(
            f"DEBUG: Zeichne FIXED Consumption Donut bei ({chart_cx}, {consumption_cy}) mit {pct_consumption}%"
        )
        _draw_donut(
            c,
            chart_cx,
            consumption_cy,
            pct_consumption,
            outer_r,
            inner_r,
            fg_consumption,
            bg,
        )
        # Zentrumstext
        txt = f"{int(round(pct_consumption))}%"
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(fg_consumption)
        tw = c.stringWidth(txt, "Helvetica-Bold", 10)
        c.drawString(chart_cx - tw / 2, consumption_cy - 5, txt)

        # Label unter dem Chart
        label_txt = "Tagesverbrauch"
        c.setFont("Helvetica-Bold", 8)
        # Schwarz für maximale Sichtbarkeit
        c.setFillColor(Color(0.0, 0.0, 0.0))
        lw = c.stringWidth(label_txt, "Helvetica-Bold", 8)
        c.drawString(chart_cx - lw / 2, consumption_cy - outer_r - 15, label_txt)

    # Unterer Donut: Speicher zu PV-Produktion
    if pct_production > 0:
        print(
            f"DEBUG: Zeichne FIXED Production Donut bei ({chart_cx}, {production_cy}) mit {pct_production}%"
        )
        _draw_donut(
            c,
            chart_cx,
            production_cy,
            pct_production,
            outer_r,
            inner_r,
            fg_production,
            bg,
        )
        # Zentrumstext
        txt = f"{int(round(pct_production))}%"
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(fg_production)
        tw = c.stringWidth(txt, "Helvetica-Bold", 10)
        c.drawString(chart_cx - tw / 2, production_cy - 5, txt)

        # Label unter dem Chart
        label_txt = "PV-Produktion"
        c.setFont("Helvetica-Bold", 8)
        # Schwarz für maximale Sichtbarkeit
        c.setFillColor(Color(0.0, 0.0, 0.0))
        lw = c.stringWidth(label_txt, "Helvetica-Bold", 8)
        c.drawString(chart_cx - lw / 2, production_cy - outer_r - 15, label_txt)

    c.restoreState()


# OLD: page 6 -> NEW: page 7
def _draw_page7_storage_donuts(
    c: canvas.Canvas,
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
) -> None:
    """Zeichnet Donut-Diagramme an den EXAKTEN Platzhalter-Positionen auf Seite 7."""
    # Werte aus dynamic_data ziehen
    pct_consumption = _first_valid_percent(
        dynamic_data,
        [
            "storage_consumption_ratio_percent",
        ],
    )
    pct_production = _first_valid_percent(
        dynamic_data,
        [
            "storage_production_ratio_percent",
        ],
    )

    print(
        f"DEBUG: Seite 7 Donut-Charts - Consumption: {pct_consumption}%, Production: {pct_production}%"
    )

    if pct_consumption <= 0 and pct_production <= 0:
        print("DEBUG: Keine Donut-Charts gezeichnet - beide Werte <= 0")
        return

    c.saveState()

    # EXAKTE Positionen basierend auf seite7.yml Platzhaltern
    # relation_tagverbrauch_prozent: Position: (330.0, 581.0, 500.0, 596.0)
    # relation_pvproduktion_prozent: Position: (330.0, 651.0, 500.0, 676.0)

    # Berechne Zentren der Platzhalter (links vom Text)
    consumption_center_x = 280.0  # Links vom Platzhalter bei x=330
    # Mitte von 581-596, von oben gemessen
    consumption_center_y = page_height - 588.5

    production_center_x = 280.0  # Links vom Platzhalter bei x=330
    # Mitte von 651-676, von oben gemessen
    production_center_y = page_height - 663.5

    print(
        f"DEBUG: EXAKTE Chart-Positionen - Consumption: ({consumption_center_x}, {consumption_center_y}), Production: ({production_center_x}, {production_center_y})"
    )
    print(f"DEBUG: Seitengröße: {page_width} x {page_height}")

    # Angemessene Größe für die Position
    outer_r = 20.0
    inner_r = 12.0

    # Sichtbare Farben
    from reportlab.lib.colors import Color

    bg = Color(0.9, 0.9, 0.9)  # Hellgrauer Hintergrund
    fg_consumption = Color(0.07, 0.34, 0.60)  # Blau wie in der PDF
    fg_production = Color(0.12, 0.42, 0.68)  # Etwas helleres Blau

    # Donut für Tagesverbrauch
    if pct_consumption > 0:
        print(
            f"DEBUG: Zeichne Consumption Donut bei ({consumption_center_x}, {consumption_center_y}) mit {pct_consumption}%"
        )
        _draw_donut(
            c,
            consumption_center_x,
            consumption_center_y,
            pct_consumption,
            outer_r,
            inner_r,
            fg_consumption,
            bg,
        )
        # Zentrumstext
        txt = f"{int(round(pct_consumption))}%"
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(fg_consumption)
        tw = c.stringWidth(txt, "Helvetica-Bold", 8)
        c.drawString(consumption_center_x - tw / 2, consumption_center_y - 3, txt)

    # Donut für PV-Produktion
    if pct_production > 0:
        print(
            f"DEBUG: Zeichne Production Donut bei ({production_center_x}, {production_center_y}) mit {pct_production}%"
        )
        _draw_donut(
            c,
            production_center_x,
            production_center_y,
            pct_production,
            outer_r,
            inner_r,
            fg_production,
            bg,
        )
        # Zentrumstext
        txt = f"{int(round(pct_production))}%"
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(fg_production)
        tw = c.stringWidth(txt, "Helvetica-Bold", 8)
        c.drawString(production_center_x - tw / 2, production_center_y - 3, txt)

    c.restoreState()


def _draw_page1_monthly_production_consumption_chart(
    c: canvas.Canvas,
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
) -> None:
    """Zeichnet das Monatsdiagramm (Produktion vs. Verbrauch) unten links auf Seite 1."""

    def _parse_series(raw: str | None) -> list[float]:
        if not raw:
            return []
        tokens = [
            part.strip()
            for part in str(raw).replace(";", ",").split(",")
            if part.strip()
        ]
        values: list[float] = []
        for token in tokens:
            cleaned = re.sub(r"[^0-9.,\-]", "", token).replace(",", ".")
            if cleaned in {"", ".", "-"}:
                values.append(0.0)
                continue
            try:
                values.append(float(cleaned))
            except Exception:
                values.append(0.0)
        return values

    prod_values = _parse_series(dynamic_data.get("chart_monthly_prod_series"))
    cons_values = _parse_series(dynamic_data.get("chart_monthly_cons_series"))
    month_labels = [
        label.strip()
        for label in (dynamic_data.get("chart_monthly_labels_series") or "").split(",")
        if label.strip()
    ]

    if len(prod_values) != 12 or len(cons_values) != 12:
        return

    if not month_labels or len(month_labels) != 12:
        month_labels = [
            "Jan",
            "Feb",
            "Mrz",
            "Apr",
            "Mai",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Okt",
            "Nov",
            "Dez",
        ]

    max_val = max(max(prod_values), max(cons_values), 0.0)
    if max_val <= 0:
        return

    chart_width = 190.0
    chart_height = 185.0
    chart_x = 65.0
    chart_y = 117.0

    c.saveState()
    try:
        container_x = chart_x - 25
        container_y = chart_y - 35
        container_width = chart_width + 48
        container_height = chart_height + 88

        # Titel und Legende
        title_y = container_y + container_height - 26
        c.setFillColor(Color(0.05, 0.25, 0.45))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(chart_x, title_y, "")

        legend_y = title_y - 18
        legend_x = chart_x
        prod_color = Color(0.70, 0.70, 0.70)  # Grau
        cons_color = Color(0.12, 0.42, 0.68)  # Blau

        c.setFillColor(prod_color)
        c.rect(legend_x, legend_y, 9, 9, stroke=0, fill=1)
        c.setFillColor(Color(0.08, 0.23, 0.43))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(legend_x + 16, legend_y + 1, "Stromproduktion")

        legend_x += 110
        c.setFillColor(cons_color)
        c.rect(legend_x, legend_y, 9, 9, stroke=0, fill=1)
        c.setFillColor(Color(0.08, 0.23, 0.43))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(legend_x + 16, legend_y + 1, "Stromverbrauch")

        plot_top = chart_y + chart_height
        axis_color = Color(0.75, 0.80, 0.84)
        c.setStrokeColor(axis_color)
        c.setLineWidth(0.5)
        c.line(chart_x, chart_y, chart_x + chart_width, chart_y)  # X-Achse
        c.line(chart_x, chart_y, chart_x, plot_top)  # Y-Achse

        # Vertikale Hilfslinien und Skala
        steps = 4
        c.setFont("Helvetica-Bold", 8)
        for idx in range(1, steps + 1):
            x = chart_x + (chart_width / steps) * idx
            c.setStrokeColor(Color(0.86, 0.90, 0.93))
            c.line(x, chart_y, x, plot_top)
            c.setFillColor(Color(0.15, 0.20, 0.27))
            value = max_val / steps * idx
            label = f"{value:,.0f}".replace(",", ".")
            c.drawCentredString(x, chart_y - 18, label)

        # Balken zeichnen (horizontal)
        row_height = chart_height / 12.0
        prod_bar_height = row_height * 0.75
        cons_bar_height = row_height * 0.45
        prod_offset = (row_height - prod_bar_height) / 20.0
        cons_offset = prod_offset + (prod_bar_height - cons_bar_height) / 20.0

        for idx in range(12):
            row_base_y = chart_y + chart_height - (idx + 1) * row_height
            prod_width = (prod_values[idx] / max_val) * chart_width
            cons_width = (cons_values[idx] / max_val) * chart_width

            # Produktion (Türkis, breiter Balken)
            c.setFillColor(prod_color)
            c.setStrokeColor(prod_color)
            c.roundRect(
                chart_x,
                row_base_y + prod_offset,
                max(prod_width, 0.9),
                max(prod_bar_height, 0.4),
                2,
                stroke=1,
                fill=1,
            )

            # Verbrauch (Blau, schmaler und überlagert)
            c.setFillColor(cons_color)
            c.setStrokeColor(cons_color)
            c.roundRect(
                chart_x,
                row_base_y + cons_offset,
                max(cons_width, 0.9),
                max(cons_bar_height, 0.5),
                2,
                stroke=1,
                fill=1,
            )

            # Monatslabel links neben dem Balken
            label_center_y = row_base_y + row_height / 2.0
            c.setFillColor(Color(0.15, 0.20, 0.27))
            c.setFont("Helvetica-Bold", 8)
            c.drawRightString(chart_x - 10, label_center_y - 3, month_labels[idx])

    finally:
        c.restoreState()


# OLD: page 1 -> NEW: page 2
def _draw_page2_kpi_donuts(
    c: canvas.Canvas,
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
) -> None:
    """Zeichnet zwei Donut-Diagramme (Unabhängigkeit, Eigenverbrauch) auf Seite 2 unterhalb der KPI-Überschrift."""
    # Werte aus dynamic_data ziehen (formatiert wie "54%" / "42%")
    # Robuste Ermittlung mit Fallback-Keys
    pct_autark = _first_valid_percent(
        dynamic_data,
        [
            "self_supply_rate_percent",
            "self_sufficiency_percent",
            "autarky_percent",
        ],
    )
    pct_ev = _first_valid_percent(
        dynamic_data,
        [
            "self_consumption_percent",
            # Seite 2 abgeleiteter Wert (nur Zahl): direkter Deckungsanteil am
            # Verbrauch
            "direct_cover_consumption_percent_number",
        ],
    )
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
        txt = dynamic_data.get("self_supply_rate_percent", f"{int(round(pct_autark))}%")
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(fg_blue)
        tw = c.stringWidth(txt, "Helvetica-Bold", 12)
        c.drawString(left_cx - tw / 2, cy - 6, txt)
    if pct_ev > 0:
        _draw_donut(c, right_cx, cy, pct_ev, outer_r, inner_r, fg_blue, bg)
        txt = dynamic_data.get("self_consumption_percent", f"{int(round(pct_ev))}%")
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(fg_blue)
        tw = c.stringWidth(txt, "Helvetica-Bold", 12)
        c.drawString(right_cx - tw / 2, cy - 6, txt)
    c.restoreState()


def _draw_top_right_triangle(
    c: canvas.Canvas, page_width: float, page_height: float, size: float = 36.0
) -> None:
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


def validate_page_files(
    page_num: int, coords_dir: Path, template_dir: Path | None = None
) -> tuple[bool, list[str]]:
    """Validates that all required files exist for a given page number.

    Args:
        page_num: Page number to validate (1-8)
        coords_dir: Directory containing coordinate YML files (coords/ or coords_wp/)
        template_dir: Directory containing PDF template files (defaults to pdf_templates_static/notext/)

    Returns:
        Tuple of (is_valid, missing_files) where:
        - is_valid: True if all required files exist
        - missing_files: List of missing file paths as strings

    Example:
        >>> is_valid, missing = validate_page_files(1, Path("coords"))
        >>> if not is_valid:
        ...     print(f"Missing files: {missing}")
    """
    missing = []

    # Determine if this is heatpump variant based on coords_dir name
    is_heatpump = "wp" in str(coords_dir).lower()

    # Check coordinates file
    coords_prefix = "wp_" if is_heatpump else ""
    coords_file = coords_dir / f"{coords_prefix}seite{page_num}.yml"
    if not coords_file.exists():
        missing.append(str(coords_file))

    # Check template file
    if template_dir is None:
        template_dir = Path(__file__).parent.parent / "pdf_templates_static" / "notext"

    template_prefix = "hp_nt_" if is_heatpump else "nt_nt_"
    template_file = template_dir / f"{template_prefix}{page_num:02d}.pdf"
    if not template_file.exists():
        missing.append(str(template_file))

    return (len(missing) == 0, missing)


# pdf_template_engine/dynamic_overlay.py


def generate_overlay(
    coords_dir: Path, dynamic_data: dict[str, str], total_pages: int = 8
) -> bytes:
    """Erzeugt ein Overlay-PDF für acht Seiten anhand der coords-Dateien.

    total_pages steuert die Fußzeilen-Nummerierung als "Seite x von XX".
    """
    # Validate that all required page files exist before starting generation
    template_dir = Path(__file__).parent.parent / "pdf_templates_static" / "notext"
    missing_files_summary = []
    missing_pages = set()

    for page_num in range(1, total_pages + 1):
        is_valid, missing_files = validate_page_files(
            page_num, coords_dir, template_dir
        )
        if not is_valid:
            missing_files_summary.extend(missing_files)
            missing_pages.add(page_num)
            print(f"⚠️  Warning: Missing files for page {page_num}:")
            for missing_file in missing_files:
                print(f"    - {missing_file}")

    # Graceful degradation: If page 8 files are missing, fall back to 7 pages
    if 8 in missing_pages and total_pages == 8:
        print("\n⚠️  Page 8 files are missing. Falling back to 7-page generation.")
        print(
            "    This is expected if you haven't yet created the new page 8 templates."
        )
        print("    PDF will be generated with 7 pages instead.\n")
        total_pages = 7
        # Re-validate with reduced page count
        missing_files_summary = []
        missing_pages = set()
        for page_num in range(1, total_pages + 1):
            is_valid, missing_files = validate_page_files(
                page_num, coords_dir, template_dir
            )
            if not is_valid:
                missing_files_summary.extend(missing_files)
                missing_pages.add(page_num)

    # If any files are still missing after fallback, provide a clear summary
    if missing_files_summary:
        print(f"\n⚠️  Total missing files: {len(missing_files_summary)}")
        print(
            "    PDF generation will continue but may fail if these files are accessed."
        )
        print("    Please ensure all required template and coordinate files exist.\n")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4
    # Use total_pages (which may have been adjusted by graceful degradation)
    for i in range(
        1, total_pages + 1
    ):  # MIGRATION: 7→8 pages (supports both 7 and 8 pages)
        yml_path = coords_dir / f"seite{i}.yml"
        elements = parse_coords_file(yml_path)
        # Firmenlogo zuerst
        _draw_company_logo(c, dynamic_data, page_width, page_height, page_index=i)
        # Dreieck
        _draw_top_right_triangle(c, page_width, page_height, size=0.0)
        # Seite 1: Neue Seite 1 Inhalte
        if i == 1:
            _draw_page1_new_content(c, dynamic_data, page_width, page_height)
        # OLD: page 1 -> NEW: page 2
        elif i == 2:
            _draw_page2_kpi_donuts(c, dynamic_data, page_width, page_height)
            _draw_page1_monthly_production_consumption_chart(
                c, dynamic_data, page_width, page_height
            )
        # OLD: page 6 -> NEW: page 7
        if i == 7:
            _draw_page7_storage_donuts(c, dynamic_data, page_width, page_height)

        # OLD: page 3 -> NEW: page 4
        if i == 4:
            _draw_page4_waterfall_chart(c, dynamic_data, page_width, page_height)
        # OLD: page 3 -> NEW: page 4 (rechter Chart)
        if i == 4:
            try:
                c.saveState()
                try:
                    c.setFillColorRGB(1, 1, 1)
                    c.rect(350, page_height - 170 - 230, 260, 250, stroke=0, fill=1)
                finally:
                    c.restoreState()
                _draw_page4_right_chart_and_separator(
                    c, elements, dynamic_data, page_width, page_height
                )
            except Exception:
                pass
        # OLD: page 4 -> NEW: page 5
        if i == 5:
            _draw_page5_component_images(c, dynamic_data, page_width, page_height)
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
            "36.958,00 EUR*",  # anlage_kwp (tatsächlicher Beispieltext!)
            "8.251,92 kWh/Jahr",  # annual_pv_production_kwh
            "29.150,00 EUR*",  # amortization_time
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

        right_align_tokens_s7 = {
            "zwischensumme_preis",
            "minus_mwst",
            "plus_aufpreis",
            "minus_rabatt",
            "zubehor_preis",
            "preis_mit_mwst",
        }

        right_align_tokens_s8_static = {
            "Anzahlung bei Auftragserteilung",
            "nach erfolgreicher Lieferung und Erhalt der",
            "PV Komponente und nach abgeschlossener DC Montage",
            "nach erfolgreicher AC Elektroinstallation",
            "sowie die Inbetriebnahme der PV Anlage *",
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
                if (
                    ttxt in _cost_token_map
                    and isinstance(elem.get("position"), tuple)
                    and len(elem.get("position")) == 4
                ):
                    # Speichere Position + Font-Infos und referenzierten
                    # dynamischen Key
                    page3_cost_tokens[_cost_token_map[ttxt]] = {
                        "position": elem.get("position"),
                        "font": elem.get("font", "Helvetica-Bold"),
                        "font_size": float(elem.get("font_size", 10.49)),
                        "original_text": ttxt,
                    }

        # Seite 6: Dynamisches Nachrücken (Compacting) für Produkt- & Dienstleistungszeilen
        # OLD: page 6 -> NEW: page 7
        if i == 7:
            try:
                elements = _compact_page7_elements(elements, dynamic_data, page_height)
            except Exception as e:
                print(f"WARN: Compacting Seite7 fehlgeschlagen: {e}")

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
                "relation_pvproduktion_prozent",
            ]:
                print(
                    f"DEBUG: Überspringe Platzhalter-Text '{text}' - wird durch Donut-Chart ersetzt"
                )
                continue

            # Seite 4 & 5: Firmenname und TÜV-Text dynamisch behandeln
            if i in (4, 5) and text == "firmen_name":
                company_name = dynamic_data.get("company_name", "")
                if company_name:
                    draw_text = company_name
                    print(
                        f"DEBUG: Seite {i} Firmenname ersetzt: '{text}' -> '{company_name}'"
                    )
                else:
                    draw_text = "Ihr Unternehmen"  # Fallback
            else:
                # Normale Text-Behandlung
                draw_text = dynamic_data.get(key, "") if key else text

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

            # Seite 4 & 5: TÜV-Text dynamisch nach Firmennamen positionieren
            if (
                i in (4, 5)
                and text
                == "verwendet ausschließlich TÜV geprüfte Komponenten, die sämtlichen gängigen Normen und Zertifizierungen entsprechen."
            ):
                company_name = dynamic_data.get("company_name", "Ihr Unternehmen")

                # Font setzen für Breitenberechnung
                try:
                    c.setFont(font_name, font_size)
                except Exception:
                    c.setFont("Helvetica", font_size)

                # Breite des Firmennamens + 1 Leertaste berechnen
                # ReportLab-kompatible Font-Namen verwenden
                safe_font_name = "Helvetica" if "Helvetica" in font_name else font_name
                company_width = c.stringWidth(
                    company_name + " ", safe_font_name, font_size
                )

                # Neue X-Position: Start des Firmennamens (45.0) + Breite des
                # Firmennamens + Leertaste
                draw_x = 45.0 + company_width

                print(
                    f"DEBUG: Seite {i} TÜV-Text dynamisch positioniert bei X={
                        draw_x:.1f} (nach '{company_name}')"
                )
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
                    sym_color_hex = dynamic_data.get("service_symbol_color")
                    lbl_color_hex = dynamic_data.get("service_label_color")
                    hide_val_col = bool(dynamic_data.get("service_value_column_hidden"))
                    is_label = text.startswith("X_LBL_")
                    is_value = text.startswith("X_SRV_") or text.startswith("X_PROD_")

                    def _hex_to_color(h):
                        from reportlab.lib.colors import Color

                        h = h.lstrip("#")
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
                    if (
                        hide_val_col
                        and is_value
                        and (text.startswith("X_SRV_") or text.startswith("X_PROD_"))
                    ):
                        draw_text = ""
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
                "self_consumption_percent",
            }:
                continue

            if i == 3 and text and "JAHRE SIMULATION" in text and len(pos) == 4:
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
                        fill=1,
                    )
                finally:
                    c.restoreState()

            try:
                raw = (text or "").strip()
                is_footer_candidate = (
                    not key
                    and raw.isdigit()
                    and len(pos) == 4
                    and (pos[3] >= 780.0)
                    and (pos[0] >= 520.0)
                    and color_int == 0xFFFFFF
                )
            except Exception:
                is_footer_candidate = False

            if is_footer_candidate:
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
                        tw = c.stringWidth(str(draw_text), font_name, font_size)
                        mid_x = (x0 + x1) / 2.0
                        c.drawString(mid_x - tw / 2.0, draw_y, str(draw_text))
                    except Exception:
                        c.drawString(draw_x, draw_y, str(draw_text))
                elif (text in right_align_tokens_s1) and len(pos) == 4:
                    # Rechtsbündige Ausrichtung für die KPI-Werte der
                    # Titelseite
                    try:
                        c.drawRightString(x1 + 17, draw_y, str(draw_text))
                    except Exception:
                        c.drawString(draw_x, draw_y, str(draw_text))
                elif (text in right_align_tokens_s3) and len(pos) == 4:
                    # Rechtsbündig für Wirtschaftlichkeitswerte (Seite 3/4 je
                    # nach Layout)
                    try:
                        c.drawRightString(x1, draw_y, str(draw_text))
                    except Exception:
                        c.drawString(draw_x, draw_y, str(draw_text))
                elif (text in right_align_tokens_s7) and len(pos) == 4:
                    # Rechtsbündige Ausrichtung für Preiszusammenfassung (Seite
                    # 7/8)
                    try:
                        c.drawRightString(x1, draw_y, str(draw_text))
                    except Exception:
                        c.drawString(draw_x, draw_y, str(draw_text))
                elif len(pos) == 4 and (
                    text in right_align_tokens_s8_static
                    or (text or "").strip() in right_align_tokens_s8_static
                ):
                    # Rechte Spalte auf Seite 8 bündig mit Referenz "Montage"
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
                    val = dynamic_data.get(dyn_key) or meta.get("original_text") or ""
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
                        fill=1,
                    )
                    c.restoreState()
                    c.setFillColor(colors.black)
                    c.drawString(x0, draw_y, str(val))
            finally:
                c.restoreState()

        # OLD: page 4 -> NEW: page 5 (Hersteller-Logos nach den Texten
        # zeichnen)
        if i == 5:
            try:
                _draw_page5_brand_logos(c, dynamic_data, page_width, page_height)
            except Exception as e:
                print(f"WARN: Fehler beim Zeichnen der Hersteller-Logos Seite5: {e}")

        c.showPage()
    c.save()
    return buffer.getvalue()


# OLD: page 6 -> NEW: page 7
def _compact_page7_elements(
    elements: list[dict[str, Any]], dynamic_data: dict[str, str], page_height: float
) -> list[dict[str, Any]]:
    """Verdichtet Seite 7 vertikal: Entfernt deaktivierte Dienstleistungszeilen.

    Strategie:
    - Identifiziere Paare (Label + Wert) anhand ihrer Y-Position (Originalkoordinaten in YAML).
    - Ein Paar gehört zur Dienstleistungen-/Produkte-Sektion, wenn BOTH:
        * Text ist Platzhalter (beginnt mit 'X_LBL_' oder 'X_SRV_' oder 'X_PROD_') ODER bereits gemappt wurde
        * Y-Koordinate im Bereich des Dienstleistungsblocks liegt (>= ~190 und <= ~600 in Vorlage)
    - Wenn sowohl Label- als auch Value-Platzhalter leer (dynamic_data liefert "") -> Paar wird entfernt.
    - Übrige Paare werden in Originalreihenfolge neu nach unten versetzt ohne Lücken.
    - Nicht-betroffene Elemente (Header, Footer, Summary, etc.) bleiben unverändert.
    """
    # Bereich in dem Produkt + Dienstleistungszeilen liegen (aus seite7.yml
    # entnommen)
    Y_MIN = 120.0  # etwas großzügiger für Produktzeilen
    Y_MAX = 610.0

    # Hilfsfunktion: Hole Canvas-Y1 (oberer Rand) aus Positionstuple
    def _y_top(pos_tuple):
        if not (isinstance(pos_tuple, tuple) and len(pos_tuple) == 4):
            return None
        # YAML speichert (x0, y0, x1, y1) mit y1 als maxY (unten?) -> In Vorlage: (70, 200, 200, 215)
        # Wir nehmen das obere Ende als y1
        return (
            float(pos_tuple[1]) if pos_tuple[1] < pos_tuple[3] else float(pos_tuple[3])
        )

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
        if Y_MIN <= y_top <= Y_MAX and (
            txt.startswith("X_LBL_")
            or txt.startswith("X_SRV_")
            or txt.startswith("X_PROD_")
        ):
            service_rows.append(el)
        else:
            other_elements.append(el)

    # Gruppiere Zeilenpaare: Label (X_LBL_*) + Wert (X_SRV_* oder X_PROD_*)
    # Vorgehen: Sortiere nach y (aufsteigend) und verarbeite sequentiell
    service_rows_sorted = sorted(
        service_rows, key=lambda e: _y_top(e.get("position")) or 0.0
    )

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
            lbl_key = (
                PLACEHOLDER_MAPPING.get((lbl_el.get("text") or "").strip())
                if lbl_el
                else None
            )
            lbl_val = dynamic_data.get(lbl_key, "") if lbl_key else ""
            val_key = (
                PLACEHOLDER_MAPPING.get((val_el.get("text") or "").strip())
                if val_el
                else None
            )
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

    first_top = (
        min(
            _y_top(el.get("position"))
            for el in service_rows_sorted
            if _y_top(el.get("position")) is not None
        )
        or 0.0
    )
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
        if not (
            txt.startswith("X_LBL_")
            or txt.startswith("X_SRV_")
            or txt.startswith("X_PROD_")
        ):
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
        el["position"] = (x0, new_y0, x1, new_y1)
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


# OLD: page 3 -> NEW: page 4


def _draw_page4_right_chart_and_separator(
    c: canvas.Canvas,
    elements: list[dict[str, Any]],
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
) -> None:
    """Seite 4: Rechts NUR die 20-Jahres-Gesamtergebnisse als Text + vertikale Trennlinie.

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
            if (
                t == "25.000"
                and isinstance(el.get("position"), tuple)
                and len(el.get("position")) == 4
            ):
                top_label_y1 = el["position"][3]
            if (
                t == "0"
                and isinstance(el.get("position"), tuple)
                and len(el.get("position")) == 4
            ):
                bottom_label_y1 = el["position"][3]
        # Fallbacks, falls tokens bereits dynamisch ersetzt wurden und oben
        # nicht gefunden wurden
        if top_label_y1 is None or bottom_label_y1 is None:
            # Suche nach kleinster/größter y1 bei numerischen Tick-Labels im
            # Bereich der linken Achse
            candidates = []
            for el in elements:
                t = (el.get("text") or "").strip().replace(".", "").replace(",", ".")
                if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t):
                    pos = el.get("position")
                    if isinstance(pos, tuple) and len(pos) == 4 and pos[0] < 100.0:
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
        c.line(sep_x, axis_bottom_y - 0.0, sep_x, axis_top_y + 8.0)
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
                ss = (
                    re.sub(r"[^0-9,\.]", "", (s or ""))
                    .replace(".", "")
                    .replace(",", ".")
                )
                return float(ss or 0.0)
            except Exception:
                return 0.0

        v_no_inc_total = _parse_money(
            dynamic_data.get("cost_20y_no_increase_number") or "0"
        )
        v_with_inc_total = _parse_money(
            dynamic_data.get("cost_20y_with_increase_number") or "0"
        )

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
            lbl = (
                f"{
                tv:,.2f}".replace(
                    ",", "#"
                )
                .replace(".", ",")
                .replace("#", ".")
            )
            try:
                tw = c.stringWidth(lbl, "Helvetica", 6.0)
            except Exception:
                tw = c.stringWidth(lbl, "Helvetica", 6)
            c.setFillColor(colors.black)  # Schwarz statt Dunkelblau
            c.drawString(y_axis_x - 6.0 - tw, py - 2.0, lbl)
        c.restoreState()

        # Balken zeichnen
        def _h(val: float) -> float:
            return 0.0 if top <= 0 else (max(0.0, min(1.0, val / top)) * (y1 - y0))

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
        c.rect(legend_x, legend1_base_y, square_size, square_size, stroke=0, fill=1)
        c.restoreState()
        c.setFillColor(colors.black)  # Schwarz statt Dunkelblau
        c.drawString(
            legend_x + square_size + label_gap + text_offset_x,
            legend1_base_y - 1.0 + text_offset_y,
            legend_texts[0],
        )
        # Eintrag 2 (dunkelblau) - Quadrat an ursprünglicher Position
        c.saveState()
        c.setFillColor(dark_blue)
        c.rect(legend_x, legend2_base_y, square_size, square_size, stroke=0, fill=1)
        c.restoreState()
        c.setFillColor(colors.black)  # Schwarz statt Dunkelblau
        c.drawString(
            legend_x + square_size + label_gap + text_offset_x,
            legend2_base_y - 1.0 + text_offset_y,
            legend_texts[1] if len(legend_texts) > 1 else "",
        )

    finally:
        # Canvas-Zustand wiederherstellen, damit nachfolgende Texte nicht
        # beeinflusst werden
        c.restoreState()


# OLD: page 4 -> NEW: page 5
def _draw_page5_component_images(
    c: canvas.Canvas,
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
) -> None:
    """Zeigt bis zu drei Produktbilder (Module, WR, Speicher) auf Seite 5 an.

    Erwartet Base64 in Keys: module_image_b64, inverter_image_b64, storage_image_b64.
    Positionierung: linke Spalte Bilderblöcke oberhalb/links der jeweiligen Textblöcke,
    sodass die bestehenden Textfelder (aus seite5.yml) nicht überlagert werden.
    """
    try:
        images = [
            (
                dynamic_data.get("module_image_b64"),
                {
                    "x": 50.0,
                    "y_top": page_height - 250.0,
                    "max_w": 140.0,
                    "max_h": 90.0,
                },
            ),
            (
                dynamic_data.get("inverter_image_b64"),
                {
                    "x": 50.0,
                    "y_top": page_height - 440.0,
                    "max_w": 140.0,
                    "max_h": 90.0,
                },
            ),
            (
                dynamic_data.get("storage_image_b64"),
                {
                    "x": 50.0,
                    "y_top": page_height - 630.0,
                    "max_w": 140.0,
                    "max_h": 90.0,
                },
            ),
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
                    mask="auto",
                )
            finally:
                c.restoreState()
    except Exception:
        return


# OLD: page 4 -> NEW: page 5
def _draw_page5_brand_logos(
    c: canvas.Canvas,
    dynamic_data: dict[str, str],
    page_width: float,
    page_height: float,
) -> None:
    """Zeichnet Hersteller-Logos (Module / WR / Speicher) auf Seite 5 rechts neben den Überschriften.

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
            "batteriespeicher": {"x": 520.0, "y": 180.0, "width": 60.0, "height": 30.0},
            "wechselrichter": {"x": 520.0, "y": 370.0, "width": 60.0, "height": 30.0},
            "modul": {"x": 520.0, "y": 560.0, "width": 60.0, "height": 30.0},
        }
        try:
            positions = (
                load_admin_setting("pdf_logo_positions", default_positions)
                or default_positions
            )
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
            align_with_titles = (
                load_admin_setting("pdf_logo_align_with_titles", True)
                and not manual_mode
            )
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
                    "pdf_logo_keep_alignment_when_customized", False
                )
            except Exception:
                keep_align = False
            if align_with_titles and not keep_align:
                align_with_titles = False
                print(
                    "DEBUG LOGO AUTO-DISABLE ALIGN: Admin-Positionen weichen von Defaults ab -> benutze Admin-Y"
                )
            else:
                if align_with_titles:
                    print(
                        "DEBUG LOGO ALIGN trotz Admin-Anpassung aktiv (keep_alignment_when_customized=True)"
                    )

        # Optionale vertikale Offsets (in pt) je Kategorie für Feintuning
        try:
            vertical_offsets = load_admin_setting("pdf_logo_vertical_offsets", {}) or {}
            if not isinstance(vertical_offsets, dict):
                vertical_offsets = {}
        except Exception:
            vertical_offsets = {}

        title_y_centers: dict[str, float] = {}
        if align_with_titles:
            # Wir lesen coords/seite5.yml und suchen die Überschriften SOLARMODULE / WECHSELRICHTER / BATTERIESPEICHER.
            # Format:
            # Text: SOLARMODULE\n
            # Position: (x1, y1, x2, y2)
            import os
            import re

            coords_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "coords", "seite4.yml"
            )
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
                                p.strip() for p in m.group(1).split(",") if p.strip()
                            ]
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
                custom_order = load_admin_setting("pdf_logo_custom_order", []) or []
                if not custom_order:
                    # Fallback harte Wunsch-Reihenfolge
                    custom_order = ["modul", "wechselrichter", "batteriespeicher"]
                if not isinstance(custom_order, list):
                    custom_order = []
            except Exception:
                custom_order = ["modul", "wechselrichter", "batteriespeicher"]

            # Falls custom_order gesetzt ist und alle Kategorien enthält,
            # verteilen wir die Y-Center gemäß Sortierung (oben->unten) nach
            # den vorhandenen Y-Werten sortiert.
            if len(custom_order) == 3 and set(custom_order) == set(
                title_y_centers.keys()
            ):
                # Sortiere existierende Zentren nach Y (aufsteigend) ->
                # unterste zuerst
                centers_sorted = sorted(title_y_centers.items(), key=lambda kv: kv[1])
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
                box_h = float(pos.get("height", default_positions[cat]["height"]))
                offset = float(vertical_offsets.get(cat, 0.0))
                new_y_bottom = max(0.0, y_center - box_h / 2.0 + offset)
                pos["y"] = new_y_bottom
                positions[cat] = pos
            print(f"DEBUG LOGO ALIGN aktiv – Titel-Zentren genutzt: {title_y_centers}")
        else:
            if align_with_titles:
                print(
                    "DEBUG LOGO ALIGN keine Titel-Zentren gefunden – Fallback auf Admin/Default-Y"
                )
            if manual_mode:
                print(
                    "DEBUG LOGO MANUAL MODE aktiv – verwende reine Admin-Positionen ohne Alignment"
                )

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
            box_w = float(pos.get("width", default_positions[category]["width"]))
            box_h = float(pos.get("height", default_positions[category]["height"]))

            # Optional: 2cm vom rechten Rand erzwingen falls Admin-x sehr weit links (< rechte Rand - 2cm)
            # 2 cm ≈ 56.7 pt. Rechter Rand (A4 width ~595). Ziel-x = 595 - 56.7
            # - box_w
            try:
                enforce_margin = load_admin_setting(
                    "pdf_logo_right_margin_enforce", True
                )
            except Exception:
                enforce_margin = True
            if enforce_margin:
                right_margin_cm = 2.0
                right_margin_pt = right_margin_cm * 28.3465
                desired_x = page_width - right_margin_pt - box_w
                if (
                    x > desired_x + 40 or x < desired_x - 120
                ):  # Falls Admin versehentlich zu weit rechts (überlappt Rand), korrigieren
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
                    mask="auto",
                )
                print(
                    f"DEBUG LOGO DRAW {category}: x={
                        x:.1f}, y={
                        y:.1f}, w={
                        dw:.1f}, h={
                        dh:.1f}"
                )
            except Exception as e:
                print(f"Fehler beim Zeichnen Logo {category}: {e}")
            finally:
                c.restoreState()
    except Exception as e:
        print(f"Fehler _draw_page4_brand_logos: {e}")


def _remove_text_from_page(page, texts_to_remove: list[str]):
    """Entfernt spezifische Texte aus dem Content-Stream einer PDF-Seite."""
    try:
        if not hasattr(page, "get_contents") or not texts_to_remove:
            return

        content = page.get_contents()
        if content is None:
            return

        # Content-Stream als String laden
        if hasattr(content, "get_data"):
            content_data = content.get_data()
        else:
            content_data = content.read()

        if isinstance(content_data, bytes):
            try:
                content_str = content_data.decode("latin-1", errors="ignore")
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
            new_content = io.BytesIO(content_str.encode("latin-1", errors="ignore"))
            if hasattr(page, "_contents"):
                page._contents = new_content

    except Exception:
        pass  # Bei Fehlern einfach ignorieren


def merge_with_background(overlay_bytes: bytes, bg_dir: Path) -> bytes:
    """Verschmilzt das Overlay mit nt_nt_01.pdf … nt_nt_08.pdf aus bg_dir."""
    overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
    writer = PdfWriter()
    for page_num in range(
        1, 9
    ):  # MIGRATION: Changed from range(1, 8) to range(1, 9) for 8 pages
        # Unterstütze beide Muster: nt_nt_XX.pdf und nt_XX.pdf
        candidates = [
            bg_dir
            / f"nt_nt_{
                page_num:02d}.pdf",
            bg_dir
            / f"nt_{
                page_num:02d}.pdf",
        ]
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
                texts_to_remove = ["", "", "", "", ""]
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
                        width=bw, height=bh
                    )  # type: ignore
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


def append_additional_pages(base_pdf: bytes, additional_pdf: bytes | None) -> bytes:
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
    print(f"DEBUG: generate_custom_offer_pdf called with {len(dynamic_data)} dynamic_data keys")
    
    # Bestimme Gesamtseiten für Fußzeile (8 + ggf. Zusatzseiten)
    total_pages = 8
    if additional_pdf:
        try:
            add_reader = PdfReader(io.BytesIO(additional_pdf))
            total_pages = 8 + len(add_reader.pages)
            print(f"DEBUG: Additional PDF has {len(add_reader.pages)} pages, total_pages={total_pages}")
        except Exception as e:
            print(f"DEBUG: Error reading additional PDF: {e}")
            total_pages = 8
    
    print(f"DEBUG: total_pages={total_pages}, starting PDF generation...")
    
    try:
        # 1. Generiere komplettes 8-seitiges Overlay-PDF
        print("DEBUG: Calling generate_overlay()...")
        overlay_bytes = generate_overlay(coords_dir, dynamic_data, total_pages)
        
        if not overlay_bytes:
            print("ERROR: generate_overlay() returned None!")
            return None
        
        print(f"DEBUG: Overlay generated successfully: {len(overlay_bytes)} bytes")
        
        # 2. Merge Overlay mit Background-Templates (alle 8 Seiten)
        print("DEBUG: Calling merge_with_background()...")
        merged_bytes = merge_with_background(overlay_bytes, bg_dir)
        
        if not merged_bytes:
            print("ERROR: merge_with_background() returned None!")
            return None
        
        print(f"DEBUG: Merge successful: {len(merged_bytes)} bytes")
        
        # 3. Optional: Zusatz-PDF anhängen
        if additional_pdf:
            try:
                print("DEBUG: Appending additional PDF...")
                main_reader = PdfReader(io.BytesIO(merged_bytes))
                add_reader = PdfReader(io.BytesIO(additional_pdf))
                
                writer = PdfWriter()
                
                # Hauptdokument (8 Seiten)
                for page in main_reader.pages:
                    writer.add_page(page)
                
                # Zusätzliche Seiten
                for page in add_reader.pages:
                    writer.add_page(page)
                
                output_buffer = io.BytesIO()
                writer.write(output_buffer)
                result = output_buffer.getvalue()
                print(f"DEBUG: Final PDF with additional pages: {len(result)} bytes, {len(writer.pages)} pages")
                return result
                
            except Exception as e:
                print(f"ERROR: Failed to append additional PDF: {e}")
                import traceback
                traceback.print_exc()
                # Gib wenigstens das Haupt-PDF zurück
                return merged_bytes
        
        # 4. Kein Zusatz-PDF: Gib merged PDF zurück
        print(f"DEBUG: Final PDF generated: {len(merged_bytes)} bytes")
        return merged_bytes
        
    except Exception as e:
        print(f"ERROR: PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_multi_offer_pdfs(
    selected_firms: list,
    standard_products: dict,
    project_data: dict,
    analysis_results: dict,
    company_info: dict,
    profit_margin: float = 0,
    modifier_pct: float = 15.0,
    progression_pct: float = 5.0,
    additional_pdf: bytes | None = None,
) -> list[tuple[str, bytes]]:
    """
    Generiere Multiple PDFs für verschiedene Firmen mit rotierenden Produkten
    
    Args:
        selected_firms: Liste von Firmen-Dicts aus Firmendatenbank
        standard_products: {category: product_dict} vom Standard-Angebot
        project_data: Projekt-Daten (Kunde, Verbräuche, etc.)
        analysis_results: Analyse-Resultate mit Berechnungen
        company_info: Firmen-Info für Standard-Angebot
        profit_margin: Gewinnmarge in Prozent
        modifier_pct: Basis-Aufschlag für Multi-PDFs
        progression_pct: Progressive Aufschlag-Steigerung pro Firma
        additional_pdf: Optional zusätzliche PDF-Seiten
    
    Returns:
        Liste von (firmenname, pdf_bytes) Tupeln
    """
    from product_rotation_engine import rotate_products, track_used_brands, track_used_models
    from price_modification_engine import calculate_price_with_products
    
    print(f"\n{'='*80}")
    print(f"MULTI-PDF GENERIERUNG: {len(selected_firms)} Firmen")
    print(f"{'='*80}\n")
    
    results = []
    used_brands = track_used_brands(standard_products)
    used_models = track_used_models(standard_products)
    
    print(f"Standard-Angebot verwendet Marken: {used_brands}")
    print(f"Standard-Angebot verwendet Modelle: {used_models}")
    
    for firm_index, firm in enumerate(selected_firms):
        firm_name = firm.get('name') or firm.get('Name') or f"Firma_{firm_index + 1}"
        
        print(f"\n{'-'*80}")
        print(f"Firma {firm_index + 1}/{len(selected_firms)}: {firm_name}")
        print(f"{'-'*80}")
        
        try:
            # 1. Rotiere Produkte für diese Firma
            print(f"\n[1/4] Produkt-Rotation...")
            rotated_products = rotate_products(
                standard_products=standard_products,
                used_brands=used_brands,
                firm_index=firm_index,
                used_models=used_models
            )
            
            if not rotated_products:
                print(f"ERROR: Keine Produkte rotiert für {firm_name}")
                continue
            
            print(f"✓ {len(rotated_products)} Produkte rotiert")
            
            # 2. Berechne Preis mit Modifikation
            print(f"\n[2/4] Preisberechnung...")
            price_result = calculate_price_with_products(
                products=rotated_products,
                analysis_results=analysis_results,
                profit_margin=profit_margin,
                modifier_pct=modifier_pct,
                firm_index=firm_index,
                progression_pct=progression_pct
            )
            
            modified_price = price_result['modified_price']
            print(f"✓ Preis: {modified_price:.2f}€ (Aufschlag: +{price_result['modifier_applied']:.1f}%)")
            
            # 3. Baue Dynamic Data mit rotierten Produkten
            print(f"\n[3/4] Dynamic Data erstellen...")
            
            # Erstelle modifizierte analysis_results mit neuem Preis
            modified_analysis = analysis_results.copy() if analysis_results else {}
            
            # WICHTIG: Setze alle möglichen Preis-Keys mit modifiziertem Preis
            modified_analysis['total_price'] = modified_price
            modified_analysis['FINAL_END_PREIS'] = modified_price
            modified_analysis['final_end_preis'] = modified_price
            modified_analysis['endpreis'] = modified_price
            modified_analysis['gesamtpreis'] = modified_price
            modified_analysis['total_cost'] = modified_price
            
            # Formatierter Preis (z.B. "19.550,00 €")
            formatted_price = f"{modified_price:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
            modified_analysis['FINAL_END_PREIS_FORMATTED'] = formatted_price
            modified_analysis['final_end_preis_formatted'] = formatted_price
            
            # Rotierte Produkte speichern
            modified_analysis['rotated_products'] = rotated_products
            
            # Firmen-Info kopieren und erweitern
            multi_company_info = firm.copy()
            
            print(f"✓ Modifizierter Preis in analysis_results: {modified_price:.2f}€")
            print(f"✓ Formatierter Preis: {formatted_price}")
            
            # Baue Dynamic Data mit modifizierten Daten
            try:
                from pdf_template_engine.placeholders import build_dynamic_data
                
                multi_dynamic_data = build_dynamic_data(
                    project_data=project_data,
                    analysis_results=modified_analysis,  # Mit modifiziertem Preis!
                    company_info=multi_company_info
                )
                
                # DOPPELTE SICHERHEIT: Überschreibe Preis-Keys in Dynamic Data
                multi_dynamic_data['FINAL_END_PREIS'] = f"{modified_price:.2f}"
                multi_dynamic_data['FINAL_END_PREIS_FORMATTED'] = formatted_price
                multi_dynamic_data['final_end_preis'] = f"{modified_price:.2f}"
                multi_dynamic_data['final_end_preis_formatted'] = formatted_price
                
                print(f"✓ Dynamic Data: {len(multi_dynamic_data)} Einträge")
                print(f"✓ FINAL_END_PREIS_FORMATTED in Dynamic Data: {multi_dynamic_data.get('FINAL_END_PREIS_FORMATTED')}")
                
            except Exception as e:
                print(f"ERROR: build_dynamic_data() fehlgeschlagen: {e}")
                import traceback
                traceback.print_exc()
                
                # Fallback: Minimal Dynamic Data mit Preis
                multi_dynamic_data = {
                    'firma_name': firm_name,
                    'FINAL_END_PREIS': f"{modified_price:.2f}",
                    'FINAL_END_PREIS_FORMATTED': formatted_price,
                    'final_end_preis': f"{modified_price:.2f}",
                    'final_end_preis_formatted': formatted_price,
                }
            
            # 4. Generiere PDF mit firma-spezifischen Templates
            print(f"\n[4/4] PDF-Generierung mit Firma-Templates...")
            
            # Firma-spezifische Pfade (f1, f2, f3, ...)
            firm_suffix = f"f{firm_index + 1}"
            
            coords_dir = Path(f"coords_multi")  # Verwendet seite1_f1.yml, seite2_f1.yml, etc.
            bg_dir = Path(f"pdf_templates_static/multi")  # Verwendet multi_nt_01_f1.pdf, etc.
            
            # Erstelle temporäre Symlinks oder kopiere Dateien mit richtigem Namen
            # Da generate_custom_offer_pdf() seite1.yml ... seite8.yml erwartet,
            # müssen wir eine angepasste Version verwenden
            
            pdf_bytes = generate_multi_firm_pdf(
                coords_dir=coords_dir,
                bg_dir=bg_dir,
                dynamic_data=multi_dynamic_data,
                firm_suffix=firm_suffix,
                additional_pdf=additional_pdf
            )
            
            if not pdf_bytes:
                print(f"ERROR: PDF-Generierung fehlgeschlagen für {firm_name}")
                continue
            
            print(f"✓ PDF generiert: {len(pdf_bytes)} bytes")
            
            # 5. Speichere Resultat
            results.append((firm_name, pdf_bytes))
            
            # 6. Aktualisiere verwendete Marken/Modelle für nächste Firma
            used_brands.update(track_used_brands(rotated_products))
            
            for category, models in track_used_models(rotated_products).items():
                if category not in used_models:
                    used_models[category] = set()
                used_models[category].update(models)
            
            print(f"\n✓ Firma {firm_name} abgeschlossen")
            
        except Exception as e:
            print(f"ERROR bei Firma {firm_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*80}")
    print(f"MULTI-PDF GENERIERUNG ABGESCHLOSSEN: {len(results)}/{len(selected_firms)} erfolgreich")
    print(f"{'='*80}\n")
    
    return results


def generate_multi_firm_pdf(
    coords_dir: Path,
    bg_dir: Path,
    dynamic_data: dict[str, str],
    firm_suffix: str,
    additional_pdf: bytes | None = None,
) -> bytes:
    """
    Generiere PDF für eine spezifische Firma mit firma-spezifischen Templates
    
    Args:
        coords_dir: Basis-Pfad zu coords_multi/
        bg_dir: Basis-Pfad zu pdf_templates_static/multi/
        dynamic_data: Dynamic Data Dictionary
        firm_suffix: "f1", "f2", "f3", ... für Firma-Nummer
        additional_pdf: Optional zusätzliche PDF-Seiten
    
    Returns:
        PDF bytes oder None bei Fehler
    """
    import yaml
    
    print(f"DEBUG: generate_multi_firm_pdf für {firm_suffix}")
    print(f"DEBUG: coords_dir={coords_dir}, bg_dir={bg_dir}")
    
    try:
        # Bestimme Gesamtseiten
        total_pages = 8
        if additional_pdf:
            try:
                add_reader = PdfReader(io.BytesIO(additional_pdf))
                total_pages = 8 + len(add_reader.pages)
            except Exception:
                pass
        
        # Generiere Overlay für alle 8 Seiten mit firma-spezifischen Koordinaten
        overlay_buffer = io.BytesIO()
        c = canvas.Canvas(overlay_buffer, pagesize=A4)
        page_width, page_height = A4
        
        for page_num in range(1, 9):
            # Lade firma-spezifische YML: seite1_f1.yml, seite2_f2.yml, etc.
            yml_file = coords_dir / f"seite{page_num}_{firm_suffix}.yml"
            
            if not yml_file.exists():
                print(f"WARNING: {yml_file} nicht gefunden, überspringe Seite {page_num}")
                c.showPage()
                continue
            
            # Lade Koordinaten
            with open(yml_file, 'r', encoding='utf-8') as f:
                coords = yaml.safe_load(f) or []
            
            print(f"DEBUG: Seite {page_num}: {len(coords)} Platzhalter aus {yml_file}")
            
            # Zeichne Platzhalter auf dieser Seite
            for item in coords:
                placeholder = item.get('placeholder', '')
                value = dynamic_data.get(placeholder, '')
                
                x = item.get('x', 0)
                y = item.get('y', 0)
                font = item.get('font', 'Helvetica')
                size = item.get('size', 12)
                color_str = item.get('color', 'black')
                
                # Zeichne Text
                c.setFont(font, size)
                c.drawString(x, y, str(value))
            
            c.showPage()
        
        c.save()
        overlay_bytes = overlay_buffer.getvalue()
        
        if not overlay_bytes:
            print("ERROR: Overlay-Generierung fehlgeschlagen")
            return None
        
        print(f"DEBUG: Overlay generiert: {len(overlay_bytes)} bytes")
        
        # Merge mit firma-spezifischen Backgrounds
        overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
        writer = PdfWriter()
        
        for page_num in range(8):
            # Lade firma-spezifisches Background: multi_nt_01_f1.pdf, etc.
            bg_file = bg_dir / f"multi_nt_{page_num+1:02d}_{firm_suffix}.pdf"
            
            if not bg_file.exists():
                print(f"WARNING: {bg_file} nicht gefunden, überspringe Background für Seite {page_num+1}")
                # Verwende nur Overlay
                writer.add_page(overlay_reader.pages[page_num])
                continue
            
            # Merge Overlay + Background
            bg_reader = PdfReader(bg_file)
            bg_page = bg_reader.pages[0]
            overlay_page = overlay_reader.pages[page_num]
            
            bg_page.merge_page(overlay_page)
            writer.add_page(bg_page)
        
        # Optional: Zusatz-PDF anhängen
        if additional_pdf:
            try:
                add_reader = PdfReader(io.BytesIO(additional_pdf))
                for page in add_reader.pages:
                    writer.add_page(page)
            except Exception as e:
                print(f"WARNING: Zusatz-PDF konnte nicht angehängt werden: {e}")
        
        # Schreibe finales PDF
        final_buffer = io.BytesIO()
        writer.write(final_buffer)
        final_bytes = final_buffer.getvalue()
        
        print(f"DEBUG: Final PDF für {firm_suffix}: {len(final_bytes)} bytes")
        
        return final_bytes
        
    except Exception as e:
        print(f"ERROR: PDF-Generierung für {firm_suffix} fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return None
