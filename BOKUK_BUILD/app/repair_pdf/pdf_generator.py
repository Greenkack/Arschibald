"""
Datei: pdf_generator.py
Zweck: Erzeugt Angebots-PDFs für die Solar-App.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-03
"""
from __future__ import annotations

# pdf_generator.py
import os
import re

import base64
import io
import math
import traceback
from calculations_extended import run_all_extended_analyses
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
from theming.pdf_styles import get_theme

# Optional PDF Templates import
try:
    from pdf_templates import get_cover_letter_template, get_project_summary_template
    _PDF_TEMPLATES_AVAILABLE = True
except ImportError:
    _PDF_TEMPLATES_AVAILABLE = True
    # Fallback functions
    def get_cover_letter_template(*args, **kwargs):
        return None
    def get_project_summary_template(*args, **kwargs):
        return None
_REPORTLAB_AVAILABLE = True
_PYPDF_AVAILABLE = True

try:
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (Frame, Image, PageBreak, PageTemplate,
        Paragraph, SimpleDocTemplate, Spacer, Table,
        TableStyle, Flowable, KeepInFrame, KeepTogether)
    from reportlab.lib import pagesizes
    _REPORTLAB_AVAILABLE = True
except ImportError:
    pass
except Exception as e_reportlab_import:
    pass

try:
    from pypdf import PdfReader, PdfWriter
    _PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        _PYPDF_AVAILABLE = True
    except ImportError:
        class PdfReader: # type: ignore
            def __init__(self, *args, **kwargs): pass
            @property
            def pages(self): return []
        class PdfWriter: # type: ignore
            def __init__(self, *args, **kwargs): pass
            def add_page(self, page): pass
            def write(self, stream): pass
        _PYPDF_AVAILABLE = True
except Exception as e_pypdf_import:
    class PdfReader: # type: ignore
        def __init__(self, *args, **kwargs): pass
        @property
        def pages(self): return []
    class PdfWriter: # type: ignore
        def __init__(self, *args, **kwargs): pass
        def add_page(self, page): pass
        def write(self, stream): pass
    _PYPDF_AVAILABLE = True
class PDFGenerator:
    """Kapselt die gesamte PDF-Erstellungslogik."""

    def __init__(self, offer_data: Dict, module_order: List[Dict], theme_name: str, filename: str):
        self.offer_data = offer_data
        self.module_order = module_order
        self.theme = get_theme(theme_name)
        self.filename = filename
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Eigene Stile basierend auf dem Theme erstellen
        self.styles.add(ParagraphStyle(name='H1', fontName=self.theme["fonts"]["family_bold"],
                                        fontSize=self.theme["fonts"]["size_h1"],
                                        textColor=self.theme["colors"]["primary"]))
        self.styles.add(ParagraphStyle(name='Body', fontName=self.theme["fonts"]["family_main"],
                                        fontSize=self.theme["fonts"]["size_body"],
                                        textColor=self.theme["colors"]["text"], leading=14))

    def _header_footer(self, canvas, doc):
        """Erstellt die Kopf- und Fußzeile für jede Seite."""
        canvas.saveState()
        
        page_num = canvas.getPageNumber()
        
        # HEADER - ab Seite 2
        if page_num > 1:
            # Kapitelüberschrift links oben
            canvas.setFont("Helvetica", 10)
            canvas.setFillColor(colors.black)
            canvas.drawString(2*cm, self.height - 1.5*cm, "Angebot")
            
            # Horizontale Linie unter Header
            canvas.setStrokeColor(colors.grey)
            canvas.setLineWidth(0.5)
            canvas.line(2*cm, self.height - 2*cm, self.width - 2*cm, self.height - 2*cm)

        # FOOTER - alle Seiten
        # Horizontale Linie über Footer
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(0.5)
        canvas.line(2*cm, 1.5*cm, self.width - 2*cm, 1.5*cm)
        
        # Footer Text zentriert
        footer_text = f"Angebot, {datetime.now().strftime('%d.%m.%Y')} | Seite {page_num}"
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.black)
        text_width = canvas.stringWidth(footer_text, "Helvetica", 8)
        canvas.drawString((self.width - text_width) / 2, 1*cm, footer_text)
        
        canvas.restoreState()

    def create_pdf(self):
        """Hauptfunktion, die alle Module zusammensetzt und das PDF speichert."""
        doc = SimpleDocTemplate(self.filename, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=3*cm, bottomMargin=3*cm)

        module_map = self._get_module_map()

        for module_spec in self.module_order:
            module_id = module_spec["id"]
            draw_function = module_map.get(module_id)
            if draw_function:
                if module_id == "benutzerdefiniert":
                    draw_function(module_spec.get("content", {}))
                else:
                    draw_function()
                self.story.append(PageBreak())
        
        # Entferne den letzten PageBreak, um keine leere Seite zu erzeugen
        if self.story and isinstance(self.story[-1], PageBreak):
            self.story.pop()
            
        # Verwende die Header/Footer-Funktion für ALLE Seiten
        doc.build(self.story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)

    def _draw_cover_page(self):
        self.story.append(Spacer(1, 8*cm))
        self.story.append(Paragraph("Angebot", self.styles['H1']))
        self.story.append(Spacer(1, 0.5*cm))
        customer = self.offer_data.get("customer", {})
        self.story.append(Paragraph(f"für {customer.get('name', 'N/A')}", self.styles['Body']))
        self.story.append(Paragraph(f"Datum: {self.offer_data.get('date', 'N/A')}", self.styles['Body']))
        
    def _draw_cover_letter(self):
        text = get_cover_letter_template(
            customer_name=self.offer_data.get("customer", {}).get("name", "N/A"),
            offer_id=self.offer_data.get("offer_id", "N/A")
        ).replace('\n', '<br/>')
        self.story.append(Paragraph("Ihr persönliches Angebot", self.styles['H1']))
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph(text, self.styles['Body']))

    def _draw_offer_table(self):
        self.story.append(Paragraph("Angebotspositionen", self.styles['H1']))
        self.story.append(Spacer(1, 1*cm))

        data = [["Pos", "Beschreibung", "Menge", "Einzelpreis", "Gesamtpreis"]]
        items = self.offer_data.get("items", [])
        for i, item in enumerate(items):
            data.append([
                str(i + 1),
                item.get("name", "N/A"),
                str(item.get("quantity", 0)),
                f"{item.get('unit_price', 0):.2f} €",
                f"{item.get('total_price', 0):.2f} €"
            ])
        
        data.append(["", "", "", "Netto:", f"{self.offer_data.get('net_total', 0):.2f} €"])
        data.append(["", "", "", "MwSt. 19%:", f"{self.offer_data.get('vat', 0):.2f} €"])
        data.append(["", "", "", Paragraph("<b>Gesamt</b>", self.styles['Body']), f"{self.offer_data.get('grand_total', 0):.2f} €"])

        table = Table(data, colWidths=[1.5*cm, 8*cm, 2*cm, 2.5*cm, 3*cm])
        
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(self.theme["colors"]["table_header_bg"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor(self.theme["colors"]["header_text"])),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.theme["fonts"]["family_bold"]),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), HexColor(self.theme["colors"]["table_row_bg_odd"])),
            ('GRID', (0,0), (-1,-3), 1, HexColor(self.theme["colors"]["primary"])),
            ('ALIGN', (1,1), (1,-1), 'LEFT'), # Beschreibung linksbündig
        ])
        table.setStyle(style)
        self.story.append(table)

    # In pdf_generator.py, innerhalb der Klasse PDFGenerator

    # ... zu den anderen draw-Methoden hinzufügen
    def _draw_heatpump_section(self):
        if 'selected_heatpump_data' not in self.offer_data:
            return # Modul überspringen, wenn keine Daten vorhanden

        data = self.offer_data['selected_heatpump_data']
        
        self.story.append(Paragraph("Analyse Wärmepumpe", self.styles['H1']))
        self.story.append(Spacer(1, 1*cm))
        
        text = f"""
        Basierend auf Ihren Gebäudedaten wurde eine Heizlast von <b>{self.offer_data.get('heat_load_kw', 0):.2f} kW</b> ermittelt.
        Wir empfehlen folgendes Modell:
        <br/><br/>
        <b>Hersteller:</b> {data['manufacturer']}<br/>
        <b>Modell:</b> {data['model_name']}<br/>
        <b>Heizleistung:</b> {data['heating_output_kw']:.2f} kW<br/>
        <b>Jahresarbeitszahl (SCOP):</b> {data['scop']:.2f}<br/>
        <b>Geschätzter jährl. Stromverbrauch:</b> {data.get('annual_consumption', 0):.0f} kWh
        """
        self.story.append(Paragraph(text, self.styles['Body']))

    def _get_module_map(self):
        """Gibt die Mapping-Funktion für PDF-Module zurück."""
        return {
            "deckblatt": self._draw_cover_page,
            "anschreiben": self._draw_cover_letter,
            "angebotstabelle": self._draw_offer_table,
            "benutzerdefiniert": self._draw_custom_content,
            "waermepumpe": self._draw_heatpump_section,
        }

    def _draw_custom_content(self, content: Dict):
        content_type = content.get("type", "text")
        data = content.get("data")
        if not data: return

        if content_type == "image":
            try:
                self.story.append(Image(data, width=self.width - 4*cm, height=self.height/3, preserveAspectRatio=True))
            except Exception as e:
                self.story.append(Paragraph(f"Fehler beim Laden des Bildes: {e}", self.styles['Body']))
    
    def merge_pdfs(self, pdf_files: List[Union[str, bytes, io.BytesIO]]) -> bytes:
        """
        Führt mehrere PDF-Dateien zu einer einzigen zusammen.
        
        Args:
            pdf_files: Liste von PDF-Dateien (Pfade, Bytes oder BytesIO-Objekte)
            
        Returns:
            bytes: Die zusammengeführte PDF als Bytes
        """
        if not _PYPDF_AVAILABLE:
            raise RuntimeError("PyPDF ist nicht verfügbar für das Zusammenführen von PDFs")
            
        if not pdf_files:
            return b""
            
        merger = PdfWriter()
        
        try:
            for pdf_file in pdf_files:
                if isinstance(pdf_file, str):
                    # Pfad zu PDF-Datei
                    if os.path.exists(pdf_file):
                        with open(pdf_file, 'rb') as f:
                            reader = PdfReader(f)
                            for page in reader.pages:
                                merger.add_page(page)
                elif isinstance(pdf_file, bytes):
                    # PDF als Bytes
                    reader = PdfReader(io.BytesIO(pdf_file))
                    for page in reader.pages:
                        merger.add_page(page)
                elif isinstance(pdf_file, io.BytesIO):
                    # PDF als BytesIO
                    pdf_file.seek(0)  # Sicherstellung, dass wir am Anfang sind
                    reader = PdfReader(pdf_file)
                    for page in reader.pages:
                        merger.add_page(page)
                        
            # Zusammengeführte PDF in BytesIO schreiben
            output = io.BytesIO()
            merger.write(output)
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            # Fallback: Erste PDF zurückgeben wenn verfügbar
            if pdf_files:
                first_pdf = pdf_files[0]
                if isinstance(first_pdf, str) and os.path.exists(first_pdf):
                    with open(first_pdf, 'rb') as f:
                        return f.read()
                elif isinstance(first_pdf, bytes):
                    return first_pdf
                elif isinstance(first_pdf, io.BytesIO):
                    first_pdf.seek(0)
                    return first_pdf.getvalue()
            return b""

# =============== NEUE TEMPLATE-HAUPTAUSGABE (6 Seiten) API ==================
def generate_main_template_pdf_bytes(
    project_data: Dict[str, Any],
    analysis_results: Optional[Dict[str, Any]],
    company_info: Dict[str, Any],
    additional_pdf: Optional[bytes] = None,
) -> Optional[bytes]:
    """Erzeugt die 6-seitige Hauptausgabe basierend auf coords/ und pdf_templates_static/notext/.

    Nutzt pdf_template_engine: liest YML-Koordinaten, erstellt Text-Overlay nach
    Platzhalter-Mapping und fusioniert mit den sechs statischen Template-PDFs.
    """
    try:
        from pdf_template_engine import build_dynamic_data, generate_overlay, merge_with_background
    except Exception as e:
        print(f"pdf_template_engine nicht verfügbar: {e}")
        return None

    base_dir = os.path.dirname(os.path.abspath(__file__))
    coords_dir = Path(base_dir) / "coords"
    bg_dir = Path(base_dir) / "pdf_templates_static" / "notext"

    debug_templates = os.environ.get("DING_TEMPLATE_DEBUG", "0").lower() in {"1","true","yes","on"}
    if debug_templates:
        print("[TEMPLATE] build_dynamic_data start")
    dyn_data = build_dynamic_data(project_data, analysis_results, company_info)
    if debug_templates:
        print(f"[TEMPLATE] build_dynamic_data done keys={len(dyn_data)}")
    # Haupt-PDF mit korrekter "Seite x von XX"-Nummerierung, aber ohne Zusatzseiten anhängen
    try:
        total_pages = 6
        if additional_pdf:
            try:
                from pypdf import PdfReader
                import io as _io
                total_pages = 6 + len(PdfReader(_io.BytesIO(additional_pdf)).pages)
            except Exception:
                total_pages = 6
        if debug_templates:
            print(f"[TEMPLATE] generate_overlay call total_pages={total_pages}")
        overlay_bytes = generate_overlay(coords_dir, dyn_data, total_pages=total_pages)
        if debug_templates:
            print(f"[TEMPLATE] overlay size={len(overlay_bytes)} bytes")
        fused = merge_with_background(overlay_bytes, bg_dir)
        if debug_templates:
            print(f"[TEMPLATE] fused main6 size={len(fused)} bytes")
        return fused
    except Exception as e_gen:
        import traceback, sys
        print(f"[TEMPLATE] Fehler bei Overlay/Merge der 6-Seiten-PDF: {e_gen}")
        try:
            traceback.print_exc()
        except Exception:
            print("[TEMPLATE] (Traceback konnte nicht ausgegeben werden)")
        return None

def generate_offer_pdf_with_main_templates(
    project_data: Dict[str, Any],
    analysis_results: Optional[Dict[str, Any]],
    company_info: Dict[str, Any],
    company_logo_base64: Optional[str],
    selected_title_image_b64: Optional[str],
    selected_offer_title_text: str,
    selected_cover_letter_text: str,
    sections_to_include: Optional[List[str]],
    inclusion_options: Dict[str, Any],
    load_admin_setting_func: Callable,
    save_admin_setting_func: Callable,
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]],
    active_company_id: Optional[int],
    texts: Dict[str, str],
    use_modern_design: bool = True,
    **kwargs,
) -> Optional[bytes]:
    """Neue Gesamt-Generatorfunktion:
    1) Erzeuge 6-seitige Hauptausgabe per Templates (coords + notext PDFs)
    2) Erzeuge bisheriges PDF als Zusatz (ohne Deckblatt/Anschreiben)
    3) Hänge es an die 6 Seiten an und liefere Bytes
    """
    # Erzeuge optional die Zusatz-PDF zuerst, damit die 6-Seiten-Nummerierung "von XX" korrekt ist
    additional_pdf = None
    try:
        append_after_main6 = bool((inclusion_options or {}).get("append_additional_pages_after_main6", False))
    except Exception:
        append_after_main6 = False
    if append_after_main6:
        inclusion_options_mod = dict(inclusion_options or {})
        inclusion_options_mod["skip_cover_and_letter"] = True
        additional_pdf = generate_offer_pdf(
            project_data, analysis_results, company_info, company_logo_base64,
            selected_title_image_b64, selected_offer_title_text, selected_cover_letter_text,
            sections_to_include, inclusion_options_mod, load_admin_setting_func,
            save_admin_setting_func, list_products_func, get_product_by_id_func,
            db_list_company_documents_func, active_company_id, texts,
            use_modern_design=use_modern_design, disable_main_template_combiner=True,
            **{k: v for k, v in (kwargs or {}).items() if k != 'disable_main_template_combiner'},
        )

    main6 = generate_main_template_pdf_bytes(project_data, analysis_results, company_info, additional_pdf=additional_pdf)
    if main6 is None:
        # Fallback: Nur die alte Generierung
        return generate_offer_pdf(
            project_data, analysis_results, company_info, company_logo_base64,
            selected_title_image_b64, selected_offer_title_text, selected_cover_letter_text,
            sections_to_include, inclusion_options, load_admin_setting_func,
            save_admin_setting_func, list_products_func, get_product_by_id_func,
            db_list_company_documents_func, active_company_id, texts,
            use_modern_design=use_modern_design, **kwargs,
        )

    # Hilfsfunktion: Zusatzseiten mit Footer "Angebot, <Datum>" und "Seite x von XX" versehen
    def _overlay_footer_page_numbers(pdf_bytes: bytes, start_number: int, total_pages: int, logo_b64: Optional[str] = None, footer_left_text: Optional[str] = None) -> bytes:
        try:
            if not pdf_bytes:
                return pdf_bytes
            # ReportLab/PyPDF verfügbar?
            if not _PYPDF_AVAILABLE or not _REPORTLAB_AVAILABLE:
                return pdf_bytes
            reader = PdfReader(io.BytesIO(pdf_bytes))
            writer = PdfWriter()
            # Erstelle einmal einen leeren Overlay-Buffer; pro Seite neu befüllen
            from reportlab.pdfgen import canvas as _rl_canvas
            from reportlab.lib.colors import black, white, HexColor, Color
            from datetime import datetime as _dt
            date_text = f"Angebot, {_dt.now().strftime('%d.%m.%Y')}"
            for idx, page in enumerate(reader.pages):
                # Seitengröße erfassen
                box = page.mediabox
                pw = float(box.width)
                ph = float(box.height)
                # Overlay-PDF mit gleicher Seitengröße erzeugen
                overlay_buf = io.BytesIO()
                canv = _rl_canvas.Canvas(overlay_buf, pagesize=(pw, ph))
                # Dekoratives Dreieck oben rechts (wie Hauptseiten)
                try:
                    tri = _rl_canvas.Path()
                except Exception:
                    tri = None
                accent = Color(27/255.0, 54/255.0, 112/255.0)
                try:
                    canv.saveState()
                    canv.setFillColor(accent)
                    canv.setStrokeColor(accent)
                    size = 36.0
                    x0, y0 = pw, ph
                    p = canv.beginPath()
                    p.moveTo(x0, y0)
                    p.lineTo(x0 - size, y0)
                    p.lineTo(x0, y0 - size)
                    p.close()
                    canv.drawPath(p, stroke=0, fill=1)
                finally:
                    try:
                        canv.restoreState()
                    except Exception:
                        pass

                # Footer-Hintergrundleiste (minimal bläulicher als Primärfarbe)
                bar_height = 36
                try:
                    # Primärfarbe leicht in Richtung Blau schieben
                    _hex = str(PRIMARY_COLOR_HEX).strip()
                    if _hex.startswith('#') and len(_hex) == 7:
                        r = int(_hex[1:3], 16); g = int(_hex[3:5], 16); b = int(_hex[5:7], 16)
                        b = min(255, b + 16)  # +16 Blauanteil
                        footer_hex = f"#{r:02X}{g:02X}{b:02X}"
                    else:
                        footer_hex = _hex
                    canv.setFillColor(HexColor(footer_hex))
                except Exception:
                    # Fallback dunkelblau
                    canv.setFillColor(HexColor('#1B3670'))
                canv.setStrokeColor(HexColor('#000000'))
                canv.rect(0, 0, pw, bar_height, stroke=0, fill=1)
                # Footer-Text-Style (weiß)
                font_name = "Helvetica-Bold"; font_size = 9
                canv.setFillColor(white)
                canv.setFont(font_name, font_size)
                # Firmenlogo oben links (optional)
                if logo_b64:
                    try:
                        img_bytes = base64.b64decode(logo_b64)
                        img = ImageReader(io.BytesIO(img_bytes))
                        max_w, max_h = 120, 50
                        # Position: 20pt vom linken Rand, 20pt vom oberen Rand (unterhalb)
                        canv.drawImage(img, 20, ph - 20 - max_h, width=max_w, height=max_h, preserveAspectRatio=True, mask='auto')
                    except Exception:
                        pass
                # Zentrierter Datums-Text (vertikal mittig in der Leiste)
                center_y = float(bar_height) / 2.0
                tw = canv.stringWidth(date_text, font_name, font_size)
                canv.drawString((pw - tw) / 2.0, center_y, date_text)
                # Linker Footer-Text: Kundenname, falls vorhanden
                if footer_left_text:
                    try:
                        canv.drawString(20, center_y, str(footer_left_text))
                    except Exception:
                        pass
                # Rechte Nummer "Seite x von XX"
                page_num = start_number + idx
                right_text = f"Seite {page_num} von {total_pages}"
                tw_r = canv.stringWidth(right_text, font_name, font_size)
                canv.drawString(pw - 18 - tw_r, center_y, right_text)
                canv.showPage(); canv.save()
                # Overlay zurück an den Anfang und mergen
                overlay_buf.seek(0)
                ov_reader = PdfReader(overlay_buf)
                ov_page = ov_reader.pages[0]
                try:
                    page.merge_page(ov_page)
                except Exception:
                    # Fallback für ältere PyPDF2 APIs
                    page.mergePage(ov_page)  # type: ignore
                writer.add_page(page)
            out_buf = io.BytesIO(); writer.write(out_buf)
            return out_buf.getvalue()
        except Exception:
            return pdf_bytes

    try:
        from pypdf import PdfReader, PdfWriter
        base_reader = PdfReader(io.BytesIO(main6))
        writer = PdfWriter()
        for p in base_reader.pages: writer.add_page(p)
        if additional_pdf:
            # Seitenanzahl ermitteln (gesamt = 6 + n)
            tmp_reader = PdfReader(io.BytesIO(additional_pdf))
            total_pages = 6 + len(tmp_reader.pages)
            # Zusatzseiten mit Footer versehen: Startnummer = 7
            logo_b64 = None
            try:
                logo_b64 = company_logo_base64 or (company_info.get('logo_base64') if isinstance(company_info, dict) else None)
            except Exception:
                logo_b64 = company_logo_base64
            # Kundenname für linken Footer
            try:
                cust = (project_data or {}).get('customer_data', {})
                first = str(cust.get('first_name') or '').strip()
                last = str(cust.get('last_name') or '').strip()
                sal = str(cust.get('salutation') or '').strip()
                title = str(cust.get('title') or '').strip()
                name_parts = [p for p in [sal, title, first, last] if p]
                footer_left = ' '.join(name_parts)
            except Exception:
                footer_left = None
            additional_pdf = _overlay_footer_page_numbers(additional_pdf, start_number=7, total_pages=total_pages, logo_b64=logo_b64, footer_left_text=footer_left)
            add_reader = PdfReader(io.BytesIO(additional_pdf))
            for p in add_reader.pages: writer.add_page(p)
        buf = io.BytesIO(); writer.write(buf)
        return buf.getvalue()
    except Exception:
        # Falls Zusammenführen fehlschlägt, gib die 6 Seiten zurück
        return main6

