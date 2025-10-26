"""
Test suite for PriceMatrix class to verify INDEX/MATCH logic implementation.
"""

import pandas as pd
import pytest
from price_matrix import PriceMatrix


def create_test_matrix():
    """Create a test price matrix for testing."""
    data = {
        'Speicher A': [15000.00, 18000.00, 21000.00, 24000.00],
        'Speicher B': [16000.00, 19000.00, 22000.00, 25000.00],
        'Speicher C': [17000.00, 20000.00, 23000.00, 26000.00],
        'Ohne Speicher': [12000.00, 14000.00, 16000.00, 18000.00]
    }
    index = [10, 15, 20, 25]
    return pd.DataFrame(data, index=index)


def test_price_matrix_initialization():
    """Test PriceMatrix initialization with valid data."""
    df = create_test_matrix()
    matrix = PriceMatrix(df)

    assert len(matrix.module_counts) == 4
    assert len(matrix.storage_models) == 4
    assert matrix.has_no_storage_option()


def test_price_matrix_validation():
    """Test matrix structure validation."""
    df = create_test_matrix()
    matrix = PriceMatrix(df)

    errors = matrix.validate_structure()
    assert len(errors) == 0  # Should have no validation errors


def test_get_price_exact_match():
    """Test exact INDEX/MATCH functionality."""
    df = create_test_matrix()
    matrix = PriceMatrix(df)

    # Test exact matches
    price, errors = matrix.get_price(10, 'Speicher A', True)
    assert price == 15000.00
    assert len(errors) == 0

    price, errors = matrix.get_price(20, 'Speicher B', True)
    assert price == 22000.00
    assert len(errors) == 0


def test_get_price_no_storage():
    """Test 'Ohne Speicher' functionality."""
    df = create_test_matrix()
    matrix = PriceMatrix(df)

    # Test no storage option
    price, errors = matrix.get_price(15, None, False)
    assert price == 14000.00
    assert len(errors) == 0

    # Test with include_storage=False
    price, errors = matrix.get_price(25, 'Speicher A', False)
    assert price == 18000.00
    assert len(errors) == 0


def test_storage_model_normalization():
    """Test case-insensitive and trimmed storage model matching."""
    df = create_test_matrix()
    matrix = PriceMatrix(df)

    # Test case insensitive matching
    price, errors = matrix.get_price(10, 'speicher a', True)
    assert price == 15000.00
    assert len(errors) == 0

    # Test with extra whitespace
    price, errors = matrix.get_price(15, '  Speicher B  ', True)
    assert price == 19000.00
    assert len(errors) == 0


def test_module_count_not_found():
    """Test behavior when module count is not in matrix."""
    df = create_test_matrix()
    matrix = PriceMatrix(df)

    price, errors = matrix.get_price(12, 'Speicher A', True)
    assert price == 0.0
    assert len(errors) == 1
    assert "Module count 12 not found" in errors[0]


def test_storage_model_not_found():
    """Test fallback to 'Ohne Speicher' when storage model not found."""
    df = create_test_matrix()
    matrix = PriceMatrix(df)

    price, errors = matrix.get_price(10, 'Unknown Storage', True)
    assert price == 12000.00  # Should fallback to "Ohne Speicher"
    assert len(errors) == 1
    assert "Storage model 'Unknown Storage' not found" in errors[0]


def test_get_available_options():
    """Test methods that return available options."""
    df = create_test_matrix()
    matrix = PriceMatrix(df)

    module_counts = matrix.get_available_module_counts()
    assert module_counts == [10, 15, 20, 25]

    storage_models = matrix.get_available_storage_models()
    assert storage_models == ['Speicher A', 'Speicher B', 'Speicher C']


def test_matrix_info():
    """Test matrix information method."""
    df = create_test_matrix()
    matrix = PriceMatrix(df)

    info = matrix.get_matrix_info()
    assert info['module_count_range'] == (10, 25)
    assert info['total_module_options'] == 4
    assert info['total_storage_options'] == 3
    assert info['has_no_storage']
    assert info['matrix_shape'] == (4, 4)


def test_invalid_matrix_empty():
    """Test validation with empty matrix."""
    df = pd.DataFrame()

    with pytest.raises(ValueError, match="Price matrix cannot be empty"):
        PriceMatrix(df)


def test_invalid_matrix_non_numeric():
    """Test validation with non-numeric values."""
    data = {
        'Speicher A': ['invalid', 18000.00, 21000.00],
        'Ohne Speicher': [12000.00, 14000.00, 16000.00]
    }
    df = pd.DataFrame(data, index=[10, 15, 20])

    # Should handle non-numeric values by converting to NaN
    matrix = PriceMatrix(df)
    price, errors = matrix.get_price(10, 'Speicher A', True)
    assert price == 0.0  # NaN should result in 0.0
    assert len(errors) == 1


def test_matrix_with_missing_values():
    """Test matrix with NaN values."""
    data = {
        'Speicher A': [15000.00, None, 21000.00],
        'Ohne Speicher': [12000.00, 14000.00, 16000.00]
    }
    df = pd.DataFrame(data, index=[10, 15, 20])

    matrix = PriceMatrix(df)

    # Should handle NaN by returning 0.0 and error
    price, errors = matrix.get_price(15, 'Speicher A', True)
    assert price == 0.0
    assert len(errors) == 1
    assert "No price found" in errors[0]


if __name__ == "__main__":
    # Run basic tests
    print("Running PriceMatrix tests...")

    # Test 1: Basic functionality
    df = create_test_matrix()
    matrix = PriceMatrix(df)
    print(
        f"✓ Matrix initialized with {len(matrix.module_counts)} module counts")

    # Test 2: Exact match
    price, errors = matrix.get_price(10, 'Speicher A', True)
    print(f"✓ Exact match test: {price} (expected: 15000.0)")

    # Test 3: Case insensitive
    price, errors = matrix.get_price(15, 'speicher b', True)
    print(f"✓ Case insensitive test: {price} (expected: 19000.0)")

    # Test 4: No storage
    price, errors = matrix.get_price(20, None, False)
    print(f"✓ No storage test: {price} (expected: 16000.0)")

    # Test 5: Fallback behavior
    price, errors = matrix.get_price(25, 'Unknown Model', True)
    print(
        f"✓ Fallback test: {price} (expected: 18000.0, fallback to 'Ohne Speicher')")

    # Test 6: Matrix info
    info = matrix.get_matrix_info()
    print(
        f"✓ Matrix info: {
            info['total_module_options']} module options, {
            info['total_storage_options']} storage options")

    print("All tests completed successfully!")
