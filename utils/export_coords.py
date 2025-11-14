"""
Ermittelt aus allen PDF-Vorlagen jeden Textblock
und speichert X/Y (Ursprung links-unten) in YAML.
"""
import collections
import re
from pathlib import Path
from typing import Optional, Union, Dict
import logging

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber nicht installiert. PDF-Koordinaten-Export nicht verfügbar.")

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logging.warning("PyYAML nicht installiert. YAML-Export nicht verfügbar.")

SRC = Path("pdf_templates_static")              # hier liegen 01.pdf … 06.pdf
OUT = Path("coords_raw.yaml")


def export_pdf_coordinates(
    input_dir: Union[str, Path] = SRC,
    output_file: Union[str, Path] = OUT,
    pdf_pattern: str = "[01][02][03][04][05][06].pdf"
) -> bool:
    """
    Extrahiert Koordinaten aller Textblöcke aus PDF-Vorlagen und speichert sie in YAML.
    
    Args:
        input_dir: Verzeichnis mit PDF-Vorlagen
        output_file: Ausgabe-YAML-Datei
        pdf_pattern: Glob-Pattern für PDF-Dateien
    
    Returns:
        True wenn erfolgreich, False bei Fehler
    """
    if not PDFPLUMBER_AVAILABLE:
        logging.error("pdfplumber nicht verfügbar. PDF-Koordinaten-Export nicht möglich.")
        return False
    
    if not YAML_AVAILABLE:
        logging.error("PyYAML nicht verfügbar. YAML-Export nicht möglich.")
        return False
    
    try:
        input_dir = Path(input_dir)
        output_file = Path(output_file)
        
        if not input_dir.exists():
            logging.error(f"Verzeichnis nicht gefunden: {input_dir}")
            return False
        
        all_pages = collections.OrderedDict()
        pdf_files = sorted(input_dir.glob(pdf_pattern))
        
        if not pdf_files:
            logging.warning(f"Keine PDF-Dateien gefunden in {input_dir} mit Pattern '{pdf_pattern}'")
            return False
        
        logging.info(f"Verarbeite {len(pdf_files)} PDF-Dateien...")
        
        for pdf_file in pdf_files:
            logging.info(f"  Analysiere {pdf_file.name}...")
            
            doc = pdfplumber.open(pdf_file)
            page = doc.pages[0]  # jede deiner Vorlagen hat 1 Seite
            h = page.height
            
            # Zeilen bilden
            lines = {}
            for w in page.extract_words():
                key = round(w["top"], 1)  # Zeilenhöhe als Gruppenschlüssel
                lines.setdefault(key, []).append(w)
            
            # sortiert durchgehen
            page_dict = collections.OrderedDict()
            for top in sorted(lines):
                wlist = sorted(lines[top], key=lambda w: w["x0"])
                text = " ".join(w["text"] for w in wlist)
                slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:60]
                x = min(w["x0"] for w in wlist)
                y = h - min(w["top"] for w in wlist)
                page_dict[slug] = [round(x, 1), round(y, 1)]
            
            all_pages[pdf_file.stem] = page_dict
            doc.close()
            
            logging.debug(f"    Extrahiert: {len(page_dict)} Textblöcke")
        
        # In YAML speichern
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with output_file.open("w", encoding="utf-8") as fp:
            yaml.dump(all_pages, fp, allow_unicode=True)
        
        logging.info(f"[OK] Koordinaten gespeichert in: {output_file}")
        return True
        
    except Exception as e:
        logging.error(f"Fehler beim Exportieren der PDF-Koordinaten: {e}")
        return False


def get_text_coordinates(
    pdf_file: Union[str, Path],
    page_num: int = 0
) -> Optional[Dict]:
    """
    Extrahiert Koordinaten aller Textblöcke aus einer einzelnen PDF-Seite.
    
    Args:
        pdf_file: Pfad zur PDF-Datei
        page_num: Seitennummer (0-basiert)
    
    Returns:
        Dictionary mit Slug -> [x, y] Koordinaten, oder None bei Fehler
    """
    if not PDFPLUMBER_AVAILABLE:
        logging.error("pdfplumber nicht verfügbar")
        return None
    
    try:
        pdf_file = Path(pdf_file)
        
        if not pdf_file.exists():
            logging.error(f"PDF nicht gefunden: {pdf_file}")
            return None
        
        doc = pdfplumber.open(pdf_file)
        
        if page_num >= len(doc.pages):
            logging.error(f"Seite {page_num} existiert nicht in {pdf_file.name}")
            doc.close()
            return None
        
        page = doc.pages[page_num]
        h = page.height
        
        # Zeilen bilden
        lines = {}
        for w in page.extract_words():
            key = round(w["top"], 1)
            lines.setdefault(key, []).append(w)
        
        # Koordinaten extrahieren
        coords = {}
        for top in sorted(lines):
            wlist = sorted(lines[top], key=lambda w: w["x0"])
            text = " ".join(w["text"] for w in wlist)
            slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:60]
            x = min(w["x0"] for w in wlist)
            y = h - min(w["top"] for w in wlist)
            coords[slug] = [round(x, 1), round(y, 1)]
        
        doc.close()
        return coords
        
    except Exception as e:
        logging.error(f"Fehler beim Extrahieren der Koordinaten: {e}")
        return None


# CLI-Modus (wenn direkt ausgeführt)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    print("📍 PDF-Koordinaten-Exporter")
    print("=" * 50)
    
    success = export_pdf_coordinates()
    
    print("=" * 50)
    if success:
        print(f"[OK] Erfolgreich! Koordinaten in {OUT}")
    else:
        print("[ERROR] Fehler beim Export!")

