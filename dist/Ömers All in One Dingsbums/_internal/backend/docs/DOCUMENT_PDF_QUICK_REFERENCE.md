# Document PDF Conversion - Quick Reference

**Task 228** | **Requirements: 14.8**

## Quick Start

```python
from backend.services.document_pdf_service import DocumentPDFService

service = DocumentPDFService()
```

## Text to PDF

```python
# From string
pdf_bytes = service.text_to_pdf_bytes(text_content="Hello World")

# From file
pdf_bytes = service.text_to_pdf_bytes(file_path="document.txt")

# With formatting preserved
pdf_bytes = service.text_to_pdf_bytes(
    text_content=code,
    preserve_formatting=True
)
```

## Word to PDF

```python
# From file
pdf_bytes = service.word_to_pdf_bytes(file_path="document.docx")

# From bytes
pdf_bytes = service.word_to_pdf_bytes(file_content=docx_bytes)
```

## Excel to PDF

```python
# Basic conversion
pdf_bytes = service.excel_to_pdf_bytes(file_path="data.xlsx")

# Specific sheet
pdf_bytes = service.excel_to_pdf_bytes(
    file_path="data.xlsx",
    sheet_name="Sheet1"
)

# Limited rows/columns
pdf_bytes = service.excel_to_pdf_bytes(
    file_path="data.xlsx",
    max_rows=100,
    max_cols=10
)
```

## Merge PDFs

```python
# From bytes
merged = service.merge_pdf_documents([pdf1, pdf2, pdf3])

# From files
merged = service.merge_pdf_documents([
    "doc1.pdf",
    "doc2.pdf",
    "doc3.pdf"
])

# With metadata
from backend.core.pdf_bytes import PDFMetadata

metadata = PDFMetadata(title="Merged Document")
merged = service.merge_pdf_documents(pdfs, metadata)
```

## Generic Conversion

```python
# Auto-detect type from extension
pdf_bytes = service.document_to_pdf_bytes(file_path="doc.txt")

# Explicit type
pdf_bytes = service.document_to_pdf_bytes(
    file_content=bytes_data,
    file_type="docx"
)
```

## With Metadata

```python
from backend.core.pdf_bytes import PDFMetadata

metadata = PDFMetadata(
    title="My Document",
    author="John Doe",
    subject="Report",
    keywords=["report", "2024"]
)

pdf_bytes = service.text_to_pdf_bytes(
    text_content="Content",
    metadata=metadata
)
```

## Convenience Functions

```python
from backend.services.document_pdf_service import (
    text_to_pdf,
    word_to_pdf,
    excel_to_pdf,
    merge_pdfs
)

# One-liners
text_to_pdf("input.txt", "output.pdf")
word_to_pdf("doc.docx", "output.pdf")
excel_to_pdf("data.xlsx", "output.pdf")
merge_pdfs(["1.pdf", "2.pdf"], "merged.pdf")
```

## Batch Processing

```python
# Convert multiple
documents = [
    {'file_path': 'doc1.txt', 'file_type': 'txt'},
    {'file_path': 'doc2.docx', 'file_type': 'docx'}
]

pdfs = []
for doc in documents:
    pdf = service.document_to_pdf_bytes(**doc)
    pdfs.append(pdf)

# Merge all
merged = service.merge_pdf_documents(pdfs)
```

## German Numbers

```python
# Numbers are preserved in German format
text = "Preis: 1.234,56 €"
pdf_bytes = service.text_to_pdf_bytes(text_content=text)
# Output PDF shows: 1.234,56 €
```

## Error Handling

```python
from backend.services.document_pdf_service import DocumentConversionError

try:
    pdf = service.document_to_pdf_bytes(file_path="doc.xyz")
except DocumentConversionError as e:
    print(f"Conversion failed: {e}")
except ImportError as e:
    print(f"Missing dependency: {e}")
```

## Common Patterns

### Pattern 1: Convert and Save

```python
pdf_bytes = service.text_to_pdf_bytes(text_content="Content")
with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Pattern 2: Convert Multiple and Merge

```python
pdfs = [
    service.text_to_pdf_bytes(text_content="Doc 1"),
    service.text_to_pdf_bytes(text_content="Doc 2")
]
merged = service.merge_pdf_documents(pdfs)
```

### Pattern 3: Batch with Metadata

```python
for i, content in enumerate(contents):
    metadata = PDFMetadata(title=f"Document {i+1}")
    pdf = service.text_to_pdf_bytes(
        text_content=content,
        metadata=metadata
    )
    with open(f'doc_{i+1}.pdf', 'wb') as f:
        f.write(pdf)
```

## Dependencies

```bash
pip install reportlab PyPDF2 python-docx openpyxl
```

## File Types

| Extension | Method | Requires |
|-----------|--------|----------|
| .txt, .md | `text_to_pdf_bytes()` | reportlab |
| .docx | `word_to_pdf_bytes()` | python-docx |
| .xlsx | `excel_to_pdf_bytes()` | openpyxl |
| .pdf | `merge_pdf_documents()` | PyPDF2 |

## Testing

```bash
# Run tests
pytest backend/tests/test_document_pdf_service.py -v

# Run demo
python backend/demo_document_pdf.py
```

## See Also

- Full Documentation: `DOCUMENT_PDF_CONVERSION.md`
- PDF Bytes Core: `PDF_BYTE_GENERATION.md`
- Chart PDF: `CHART_PDF_GENERATION.md`
- Media PDF: `MEDIA_PDF_GENERATION.md`