_PDF_GENERATOR_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Da pdf_generator.py im selben Verzeichnis wie der data/ Ordner liegt, ist der Basis-Pfad korrekt
PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN = os.path.join(_PDF_GENERATOR_BASE_DIR, "data", "product_datasheets")
COMPANY_DOCS_BASE_DIR_PDF_GEN = os.path.join(_PDF_GENERATOR_BASE_DIR, "data", "company_docs")

# Dynamische PDF-Overlay-Pfade (Koordinatendateien und PDF-Hintergründe)
# Der coords-Ordner enthält seite1.yml … seite6.yml mit den Positionsinformationen.
COORDS_DIR = os.path.join(_PDF_GENERATOR_BASE_DIR, "coords")

# Der Ordner pdf_templates_static/notext enthält die sechs PDF-Vorlagen nt-nt-01 … nt-nt-06.
BG_DIR = os.path.join(_PDF_GENERATOR_BASE_DIR, "pdf_templates_static", "notext")

# Vorlage für die dynamischen Textfelder in den Overlays.
# Die Schlüssel entsprechen den Platzhaltern, die in den YML-Dateien als Beispieldaten hinterlegt sind.
DYNAMIC_DATA_TEMPLATE: Dict[str, str] = {
    "customer_name": "",
    "customer_street": "",
    "customer_city_zip": "",
    "customer_phone": "",
    "customer_email": "",
    "savings_with_battery": "",
    "savings_without_battery": "",
    "pv_power_kWp": "",
    "battery_capacity_kWh": "",
    "annual_yield_kwh": "",
    "self_sufficiency": "",
    "self_consumption": ""
}


def get_text(texts_dict: Dict[str, str], key: str, fallback_text_value: Optional[str] = None) -> str:
    if not isinstance(texts_dict, dict): return fallback_text_value if fallback_text_value is not None else key
    if fallback_text_value is None: fallback_text_value = key.replace("_", " ").title() + " (PDF-Text fehlt)"
    retrieved = texts_dict.get(key, fallback_text_value)
    return str(retrieved)

def format_kpi_value(value: Any, unit: str = "", na_text_key: str = "not_applicable_short", precision: int = 2, texts_dict: Optional[Dict[str,str]] = None) -> str:
    current_texts = texts_dict if texts_dict is not None else {}
    na_text = get_text(current_texts, na_text_key, "k.A.")
    if value is None or (isinstance(value, (float, int)) and math.isnan(value)): return na_text
    if isinstance(value, str) and value == na_text: return value
    if isinstance(value, str):
        try:
            cleaned_value_str = value
            if '.' in value and ',' in value:
                 if value.rfind('.') > value.rfind(','): cleaned_value_str = value.replace(',', '')
                 elif value.rfind(',') > value.rfind('.'): cleaned_value_str = value.replace('.', '')
            cleaned_value_str = cleaned_value_str.replace(',', '.')
            value = float(cleaned_value_str)
        except ValueError: return value

    if isinstance(value, (int, float)):
        if math.isinf(value): return get_text(current_texts, "value_infinite", "Nicht berechenbar")
        if unit == "Jahre": return get_text(current_texts, "years_format_string_pdf", "{val:.1f} Jahre").format(val=value)
        
        formatted_num_en = f"{value:,.{precision}f}"
        formatted_num_de = formatted_num_en.replace(",", "#TEMP#").replace(".", ",").replace("#TEMP#", ".")
        return f"{formatted_num_de} {unit}".strip()
    return str(value)

def _sanitize_chart_title(raw_title: str) -> str:
    """Entfernt alle Klammerzusätze wie "(Jahr 1)", "(3D)" aus einem Titel und trimmt Whitespace."""
    try:
        if not isinstance(raw_title, str):
            return str(raw_title)
        # Entferne alle Teilstrings in runden Klammern inkl. führender Leerzeichen
        cleaned = re.sub(r"\s*\([^)]*\)", "", raw_title)
        # Mehrfache Leerzeichen normalisieren
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned
    except Exception:
        return raw_title

# --- Vereinfachter Wrapper für alte/vereinfachte Aufrufe (erzwingt neuen Template-Flow) ---
def generate_offer_pdf_simple(
    project_data: Dict[str, Any],
    analysis_results: Optional[Dict[str, Any]],
    company_info: Dict[str, Any],
    texts: Dict[str, str],
    inclusion_options: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Optional[bytes]:
    def _noop(*a, **k):
        return None
    inclusion_options = inclusion_options or {}
    try:
        return generate_offer_pdf_with_main_templates(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            company_logo_base64=(company_info or {}).get('logo_base64'),
            selected_title_image_b64=None,
            selected_offer_title_text="",
            selected_cover_letter_text="",
            sections_to_include=None,
            inclusion_options=inclusion_options,
            load_admin_setting_func=kwargs.get('load_admin_setting_func', _noop),
            save_admin_setting_func=kwargs.get('save_admin_setting_func', _noop),
            list_products_func=kwargs.get('list_products_func', _noop),
            get_product_by_id_func=kwargs.get('get_product_by_id_func', _noop),
            db_list_company_documents_func=kwargs.get('db_list_company_documents_func', lambda *a, **k: []),
            active_company_id=kwargs.get('active_company_id'),
            texts=texts,
            use_modern_design=kwargs.get('use_modern_design', True),
        )
    except Exception as e:
        print(f"WARN generate_offer_pdf_simple Fallback: {e}")
        return None

def _build_chart_kpi_html(chart_key: str, analysis: Dict[str, Any], texts: Dict[str, str]) -> str:
    """Erzeugt eine kompakte KPI-Zeile passend zum Diagramm. Leerstring, wenn nichts Passendes vorhanden ist."""
    kpis: List[str] = []

    def add(label_key: str, fallback_label: str, value: Any, unit: str = "", precision: int = 1, na_key: str = "value_not_available_short_pdf") -> None:
        if value is None:
            return
        formatted = format_kpi_value(value, unit=unit, precision=precision, texts_dict=texts, na_text_key=na_key)
        kpis.append(f"<b>{get_text(texts, label_key, fallback_label)}:</b> {formatted}")

    try:
        # Abdeckung Gesamtverbrauch / Autarkiegrad
        if chart_key in {"consumption_coverage_pie_chart_bytes", "selfuse_ratio_switcher_chart_bytes"}:
            add("self_supply_rate_percent_pdf", "Autarkiegrad (ca.)", analysis.get("self_supply_rate_percent"), "%", 1)

        # Nutzung PV-Strom / Eigenverbrauchsquote
        if chart_key in {"pv_usage_pie_chart_bytes", "selfuse_stack_switcher_chart_bytes"}:
            add("self_consumption_percent_pdf", "Eigenverbrauch (ca.)", analysis.get("self_consumption_percent"), "%", 1)

        # Produktion
        if chart_key in {"monthly_prod_cons_chart_bytes", "yearly_production_switcher_chart_bytes", "yearly_production_chart_bytes", "daily_production_switcher_chart_bytes", "weekly_production_switcher_chart_bytes"}:
            add("annual_pv_production_kwh_pdf", "Jährliche PV-Produktion (ca.)", analysis.get("annual_pv_production_kwh"), "kWh", 0)

        # Kosten / Einnahmen / Vorteil Jahr 1
        if chart_key in {"cost_projection_chart_bytes", "income_projection_switcher_chart_bytes"}:
            add("annual_financial_benefit_pdf", "Finanzieller Vorteil (Jahr 1, ca.)", analysis.get("annual_financial_benefit_year1"), "€", 0)

        # Wirtschaftlichkeit / Amortisation / ROI
        if chart_key in {"cumulative_cashflow_chart_bytes", "break_even_chart_bytes", "amortisation_chart_bytes", "roi_comparison_switcher_chart_bytes"}:
            add("amortization_time_years_pdf", "Amortisationszeit (ca.)", analysis.get("amortization_time_years"), "Jahre", 1)
            add("simple_roi_percent_label_pdf", "Einfache Rendite (Jahr 1, ca.)", analysis.get("simple_roi_percent"), "%", 1)

        # CO2
        if chart_key in {"co2_savings_chart_bytes", "co2_savings_value_switcher_chart_bytes"}:
            add("annual_co2_savings_label_pdf", "Jährliche CO₂-Einsparung", analysis.get("annual_co2_savings_kg"), "kg", 0)
    except Exception:
        # still: keine KPIs anzeigen, wenn etwas schiefgeht
        pass

    return " • ".join(kpis)

STYLES: Any = {}
FONT_NORMAL = "Helvetica"; FONT_BOLD = "Helvetica-Bold"; FONT_ITALIC = "Helvetica-Oblique"
# KORREKTUR: Standardfarben gemäß neuen Designrichtlinien
PRIMARY_COLOR_HEX = "#1B365D"  # Dunkelblau - Professionell und vertrauensvoll 
SECONDARY_COLOR_HEX = "#2E8B57" # Solargrün - Nachhaltigkeit und Energie
ACCENT_COLOR_HEX = "#FFB347"       # Sonnenorange - Wärme und Optimismus
TEXT_COLOR_HEX = "#2C3E50"         # Anthrazit - Optimale Lesbarkeit
BACKGROUND_COLOR_HEX = "#F8F9FA"   # Hellgrau - Modern und Clean
TEXT_COLOR_HEX = "#333333"
SEPARATOR_LINE_COLOR_HEX = "#E9ECEF" # Subtile, moderne Linienfarbe

# Moderne Farbpalette als Dictionary für bessere Zugänglichkeit
COLORS = {
    'accent_primary': PRIMARY_COLOR_HEX,
    'accent_secondary': SECONDARY_COLOR_HEX,
    'accent_orange': ACCENT_COLOR_HEX,
    'text_dark': TEXT_COLOR_HEX,
    'background_light': BACKGROUND_COLOR_HEX,
    'separator_line': SEPARATOR_LINE_COLOR_HEX,
    'table_header_bg': PRIMARY_COLOR_HEX,
    'table_header_text': '#FFFFFF',
    'table_row_bg': '#FAFBFC',
    'table_alt_row_bg': '#F1F3F4',
    'table_border': '#E1E5E9',
    'success_green': '#28A745',
    'warning_orange': '#FFC107',
    'error_red': '#DC3545',
    'info_blue': '#17A2B8'
}

if _REPORTLAB_AVAILABLE:
    STYLES = getSampleStyleSheet()
    STYLES.add(ParagraphStyle(name='NormalLeft', alignment=TA_LEFT, fontName=FONT_NORMAL, fontSize=10, leading=12, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='NormalRight', alignment=TA_RIGHT, fontName=FONT_NORMAL, fontSize=10, leading=12, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='NormalCenter', alignment=TA_CENTER, fontName=FONT_NORMAL, fontSize=10, leading=12, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='Footer', parent=STYLES['NormalCenter'], fontName=FONT_ITALIC, fontSize=8, textColor=colors.darkgrey)) # Dunkleres Grau für Footer
    STYLES.add(ParagraphStyle(name='OfferTitle', parent=STYLES['h1'], fontName=FONT_BOLD, fontSize=24, alignment=TA_CENTER, spaceBefore=1.5*cm, spaceAfter=1.5*cm, textColor=colors.HexColor(PRIMARY_COLOR_HEX), leading=28)) # Größer und eleganter
    STYLES.add(ParagraphStyle(name='SectionTitle', parent=STYLES['h2'], fontName=FONT_BOLD, fontSize=16, spaceBefore=1.2*cm, spaceAfter=0.8*cm, keepWithNext=1, textColor=colors.HexColor(PRIMARY_COLOR_HEX), leading=20)) # Moderner
    STYLES.add(ParagraphStyle(name='SubSectionTitle', parent=STYLES['h3'], fontName=FONT_BOLD, fontSize=13, spaceBefore=1*cm, spaceAfter=0.5*cm, keepWithNext=1, textColor=colors.HexColor(SECONDARY_COLOR_HEX), leading=16)) # Sekundärfarbe für Abwechslung
    STYLES.add(ParagraphStyle(name='ComponentTitle', parent=STYLES['SubSectionTitle'], fontSize=11, spaceBefore=0.5*cm, spaceAfter=0.2*cm, alignment=TA_LEFT, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='CompanyInfoDeckblatt', parent=STYLES['NormalCenter'], fontName=FONT_NORMAL, fontSize=9, leading=11, spaceAfter=0.5*cm, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='CoverLetter', parent=STYLES['NormalLeft'], fontSize=11, leading=15, spaceBefore=0.5*cm, spaceAfter=0.5*cm, alignment=TA_JUSTIFY, firstLineIndent=0, leftIndent=0, rightIndent=0, textColor=colors.HexColor(TEXT_COLOR_HEX))) # Etwas mehr Zeilenabstand    # Neuer Stil für rechtsbündige Kundenadresse auf Deckblatt
    STYLES.add(ParagraphStyle(name='CustomerAddressDeckblattRight', parent=STYLES['NormalRight'], fontSize=10, leading=12, spaceBefore=0.5*cm, spaceAfter=0.8*cm, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='CustomerAddressInner', parent=STYLES['NormalLeft'], fontSize=10, leading=12, spaceBefore=0.5*cm, spaceAfter=0.8*cm, textColor=colors.HexColor(TEXT_COLOR_HEX))) # Für Anschreiben etc.
    # FEHLENDER STYLE - CustomerAddress (allgemein)
    STYLES.add(ParagraphStyle(name='CustomerAddress', parent=STYLES['NormalLeft'], fontSize=10, leading=12, spaceBefore=0.5*cm, spaceAfter=0.8*cm, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    
    STYLES.add(ParagraphStyle(name='TableText', parent=STYLES['NormalLeft'], fontName=FONT_NORMAL, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX))) # Helvetica für Tabellentext
    STYLES.add(ParagraphStyle(name='TableTextSmall', parent=STYLES['NormalLeft'], fontName=FONT_NORMAL, fontSize=8, leading=10, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='TableNumber', parent=STYLES['NormalRight'], fontName=FONT_NORMAL, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='TableLabel', parent=STYLES['NormalLeft'], fontName=FONT_BOLD, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    # KORREKTUR: Tabellenheader Farbe und Textfarbe
    STYLES.add(ParagraphStyle(name='TableHeader', parent=STYLES['NormalCenter'], fontName=FONT_BOLD, fontSize=9, leading=11, textColor=colors.white, backColor=colors.HexColor(PRIMARY_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='TableBoldRight', parent=STYLES['NormalRight'], fontName=FONT_BOLD, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='ImageCaption', parent=STYLES['NormalCenter'], fontName=FONT_ITALIC, fontSize=8, spaceBefore=0.1*cm, textColor=colors.grey))
    STYLES.add(ParagraphStyle(name='ChartTitle', parent=STYLES['SubSectionTitle'], alignment=TA_CENTER, spaceBefore=0.6*cm, spaceAfter=0.2*cm, fontSize=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='ChapterHeader', parent=STYLES['NormalRight'], fontName=FONT_NORMAL, fontSize=9, textColor=colors.grey, alignment=TA_RIGHT))

    TABLE_STYLE_DEFAULT = TableStyle([
        ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
        ('FONTNAME',(0,0),(0,-1),FONT_BOLD), ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('FONTNAME',(1,0),(1,-1),FONT_NORMAL),('ALIGN',(1,0),(1,-1),'LEFT'), # Werte linksbündig für Standardtabelle
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)), # Dezente Gridlinien
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),3*mm), ('RIGHTPADDING',(0,0),(-1,-1),3*mm),
        ('TOPPADDING',(0,0),(-1,-1),2*mm), ('BOTTOMPADDING',(0,0),(-1,-1),2*mm)
    ])
    # KORREKTUR: DATA_TABLE_STYLE für Konsistenz
    DATA_TABLE_STYLE = TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor(PRIMARY_COLOR_HEX)), # Kopfzeile Primärfarbe
        ('TEXTCOLOR',(0,0),(-1,0),colors.white), # Kopfzeile Text weiß
        ('FONTNAME',(0,0),(-1,0),FONT_BOLD),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('FONTNAME',(0,1),(-1,-1),FONT_NORMAL), # Datenzellen Helvetica
        ('ALIGN',(0,1),(0,-1),'LEFT'), # Erste Datenspalte links
        ('ALIGN',(1,1),(-1,-1),'RIGHT'), # Andere Datenspalten rechts (für Zahlen)
        ('LEFTPADDING',(0,0),(-1,-1),2*mm), ('RIGHTPADDING',(0,0),(-1,-1),2*mm),
        ('TOPPADDING',(0,0),(-1,-1),1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1),1.5*mm), 
        ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)) # Textfarbe Datenzellen
    ])
    PRODUCT_TABLE_STYLE = TableStyle([
        ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
        ('FONTNAME',(0,0),(0,-1),FONT_BOLD), ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('FONTNAME',(1,0),(1,-1),FONT_NORMAL), ('ALIGN',(1,0),(1,-1),'LEFT'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),2*mm), ('RIGHTPADDING',(0,0),(-1,-1),2*mm),
        ('TOPPADDING',(0,0),(-1,-1),1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1),1.5*mm)
    ])
    PRODUCT_MAIN_TABLE_STYLE = TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)])

    # MODERNE TABELLENSTYLES mit Zebra-Streifen
    def create_zebra_table_style(num_rows, header_bg=PRIMARY_COLOR_HEX, alt_bg=BACKGROUND_COLOR_HEX):
        """Erstellt einen modernen Tabellenstil mit Zebra-Streifen"""
        style = [
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(header_bg)), # Header
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),FONT_BOLD),
            ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('FONTNAME',(0,1),(-1,-1),FONT_NORMAL),
            ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
            ('LEFTPADDING',(0,0),(-1,-1),3*mm),
            ('RIGHTPADDING',(0,0),(-1,-1),3*mm),
            ('TOPPADDING',(0,0),(-1,-1),2.5*mm),
            ('BOTTOMPADDING',(0,0),(-1,-1),2.5*mm),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
        ]
        # Zebra-Streifen für ungerade Zeilen
        for row in range(1, num_rows):
            if row % 2 == 0:  # Jede zweite Zeile
                style.append(('BACKGROUND',(0,row),(-1,row),colors.HexColor(alt_bg)))
        return TableStyle(style)
        
    # MODERNE PRODUKT-TABELLE mit Schatten-Effekt
    MODERN_PRODUCT_TABLE_STYLE = TableStyle([
        ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
        ('FONTNAME',(0,0),(0,-1),FONT_BOLD), 
        ('FONTNAME',(1,0),(1,-1),FONT_NORMAL),
        ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('ALIGN',(1,0),(1,-1),'LEFT'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),4*mm),
        ('RIGHTPADDING',(0,0),(-1,-1),4*mm),
        ('TOPPADDING',(0,0),(-1,-1),3*mm),
        ('BOTTOMPADDING',(0,0),(-1,-1),3*mm),
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#FFFFFF")),
        ('BOX',(0,0),(-1,-1),1,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
        ('LINEBELOW',(0,0),(-1,0),2,colors.HexColor(PRIMARY_COLOR_HEX)), # Elegante Unterstreichung
    ])

class PageNumCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self._page_layout_callback = kwargs.pop('onPage_callback', None)
        self._callback_kwargs = kwargs.pop('callback_kwargs', {})
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.total_pages = 0 
        self.current_chapter_title_for_header = '' 
    def showPage(self): 
        self._saved_page_states.append(dict(self.__dict__))
        super().showPage()
    
    def save(self):
        self.total_pages = len(self._saved_page_states)
        for state_idx, state in enumerate(self._saved_page_states):
            self.__dict__.update(state) 
            self._pageNumber = state_idx + 1 
            if self._page_layout_callback:
                self._page_layout_callback(canvas_obj=self, doc_template=self._doc, **self._callback_kwargs)
        super().save()

class SetCurrentChapterTitle(Flowable):
    def __init__(self, title): Flowable.__init__(self); self.title = title
    def wrap(self, availWidth, availHeight): return 0,0
    def draw(self):
        if hasattr(self, 'canv'): self.canv.current_chapter_title_for_header = self.title

