# === AUTO-GENERATED INSERT PATCH ===
# target_module: pdf_template_engine/dynamic_overlay.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
from __future__ import annotations

import base64
import io
import re
from pathlib import Path
from typing import Any

from reportlab.lib import colors  # für add_page3_elements (colors.black)
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


# --- DEF BLOCK START: func _as_image_reader ---
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: func _draw_page3_right_chart_and_separator ---
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
# --- DEF BLOCK END ---


# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---


# --- DEF BLOCK START: func _remove_text_from_page ---
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
# --- DEF BLOCK END ---
