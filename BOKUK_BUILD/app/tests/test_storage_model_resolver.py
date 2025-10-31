"""
Tests for StorageModelResolver functionality.

This module tests the storage ID to model name resolution logic
including fallback scenarios and edge cases.
"""

from typing import Any

from storage_model_resolver import StorageModelResolver, resolve_storage_model_name


class TestStorageModelResolver:
    """Test cases for StorageModelResolver class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.resolver = StorageModelResolver()

        # Mock product database
        self.mock_products = {
            1: {"id": 1, "model_name": "Tesla Powerwall 2", "category": "Batteriespeicher"},
            2: {"id": 2, "model_name": "BYD Battery-Box Premium HVS", "category": "Batteriespeicher"},
            3: {"id": 3, "model_name": "Sonnen eco 10", "category": "Batteriespeicher"},
            # Empty model name
            4: {"id": 4, "model_name": "", "category": "Batteriespeicher"},
            # Missing model_name key
            5: {"id": 5, "category": "Batteriespeicher"},
            # Whitespace
            6: {"id": 6, "model_name": "   Fronius Solar Battery   ", "category": "Batteriespeicher"},
        }

    def mock_get_product_func(self, product_id: int) -> dict[str, Any] | None:
        """Mock function to simulate product database lookup."""
        return self.mock_products.get(product_id)

    def mock_get_product_func_with_error(
            self, product_id: int) -> dict[str, Any] | None:
        """Mock function that raises an error."""
        raise Exception("Database connection error")

    def test_resolve_storage_name_include_storage_false(self):
        """Test that include_storage=False always returns 'Ohne Speicher'."""
        result = self.resolver.resolve_storage_name(
            "1", False, self.mock_get_product_func)
        assert result == "Ohne Speicher"

        result = self.resolver.resolve_storage_name(
            "999", False, self.mock_get_product_func)
        assert result == "Ohne Speicher"

        result = self.resolver.resolve_storage_name(
            None, False, self.mock_get_product_func)
        assert result == "Ohne Speicher"

    def test_resolve_storage_name_no_storage_id(self):
        """Test that missing storage_id returns 'Ohne Speicher'."""
        result = self.resolver.resolve_storage_name(
            None, True, self.mock_get_product_func)
        assert result == "Ohne Speicher"

        result = self.resolver.resolve_storage_name(
            "", True, self.mock_get_product_func)
        assert result == "Ohne Speicher"

        result = self.resolver.resolve_storage_name(
            "   ", True, self.mock_get_product_func)
        assert result == "Ohne Speicher"

    def test_resolve_storage_name_invalid_id_format(self):
        """Test that invalid storage_id format returns 'Ohne Speicher'."""
        result = self.resolver.resolve_storage_name(
            "abc", True, self.mock_get_product_func)
        assert result == "Ohne Speicher"

        result = self.resolver.resolve_storage_name(
            "1.5", True, self.mock_get_product_func)
        assert result == "Ohne Speicher"

        result = self.resolver.resolve_storage_name(
            "1a", True, self.mock_get_product_func)
        assert result == "Ohne Speicher"

    def test_resolve_storage_name_valid_product(self):
        """Test successful resolution of valid storage products."""
        result = self.resolver.resolve_storage_name(
            "1", True, self.mock_get_product_func)
        assert result == "Tesla Powerwall 2"

        result = self.resolver.resolve_storage_name(
            "2", True, self.mock_get_product_func)
        assert result == "BYD Battery-Box Premium HVS"

        result = self.resolver.resolve_storage_name(
            "3", True, self.mock_get_product_func)
        assert result == "Sonnen eco 10"

    def test_resolve_storage_name_product_not_found(self):
        """Test that non-existent product ID returns 'Ohne Speicher'."""
        result = self.resolver.resolve_storage_name(
            "999", True, self.mock_get_product_func)
        assert result == "Ohne Speicher"

    def test_resolve_storage_name_empty_model_name(self):
        """Test that empty model_name returns 'Ohne Speicher'."""
        result = self.resolver.resolve_storage_name(
            "4", True, self.mock_get_product_func)
        assert result == "Ohne Speicher"

    def test_resolve_storage_name_missing_model_name_key(self):
        """Test that missing model_name key returns 'Ohne Speicher'."""
        result = self.resolver.resolve_storage_name(
            "5", True, self.mock_get_product_func)
        assert result == "Ohne Speicher"

    def test_resolve_storage_name_whitespace_trimming(self):
        """Test that model names with whitespace are properly trimmed."""
        result = self.resolver.resolve_storage_name(
            "6", True, self.mock_get_product_func)
        assert result == "Fronius Solar Battery"

    def test_resolve_storage_name_database_error(self):
        """Test that database errors are handled gracefully."""
        result = self.resolver.resolve_storage_name(
            "1", True, self.mock_get_product_func_with_error)
        assert result == "Ohne Speicher"

    def test_resolve_storage_name_caching(self):
        """Test that results are properly cached."""
        # Clear cache first to ensure clean state
        self.resolver.clear_cache()

        # First call should hit the database
        result1 = self.resolver.resolve_storage_name(
            "1", True, self.mock_get_product_func)
        assert result1 == "Tesla Powerwall 2"

        # Second call should use cache (we can verify by checking cache stats)
        result2 = self.resolver.resolve_storage_name(
            "1", True, self.mock_get_product_func)
        assert result2 == "Tesla Powerwall 2"

        # Check cache stats
        stats = self.resolver.get_cache_stats()
        assert stats["cache_size"] == 1
        assert "storage_1" in stats["cached_items"]

    def test_normalize_storage_name(self):
        """Test storage name normalization."""
        # Normal case
        result = self.resolver.normalize_storage_name("Tesla Powerwall 2")
        assert result == "Tesla Powerwall 2"

        # Whitespace trimming
        result = self.resolver.normalize_storage_name("  Tesla Powerwall 2  ")
        assert result == "Tesla Powerwall 2"

        # Empty/None cases
        result = self.resolver.normalize_storage_name("")
        assert result == "Ohne Speicher"

        result = self.resolver.normalize_storage_name(None)
        assert result == "Ohne Speicher"

        # No storage variants
        no_storage_cases = [
            "ohne speicher", "OHNE SPEICHER", "Ohne Speicher",
            "kein speicher", "no storage", "ohne", "none", "null"
        ]

        for case in no_storage_cases:
            result = self.resolver.normalize_storage_name(case)
            assert result == "Ohne Speicher", f"Failed for case: {case}"

    def test_validate_storage_name_in_matrix(self):
        """Test storage name validation against matrix columns."""
        available_models = [
            "Tesla Powerwall 2",
            "BYD Battery-Box Premium HVS",
            "Sonnen eco 10",
            "Fronius Solar Battery"
        ]

        # Exact match (case-insensitive)
        result, is_exact = self.resolver.validate_storage_name_in_matrix(
            "Tesla Powerwall 2", available_models
        )
        assert result == "Tesla Powerwall 2"
        assert is_exact

        # Case-insensitive exact match
        result, is_exact = self.resolver.validate_storage_name_in_matrix(
            "tesla powerwall 2", available_models
        )
        assert result == "Tesla Powerwall 2"
        assert is_exact

        # Partial match
        result, is_exact = self.resolver.validate_storage_name_in_matrix(
            "Tesla", available_models
        )
        assert result == "Tesla Powerwall 2"
        assert is_exact == False

        # No match - fallback to "Ohne Speicher"
        result, is_exact = self.resolver.validate_storage_name_in_matrix(
            "Unknown Battery", available_models
        )
        assert result == "Ohne Speicher"
        assert is_exact == False

        # Empty input
        result, is_exact = self.resolver.validate_storage_name_in_matrix(
            "", available_models
        )
        assert result == "Ohne Speicher"
        assert is_exact == False

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Add something to cache
        self.resolver.resolve_storage_name(
            "1", True, self.mock_get_product_func)

        # Verify cache has content
        stats = self.resolver.get_cache_stats()
        assert stats["cache_size"] > 0

        # Clear cache
        self.resolver.clear_cache()

        # Verify cache is empty
        stats = self.resolver.get_cache_stats()
        assert stats["cache_size"] == 0
        assert len(stats["cached_items"]) == 0

    def test_convenience_function(self):
        """Test the convenience function."""
        result = resolve_storage_model_name(
            "1", True, self.mock_get_product_func)
        assert result == "Tesla Powerwall 2"

        result = resolve_storage_model_name(
            "1", False, self.mock_get_product_func)
        assert result == "Ohne Speicher"


class TestStorageModelResolverIntegration:
    """Integration tests with real-world scenarios."""

    def test_real_world_scenario_with_storage(self):
        """Test a complete real-world scenario with storage."""
        resolver = StorageModelResolver()

        # Mock a realistic product database response
        def get_product_realistic(product_id: int) -> dict[str, Any] | None:
            products = {
                101: {
                    "id": 101,
                    "model_name": "Tesla Powerwall 2",
                    "category": "Batteriespeicher",
                    "storage_power_kw": 13.5,
                    "price_euro": 8500.0
                }
            }
            return products.get(product_id)

        # Test successful resolution
        result = resolver.resolve_storage_name(
            "101", True, get_product_realistic)
        assert result == "Tesla Powerwall 2"

    def test_real_world_scenario_without_storage(self):
        """Test a complete real-world scenario without storage."""
        resolver = StorageModelResolver()

        def get_product_realistic(product_id: int) -> dict[str, Any] | None:
            return {"id": product_id, "model_name": "Some Battery"}

        # Test with include_storage=False
        result = resolver.resolve_storage_name(
            "101", False, get_product_realistic)
        assert result == "Ohne Speicher"

    def test_edge_case_numeric_string_ids(self):
        """Test with various numeric string formats."""
        resolver = StorageModelResolver()

        def get_product_numeric(product_id: int) -> dict[str, Any] | None:
            return {"id": product_id, "model_name": f"Battery {product_id}"}

        # Test different numeric string formats
        test_cases = [
            ("1", "Battery 1"),
            ("01", "Battery 1"),  # Leading zero
            ("123", "Battery 123"),
        ]

        for storage_id, expected_name in test_cases:
            result = resolver.resolve_storage_name(
                storage_id, True, get_product_numeric)
            assert result == expected_name


if __name__ == "__main__":
    # Run basic tests if executed directly
    print("Running StorageModelResolver tests...")

    test_instance = TestStorageModelResolver()
    test_instance.setup_method()

    # Test basic functionality
    print("✓ Testing basic resolution...")
    test_instance.test_resolve_storage_name_valid_product()

    print("✓ Testing fallback scenarios...")
    test_instance.test_resolve_storage_name_include_storage_false()
    test_instance.test_resolve_storage_name_no_storage_id()

    print("✓ Testing error handling...")
    test_instance.test_resolve_storage_name_invalid_id_format()
    test_instance.test_resolve_storage_name_product_not_found()

    print("✓ Testing normalization...")
    test_instance.test_normalize_storage_name()

    print("✓ Testing validation...")
    test_instance.test_validate_storage_name_in_matrix()

    print("✓ Testing caching...")
    test_instance.test_resolve_storage_name_caching()

    print("\nAll tests passed! ✅")