# Einfache HRFlowable für Trennlinien, falls die ReportLab Version sie nicht direkt hat
class SimpleHRFlowable(Flowable):
    def __init__(self, width="100%", thickness=0.5, color=colors.HexColor(SEPARATOR_LINE_COLOR_HEX), spaceBefore=0.2*cm, spaceAfter=0.2*cm, vAlign='BOTTOM'):
        Flowable.__init__(self)
        self.width_spec = width
        self.thickness = thickness
        self.color = color
        self.spaceBefore = spaceBefore
        self.spaceAfter = spaceAfter
        self.vAlign = vAlign # Kann 'TOP', 'MIDDLE', 'BOTTOM' sein

    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        # y-Position anpassen basierend auf vAlign und Höhe des Flowables (nur thickness)
        y_pos = 0
        if self.vAlign == 'TOP':
            y_pos = -self.thickness 
        elif self.vAlign == 'MIDDLE':
            y_pos = -self.thickness / 2.0
        # Für 'BOTTOM' ist y_pos = 0 korrekt

        self.canv.line(0, y_pos, self.drawWidth, y_pos) # drawWidth wird von ReportLab gesetzt
        self.canv.restoreState()

    def wrap(self, availWidth, availHeight):
        self.drawWidth = availWidth # Nutze die verfügbare Breite
        if isinstance(self.width_spec, str) and self.width_spec.endswith('%'):
            self.drawWidth = availWidth * (float(self.width_spec[:-1]) / 100.0)
        elif isinstance(self.width_spec, (int, float)):
            self.drawWidth = self.width_spec
        return self.drawWidth, self.thickness + self.spaceBefore + self.spaceAfter

    def getSpaceBefore(self):
        return self.spaceBefore

    def getSpaceAfter(self):
        return self.spaceAfter

class SetCurrentChapterTitle(Flowable):
    def __init__(self, title): Flowable.__init__(self); self.title = title
    def wrap(self, availWidth, availHeight): return 0,0
    def draw(self):
        if hasattr(self, 'canv'): self.canv.current_chapter_title_for_header = self.title

def _update_styles_with_dynamic_colors(design_settings: Dict[str, str]):
    global PRIMARY_COLOR_HEX, SECONDARY_COLOR_HEX, SEPARATOR_LINE_COLOR_HEX, STYLES, DATA_TABLE_STYLE
    if not _REPORTLAB_AVAILABLE: return

    PRIMARY_COLOR_HEX = design_settings.get('primary_color', "#0055A4")
    # SECONDARY_COLOR_HEX wird aktuell nicht stark verwendet, da #F2F2F2 sehr hell ist.
    # Für Hintergründe etc. können wir es definieren, aber Tabellenheader nutzen Primärfarbe.
    SECONDARY_COLOR_HEX = design_settings.get('secondary_color', "#F2F2F2") 
    SEPARATOR_LINE_COLOR_HEX = design_settings.get('separator_color', "#CCCCCC") # Eigene Farbe für Trennlinien

    if STYLES: # Nur wenn STYLES initialisiert wurde
        STYLES['OfferTitle'].textColor = colors.HexColor(PRIMARY_COLOR_HEX)
        STYLES['SectionTitle'].textColor = colors.HexColor(PRIMARY_COLOR_HEX)
        STYLES['SubSectionTitle'].textColor = colors.HexColor(PRIMARY_COLOR_HEX) # Subsektionen auch in Primärfarbe
        
        # Tabellenheader explizit mit Primärfarbe und weißem Text
        STYLES['TableHeader'].backColor = colors.HexColor(PRIMARY_COLOR_HEX)
        STYLES['TableHeader'].textColor = colors.white
        
        DATA_TABLE_STYLE = TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(PRIMARY_COLOR_HEX)), 
            ('TEXTCOLOR',(0,0),(-1,0),colors.white), 
            ('FONTNAME',(0,0),(-1,0),FONT_BOLD), ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'), ('FONTNAME',(0,1),(-1,-1),FONT_NORMAL),
            ('ALIGN',(0,1),(0,-1),'LEFT'), ('ALIGN',(1,1),(-1,-1),'RIGHT'),
            ('LEFTPADDING',(0,0),(-1,-1),2*mm), ('RIGHTPADDING',(0,0),(-1,-1),2*mm),
            ('TOPPADDING',(0,0),(-1,-1),1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1),1.5*mm), 
            ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor(TEXT_COLOR_HEX))
        ])


def _get_image_flowable(image_data_input: Optional[Union[str, bytes]], desired_width: float, texts: Dict[str, str], caption_text_key: Optional[str] = None, max_height: Optional[float] = None, align: str = 'CENTER') -> List[Any]:
    flowables: List[Any] = []
    if not _REPORTLAB_AVAILABLE: return flowables
    img_data_bytes: Optional[bytes] = None

    if isinstance(image_data_input, str) and image_data_input.strip().lower() not in ["", "none", "null", "nan"]:
        try:
            if image_data_input.startswith('data:image'): image_data_input = image_data_input.split(',', 1)[1]
            img_data_bytes = base64.b64decode(image_data_input)
        except Exception: img_data_bytes = None 
    elif isinstance(image_data_input, bytes): img_data_bytes = image_data_input
    
    if img_data_bytes:
        try:
            if not img_data_bytes: raise ValueError("Bilddaten sind leer nach Verarbeitung.")
            img_file_like = io.BytesIO(img_data_bytes)
            img_reader = ImageReader(img_file_like)
            iw, ih = img_reader.getSize()
            if iw <= 0 or ih <= 0: raise ValueError(f"Ungültige Bilddimensionen: w={iw}, h={ih}")
            aspect = ih / float(iw) if iw > 0 else 1.0
            img_h_calc = desired_width * aspect; img_w_final, img_h_final = desired_width, img_h_calc
            if max_height and img_h_calc > max_height: img_h_final = max_height; img_w_final = img_h_final / aspect if aspect > 0 else desired_width
            
            # KORREKTUR: Stelle sicher, dass img_w_final und img_h_final positiv sind
            if img_w_final <=0 or img_h_final <=0:
                raise ValueError(f"Finale Bilddimensionen ungültig: w={img_w_final}, h={img_h_final}")

            img = Image(io.BytesIO(img_data_bytes), width=img_w_final, height=img_h_final)
            img.hAlign = align.upper(); flowables.append(img)
            if caption_text_key:
                caption_text = get_text(texts, caption_text_key, "")
                if caption_text and not caption_text.startswith(caption_text_key) and not caption_text.endswith("(PDF-Text fehlt)"):
                    flowables.append(Spacer(1, 0.1*cm)); flowables.append(Paragraph(caption_text, STYLES['ImageCaption']))
        except Exception: 
            if caption_text_key :
                caption_text_fb = get_text(texts, caption_text_key, "")
                if caption_text_fb and not caption_text_fb.startswith(caption_text_key):
                     flowables.append(Paragraph(f"<i>({caption_text_fb}: {get_text(texts, 'image_not_available_pdf', 'Bild nicht verfügbar')})</i>", STYLES['ImageCaption']))
    elif caption_text_key:
        caption_text_fb = get_text(texts, caption_text_key, "")
        if caption_text_fb and not caption_text_fb.startswith(caption_text_key):
            flowables.append(Paragraph(f"<i>({caption_text_fb}: {get_text(texts, 'image_not_available_pdf', 'Bild nicht verfügbar')})</i>", STYLES['ImageCaption']))
    return flowables

def _draw_cover_page(c: canvas.Canvas, theme: Dict, offer_data: Dict):
    c.setFont(theme["fonts"]["family_main"], 40)
    c.setFillColor(theme["colors"]["primary"])
    c.drawCentredString(A4[0] / 2, A4[1] / 2 + 5*cm, "Angebot")
    # ... weitere Details für das Deckblatt ...
    c.showPage()

def _draw_cover_letter(c: canvas.Canvas, theme: Dict, offer_data: Dict):
    text_content = get_cover_letter_template(
        customer_name=offer_data["customer"]["name"],
        offer_id=offer_data["offer_id"]
    )
    # ... Logik zum Rendern des Textes auf der Seite ...
    c.showPage()

def _draw_offer_table(c: canvas.Canvas, theme: Dict, offer_data: Dict):
    # ... Logik zum Zeichnen der Angebotstabelle mit Positionen und Preisen ...
    c.showPage()
    
def _draw_custom_content(c: canvas.Canvas, theme: Dict, content: Dict):
    # Diese Funktion verarbeitet die vom Benutzer hochgeladenen Inhalte
    if content.get("type") == "text":
        # Rendere Text
        pass
    elif content.get("type") == "image":
        # Platziere Bild
        image_path = content.get("data")
        c.drawImage(image_path, 1*cm, 1*cm, width=18*cm, preserveAspectRatio=True)
    c.showPage()

# Mapping von Modul-Namen (aus der UI) zu den Zeichenfunktionen
MODULE_MAP = {
    "deckblatt": _draw_cover_page,
    "anschreiben": _draw_cover_letter,
    "angebotstabelle": _draw_offer_table,
    "benutzerdefiniert": _draw_custom_content,
    # Weitere Module hier hinzufügen (z.B. für Analysen, Datenblätter etc.)
}

def _draw_extended_analysis(c: canvas.Canvas, theme: Dict, offer_data: Dict):
    """Zeichnet die Seite mit den erweiterten Wirtschaftlichkeitsanalysen."""
    c.setFont(theme["fonts"]["family_main"], theme["fonts"]["size_h2"])
    c.setFillColor(theme["colors"]["primary"])
    c.drawString(2*cm, A4[1] - 2*cm, "Detaillierte Wirtschaftlichkeitsanalyse")
    
    results = run_all_extended_analyses(offer_data)
    
    # Hier folgt die Logik, um die 'results' formatiert auf der PDF-Seite auszugeben.
    # z.B. Amortisation, IRR, LCOE etc. als Text oder kleine Tabelle.
    
    c.showPage()

# ... (in der MODULE_MAP)
MODULE_MAP = {
    "deckblatt": _draw_cover_page,
    "anschreiben": _draw_cover_letter,
    "angebotstabelle": _draw_offer_table,
    "benutzerdefiniert": _draw_custom_content,
    "wirtschaftlichkeitsanalyse": _draw_extended_analysis, # NEU
}

def create_offer_pdf(
    offer_data: Dict[str, Any],
    output_filename: str,
    module_order: List[Dict[str, Any]], # NEU: Liste der zu rendernden Module
    theme_name: str,
):
    """
    Erstellt ein PDF-Dokument, indem es die Module in der festgelegten Reihenfolge aufruft.

    Args:
        offer_data (Dict): Die Daten für das Angebot.
        output_filename (str): Der Speicherpfad für das PDF.
        module_order (List[Dict]): Eine geordnete Liste von Modulen, die gezeichnet werden sollen.
                                   Jedes Element ist ein Dict, z.B. {'id': 'anschreiben'} oder
                                   {'id': 'benutzerdefiniert', 'content': {...}}.
        theme_name (str): Der Name des zu verwendenden Designs.
    """
    c = canvas.Canvas(output_filename, pagesize=A4)
    theme = get_theme(theme_name)

    # Setze den Titel des PDF-Dokuments
    c.setTitle(f"Angebot {offer_data.get('offer_id', '')} für {offer_data.get('customer', {}).get('name', '')}")

    # Iteriere durch die vom Benutzer definierte Reihenfolge und rufe die Funktionen auf
    for module_spec in module_order:
        module_id = module_spec["id"]
        draw_function = MODULE_MAP.get(module_id)
        
        if draw_function:
            # Für benutzerdefinierte Module übergeben wir den spezifischen Inhalt
            if module_id == "benutzerdefiniert":
                draw_function(c, theme, module_spec.get("content", {}))
            else:
                draw_function(c, theme, offer_data)
        else:
            print(f"Warnung: PDF-Modul '{module_id}' wurde nicht gefunden.")

    c.save()
    print(f"PDF erfolgreich erstellt: {output_filename}")

def _get_chart_description(chart_key: str, texts: Dict[str, str]) -> str:
    """Gibt eine ausführliche, persönliche und ansprechende Beschreibung für das angegebene Diagramm zurück."""
    descriptions = {
        'monthly_prod_cons_chart_bytes': get_text(texts, "chart_desc_monthly_prod_cons", 
            "📊 <b>Ihr persönlicher Jahresrhythmus:</b> Diese Darstellung zeigt Ihnen, wie Ihre PV-Anlage im Einklang mit den Jahreszeiten arbeitet. "
            "In den sonnenreichen Sommermonaten erzeugen Sie deutlich mehr Strom als Sie verbrauchen – perfekt für hohe Einspeisevergütungen! "
            "Im Winter gleicht sich Produktion und Verbrauch harmonisch aus. So planen Sie Ihren Energiehaushalt optimal."),
        
        'cost_projection_chart_bytes': get_text(texts, "chart_desc_cost_projection", 
            "💰 <b>Ihre finanzielle Zukunft im Blick:</b> Hier sehen Sie schwarz auf weiß, wie sich Ihre Stromkosten mit und ohne PV-Anlage entwickeln. "
            "Während herkömmliche Stromkosten Jahr für Jahr steigen, bleiben Sie mit Ihrer eigenen Solaranlage unabhängig von Preiserhöhungen. "
            "Die Schere öffnet sich zu Ihren Gunsten – je länger die Laufzeit, desto größer Ihre Ersparnis!"),
        
        'cumulative_cashflow_chart_bytes': get_text(texts, "chart_desc_cumulative_cashflow", 
            "📈 <b>Der Weg zu Ihrem persönlichen Gewinn:</b> Diese Kurve zeigt Ihren finanziellen Erfolgsweg. Anfangs investieren Sie, "
            "aber schon nach wenigen Jahren kehrt sich das Blatt: Ihre Anlage arbeitet für Sie und erwirtschaftet echte Gewinne. "
            "Der Break-Even-Punkt markiert den Beginn Ihrer 'kostenlosen' Stromzeit – ab dann ist jede kWh reiner Gewinn für Sie!"),
        
        'consumption_coverage_pie_chart_bytes': get_text(texts, "chart_desc_consumption_coverage", 
            "🏠 <b>Ihr Grad der Energiefreiheit:</b> Dieses Kreisdiagramm zeigt, wie unabhängig Sie vom Stromnetz werden. "
            "Je größer der grüne Anteil, desto mehr Ihres Haushaltsstroms kommt direkt vom eigenen Dach. "
            "Das bedeutet weniger Abhängigkeit von Strompreiserhöhungen und mehr Kontrolle über Ihre Energiekosten. Ihre persönliche Energiewende visualisiert!"),
        
        'pv_usage_pie_chart_bytes': get_text(texts, "chart_desc_pv_usage", 
            "⚡ <b>Wohin fließt Ihr selbst erzeugter Strom:</b> Hier sehen Sie die clevere Aufteilung Ihres Solarstroms. "
            "Der blaue Bereich zeigt, was Sie direkt selbst nutzen (= sofortige Ersparnis), der orange Teil wird ins Netz eingespeist (= garantierte Vergütung). "
            "Jede selbst verbrauchte kWh spart Ihnen ca. 30 Cent, jede eingespeiste kWh bringt Ihnen sichere Einnahmen!"),
        
        'daily_production_switcher_chart_bytes': get_text(texts, "chart_desc_daily_production", 
            "🌅 <b>Ihr Kraftwerk im Tagesverlauf:</b> Erleben Sie, wie Ihre Anlage mit der Sonne 'aufwacht' und arbeitet! "
            "Von den ersten Strahlen am Morgen bis zum Sonnenuntergang sehen Sie hier die natürliche Leistungskurve. "
            "Die Mittagsspitze zeigt Ihr maximales Potenzial – genau dann, wenn auch Ihr Haushalt oft am meisten Strom braucht. Perfektes Timing der Natur!"),
        
        'weekly_production_switcher_chart_bytes': get_text(texts, "chart_desc_weekly_production", 
            "📅 <b>Ihre Wochenenergie im Überblick:</b> So arbeitet Ihre Anlage durch die ganze Woche für Sie! "
            "Interessant zu sehen: Auch am Wochenende, wenn Sie vielleicht mehr zu Hause sind, produziert Ihre Anlage zuverlässig. "
            "Die gleichmäßige Verteilung zeigt: Ihre Investition arbeitet 7 Tage die Woche ohne Pause für Ihren Geldbeutel."),
        
        'yearly_production_switcher_chart_bytes': get_text(texts, "chart_desc_yearly_production", 
            "🗓️ <b>Ihr Energiejahr in 3D:</b> Hier erleben Sie die Kraft der Jahreszeiten! Die hohen Säulen im Sommer zeigen Ihre 'Erntezeit' – "
            "jetzt sammeln Sie Energie für das ganze Jahr. Selbst in den schwächeren Wintermonaten arbeitet Ihre Anlage noch profitabel. "
            "Diese natürlichen Schwankungen sind eingeplant und machen Ihre Jahresrechnung trotzdem sehr positiv!"),
        
        'project_roi_matrix_switcher_chart_bytes': get_text(texts, "chart_desc_project_roi", 
            "📊 <b>Ihre Rendite-Sicherheit visualisiert:</b> Diese Matrix zeigt, wie robust Ihre Investition ist. "
            "Selbst bei verschiedenen Strompreisentwicklungen bleibt Ihre Rendite attraktiv – das nennt man eine sichere Anlage! "
            "Vergleichen Sie das mal mit Ihrem Sparbuch: Hier sehen Sie reale Werte zwischen 3-8% Rendite pro Jahr. Ihre Anlage ist eine Geldanlage mit Garantie!"),
        
        'feed_in_revenue_switcher_chart_bytes': get_text(texts, "chart_desc_feed_in_revenue", 
            "💶 <b>Ihre garantierten Einnahmen:</b> Das ist Ihr 'Gehalt' vom Stromnetz! 20 Jahre lang bekommen Sie für jede eingespeiste kWh "
            "die staatlich garantierte Vergütung – ein sicheres Einkommen neben Ihrer Stromersparnis. "
            "Diese Kurve zeigt Ihnen, wie sich Ihre Einspeisevergütung über die Jahre summiert. Nebeneinkommen war nie so einfach!"),
        
        'prod_vs_cons_switcher_chart_bytes': get_text(texts, "chart_desc_prod_vs_cons", 
            "⚖️ <b>Das perfekte Gleichgewicht:</b> Hier sehen Sie das Zusammenspiel zwischen dem, was Sie erzeugen und dem, was Sie verbrauchen. "
            "Die ideale Balance bedeutet: wenig Strom einkaufen müssen und trotzdem schöne Überschüsse für die Einspeisung. "
            "Ihre Anlage ist so dimensioniert, dass Sie optimal zwischen Eigenverbrauch und Gewinnoptimierung navigieren!"),
        
        'co2_savings_chart_bytes': get_text(texts, "chart_desc_co2_savings", 
            "🌱 <b>Ihr Beitrag für die nächste Generation:</b> Jede kWh Ihres Solarstroms ersetzt schmutzigen Kohlestrom! "
            "Diese Grafik zeigt nicht nur Zahlen, sondern Ihren echten Umweltbeitrag. Stolze [CO2-Menge] kg CO₂ weniger pro Jahr – "
            "das entspricht [Bäume-Anzahl] gepflanzten Bäumen! Sie investieren nicht nur in Ihre Finanzen, sondern in eine saubere Zukunft."),
        
        'investment_value_switcher_chart_bytes': get_text(texts, "chart_desc_investment_value", 
            "💎 <b>Mehr als nur Geld – Ihr Wertzuwachs:</b> Diese Darstellung zeigt den Gesamtwert Ihrer Investition: "
            "Finanzielle Rendite + Umweltnutzen + Unabhängigkeit + Immobilienwert-Steigerung. "
            "Eine PV-Anlage ist mehr als nur Technik – sie ist Ihre persönliche Energiewende mit messbaren Vorteilen auf allen Ebenen!"),
        
        'storage_effect_switcher_chart_bytes': get_text(texts, "chart_desc_storage_effect", 
            "🔋 <b>Ihr persönlicher Energietresor:</b> Der Batteriespeicher macht Sie noch unabhängiger! "
            "Tagsüber 'tanken' Sie Sonnenstrom, abends nutzen Sie ihn gemütlich beim Fernsehen oder Kochen. "
            "Diese Grafik zeigt, wie sich Ihr Eigenverbrauch durch den Speicher erhöht – weniger Netzbezug, mehr Ersparnis, mehr Autarkie!"),
        
        'selfuse_stack_switcher_chart_bytes': get_text(texts, "chart_desc_selfuse_stack", 
            "🏠 <b>Eigenverbrauch ist bares Geld:</b> Jede selbst verbrauchte kWh ist wertvoller als eine eingespeiste! "
            "Diese gestapelte Darstellung zeigt Ihr optimales Verhältnis: Ein hoher blauer Bereich bedeutet direkte Kosteneinsparung, "
            "der orange Bereich bringt Ihnen die Einspeisevergütung. Die perfekte Mischung für maximalen finanziellen Vorteil!"),
        
        'cost_growth_switcher_chart_bytes': get_text(texts, "chart_desc_cost_growth", 
            "📈 <b>Steigende Strompreise – Ihr Vorteil wächst:</b> Während andere über teure Stromrechnungen stöhnen, profitieren Sie! "
            "Je mehr die Strompreise steigen, desto wertvoller wird jede selbst erzeugte kWh. "
            "Diese Projektion zeigt: Ihre PV-Anlage wird mit jedem Jahr noch rentabler. Sie haben heute die richtige Entscheidung getroffen!"),
        
        'roi_comparison_switcher_chart_bytes': get_text(texts, "chart_desc_roi_comparison", 
            "🏆 <b>Besser als jede Bank:</b> Hier sehen Sie Ihre PV-Rendite im Vergleich zu traditionellen Geldanlagen. "
            "Während Sparbücher kaum Zinsen bringen und die Inflation Ihr Geld entwertet, arbeitet Ihre Anlage mit 4-7% Rendite für Sie. "
            "Dazu kommt: Ihre Investition ist greifbar, auf Ihrem Dach und arbeitet 25+ Jahre zuverlässig!"),
        
        'break_even_chart_bytes': get_text(texts, "chart_desc_break_even", 
            "🎯 <b>Ihr Zielsprint zur Gewinnschwelle:</b> Diese Kurve zeigt Ihren Weg zur 'schwarzen Null' und darüber hinaus! "
            "Der Break-Even-Punkt ist wie die Ziellinie beim Marathon – ab hier läuft alles für Sie! "
            "Meist nach 8-12 Jahren ist es soweit: Von da an sind Sie 15+ Jahre im Plus. Das ist finanzielle Freiheit!"),
        
        'amortisation_chart_bytes': get_text(texts, "chart_desc_amortisation", 
            "💰 <b>Wie sich Ihre Investition zurückzahlt:</b> Diese Kurve ist Ihr persönlicher Finanzkompass! "
            "Sie zeigt, wie sich Ihre Anfangsinvestition Stück für Stück durch Ersparnisse und Einnahmen zurückzahlt. "
            "Je steiler die Kurve, desto schneller haben Sie Ihr Geld wieder drin. Und danach? Jahrelange Gewinne sind garantiert!")
    }
    
    return descriptions.get(chart_key, get_text(texts, "chart_desc_generic", 
        "🔆 <b>Ihre persönliche Energieanalyse:</b> Dieses Diagramm visualisiert wichtige Aspekte Ihrer maßgeschneiderten Photovoltaikanlage. "
        "Jede Grafik hilft Ihnen dabei, die Vorteile Ihrer Investition besser zu verstehen und fundierte Entscheidungen für Ihre Energiezukunft zu treffen."))

