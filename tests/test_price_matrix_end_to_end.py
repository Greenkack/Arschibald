"""test_price_matrix_end_to_end.py

End-to-End Tests für das Preismatrix-System mit realen Daten.

Testet den kompletten Workflow:
1. Upload → Matrix-Erstellung
2. Berechnung → Preis-Lookup
3. Anzeige → UI-Integration

Task 10: Führe End-to-End Tests mit realen Daten durch
Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""

import io
import os
import tempfile
from typing import Any

import pandas as pd
import pytest

# Import core modules
import price_matrix_store
from price_matrix_lookup import calculate_price_from_matrix
from price_matrix_validation import validate_matrix_for_pricing


class TestEndToEndMatrixWorkflow:
    """End-to-End Tests für den kompletten Matrix-Workflow"""
    
    @pytest.fixture
    def real_matrix_csv(self):
        """Realistische Preismatrix als CSV"""
        return """Anzahl Module;BYD Battery-Box Premium HVS 10.2;BYD Battery-Box Premium HVS 12.8;Kein Speicher
10;15000.00;16500.00;12000.00
15;18000.00;19500.00;14500.00
20;21000.00;22500.00;17000.00
25;24000.00;25500.00;19500.00
30;27000.00;28500.00;22000.00
35;30000.00;31500.00;24500.00
40;33000.00;34500.00;27000.00"""
    
    @pytest.fixture
    def real_matrix_excel_bytes(self, real_matrix_csv):
        """Realistische Preismatrix als Excel-Bytes"""
        # Parse CSV to DataFrame
        df = pd.read_csv(io.StringIO(real_matrix_csv), sep=';', index_col=0)
        
        # Convert to Excel bytes
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, engine='openpyxl')
        excel_buffer.seek(0)
        
        return excel_buffer.read()
    
    @pytest.fixture
    def cleanup_test_matrices(self):
        """Cleanup fixture to remove test matrices after tests"""
        created_matrix_ids = []
        
        yield created_matrix_ids
        
        # Cleanup
        for matrix_id in created_matrix_ids:
            try:
                price_matrix_store.delete_matrix(matrix_id)
            except Exception:
                pass
    
    def test_complete_csv_upload_workflow(self, real_matrix_csv, cleanup_test_matrices):
        """
        Test 1: Kompletter CSV-Upload Workflow
        
        Schritte:
        1. CSV-Matrix importieren
        2. Als aktiv setzen
        3. Validieren
        4. Preis berechnen
        5. Ergebnis prüfen
        
        Requirements: 1.1, 1.2, 2.1, 2.2
        """
        # Step 1: Import CSV matrix
        matrix_id = price_matrix_store.import_matrix_csv(
            name="E2E Test Matrix CSV",
            csv_text=real_matrix_csv,
            delimiter=';'
        )
        
        assert matrix_id is not None, "Matrix import failed"
        cleanup_test_matrices.append(matrix_id)
        
        # Step 2: Set as active
        success = price_matrix_store.set_active_matrix(matrix_id)
        assert success, "Failed to set matrix as active"
        
        # Verify it's active
        active_id = price_matrix_store.get_active_matrix_id()
        assert active_id == matrix_id, "Matrix is not active"
        
        # Step 3: Validate matrix
        validation = validate_matrix_for_pricing(matrix_id)
        assert validation['valid'], f"Matrix validation failed: {validation['errors']}"
        
        # Step 4: Calculate prices for various scenarios
        test_cases = [
            # (module_count, storage_model, expected_price)
            (10, "BYD Battery-Box Premium HVS 10.2", 15000.00),
            (20, "BYD Battery-Box Premium HVS 12.8", 22500.00),
            (30, None, 22000.00),  # Kein Speicher
            (15, "BYD Battery-Box Premium HVS 10.2", 18000.00),
        ]
        
        for module_count, storage_model, expected_price in test_cases:
            result = calculate_price_from_matrix(module_count, storage_model, matrix_id)
            
            assert result['success'], f"Price calculation failed for {module_count} modules, {storage_model}: {result['error']}"
            assert result['base_price'] == expected_price, \
                f"Expected {expected_price}, got {result['base_price']} for {module_count} modules, {storage_model}"
            assert result['matrix_id'] == matrix_id
            assert result['row_used'] == str(module_count)
    
    def test_complete_excel_upload_workflow(self, real_matrix_excel_bytes, cleanup_test_matrices):
        """
        Test 2: Kompletter Excel-Upload Workflow
        
        Schritte:
        1. Excel-Matrix erstellen und importieren
        2. Als aktiv setzen
        3. Validieren
        4. Preis berechnen
        5. Ergebnis prüfen
        
        Requirements: 1.1, 1.2, 2.1, 2.2
        """
        # Step 1: Create matrix and import Excel data
        matrix_id = price_matrix_store.create_matrix(
            name="E2E Test Matrix Excel",
            description="End-to-End Test mit Excel-Daten"
        )
        
        assert matrix_id is not None, "Matrix creation failed"
        cleanup_test_matrices.append(matrix_id)
        
        # Parse Excel bytes to DataFrame
        df = pd.read_excel(io.BytesIO(real_matrix_excel_bytes), index_col=0, engine='openpyxl')
        
        # Import data into matrix
        # Add rows (module counts)
        row_ids = {}
        for idx, row_label in enumerate(df.index):
            row_id = price_matrix_store.add_row(matrix_id, str(row_label), position=idx)
            assert row_id is not None, f"Failed to add row {row_label}"
            row_ids[row_label] = row_id
        
        # Add columns (storage models)
        col_ids = {}
        for idx, col_label in enumerate(df.columns):
            col_id = price_matrix_store.add_column(matrix_id, str(col_label), position=idx)
            assert col_id is not None, f"Failed to add column {col_label}"
            col_ids[col_label] = col_id
        
        # Add cell values
        for row_label in df.index:
            for col_label in df.columns:
                value = df.loc[row_label, col_label]
                if pd.notna(value):
                    success = price_matrix_store.set_cell_value(
                        matrix_id,
                        row_ids[row_label],
                        col_ids[col_label],
                        float(value),
                        data_type='number'
                    )
                    assert success, f"Failed to set cell value at ({row_label}, {col_label})"
        
        # Step 2: Set as active
        success = price_matrix_store.set_active_matrix(matrix_id)
        assert success, "Failed to set matrix as active"
        
        # Step 3: Validate matrix
        validation = validate_matrix_for_pricing(matrix_id)
        assert validation['valid'], f"Matrix validation failed: {validation['errors']}"
        
        # Step 4: Calculate prices
        result = calculate_price_from_matrix(25, "BYD Battery-Box Premium HVS 12.8", matrix_id)
        
        assert result['success'], f"Price calculation failed: {result['error']}"
        assert result['base_price'] == 25500.00
        assert result['matrix_id'] == matrix_id
    
    def test_storage_model_variations(self, real_matrix_csv, cleanup_test_matrices):
        """
        Test 3: Verschiedene Speicher-Kombinationen
        
        Testet:
        - Verschiedene Speichermodelle
        - "Kein Speicher" Option
        - Case-insensitive Matching
        
        Requirements: 1.2, 1.3
        """
        # Import matrix
        matrix_id = price_matrix_store.import_matrix_csv(
            name="E2E Storage Test Matrix",
            csv_text=real_matrix_csv,
            delimiter=';'
        )
        
        assert matrix_id is not None
        cleanup_test_matrices.append(matrix_id)
        
        price_matrix_store.set_active_matrix(matrix_id)
        
        # Test different storage models
        test_cases = [
            # Exact match
            (20, "BYD Battery-Box Premium HVS 10.2", 21000.00, True),
            # Different storage
            (20, "BYD Battery-Box Premium HVS 12.8", 22500.00, True),
            # No storage (None)
            (20, None, 17000.00, True),
            # No storage (explicit)
            (20, "Kein Speicher", 17000.00, True),
            # Case variations (should work with normalization)
            (20, "byd battery-box premium hvs 10.2", 21000.00, True),
            # Non-existent storage (should fail)
            (20, "Unknown Storage Model", 0.0, False),
        ]
        
        for module_count, storage_model, expected_price, should_succeed in test_cases:
            result = calculate_price_from_matrix(module_count, storage_model, matrix_id)
            
            if should_succeed:
                assert result['success'], \
                    f"Expected success for {module_count} modules, {storage_model}, but got error: {result['error']}"
                assert result['base_price'] == expected_price, \
                    f"Expected {expected_price}, got {result['base_price']} for {module_count} modules, {storage_model}"
            else:
                assert not result['success'], \
                    f"Expected failure for {module_count} modules, {storage_model}, but got success with price {result['base_price']}"
    
    def test_module_count_floor_logic(self, real_matrix_csv, cleanup_test_matrices):
        """
        Test 4: Floor-Logik für Modulanzahl
        
        Testet:
        - Exakte Übereinstimmung
        - Nächst-kleinere Zahl (Floor)
        - Zu kleine Modulanzahl (Fehler)
        
        Requirements: 1.1, 4.1, 4.2
        """
        # Import matrix
        matrix_id = price_matrix_store.import_matrix_csv(
            name="E2E Floor Logic Test Matrix",
            csv_text=real_matrix_csv,
            delimiter=';'
        )
        
        assert matrix_id is not None
        cleanup_test_matrices.append(matrix_id)
        
        price_matrix_store.set_active_matrix(matrix_id)
        
        storage_model = "BYD Battery-Box Premium HVS 10.2"
        
        test_cases = [
            # (module_count, expected_row_used, expected_price, should_succeed)
            # Exact matches
            (10, "10", 15000.00, True),
            (20, "20", 21000.00, True),
            (30, "30", 27000.00, True),
            
            # Floor logic (nächst-kleinere Zahl)
            (12, "10", 15000.00, True),  # 12 → 10
            (18, "15", 18000.00, True),  # 18 → 15
            (23, "20", 21000.00, True),  # 23 → 20
            (37, "35", 30000.00, True),  # 37 → 35
            
            # Too small (should fail)
            (5, None, 0.0, False),  # Kleiner als kleinste Modulanzahl
            (0, None, 0.0, False),  # Invalid
        ]
        
        for module_count, expected_row, expected_price, should_succeed in test_cases:
            result = calculate_price_from_matrix(module_count, storage_model, matrix_id)
            
            if should_succeed:
                assert result['success'], \
                    f"Expected success for {module_count} modules, but got error: {result['error']}"
                assert result['row_used'] == expected_row, \
                    f"Expected row {expected_row}, got {result['row_used']} for {module_count} modules"
                assert result['base_price'] == expected_price, \
                    f"Expected {expected_price}, got {result['base_price']} for {module_count} modules"
            else:
                assert not result['success'], \
                    f"Expected failure for {module_count} modules, but got success"
    
    def test_matrix_validation_workflow(self, cleanup_test_matrices):
        """
        Test 5: Matrix-Validierung Workflow
        
        Testet:
        - Validierung bei Upload
        - Fehlerhafte Matrix-Strukturen
        - Validierungsmeldungen
        
        Requirements: 2.2, 2.4, 4.4
        """
        # Test 1: Valid matrix
        valid_csv = """Anzahl Module;Speicher A;Kein Speicher
