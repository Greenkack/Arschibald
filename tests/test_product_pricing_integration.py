"""
Tests für Excel Product Pricing Integration

Testet die Integration zwischen Excel-Matrizen und Produktpreisen.
"""

import pytest
from excel.excel_product_pricing import (
    ProductPriceResult,
    calculate_product_price_from_matrix,
    calculate_product_price_for_product,
    get_price_preview,
    validate_matrix_for_product_pricing
)
from price_matrix_store import (
    create_matrix,
    add_row,
    add_column,
    set_cell_value,
    set_active_matrix,
    update_matrix_pricing_mode,
    delete_matrix
)


class TestProductPriceResult:
    """Tests für ProductPriceResult Dataclass"""
    
    def test_is_valid_with_price(self):
        """Test: is_valid gibt True zurück wenn Preis vorhanden"""
        result = ProductPriceResult(total_price=100.0)
        assert result.is_valid() is True
    
    def test_is_valid_without_price(self):
        """Test: is_valid gibt False zurück wenn kein Preis"""
        result = ProductPriceResult(total_price=None)
        assert result.is_valid() is False
    
    def test_is_valid_with_error(self):
        """Test: is_valid gibt False zurück bei Fehler"""
        result = ProductPriceResult(total_price=100.0, error="Test Error")
        assert result.is_valid() is False


