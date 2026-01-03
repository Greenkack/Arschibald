"""
Integration Tests für Excel Product Pricing UI

Testet die UI-Komponenten für Produktpreis-Konfiguration.
"""

import pytest
from excel.excel_product_pricing import (
    calculate_product_price_from_matrix,
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
    delete_matrix,
    list_matrices
)


class TestPriceCalculationFromMatrix:
    """Tests für Preisberechnung aus Matrix"""
    
    @pytest.fixture
    def pauschal_matrix(self):
        """Erstellt eine Pauschal-Preismatrix"""
        matrix_id = create_matrix(
            "Test Pauschal Matrix",
            "Test Matrix für Pauschalpreise",
            pricing_mode='pauschal'
        )
        
        # Füge Zeilen hinzu (Modulanzahl)
        rows = {}
        for modules in [10, 15, 20, 25, 30]:
            rows[modules] = add_row(matrix_id, str(modules))
        
        # Füge Spalten hinzu (Speicher-Varianten)
        cols = {}
        for storage in [5, 10, 15, 20]:
            cols[storage] = add_column(matrix_id, f"{storage}kWh")
        
        # Setze Preise (Basis: 500€ pro Modul + 1000€ pro kWh Speicher)
        for modules, row_id in rows.items():
            for storage, col_id in cols.items():
                price = modules * 500 + storage * 1000
                set_cell_value(matrix_id, row_id, col_id, float(price))
        
        set_active_matrix(matrix_id)
        
        yield matrix_id
        
        delete_matrix(matrix_id)
    
    def test_calculate_price_pauschal_mode(self, pauschal_matrix):
        """Test: Preis aus Matrix berechnen (Pauschal-Modus)"""
        # Berechne Preis für 20 Module mit 10kWh Speicher
        result = calculate_product_price_from_matrix("20", "10kWh")
        
        assert result.is_valid()
        assert result.base_price == 20000.0  # 20*500 + 10*1000
        assert result.total_price == 20000.0
        assert result.pricing_mode == 'pauschal'
        assert result.accessories_price == 0.0
        assert result.misc_price == 0.0
    
    def test_calculate_price_with_floor_matching(self, pauschal_matrix):
        """Test: Floor-Matching für numerische Zeilen"""
        # Anfrage für 22 Module sollte auf 20 Module zurückfallen
        result = calculate_product_price_from_matrix("22", "10kWh")
        
        assert result.is_valid()
        assert result.base_price == 20000.0
        assert result.row_used == "20"
        assert result.row_floor_source == "20"
    
    def test_calculate_price_all_combinations(self, pauschal_matrix):
        """Test: Alle Kombinationen berechnen"""
        module_counts = [10, 15, 20, 25, 30]
        storage_sizes = [5, 10, 15, 20]
        
        for modules in module_counts:
            for storage in storage_sizes:
                result = calculate_product_price_from_matrix(
                    str(modules),
                    f"{storage}kWh"
                )
                
                assert result.is_valid()
                expected_price = modules * 500 + storage * 1000
                assert result.total_price == expected_price


