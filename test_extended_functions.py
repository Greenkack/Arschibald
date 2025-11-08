"""
Test: Erweiterte Excel-Funktionen

Testet alle 30+ neu hinzugefügten Excel-Funktionen
"""

import pytest
from excel.excel_manager import ExcelManager
from excel.excel_models import ExcelMatrix


class TestStatisticalFunctions:
    """Tests für statistische Funktionen"""
    
    def test_median(self):
        """Test MEDIAN Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=10, columns=2))
        for i, val in enumerate([10, 20, 30, 40, 50]):
            manager.set_cell_value(i, 0, val, str(val))
        
        manager.set_cell_value(5, 0, None, "=MEDIAN(A1:A5)")
        assert manager.get_cell_value(5, 0) == 30.0
    
    def test_mode(self):
        """Test MODE Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=10, columns=2))
        for i, val in enumerate([10, 20, 20, 30, 40]):
            manager.set_cell_value(i, 0, val, str(val))
        
        manager.set_cell_value(5, 0, None, "=MODE(A1:A5)")
        assert manager.get_cell_value(5, 0) == 20
    
    def test_stdev(self):
        """Test STDEV Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=10, columns=2))
        for i, val in enumerate([10, 20, 30, 40, 50]):
            manager.set_cell_value(i, 0, val, str(val))
        
        manager.set_cell_value(5, 0, None, "=STDEV(A1:A5)")
        result = manager.get_cell_value(5, 0)
        assert 15 < result < 16  # Ungefähr 15.81
    
    def test_percentile(self):
        """Test PERCENTILE Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=10, columns=2))
        for i, val in enumerate([10, 20, 30, 40, 50]):
            manager.set_cell_value(i, 0, val, str(val))
        
        manager.set_cell_value(5, 0, None, "=PERCENTILE(A1:A5, 0.5)")
        assert manager.get_cell_value(5, 0) == 30.0
    
    def test_rank(self):
        """Test RANK Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=10, columns=2))
        for i, val in enumerate([10, 20, 30, 40, 50]):
            manager.set_cell_value(i, 0, val, str(val))
        
        manager.set_cell_value(5, 0, None, "=RANK(50, A1:A5, 0)")
        assert manager.get_cell_value(5, 0) == 1


class TestIFFunctions:
    """Tests für erweiterte IF-Funktionen"""
    
    def test_ifs(self):
        """Test IFS Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, 95, "95")
        manager.set_cell_value(0, 1, None, "=IFS(A1>=90, \"A\", A1>=80, \"B\", A1>=70, \"C\")")
        assert manager.get_cell_value(0, 1) == "A"
        
        manager.set_cell_value(1, 0, 75, "75")
        manager.set_cell_value(1, 1, None, "=IFS(A2>=90, \"A\", A2>=80, \"B\", A2>=70, \"C\")")
        assert manager.get_cell_value(1, 1) == "C"
    
    def test_switch(self):
        """Test SWITCH Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, 1, "1")
        manager.set_cell_value(0, 1, None, "=SWITCH(A1, 1, \"Eins\", 2, \"Zwei\", 3, \"Drei\")")
        assert manager.get_cell_value(0, 1) == "Eins"
        
        manager.set_cell_value(1, 0, 3, "3")
        manager.set_cell_value(1, 1, None, "=SWITCH(A2, 1, \"Eins\", 2, \"Zwei\", 3, \"Drei\")")
        assert manager.get_cell_value(1, 1) == "Drei"
    
    def test_choose(self):
        """Test CHOOSE Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, 2, "2")
        manager.set_cell_value(0, 1, None, "=CHOOSE(A1, \"Rot\", \"Grün\", \"Blau\")")
        assert manager.get_cell_value(0, 1) == "Grün"


class TestTextFunctions:
    """Tests für Textfunktionen"""
    
    def test_left(self):
        """Test LEFT Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, "Hallo", "Hallo")
        manager.set_cell_value(0, 1, None, "=LEFT(A1, 3)")
        assert manager.get_cell_value(0, 1) == "Hal"
    
    def test_right(self):
        """Test RIGHT Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, "Hallo", "Hallo")
        manager.set_cell_value(0, 1, None, "=RIGHT(A1, 3)")
        assert manager.get_cell_value(0, 1) == "llo"
    
    def test_mid(self):
        """Test MID Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, "Hallo", "Hallo")
        manager.set_cell_value(0, 1, None, "=MID(A1, 2, 3)")
        assert manager.get_cell_value(0, 1) == "all"
    
    def test_len(self):
        """Test LEN Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, "Hallo", "Hallo")
        manager.set_cell_value(0, 1, None, "=LEN(A1)")
        assert manager.get_cell_value(0, 1) == 5
    
    def test_lower_upper(self):
        """Test LOWER und UPPER Funktionen"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=3))
        manager.set_cell_value(0, 0, "Hallo", "Hallo")
        manager.set_cell_value(0, 1, None, "=LOWER(A1)")
        manager.set_cell_value(0, 2, None, "=UPPER(A1)")
        assert manager.get_cell_value(0, 1) == "hallo"
        assert manager.get_cell_value(0, 2) == "HALLO"
    
    def test_trim(self):
        """Test TRIM Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, "  Hallo  Welt  ", "  Hallo  Welt  ")
        manager.set_cell_value(0, 1, None, "=TRIM(A1)")
        assert manager.get_cell_value(0, 1) == "Hallo Welt"


