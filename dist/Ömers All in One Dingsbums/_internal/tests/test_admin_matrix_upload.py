"""
Tests für Admin Panel Matrix Upload Validierung

Task 5: Verbessere Admin Panel Matrix-Upload Validierung
Requirements: 2.1, 2.2, 2.4
"""

import io
import pandas as pd
import pytest
from admin_price_matrix_upload import (
    validate_uploaded_file,
    _parse_csv_file,
    _parse_excel_file,
    _validate_matrix_structure,
    _validate_index_numeric,
    _validate_column_headers,
    _find_no_storage_column,
    _validate_price_cells
)


def test_validate_csv_file_valid():
    """Test: Gültige CSV-Datei wird akzeptiert"""
    csv_content = """Anzahl Module;10kWh;15kWh;Ohne Speicher
10;15000.00;17500.00;12000.00
15;18000.00;20500.00;15000.00
20;21000.00;23500.00;18000.00"""
    
    file_content = csv_content.encode('utf-8')
    result = validate_uploaded_file(file_content, 'csv')
    
    assert result['valid'] == True
    assert len(result['errors']) == 0
    assert result['preview_df'] is not None
    assert 'no_storage_column' in result['info']


def test_validate_csv_file_missing_no_storage_column():
    """Test: CSV ohne 'Ohne Speicher' Spalte wird abgelehnt"""
    csv_content = """Anzahl Module;10kWh;15kWh
10;15000.00;17500.00
15;18000.00;20500.00"""
    
    file_content = csv_content.encode('utf-8')
    result = validate_uploaded_file(file_content, 'csv')
    
    assert result['valid'] == False
    assert any('Ohne Speicher' in error for error in result['errors'])


def test_validate_csv_file_non_numeric_index():
    """Test: CSV mit nicht-numerischem Index wird abgelehnt"""
    csv_content = """Anzahl Module;10kWh;Ohne Speicher
ABC;15000.00;12000.00
DEF;18000.00;15000.00"""
    
    file_content = csv_content.encode('utf-8')
    result = validate_uploaded_file(file_content, 'csv')
    
    assert result['valid'] == False
    assert any('numerisch' in error.lower() for error in result['errors'])


def test_validate_csv_file_non_numeric_prices():
    """Test: CSV mit nicht-numerischen Preisen wird abgelehnt"""
    csv_content = """Anzahl Module;10kWh;Ohne Speicher
10;ABC;12000.00
15;18000.00;XYZ"""
    
    file_content = csv_content.encode('utf-8')
    result = validate_uploaded_file(file_content, 'csv')
    
    assert result['valid'] == False
    assert any('numerisch' in error.lower() for error in result['errors'])


def test_parse_csv_file_semicolon_delimiter():
    """Test: CSV mit Semikolon-Delimiter wird korrekt geparst"""
    csv_content = """Anzahl Module;10kWh;Ohne Speicher
10;15000.00;12000.00
15;18000.00;15000.00"""
    
    file_content = csv_content.encode('utf-8')
    result = _parse_csv_file(file_content)
    
    assert result['success'] == True
    assert result['dataframe'] is not None
    assert result['info']['delimiter'] == ';'
    assert len(result['dataframe']) == 2
    assert len(result['dataframe'].columns) == 2


def test_parse_csv_file_comma_delimiter():
    """Test: CSV mit Komma-Delimiter wird korrekt geparst"""
    csv_content = """Anzahl Module,10kWh,Ohne Speicher
10,15000.00,12000.00
15,18000.00,15000.00"""
    
    file_content = csv_content.encode('utf-8')
    result = _parse_csv_file(file_content)
    
    assert result['success'] == True
    assert result['dataframe'] is not None
    assert result['info']['delimiter'] == ','


def test_parse_csv_file_different_encodings():
    """Test: CSV mit verschiedenen Encodings wird korrekt geparst"""
    csv_content = """Anzahl Module;10kWh;Ohne Speicher
10;15000.00;12000.00"""
    
    # Test UTF-8
    file_content = csv_content.encode('utf-8')
    result = _parse_csv_file(file_content)
    assert result['success'] == True
    
    # Test Latin-1
    file_content = csv_content.encode('latin-1')
    result = _parse_csv_file(file_content)
    assert result['success'] == True


def test_validate_index_numeric_valid():
    """Test: Numerischer Index wird akzeptiert"""
    df = pd.DataFrame(
        [[15000, 12000], [18000, 15000]],
        index=[10, 15],
        columns=['10kWh', 'Ohne Speicher']
    )
    
    errors = _validate_index_numeric(df)
    assert len(errors) == 0


def test_validate_index_numeric_invalid():
    """Test: Nicht-numerischer Index wird abgelehnt"""
    df = pd.DataFrame(
        [[15000, 12000], [18000, 15000]],
        index=['ABC', 'DEF'],
        columns=['10kWh', 'Ohne Speicher']
    )
    
    errors = _validate_index_numeric(df)
    assert len(errors) > 0
    assert 'numerisch' in errors[0].lower()


def test_validate_column_headers_valid():
    """Test: Gültige Spaltenüberschriften werden akzeptiert"""
    df = pd.DataFrame(
        [[15000, 12000]],
        index=[10],
        columns=['10kWh', 'Ohne Speicher']
    )
    
    errors = _validate_column_headers(df)
    assert len(errors) == 0


def test_validate_column_headers_empty():
    """Test: Leere Spaltenüberschriften werden abgelehnt"""
    df = pd.DataFrame(
        [[15000, 12000]],
        index=[10],
        columns=['10kWh', '']
    )
    
    errors = _validate_column_headers(df)
    assert len(errors) > 0