class TestAdditivPricingMode:
    """Tests für Additiv-Preisberechnung"""
    
    @pytest.fixture
    def additiv_matrix(self):
        """Erstellt eine Additiv-Preismatrix"""
        matrix_id = create_matrix(
            "Test Additiv Matrix",
            "Test Matrix für Additiv-Preise",
            pricing_mode='additiv'
        )
        
        update_matrix_pricing_mode(
            matrix_id,
            'additiv',
            include_accessories=True,
            include_misc=True
        )
        
        # Füge Daten hinzu
        rows = {}
        for modules in [10, 20, 30]:
            rows[modules] = add_row(matrix_id, str(modules))
        
        cols = {}
        for storage in [5, 10, 15]:
            cols[storage] = add_column(matrix_id, f"{storage}kWh")
        
        # Setze Basis-Preise (niedriger als Pauschal)
        for modules, row_id in rows.items():
            for storage, col_id in cols.items():
                base_price = modules * 400 + storage * 800
                set_cell_value(matrix_id, row_id, col_id, float(base_price))
        
        set_active_matrix(matrix_id)
        
        yield matrix_id
        
        delete_matrix(matrix_id)
    
    def test_additiv_mode_without_extras(self, additiv_matrix):
        """Test: Additiv-Modus ohne Zubehör"""
        result = calculate_product_price_from_matrix("20", "10kWh")
        
        assert result.is_valid()
        assert result.base_price == 16000.0  # 20*400 + 10*800
        assert result.total_price == 16000.0
        assert result.pricing_mode == 'additiv'
        assert result.accessories_price == 0.0
        assert result.misc_price == 0.0
    
    def test_additiv_mode_with_accessories(self, additiv_matrix):
        """Test: Additiv-Modus mit Zubehör"""
        result = calculate_product_price_from_matrix(
            "20", "10kWh",
            accessories_price=1500.0,
            misc_price=500.0
        )
        
        assert result.is_valid()
        assert result.base_price == 16000.0
        assert result.accessories_price == 1500.0
        assert result.misc_price == 500.0
        assert result.total_price == 18000.0  # 16000 + 1500 + 500
    
    def test_additiv_mode_exclude_accessories(self, additiv_matrix):
        """Test: Additiv-Modus ohne Zubehör-Einbeziehung"""
        # Ändere Matrix-Einstellungen
        update_matrix_pricing_mode(
            additiv_matrix,
            'additiv',
            include_accessories=False,
            include_misc=True
        )
        
        result = calculate_product_price_from_matrix(
            "20", "10kWh",
            accessories_price=1500.0,
            misc_price=500.0
        )
        
        assert result.is_valid()
        assert result.base_price == 16000.0
        assert result.accessories_price == 0.0  # Nicht einbezogen
        assert result.misc_price == 500.0
        assert result.total_price == 16500.0  # 16000 + 500
    
    def test_additiv_mode_exclude_misc(self, additiv_matrix):
        """Test: Additiv-Modus ohne Sonstiges-Einbeziehung"""
        # Ändere Matrix-Einstellungen
        update_matrix_pricing_mode(
            additiv_matrix,
            'additiv',
            include_accessories=True,
            include_misc=False
        )
        
        result = calculate_product_price_from_matrix(
            "20", "10kWh",
            accessories_price=1500.0,
            misc_price=500.0
        )
        
        assert result.is_valid()
        assert result.base_price == 16000.0
        assert result.accessories_price == 1500.0
        assert result.misc_price == 0.0  # Nicht einbezogen
        assert result.total_price == 17500.0  # 16000 + 1500


class TestMatrixChangeUpdatesPrice:
    """Tests für automatische Preis-Aktualisierung bei Matrix-Änderungen"""
    
    @pytest.fixture
    def test_matrix(self):
        """Erstellt eine Test-Matrix"""
        matrix_id = create_matrix("Test Matrix für Updates")
        
        row_id = add_row(matrix_id, "20")
        col_id = add_column(matrix_id, "10kWh")
        set_cell_value(matrix_id, row_id, col_id, 15000.0)
        
        set_active_matrix(matrix_id)
        
        yield (matrix_id, row_id, col_id)
        
        delete_matrix(matrix_id)
    
    def test_price_updates_when_matrix_changes(self, test_matrix):
        """Test: Preis aktualisiert sich bei Matrix-Änderung"""
        matrix_id, row_id, col_id = test_matrix
        
        # Erste Berechnung
        result1 = calculate_product_price_from_matrix("20", "10kWh")
        assert result1.is_valid()
        assert result1.total_price == 15000.0
        
        # Ändere Preis in Matrix
        set_cell_value(matrix_id, row_id, col_id, 18000.0)
        
        # Zweite Berechnung
        result2 = calculate_product_price_from_matrix("20", "10kWh")
        assert result2.is_valid()
        assert result2.total_price == 18000.0
        
        # Preis hat sich geändert
        assert result2.total_price != result1.total_price
    
    def test_price_updates_when_row_added(self, test_matrix):
        """Test: Neue Zeile wird erkannt"""
        matrix_id, _, col_id = test_matrix
        
        # Füge neue Zeile hinzu
        new_row_id = add_row(matrix_id, "25")
        set_cell_value(matrix_id, new_row_id, col_id, 20000.0)
        
        # Berechne Preis für neue Zeile
        result = calculate_product_price_from_matrix("25", "10kWh")
        assert result.is_valid()
        assert result.total_price == 20000.0
    
    def test_price_updates_when_column_added(self, test_matrix):
        """Test: Neue Spalte wird erkannt"""
        matrix_id, row_id, _ = test_matrix
        
        # Füge neue Spalte hinzu
        new_col_id = add_column(matrix_id, "15kWh")
        set_cell_value(matrix_id, row_id, new_col_id, 22000.0)
        
        # Berechne Preis für neue Spalte
        result = calculate_product_price_from_matrix("20", "15kWh")
        assert result.is_valid()
        assert result.total_price == 22000.0