def page_layout_handler(canvas_obj: canvas.Canvas, doc_template: SimpleDocTemplate, texts_ref: Dict[str, str], company_info_ref: Dict, company_logo_base64_ref: Optional[str], offer_number_ref: str, page_width_ref: float, page_height_ref: float, margin_left_ref: float, margin_right_ref: float, margin_top_ref: float, margin_bottom_ref: float, doc_width_ref: float, doc_height_ref: float, include_custom_footer_ref: bool = True, include_header_logo_ref: bool = True):
    print(f"DEBUG: page_layout_handler aufgerufen für Seite {canvas_obj.getPageNumber()}")  # DEBUG
    canvas_obj.saveState()
    page_num = canvas_obj.getPageNumber()

    # DÜNNER STRICH OBEN - alle Seiten
    canvas_obj.setStrokeColor(colors.black)
    canvas_obj.setLineWidth(0.5)
    line_start = page_width_ref * 0.2
    line_end = page_width_ref * 0.8
    top_line_y = page_height_ref - 30
    canvas_obj.line(line_start, top_line_y, line_end, top_line_y)

    # HEADER - ab Seite 2 - OBERHALB des Content-Bereichs
    if page_num > 1:
        print("DEBUG: Header wird gezeichnet")  # DEBUG
        # Header weit oben positionieren - oberhalb der Margin
        header_y = page_height_ref - 40  # 40 Punkte vom oberen Rand
        
        canvas_obj.setFont("Helvetica-Bold", 12)
        canvas_obj.setFillColor(colors.black)
        canvas_obj.drawString(50, header_y, "Angebot")
        
        # Horizontale Linie unter dem Header
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(50, header_y - 10, page_width_ref - 50, header_y - 10)

    # FOOTER - alle Seiten - UNTERHALB des Content-Bereichs
    print("DEBUG: Footer wird gezeichnet")  # DEBUG
    footer_y = 40  # 40 Punkte vom unteren Rand
    
    # Horizontale Linie über dem Footer
    canvas_obj.setStrokeColor(colors.black)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(50, footer_y + 20, page_width_ref - 50, footer_y + 20)
    
    # Footer-Text zentriert
    footer_text = f"Angebot, {datetime.now().strftime('%d.%m.%Y')} | Seite {page_num}"
    canvas_obj.setFont("Helvetica", 10)
    canvas_obj.setFillColor(colors.black)
    text_width = canvas_obj.stringWidth(footer_text, "Helvetica", 10)
    center_x = page_width_ref / 2
    canvas_obj.drawString(center_x - text_width/2, footer_y, footer_text)

    # DÜNNER STRICH UNTEN - alle Seiten
    canvas_obj.setStrokeColor(colors.black)
    canvas_obj.setLineWidth(0.5)
    bottom_line_y = 20
    canvas_obj.line(line_start, bottom_line_y, line_end, bottom_line_y)

    canvas_obj.restoreState()

def _generate_complete_salutation_line(customer_data: Dict, texts: Dict[str, str]) -> str:
    salutation_value = customer_data.get("salutation") 
    title = customer_data.get("title", "")
    first_name = customer_data.get("first_name", "")
    last_name = customer_data.get("last_name", "")

    name_parts = [p for p in [title, first_name, last_name] if p and str(p).strip()]
    customer_full_name_for_salutation = " ".join(name_parts).strip()

    salutation_key_base = "salutation_polite"
    if isinstance(salutation_value, str):
        sl_lower = salutation_value.lower().strip()
        if sl_lower == "herr": salutation_key_base = "salutation_male_polite"
        elif sl_lower == "frau": salutation_key_base = "salutation_female_polite"
        elif sl_lower == "familie":
            fam_name = last_name if last_name and str(last_name).strip() else customer_data.get("company_name", get_text(texts, "family_default_name_pdf", "Familie"))
            return f"{get_text(texts, 'salutation_family_polite', 'Sehr geehrte Familie')} {str(fam_name).strip()},"
        elif sl_lower == "firma": 
            company_name_val = customer_data.get("company_name", "") or last_name 
            if company_name_val: return f"{get_text(texts, 'salutation_company_polite', 'Sehr geehrte Damen und Herren der Firma')} {str(company_name_val).strip()},"
            else: return get_text(texts, 'salutation_generic_fallback', 'Sehr geehrte Damen und Herren,')
    
    default_salutation_text = get_text(texts, salutation_key_base, "Sehr geehrte/r")
    
    if customer_full_name_for_salutation:
        return f"{default_salutation_text} {customer_full_name_for_salutation},"
    else: 
        return get_text(texts, 'salutation_generic_fallback', 'Sehr geehrte Damen und Herren,')


def _replace_placeholders(text_template: str, customer_data: Dict, company_info: Dict, offer_number: str, texts_dict: Dict[str, str], analysis_results_for_placeholder: Optional[Dict[str, Any]] = None) -> str:
    if text_template is None: text_template = ""
    processed_text = str(text_template)
    now_date_str = datetime.now().strftime('%d.%m.%Y')
    complete_salutation_line = _generate_complete_salutation_line(customer_data, texts_dict)
    
    ersatz_dict = {
        "[VollständigeAnrede]": complete_salutation_line,
        "[Ihr Name/Firmenname]": str(company_info.get("name", get_text(texts_dict, "company_name_default_placeholder_pdf", "Ihr Solarexperte"))),
        "[Angebotsnummer]": str(offer_number),
        "[Datum]": now_date_str,
        "[KundenNachname]": str(customer_data.get("last_name", "")),
        "[Nachname]": str(customer_data.get("last_name", "")),  # NEUER PLATZHALTER wie gewünscht
        "[KundenVorname]": str(customer_data.get("first_name", "")),
        "[KundenAnredeFormell]": str(customer_data.get("salutation", "")),
        "[KundenTitel]": str(customer_data.get("title", "")),
        "[KundenStrasseNr]": f"{customer_data.get('address','')} {customer_data.get('house_number','',)}".strip(),
        "[KundenPLZOrt]": f"{customer_data.get('zip_code','')} {customer_data.get('city','',)}".strip(),
        "[KundenFirmenname]": str(customer_data.get("company_name", "")),
    }
    if analysis_results_for_placeholder and isinstance(analysis_results_for_placeholder, dict):
        anlage_kwp_val = analysis_results_for_placeholder.get('anlage_kwp')
        ersatz_dict["[AnlagenleistungkWp]"] = format_kpi_value(anlage_kwp_val, "kWp", texts_dict=texts_dict, na_text_key="value_not_calculated_short") if anlage_kwp_val is not None else get_text(texts_dict, "value_not_calculated_short", "k.B.")
        
        total_invest_brutto_val = analysis_results_for_placeholder.get('total_investment_brutto')
        ersatz_dict["[GesamtinvestitionBrutto]"] = format_kpi_value(total_invest_brutto_val, "€", texts_dict=texts_dict, na_text_key="value_not_calculated_short") if total_invest_brutto_val is not None else get_text(texts_dict, "value_not_calculated_short", "k.B.")

        annual_benefit_yr1_val = analysis_results_for_placeholder.get('annual_financial_benefit_year1')
        ersatz_dict["[FinanziellerVorteilJahr1]"] = format_kpi_value(annual_benefit_yr1_val, "€", texts_dict=texts_dict, na_text_key="value_not_calculated_short") if annual_benefit_yr1_val is not None else get_text(texts_dict, "value_not_calculated_short", "k.B.")

    for placeholder, value_repl in ersatz_dict.items():
        processed_text = processed_text.replace(placeholder, str(value_repl))
    return processed_text

def _get_next_offer_number(texts: Dict[str,str], load_admin_setting_func: Callable, save_admin_setting_func: Callable) -> str:
    try:
        current_suffix_obj = load_admin_setting_func('offer_number_suffix', 1000)
        current_suffix = int(str(current_suffix_obj)) if current_suffix_obj is not None else 1000
        next_suffix = current_suffix + 1
        save_admin_setting_func('offer_number_suffix', next_suffix)
        return f"AN{datetime.now().year}-{next_suffix:04d}"
    except Exception: 
        return f"AN{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def _prepare_cost_table_for_pdf(analysis_results: Dict[str, Any], texts: Dict[str, str]) -> List[List[Any]]:
    cost_data_pdf = []
    cost_items_ordered_pdf = [
        ('base_matrix_price_netto', 'base_matrix_price_netto', True, 'TableText'),
        ('cost_modules_aufpreis_netto', 'cost_modules', True, 'TableText'),
        ('cost_inverter_aufpreis_netto', 'cost_inverter', True, 'TableText'),
        ('cost_storage_aufpreis_product_db_netto', 'cost_storage', True, 'TableText'),
        ('total_optional_components_cost_netto', 'total_optional_components_cost_netto_label', True, 'TableText'),
        ('cost_accessories_aufpreis_netto', 'cost_accessories_aufpreis_netto', True, 'TableText'),
        ('cost_scaffolding_netto', 'cost_scaffolding_netto', True, 'TableText'),
        ('cost_misc_netto', 'cost_misc_netto', True, 'TableText'),
        ('cost_custom_netto', 'cost_custom_netto', True, 'TableText'),
        ('subtotal_netto', 'subtotal_netto', True, 'TableBoldRight'),
        ('one_time_bonus_eur', 'one_time_bonus_eur_label', True, 'TableText'),
        ('total_investment_netto', 'total_investment_netto', True, 'TableBoldRight'),
        ('vat_rate_percent', 'vat_rate_percent', True, 'TableText'),
        ('total_investment_brutto', 'total_investment_brutto', True, 'TableBoldRight'),
    ]
    for result_key, label_key, is_euro_val, base_style_name in cost_items_ordered_pdf:
        value_cost = analysis_results.get(result_key)
        if value_cost is not None:
            if value_cost == 0.0 and result_key not in ['total_investment_netto', 'total_investment_brutto', 'subtotal_netto', 'vat_rate_percent', 'base_matrix_price_netto', 'one_time_bonus_eur']:
                continue
            label_text_pdf = get_text(texts, label_key, label_key.replace("_", " ").title())
            unit_pdf = "€" if is_euro_val else "%" if label_key == 'vat_rate_percent' else ""
            precision_pdf = 1 if label_key == 'vat_rate_percent' else 2
            formatted_value_str_pdf = format_kpi_value(value_cost, unit=unit_pdf, precision=precision_pdf, texts_dict=texts)
            value_style_name = base_style_name
            if result_key in ['total_investment_netto', 'total_investment_brutto', 'subtotal_netto']: value_style_name = 'TableBoldRight'
            elif is_euro_val or unit_pdf == "%": value_style_name = 'TableNumber'
            value_style = STYLES.get(value_style_name, STYLES['TableText'])
            cost_data_pdf.append([Paragraph(str(label_text_pdf), STYLES.get('TableLabel')), Paragraph(str(formatted_value_str_pdf), value_style)])
    return cost_data_pdf

def _prepare_simulation_table_for_pdf(analysis_results: Dict[str, Any], texts: Dict[str, str], num_years_to_show: int = 10) -> List[List[Any]]:
    sim_data_for_pdf_final: List[List[Any]] = []
    header_config_pdf = [
        (get_text(texts,"analysis_table_year_header","Jahr"), None, "", 0, 'TableText'),
        (get_text(texts,"annual_pv_production_kwh","PV Prod."), 'annual_productions_sim', "kWh", 0, 'TableNumber'),
        (get_text(texts,"annual_financial_benefit","Jährl. Vorteil"), 'annual_benefits_sim', "€", 2, 'TableNumber'),
        (get_text(texts,"annual_maintenance_cost_sim","Wartung"), 'annual_maintenance_costs_sim', "€", 2, 'TableNumber'),
        (get_text(texts,"analysis_table_annual_cf_header","Jährl. CF"), 'annual_cash_flows_sim', "€", 2, 'TableNumber'),
        (get_text(texts,"analysis_table_cumulative_cf_header","Kum. CF"), 'cumulative_cash_flows_sim_display', "€", 2, 'TableBoldRight')
    ]
    header_row_pdf = [Paragraph(hc[0], STYLES['TableHeader']) for hc in header_config_pdf]
    sim_data_for_pdf_final.append(header_row_pdf)

    sim_period_eff_pdf = int(analysis_results.get('simulation_period_years_effective', 0))
    if sim_period_eff_pdf == 0: return sim_data_for_pdf_final

    actual_years_to_display_pdf = min(sim_period_eff_pdf, num_years_to_show)
    cumulative_cash_flows_base_sim = analysis_results.get('cumulative_cash_flows_sim', [])
    if cumulative_cash_flows_base_sim and len(cumulative_cash_flows_base_sim) == (sim_period_eff_pdf + 1) :
        analysis_results['cumulative_cash_flows_sim_display'] = cumulative_cash_flows_base_sim[1:]
    else: 
        analysis_results['cumulative_cash_flows_sim_display'] = [None] * sim_period_eff_pdf

    for i_pdf in range(actual_years_to_display_pdf):
        row_items_formatted_pdf = [Paragraph(str(i_pdf + 1), STYLES.get(header_config_pdf[0][4]))]
        for j_pdf, header_conf_item in enumerate(header_config_pdf[1:]):
            result_key_pdf, unit_pdf, precision_pdf, style_name_data_pdf = header_conf_item[1], header_conf_item[2], header_conf_item[3], header_conf_item[4]
            current_list_pdf = analysis_results.get(str(result_key_pdf), [])
            value_to_format_pdf = current_list_pdf[i_pdf] if isinstance(current_list_pdf, list) and i_pdf < len(current_list_pdf) else None
            formatted_str_pdf = format_kpi_value(value_to_format_pdf, unit=unit_pdf, precision=precision_pdf, texts_dict=texts, na_text_key="value_not_available_short_pdf")
            row_items_formatted_pdf.append(Paragraph(str(formatted_str_pdf), STYLES.get(style_name_data_pdf, STYLES['TableText'])))
        sim_data_for_pdf_final.append(row_items_formatted_pdf)

    if sim_period_eff_pdf > num_years_to_show:
        ellipsis_row_pdf = [Paragraph("...", STYLES['TableText']) for _ in header_config_pdf]
        for cell_para_pdf in ellipsis_row_pdf: cell_para_pdf.style.alignment = TA_CENTER
        sim_data_for_pdf_final.append(ellipsis_row_pdf)
    return sim_data_for_pdf_final

def _create_product_table_with_image(details_data_prod: List[List[Any]], product_image_flowables_prod: List[Any], available_width: float) -> List[Any]:
    if not _REPORTLAB_AVAILABLE: return []
    story_elements: List[Any] = []
    if details_data_prod and product_image_flowables_prod:
        text_table_width = available_width * 0.62
        image_cell_width = available_width * 0.35
        text_table = Table(details_data_prod, colWidths=[text_table_width * 0.4, text_table_width * 0.6])
        text_table.setStyle(PRODUCT_TABLE_STYLE)
        image_cell_content = [Spacer(1, 0.1*cm)] + product_image_flowables_prod
        image_frame = KeepInFrame(image_cell_width, 6*cm, image_cell_content)
        combined_table_data = [[text_table, image_frame]]
        combined_table = Table(combined_table_data, colWidths=[text_table_width + 0.03*available_width, image_cell_width])
        combined_table.setStyle(PRODUCT_MAIN_TABLE_STYLE)
        story_elements.append(combined_table)
    elif details_data_prod:
        text_only_table = Table(details_data_prod, colWidths=[available_width * 0.4, available_width * 0.6])
        text_only_table.setStyle(PRODUCT_TABLE_STYLE)
        story_elements.append(text_only_table)
    elif product_image_flowables_prod:
        story_elements.extend(product_image_flowables_prod)
    return story_elements

def _add_product_details_to_story(
    story: List[Any], product_id: Optional[Union[int, float]],
    component_name_text: str, texts: Dict[str,str],
    available_width: float, get_product_by_id_func_param: Callable,
    include_product_images: bool
):
    """
    VERBESSERTE Produktdetails mit korrekten Bezeichnungen und Seitenumbruch-Schutz
    """
    if not _REPORTLAB_AVAILABLE: return
    
    # SEITENUMBRUCH-SCHUTZ: Sammle alle Elemente in einer Liste
    protected_elements: List[Any] = []
    
    product_details: Optional[Dict[str, Any]] = None
    if product_id is not None and callable(get_product_by_id_func_param):
        product_details = get_product_by_id_func_param(product_id)

    if not product_details:
        protected_elements.append(Paragraph(f"{component_name_text}: {get_text(texts,'details_not_available_pdf', 'Details nicht verfügbar')}", STYLES.get('NormalLeft')))
        protected_elements.append(Spacer(1, 0.3*cm))
        
        # SEITENUMBRUCH-SCHUTZ anwenden
        story.append(KeepTogether(protected_elements))
        return

    # VERBESSERTE PRODUKTBEZEICHNUNG
    brand = product_details.get('brand', '').strip()
    model = product_details.get('model_name', '').strip()
    
    # Korrekte Darstellung: "Marke Modell" oder fallback zu ursprünglichem Namen
    if brand and model:
        full_product_name = f"{brand} {model}"
    elif brand:
        full_product_name = brand
    elif model:
        full_product_name = model
    else:
        full_product_name = component_name_text
    
    # Titel mit vollständiger Produktbezeichnung
    protected_elements.append(Paragraph(f"{component_name_text}: {full_product_name}", STYLES.get('ComponentTitle')))
    
    details_data_prod: List[List[Any]] = []

    default_fields_prod = [
        ('brand', 'product_brand'), ('model_name', 'product_model'),
        ('warranty_years', 'product_warranty')
    ]
    component_specific_fields_prod: List[Tuple[str,str]] = []
    cat_lower_prod = str(product_details.get('category', "")).lower()

    if cat_lower_prod == 'modul':
        component_specific_fields_prod = [
            ('capacity_w', 'product_capacity_wp'),
            ('efficiency_percent', 'product_efficiency'),
            ('length_m', 'product_length_m'),
            ('width_m', 'product_width_m'),
            ('weight_kg', 'product_weight_kg'),
            # Erweiterung: echte Modul-Keys
            ('cell_technology', 'product_module_cell_technology'),
            ('module_structure', 'product_module_structure'),
            ('cell_type', 'product_module_cell_type'),
            ('version', 'product_module_version'),
            ('module_warranty_text', 'product_module_warranty_text'),
        ]
    elif cat_lower_prod == 'wechselrichter':
        component_specific_fields_prod = [('power_kw', 'product_power_kw'), ('efficiency_percent', 'product_efficiency_inverter')]
    elif cat_lower_prod == 'batteriespeicher':
        component_specific_fields_prod = [('storage_power_kw', 'product_capacity_kwh'), ('power_kw', 'product_power_storage_kw'), ('max_cycles', 'product_max_cycles_label')]
    elif cat_lower_prod == 'wallbox':
        component_specific_fields_prod = [('power_kw', 'product_power_wallbox_kw')]
    elif cat_lower_prod == 'energiemanagementsystem': # HINZUGEFÜGT: EMS
        component_specific_fields_prod = [('description', 'product_description_short')] # Beispiel, anpassen!
    elif cat_lower_prod == 'leistungsoptimierer': # HINZUGEFÜGT: Optimierer
        component_specific_fields_prod = [('efficiency_percent', 'product_optimizer_efficiency')] # Beispiel
    elif cat_lower_prod == 'carport': # HINZUGEFÜGT: Carport
        component_specific_fields_prod = [('length_m', 'product_length_m'), ('width_m', 'product_width_m')] # Beispiel
    # Notstrom und Tierabwehr könnten generische Felder wie Beschreibung verwenden oder spezifische, falls vorhanden
    elif cat_lower_prod == 'notstromversorgung':
        component_specific_fields_prod = [('power_kw', 'product_emergency_power_kw')] # Beispiel
    elif cat_lower_prod == 'tierabwehrschutz':
        component_specific_fields_prod = [('description', 'product_description_short')] # Beispiel
    
    all_fields_to_display_prod = default_fields_prod + component_specific_fields_prod

    # Helper: Attribut-Fallback nur bei Bedarf (keine globalen Imports nötig)
    def _get_attr_value_safe(pid: Optional[Union[int, float]], akey: str) -> Optional[str]:
        if pid in (None, ""):
            return None
        try:
            from product_attributes import get_attribute_value as _gav  # type: ignore
            return _gav(int(pid), akey)
        except Exception:
            return None

    for key_prod, label_text_key_prod in all_fields_to_display_prod:
        value_prod = product_details.get(key_prod)
        # Fallback: Für Modul-spezifische kanonische Felder ggf. aus Attribute-Tabelle lesen
        if (value_prod is None or str(value_prod).strip() == "") and cat_lower_prod == 'modul' and key_prod in (
            'cell_technology', 'module_structure', 'cell_type', 'version', 'module_warranty_text'
        ):
            value_prod = _get_attr_value_safe(product_details.get('id'), key_prod)
        label_prod = get_text(texts, label_text_key_prod, key_prod.replace("_", " ").title())
        
        if value_prod is not None and str(value_prod).strip() != "":
            unit_prod, prec_prod = "", 2
            if key_prod == 'capacity_w': unit_prod, prec_prod = "Wp", 0
            elif key_prod == 'power_kw': unit_prod, prec_prod = "kW", 1 # Für WR, Speicher, Wallbox etc.
            elif key_prod == 'storage_power_kw': unit_prod, prec_prod = "kWh", 1
            elif key_prod.endswith('_percent'): unit_prod, prec_prod = "%", 1
            elif key_prod == 'warranty_years': unit_prod, prec_prod = "Jahre", 0
            elif key_prod == 'max_cycles': unit_prod, prec_prod = "Zyklen", 0
            elif key_prod.endswith('_m'): unit_prod, prec_prod = "m", 3
            elif key_prod == 'weight_kg': unit_prod, prec_prod = "kg", 1
            # Für reine Textfelder (kanonische Modul-Felder) nicht numerisch formatieren
            if key_prod in ('cell_technology','module_structure','cell_type','version','module_warranty_text'):
                value_str_prod = str(value_prod)
            else:
                value_str_prod = format_kpi_value(value_prod, unit=unit_prod, precision=prec_prod, texts_dict=texts, na_text_key="value_not_available_short_pdf")
            details_data_prod.append([Paragraph(str(label_prod), STYLES.get('TableLabel')), Paragraph(str(value_str_prod), STYLES.get('TableText'))])

    product_image_flowables_prod: List[Any] = []
    if include_product_images:
        product_image_base64_prod = product_details.get('image_base64')
        if product_image_base64_prod:
            img_w_prod = min(available_width * 0.30, 5*cm); img_h_max_prod = 5*cm
            product_image_flowables_prod = _get_image_flowable(product_image_base64_prod, img_w_prod, texts, None, img_h_max_prod, align='CENTER')
    
    # Tabelle zu geschützten Elementen hinzufügen
    table_elements = _create_product_table_with_image(details_data_prod, product_image_flowables_prod, available_width)
    protected_elements.extend(table_elements)
    
    # Beschreibung hinzufügen
    description_prod_val = product_details.get('description')
    if description_prod_val and str(description_prod_val).strip():
        protected_elements.append(Spacer(1, 0.2*cm))
        protected_elements.append(Paragraph(f"<i>{str(description_prod_val).strip()}</i>", STYLES.get('TableTextSmall')))
    
    protected_elements.append(Spacer(1, 0.5*cm))

    # SEITENUMBRUCH-SCHUTZ: Gesamtes Produktmodul zusammenhalten
    story.append(KeepTogether(protected_elements))