def test_find_no_storage_column_found():
    """Test: 'Ohne Speicher' Spalte wird gefunden"""
    df = pd.DataFrame(
        [[15000, 12000]],
        index=[10],
        columns=['10kWh', 'Ohne Speicher']
    )
    
    result = _find_no_storage_column(df)
    assert result['found'] == True
    assert result['column_name'] == 'Ohne Speicher'


def test_find_no_storage_column_variations():
    """Test: Verschiedene Varianten von 'Ohne Speicher' werden erkannt"""
    variations = [
        'Ohne Speicher',
        'Kein Speicher',
        'ohne speicher',
        'KEIN SPEICHER',
        'No Storage',
        'none'
    ]
    
    for variation in variations:
        df = pd.DataFrame(
            [[15000, 12000]],
            index=[10],
            columns=['10kWh', variation]
        )
        
        result = _find_no_storage_column(df)
        assert result['found'] == True, f"Variation '{variation}' wurde nicht erkannt"


def test_find_no_storage_column_not_found():
    """Test: Fehlende 'Ohne Speicher' Spalte wird erkannt"""
    df = pd.DataFrame(
        [[15000, 17000]],
        index=[10],
        columns=['10kWh', '15kWh']
    )
    
    result = _find_no_storage_column(df)
    assert result['found'] == False


def test_validate_price_cells_valid():
    """Test: Numerische Preis-Zellen werden akzeptiert"""
    df = pd.DataFrame(
        [[15000.00, 12000.00], [18000.00, 15000.00]],
        index=[10, 15],
        columns=['10kWh', 'Ohne Speicher']
    )
    
    errors, warnings = _validate_price_cells(df)
    assert len(errors) == 0


def test_validate_price_cells_with_comma_decimal():
    """Test: Preise mit Komma als Dezimaltrennzeichen werden akzeptiert"""
    df = pd.DataFrame(
        [['15000,00', '12000,00'], ['18000,00', '15000,00']],
        index=[10, 15],
        columns=['10kWh', 'Ohne Speicher']
    )
    
    errors, warnings = _validate_price_cells(df)
    assert len(errors) == 0


def test_validate_price_cells_invalid():
    """Test: Nicht-numerische Preis-Zellen werden abgelehnt"""
    df = pd.DataFrame(
        [['ABC', 12000.00], [18000.00, 'XYZ']],
        index=[10, 15],
        columns=['10kWh', 'Ohne Speicher']
    )
    
    errors, warnings = _validate_price_cells(df)
    assert len(errors) > 0
    assert 'numerisch' in errors[0].lower()


def test_validate_matrix_structure_complete():
    """Test: Vollständige Matrix-Struktur-Validierung"""
    df = pd.DataFrame(
        [[15000.00, 17500.00, 12000.00],
         [18000.00, 20500.00, 15000.00],
         [21000.00, 23500.00, 18000.00]],
        index=[10, 15, 20],
        columns=['10kWh', '15kWh', 'Ohne Speicher']
    )
    
    result = _validate_matrix_structure(df)
    
    assert len(result['errors']) == 0
    assert 'no_storage_column' in result['info']
    assert result['info']['no_storage_column'] == 'Ohne Speicher'
    assert len(result['info']['module_counts']) == 3
    assert result['info']['module_counts'] == [10, 15, 20]


def test_validate_matrix_structure_empty():
    """Test: Leere Matrix wird abgelehnt"""
    df = pd.DataFrame()
    
    result = _validate_matrix_structure(df)
    
    assert len(result['errors']) > 0
    assert 'leer' in result['errors'][0].lower()


def test_validate_matrix_structure_warnings():
    """Test: Warnungen für kleine Matrizen"""
    # Matrix mit nur einer Zeile
    df = pd.DataFrame(
        [[15000.00, 12000.00]],
        index=[10],
        columns=['10kWh', 'Ohne Speicher']
    )
    
    result = _validate_matrix_structure(df)
    
    assert len(result['warnings']) > 0
    assert any('eine Zeile' in warning for warning in result['warnings'])


def test_validate_uploaded_file_excel():
    """Test: Excel-Datei wird validiert"""
    # Erstelle Excel-Datei im Speicher
    df = pd.DataFrame(
        [[15000.00, 17500.00, 12000.00],
         [18000.00, 20500.00, 15000.00]],
        index=[10, 15],
        columns=['10kWh', '15kWh', 'Ohne Speicher']
    )
    df.index.name = 'Anzahl Module'
    
    # Schreibe zu BytesIO
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, engine='openpyxl')
    excel_content = excel_buffer.getvalue()
    
    result = validate_uploaded_file(excel_content, 'excel')
    
    assert result['valid'] == True
    assert len(result['errors']) == 0
    assert result['preview_df'] is not None


def test_validate_uploaded_file_unsupported_type():
    """Test: Nicht unterstützter Dateityp wird abgelehnt"""
    result = validate_uploaded_file(b'test', 'pdf')
    
    assert result['valid'] == False
    assert any('unterstützt' in error.lower() for error in result['errors'])


def test_info_extraction():
    """Test: Informationen werden korrekt extrahiert"""
    csv_content = """Anzahl Module;10kWh;15kWh;20kWh;Ohne Speicher
10;15000.00;17500.00;19000.00;12000.00
15;18000.00;20500.00;22000.00;15000.00
20;21000.00;23500.00;25000.00;18000.00
25;24000.00;26500.00;28000.00;21000.00"""
    
    file_content = csv_content.encode('utf-8')
    result = validate_uploaded_file(file_content, 'csv')
    
    assert result['valid'] == True
    assert result['info']['rows'] == 4
    assert result['info']['columns'] == 4
    assert len(result['info']['module_counts']) == 4
    assert result['info']['module_counts'] == [10, 15, 20, 25]
    assert len(result['info']['storage_models']) == 4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
