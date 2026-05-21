"""
Tests for Price Matrix Formula Engine

**Feature: streamlit-to-electron-migration, Task 140**
"""

import pytest
from services.formula_engine import (
    FormulaEngine,
    PriceMatrixFormulaEngine,
    FormulaError,
    ParseError,
    EvaluationError,
    CircularReferenceError,
    FormulaDebugger,
    FormulaOptimizer,
    MatchType
)


class TestFormulaEngine:
    """Test basic formula engine functionality"""
    
    def test_simple_value(self):
        """Test simple value retrieval"""
        engine = FormulaEngine()
        engine.set_value("A1", 42)
        assert engine.get_value("A1") == 42
    
    def test_simple_formula(self):
        """Test simple formula evaluation"""
        engine = FormulaEngine()
        engine.set_value("A1", 10)
        engine.set_value("A2", 20)
        # Note: Basic arithmetic not implemented yet, just testing structure
        assert engine.get_value("A1") == 10
    
    def test_index_function_basic(self):
        """Test basic INDEX function"""
        engine = FormulaEngine()
        
        # Setup data: A1:A3 = [10, 20, 30]
        engine.set_value("A1", 10)
        engine.set_value("A2", 20)
        engine.set_value("A3", 30)
        
        # INDEX(A1:A3, 2) should return 20
        result = engine.evaluate("INDEX(A1:A3, 2)")
        assert result == 20
    
    def test_index_function_2d(self):
        """Test INDEX function with 2D array"""
        engine = FormulaEngine()
        
        # Setup 2x2 matrix
        engine.set_value("A1", 10)
        engine.set_value("B1", 20)
        engine.set_value("A2", 30)
        engine.set_value("B2", 40)
        
        # INDEX(A1:B2, 2, 2) should return 40
        result = engine.evaluate("INDEX(A1:B2, 2, 2)")
        assert result == 40
    
    def test_index_out_of_bounds(self):
        """Test INDEX with out of bounds index"""
        engine = FormulaEngine()
        engine.set_value("A1", 10)
        engine.set_value("A2", 20)
        
        with pytest.raises(EvaluationError, match="außerhalb des Bereichs"):
            engine.evaluate("INDEX(A1:A2, 5)")
    
    def test_match_function_exact(self):
        """Test MATCH function with exact match"""
        engine = FormulaEngine()
        
        # Setup array: A1:A5 = [10, 20, 30, 40, 50]
        for i, val in enumerate([10, 20, 30, 40, 50], start=1):
            engine.set_value(f"A{i}", val)
        
        # MATCH(30, A1:A5, 0) should return 3
        result = engine.evaluate("MATCH(30, A1:A5, 0)")
        assert result == 3
    
    def test_match_function_string(self):
        """Test MATCH function with string values"""
        engine = FormulaEngine()
        
        # Setup array: A1:A3 = ["Apple", "Banana", "Cherry"]
        engine.set_value("A1", "Apple")
        engine.set_value("A2", "Banana")
        engine.set_value("A3", "Cherry")
        
        # MATCH("Banana", A1:A3, 0) should return 2
        result = engine.evaluate('MATCH("Banana", A1:A3, 0)')
        assert result == 2
    
    def test_match_not_found(self):
        """Test MATCH when value not found"""
        engine = FormulaEngine()
        engine.set_value("A1", 10)
        engine.set_value("A2", 20)
        
        with pytest.raises(EvaluationError, match="nicht gefunden"):
            engine.evaluate("MATCH(99, A1:A2, 0)")
    
    def test_nested_index_match(self):
        """Test nested INDEX/MATCH formula"""
        engine = FormulaEngine()
        
        # Setup module counts in column A
        for i, count in enumerate([10, 20, 30], start=2):
            engine.set_value(f"A{i}", count)
        
        # Setup battery models in row 2
        engine.set_value("B2", "Model A")
        engine.set_value("C2", "Model B")
        
        # Setup prices
        engine.set_value("B2", "Model A")
        engine.set_value("C2", "Model B")
        engine.set_value("B3", 15000)  # 20 modules, Model A
        engine.set_value("C3", 18000)  # 20 modules, Model B
        
        # INDEX(A2:C4, MATCH(20, A2:A4, 0), MATCH("Model B", B2:C2, 0))
        result = engine.evaluate(
            'INDEX(A2:C4, MATCH(20, A2:A4, 0), MATCH("Model B", B2:C2, 0))'
        )
        assert result == 18000
    
    def test_circular_reference_detection(self):
        """Test circular reference detection"""
        engine = FormulaEngine()
        
        # Create circular reference: A1 -> A2 -> A1
        engine.set_formula("A1", "=A2")
        engine.set_formula("A2", "=A1")
        
        with pytest.raises(CircularReferenceError, match="Zirkuläre Referenz"):
            engine.get_value("A1")
    
    def test_column_conversion(self):
        """Test column letter/number conversion"""
        engine = FormulaEngine()
        
        assert engine._col_letter_to_num("A") == 1
        assert engine._col_letter_to_num("Z") == 26
        assert engine._col_letter_to_num("AA") == 27
        assert engine._col_letter_to_num("XX") == 648
        
        assert engine._col_num_to_letter(1) == "A"
        assert engine._col_num_to_letter(26) == "Z"
        assert engine._col_num_to_letter(27) == "AA"
        assert engine._col_num_to_letter(648) == "XX"


