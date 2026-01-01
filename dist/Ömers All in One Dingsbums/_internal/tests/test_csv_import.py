"""
Test CSV Import Funktionalität

Testet die CSV-Import-Funktionen für die Excel-Integration.
"""

import pytest
from excel.excel_import import (
    detect_encoding,
    detect_delimiter,
    parse_csv_content,
    import_csv_to_matrix,
    validate_csv_file,
    get_csv_preview,
    ImportError
)


def test_detect_delimiter():
    """Test Delimiter-Erkennung"""
    # Semikolon
    csv_text = "A;B;C\n1;2;3\n4;5;6"
    assert detect_delimiter(csv_text) == ';'
    
    # Komma
    csv_text = "A,B,C\n1,2,3\n4,5,6"
    assert detect_delimiter(csv_text) == ','
    
    # Tab
    csv_text = "A\tB\tC\n1\t2\t3\n4\t5\t6"
    assert detect_delimiter(csv_text) == '\t'


def test_parse_csv_content():
    """Test CSV-Parsing"""
    csv_text = "Name;Wert;Preis\nProdukt A;10;100\nProdukt B;20;200"
    
    header, rows = parse_csv_content(csv_text, delimiter=';')
    
    assert header == ['Name', 'Wert', 'Preis']
    assert len(rows) == 2
    assert rows[0] == ['Produkt A', '10', '100']
    assert rows[1] == ['Produkt B', '20', '200']


def test_parse_csv_without_header():
    """Test CSV-Parsing ohne Header"""
    csv_text = "10;100\n20;200"
    
    header, rows = parse_csv_content(csv_text, delimiter=';', has_header=False)
    
    # Automatisch generierte Header (A, B, C, ...)
    assert header == ['A', 'B']
    assert len(rows) == 2
    assert rows[0] == ['10', '100']


def test_import_csv_to_matrix():
    """Test CSV-Import zu Matrix"""
    csv_text = "Spalte1;Spalte2;Spalte3\n10;20;30\n40;50;60"
    csv_bytes = csv_text.encode('utf-8')
    
    manager = import_csv_to_matrix(
        csv_bytes,
        "Test Matrix",
        delimiter=';',
        has_header=True,
        encoding='utf-8'
    )
    
    assert manager is not None
    assert manager.matrix.name == "Test Matrix"
    
    # Prüfe Zellwerte
    assert manager.get_cell_value(0, 0) == 10
    assert manager.get_cell_value(0, 1) == 20
    assert manager.get_cell_value(0, 2) == 30
    assert manager.get_cell_value(1, 0) == 40
    assert manager.get_cell_value(1, 1) == 50
    assert manager.get_cell_value(1, 2) == 60


def test_import_csv_with_formulas():
    """Test CSV-Import mit Formeln"""
    csv_text = "A;B;C\n10;20;=A1+B1\n30;40;=A2+B2"
    csv_bytes = csv_text.encode('utf-8')
    
    manager = import_csv_to_matrix(
        csv_bytes,
        "Test Matrix mit Formeln",
        delimiter=';',
        has_header=True,
        encoding='utf-8'
    )
    
    assert manager is not None
    
    # Prüfe dass Formeln erkannt wurden
    cell_c1 = manager.get_cell(0, 2)
    assert cell_c1.is_formula()
    assert cell_c1.formula == "=A1+B1"
    
    # Prüfe berechnete Werte
    assert cell_c1.value == 30  # 10 + 20


def test_import_csv_with_german_numbers():
    """Test CSV-Import mit deutschen Zahlenformaten (Komma als Dezimaltrennzeichen)"""
    csv_text = "Preis\n10,50\n20,75\n30,25"
    csv_bytes = csv_text.encode('utf-8')
    
    manager = import_csv_to_matrix(
        csv_bytes,
        "Test Matrix deutsche Zahlen",
        delimiter=';',
        has_header=True,
        encoding='utf-8'
    )
    
    assert manager is not None
    
    # Prüfe dass Komma-Zahlen korrekt konvertiert wurden
    assert manager.get_cell_value(0, 0) == 10.5
    assert manager.get_cell_value(1, 0) == 20.75
    assert manager.get_cell_value(2, 0) == 30.25