class TestPricePreview:
    """Tests für Preis-Vorschau-Funktionalität"""
    
    @pytest.fixture
    def large_matrix(self):
        """Erstellt eine größere Matrix für Vorschau-Tests"""
        matrix_id = create_matrix("Large Test Matrix")
        
        # Füge viele Zeilen und Spalten hinzu
        rows = []
        for i in range(20):
            rows.append(add_row(matrix_id, f"{(i+1)*10}"))
        
        cols = []
        for i in range(10):
            cols.append(add_column(matrix_id, f"{(i+1)*5}kWh"))
        
        # Setze einige Preise
        for i, row_id in enumerate(rows[:10]):
            for j, col_id in enumerate(cols[:5]):
                price = (i + 1) * 1000 + (j + 1) * 500
                set_cell_value(matrix_id, row_id, col_id, float(price))
        
        set_active_matrix(matrix_id)
        
        yield matrix_id
        
        delete_matrix(matrix_id)
    
    def test_preview_returns_limited_data(self, large_matrix):
        """Test: Vorschau limitiert Daten"""
        preview = get_price_preview(max_rows=5, max_cols=5)
        
        assert 'error' not in preview
        assert len(preview['rows']) <= 5
        assert len(preview['columns']) <= 5
        assert preview['truncated'] is True
    
    def test_preview_shows_all_prices(self, large_matrix):
        """Test: Vorschau zeigt alle verfügbaren Preise"""
        preview = get_price_preview(max_rows=10, max_cols=5)
        
        # Prüfe dass Preise vorhanden sind
        assert len(preview['prices']) > 0
        
        # Prüfe dass alle Preise numerisch sind
        for price in preview['prices'].values():
            assert isinstance(price, (int, float))
            assert price > 0


class TestMatrixValidation:
    """Tests für Matrix-Validierung"""
    
    def test_validate_valid_matrix(self):
        """Test: Validierung einer gültigen Matrix"""
        matrix_id = create_matrix("Valid Matrix")
        row_id = add_row(matrix_id, "10")
        col_id = add_column(matrix_id, "5kWh")
        set_cell_value(matrix_id, row_id, col_id, 1000.0)
        set_active_matrix(matrix_id)
        
        validation = validate_matrix_for_product_pricing()
        
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
        
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


class TestCompleteWorkflow:
    """Integrations-Tests für kompletten Workflow"""
    
    def test_complete_product_pricing_workflow(self):
        """Test: Kompletter Workflow von Matrix-Erstellung bis Preisberechnung"""
        # 1. Erstelle Matrix
        matrix_id = create_matrix(
            "Complete Workflow Matrix",
            "Test für kompletten Workflow",
            pricing_mode='pauschal'
        )
        
        # 2. Füge Zeilen hinzu
        rows = {}
        for modules in [10, 15, 20, 25, 30]:
            rows[modules] = add_row(matrix_id, str(modules))
        
        # 3. Füge Spalten hinzu
        cols = {}
        for storage in [5, 10, 15, 20]:
            cols[storage] = add_column(matrix_id, f"{storage}kWh")
        
        # 4. Setze Preise
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
        
        # 8. Berechne verschiedene Preise
        test_cases = [
            ("10", "5kWh", 10000.0),
            ("20", "10kWh", 20000.0),
            ("30", "15kWh", 30000.0),
        ]
        
        for row, col, expected_price in test_cases:
            result = calculate_product_price_from_matrix(row, col)
            assert result.is_valid()
            assert result.total_price == expected_price
        
        # 9. Teste Floor-Matching
        result = calculate_product_price_from_matrix("22", "10kWh")
        assert result.is_valid()
        assert result.base_price == 20000.0
        assert result.row_floor_source == "20"
        
        # Cleanup
        delete_matrix(matrix_id)
    
    def test_switch_between_pricing_modes(self):
        """Test: Wechsel zwischen Pauschal und Additiv"""
        # Erstelle Matrix
        matrix_id = create_matrix("Mode Switch Matrix", pricing_mode='pauschal')
        
        row_id = add_row(matrix_id, "20")
        col_id = add_column(matrix_id, "10kWh")
        set_cell_value(matrix_id, row_id, col_id, 15000.0)
        set_active_matrix(matrix_id)
        
        # Test Pauschal-Modus
        result1 = calculate_product_price_from_matrix("20", "10kWh")
        assert result1.is_valid()
        assert result1.pricing_mode == 'pauschal'
        assert result1.total_price == 15000.0
        
        # Wechsel zu Additiv-Modus
        update_matrix_pricing_mode(
            matrix_id,
            'additiv',
            include_accessories=True,
            include_misc=True
        )
        
        # Test Additiv-Modus ohne Extras
        result2 = calculate_product_price_from_matrix("20", "10kWh")
        assert result2.is_valid()
        assert result2.pricing_mode == 'additiv'
        assert result2.total_price == 15000.0
        
        # Test Additiv-Modus mit Extras
        result3 = calculate_product_price_from_matrix(
            "20", "10kWh",
            accessories_price=1000.0,
            misc_price=500.0
        )
        assert result3.is_valid()
        assert result3.total_price == 16500.0
        
        # Cleanup
        delete_matrix(matrix_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