def generate_offer_pdf(
    project_data: Dict[str, Any],
    analysis_results: Optional[Dict[str, Any]],
    company_info: Dict[str, Any],
    company_logo_base64: Optional[str],
    selected_title_image_b64: Optional[str],
    selected_offer_title_text: str,
    selected_cover_letter_text: str,
    sections_to_include: Optional[List[str]],
    inclusion_options: Dict[str, Any],
    load_admin_setting_func: Callable, 
    save_admin_setting_func: Callable, 
    list_products_func: Callable, 
    get_product_by_id_func: Callable, 
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]],
    active_company_id: Optional[int],
    texts: Dict[str, str],
    use_modern_design: bool = True,    **kwargs
) -> Optional[bytes]:
    # Frühzeitige Delegation: Verwende standardmäßig den neuen 6-Seiten-Template-Flow
    # Verhindere Rekursion mittels Flag 'disable_main_template_combiner'
    if not kwargs.get('disable_main_template_combiner'):
        try:
            combined_bytes = generate_offer_pdf_with_main_templates(
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info,
                company_logo_base64=company_logo_base64,
                selected_title_image_b64=selected_title_image_b64,
                selected_offer_title_text=selected_offer_title_text,
                selected_cover_letter_text=selected_cover_letter_text,
                sections_to_include=sections_to_include,
                inclusion_options=inclusion_options,
                load_admin_setting_func=load_admin_setting_func,
                save_admin_setting_func=save_admin_setting_func,
                list_products_func=list_products_func,
                get_product_by_id_func=get_product_by_id_func,
                db_list_company_documents_func=db_list_company_documents_func,
                active_company_id=active_company_id,
                texts=texts,
                use_modern_design=use_modern_design,
                disable_main_template_combiner=True,
                **kwargs,
            )
            if combined_bytes:
                return combined_bytes
            else:
                print("WARN: Template-Combiner lieferte keine Bytes – fallback auf Legacy-Generator")
        except Exception as e:
            print(f"WARN: Template-Combiner Exception – fallback auf Legacy-Generator: {e}")

    if not _REPORTLAB_AVAILABLE:
        if project_data and texts and company_info:
            return _create_plaintext_pdf_fallback(project_data, analysis_results, texts, company_info, selected_offer_title_text, selected_cover_letter_text)
        return None
    
    # Vor-Validierung: fehlende Felder defensiv ergänzen (Firmendaten + final_price)
    try:
        # Projekt-/Analyse-Dicts lokal kopieren, um Seiteneffekte zu vermeiden
        project_data = dict(project_data or {})
        analysis_results = dict(analysis_results or {})

        # 1) Firmendaten in project_data.company_information injizieren, falls nicht vorhanden
        company_info_safe = dict(company_info or {})
        proj_company_info = project_data.get('company_information')
        if not isinstance(proj_company_info, dict) or not proj_company_info.get('name'):
            project_data['company_information'] = company_info_safe
        else:
            # Fehlende Standardfelder aus company_info ergänzen, ohne bestehende zu überschreiben
            for k, v in company_info_safe.items():
                if proj_company_info.get(k) in (None, ""):
                    proj_company_info[k] = v

        # 2) final_price befüllen: bevorzugt aus Streamlit-Session, sonst aus Analyse-Feldern ableiten
        final_price_val = analysis_results.get('final_price')
        if final_price_val in (None, 0, 0.0):
            try:
                import streamlit as st  # optional, nur falls in UI-Session
                live = st.session_state.get('live_pricing_calculations', {}) if hasattr(st, 'session_state') else {}
                fp = live.get('final_price')
                if isinstance(fp, (int, float)) and fp > 0:
                    final_price_val = fp
            except Exception:
                # streamlit evtl. nicht verfügbar – ignoriere
                pass

        if final_price_val in (None, 0, 0.0):
            # Ableitung aus Netto/Brutto-Totalen
            totals_candidates = [
                analysis_results.get('total_investment_netto'),
                analysis_results.get('total_investment_brutto'),
                analysis_results.get('subtotal_netto'),
            ]
            final_price_val = next((v for v in totals_candidates if isinstance(v, (int, float)) and v > 0), None)

        if isinstance(final_price_val, (int, float)) and final_price_val > 0:
            analysis_results['final_price'] = final_price_val

        # 3) Kundenname defensiv setzen (für Validierung, nicht kritisch)
        cust = project_data.get('customer_data') or {}
        if not isinstance(cust, dict):
            cust = {}
        if not cust.get('last_name'):
            # Fallback: aus project_details (z. B. customer_name) oder Platzhalter
            pd = project_data.get('project_details') or {}
            fullname = pd.get('customer_full_name') or pd.get('customer_name') or ''
            if isinstance(fullname, str) and fullname.strip():
                # Split: letzter Token als Nachname
                parts = fullname.strip().split()
                if parts:
                    cust['last_name'] = parts[-1]
                    cust['first_name'] = ' '.join(parts[:-1]) if len(parts) > 1 else cust.get('first_name', '')
            if not cust.get('last_name'):
                cust['last_name'] = 'Kunde'
        project_data['customer_data'] = cust

        # 4) Fehlende KPIs anlage_kwp / annual_pv_production_kwh defensiv ableiten
        if not analysis_results.get('anlage_kwp'):
            pd = project_data.get('project_details') or {}
            try:
                mod_qty = float(pd.get('module_quantity') or 0)
                mod_wp = float(pd.get('selected_module_capacity_w') or 0)
                kwp = (mod_qty * mod_wp) / 1000.0 if mod_qty > 0 and mod_wp > 0 else None
            except Exception:
                kwp = None
            if isinstance(kwp, float) and kwp > 0:
                analysis_results['anlage_kwp'] = kwp
        if not analysis_results.get('annual_pv_production_kwh'):
            # grober Default aus kWp
            kwp = analysis_results.get('anlage_kwp')
            if isinstance(kwp, (int, float)) and kwp > 0:
                analysis_results['annual_pv_production_kwh'] = float(kwp) * 1000.0
    except Exception:
        # Defensive: Bei jedem Fehler in der Präparation weiterfahren – Validierung fängt ab
        pass

    # DATENVALIDIERUNG: Prüfe Verfügbarkeit der erforderlichen Daten
    validation_result = _validate_pdf_data_availability(project_data or {}, analysis_results or {}, texts)
    
    # Wenn kritische Daten fehlen, erstelle Fallback-PDF
    if not validation_result['is_valid']:
        print(f" PDF-Erstellung: Kritische Daten fehlen: {', '.join(validation_result['critical_errors'])}")
        customer_data = project_data.get('customer_data', {}) if project_data else {}
        return _create_no_data_fallback_pdf(texts, customer_data)
    
    # Warnungen ausgeben, wenn Daten unvollständig sind
    if validation_result['warnings']:
        print(f" PDF-Erstellung: Daten unvollständig: {', '.join(validation_result['missing_data_summary'])}")
        for warning in validation_result['warnings']:
            print(f"   - {warning}")
    
    design_settings = load_admin_setting_func('pdf_design_settings', {'primary_color': PRIMARY_COLOR_HEX, 'secondary_color': SECONDARY_COLOR_HEX})
    if isinstance(design_settings, dict):
        _update_styles_with_dynamic_colors(design_settings)
    
    main_offer_buffer = io.BytesIO()
    offer_number_final = _get_next_offer_number(texts, load_admin_setting_func, save_admin_setting_func)
    
    include_company_logo_opt = inclusion_options.get("include_company_logo", True)
    include_product_images_opt = inclusion_options.get("include_product_images", True)
    include_all_documents_opt = inclusion_options.get("include_all_documents", True) # Korrigierter Key
    company_document_ids_to_include_opt = inclusion_options.get("company_document_ids_to_include", [])
    include_optional_component_details_opt = inclusion_options.get("include_optional_component_details", True) # NEUE Option
    
    # NEUE OPTIONEN für Footer und Header-Logo (wie gewünscht)
    include_custom_footer_opt = inclusion_options.get("include_custom_footer", True)  
    include_header_logo_opt = inclusion_options.get("include_header_logo", True)
    
    #  NEUE EXTENDED FEATURES (aus Session State)
    financing_config = inclusion_options.get("financing_config", {})
    chart_config = inclusion_options.get("chart_config", {})
    custom_content_items = inclusion_options.get("custom_content_items", [])
    pdf_editor_config = inclusion_options.get("pdf_editor_config", {})
    pdf_design_config = inclusion_options.get("pdf_design_config", {})

    doc = SimpleDocTemplate(main_offer_buffer, title=get_text(texts, "pdf_offer_title_doc_param", "Angebot: Photovoltaikanlage").format(offer_number=offer_number_final),
                            author=company_info.get("name", "SolarFirma"), pagesize=pagesizes.A4,
                            leftMargin=2*cm, rightMargin=2*cm, topMargin=2.5*cm, bottomMargin=2.5*cm)

    story: List[Any] = []
    # Optional: Deckblatt & Anschreiben überspringen (für Template-Hauptausgabe)
    skip_cover_and_letter: bool = bool(inclusion_options.get("skip_cover_and_letter", False) or kwargs.get("skip_cover_and_letter", False))
    
    current_project_data_pdf = project_data if isinstance(project_data, dict) else {}
    current_analysis_results_pdf = analysis_results if isinstance(analysis_results, dict) else {}
    customer_pdf = current_project_data_pdf.get("customer_data", {})
    pv_details_pdf = current_project_data_pdf.get("project_details", {})
    available_width_content = doc.width

    # --- Deckblatt ---
    if not skip_cover_and_letter:
        try:
            if selected_title_image_b64:
                img_flowables_title = _get_image_flowable(selected_title_image_b64, doc.width, texts, max_height=doc.height / 1.8, align='CENTER')
                if img_flowables_title:
                    story.extend(img_flowables_title)
                    story.append(Spacer(1, 0.5 * cm))

            if include_company_logo_opt and company_logo_base64:
                logo_flowables_deckblatt = _get_image_flowable(company_logo_base64, 6*cm, texts, max_height=3*cm, align='CENTER')
                if logo_flowables_deckblatt:
                    story.extend(logo_flowables_deckblatt)
                    story.append(Spacer(1, 0.5 * cm))

            offer_title_processed_pdf = _replace_placeholders(selected_offer_title_text, customer_pdf, company_info, offer_number_final, texts, current_analysis_results_pdf)
            story.append(Paragraph(offer_title_processed_pdf, STYLES.get('OfferTitle')))
            
            company_info_html_pdf = "<br/>".join(filter(None, [
                f"<b>{company_info.get('name', '')}</b>", company_info.get("street", ""),
                f"{company_info.get('zip_code', '')} {company_info.get('city', '')}".strip(),
                (f"{get_text(texts, 'pdf_phone_label_short', 'Tel.')}: {company_info.get('phone', '')}" if company_info.get('phone') else None),
                (f"{get_text(texts, 'pdf_email_label_short', 'Mail')}: {company_info.get('email', '')}" if company_info.get('email') else None),
                (f"{get_text(texts, 'pdf_website_label_short', 'Web')}: {company_info.get('website', '')}" if company_info.get('website') else None),
                (f"{get_text(texts, 'pdf_taxid_label', 'StNr/USt-ID')}: {company_info.get('tax_id', '')}" if company_info.get('tax_id') else None),
            ]))
            story.append(Paragraph(company_info_html_pdf, STYLES.get('CompanyInfoDeckblatt')))
            # KORRIGIERTES 4-ZEILEN-FORMAT wie gewünscht:
            # [Anrede] [Titel]
            # [Nachname] [Vorname]  
            # [Strasse] [Hausnummer]
            # [Postleitzahl] [Ort]
            line1 = f"{customer_pdf.get('salutation','')} {customer_pdf.get('title','')}".strip()
            line2 = f"{customer_pdf.get('last_name','')} {customer_pdf.get('first_name','')}".strip()
            line3 = f"{customer_pdf.get('address','')} {customer_pdf.get('house_number','')}".strip()
            line4 = f"{customer_pdf.get('zip_code','')} {customer_pdf.get('city','')}".strip()
            
            customer_address_block_pdf_lines = [line1, line2, line3, line4]
            # Firmenname falls vorhanden zusätzlich einfügen
            if customer_pdf.get("company_name"):
                customer_address_block_pdf_lines.insert(1, str(customer_pdf.get("company_name")))
                
            customer_address_block_pdf = "<br/>".join(filter(None, customer_address_block_pdf_lines))
            story.append(Paragraph(customer_address_block_pdf, STYLES.get("CustomerAddress")))
            
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph(f"{get_text(texts, 'pdf_offer_number_label', 'Angebotsnummer')}: <b>{offer_number_final}</b>", STYLES.get('NormalRight')))
            story.append(Paragraph(f"{get_text(texts, 'pdf_offer_date_label', 'Datum')}: {datetime.now().strftime('%d.%m.%Y')}", STYLES.get('NormalRight')))
            story.append(PageBreak())
        except Exception as e_cover:
            story.append(Paragraph(f"Fehler bei Erstellung des Deckblatts: {e_cover}", STYLES.get('NormalLeft')))
            story.append(PageBreak())

    # --- Anschreiben ---
    if not skip_cover_and_letter:
        try:
            # SEITENUMBRUCH-SCHUTZ: Anschreiben als zusammenhängende Einheit
            cover_letter_elements = []
            
            story.append(SetCurrentChapterTitle(get_text(texts, "pdf_chapter_title_cover_letter", "Anschreiben")))
            company_sender_address_lines = [company_info.get("name", ""), company_info.get("street", ""), f"{company_info.get('zip_code', '')} {company_info.get('city', '')}".strip()]
            cover_letter_elements.append(Paragraph("<br/>".join(filter(None,company_sender_address_lines)), STYLES.get('NormalLeft'))) 
            cover_letter_elements.append(Spacer(1, 1.5*cm))
            cover_letter_elements.append(Paragraph(customer_address_block_pdf, STYLES.get('NormalLeft')))
            cover_letter_elements.append(Spacer(1, 1*cm))
            cover_letter_elements.append(Paragraph(datetime.now().strftime('%d.%m.%Y'), STYLES.get('NormalRight')))
            cover_letter_elements.append(Spacer(1, 0.5*cm))
            offer_subject_text = get_text(texts, "pdf_offer_subject_line_param", "Ihr persönliches Angebot für eine Photovoltaikanlage, Nr. {offer_number}").format(offer_number=offer_number_final)
            cover_letter_elements.append(Paragraph(f"<b>{offer_subject_text}</b>", STYLES.get('NormalLeft')))
            cover_letter_elements.append(Spacer(1, 0.5*cm))

            cover_letter_processed_pdf = _replace_placeholders(selected_cover_letter_text, customer_pdf, company_info, offer_number_final, texts, current_analysis_results_pdf)
            cover_letter_paragraphs = cover_letter_processed_pdf.split('\n') 
            for para_text in cover_letter_paragraphs:
                if para_text.strip(): 
                    cover_letter_elements.append(Paragraph(para_text.replace('\r',''), STYLES.get('CoverLetter'))) 
                else: 
                    cover_letter_elements.append(Spacer(1, 0.2*cm)) 
            cover_letter_elements.append(Spacer(1, 1*cm))
            cover_letter_elements.append(Paragraph(get_text(texts, "pdf_closing_greeting", "Mit freundlichen Grüßen"), STYLES.get('NormalLeft')))
            cover_letter_elements.append(Spacer(1, 0.3*cm))
            cover_letter_elements.append(Paragraph(str(company_info.get("name", "")), STYLES.get('NormalLeft')))
            
            # SEITENUMBRUCH-SCHUTZ: Anschreiben zusammenhalten
            story.append(KeepTogether(cover_letter_elements))
            story.append(PageBreak())
        except Exception as e_letter:
            story.append(Paragraph(f"Fehler bei Erstellung des Anschreibens: {e_letter}", STYLES.get('NormalLeft')))
            story.append(PageBreak())    # --- Dynamische Sektionen ---
    active_sections_set_pdf = set(sections_to_include or [])
    
    section_chapter_titles_map = {
        "ProjectOverview": get_text(texts, "pdf_chapter_title_overview", "Projektübersicht"),
        "TechnicalComponents": get_text(texts, "pdf_chapter_title_components", "Komponenten"),
        "CostDetails": get_text(texts, "pdf_chapter_title_cost_details", "Kosten"),
        "Economics": get_text(texts, "pdf_chapter_title_economics", "Wirtschaftlichkeit"),
        "SimulationDetails": get_text(texts, "pdf_chapter_title_simulation", "Simulation"),
        "CO2Savings": get_text(texts, "pdf_chapter_title_co2", "CO₂-Einsparung"),
        "Visualizations": get_text(texts, "pdf_chapter_title_visualizations", "Visualisierungen"),
        "FutureAspects": get_text(texts, "pdf_chapter_title_future_aspects", "Zukunftsaspekte"),
        
        # NEUE OPTIONALE SEITENVORLAGEN (5+ wie gewünscht)
        "CompanyProfile": get_text(texts, "pdf_chapter_title_company_profile", "Unternehmensprofil"),
        "Certifications": get_text(texts, "pdf_chapter_title_certifications", "Zertifizierungen & Qualität"),
        "References": get_text(texts, "pdf_chapter_title_references", "Referenzen & Kundenstimmen"), 
        "Installation": get_text(texts, "pdf_chapter_title_installation", "Installation & Montage"),
        "Maintenance": get_text(texts, "pdf_chapter_title_maintenance", "Wartung & Service"),        "Financing": get_text(texts, "pdf_chapter_title_financing", "Finanzierungsmöglichkeiten"),
        "Insurance": get_text(texts, "pdf_chapter_title_insurance", "Versicherungsschutz"),
        "Warranty": get_text(texts, "pdf_chapter_title_warranty", "Garantie & Gewährleistung")
    }
    
    ordered_section_definitions_pdf = [
        ("ProjectOverview", "pdf_section_title_overview", "1. Projektübersicht & Eckdaten"),
        ("TechnicalComponents", "pdf_section_title_components", "2. Angebotene Systemkomponenten"),
        ("CostDetails", "pdf_section_title_cost_details", "3. Detaillierte Kostenaufstellung"),
        ("Economics", "pdf_section_title_economics", "4. Wirtschaftlichkeit im Überblick"),
        ("SimulationDetails", "pdf_section_title_simulation", "5. Simulationsübersicht (Auszug)"),
        ("CO2Savings", "pdf_section_title_co2", "6. Ihre CO₂-Einsparung"),
        ("Visualizations", "pdf_section_title_visualizations", "7. Grafische Auswertungen"),
        ("FutureAspects", "pdf_chapter_title_future_aspects", "8. Zukunftsaspekte & Erweiterungen"),
        
        # NEUE OPTIONALE SEITENVORLAGEN (individuell gestaltbar)
        ("CompanyProfile", "pdf_section_title_company_profile", "9. Unser Unternehmen"),
        ("Certifications", "pdf_section_title_certifications", "10. Zertifizierungen & Qualitätsstandards"),
        ("References", "pdf_section_title_references", "11. Referenzen & Kundenerfahrungen"),
        ("Installation", "pdf_section_title_installation", "12. Professionelle Installation"),
        ("Maintenance", "pdf_section_title_maintenance", "13. Wartung & Langzeitservice"),
        ("Financing", "pdf_section_title_financing", "14. Flexible Finanzierungslösungen"),
        ("Insurance", "pdf_section_title_insurance", "15. Umfassender Versicherungsschutz"),        ("Warranty", "pdf_section_title_warranty", "16. Herstellergarantie & Gewährleistung")
    ]
    # Anwenden einer benutzerdefinierten Reihenfolge aus dem Drag&Drop-Manager (falls vorhanden)
    try:
        dnd_order = (inclusion_options or {}).get('custom_section_order')
        if isinstance(dnd_order, list) and dnd_order:
            # Mapping der DnD-Keys (Manager) auf die Generator-Keys
            dnd_to_gen_map = {
                'project_overview': 'ProjectOverview',
                'technical_components': 'TechnicalComponents',
                'cost_details': 'CostDetails',
                'economics': 'Economics',
                # Weitere Mappings können bei Bedarf ergänzt werden
            }
            preferred_gen_order = [dnd_to_gen_map[k] for k in dnd_order if k in dnd_to_gen_map]
            if preferred_gen_order:
                def_map = {k: tpl for (k, *rest), tpl in [((k, v1, v2), (k, v1, v2)) for (k, v1, v2) in ordered_section_definitions_pdf]}
                seen = set()
                reordered: list[tuple[str, str, str]] = []
                for key in preferred_gen_order:
                    if key in def_map and key not in seen:
                        reordered.append(def_map[key]); seen.add(key)
                for tpl in ordered_section_definitions_pdf:
                    if tpl[0] not in seen:
                        reordered.append(tpl); seen.add(tpl[0])
                ordered_section_definitions_pdf = reordered
    except Exception as _e_order:
        # Still und robust: Bei Problemen Standard-Reihenfolge verwenden
        pass
    # Anwenden einer benutzerdefinierten Reihenfolge, falls vorhanden
    try:
        custom_order = (inclusion_options or {}).get('custom_section_order')
        if isinstance(custom_order, list) and custom_order:
            # Mapping von Key -> (Key, TitleKey, DefaultTitle)
            section_map = {key: tpl for key, *rest in [(tpl[0], *tpl[1:]) for tpl in ordered_section_definitions_pdf] for tpl in [ (key, rest[0], rest[1]) ]}
            # Obige Zeile formt eine Map, bewahrt aber das Tupel-Format
            section_map = {tpl[0]: tpl for tpl in ordered_section_definitions_pdf}
            added = set()
            reordered: List[tuple] = []
            # 1) Nach benutzerdefinierter Reihenfolge
            for k in custom_order:
                if k in section_map and k not in added:
                    reordered.append(section_map[k])
                    added.add(k)
            # 2) Rest in Standard-Reihenfolge anfügen
            for tpl in ordered_section_definitions_pdf:
                if tpl[0] not in added:
                    reordered.append(tpl)
                    added.add(tpl[0])
            ordered_section_definitions_pdf = reordered
    except Exception as _e_custom_order:
        # Bei Problemen mit der benutzerdefinierten Reihenfolge einfach Standardreihenfolge verwenden
        pass
    current_section_counter_pdf = 1
    for section_key_current, title_text_key_current, default_title_current in ordered_section_definitions_pdf:
        if section_key_current in active_sections_set_pdf:
            try:
                # SEITENUMBRUCH-SCHUTZ: Sammle alle Elemente einer Sektion
                section_elements = []
                
                chapter_title_for_header_current = section_chapter_titles_map.get(section_key_current, default_title_current.split('. ',1)[-1] if '. ' in default_title_current else default_title_current)
                story.append(SetCurrentChapterTitle(chapter_title_for_header_current))
                numbered_title_current = f"{current_section_counter_pdf}. {get_text(texts, title_text_key_current, default_title_current.split('. ',1)[-1] if '. ' in default_title_current else default_title_current)}"
                section_elements.append(Paragraph(numbered_title_current, STYLES.get('SectionTitle')))
                section_elements.append(Spacer(1, 0.2 * cm))

                if section_key_current == "ProjectOverview":
                    if pv_details_pdf.get('visualize_roof_in_pdf_satellite', True) and pv_details_pdf.get('satellite_image_base64_data'):
                        section_elements.append(Paragraph(get_text(texts,"satellite_image_header_pdf","Satellitenansicht Objekt"), STYLES.get('SubSectionTitle')))
                        sat_img_flowables = _get_image_flowable(pv_details_pdf['satellite_image_base64_data'], available_width_content * 0.8, texts, caption_text_key="satellite_image_caption_pdf", max_height=10*cm)
                        if sat_img_flowables: section_elements.extend(sat_img_flowables); section_elements.append(Spacer(1, 0.5*cm))
                    
                    overview_data_content_pdf = [
                        [get_text(texts,"anlage_size_label_pdf", "Anlagengröße"),format_kpi_value(current_analysis_results_pdf.get('anlage_kwp'),"kWp",texts_dict=texts, na_text_key="value_not_available_short_pdf")],
                        [get_text(texts,"module_quantity_label_pdf","Anzahl Module"),str(pv_details_pdf.get('module_quantity', get_text(texts, "value_not_available_short_pdf")))],
                        [get_text(texts,"annual_pv_production_kwh_pdf", "Jährliche PV-Produktion (ca.)"),format_kpi_value(current_analysis_results_pdf.get('annual_pv_production_kwh'),"kWh",precision=0,texts_dict=texts, na_text_key="value_not_available_short_pdf")],
                        [get_text(texts,"self_supply_rate_percent_pdf", "Autarkiegrad (ca.)"),format_kpi_value(current_analysis_results_pdf.get('self_supply_rate_percent'),"%",precision=1,texts_dict=texts, na_text_key="value_not_available_short_pdf")],
                    ]
                    if pv_details_pdf.get('include_storage'):
                         overview_data_content_pdf.extend([[get_text(texts,"selected_storage_capacity_label_pdf", "Speicherkapazität"),format_kpi_value(pv_details_pdf.get('selected_storage_storage_power_kw'),"kWh",texts_dict=texts, na_text_key="value_not_available_short_pdf")]])
                    if overview_data_content_pdf:
                        overview_table_data_styled_content_pdf = [[Paragraph(str(cell[0]),STYLES.get('TableLabel')),Paragraph(str(cell[1]),STYLES.get('TableText'))] for cell in overview_data_content_pdf]
                        overview_table_content_pdf = Table(overview_table_data_styled_content_pdf,colWidths=[available_width_content*0.5,available_width_content*0.5])
                        overview_table_content_pdf.setStyle(TABLE_STYLE_DEFAULT)
                        section_elements.append(overview_table_content_pdf)
                    
                    # SEITENUMBRUCH-SCHUTZ: Projektübersicht zusammenhalten
                    story.append(KeepTogether(section_elements))

                elif section_key_current == "TechnicalComponents":
                    section_elements.append(Paragraph(get_text(texts, "pdf_components_intro", "Nachfolgend die Details zu den Kernkomponenten Ihrer Anlage:"), STYLES.get('NormalLeft')))
                    section_elements.append(Spacer(1, 0.3*cm))
                    
                    # Für TechnicalComponents sind die Produktdetails bereits mit KeepTogether geschützt
                    # Also nur Titel und Intro zusammenhalten
                    story.append(KeepTogether(section_elements))
                    
                    # Mengenhinweis für Wechselrichter (z. B. "(2x)")
                    inverter_qty_suffix = ""
                    try:
                        inv_qty_val = int(pv_details_pdf.get("selected_inverter_quantity", 1) or 1)
                        if inv_qty_val > 1:
                            inverter_qty_suffix = f" ({inv_qty_val}x)"
                    except Exception:
                        inverter_qty_suffix = ""

                    main_components = [
                        (pv_details_pdf.get("selected_module_id"), get_text(texts, "pdf_component_module_title", "PV-Module")),
                        (pv_details_pdf.get("selected_inverter_id"), get_text(texts, "pdf_component_inverter_title", "Wechselrichter") + inverter_qty_suffix),
                    ]
                    if pv_details_pdf.get("include_storage"):
                        main_components.append((pv_details_pdf.get("selected_storage_id"), get_text(texts, "pdf_component_storage_title", "Batteriespeicher")))
                    
                    for comp_id, comp_title in main_components:
                        if comp_id: _add_product_details_to_story(story, comp_id, comp_title, texts, available_width_content, get_product_by_id_func, include_product_images_opt)

                    # ERWEITERUNG: Optionale Komponenten / Zubehör
                    if pv_details_pdf.get('include_additional_components', True) and include_optional_component_details_opt:
                        story.append(Paragraph(get_text(texts, "pdf_additional_components_header_pdf", "Optionale Komponenten"), STYLES.get('SubSectionTitle')))
                        optional_comps_map = {
                            'selected_wallbox_id': get_text(texts, "pdf_component_wallbox_title", "Wallbox"),
                            'selected_ems_id': get_text(texts, "pdf_component_ems_title", "Energiemanagementsystem"),
                            'selected_optimizer_id': get_text(texts, "pdf_component_optimizer_title", "Leistungsoptimierer"),
                            'selected_carport_id': get_text(texts, "pdf_component_carport_title", "Solarcarport"),
                            'selected_notstrom_id': get_text(texts, "pdf_component_emergency_power_title", "Notstromversorgung"),
                            'selected_tierabwehr_id': get_text(texts, "pdf_component_animal_defense_title", "Tierabwehrschutz")
                        }
                        any_optional_component_rendered = False
                        for key, title in optional_comps_map.items():
                            opt_comp_id = pv_details_pdf.get(key)
                            if opt_comp_id: 
                                _add_product_details_to_story(story, opt_comp_id, title, texts, available_width_content, get_product_by_id_func, include_product_images_opt)
                                any_optional_component_rendered = True
                        if not any_optional_component_rendered:
                            story.append(Paragraph(get_text(texts, "pdf_no_optional_components_selected_for_details", "Keine optionalen Komponenten für Detailanzeige ausgewählt."), STYLES.get('NormalLeft')))
                        
                elif section_key_current == "CostDetails":
                    cost_table_data_final_pdf = _prepare_cost_table_for_pdf(current_analysis_results_pdf, texts)
                    if cost_table_data_final_pdf:
                        cost_table_obj_final_pdf = Table(cost_table_data_final_pdf, colWidths=[available_width_content*0.6, available_width_content*0.4])
                        cost_table_obj_final_pdf.setStyle(TABLE_STYLE_DEFAULT)
                        
                        # SEITENUMBRUCH-SCHUTZ für Kostentabelle
                        cost_elements = [cost_table_obj_final_pdf]
                        
                        if current_analysis_results_pdf.get('base_matrix_price_netto', 0.0) == 0 and current_analysis_results_pdf.get('cost_storage_aufpreis_product_db_netto', 0.0) > 0: 
                            cost_elements.extend([Spacer(1,0.2*cm), Paragraph(get_text(texts, "analysis_storage_cost_note_single_price_pdf", "<i>Hinweis: Speicherkosten als Einzelposten, da kein Matrix-Pauschalpreis.</i>"), STYLES.get('TableTextSmall'))])
                        elif current_analysis_results_pdf.get('base_matrix_price_netto', 0.0) > 0 and current_analysis_results_pdf.get('cost_storage_aufpreis_product_db_netto', 0.0) > 0:
                            cost_elements.extend([Spacer(1,0.2*cm), Paragraph(get_text(texts, "analysis_storage_cost_note_matrix_pdf", "<i>Hinweis: Speicherkosten als Aufpreis, da Matrixpreis 'Ohne Speicher' verwendet wurde.</i>"), STYLES.get('TableTextSmall'))])
                        
                        section_elements.extend(cost_elements)
                    
                    # SEITENUMBRUCH-SCHUTZ: Kostendetails zusammenhalten
                    story.append(KeepTogether(section_elements))

                elif section_key_current == "Economics":
                    #  ERWEITERTE FINANZIERUNGSANALYSE
                    if financing_config and financing_config.get('enabled', False):
                        # Advanced Financing Header
                        section_elements.append(Paragraph(get_text(texts, "pdf_advanced_financing_title", " ERWEITERTE FINANZIERUNGSANALYSE"), STYLES.get('SectionTitle')))
                        section_elements.append(Spacer(1, 0.3*cm))
                        
                        # Scenario Comparison
                        if financing_config.get('scenario_analysis', False):
                            section_elements.append(Paragraph(get_text(texts, "pdf_financing_scenarios_title", " FINANZIERUNGSSZENARIEN"), STYLES.get('SubSectionTitle')))
                            
                            scenarios = ['conservative', 'balanced', 'aggressive']
                            scenario_labels = {
                                'conservative': 'Konservativ',
                                'balanced': 'Ausgeglichen', 
                                'aggressive': 'Optimistisch'
                            }
                            
                            scenario_data = []
                            scenario_data.append(['Szenario', 'ROI Jahr 1', 'Amortisation', 'Gesamtersparniss 20J'])
                            
                            for scenario in scenarios:
                                if scenario in financing_config:
                                    config = financing_config[scenario]
                                    scenario_data.append([
                                        scenario_labels[scenario],
                                        f"{config.get('roi_year_1', 0):.1f}%",
                                        f"{config.get('payback_years', 0):.1f} Jahre",
                                        f"{config.get('total_savings_20y', 0):,.0f} €"
                                    ])
                            
                            if len(scenario_data) > 1:
                                scenario_table = Table(scenario_data, colWidths=[
                                    available_width_content*0.25,
                                    available_width_content*0.25,
                                    available_width_content*0.25,
                                    available_width_content*0.25
                                ])
                                scenario_table.setStyle(TABLE_STYLE_DEFAULT)
                                section_elements.append(scenario_table)
                                section_elements.append(Spacer(1, 0.3*cm))
                        
                        # Sensitivity Analysis
                        if financing_config.get('sensitivity_analysis', False):
                            section_elements.append(Paragraph(get_text(texts, "pdf_sensitivity_analysis_title", " SENSITIVITÄTSANALYSE"), STYLES.get('SubSectionTitle')))
                            
                            sensitivity_text = f"""
                            <b>Einfluss verschiedener Parameter auf die Rentabilität:</b><br/>
                            • Strompreissteigerung: {financing_config.get('electricity_price_increase', 3)}% p.a.<br/>
                            • Inflation: {financing_config.get('inflation_rate', 2)}% p.a.<br/>
                            • Degradation PV-Module: {financing_config.get('module_degradation', 0.5)}% p.a.<br/>
                            • Eigenverbrauchsquote: {financing_config.get('self_consumption_ratio', 30)}-{financing_config.get('self_consumption_ratio', 30)+20}%<br/>
                            """
                            
                            section_elements.append(Paragraph(sensitivity_text, STYLES.get('NormalLeft')))
                            section_elements.append(Spacer(1, 0.3*cm))
                        
                        # Financing Options
                        if financing_config.get('financing_options', False):
                            section_elements.append(Paragraph(get_text(texts, "pdf_financing_options_title", " FINANZIERUNGSOPTIONEN"), STYLES.get('SubSectionTitle')))
                            
                            financing_options_data = []
                            financing_options_data.append(['Option', 'Zinssatz', 'Laufzeit', 'Monatl. Rate'])
                            
                            if financing_config.get('bank_loan'):
                                loan = financing_config['bank_loan']
                                financing_options_data.append([
                                    'Bankkredit',
                                    f"{loan.get('interest_rate', 0):.2f}%",
                                    f"{loan.get('duration_years', 0)} Jahre",
                                    f"{loan.get('monthly_payment', 0):,.0f} €"
                                ])
                            
                            if financing_config.get('kfw_loan'):
                                kfw = financing_config['kfw_loan']
                                financing_options_data.append([
                                    'KfW-Förderung',
                                    f"{kfw.get('interest_rate', 0):.2f}%",
                                    f"{kfw.get('duration_years', 0)} Jahre",
                                    f"{kfw.get('monthly_payment', 0):,.0f} €"
                                ])
                            
                            if len(financing_options_data) > 1:
                                financing_table = Table(financing_options_data, colWidths=[
                                    available_width_content*0.25,
                                    available_width_content*0.25,
                                    available_width_content*0.25,
                                    available_width_content*0.25
                                ])
                                financing_table.setStyle(TABLE_STYLE_DEFAULT)
                                section_elements.append(financing_table)
                                section_elements.append(Spacer(1, 0.5*cm))

                    # Standard Economics Data
                    eco_kpi_data_for_pdf_table = [
                        [get_text(texts, "total_investment_brutto_pdf", "Gesamtinvestition (Brutto)"), format_kpi_value(current_analysis_results_pdf.get('total_investment_brutto'), "€", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "annual_financial_benefit_pdf", "Finanzieller Vorteil (Jahr 1, ca.)"), format_kpi_value(current_analysis_results_pdf.get('annual_financial_benefit_year1'), "€", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "amortization_time_years_pdf", "Amortisationszeit (ca.)"), format_kpi_value(current_analysis_results_pdf.get('amortization_time_years'), "Jahre", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "simple_roi_percent_label_pdf", "Einfache Rendite (Jahr 1, ca.)"), format_kpi_value(current_analysis_results_pdf.get('simple_roi_percent'), "%", precision=1, texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "lcoe_euro_per_kwh_label_pdf", "Stromgestehungskosten (LCOE, ca.)"), format_kpi_value(current_analysis_results_pdf.get('lcoe_euro_per_kwh'), "€/kWh", precision=3, texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "npv_over_years_pdf", "Kapitalwert über Laufzeit (NPV, ca.)"), format_kpi_value(current_analysis_results_pdf.get('npv_value'), "€", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "irr_percent_pdf", "Interner Zinsfuß (IRR, ca.)"), format_kpi_value(current_analysis_results_pdf.get('irr_percent'), "%", precision=1, texts_dict=texts, na_text_key="value_not_calculated_short_pdf")]                    ]
                    if eco_kpi_data_for_pdf_table:
                        eco_kpi_table_styled_content = [[Paragraph(str(cell[0]), STYLES.get('TableLabel')), Paragraph(str(cell[1]), STYLES.get('TableNumber'))] for cell in eco_kpi_data_for_pdf_table]
                        eco_table_object = Table(eco_kpi_table_styled_content, colWidths=[available_width_content*0.6, available_width_content*0.4])
                        eco_table_object.setStyle(TABLE_STYLE_DEFAULT)
                        section_elements.append(eco_table_object)
                    
                    # SEITENUMBRUCH-SCHUTZ: Economics zusammenhalten
                    story.append(KeepTogether(section_elements))
                        
                elif section_key_current == "SimulationDetails":
                    sim_table_data_content_pdf = _prepare_simulation_table_for_pdf(current_analysis_results_pdf, texts, num_years_to_show=10)
                    if len(sim_table_data_content_pdf) > 1:
                        sim_table_obj_final_pdf = Table(sim_table_data_content_pdf, colWidths=None)
                        sim_table_obj_final_pdf.setStyle(DATA_TABLE_STYLE)
                        section_elements.append(sim_table_obj_final_pdf)
                    else: 
                        section_elements.append(Paragraph(get_text(texts, "pdf_simulation_data_not_available", "Simulationsdetails nicht ausreichend für Tabellendarstellung."), STYLES.get('NormalLeft')))
                    
                    # SEITENUMBRUCH-SCHUTZ: Simulation zusammenhalten
                    story.append(KeepTogether(section_elements))

                elif section_key_current == "CO2Savings":
                    co2_savings_val = current_analysis_results_pdf.get('annual_co2_savings_kg', 0.0)
                    trees_equiv = current_analysis_results_pdf.get('co2_equivalent_trees_per_year', 0.0)
                    car_km_equiv = current_analysis_results_pdf.get('co2_equivalent_car_km_per_year', 0.0)
                    airplane_km_equiv = co2_savings_val / 0.23 if co2_savings_val > 0 else 0.0
                    
                    # Verbesserter CO₂-Text mit mehr Details und professioneller Formatierung
                    co2_intro = get_text(texts, "pdf_co2_intro", "Mit Ihrer neuen Photovoltaikanlage leisten Sie einen wertvollen Beitrag zum Klimaschutz:")
                    section_elements.append(Paragraph(co2_intro, STYLES.get('NormalLeft')))
                    section_elements.append(Spacer(1, 0.2 * cm))
                    
                    # Haupteinsparung hervorheben
                    co2_main = get_text(texts, "pdf_annual_co2_main", " <b>Jährliche CO₂-Einsparung: {co2_savings_kg_formatted} kg</b>").format(
                        co2_savings_kg_formatted=format_kpi_value(co2_savings_val, "", precision=0, texts_dict=texts)
                    )
                    section_elements.append(Paragraph(co2_main, STYLES.get('HeadingCenter')))
                    section_elements.append(Spacer(1, 0.3 * cm))
                    
                    # Anschauliche Vergleiche in einer schönen Tabelle
                    co2_data = [
                        [get_text(texts, "pdf_co2_comparison_header", "Vergleich"), get_text(texts, "pdf_co2_equivalent_header", "Entspricht")],
                        [" Bäume (CO₂-Bindung)", f"{trees_equiv:.0f} Bäume pro Jahr"],
                        [" Autofahrten", f"{car_km_equiv:,.0f} km weniger pro Jahr"],
                        [" Flugreisen", f"{airplane_km_equiv:,.0f} km weniger pro Jahr"],
                        [" CO₂-Fußabdruck", get_text(texts, "pdf_co2_footprint_reduction", "Deutliche Reduktion Ihres persönlichen CO₂-Fußabdrucks")]
                    ]
                    
                    co2_table = Table(co2_data, colWidths=[8*cm, 8*cm])
                    co2_table.setStyle(TableStyle([
                        # Header-Stil
                        ('BACKGROUND', (0, 0), (-1, 0), COLORS['table_header_bg']),
                        ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['table_header_text']),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                        
                        # Datenzeilen
                        ('BACKGROUND', (0, 1), (-1, -1), COLORS['table_row_bg']),
                        ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text_dark']),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                        
                        # Rahmen und Linien
                        ('GRID', (0, 0), (-1, -1), 1, COLORS['table_border']),
                        ('LINEBELOW', (0, 0), (-1, 0), 2, COLORS['accent_primary']),
                        
                        # Zebra-Streifen für bessere Lesbarkeit
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['table_row_bg'], COLORS['table_alt_row_bg']]),
                        
                        # Padding
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ]))
                    
                    section_elements.append(co2_table)
                    section_elements.append(Spacer(1, 0.3 * cm))
                    
                    # CO₂-Grafik einfügen, falls verfügbar
                    co2_chart_bytes = current_analysis_results_pdf.get('co2_savings_chart_bytes')
                    if co2_chart_bytes:
                        try:
                            co2_img = ImageReader(io.BytesIO(co2_chart_bytes))
                            co2_image = Image(co2_img, width=16*cm, height=10*cm)
                            section_elements.append(co2_image)
                            section_elements.append(Spacer(1, 0.2 * cm))
                        except Exception as e:
                            print(f"Fehler beim Einfügen der CO₂-Grafik: {e}")
                    
                    # Abschließender motivierender Text
                    co2_conclusion = get_text(texts, "pdf_co2_conclusion", "Diese Zahlen verdeutlichen den positiven Umweltbeitrag Ihrer Photovoltaikanlage. Über die gesamte Betriebsdauer von 25+ Jahren summiert sich die CO₂-Einsparung auf mehrere Tonnen – ein wichtiger Schritt für den Klimaschutz und nachfolgende Generationen.")
                    section_elements.append(Paragraph(co2_conclusion, STYLES.get('NormalLeft')))
                    
                    # SEITENUMBRUCH-SCHUTZ: CO2Savings zusammenhalten
                    story.append(KeepTogether(section_elements))

                elif section_key_current == "Visualizations":
                    # INTRO nur als Überschrift - keine gemeinsame Sektion
                    intro_elements = []
                    intro_elements.append(Paragraph(get_text(texts, "pdf_visualizations_intro", "Die folgenden Diagramme visualisieren die Ergebnisse Ihrer Photovoltaikanlage und deren Wirtschaftlichkeit:"), STYLES.get('NormalLeft')))
                    intro_elements.append(Spacer(1, 0.5 * cm))
                    story.append(KeepTogether(intro_elements))
                    
                    # ERWEITERUNG: Vollständige Liste der Diagramme für PDF-Auswahl
                    # Diese Map sollte idealerweise mit `chart_key_to_friendly_name_map` aus `pdf_ui.py` synchronisiert werden.
                    charts_config_for_pdf_generator = {
                        'monthly_prod_cons_chart_bytes': {"title_key": "pdf_chart_title_monthly_comp_pdf", "default_title": "Monatl. Produktion/Verbrauch (2D)"},
                        'cost_projection_chart_bytes': {"title_key": "pdf_chart_label_cost_projection", "default_title": "Stromkosten-Hochrechnung (2D)"},
                        'cumulative_cashflow_chart_bytes': {"title_key": "pdf_chart_label_cum_cashflow", "default_title": "Kumulierter Cashflow (2D)"},
                        'consumption_coverage_pie_chart_bytes': {"title_key": "pdf_chart_title_consumption_coverage_pdf", "default_title": "Deckung Gesamtverbrauch (Jahr 1)"},
                        'pv_usage_pie_chart_bytes': {"title_key": "pdf_chart_title_pv_usage_pdf", "default_title": "Nutzung PV-Strom (Jahr 1)"},
                        'daily_production_switcher_chart_bytes': {"title_key": "pdf_chart_label_daily_3d", "default_title": "Tagesproduktion (3D)"},
                        'weekly_production_switcher_chart_bytes': {"title_key": "pdf_chart_label_weekly_3d", "default_title": "Wochenproduktion (3D)"},
                        'yearly_production_switcher_chart_bytes': {"title_key": "pdf_chart_label_yearly_3d_bar", "default_title": "Jahresproduktion (3D-Balken)"},
                        'project_roi_matrix_switcher_chart_bytes': {"title_key": "pdf_chart_label_roi_matrix_3d", "default_title": "Projektrendite-Matrix (3D)"},
                        'feed_in_revenue_switcher_chart_bytes': {"title_key": "pdf_chart_label_feedin_3d", "default_title": "Einspeisevergütung (3D)"},
                        'prod_vs_cons_switcher_chart_bytes': {"title_key": "pdf_chart_label_prodcons_3d", "default_title": "Verbr. vs. Prod. (3D)"},
                        'tariff_cube_switcher_chart_bytes': {"title_key": "pdf_chart_label_tariffcube_3d", "default_title": "Tarifvergleich (3D)"},
                        'co2_savings_value_switcher_chart_bytes': {"title_key": "pdf_chart_label_co2value_3d", "default_title": "CO2-Ersparnis vs. Wert (3D)"},
                        'co2_savings_chart_bytes': {"title_key": "pdf_chart_label_co2_realistic", "default_title": "CO₂-Einsparung (Realistische Darstellung)"},
                        'investment_value_switcher_chart_bytes': {"title_key": "pdf_chart_label_investval_3D", "default_title": "Investitionsnutzwert (3D)"},
                        'storage_effect_switcher_chart_bytes': {"title_key": "pdf_chart_label_storageeff_3d", "default_title": "Speicherwirkung (3D)"},
                        'selfuse_stack_switcher_chart_bytes': {"title_key": "pdf_chart_label_selfusestack_3d", "default_title": "Eigenverbr. vs. Einspeis. (3D)"},
                        'cost_growth_switcher_chart_bytes': {"title_key": "pdf_chart_label_costgrowth_3d", "default_title": "Stromkostensteigerung (3D)"},
                        'selfuse_ratio_switcher_chart_bytes': {"title_key": "pdf_chart_label_selfuseratio_3d", "default_title": "Eigenverbrauchsgrad (3D)"},
                        'roi_comparison_switcher_chart_bytes': {"title_key": "pdf_chart_label_roicompare_3d", "default_title": "ROI-Vergleich (3D)"},
                        'scenario_comparison_switcher_chart_bytes': {"title_key": "pdf_chart_label_scenariocomp_3d", "default_title": "Szenarienvergleich (3D)"},
                        'tariff_comparison_switcher_chart_bytes': {"title_key": "pdf_chart_label_tariffcomp_3d", "default_title": "Vorher/Nachher Stromkosten (3D)"},
                        'income_projection_switcher_chart_bytes': {"title_key": "pdf_chart_label_incomeproj_3d", "default_title": "Einnahmenprognose (3D)"},
                        'yearly_production_chart_bytes': {"title_key": "pdf_chart_label_pvvis_yearly", "default_title": "PV Visuals: Jahresproduktion"},
                        'break_even_chart_bytes': {"title_key": "pdf_chart_label_pvvis_breakeven", "default_title": "PV Visuals: Break-Even"},
                        'amortisation_chart_bytes': {"title_key": "pdf_chart_label_pvvis_amort", "default_title": "PV Visuals: Amortisation"},
                    }
                    charts_added_count = 0
                    selected_charts_for_pdf_opt = inclusion_options.get("selected_charts_for_pdf", [])
                    
                    # SMARTES LAYOUT: Gruppiere Diagramme für optimale Seitenaufteilung
                    charts_per_page = 3  # Max 3 Diagramme pro Seite
                    current_page_chart_count = 0
                    
                    # Chart-spezifische Verarbeitung basierend auf Konfiguration
                    for chart_key, config in charts_config_for_pdf_generator.items():
                        if chart_key not in selected_charts_for_pdf_opt:
                            continue # Überspringe dieses Diagramm, wenn nicht vom Nutzer ausgewählt

                        chart_image_bytes = current_analysis_results_pdf.get(chart_key)
                        if chart_image_bytes and isinstance(chart_image_bytes, bytes):
                            # NEUE SEITE wenn bereits 3 Diagramme auf aktueller Seite
                            if current_page_chart_count >= charts_per_page:
                                story.append(PageBreak())
                                current_page_chart_count = 0
                            
                            # KOMPAKTERE DIAGRAMME für mehrere pro Seite
                            chart_elements = []
                            
                            chart_display_title = get_text(texts, config["title_key"], config["default_title"])
                            chart_display_title = _sanitize_chart_title(chart_display_title)
                            
                            # Chart Title (kompakter)
                            chart_elements.append(Paragraph(f"<b>{chart_display_title}</b>", STYLES.get('SubSectionTitle')))
                            chart_elements.append(Spacer(1, 0.1*cm))
                            
                            # NOCH KLEINERE DIAGRAMMGRÖSSE für 3 pro Seite
                            chart_width = available_width_content * 0.6  # Reduziert von 0.7 auf 0.6
                            max_height = 5*cm  # Reduziert von 6cm auf 5cm für mehr Platz
                            
                            img_flowables_chart = _get_image_flowable(chart_image_bytes, chart_width, texts, max_height=max_height, align='CENTER')
                            if img_flowables_chart: 
                                chart_elements.extend(img_flowables_chart)
                                chart_elements.append(Spacer(1, 0.2*cm))
                                # Kompakte KPI-Zeile oberhalb der Beschreibung
                                kpi_html = _build_chart_kpi_html(chart_key, current_analysis_results_pdf, texts)
                                if kpi_html:
                                    chart_elements.append(Paragraph(kpi_html, STYLES.get('TableTextSmall')))
                                    chart_elements.append(Spacer(1, 0.15*cm))
                                
                                # DIAGRAMM-BESCHREIBUNG hinzufügen
                                chart_description = _get_chart_description(chart_key, texts)
                                chart_elements.append(Paragraph(f"<i>{chart_description}</i>", STYLES.get('TableTextSmall')))
                                chart_elements.append(Spacer(1, 0.4*cm))
                                
                                # KOMPAKTERER SEITENUMBRUCH-SCHUTZ: Nur einzelnes Chart schützen
                                story.append(KeepTogether(chart_elements))
                                charts_added_count += 1
                                current_page_chart_count += 1
                            else: 
                                chart_elements.append(Paragraph(get_text(texts, "pdf_chart_load_error_placeholder_param", f"(Fehler beim Laden: {chart_display_title})"), STYLES.get('NormalCenter')))
                                chart_elements.append(Spacer(1, 0.3*cm))
                                story.append(KeepTogether(chart_elements))
                                current_page_chart_count += 1
                    
                    if charts_added_count == 0 and selected_charts_for_pdf_opt : # Wenn Charts ausgewählt wurden, aber keine gerendert werden konnten
                         fallback_elements = []
                         fallback_elements.append(Paragraph(get_text(texts, "pdf_selected_charts_not_renderable", "Ausgewählte Diagramme konnten nicht geladen/angezeigt werden."), STYLES.get('NormalCenter')))
                         story.append(KeepTogether(fallback_elements))
                    elif not selected_charts_for_pdf_opt : # Wenn gar keine Charts ausgewählt wurden
                         fallback_elements = []
                         fallback_elements.append(Paragraph(get_text(texts, "pdf_no_charts_selected_for_section", "Keine Diagramme für diese Sektion ausgewählt."), STYLES.get('NormalCenter')))
                         story.append(KeepTogether(fallback_elements))

                elif section_key_current == "FutureAspects":
                    future_aspects_text = ""
                    if pv_details_pdf.get('future_ev'):
                        future_aspects_text += get_text(texts, "pdf_future_ev_text_param", "<b>E-Mobilität:</b> Die Anlage ist auf eine zukünftige Erweiterung um ein Elektrofahrzeug vorbereitet. Der prognostizierte PV-Anteil an der Fahrzeugladung beträgt ca. {eauto_pv_coverage_kwh:.0f} kWh/Jahr.").format(eauto_pv_coverage_kwh=current_analysis_results_pdf.get('eauto_ladung_durch_pv_kwh',0.0)) + "<br/>"
                    if pv_details_pdf.get('future_hp'):
                        future_aspects_text += get_text(texts, "pdf_future_hp_text_param", "<b>Wärmepumpe:</b> Die Anlage kann zur Unterstützung einer zukünftigen Wärmepumpe beitragen. Der geschätzte PV-Deckungsgrad für die Wärmepumpe liegt bei ca. {hp_pv_coverage_pct:.0f}%. ").format(hp_pv_coverage_pct=current_analysis_results_pdf.get('pv_deckungsgrad_wp_pct',0.0)) + "<br/>"
                    if not future_aspects_text: future_aspects_text = get_text(texts, "pdf_no_future_aspects_selected", "Keine spezifischen Zukunftsaspekte für dieses Angebot ausgewählt.")
                    section_elements.append(Paragraph(future_aspects_text, STYLES.get('NormalLeft')))
                    
                    # SEITENUMBRUCH-SCHUTZ: FutureAspects zusammenhalten
                    story.append(KeepTogether(section_elements))
                
                # NEUE OPTIONALE SEITENVORLAGEN (individuell gestaltbar, wie gewünscht)
                elif section_key_current == "CompanyProfile":
                    company_profile_text = get_text(texts, "pdf_company_profile_content", 
                        f"<b>{company_info.get('name', 'Unser Unternehmen')}</b><br/><br/>"
                        f"Mit langjähriger Erfahrung im Bereich Photovoltaik sind wir Ihr zuverlässiger Partner für nachhaltige Energielösungen. "
                        f"Unser engagiertes Team begleitet Sie von der ersten Beratung bis zur finalen Inbetriebnahme Ihrer Anlage.<br/><br/>"
                        f"<b>Kontakt:</b><br/>"
                        f" {company_info.get('street', '')}, {company_info.get('zip_code', '')} {company_info.get('city', '')}<br/>"
                        f" {company_info.get('phone', '')}<br/>"
                        f" {company_info.get('email', '')}")
                    section_elements.append(Paragraph(company_profile_text, STYLES.get('NormalLeft')))
                    
                    # SEITENUMBRUCH-SCHUTZ: CompanyProfile zusammenhalten
                    story.append(KeepTogether(section_elements))
                
                elif section_key_current == "Certifications":
                    cert_text = get_text(texts, "pdf_certifications_content",
                        "<b>Unsere Zertifizierungen & Qualitätsstandards:</b><br/><br/>"
                        " <b>VDE-Zertifizierung</b> - Elektrotechnische Sicherheit<br/>"
                        " <b>Meisterbetrieb</b> - Handwerkliche Qualität<br/>"
                        " <b>IHK-Sachverständiger</b> - Technische Expertise<br/>"
                        " <b>ISO 9001</b> - Qualitätsmanagementsystem<br/>"
                        " <b>Fachbetrieb für Photovoltaik</b> - Spezialisierung<br/><br/>"
                        "Alle Komponenten entsprechen den aktuellen DIN- und VDE-Normen.")
                    section_elements.append(Paragraph(cert_text, STYLES.get('NormalLeft')))
                    
                    # SEITENUMBRUCH-SCHUTZ: Certifications zusammenhalten
                    story.append(KeepTogether(section_elements))
                
                elif section_key_current == "References":
                    ref_text = get_text(texts, "pdf_references_content",
                        "<b>Referenzen & Kundenerfahrungen:</b><br/><br/>"
                        " <i>\"Professionelle Beratung und saubere Montage. Unsere Anlage läuft seit 2 Jahren perfekt!\"</i><br/>"
                        "- Familie Müller, 8,5 kWp Anlage<br/><br/>"
                        " <i>\"Von der Planung bis zur Inbetriebnahme - alles aus einer Hand und termingerecht.\"</i><br/>"
                        "- Herr Schmidt, 12 kWp mit Speicher<br/><br/>"
                        " <i>\"Kompetente Beratung, faire Preise, einwandfreie Ausführung. Sehr empfehlenswert!\"</i><br/>"
                        "- Frau Weber, 6,2 kWp Anlage<br/><br/>"
                        "<b>Über 500 zufriedene Kunden</b> vertrauen auf unsere Expertise.")
                    section_elements.append(Paragraph(ref_text, STYLES.get('NormalLeft')))
                    
                    # SEITENUMBRUCH-SCHUTZ: References zusammenhalten
                    story.append(KeepTogether(section_elements))
                
                elif section_key_current == "Installation":
                    install_text = get_text(texts, "pdf_installation_content",
                        "<b>Professionelle Installation - Ihr Weg zur eigenen Solaranlage:</b><br/><br/>"
                        "<b>1. Terminplanung & Vorbereitung</b><br/>"
                        "• Detaillierte Terminabsprache<br/>"
                        "• Anmeldung beim Netzbetreiber<br/>"
                        "• Bereitstellung aller Komponenten<br/><br/>"
                        "<b>2. Montage (1-2 Tage)</b><br/>"
                        "• Dachmontage durch zertifizierte Dachdecker<br/>"
                        "• Elektrische Installation durch Elektromeister<br/>"
                        "• Sicherheitsprüfung nach VDE-Norm<br/><br/>"
                        "<b>3. Inbetriebnahme & Übergabe</b><br/>"
                        "• Funktionstest und Messung<br/>"
                        "• Einweisung in die Bedienung<br/>"
                        "• Übergabe aller Unterlagen")
                    section_elements.append(Paragraph(install_text, STYLES.get('NormalLeft')))
                    
                    # SEITENUMBRUCH-SCHUTZ: Installation zusammenhalten
                    story.append(KeepTogether(section_elements))
                
                elif section_key_current == "Maintenance":
                    maint_text = get_text(texts, "pdf_maintenance_content",
                        "<b>Wartung & Langzeitservice für maximale Erträge:</b><br/><br/>"
                        "<b>Wartungsleistungen:</b><br/>"
                        "• Jährliche Sichtprüfung der Module<br/>"
                        "• Überprüfung der elektrischen Verbindungen<br/>"
                        "• Funktionstest des Wechselrichters<br/>"
                        "• Reinigung bei Bedarf<br/>"
                        "• Ertragskontrolle und Optimierung<br/><br/>"
                        "<b>24/7 Monitoring:</b><br/>"
                        "• Online-Überwachung der Anlagenleistung<br/>"
                        "• Automatische Störungsmeldung<br/>"
                        "• Ferndiagnose und schnelle Hilfe<br/><br/>"
                        "<b>Wartungsvertrag verfügbar</b> - Sprechen Sie uns an!")
                    section_elements.append(Paragraph(maint_text, STYLES.get('NormalLeft')))
                    
                    # SEITENUMBRUCH-SCHUTZ: Maintenance zusammenhalten
                    story.append(KeepTogether(section_elements))
                
                elif section_key_current == "Financing":
                    fin_text = get_text(texts, "pdf_financing_content",
                        "<b>Flexible Finanzierungsmöglichkeiten:</b><br/><br/>"
                        " <b>KfW-Förderung</b><br/>"
                        "• Zinsgünstige Darlehen bis 150.000€<br/>"
                        "• Tilgungszuschüsse möglich<br/>"
                        "• Wir unterstützen bei der Antragstellung<br/><br/>"
                        " <b>Bankfinanzierung</b><br/>"
                        "• Partnerschaften mit regionalen Banken<br/>"
                        "• Attraktive Konditionen für Solaranlagen<br/>"
                        "• Laufzeiten bis 20 Jahre<br/><br/>"
                        " <b>Leasing & Pacht</b><br/>"
                        "• Keine Anfangsinvestition<br/>"
                        "• Monatliche Raten ab 89€<br/>"
                        "• Rundum-Sorglos-Paket inklusive<br/><br/>"
                        "Gerne erstellen wir Ihnen ein individuelles Finanzierungskonzept!")
                    section_elements.append(Paragraph(fin_text, STYLES.get('NormalLeft')))
                    
                    # SEITENUMBRUCH-SCHUTZ: Financing zusammenhalten
                    story.append(KeepTogether(section_elements))
                
                elif section_key_current == "Insurance":
                    ins_text = get_text(texts, "pdf_insurance_content",
                        "<b>Umfassender Versicherungsschutz für Ihre Investition:</b><br/><br/>"
                        " <b>Photovoltaik-Versicherung</b><br/>"
                        "• Schutz vor Sturm, Hagel, Blitzschlag<br/>"
                        "• Diebstahl- und Vandalismus-Schutz<br/>"
                        "• Elektronikversicherung für Wechselrichter<br/><br/>"
                        " <b>Ertragsausfallversicherung</b><br/>"
                        "• Absicherung bei Produktionsausfall<br/>"
                        "• Ersatz entgangener EEG-Vergütung<br/>"
                        "• Mehrkosten bei Reparaturen<br/><br/>"
                        " <b>Integration in bestehende Versicherungen</b><br/>"
                        "• Prüfung der Wohngebäudeversicherung<br/>"
                        "• Anpassung bestehender Policen<br/>"
                        "• Kostengünstige Ergänzungen<br/><br/>"
                        "Wir beraten Sie gerne zu optimalen Versicherungslösungen!")
                    section_elements.append(Paragraph(ins_text, STYLES.get('NormalLeft')))
                    
                    # SEITENUMBRUCH-SCHUTZ: Insurance zusammenhalten
                    story.append(KeepTogether(section_elements))
                
                elif section_key_current == "Warranty":
                    warr_text = get_text(texts, "pdf_warranty_content",
                        "<b>Garantie & Gewährleistung - Ihre Sicherheit:</b><br/><br/>"
                        " <b>Herstellergarantien:</b><br/>"
                        "• <b>Module:</b> 25 Jahre Leistungsgarantie<br/>"
                        "• <b>Wechselrichter:</b> 10-20 Jahre Herstellergarantie<br/>"
                        "• <b>Speichersystem:</b> 10 Jahre Garantie<br/>"
                        "• <b>Montagesystem:</b> 15 Jahre Material-/Korrosionsschutz<br/><br/>"
                        " <b>Handwerkergewährleistung:</b><br/>"
                        "• 2 Jahre auf Montage und Installation<br/>"
                        "• 5 Jahre erweiterte Gewährleistung möglich<br/>"
                        "• Schnelle Reaktionszeiten bei Problemen<br/><br/>"
                        " <b>Service-Hotline:</b><br/>"
                        "• Kostenlose Beratung bei Fragen<br/>"
                        "• Ferndiagnose und Support<br/>"
                        "• Vor-Ort-Service innerhalb 48h<br/><br/>"
                        "<b>Ihr Vertrauen ist unsere Verpflichtung!</b>")
                    section_elements.append(Paragraph(warr_text, STYLES.get('NormalLeft')))
                    section_elements.append(Spacer(1, 0.5*cm))
                    
                    # SEITENUMBRUCH-SCHUTZ: Warranty zusammenhalten
                    story.append(KeepTogether(section_elements))
                
                # Aktualisiere Counter
                current_section_counter_pdf +=1
            except Exception as e_section:
                error_elements = []
                error_elements.append(Paragraph(f"Fehler in Sektion '{default_title_current}': {e_section}", STYLES.get('NormalLeft')))
                error_elements.append(Spacer(1, 0.5*cm))
                # SEITENUMBRUCH-SCHUTZ auch für Fehlermeldungen
                story.append(KeepTogether(error_elements))
                current_section_counter_pdf +=1
    
    #  CUSTOM CONTENT INTEGRATION
    if custom_content_items and len(custom_content_items) > 0:
        story.append(PageBreak())
        story.append(SetCurrentChapterTitle("BENUTZERDEFINIERTE INHALTE"))
        
        # SEITENUMBRUCH-SCHUTZ für Custom Content Header
        custom_header_elements = []
        custom_header_elements.append(Paragraph(" BENUTZERDEFINIERTE INHALTE", STYLES.get('SectionTitle')))
        custom_header_elements.append(Spacer(1, 0.5*cm))
        story.append(KeepTogether(custom_header_elements))
        
        # Sortiere Custom Content nach Position
        top_items = [item for item in custom_content_items if item.get('position') == 'top']
        middle_items = [item for item in custom_content_items if item.get('position') == 'middle']
        bottom_items = [item for item in custom_content_items if item.get('position') == 'bottom']
        
        # Alle Items in der richtigen Reihenfolge
        all_custom_items = top_items + middle_items + bottom_items
        
        for item in all_custom_items:
            item_type = item.get('type', 'text')
            item_title = item.get('title', 'Custom Content')
            
            try:
                # SEITENUMBRUCH-SCHUTZ für jedes Custom Content Item
                item_elements = []
                
                if item_type == 'text':
                    # Text-Content
                    item_elements.append(Paragraph(f"<b>{item_title}</b>", STYLES.get('SubSectionTitle')))
                    
                    content = item.get('content', '')
                    style = item.get('style', 'normal')
                    
                    if style == 'bold':
                        content = f"<b>{content}</b>"
                    elif style == 'italic':
                        content = f"<i>{content}</i>"
                    elif style == 'highlight':
                        content = f"<b><font color='#ff7b7b'>{content}</font></b>"
                    elif style == 'quote':
                        content = f"<i>\"{content}\"</i>"
                    
                    item_elements.append(Paragraph(content, STYLES.get('NormalLeft')))
                    item_elements.append(Spacer(1, 0.3*cm))
                
                elif item_type == 'image' and item.get('content'):
                    # Image-Content
                    item_elements.append(Paragraph(f"<b>{item_title}</b>", STYLES.get('SubSectionTitle')))
                    
                    try:
                        import base64
                        image_data = base64.b64decode(item['content'])
                        
                        # Bildgröße basierend auf Konfiguration
                        size = item.get('size', 'medium')
                        if size == 'small':
                            image_width = available_width_content * 0.4
                        elif size == 'large':
                            image_width = available_width_content * 0.8
                        elif size == 'full':
                            image_width = available_width_content
                        else:  # medium
                            image_width = available_width_content * 0.6
                        
                        img_flowables = _get_image_flowable(image_data, image_width, texts, max_height=10*cm, align='CENTER')
                        if img_flowables:
                            item_elements.extend(img_flowables)
                            
                            # Bildunterschrift
                            caption = item.get('caption', '')
                            if caption:
                                item_elements.append(Spacer(1, 0.2*cm))
                                item_elements.append(Paragraph(f"<i>{caption}</i>", STYLES.get('TableTextSmall')))
                        
                        item_elements.append(Spacer(1, 0.5*cm))
                    except Exception as img_error:
                        item_elements.append(Paragraph(f"[Fehler beim Laden des Bildes: {img_error}]", STYLES.get('NormalLeft')))
                        item_elements.append(Spacer(1, 0.3*cm))
                
                elif item_type == 'table':
                    # Table-Content
                    item_elements.append(Paragraph(f"<b>{item_title}</b>", STYLES.get('SubSectionTitle')))
                    
                    headers = item.get('headers', [])
                    rows = item.get('rows', [])
                    
                    if headers and rows:
                        # Tabellendaten vorbereiten
                        table_data = [headers]
                        table_data.extend(rows)
                        
                        # Spaltenbreiten berechnen
                        num_cols = len(headers)
                        col_width = available_width_content / num_cols
                        col_widths = [col_width] * num_cols
                        
                        # Tabelle erstellen
                        custom_table = Table(table_data, colWidths=col_widths)
                        custom_table.setStyle(TABLE_STYLE_DEFAULT)
                        item_elements.append(custom_table)
                        item_elements.append(Spacer(1, 0.5*cm))
                    else:
                        item_elements.append(Paragraph("[Keine Tabellendaten verfügbar]", STYLES.get('NormalLeft')))
                        item_elements.append(Spacer(1, 0.3*cm))
                
                # SEITENUMBRUCH-SCHUTZ: Jedes Custom Content Item zusammenhalten
                story.append(KeepTogether(item_elements))
                
            except Exception as item_error:
                error_item_elements = []
                error_item_elements.append(Paragraph(f"[Fehler beim Verarbeiten von '{item_title}': {item_error}]", STYLES.get('NormalLeft')))
                error_item_elements.append(Spacer(1, 0.3*cm))
                # SEITENUMBRUCH-SCHUTZ auch für Fehlermeldungen in Custom Content
                story.append(KeepTogether(error_item_elements))
    
    #  PDF DESIGN STYLING (falls konfiguriert)
    if pdf_design_config and pdf_design_config.get('theme'):
        theme_name = pdf_design_config.get('theme')
        # Note: Design-Anpassungen werden hier notiert, aber die meisten Styling-Änderungen 
        # müssten in den STYLES und Farben vorgenommen werden
        story.append(Paragraph(f"<i>PDF erstellt mit '{theme_name.title()}' Design-Theme</i>", STYLES.get('TableTextSmall')))
        story.append(Spacer(1, 0.2*cm))
    
    main_pdf_bytes: Optional[bytes] = None
    try:
        layout_callback_kwargs_build = {
            'texts_ref': texts, 'company_info_ref': company_info,
            'company_logo_base64_ref': company_logo_base64 if include_company_logo_opt else None,
            'offer_number_ref': offer_number_final, 'page_width_ref': doc.pagesize[0], 
            'page_height_ref': doc.pagesize[1],'margin_left_ref': doc.leftMargin, 
            'margin_right_ref': doc.rightMargin,'margin_top_ref': doc.topMargin, 
            'margin_bottom_ref': doc.bottomMargin,'doc_width_ref': doc.width, 'doc_height_ref': doc.height,
            # NEUE OPTIONEN (wie gewünscht)
            'include_custom_footer_ref': include_custom_footer_opt,
            'include_header_logo_ref': include_header_logo_opt
        }
        doc.build(story, canvasmaker=lambda *args, **kwargs_c: PageNumCanvas(*args, onPage_callback=page_layout_handler, callback_kwargs=layout_callback_kwargs_build, **kwargs_c))
        main_pdf_bytes = main_offer_buffer.getvalue()
    except Exception as e_build_pdf:
        return _create_plaintext_pdf_fallback(project_data, analysis_results, texts, company_info, selected_offer_title_text, selected_cover_letter_text)
    finally:
        main_offer_buffer.close()
    
    if not main_pdf_bytes: 
        return None
    
    # PDF-Anhänge nur wenn beide Bedingungen erfüllt sind
    if not (include_all_documents_opt and _PYPDF_AVAILABLE):
        return main_pdf_bytes

    paths_to_append: List[str] = []
    debug_info = {
        'product_datasheets_found': [],
        'product_datasheets_missing': [],
        'company_docs_found': [],
        'company_docs_missing': [],
        'total_paths_to_append': 0
    }
    
    # Produktdatenblätter (Hauptkomponenten UND Zubehör)
    product_ids_for_datasheets = list(filter(None, [
        pv_details_pdf.get("selected_module_id"),
        pv_details_pdf.get("selected_inverter_id"),
        pv_details_pdf.get("selected_storage_id") if pv_details_pdf.get("include_storage") else None
    ]))
    if pv_details_pdf.get('include_additional_components', True): # Nur wenn Zubehör überhaupt aktiv ist
        for opt_id_key in ['selected_wallbox_id', 'selected_ems_id', 'selected_optimizer_id', 'selected_carport_id', 'selected_notstrom_id', 'selected_tierabwehr_id']:
            comp_id_val = pv_details_pdf.get(opt_id_key)
            if comp_id_val: product_ids_for_datasheets.append(comp_id_val)
    
    # Duplikate entfernen, falls ein Produkt mehrfach auftaucht (unwahrscheinlich, aber sicher)
    product_ids_for_datasheets = list(set(product_ids_for_datasheets))

    for prod_id in product_ids_for_datasheets:
        try:
            product_info = get_product_by_id_func(prod_id) 
            if product_info:
                datasheet_path_from_db = product_info.get("datasheet_link_db_path")
                if datasheet_path_from_db:
                    full_datasheet_path = os.path.join(PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN, datasheet_path_from_db)
                    if os.path.exists(full_datasheet_path):
                        paths_to_append.append(full_datasheet_path)
                        debug_info['product_datasheets_found'].append({'id': prod_id, 'model': product_info.get('model_name'), 'path': full_datasheet_path})
                    else:
                        debug_info['product_datasheets_missing'].append({'id': prod_id, 'model': product_info.get('model_name'), 'path': full_datasheet_path})
                else:
                    debug_info['product_datasheets_missing'].append({'id': prod_id, 'model': product_info.get('model_name'), 'reason': 'Kein Datenblatt-Pfad in DB'})
            else:
                debug_info['product_datasheets_missing'].append({'id': prod_id, 'reason': 'Produkt nicht in DB gefunden'})
        except Exception as e_prod:
            # Fehler beim Laden von Produktinformationen - wird still behandelt
            pass
            
    # Firmendokumente
    if company_document_ids_to_include_opt and active_company_id is not None and callable(db_list_company_documents_func):
        try:
            all_company_docs_for_active_co = db_list_company_documents_func(active_company_id, None) # doc_type=None für alle
            for doc_info in all_company_docs_for_active_co:
                if doc_info.get('id') in company_document_ids_to_include_opt:
                    relative_doc_path = doc_info.get("relative_db_path") 
                    if relative_doc_path: 
                        full_doc_path = os.path.join(COMPANY_DOCS_BASE_DIR_PDF_GEN, relative_doc_path)
                        if os.path.exists(full_doc_path):
                            paths_to_append.append(full_doc_path)
                            debug_info['company_docs_found'].append({'id': doc_info.get('id'), 'name': doc_info.get('display_name'), 'path': full_doc_path})
                        else:
                            debug_info['company_docs_missing'].append({'id': doc_info.get('id'), 'name': doc_info.get('display_name'), 'path': full_doc_path})
                    else:
                        debug_info['company_docs_missing'].append({'id': doc_info.get('id'), 'name': doc_info.get('display_name'), 'reason': 'Kein relativer Pfad in DB'})
        except Exception as e_company_docs:
            # Fehler beim Laden der Firmendokumente - wird still behandelt
            pass
    
    debug_info['total_paths_to_append'] = len(paths_to_append)
    
    if not paths_to_append: 
        return main_pdf_bytes
    
    pdf_writer = PdfWriter()
    try:
        main_offer_reader = PdfReader(io.BytesIO(main_pdf_bytes))
        for page in main_offer_reader.pages: 
            pdf_writer.add_page(page)
    except Exception as e_read_main:
        return main_pdf_bytes 

    successfully_appended = 0
    for pdf_path in paths_to_append:
        try:
            datasheet_reader = PdfReader(pdf_path)
            for page in datasheet_reader.pages: 
                pdf_writer.add_page(page)
            successfully_appended += 1
        except Exception as e_append_ds:
            pass  # Fehler beim Anhängen werden still behandelt
    
    final_buffer = io.BytesIO()
    try:
        pdf_writer.write(final_buffer)
        final_pdf_bytes = final_buffer.getvalue()
        return final_pdf_bytes
    except Exception as e_write_final:
        return main_pdf_bytes 
    finally:
        final_buffer.close()