class TestCalculateProductPriceFromMatrix:
    """Tests für calculate_product_price_from_matrix"""
    
    @pytest.fixture
    def test_matrix(self):
        """Erstellt eine Test-Matrix"""
        # Erstelle Matrix
        matrix_id = create_matrix(
            "Test Pricing Matrix",
            "Test Matrix für Produktpreise",
            pricing_mode='pauschal'
        )
        
        # Füge Zeilen hinzu (Modulanzahl)
        row_10 = add_row(matrix_id, "10")
        row_20 = add_row(matrix_id, "20")
        row_30 = add_row(matrix_id, "30")
        
        # Füge Spalten hinzu (Speicher-Varianten)
        col_5kwh = add_column(matrix_id, "5kWh")
        col_10kwh = add_column(matrix_id, "10kWh")
        col_15kwh = add_column(matrix_id, "15kWh")
        
        # Setze Preise
        set_cell_value(matrix_id, row_10, col_5kwh, 8000.0)
        set_cell_value(matrix_id, row_10, col_10kwh, 10000.0)
        set_cell_value(matrix_id, row_10, col_15kwh, 12000.0)
        
        set_cell_value(matrix_id, row_20, col_5kwh, 15000.0)
        set_cell_value(matrix_id, row_20, col_10kwh, 18000.0)
        set_cell_value(matrix_id, row_20, col_15kwh, 21000.0)
        
        set_cell_value(matrix_id, row_30, col_5kwh, 22000.0)
        set_cell_value(matrix_id, row_30, col_10kwh, 26000.0)
        set_cell_value(matrix_id, row_30, col_15kwh, 30000.0)
        
        # Setze als aktive Matrix
        set_active_matrix(matrix_id)
        
        yield matrix_id
        
        # Cleanup
        delete_matrix(matrix_id)
    
    def test_calculate_pauschal_mode(self, test_matrix):
        """Test: Berechnung im Pauschal-Modus"""
        result = calculate_product_price_from_matrix("20", "10kWh")
        
        assert result.is_valid()
        assert result.base_price == 18000.0
        assert result.total_price == 18000.0
        assert result.pricing_mode == 'pauschal'
        assert result.row_used == "20"
        assert result.column_used == "10kWh"
        assert result.error is None
    
    def test_calculate_with_floor_matching(self, test_matrix):
        """Test: Floor-Matching für numerische Zeilen"""
        # Anfrage für 25 Module sollte auf 20 Module zurückfallen
        result = calculate_product_price_from_matrix("25", "10kWh")
        
        assert result.is_valid()
        assert result.base_price == 18000.0
        assert result.row_used == "20"
        assert result.row_floor_source == "20"
    
    def test_calculate_additiv_mode_without_extras(self, test_matrix):
        """Test: Additiv-Modus ohne Zubehör"""
        # Ändere zu Additiv-Modus
        update_matrix_pricing_mode(
            test_matrix,
            'additiv',
            include_accessories=True,
            include_misc=True
        )
        
        result = calculate_product_price_from_matrix("20", "10kWh")
        
        assert result.is_valid()
        assert result.base_price == 18000.0
        assert result.total_price == 18000.0
        assert result.pricing_mode == 'additiv'
    
    def test_calculate_additiv_mode_with_accessories(self, test_matrix):
        """Test: Additiv-Modus mit Zubehör"""
        # Ändere zu Additiv-Modus
        update_matrix_pricing_mode(
            test_matrix,
            'additiv',
            include_accessories=True,
            include_misc=True
        )
        
        result = calculate_product_price_from_matrix(
            "20", "10kWh",
            accessories_price=500.0,
            misc_price=200.0
        )
        
        assert result.is_valid()
        assert result.base_price == 18000.0
        assert result.accessories_price == 500.0
        assert result.misc_price == 200.0
        assert result.total_price == 18700.0
    
    def test_calculate_additiv_mode_exclude_accessories(self, test_matrix):
        """Test: Additiv-Modus ohne Zubehör-Einbeziehung"""
        # Ändere zu Additiv-Modus ohne Zubehör
        update_matrix_pricing_mode(
            test_matrix,
            'additiv',
            include_accessories=False,
            include_misc=True
        )
        
        result = calculate_product_price_from_matrix(
            "20", "10kWh",
            accessories_price=500.0,
            misc_price=200.0
        )
        
        assert result.is_valid()
        assert result.base_price == 18000.0
        assert result.accessories_price == 0.0  # Nicht einbezogen
        assert result.misc_price == 200.0
        assert result.total_price == 18200.0
    
    def test_calculate_invalid_row(self, test_matrix):
        """Test: Floor-Matching für sehr hohe Werte"""
        # 999 Module sollte auf höchsten Wert (30) zurückfallen
        result = calculate_product_price_from_matrix("999", "10kWh")
        
        assert result.is_valid()
        assert result.base_price == 26000.0  # Preis für 30 Module
        assert result.row_used == "30"
        assert result.row_floor_source == "30"
    
    def test_calculate_invalid_column(self, test_matrix):
        """Test: Fehler bei ungültiger Spalte"""
        result = calculate_product_price_from_matrix("20", "999kWh")
        
        assert not result.is_valid()
        assert result.error is not None
    
    def test_calculate_without_active_matrix(self):
        """Test: Fehler wenn keine aktive Matrix"""
        # Setze keine Matrix als aktiv
        result = calculate_product_price_from_matrix("20", "10kWh")
        
        assert not result.is_valid()
        assert result.error is not None
        assert "Keine aktive Matrix" in result.error
    
    def test_calculate_with_specific_matrix_id(self, test_matrix):
        """Test: Berechnung mit spezifischer Matrix-ID"""
        result = calculate_product_price_from_matrix(
            "20", "10kWh",
            matrix_id=test_matrix
        )
        
        assert result.is_valid()
        assert result.matrix_id == test_matrix


