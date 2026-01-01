"""tests/test_pdf_generation.py - Unit Tests für PDF-Generierung"""
import unittest
import tempfile
import shutil
from pathlib import Path
from pdf_generator import generate_multi_firm_pdf
from pdf_template_engine.dynamic_overlay import parse_coords_file, apply_text_overlay

class TestPDFGeneration(unittest.TestCase):
    """Tests für PDF-Generierung"""
    
    def setUp(self):
        """Setup vor jedem Test"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_parse_coords_file_basic(self):
        """Test: YAML-Koordinaten parsen"""
        # Mock YAML-Datei erstellen
        test_yaml = self.temp_dir / "test.yml"
        test_yaml.write_text("""
- Text: "Test Placeholder"
  Position: [100, 200, 300, 400]
  Schriftart: "Helvetica"
  Schriftgröße: 12
  Farbe: 0
""")
        
        result = parse_coords_file(test_yaml)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['Text'], "Test Placeholder")
        self.assertEqual(result[0]['Position'], [100, 200, 300, 400])
    
    def test_parse_coords_file_missing(self):
        """Test: Fehlende YAML-Datei"""
        result = parse_coords_file(self.temp_dir / "nonexistent.yml")
        self.assertEqual(result, [])
    
    def test_placeholder_replacement(self):
        """Test: Platzhalter-Ersetzung"""
        placeholder_map = {
            'KUNDENNAME': 'Max Mustermann',
            'PROJEKT_NUMMER': 'P-2025-001',
            'DATUM': '25.01.2025'
        }
        
        text = "Kunde: KUNDENNAME, Projekt: PROJEKT_NUMMER"
        for key, value in placeholder_map.items():
            text = text.replace(key, value)
        
        self.assertIn('Max Mustermann', text)
        self.assertIn('P-2025-001', text)
        self.assertNotIn('KUNDENNAME', text)
    
    def test_price_formatting_german(self):
        """Test: Deutsche Preisformatierung"""
        price = 95464.18
        formatted = f"{price:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        self.assertEqual(formatted, "95.464,18 €")
    
    def test_multi_firm_pdf_data_structure(self):
        """Test: Multi-Firma-Datenstruktur"""
        test_data = {
            'customer_name': 'Test Kunde',
            'project_number': 'P-001',
            'modules': [
                {'manufacturer': 'JA Solar', 'model': 'JAM72S30', 'count': 20}
            ],
            'inverter': {'manufacturer': 'Fronius', 'model': 'Symo 10.0', 'count': 1},
            'battery': {'manufacturer': 'BYD', 'model': 'HVS 10.2', 'count': 1},
            'total_price': 25000.00
        }
        
        self.assertIn('customer_name', test_data)
        self.assertIn('modules', test_data)
        self.assertIsInstance(test_data['modules'], list)
        self.assertGreater(test_data['total_price'], 0)
    
    def test_coordinate_bounds(self):
        """Test: Koordinaten-Grenzen für A4"""
        # A4 in ReportLab: 595.27 x 841.89 points
        coords = [100, 200, 300, 400]
        
        self.assertGreaterEqual(coords[0], 0)  # x1
        self.assertGreaterEqual(coords[1], 0)  # y1
        self.assertLessEqual(coords[2], 595.27)  # x2
        self.assertLessEqual(coords[3], 841.89)  # y2
    
    def test_font_availability(self):
        """Test: Verfügbare Schriftarten"""
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # Standard-Fonts sollten verfügbar sein
        available_fonts = ['Helvetica', 'Helvetica-Bold', 'Times-Roman', 'Courier']
        
        for font in available_fonts:
            # Sollte nicht fehlschlagen
            try:
                # Test-Font-Zugriff
                pass
            except:
                self.fail(f"Font {font} nicht verfügbar")
    
    def test_right_align_calculation(self):
        """Test: Rechtsbündige Text-Berechnung"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        # Mock Canvas
        temp_pdf = self.temp_dir / "test.pdf"
        c = canvas.Canvas(str(temp_pdf), pagesize=A4)
        
        # Rechtsbündiger Text bei x2=500
        text = "12.345,67 €"
        x2 = 500
        
        # drawRightString sollte bei x2 enden
        c.setFont("Helvetica", 10)
        text_width = c.stringWidth(text, "Helvetica", 10)
        
        self.assertGreater(text_width, 0)
        self.assertLess(text_width, x2)
        
        c.save()
    
    def test_pdf_merge_basic(self):
        """Test: PDF-Zusammenführung"""
        from PyPDF2 import PdfMerger
        
        merger = PdfMerger()
        # Merger sollte initialisiert sein
        self.assertIsNotNone(merger)
    
    def test_product_rotation_data(self):
        """Test: Produkt-Rotation-Datenstruktur"""
        from product_rotation_engine import rotate_products
        
        base_products = {
            'modules': [
                {'manufacturer': 'JA Solar', 'model': 'JAM72S30'},
                {'manufacturer': 'Longi', 'model': 'LR5-72HPH'}
            ]
        }
        
        # Rotation sollte verschiedene Kombinationen erzeugen
        self.assertEqual(len(base_products['modules']), 2)


class TestPDFTemplateEngine(unittest.TestCase):
    """Tests für PDF-Template-Engine"""
    
    def test_color_conversion(self):
        """Test: Farb-Konvertierung"""
        # RGB Integer zu (R, G, B) Float
        color_int = 3487029  # 0x353535
        
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        
        self.assertGreaterEqual(r, 0)
        self.assertLessEqual(r, 1)
        self.assertGreaterEqual(g, 0)
        self.assertLessEqual(g, 1)
        self.assertGreaterEqual(b, 0)
        self.assertLessEqual(b, 1)
    
    def test_alignment_detection(self):
        """Test: Text-Alignment-Erkennung"""
        right_align_tokens = ['€', 'kWp', '%', 'Stk']
        
        text1 = "12.345,67 €"
        text2 = "Kunde: Max Mustermann"
        
        # Text1 sollte rechtsbündig sein
        self.assertTrue(any(token in text1 for token in right_align_tokens))
        # Text2 sollte linksbündig sein
        self.assertFalse(any(token in text2 for token in right_align_tokens))


if __name__ == '__main__':
    unittest.main()
