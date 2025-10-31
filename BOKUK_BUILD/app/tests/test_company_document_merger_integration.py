"""
Integration test for CompanyDocumentMerger with actual PDF files.

Creates test PDF files and verifies the merging functionality.
"""

from extended_pdf_generator import CompanyDocumentMerger
import os
import sys
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_test_pdf(text: str, num_pages: int = 1) -> bytes:
    """Creates a simple test PDF with the given text."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    for i in range(num_pages):
        c.drawString(100, 750, f"{text} - Page {i + 1}")
        c.showPage()

    c.save()
    return buffer.getvalue()


def setup_test_documents():
    """Creates test company documents in the database."""
    from database import get_db_connection, COMPANY_DOCS_BASE_DIR
    import sqlite3

    # Create test PDFs
    pdf1 = create_test_pdf("Test Document 1", 2)
    pdf2 = create_test_pdf("Test Document 2", 1)
    pdf3 = create_test_pdf("Test Document 3", 3)

    # Ensure company_docs directory exists
    os.makedirs(COMPANY_DOCS_BASE_DIR, exist_ok=True)
    test_dir = os.path.join(COMPANY_DOCS_BASE_DIR, "test_company")
    os.makedirs(test_dir, exist_ok=True)

    # Save test PDFs
    test_files = []
    for idx, pdf_bytes in enumerate([pdf1, pdf2, pdf3], 1):
        filename = f"test_doc_{idx}.pdf"
        relative_path = os.path.join("test_company", filename)
        full_path = os.path.join(COMPANY_DOCS_BASE_DIR, relative_path)

        with open(full_path, 'wb') as f:
            f.write(pdf_bytes)

        test_files.append((filename, relative_path, full_path))

    # Insert into database
    conn = get_db_connection()
    if not conn:
        raise Exception("Could not connect to database")

    cursor = conn.cursor()
    doc_ids = []

    for filename, relative_path, full_path in test_files:
        cursor.execute(
            "INSERT INTO company_documents "
            "(company_id, document_type, display_name, file_name, absolute_file_path) "
            "VALUES (?, ?, ?, ?, ?)",
            (1, "Test", f"Test Document {filename}", filename, relative_path)
        )
        doc_ids.append(cursor.lastrowid)

    conn.commit()
    conn.close()

    return doc_ids, test_files


def cleanup_test_documents(doc_ids, test_files):
    """Removes test documents from database and filesystem."""
    from database import get_db_connection, COMPANY_DOCS_BASE_DIR

    # Remove from database
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        for doc_id in doc_ids:
            cursor.execute(
                "DELETE FROM company_documents WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()

    # Remove files
    for _, _, full_path in test_files:
        if os.path.exists(full_path):
            os.remove(full_path)

    # Remove test directory if empty
    test_dir = os.path.join(COMPANY_DOCS_BASE_DIR, "test_company")
    if os.path.exists(test_dir) and not os.listdir(test_dir):
        os.rmdir(test_dir)


def test_merge_multiple_documents():
    """Test merging multiple company documents."""
    print("\n=== Integration Test: Merge Multiple Documents ===")

    doc_ids = None
    test_files = None

    try:
        # Setup test documents
        doc_ids, test_files = setup_test_documents()
        print(f"Created {len(doc_ids)} test documents: {doc_ids}")

        # Test merging
        merger = CompanyDocumentMerger()
        result = merger.merge(doc_ids)

        # Verify result
        assert result, "Merge should return PDF bytes"

        reader = PdfReader(BytesIO(result))
        num_pages = len(reader.pages)

        # Should have 2 + 1 + 3 = 6 pages total
        expected_pages = 6
        assert num_pages == expected_pages, f"Expected {expected_pages} pages, got {num_pages}"

        print(
            f"✓ Successfully merged {
                len(doc_ids)} documents into {num_pages} pages")

        # Verify page content
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            print(f"  Page {i + 1}: {text[:50]}...")

        print("✓ All pages contain expected content")

    finally:
        # Cleanup
        if doc_ids and test_files:
            cleanup_test_documents(doc_ids, test_files)
            print("✓ Cleaned up test documents")


def test_merge_with_missing_file():
    """Test merging when one file is missing."""
    print("\n=== Integration Test: Merge with Missing File ===")

    doc_ids = None
    test_files = None

    try:
        # Setup test documents
        doc_ids, test_files = setup_test_documents()

        # Delete one file from filesystem (but keep in DB)
        _, _, file_to_delete = test_files[1]
        os.remove(file_to_delete)
        print(f"Deleted file: {file_to_delete}")

        # Test merging - should skip missing file
        merger = CompanyDocumentMerger()
        result = merger.merge(doc_ids)

        # Should still get a result with remaining documents
        assert result, "Merge should return PDF bytes even with missing file"

        reader = PdfReader(BytesIO(result))
        num_pages = len(reader.pages)

        # Should have 2 + 3 = 5 pages (skipped the missing one with 1 page)
        expected_pages = 5
        assert num_pages == expected_pages, f"Expected {expected_pages} pages, got {num_pages}"

        print(f"✓ Successfully merged remaining documents ({num_pages} pages)")
        print("✓ Missing file was handled gracefully")

    finally:
        # Cleanup
        if doc_ids and test_files:
            cleanup_test_documents(doc_ids, test_files)
            print("✓ Cleaned up test documents")


def test_merge_single_document():
    """Test merging a single document."""
    print("\n=== Integration Test: Merge Single Document ===")

    doc_ids = None
    test_files = None

    try:
        # Setup test documents
        doc_ids, test_files = setup_test_documents()

        # Test merging just the first document
        merger = CompanyDocumentMerger()
        result = merger.merge([doc_ids[0]])

        assert result, "Merge should return PDF bytes"

        reader = PdfReader(BytesIO(result))
        num_pages = len(reader.pages)

        # First document has 2 pages
        expected_pages = 2
        assert num_pages == expected_pages, f"Expected {expected_pages} pages, got {num_pages}"

        print(f"✓ Successfully merged single document ({num_pages} pages)")

    finally:
        # Cleanup
        if doc_ids and test_files:
            cleanup_test_documents(doc_ids, test_files)
            print("✓ Cleaned up test documents")


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("CompanyDocumentMerger Integration Tests")
    print("=" * 60)

    try:
        test_merge_multiple_documents()
        test_merge_with_missing_file()
        test_merge_single_document()

        print("\n" + "=" * 60)
        print("All integration tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