def merge_pdfs(pdf_files: List[Union[str, bytes, io.BytesIO]]) -> bytes:
    """
    Standalone-Funktion zum Zusammenführen mehrerer PDF-Dateien.
    
    Args:
        pdf_files: Liste von PDF-Dateien (Pfade, Bytes oder BytesIO-Objekte)
        
    Returns:
        bytes: Die zusammengeführte PDF als Bytes
    """
    if not _PYPDF_AVAILABLE:
        raise RuntimeError("PyPDF ist nicht verfügbar für das Zusammenführen von PDFs")
        
    if not pdf_files:
        return b""
        
    merger = PdfWriter()
    
    try:
        for pdf_file in pdf_files:
            if isinstance(pdf_file, str):
                # Pfad zu PDF-Datei
                if os.path.exists(pdf_file):
                    with open(pdf_file, 'rb') as f:
                        reader = PdfReader(f)
                        for page in reader.pages:
                            merger.add_page(page)
            elif isinstance(pdf_file, bytes):
                # PDF als Bytes
                reader = PdfReader(io.BytesIO(pdf_file))
                for page in reader.pages:
                    merger.add_page(page)
            elif isinstance(pdf_file, io.BytesIO):
                # PDF als BytesIO
                pdf_file.seek(0)  # Sicherstellung, dass wir am Anfang sind
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    merger.add_page(page)
                    
        # Zusammengeführte PDF in BytesIO schreiben
        output = io.BytesIO()
        merger.write(output)
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        # Fallback: Erste PDF zurückgeben wenn verfügbar
        if pdf_files:
            first_pdf = pdf_files[0]
            if isinstance(first_pdf, str) and os.path.exists(first_pdf):
                with open(first_pdf, 'rb') as f:
                    return f.read()
            elif isinstance(first_pdf, bytes):
                return first_pdf
            elif isinstance(first_pdf, io.BytesIO):
                first_pdf.seek(0)
                return first_pdf.getvalue()
        return b""