class TestGetPricePreview:
    """Tests für get_price_preview"""
    
    @pytest.fixture
    def test_matrix(self):
        """Erstellt eine Test-Matrix"""
        matrix_id = create_matrix("Preview Test Matrix")
        
        # Füge mehrere Zeilen und Spalten hinzu
        rows = []
        for i in range(15):
            rows.append(add_row(matrix_id, f"{(i+1)*10}"))
        
        cols = []
        for i in range(8):
            cols.append(add_column(matrix_id, f"{(i+1)*5}kWh"))
        
        # Setze einige Preise
        for i, row_id in enumerate(rows[:5]):
            for j, col_id in enumerate(cols[:5]):
                price = (i + 1) * 1000 + (j + 1) * 100
                set_cell_value(matrix_id, row_id, col_id, float(price))
        
        set_active_matrix(matrix_id)
        
        yield matrix_id
        
        delete_matrix(matrix_id)
    
    def test_preview_default(self, test_matrix):
        """Test: Standard-Vorschau"""
        preview = get_price_preview()
        
        assert 'error' not in preview
        assert preview['matrix_id'] == test_matrix
        assert preview['matrix_name'] == "Preview Test Matrix"
        assert len(preview['rows']) <= 10
        assert len(preview['columns']) <= 10
        assert len(preview['prices']) > 0
    
    def test_preview_with_limits(self, test_matrix):
        """Test: Vorschau mit Limits"""
        preview = get_price_preview(max_rows=3, max_cols=3)
        
        assert len(preview['rows']) == 3
        assert len(preview['columns']) == 3
        assert preview['truncated'] is True
    
    def test_preview_with_specific_labels(self, test_matrix):
        """Test: Vorschau mit spezifischen Labels"""
        preview = get_price_preview(
            row_labels=["10", "20", "30"],
            column_labels=["5kWh", "10kWh"]
        )
        
        assert set(preview['rows']) == {"10", "20", "30"}
        assert set(preview['columns']) == {"5kWh", "10kWh"}
    
    def test_preview_prices_correct(self, test_matrix):
        """Test: Vorschau-Preise sind korrekt"""
        preview = get_price_preview(max_rows=2, max_cols=2)
        
        # Prüfe dass Preise vorhanden sind
        assert len(preview['prices']) > 0
        
        # Prüfe dass alle Preise numerisch sind
        for price in preview['prices'].values():
            assert isinstance(price, (int, float))
            assert price > 0


class TestValidateMatrixForProductPricing:
    """Tests für validate_matrix_for_product_pricing"""
    
    def test_validate_valid_matrix(self):
        """Test: Validierung einer gültigen Matrix"""
        # Erstelle gültige Matrix
        matrix_id = create_matrix("Valid Matrix")
        row_id = add_row(matrix_id, "10")
        col_id = add_column(matrix_id, "5kWh")
        set_cell_value(matrix_id, row_id, col_id, 1000.0)
        set_active_matrix(matrix_id)
        
        validation = validate_matrix_for_product_pricing()
        
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
        assert validation['info']['matrix_id'] == matrix_id
        assert validation['info']['row_count'] == 1
        assert validation['info']['column_count'] == 1
        
        delete_matrix(matrix_id)
    
    def test_validate_matrix_without_rows(self):
        """Test: Validierung Matrix ohne Zeilen"""
        matrix_id = create_matrix("No Rows Matrix")
        add_column(matrix_id, "5kWh")
        set_active_matrix(matrix_id)
        
        validation = validate_matrix_for_product_pricing()
        
        assert validation['valid'] is False
        assert any('keine Zeilen' in error for error in validation['errors'])
        
        delete_matrix(matrix_id)
    
    def test_validate_matrix_without_columns(self):
        """Test: Validierung Matrix ohne Spalten"""
        matrix_id = create_matrix("No Columns Matrix")
        add_row(matrix_id, "10")
        set_active_matrix(matrix_id)
        
        validation = validate_matrix_for_product_pricing()
        
        assert validation['valid'] is False
        assert any('keine Spalten' in error for error in validation['errors'])
        
        delete_matrix(matrix_id)
    
    def test_validate_matrix_without_values(self):
        """Test: Validierung Matrix ohne Werte (Warnung)"""
        matrix_id = create_matrix("No Values Matrix")
        add_row(matrix_id, "10")
        add_column(matrix_id, "5kWh")
        set_active_matrix(matrix_id)
        
        validation = validate_matrix_for_product_pricing()
        
        # Matrix ist technisch gültig, aber hat Warnung
        assert validation['valid'] is True
        assert any('keine Werte' in warning for warning in validation['warnings'])
        
        delete_matrix(matrix_id)
    
    def test_validate_matrix_with_duplicate_row_labels(self):
        """Test: Validierung Matrix mit doppelten Zeilen-Labels"""
        matrix_id = create_matrix("Duplicate Rows Matrix")
        add_row(matrix_id, "10")
        add_row(matrix_id, "10")  # Duplikat
        add_column(matrix_id, "5kWh")
        set_active_matrix(matrix_id)
        
        validation = validate_matrix_for_product_pricing()
        
        assert validation['valid'] is True  # Technisch gültig
        assert any('nicht eindeutig' in warning for warning in validation['warnings'])
        
        delete_matrix(matrix_id)
    
    def test_validate_without_active_matrix(self):
        """Test: Validierung ohne aktive Matrix"""
        validation = validate_matrix_for_product_pricing()
        
        assert validation['valid'] is False
        assert any('Keine aktive Matrix' in error for error in validation['errors'])


