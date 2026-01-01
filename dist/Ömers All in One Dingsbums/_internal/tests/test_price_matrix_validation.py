"""
Test für Preismatrix-Validierung (Task 4.1)

Testet die Validierungsfunktionen für die Preismatrix-Struktur.
"""

import pytest
from price_matrix_validation import (
    validate_matrix_for_pricing,
    get_validation_summary,
    EXAMPLE_MATRIX_STRUCTURE
)
from price_matrix_examples import (
    create_example_matrix_small,
    get_matrix_structure_help,
    get_quick_help_tooltips
)
from price_matrix_store import (
    create_matrix,
    add_row,
    add_column,
    set_cell_value,
    delete_matrix
)


def test_validate_empty_matrix():
    """Test: Validierung einer leeren Matrix"""
    # Erstelle leere Matrix
    matrix_id = create_matrix("Test: Leere Matrix")
    
    try:
        # Validiere
        result = validate_matrix_for_pricing(matrix_id)
        
        # Prüfe Ergebnis
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert 'leer' in result['errors'][0].lower()
    
    finally:
        # Cleanup
        delete_matrix(matrix_id)


def test_validate_example_matrix():
    """Test: Validierung einer Beispiel-Matrix"""
    # Erstelle Beispiel-Matrix
    matrix_id = create_example_matrix_small()
    
    try:
        # Validiere
        result = validate_matrix_for_pricing(matrix_id)
        
        # Prüfe Ergebnis
        assert result['valid'] is True
        assert len(result['errors']) == 0
        
        # Prüfe Info
        info = result['info']
        assert info['total_rows'] > 0
        assert info['total_columns'] > 0
        assert 'no_storage_column' in info
        assert len(info['module_counts']) > 0
        assert len(info['storage_models']) > 0
    
    finally:
        # Cleanup
        delete_matrix(matrix_id)


def test_validate_missing_no_storage_column():
    """Test: Validierung ohne 'Kein Speicher' Spalte"""
    # Erstelle Matrix ohne "Kein Speicher" Spalte
    matrix_id = create_matrix("Test: Ohne Kein Speicher")
    
    try:
        # Spalten
        col_a_id = add_column(matrix_id, "Modulanzahl", position=0)
        col_b_id = add_column(matrix_id, "10kWh", position=1)
        col_c_id = add_column(matrix_id, "15kWh", position=2)
        
        # Zeilen
        row_1_id = add_row(matrix_id, "Modulanzahl", position=0)
        row_2_id = add_row(matrix_id, "10", position=1)
        
        # Header-Zeile
        set_cell_value(matrix_id, row_1_id, col_b_id, None, "10kWh", 'text')
        set_cell_value(matrix_id, row_1_id, col_c_id, None, "15kWh", 'text')
        
        # Daten-Zeile
        set_cell_value(matrix_id, row_2_id, col_a_id, 10.0, "10", 'number')
        set_cell_value(matrix_id, row_2_id, col_b_id, 15000.0, "15000", 'number')
        set_cell_value(matrix_id, row_2_id, col_c_id, 17500.0, "17500", 'number')
        
        # Validiere
        result = validate_matrix_for_pricing(matrix_id)
        
        # Prüfe Ergebnis
        assert result['valid'] is False
        assert any('kein speicher' in error.lower() for error in result['errors'])
    
    finally:
        # Cleanup
        delete_matrix(matrix_id)


def test_validate_non_numeric_column_a():
    """Test: Validierung mit Text in Spalte A"""
    # Erstelle Matrix mit Text in Spalte A
    matrix_id = create_matrix("Test: Text in Spalte A")
    
    try:
        # Spalten
        col_a_id = add_column(matrix_id, "Modulanzahl", position=0)
        col_b_id = add_column(matrix_id, "Kein Speicher", position=1)
        
        # Zeilen
        row_1_id = add_row(matrix_id, "Modulanzahl", position=0)
        row_2_id = add_row(matrix_id, "zehn", position=1)  # Text statt Zahl
        
        # Header-Zeile
        set_cell_value(matrix_id, row_1_id, col_b_id, None, "Kein Speicher", 'text')
        
        # Daten-Zeile mit Text in Spalte A
        set_cell_value(matrix_id, row_2_id, col_a_id, None, "zehn", 'text')
        set_cell_value(matrix_id, row_2_id, col_b_id, 12000.0, "12000", 'number')
        
        # Validiere
        result = validate_matrix_for_pricing(matrix_id)
        
        # Prüfe Ergebnis
        assert result['valid'] is False
        assert any('spalte a' in error.lower() and 'numerisch' in error.lower() 
                   for error in result['errors'])
    
    finally:
        # Cleanup
        delete_matrix(matrix_id)


def test_validation_summary():
    """Test: Validierungs-Zusammenfassung"""
    # Erstelle Beispiel-Matrix
    matrix_id = create_example_matrix_small()
    
    try:
        # Validiere
        result = validate_matrix_for_pricing(matrix_id)
        
        # Erstelle Zusammenfassung
        summary = get_validation_summary(result)
        
        # Prüfe Zusammenfassung
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert 'Matrix ist gültig' in summary or 'Matrix ist NICHT gültig' in summary
    
    finally:
        # Cleanup
        delete_matrix(matrix_id)


def test_example_matrix_structure():
    """Test: Beispiel-Matrix-Struktur ist verfügbar"""
    assert isinstance(EXAMPLE_MATRIX_STRUCTURE, str)
    assert len(EXAMPLE_MATRIX_STRUCTURE) > 0
    assert 'Modulanzahl' in EXAMPLE_MATRIX_STRUCTURE


def test_matrix_structure_help():
    """Test: Matrix-Struktur-Hilfe ist verfügbar"""
    help_text = get_matrix_structure_help()
    
    assert isinstance(help_text, str)
    assert len(help_text) > 0
    assert 'Modulanzahl' in help_text
    assert 'Speichermodell' in help_text


def test_quick_help_tooltips():
    """Test: Quick-Help-Tooltips sind verfügbar"""
    tooltips = get_quick_help_tooltips()
    
    assert isinstance(tooltips, dict)
    assert 'column_a' in tooltips
    assert 'row_1' in tooltips
    assert 'price_cells' in tooltips
    assert 'no_storage' in tooltips
    assert 'validation' in tooltips
    
    # Prüfe Inhalte
    assert 'Modulanzahl' in tooltips['column_a']
    assert 'Speichermodell' in tooltips['row_1']
    assert 'Preis' in tooltips['price_cells']


if __name__ == '__main__':
    # Führe Tests aus
    print("Teste Preismatrix-Validierung...")
    
    print("\n1. Test: Leere Matrix")
    test_validate_empty_matrix()
    print("Bestanden")
    
    print("\n2. Test: Beispiel-Matrix")
    test_validate_example_matrix()
    print("Bestanden")
    
    print("\n3. Test: Fehlende 'Kein Speicher' Spalte")
    test_validate_missing_no_storage_column()
    print("Bestanden")
    
    print("\n4. Test: Text in Spalte A")
    test_validate_non_numeric_column_a()
    print("Bestanden")
    
    print("\n5. Test: Validierungs-Zusammenfassung")
    test_validation_summary()
    print("Bestanden")
    
    print("\n6. Test: Beispiel-Matrix-Struktur")
    test_example_matrix_structure()
    print("Bestanden")
    
    print("\n7. Test: Matrix-Struktur-Hilfe")
    test_matrix_structure_help()
    print("Bestanden")
    
    print("\n8. Test: Quick-Help-Tooltips")
    test_quick_help_tooltips()
    print("Bestanden")
    
    print("\nAlle Tests bestanden!")
