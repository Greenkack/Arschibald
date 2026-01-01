"""multi_pdf_positioning/coordinate_extractor.py - PDF-Koordinaten-Extraktor"""
import fitz  # PyMuPDF
import yaml
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st

class CoordinateExtractor:
    """Extrahiert Text-Koordinaten aus PDF-Vorlagen"""
    
    def __init__(self):
        self.pdf_path = None
        self.doc = None
        self.page_count = 0
    
    def load_pdf(self, pdf_path: str) -> bool:
        """Lade PDF-Datei"""
        try:
            self.pdf_path = Path(pdf_path)
            self.doc = fitz.open(pdf_path)
            self.page_count = len(self.doc)
            return True
        except Exception as e:
            st.error(f"Fehler beim Laden: {e}")
            return False
    
    def extract_page_text_blocks(self, page_num: int) -> List[Dict[str, Any]]:
        """Extrahiere Textblöcke von Seite"""
        if not self.doc or page_num >= self.page_count:
            return []
        
        page = self.doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        extracted = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        extracted.append({
                            "text": span["text"],
                            "bbox": span["bbox"],  # (x0, y0, x1, y1)
                            "font": span["font"],
                            "size": span["size"],
                            "color": span["color"]
                        })
        
        return extracted
    
    def convert_to_yaml_format(self, blocks: List[Dict[str, Any]], 
                              page_height: float) -> List[Dict[str, Any]]:
        """Konvertiere zu YAML-Format (ReportLab-Koordinaten)"""
        yaml_blocks = []
        
        for block in blocks:
            # PyMuPDF: (x0, y0, x1, y1) mit Origin oben links
            # ReportLab: (x0, y0, x1, y1) mit Origin unten links
            x0, y0, x1, y1 = block["bbox"]
            
            # Y-Koordinaten umrechnen
            rl_y0 = page_height - y1  # Bottom
            rl_y1 = page_height - y0  # Top
            
            yaml_blocks.append({
                "Text": block["text"],
                "Position": [x0, rl_y0, x1, rl_y1],
                "Schriftart": block["font"],
                "Schriftgröße": block["size"],
                "Farbe": block["color"]
            })
        
        return yaml_blocks
    
    def save_to_yaml(self, page_num: int, output_path: str, 
                     firm_index: int = None):
        """Speichere Koordinaten als YAML"""
        if not self.doc:
            return False
        
        page = self.doc[page_num]
        page_height = page.rect.height
        
        blocks = self.extract_page_text_blocks(page_num)
        yaml_blocks = self.convert_to_yaml_format(blocks, page_height)
        
        # Dateiname generieren
        if firm_index is not None:
            filename = f"seite{page_num+1}_f{firm_index}.yml"
        else:
            filename = f"seite{page_num+1}.yml"
        
        output_file = Path(output_path) / filename
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_blocks, f, allow_unicode=True, default_flow_style=False)
        
        return True
    
    def extract_all_pages(self, output_dir: str, firm_index: int = None):
        """Extrahiere alle Seiten"""
        if not self.doc:
            return False
        
        success_count = 0
        for page_num in range(self.page_count):
            if self.save_to_yaml(page_num, output_dir, firm_index):
                success_count += 1
        
        return success_count == self.page_count
    
    def close(self):
        """Schließe PDF"""
        if self.doc:
            self.doc.close()
            self.doc = None


def render_coordinate_extractor_ui():
    """Streamlit UI für Koordinaten-Extraktor"""
    st.title("📍 PDF-Koordinaten-Extraktor")
    
    st.info("""
    **Verwendung:**
    1. PDF-Vorlage hochladen
    2. Firmen-Index auswählen (optional)
    3. Koordinaten extrahieren
    4. YAML-Dateien werden in `coords_multi/` gespeichert
    """)
    
    # File Upload
    uploaded_file = st.file_uploader("PDF-Vorlage hochladen", type=['pdf'])
    
    if uploaded_file:
        # Temporäre Datei speichern
        temp_path = Path("temp_upload.pdf")
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.read())
        
        extractor = CoordinateExtractor()
        if extractor.load_pdf(str(temp_path)):
            st.success(f"PDF geladen: {extractor.page_count} Seiten")
            
            col1, col2 = st.columns(2)
            
            with col1:
                firm_index = st.number_input("Firmen-Index (optional)", 
                                            min_value=1, max_value=7, 
                                            value=1, step=1)
                use_firm_index = st.checkbox("Firmen-Index verwenden")
            
            with col2:
                output_dir = st.text_input("Ausgabeverzeichnis", 
                                          value="coords_multi")
            
            if st.button("Koordinaten extrahieren", type="primary"):
                firm_idx = firm_index if use_firm_index else None
                
                with st.spinner("Extrahiere Koordinaten..."):
                    success = extractor.extract_all_pages(output_dir, firm_idx)
                
                if success:
                    st.success(f"✅ {extractor.page_count} YAML-Dateien erstellt in `{output_dir}/`")
                else:
                    st.error("Fehler bei Extraktion")
            
            # Vorschau einzelner Seite
            st.subheader("Vorschau")
            page_preview = st.number_input("Seite", min_value=1, 
                                          max_value=extractor.page_count, 
                                          value=1) - 1
            
            if st.button("Seite anzeigen"):
                blocks = extractor.extract_page_text_blocks(page_preview)
                st.write(f"**Gefundene Textblöcke:** {len(blocks)}")
                
                with st.expander("Details anzeigen"):
                    for i, block in enumerate(blocks[:20]):  # Erste 20
                        st.json({
                            f"Block {i+1}": {
                                "Text": block["text"],
                                "Position": block["bbox"],
                                "Font": block["font"],
                                "Größe": block["size"]
                            }
                        })
            
            extractor.close()
        
        # Temp-Datei löschen
        if temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    render_coordinate_extractor_ui()