class TestMathFunctions:
    """Tests für mathematische Funktionen"""
    
    def test_abs(self):
        """Test ABS Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, None, "=ABS(-5)")
        assert manager.get_cell_value(0, 0) == 5.0
    
    def test_power(self):
        """Test POWER Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, None, "=POWER(2, 3)")
        assert manager.get_cell_value(0, 0) == 8.0
    
    def test_sqrt(self):
        """Test SQRT Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, None, "=SQRT(16)")
        assert manager.get_cell_value(0, 0) == 4.0
    
    def test_mod(self):
        """Test MOD Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=2))
        manager.set_cell_value(0, 0, None, "=MOD(10, 3)")
        assert manager.get_cell_value(0, 0) == 1.0
    
    def test_ceiling_floor(self):
        """Test CEILING und FLOOR Funktionen"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=3))
        manager.set_cell_value(0, 0, None, "=CEILING(4.3, 1)")
        manager.set_cell_value(0, 1, None, "=FLOOR(4.7, 1)")
        assert manager.get_cell_value(0, 0) == 5.0
        assert manager.get_cell_value(0, 1) == 4.0
    
    def test_sign(self):
        """Test SIGN Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=3))
        manager.set_cell_value(0, 0, None, "=SIGN(-5)")
        manager.set_cell_value(0, 1, None, "=SIGN(5)")
        manager.set_cell_value(0, 2, None, "=SIGN(0)")
        assert manager.get_cell_value(0, 0) == -1
        assert manager.get_cell_value(0, 1) == 1
        assert manager.get_cell_value(0, 2) == 0


class TestCheckFunctions:
    """Tests für Prüffunktionen"""
    
    def test_isnumber(self):
        """Test ISNUMBER Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=3))
        manager.set_cell_value(0, 0, 123, "123")
        manager.set_cell_value(0, 1, "Text", "Text")
        manager.set_cell_value(1, 0, None, "=ISNUMBER(A1)")
        manager.set_cell_value(1, 1, None, "=ISNUMBER(B1)")
        assert manager.get_cell_value(1, 0) == True
        assert manager.get_cell_value(1, 1) == False
    
    def test_istext(self):
        """Test ISTEXT Funktion"""
        manager = ExcelManager(ExcelMatrix(rows=5, columns=3))
        manager.set_cell_value(0, 0, 123, "123")
        manager.set_cell_value(0, 1, "Text", "Text")
        manager.set_cell_value(1, 0, None, "=ISTEXT(A1)")
        manager.set_cell_value(1, 1, None, "=ISTEXT(B1)")
        assert manager.get_cell_value(1, 0) == False
        assert manager.get_cell_value(1, 1) == True


class TestComplexFormulas:
    """Tests für komplexe verschachtelte Formeln"""
    
    def test_nested_ifs_with_math(self):
        """Test verschachtelte IFS mit Mathematik"""
        manager = ExcelManager(ExcelMatrix(rows=10, columns=5))
        
        # Menge
        manager.set_cell_value(0, 0, 25, "25")
        # Einzelpreis
        manager.set_cell_value(0, 1, 250, "250")
        # Rabatt basierend auf Menge
        manager.set_cell_value(0, 2, None, "=IFS(A1>=50, 15, A1>=30, 10, A1>=20, 5, A1>=10, 2, TRUE, 0)")
        # Gesamt mit Rabatt
        manager.set_cell_value(0, 3, None, "=A1*B1*(1-C1/100)")
        
        assert manager.get_cell_value(0, 2) == 5  # 5% Rabatt
        assert manager.get_cell_value(0, 3) == 5937.5  # 25 * 250 * 0.95
    
    def test_switch_with_calculations(self):
        """Test SWITCH mit Berechnungen"""
        manager = ExcelManager(ExcelMatrix(rows=10, columns=5))
        
        manager.set_cell_value(0, 0, 50, "50")
        manager.set_cell_value(0, 1, None, "=SWITCH(TRUE, A1>=50, \"Premium\", A1>=20, \"Standard\", \"Basic\")")
        
        assert manager.get_cell_value(0, 1) == "Premium"


def run_tests():
    """Führt alle Tests aus"""
    print("=" * 80)
    print("ERWEITERTE FUNKTIONEN - TESTS")
    print("=" * 80)
    
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