def test_validate_csv_file():
    """Test CSV-Validierung"""
    csv_text = "A;B;C\n1;2;3\n4;5;6"
    csv_bytes = csv_text.encode('utf-8')
    
    validation = validate_csv_file(csv_bytes)
    
    assert validation['valid'] is True
    # ASCII ist ein Subset von UTF-8, daher ist beides akzeptabel
    assert validation['encoding'].lower() in ['utf-8', 'ascii']
    assert validation['delimiter'] == ';'
    assert validation['num_rows'] == 2
    assert validation['num_cols'] == 3
    assert validation['has_formulas'] is False


def test_validate_csv_with_formulas():
    """Test CSV-Validierung mit Formeln"""
    csv_text = "A;B;C\n1;2;=A1+B1"
    csv_bytes = csv_text.encode('utf-8')
    
    validation = validate_csv_file(csv_bytes)
    
    assert validation['valid'] is True
    assert validation['has_formulas'] is True


def test_get_csv_preview():
    """Test CSV-Vorschau"""
    csv_text = "A;B;C\n" + "\n".join([f"{i};{i*2};{i*3}" for i in range(1, 21)])
    csv_bytes = csv_text.encode('utf-8')
    
    preview = get_csv_preview(csv_bytes, max_rows=5)
    
    assert preview['header'] == ['A', 'B', 'C']
    assert len(preview['rows']) == 5  # Nur 5 Zeilen in Vorschau
    assert preview['total_rows'] == 20  # Aber 20 Zeilen insgesamt
    # ASCII ist ein Subset von UTF-8, daher ist beides akzeptabel
    assert preview['encoding'].lower() in ['utf-8', 'ascii']
    assert preview['delimiter'] == ';'


def test_import_empty_csv():
    """Test Import einer leeren CSV-Datei"""
    csv_text = ""
    csv_bytes = csv_text.encode('utf-8')
    
    with pytest.raises(ImportError):
        import_csv_to_matrix(
            csv_bytes,
            "Leere Matrix",
            delimiter=';',
            has_header=True,
            encoding='utf-8'
        )


def test_import_csv_with_empty_cells():
    """Test CSV-Import mit leeren Zellen"""
    csv_text = "A;B;C\n10;;30\n;50;\n70;80;90"
    csv_bytes = csv_text.encode('utf-8')
    
    manager = import_csv_to_matrix(
        csv_bytes,
        "Test Matrix mit leeren Zellen",
        delimiter=';',
        has_header=True,
        encoding='utf-8'
    )
    
    assert manager is not None
    
    # Prüfe dass leere Zellen übersprungen wurden
    assert manager.get_cell_value(0, 0) == 10
    assert manager.get_cell_value(0, 1) is None or manager.get_cell_value(0, 1) == 0
    assert manager.get_cell_value(0, 2) == 30


def test_detect_encoding_utf8():
    """Test Encoding-Erkennung für UTF-8"""
    text = "Ä Ö Ü ß"
    bytes_utf8 = text.encode('utf-8')
    
    encoding = detect_encoding(bytes_utf8)
    
    # Sollte UTF-8 oder kompatibel erkennen
    assert encoding.lower() in ['utf-8', 'ascii']


def test_detect_encoding_latin1():
    """Test Encoding-Erkennung für Latin-1"""
    text = "Ä Ö Ü ß"
    bytes_latin1 = text.encode('latin-1')
    
    encoding = detect_encoding(bytes_latin1)
    
    # Sollte Latin-1 oder kompatibel erkennen
    assert encoding is not None


if __name__ == "__main__":
    # Führe Tests aus
    pytest.main([__file__, "-v"])