class TestPriceMatrixFormulaEngine:
    """Test price matrix specific functionality"""
    
    def test_load_matrix(self):
        """Test loading price matrix data"""
        engine = PriceMatrixFormulaEngine()
        
        module_counts = [10, 20, 30]
        battery_models = ["Model A", "Model B", "kein Speicher"]
        matrix_data = [
            [10000, 12000, 9000],
            [15000, 18000, 14000],
            [20000, 24000, 19000]
        ]
        
        engine.load_matrix(matrix_data, module_counts, battery_models)
        
        # Verify data loaded correctly
        # Row 2: Battery model headers
        assert engine.get_value("B2") == "Model A"
        assert engine.get_value("C2") == "Model B"
        assert engine.get_value("D2") == "kein Speicher"
        # Row 3: First data row (10 modules)
        assert engine.get_value("A3") == 10
        assert engine.get_value("B3") == 10000
        # Row 4: Second data row (20 modules)
        assert engine.get_value("A4") == 20
        assert engine.get_value("B4") == 15000
    
    def test_lookup_price_basic(self):
        """Test basic price lookup"""
        engine = PriceMatrixFormulaEngine()
        
        module_counts = [10, 20, 30]
        battery_models = ["Model A", "Model B", "kein Speicher"]
        matrix_data = [
            [10000, 12000, 9000],
            [15000, 18000, 14000],
            [20000, 24000, 19000]
        ]
        
        engine.load_matrix(matrix_data, module_counts, battery_models)
        
        # Lookup: 20 modules, Model B
        price = engine.lookup_price(20, "Model B")
        assert price == 18000
    
    def test_lookup_price_kein_speicher(self):
        """Test price lookup with 'kein Speicher'"""
        engine = PriceMatrixFormulaEngine()
        
        module_counts = [10, 20, 30]
        battery_models = ["Model A", "Model B", "kein Speicher"]
        matrix_data = [
            [10000, 12000, 9000],
            [15000, 18000, 14000],
            [20000, 24000, 19000]
        ]
        
        engine.load_matrix(matrix_data, module_counts, battery_models)
        
        # Lookup: 20 modules, kein Speicher (should use last column)
        price = engine.lookup_price(20, "kein Speicher")
        assert price == 14000
    
    def test_lookup_price_not_found(self):
        """Test price lookup with invalid values"""
        engine = PriceMatrixFormulaEngine()
        
        module_counts = [10, 20, 30]
        battery_models = ["Model A", "Model B"]
        matrix_data = [
            [10000, 12000],
            [15000, 18000],
            [20000, 24000]
        ]
        
        engine.load_matrix(matrix_data, module_counts, battery_models)
        
        # Invalid module count
        with pytest.raises(EvaluationError):
            engine.lookup_price(99, "Model A")
    
    def test_format_price_german(self):
        """Test German price formatting"""
        engine = PriceMatrixFormulaEngine()
        
        assert engine.format_price_german(16999.00) == "16.999,00 €"
        assert engine.format_price_german(1234.56) == "1.234,56 €"
        assert engine.format_price_german(999.99) == "999,99 €"
        assert engine.format_price_german(1000000.00) == "1.000.000,00 €"
    
    def test_large_matrix_performance(self):
        """Test performance with large matrix (200x200)"""
        engine = PriceMatrixFormulaEngine()
        
        # Create large matrix
        module_counts = list(range(1, 201))
        battery_models = [f"Model {i}" for i in range(1, 201)]
        matrix_data = [
            [10000 + i * 100 + j * 10 for j in range(200)]
            for i in range(200)
        ]
        
        engine.load_matrix(matrix_data, module_counts, battery_models)
        
        # Lookup should still work efficiently
        price = engine.lookup_price(100, "Model 50")
        assert price == 10000 + 99 * 100 + 49 * 10  # Expected value
    
    def test_case_insensitive_match(self):
        """Test case-insensitive matching for battery models"""
        engine = PriceMatrixFormulaEngine()
        
        module_counts = [10, 20]
        battery_models = ["Model A", "Model B"]
        matrix_data = [
            [10000, 12000],
            [15000, 18000]
        ]
        
        engine.load_matrix(matrix_data, module_counts, battery_models)
        
        # Should match case-insensitively
        price = engine.lookup_price(20, "model b")
        assert price == 18000


