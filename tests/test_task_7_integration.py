"""
Test for Task 7: Extended PDF Generator Integration

This test verifies that the extended PDF generator is properly integrated
into the main PDF generation flow.
"""

import io
from unittest.mock import Mock, patch, MagicMock


def test_extended_pdf_integration_disabled():
    """Test that standard PDF is returned when extended output is disabled."""
    # Import the function
    from pdf_generator import _merge_extended_pdf_pages

    # Create mock data
    base_pdf = b'%PDF-1.4 base pdf content'
    project_data = {'test': 'data'}
    analysis_results = {'test': 'results'}
    extended_options = {}  # Empty options
    texts = {'test': 'text'}

    # Call the function
    result = _merge_extended_pdf_pages(
        base_pdf,
        project_data,
        analysis_results,
        extended_options,
        texts
    )

    # Should return base PDF unchanged when no extended options
    assert result == base_pdf
    print("✓ Test passed: Standard PDF returned when extended output disabled")


def test_extended_pdf_integration_with_module_not_available():
    """Test fallback when extended_pdf_generator module is not available."""
    from pdf_generator import _merge_extended_pdf_pages
    import sys

    base_pdf = b'%PDF-1.4 base pdf content'
    project_data = {'test': 'data'}
    analysis_results = {'test': 'results'}
    extended_options = {'financing_details': True}
    texts = {'test': 'text'}

    # Mock the import to fail by patching __import__
    original_import = __builtins__.__import__

    def mock_import(name, *args, **kwargs):
        if name == 'extended_pdf_generator':
            raise ImportError("Module not found")
        return original_import(name, *args, **kwargs)

    with patch('builtins.__import__', side_effect=mock_import):
        result = _merge_extended_pdf_pages(
            base_pdf,
            project_data,
            analysis_results,
            extended_options,
            texts
        )

    # Should return base PDF on import error
    assert result == base_pdf
    print("✓ Test passed: Fallback to base PDF when module not available")


def test_merge_two_pdfs():
    """Test the PDF merging function."""
    from pdf_generator import _merge_two_pdfs

    # Create simple mock PDFs
    pdf1 = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\ntrailer\n<< /Root 1 0 R >>\n%%EOF'
    pdf2 = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\ntrailer\n<< /Root 1 0 R >>\n%%EOF'

    # Call merge function
    result = _merge_two_pdfs(pdf1, pdf2)

    # Should return bytes
    assert isinstance(result, bytes)
    assert len(result) > 0
    print("✓ Test passed: PDF merging returns valid bytes")


def test_store_extended_pdf_warning():
    """Test the warning storage function."""
    from pdf_generator import _store_extended_pdf_warning

    # The function should not raise an error even if streamlit is not available
    try:
        _store_extended_pdf_warning("Test warning message")
        # If no exception is raised, the test passes
        print("✓ Test passed: Warning storage works correctly (no errors)")
    except Exception as e:
        raise AssertionError(f"Warning storage raised unexpected error: {e}")


def test_extended_pdf_integration_with_empty_result():
    """Test that base PDF is returned when extended generator returns empty."""
    from pdf_generator import _merge_extended_pdf_pages

    base_pdf = b'%PDF-1.4 base pdf content'
    project_data = {'test': 'data'}
    analysis_results = {'test': 'results'}
    extended_options = {'financing_details': True}
    texts = {'test': 'text'}

    # Mock the ExtendedPDFGenerator to return empty bytes
    with patch('extended_pdf_generator.ExtendedPDFGenerator') as mock_generator:
        mock_instance = MagicMock()
        mock_instance.generate_extended_pages.return_value = b''
        mock_generator.return_value = mock_instance

        result = _merge_extended_pdf_pages(
            base_pdf,
            project_data,
            analysis_results,
            extended_options,
            texts
        )

    # Should return base PDF when extended pages are empty
    assert result == base_pdf
    print("✓ Test passed: Base PDF returned when extended pages are empty")


def test_extended_pdf_integration_error_handling():
    """Test that errors in extended generation are handled gracefully."""
    from pdf_generator import _merge_extended_pdf_pages

    base_pdf = b'%PDF-1.4 base pdf content'
    project_data = {'test': 'data'}
    analysis_results = {'test': 'results'}
    extended_options = {'financing_details': True}
    texts = {'test': 'text'}

    # Mock the ExtendedPDFGenerator to raise an exception
    with patch('extended_pdf_generator.ExtendedPDFGenerator') as mock_generator:
        mock_instance = MagicMock()
        mock_instance.generate_extended_pages.side_effect = Exception(
            "Generation failed")
        mock_generator.return_value = mock_instance

        result = _merge_extended_pdf_pages(
            base_pdf,
            project_data,
            analysis_results,
            extended_options,
            texts
        )

    # Should return base PDF on error (graceful degradation)
    assert result == base_pdf
    print("✓ Test passed: Graceful degradation on generation error")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Testing Task 7: Extended PDF Generator Integration")
    print("=" * 60 + "\n")

    try:
        test_extended_pdf_integration_disabled()
        test_extended_pdf_integration_with_module_not_available()
        test_merge_two_pdfs()
        test_store_extended_pdf_warning()
        test_extended_pdf_integration_with_empty_result()
        test_extended_pdf_integration_error_handling()

        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        raise
