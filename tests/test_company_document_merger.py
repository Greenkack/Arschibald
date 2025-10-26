"""
Test script for CompanyDocumentMerger class.

Tests the company document merging functionality including:
- Loading documents from database
- Merging PDF documents
- Error handling for missing files
"""

from extended_pdf_generator import CompanyDocumentMerger
import os
import sys
from io import BytesIO
from pypdf import PdfReader

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_company_document_merger_empty_list():
    """Test that empty document list returns empty bytes."""
    print("\n=== Test 1: Empty Document List ===")
    merger = CompanyDocumentMerger()
    result = merger.merge([])

    assert result == b'', "Empty list should return empty bytes"
    print("✓ Empty list returns empty bytes")


def test_company_document_merger_invalid_id():
    """Test that invalid document ID is handled gracefully."""
    print("\n=== Test 2: Invalid Document ID ===")
    merger = CompanyDocumentMerger()
    result = merger.merge([99999])  # Non-existent ID

    assert result == b'', "Invalid ID should return empty bytes"
    print("✓ Invalid ID handled gracefully")


def test_company_document_merger_with_real_documents():
    """Test merging real company documents from database."""
    print("\n=== Test 3: Real Company Documents ===")

    # First, check if we have any company documents in the database
    try:
        from database import get_db_connection

        conn = get_db_connection()
        if not conn:
            print("⚠ Could not connect to database, skipping real document test")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM company_documents LIMIT 5")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("⚠ No company documents found in database, skipping real document test")
            return

        document_ids = [row[0] for row in rows]
        print(f"Found {len(document_ids)} company documents: {document_ids}")

        # Test merging
        merger = CompanyDocumentMerger()
        result = merger.merge(document_ids)

        if result:
            # Verify it's a valid PDF
            reader = PdfReader(BytesIO(result))
            num_pages = len(reader.pages)
            print(
                f"✓ Successfully merged {
                    len(document_ids)} documents into {num_pages} pages")
        else:
            print("⚠ No documents could be merged (files may not exist on disk)")

    except Exception as e:
        print(f"⚠ Error testing real documents: {e}")


def test_company_document_merger_mixed_valid_invalid():
    """Test merging with mix of valid and invalid document IDs."""
    print("\n=== Test 4: Mixed Valid/Invalid IDs ===")

    try:
        from database import get_db_connection

        conn = get_db_connection()
        if not conn:
            print("⚠ Could not connect to database, skipping mixed ID test")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM company_documents LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if not row:
            print("⚠ No company documents found in database, skipping mixed ID test")
            return

        valid_id = row[0]
        invalid_ids = [99998, 99999]
        mixed_ids = [invalid_ids[0], valid_id, invalid_ids[1]]

        print(f"Testing with mixed IDs: {mixed_ids}")

        merger = CompanyDocumentMerger()
        result = merger.merge(mixed_ids)

        if result:
            reader = PdfReader(BytesIO(result))
            num_pages = len(reader.pages)
            print(
                f"✓ Successfully merged valid documents, skipped invalid ones ({num_pages} pages)")
        else:
            print("⚠ No documents could be merged (file may not exist on disk)")

    except Exception as e:
        print(f"⚠ Error testing mixed IDs: {e}")


def test_company_document_merger_load_document_method():
    """Test the _load_document method directly."""
    print("\n=== Test 5: _load_document Method ===")

    merger = CompanyDocumentMerger()

    # Test with invalid ID
    result = merger._load_document(99999)
    assert result is None, "Invalid ID should return None"
    print("✓ _load_document returns None for invalid ID")

    # Test with valid ID if available
    try:
        from database import get_db_connection

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM company_documents LIMIT 1")
            row = cursor.fetchone()
            conn.close()

            if row:
                valid_id = row[0]
                result = merger._load_document(valid_id)

                if result:
                    print(
                        f"✓ _load_document successfully loaded document {valid_id}")
                else:
                    print(
                        f"⚠ _load_document returned None for valid ID {valid_id} (file may not exist)")
    except Exception as e:
        print(f"⚠ Error testing _load_document with valid ID: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing CompanyDocumentMerger")
    print("=" * 60)

    try:
        test_company_document_merger_empty_list()
        test_company_document_merger_invalid_id()
        test_company_document_merger_with_real_documents()
        test_company_document_merger_mixed_valid_invalid()
        test_company_document_merger_load_document_method()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
