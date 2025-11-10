# utils/remove_text.py
# -----------------------------------------------------------
# erzeugt textfreie Kopien (nt_01.pdf … nt_06.pdf)
# -----------------------------------------------------------

from pathlib import Path
from typing import Optional, Union
import logging

try:
    import fitz  # PyMuPDF  ->  pip install pymupdf
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("PyMuPDF nicht installiert. PDF-Text-Entfernung nicht verfügbar.")

BASE = Path(__file__).resolve().parent.parent        # Projekt-Root
SRC  = BASE / "pdf_templates_static"                 # Ordner mit 01.pdf …
DST  = SRC / "notext"                                # Zielordner


def remove_text_from_pdf(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None
) -> bool:
    """
    Entfernt allen Text aus einem PDF und erstellt eine textfreie Kopie.
    
    Args:
        input_path: Pfad zur Original-PDF-Datei
        output_path: Pfad für die textfreie PDF-Datei (optional)
                    Falls None, wird "nt_<original>.pdf" verwendet
    
    Returns:
        True wenn erfolgreich, False bei Fehler
    """
    if not PYMUPDF_AVAILABLE:
        logging.error("PyMuPDF nicht verfügbar. PDF-Text-Entfernung nicht möglich.")
        return False
    
    try:
        input_path = Path(input_path)
        
        if not input_path.exists():
            logging.error(f"PDF-Datei nicht gefunden: {input_path}")
            return False
        
        # Standard-Output-Pfad generieren wenn nicht angegeben
        if output_path is None:
            output_dir = input_path.parent / "notext"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"nt_{input_path.name}"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"Bearbeite PDF: {input_path.name}")
        
        # PDF öffnen und Text entfernen
        doc = fitz.open(input_path)
        
        for page_num, page in enumerate(doc, start=1):
            text_blocks = page.get_text("dict")["blocks"]
            
            for block in text_blocks:
                if block["type"] == 0:  # Text-Block
                    r = fitz.Rect(block["bbox"])
                    page.add_redact_annot(r, fill=(1, 1, 1))  # Weiß übermalen
            
            page.apply_redactions()  # Text vollständig ausgeblendet
            logging.debug(f"  Seite {page_num}: Text entfernt")
        
        # Speichern
        doc.save(output_path)
        doc.close()
        
        logging.info(f"✓ Textfreie PDF gespeichert: {output_path.name}")
        return True
        
    except Exception as e:
        logging.error(f"Fehler beim Entfernen von Text aus PDF: {e}")
        return False


def remove_text_from_all_templates(
    source_dir: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    pattern: str = "[0-9][0-9].pdf"
) -> int:
    """
    Entfernt Text aus allen PDF-Templates in einem Verzeichnis.
    
    Args:
        source_dir: Quell-Verzeichnis (default: pdf_templates_static)
        output_dir: Ziel-Verzeichnis (default: pdf_templates_static/notext)
        pattern: Datei-Pattern für Glob (default: "[0-9][0-9].pdf")
    
    Returns:
        Anzahl der erfolgreich verarbeiteten PDFs
    """
    if source_dir is None:
        source_dir = SRC
    else:
        source_dir = Path(source_dir)
    
    if output_dir is None:
        output_dir = DST
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    
    for pdf_file in sorted(source_dir.glob(pattern)):
        output_path = output_dir / f"nt_{pdf_file.name}"
        
        if remove_text_from_pdf(pdf_file, output_path):
            success_count += 1
    
    logging.info(f"✓ {success_count} PDF-Templates verarbeitet")
    return success_count


# CLI-Modus (wenn direkt ausgeführt)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    print("🔧 PDF-Text-Entferner")
    print("=" * 50)
    
    count = remove_text_from_all_templates()
    
    print("=" * 50)
    print(f"✓ Fertig! {count} PDFs verarbeitet.")