def _validate_pdf_data_availability(project_data: Dict[str, Any], analysis_results: Dict[str, Any], texts: Dict[str, str]) -> Dict[str, Any]:
    """
    Validiert die Verfügbarkeit von Daten für die PDF-Erstellung und gibt Warnmeldungen zurück.
    
    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse
        texts: Text-Dictionary
        
    Returns:
        Dict mit Validierungsergebnissen und Warnmeldungen
    """
    validation_result = {
        'is_valid': True,
        'warnings': [],
        'critical_errors': [],
        'missing_data_summary': []
    }
    
    # Kundendaten prüfen (nicht kritisch)
    customer_data = project_data.get('customer_data', {})
    if not customer_data or not customer_data.get('last_name'):
        validation_result['warnings'].append(
            get_text(texts, 'pdf_warning_no_customer_name', 'Kein Kundenname verfügbar - wird als "Kunde" angezeigt')
        )
        validation_result['missing_data_summary'].append('Kundenname')
    
    # PV-Details prüfen
    pv_details = project_data.get('pv_details', {})
    project_details = project_data.get('project_details', {})
    
    # Entweder module in pv_details ODER module_quantity in project_details ist ausreichend
    modules_present = True
    if pv_details and pv_details.get('selected_modules'):
        modules_present = True
    elif project_details and project_details.get('module_quantity', 0) > 0:
        modules_present = True
    
    if not modules_present:
        validation_result['warnings'].append(
            get_text(texts, 'pdf_warning_no_modules', 'Keine PV-Module ausgewählt - Standardwerte werden verwendet')
        )
        validation_result['missing_data_summary'].append('PV-Module')
        # Nur als Warnung, nicht als kritischer Fehler
    
    # Analyseergebnisse prüfen - mit mehr Toleranz
    if not analysis_results or not isinstance(analysis_results, dict) or len(analysis_results) < 2:
        # Wirklich leere oder sehr minimale Analyse ist ein kritischer Fehler
        validation_result['critical_errors'].append(
            get_text(texts, 'pdf_error_no_analysis', 'Keine Analyseergebnisse verfügbar - PDF kann nicht erstellt werden')
        )
        validation_result['is_valid'] = True
        validation_result['missing_data_summary'].append('Analyseergebnisse')
    else:
        # Wenn die Analyse mindestens einige Werte enthält, betrachten wir es als gültig
        # und geben nur Warnungen aus, wenn wichtige KPIs fehlen
        important_kpis = ['anlage_kwp', 'annual_pv_production_kwh', 'final_price']
        missing_kpis = []
        for kpi in important_kpis:
            if not analysis_results.get(kpi):
                missing_kpis.append(kpi)
                
        if missing_kpis:
            missing_kpi_names = ', '.join(missing_kpis)
            validation_result['warnings'].append(
                get_text(texts, 'pdf_warning_missing_kpis', f'Fehlende wichtige Kennzahlen: {missing_kpi_names}')
            )
            validation_result['missing_data_summary'].extend(missing_kpis)
            # Fehlende KPIs sind kein kritischer Fehler mehr
    
    # Firmendaten prüfen (nicht kritisch)
    if not project_data.get('company_information', {}).get('name'):
        validation_result['warnings'].append(
            get_text(texts, 'pdf_warning_no_company', 'Keine Firmendaten verfügbar - Fallback wird verwendet')
        )
        validation_result['missing_data_summary'].append('Firmendaten')
    
    # Debug-Ausgabe
    print(f"PDF Validierung: is_valid={validation_result['is_valid']}, "
          f"Warnungen={len(validation_result['warnings'])}, "
          f"Kritische Fehler={len(validation_result['critical_errors'])}")
    
    return validation_result