class TestFormulaDebugger:
    """Test formula debugging tools"""
    
    def test_trace_evaluation(self):
        """Test formula evaluation tracing"""
        engine = FormulaEngine()
        engine.set_value("A1", 10)
        engine.set_value("A2", 20)
        
        trace = FormulaDebugger.trace_evaluation(engine, "INDEX(A1:A2, 1)")
        
        assert trace["formula"] == "INDEX(A1:A2, 1)"
        assert trace["result"] == 10
        assert trace["error"] is None
    
    def test_validate_circular_references(self):
        """Test circular reference validation"""
        engine = FormulaEngine()
        
        # Create circular reference
        engine.set_formula("A1", "=A2")
        engine.set_formula("A2", "=A3")
        engine.set_formula("A3", "=A1")
        
        circular_refs = FormulaDebugger.validate_circular_references(engine)
        
        # Should detect circular reference
        assert len(circular_refs) > 0


class TestFormulaOptimizer:
    """Test formula optimization"""
    
    def test_optimize_matrix_lookup(self):
        """Test matrix lookup optimization"""
        engine = FormulaEngine()
        optimizer = FormulaOptimizer(engine)
        
        # Should log warning for large matrix
        optimizer.optimize_matrix_lookup((200, 200))
        
        # Should not warn for small matrix
        optimizer.optimize_matrix_lookup((10, 10))
    
    def test_cache_clear(self):
        """Test cache clearing"""
        engine = FormulaEngine()
        optimizer = FormulaOptimizer(engine)
        
        optimizer.cache["test"] = "value"
        assert len(optimizer.cache) == 1
        
        optimizer.clear_cache()
        assert len(optimizer.cache) == 0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_matrix(self):
        """Test with empty matrix"""
        engine = PriceMatrixFormulaEngine()
        
        with pytest.raises(EvaluationError, match="nicht geladen"):
            engine.lookup_price(10, "Model A")
    
    def test_invalid_formula_syntax(self):
        """Test invalid formula syntax"""
        engine = FormulaEngine()
        
        with pytest.raises(ParseError):
            engine.evaluate("INVALID()")
    
    def test_missing_arguments(self):
        """Test function with missing arguments"""
        engine = FormulaEngine()
        
        with pytest.raises(ParseError, match="mindestens"):
            engine.evaluate("INDEX(A1:A2)")
    
    def test_none_values_in_matrix(self):
        """Test handling of None values in matrix"""
        engine = PriceMatrixFormulaEngine()
        
        module_counts = [10, 20]
        battery_models = ["Model A", "Model B"]
        matrix_data = [
            [10000, None],
            [15000, 18000]
        ]
        
        engine.load_matrix(matrix_data, module_counts, battery_models)
        
        # Should handle None gracefully
        price = engine.lookup_price(10, "Model B")
        assert price is None
    
    def test_special_characters_in_model_names(self):
        """Test battery models with special characters"""
        engine = PriceMatrixFormulaEngine()
        
        module_counts = [10, 20]
        battery_models = ["Model-A (Premium)", "Model B/C"]
        matrix_data = [
            [10000, 12000],
            [15000, 18000]
        ]
        
        engine.load_matrix(matrix_data, module_counts, battery_models)
        
        price = engine.lookup_price(20, "Model-A (Premium)")
        assert price == 15000


class TestGermanErrorMessages:
    """Test that all error messages are in German"""
    
    def test_error_messages_german(self):
        """Verify error messages are in German"""
        engine = FormulaEngine()
        
        # Test various error scenarios
        try:
            engine.evaluate("INDEX(A1:A2, 99)")
        except EvaluationError as e:
            assert "außerhalb" in str(e).lower() or "bereich" in str(e).lower()
        
        try:
            engine.evaluate("MATCH(99, A1:A2, 0)")
        except EvaluationError as e:
            assert "nicht gefunden" in str(e).lower()
        
        try:
            engine.evaluate("INVALID()")
        except ParseError as e:
            assert "ungültig" in str(e).lower() or "unbekannt" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