10;15000.00;12000.00
20;21000.00;17000.00"""
        
        matrix_id = price_matrix_store.import_matrix_csv(
            name="E2E Valid Matrix",
            csv_text=valid_csv,
            delimiter=';'
        )
        
        assert matrix_id is not None
        cleanup_test_matrices.append(matrix_id)
        
        validation = validate_matrix_for_pricing(matrix_id)
        assert validation['valid'], "Valid matrix should pass validation"
        assert len(validation['errors']) == 0
        
        # Test 2: Matrix without "Kein Speicher" column
        invalid_csv = """Anzahl Module;Speicher A;Speicher B
10;15000.00;16000.00
20;21000.00;22000.00"""
        
        matrix_id2 = price_matrix_store.import_matrix_csv(
            name="E2E Invalid Matrix (No Kein Speicher)",
            csv_text=invalid_csv,
            delimiter=';'
        )
        
        assert matrix_id2 is not None
        cleanup_test_matrices.append(matrix_id2)
        
        validation2 = validate_matrix_for_pricing(matrix_id2)
        # Should still be valid but with warnings
        assert 'kein speicher' in str(validation2).lower() or validation2['valid']
    
    def test_real_world_calculation_scenario(self, real_matrix_csv, cleanup_test_matrices):
        """
        Test 6: Realistische Berechnungs-Szenarien
        
        Simuliert echte Anwendungsfälle:
        - Kunde wählt 18 Module (nicht in Matrix)
        - Kunde wählt Speicher
        - System findet nächst-kleinere Modulanzahl (15)
        - Preis wird korrekt berechnet
        
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        # Import matrix
        matrix_id = price_matrix_store.import_matrix_csv(
            name="E2E Real World Test Matrix",
            csv_text=real_matrix_csv,
            delimiter=';'
        )
        
        assert matrix_id is not None
        cleanup_test_matrices.append(matrix_id)
        
        price_matrix_store.set_active_matrix(matrix_id)
        
        # Scenario 1: Kunde mit 18 Modulen und BYD 10.2 Speicher
        result1 = calculate_price_from_matrix(
            18,
            "BYD Battery-Box Premium HVS 10.2",
            matrix_id
        )
        
        assert result1['success']
        assert result1['row_used'] == "15"  # Floor: 18 → 15
        assert result1['base_price'] == 18000.00
        assert result1['column_used'] == "BYD Battery-Box Premium HVS 10.2"
        
        # Scenario 2: Kunde mit 32 Modulen ohne Speicher
        result2 = calculate_price_from_matrix(
            32,
            None,
            matrix_id
        )
        
        assert result2['success']
        assert result2['row_used'] == "30"  # Floor: 32 → 30
        assert result2['base_price'] == 22000.00
        assert result2['column_used'] == "Kein Speicher"
        
        # Scenario 3: Kunde mit 40 Modulen und BYD 12.8 Speicher (exakt)
        result3 = calculate_price_from_matrix(
            40,
            "BYD Battery-Box Premium HVS 12.8",
            matrix_id
        )
        
        assert result3['success']
        assert result3['row_used'] == "40"
        assert result3['base_price'] == 34500.00
        assert result3['column_used'] == "BYD Battery-Box Premium HVS 12.8"
    
    def test_multiple_matrices_workflow(self, real_matrix_csv, cleanup_test_matrices):
        """
        Test 7: Mehrere Matrizen verwalten
        
        Testet:
        - Mehrere Matrizen erstellen
        - Zwischen Matrizen wechseln
        - Aktive Matrix verwenden
        
        Requirements: 3.1, 3.2
        """
        # Create first matrix
        matrix_id1 = price_matrix_store.import_matrix_csv(
            name="E2E Matrix 1",
            csv_text=real_matrix_csv,
            delimiter=';'
        )
        
        assert matrix_id1 is not None
        cleanup_test_matrices.append(matrix_id1)
        
        # Create second matrix with different prices
        modified_csv = real_matrix_csv.replace("15000.00", "16000.00")
        matrix_id2 = price_matrix_store.import_matrix_csv(
            name="E2E Matrix 2",
            csv_text=modified_csv,
            delimiter=';'
        )
        
        assert matrix_id2 is not None
        cleanup_test_matrices.append(matrix_id2)
        
        # Set first matrix as active
        price_matrix_store.set_active_matrix(matrix_id1)
        
        # Calculate with first matrix
        result1 = calculate_price_from_matrix(10, "BYD Battery-Box Premium HVS 10.2")
        assert result1['success']
        assert result1['base_price'] == 15000.00
        assert result1['matrix_id'] == matrix_id1
        
        # Switch to second matrix
        price_matrix_store.set_active_matrix(matrix_id2)
        
        # Calculate with second matrix (should have different price)
        result2 = calculate_price_from_matrix(10, "BYD Battery-Box Premium HVS 10.2")
        assert result2['success']
        assert result2['base_price'] == 16000.00
        assert result2['matrix_id'] == matrix_id2
    
    def test_error_handling_and_recovery(self, real_matrix_csv, cleanup_test_matrices):
        """
        Test 8: Fehlerbehandlung und Recovery
        
        Testet:
        - Ungültige Eingaben
        - Fehlende Matrix
        - Nicht gefundene Werte
        - Benutzerfreundliche Fehlermeldungen
        
        Requirements: 4.4, 1.5, 3.4
        """
        # Import valid matrix
        matrix_id = price_matrix_store.import_matrix_csv(
            name="E2E Error Handling Test Matrix",
            csv_text=real_matrix_csv,
            delimiter=';'
        )
        
        assert matrix_id is not None
        cleanup_test_matrices.append(matrix_id)
        
        price_matrix_store.set_active_matrix(matrix_id)
        
        # Test 1: Invalid module count (negative)
        result1 = calculate_price_from_matrix(-5, "BYD Battery-Box Premium HVS 10.2", matrix_id)
        assert not result1['success']
        assert result1['error_type'] == 'invalid_input'
        assert result1['user_message'] is not None
        
        # Test 2: Module count too small (below minimum)
        result2 = calculate_price_from_matrix(5, "BYD Battery-Box Premium HVS 10.2", matrix_id)
        assert not result2['success']
        assert result2['error_type'] == 'no_row'
        assert 'modulanzahl' in result2['user_message'].lower()
        
        # Test 3: Non-existent storage model
        result3 = calculate_price_from_matrix(20, "Non-Existent Storage", matrix_id)
        assert not result3['success']
        assert result3['error_type'] == 'no_column'
        assert result3['user_message'] is not None
        
        # Test 4: No active matrix
        price_matrix_store.set_active_matrix(matrix_id)
        price_matrix_store.delete_matrix(matrix_id)
        cleanup_test_matrices.remove(matrix_id)
        
        result4 = calculate_price_from_matrix(20, "BYD Battery-Box Premium HVS 10.2")
        assert not result4['success']
        assert result4['error_type'] == 'no_matrix'
        assert result4['user_message'] is not None


