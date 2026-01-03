## Document PDF Conversion Service

**Requirements:** 14.8  
**Task:** 228

### Overview

The Document PDF Conversion Service provides comprehensive functionality for converting various document formats to PDF bytes and merging multiple PDFs into a single document.

### Supported Formats

- **Word Documents** (.docx) - Converts Word documents with text, paragraphs, and tables
- **Excel Spreadsheets** (.xlsx) - Converts Excel sheets with data and formatting
- **Text Documents** (.txt, .md) - Converts plain text with optional formatting preservation
- **PDF Merging** - Combines multiple PDF documents into one

### Key Features

✅ **Multiple Format Support** - Word, Excel, and text documents  
✅ **German Number Formatting** - Automatic formatting (1.234,56)  
✅ **PDF Merging** - Combine multiple PDFs with metadata  
✅ **Metadata Support** - Add title, author, subject, keywords  
✅ **Batch Conversion** - Convert multiple documents at once  
✅ **Unicode Support** - Full support for international characters  
✅ **Flexible Input** - File paths, bytes, or direct content  

### Installation

Required dependencies:

```bash
pip install reportlab PyPDF2 python-docx openpyxl
```

### Basic Usage

#### Text to PDF

```python
from backend.services.document_pdf_service import DocumentPDFService
from backend.core.pdf_bytes import PDFMetadata

service = DocumentPDFService()

# Convert text to PDF
text_content = "This is my document content."
pdf_bytes = service.text_to_pdf_bytes(text_content=text_content)

# Save to file
with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

#### Word to PDF

```python
# Convert Word document
pdf_bytes = service.word_to_pdf_bytes(file_path='document.docx')

# Or from bytes
with open('document.docx', 'rb') as f:
    doc_bytes = f.read()
pdf_bytes = service.word_to_pdf_bytes(file_content=doc_bytes)
```

#### Excel to PDF

```python
# Convert Excel spreadsheet
pdf_bytes = service.excel_to_pdf_bytes(
    file_path='spreadsheet.xlsx',
    sheet_name='Sheet1',  # Optional: specific sheet
    max_rows=100,         # Optional: limit rows
    max_cols=10           # Optional: limit columns
)
```

#### Merge PDFs

```python
# Merge multiple PDFs
pdf1 = service.text_to_pdf_bytes(text_content="Document 1")
pdf2 = service.text_to_pdf_bytes(text_content="Document 2")

merged = service.merge_pdf_documents([pdf1, pdf2])

# Save merged PDF
with open('merged.pdf', 'wb') as f:
    f.write(merged)
```

### Advanced Usage

#### With Metadata

```python
metadata = PDFMetadata(
    title="My Document",
    author="John Doe",
    subject="Important Report",
    keywords=["report", "analysis", "2024"]
)

pdf_bytes = service.text_to_pdf_bytes(
    text_content="Content",
    metadata=metadata
)
```

#### Preserve Text Formatting

```python
# Preserve line breaks and spacing (good for code)
pdf_bytes = service.text_to_pdf_bytes(
    text_content=code_content,
    preserve_formatting=True
)

# Flow text naturally (good for prose)
pdf_bytes = service.text_to_pdf_bytes(
    text_content=prose_content,
    preserve_formatting=False
)
```

#### Batch Conversion

```python
documents = [
    {'file_path': 'doc1.txt', 'file_type': 'txt'},
    {'file_path': 'doc2.docx', 'file_type': 'docx'},
    {'file_path': 'doc3.xlsx', 'file_type': 'xlsx'}
]

# Convert all
pdf_list = []
for doc in documents:
    pdf_bytes = service.document_to_pdf_bytes(**doc)
    pdf_list.append(pdf_bytes)

# Optionally merge
merged = service.merge_pdf_documents(pdf_list)
```

### Convenience Functions

```python
from backend.services.document_pdf_service import (
    text_to_pdf,
    word_to_pdf,
    excel_to_pdf,
    merge_pdfs
)

# Simple text conversion
pdf_bytes = text_to_pdf('input.txt', 'output.pdf')

# Simple Word conversion
pdf_bytes = word_to_pdf('document.docx', 'output.pdf')

# Simple Excel conversion
pdf_bytes = excel_to_pdf('spreadsheet.xlsx', 'output.pdf')

# Simple PDF merging
merged = merge_pdfs(['doc1.pdf', 'doc2.pdf'], 'merged.pdf')
```

### German Number Formatting

The service automatically preserves German number formatting in text documents:

```python
text_content = """
Preis: 1.234,56 €
Menge: 1.000 Stück
Rabatt: 15,50%
"""

pdf_bytes = service.text_to_pdf_bytes(text_content=text_content)
# Numbers remain in German format in the PDF
```

### Error Handling

```python
from backend.services.document_pdf_service import DocumentConversionError

try:
    pdf_bytes = service.document_to_pdf_bytes(
        file_path='document.xyz',
        file_type='xyz'
    )