def _create_no_data_fallback_pdf(texts: Dict[str, str], customer_data: Dict[str, Any] = None) -> bytes:
    """
    Erstellt eine Fallback-PDF mit Informationstext, wenn keine ausreichenden Daten verfügbar sind.
    
    Args:
        texts: Text-Dictionary
        customer_data: Optionale Kundendaten
        
    Returns:
        PDF als Bytes
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    # Titel
    title = get_text(texts, 'pdf_no_data_title', 'Photovoltaik-Angebot - Datensammlung erforderlich')
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 1*cm))
    
    # Kunde falls verfügbar
    if customer_data and customer_data.get('last_name'):
        customer_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()
        customer_text = get_text(texts, 'pdf_no_data_customer', f'Für: {customer_name}')
        story.append(Paragraph(customer_text, styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
    
    # Haupttext
    main_text = get_text(texts, 'pdf_no_data_main_text', 
        '''Liebe Kundin, lieber Kunde,
        
        für die Erstellung Ihres individuellen Photovoltaik-Angebots benötigen wir noch einige wichtige Informationen:
        
        <b>Erforderliche Daten:</b>
        • Ihre Kontaktdaten (vollständig)
        • Gewünschte PV-Module und Komponenten
        • Stromverbrauchsdaten Ihres Haushalts
        • Technische Angaben zu Ihrem Dach/Standort
        
        <b>Nächste Schritte:</b>
        1. Vervollständigen Sie die Dateneingabe in der Anwendung
        2. Führen Sie die Wirtschaftlichkeitsberechnung durch
        3. Generieren Sie anschließend Ihr personalisiertes PDF-Angebot
        
        Bei Fragen stehen wir Ihnen gerne zur Verfügung!''')
    
    story.append(Paragraph(main_text, styles['Normal']))
    story.append(Spacer(1, 1*cm))
    
    # Kontaktinformationen
    contact_text = get_text(texts, 'pdf_no_data_contact', 
        'Kontakt: Bitte wenden Sie sich an unser Beratungsteam für weitere Unterstützung.')
    story.append(Paragraph(contact_text, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
    
# Änderungshistorie
# 2025-06-03, Gemini Ultra: PageNumCanvas.save() korrigiert, um Duplizierung des PDF-Inhalts zu verhindern.
#                           Schlüssel für `include_all_documents_opt` in `generate_offer_pdf` korrigiert.
#                           Aufruf von `db_list_company_documents_func` mit `doc_type=None` versehen.
#                           Anpassung von _update_styles_with_dynamic_colors für DATA_TABLE_STYLE.
#                           Sicherstellung, dass ausgewählte Diagramme für PDF-Visualisierungen berücksichtigt werden.
#                           Korrekter Key 'relative_db_path' für Firmendokumente verwendet.
# 2025-06-03, Gemini Ultra: `charts_config_for_pdf_generator` erweitert, um alle Diagramme aus `pdf_ui.py` abzudecken.
#                           Logik zur Einbindung optionaler Komponenten (Zubehör) in Sektion "Technische Komponenten" hinzugefügt, gesteuert durch `include_optional_component_details_opt`.
#                           Logik zum Anhängen von Produktdatenblättern erweitert, um auch Zubehör-Datenblätter zu berücksichtigen.
#                           Definition von ReportLab-Styles nur ausgeführt, wenn _REPORTLAB_AVAILABLE True ist.
# 2025-06-03, Gemini Ultra: Validierungs- und Fallback-Funktionen für PDF-Erstellung ohne ausreichende Daten hinzugefügt.