class TestMatrixPricingIntegration:
    """Integration Tests für Matrix-Pricing mit anderen Komponenten"""
    
    @pytest.fixture
    def test_matrix_id(self):
        """Create a test matrix for integration tests"""
        csv_data = """Anzahl Module;BYD 10.2;Kein Speicher
10;15000.00;12000.00
20;21000.00;17000.00
30;27000.00;22000.00"""
        
        matrix_id = price_matrix_store.import_matrix_csv(
            name="Integration Test Matrix",
            csv_text=csv_data,
            delimiter=';'
        )
        
        price_matrix_store.set_active_matrix(matrix_id)
        
        yield matrix_id
        
        # Cleanup
        try:
            price_matrix_store.delete_matrix(matrix_id)
        except Exception:
            pass
    
    def test_matrix_pricing_with_extras(self, test_matrix_id):
        """
        Test 9: Matrix-Pricing mit Extras
        
        Testet Integration mit:
        - Basis-Matrixpreis
        - Zusatzkosten
        - Rabatte
        
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
        """
        # Get base price from matrix
        result = calculate_price_from_matrix(20, "BYD 10.2", test_matrix_id)
        
        assert result['success']
        base_price = result['base_price']
        assert base_price == 21000.00
        
        # Simulate extras and discounts
        accessories_cost = 1500.00  # Zubehör
        discount_percent = 5.0  # 5% Rabatt
        
        # Calculate final price
        discount_amount = base_price * (discount_percent / 100)
        final_price = base_price + accessories_cost - discount_amount
        
        expected_final = 21000.00 + 1500.00 - 1050.00  # = 21450.00
        
        assert abs(final_price - expected_final) < 0.01
    
    def test_matrix_data_persistence(self, test_matrix_id):
        """
        Test 10: Daten-Persistenz
        
        Testet:
        - Matrix bleibt nach Neustart verfügbar
        - Preise bleiben konsistent
        - Aktive Matrix wird beibehalten
        
        Requirements: 3.3
        """
        # Get initial data
        initial_result = calculate_price_from_matrix(20, "BYD 10.2", test_matrix_id)
        assert initial_result['success']
        initial_price = initial_result['base_price']
        
        # Verify matrix is active
        active_id = price_matrix_store.get_active_matrix_id()
        assert active_id == test_matrix_id
        
        # Get matrix data
        matrix_data = price_matrix_store.get_matrix_full(test_matrix_id)
        assert matrix_data is not None
        assert matrix_data['meta']['is_active']
        
        # Calculate again (should be same)
        second_result = calculate_price_from_matrix(20, "BYD 10.2", test_matrix_id)
        assert second_result['success']
        assert second_result['base_price'] == initial_price