except DocumentConversionError as e:
    print(f"Conversion failed: {e}")
except ImportError as e:
    print(f"Missing dependency: {e}")
```

### API Reference

#### DocumentPDFService

**Methods:**

- `document_to_pdf_bytes(file_path, file_content, file_type, metadata)` - Convert any supported document
- `word_to_pdf_bytes(file_path, file_content, metadata)` - Convert Word document
- `excel_to_pdf_bytes(file_path, file_content, metadata, sheet_name, max_rows, max_cols)` - Convert Excel
- `text_to_pdf_bytes(file_path, file_content, text_content, metadata, preserve_formatting)` - Convert text
- `merge_pdf_documents(pdf_files, output_metadata)` - Merge multiple PDFs
- `convert_multiple_documents(documents, merge, output_metadata)` - Batch conversion

#### PDFMetadata

**Properties:**

- `title` (str) - Document title
- `author` (str) - Document author
- `subject` (str) - Document subject
- `creator` (str) - Creator application
- `keywords` (List[str]) - Document keywords
- `creation_date` (datetime) - Creation timestamp

### Examples

#### Example 1: Convert Text File

```python
service = DocumentPDFService()

# Read text file
with open('report.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Convert to PDF
metadata = PDFMetadata(
    title="Monthly Report",
    author="Sales Team",
    subject="Sales Analysis"
)

pdf_bytes = service.text_to_pdf_bytes(
    text_content=text,
    metadata=metadata
)

# Save
with open('report.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

#### Example 2: Merge Project Documents

```python
service = DocumentPDFService()

# Convert multiple documents
overview_pdf = service.text_to_pdf_bytes(
    text_content="Project Overview...",
    metadata=PDFMetadata(title="Overview")
)

specs_pdf = service.word_to_pdf_bytes(
    file_path='specifications.docx'
)

costs_pdf = service.excel_to_pdf_bytes(
    file_path='costs.xlsx'
)

# Merge all
merged_metadata = PDFMetadata(
    title="Complete Project Documentation",
    author="Project Team",
    keywords=["project", "documentation"]
)

merged_pdf = service.merge_pdf_documents(
    [overview_pdf, specs_pdf, costs_pdf],
    output_metadata=merged_metadata
)

# Save merged document
with open('project_complete.pdf', 'wb') as f:
    f.write(merged_pdf)
```

#### Example 3: Batch Processing

```python
service = DocumentPDFService()

# Process multiple files
files = ['doc1.txt', 'doc2.txt', 'doc3.txt']
pdf_list = []

for file_path in files:
    pdf_bytes = service.text_to_pdf_bytes(file_path=file_path)
    pdf_list.append(pdf_bytes)
    
    # Save individual PDF
    output_name = file_path.replace('.txt', '.pdf')
    with open(output_name, 'wb') as f:
        f.write(pdf_bytes)

# Also create merged version
merged = service.merge_pdf_documents(pdf_list)
with open('all_documents.pdf', 'wb') as f:
    f.write(merged)
```

### Performance Considerations

- **Large Documents**: For very large documents, consider processing in chunks
- **Excel Sheets**: Use `max_rows` and `max_cols` to limit data
- **Batch Processing**: Process documents in parallel for better performance
- **Memory**: PDF bytes are kept in memory; save to disk for large files

### Limitations

- Word conversion requires `python-docx` (only .docx, not .doc)
- Excel conversion requires `openpyxl` (only .xlsx, not .xls)
- PDF merging requires `PyPDF2`
- Complex Word formatting may not be fully preserved
- Excel charts and images are not included (data only)

### Testing

Run tests:

```bash
pytest backend/tests/test_document_pdf_service.py -v
```

Run demo:

```bash
python backend/demo_document_pdf.py
```

### Integration with Universal Data System

The Document PDF Service integrates with the Universal Data System for dynamic keys and PDF bytes:

```python
from backend.services.universal_data_service import UniversalDataService
from backend.services.document_pdf_service import DocumentPDFService

# Convert document
doc_service = DocumentPDFService()
pdf_bytes = doc_service.text_to_pdf_bytes(text_content="Content")

# Store with dynamic key
data_service = UniversalDataService(db)
record = data_service.create_with_keys(
    model_class=DocumentModel,
    data={
        'content': "Content",
        'pdf_bytes': pdf_bytes
    }
)
```

### See Also

- [PDF Bytes Core](./PDF_BYTE_GENERATION.md) - Core PDF generation functionality
- [Chart PDF Service](./CHART_PDF_GENERATION.md) - Chart to PDF conversion
- [Media PDF Service](./MEDIA_PDF_GENERATION.md) - Image and media to PDF
- [Universal Data System](./UNIVERSAL_DATA_MODEL.md) - Dynamic keys and PDF bytes

### Support

For issues or questions:
- Check the demo file: `backend/demo_document_pdf.py`
- Run tests: `backend/tests/test_document_pdf_service.py`
- Review examples in this documentation