class TestIntegrationScenarios:
    """Integrations-Tests für realistische Szenarien"""
    
    def test_complete_pricing_workflow(self):
        """Test: Kompletter Workflow von Matrix-Erstellung bis Preisberechnung"""
        # 1. Erstelle Matrix
        matrix_id = create_matrix(
            "PV System Pricing",
            "Preise für PV-Systeme nach Modulanzahl und Speicher",
            pricing_mode='pauschal'
        )
        
        # 2. Füge Zeilen hinzu (Modulanzahl)
        rows = {}
        for modules in [10, 15, 20, 25, 30]:
            rows[modules] = add_row(matrix_id, str(modules))
        
        # 3. Füge Spalten hinzu (Speicher-Größen)
        cols = {}
        for storage in [5, 10, 15, 20]:
            cols[storage] = add_column(matrix_id, f"{storage}kWh")
        
        # 4. Setze Preise (Basis: 500€ pro Modul + 1000€ pro kWh Speicher)
        for modules, row_id in rows.items():
            for storage, col_id in cols.items():
                price = modules * 500 + storage * 1000
                set_cell_value(matrix_id, row_id, col_id, float(price))
        
        # 5. Setze als aktiv
        set_active_matrix(matrix_id)
        
        # 6. Validiere Matrix
        validation = validate_matrix_for_product_pricing()
        assert validation['valid'] is True
        
        # 7. Hole Vorschau
        preview = get_price_preview()
        assert len(preview['prices']) > 0
        
        # 8. Berechne Preis für 20 Module mit 10kWh Speicher
        result = calculate_product_price_from_matrix("20", "10kWh")
        assert result.is_valid()
        assert result.total_price == 20000.0  # 20*500 + 10*1000
        
        # 9. Teste Floor-Matching (22 Module sollte auf 20 zurückfallen)
        result = calculate_product_price_from_matrix("22", "10kWh")
        assert result.is_valid()
        assert result.base_price == 20000.0
        assert result.row_floor_source == "20"
        
        # Cleanup
        delete_matrix(matrix_id)
    
    def test_additiv_pricing_with_accessories(self):
        """Test: Additiv-Preisberechnung mit Zubehör"""
        # Erstelle Matrix im Additiv-Modus
        matrix_id = create_matrix(
            "Additiv Pricing",
            pricing_mode='additiv'
        )
        update_matrix_pricing_mode(
            matrix_id,
            'additiv',
            include_accessories=True,
            include_misc=True
        )
        
        # Füge Daten hinzu
        row_id = add_row(matrix_id, "20")
        col_id = add_column(matrix_id, "10kWh")
        set_cell_value(matrix_id, row_id, col_id, 15000.0)
        set_active_matrix(matrix_id)
        
        # Berechne mit Zubehör
        result = calculate_product_price_from_matrix(
            "20", "10kWh",
            accessories_price=1500.0,
            misc_price=500.0
        )
        
        assert result.is_valid()
        assert result.base_price == 15000.0
        assert result.accessories_price == 1500.0
        assert result.misc_price == 500.0
        assert result.total_price == 17000.0
        
        # Cleanup
        delete_matrix(matrix_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