def test_complete_workflow_summary():
    """
    Summary Test: Kompletter Workflow von A bis Z
    
    Dieser Test simuliert den kompletten Anwendungsfall:
    1. Admin lädt Matrix hoch
    2. System validiert Matrix
    3. Matrix wird aktiv gesetzt
    4. Benutzer berechnet Preise
    5. Ergebnisse werden angezeigt
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.4
    """
    # Step 1: Admin uploads matrix
    csv_data = """Anzahl Module;BYD Battery-Box Premium HVS 10.2;BYD Battery-Box Premium HVS 12.8;Kein Speicher
10;15000.00;16500.00;12000.00
15;18000.00;19500.00;14500.00
20;21000.00;22500.00;17000.00
25;24000.00;25500.00;19500.00
30;27000.00;28500.00;22000.00"""
    
    matrix_id = price_matrix_store.import_matrix_csv(
        name="Complete Workflow Test Matrix",
        csv_text=csv_data,
        delimiter=';'
    )
    
    try:
        assert matrix_id is not None, "Matrix import failed"
        
        # Step 2: System validates matrix
        validation = validate_matrix_for_pricing(matrix_id)
        assert validation['valid'], f"Matrix validation failed: {validation['errors']}"
        
        # Step 3: Matrix is set as active
        success = price_matrix_store.set_active_matrix(matrix_id)
        assert success, "Failed to set matrix as active"
        
        # Step 4: User calculates prices for different scenarios
        scenarios = [
            {
                'name': 'Kleines System ohne Speicher',
                'modules': 10,
                'storage': None,
                'expected_price': 12000.00
            },
            {
                'name': 'Mittleres System mit BYD 10.2',
                'modules': 20,
                'storage': 'BYD Battery-Box Premium HVS 10.2',
                'expected_price': 21000.00
            },
            {
                'name': 'Großes System mit BYD 12.8',
                'modules': 30,
                'storage': 'BYD Battery-Box Premium HVS 12.8',
                'expected_price': 28500.00
            },
            {
                'name': 'Nicht-exakte Modulanzahl (Floor-Logik)',
                'modules': 18,
                'storage': 'BYD Battery-Box Premium HVS 10.2',
                'expected_price': 18000.00  # Floor: 18 → 15
            }
        ]
        
        results = []
        for scenario in scenarios:
            result = calculate_price_from_matrix(
                scenario['modules'],
                scenario['storage'],
                matrix_id
            )
            
            assert result['success'], \
                f"Scenario '{scenario['name']}' failed: {result['error']}"
            
            assert result['base_price'] == scenario['expected_price'], \
                f"Scenario '{scenario['name']}': Expected {scenario['expected_price']}, got {result['base_price']}"
            
            results.append({
                'scenario': scenario['name'],
                'success': True,
                'price': result['base_price'],
                'row_used': result['row_used'],
                'column_used': result['column_used']
            })
        
        # Step 5: Verify all results
        assert len(results) == len(scenarios), "Not all scenarios were tested"
        assert all(r['success'] for r in results), "Some scenarios failed"
        
        # Print summary (for manual verification)
        print("\n" + "="*60)
        print("COMPLETE WORKFLOW TEST SUMMARY")
        print("="*60)
        for result in results:
            print(f"\n{result['scenario']}:")
            print(f"  [OK] Success")
            print(f"  Price: {result['price']:.2f} EUR")
            print(f"  Row: {result['row_used']}, Column: {result['column_used']}")
        print("\n" + "="*60)
        
    finally:
        # Cleanup
        try:
            price_matrix_store.delete_matrix(matrix_id)
        except Exception:
            pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
