# PDF Compression & Optimization Guide

Complete guide for using the PDF compression and optimization service in Solar Calculator Pro.

## Overview

The PDF Compression Service provides comprehensive PDF optimization capabilities including:

- **PDF Size Reduction**: Advanced compression algorithms to reduce file size
- **Image Optimization**: Compress and optimize embedded images
- **Font Optimization**: Optimize font embedding and create font subsets
- **PDF Streaming**: Stream large PDFs in chunks for efficient delivery
- **PDF Encryption**: Password-protect PDFs with customizable permissions
- **Metadata Management**: Add, update, or remove PDF metadata

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Compression Options](#compression-options)
3. [Image Optimization](#image-optimization)
4. [Font Optimization](#font-optimization)
5. [PDF Streaming](#pdf-streaming)
6. [PDF Encryption](#pdf-encryption)
7. [Metadata Management](#metadata-management)
8. [Complete Optimization](#complete-optimization)
9. [API Reference](#api-reference)
10. [Best Practices](#best-practices)

## Basic Usage

### Python Service

```python
from services.pdf_compression_service import pdf_compression_service

# Read PDF file
with open('input.pdf', 'rb') as f:
    pdf_bytes = f.read()

# Compress PDF
compressed_pdf = pdf_compression_service.compress_pdf(pdf_bytes)

# Save compressed PDF
with open('output.pdf', 'wb') as f:
    f.write(compressed_pdf)
```

### REST API

```bash
# Compress PDF via API
curl -X POST "http://localhost:8000/api/v1/pdf-compression/compress" \
  -F "file=@input.pdf" \
  -F "options={\"compression_level\": 9}" \
  -o compressed.pdf
```

## Compression Options

### Compression Levels

The service supports compression levels from 0 (no compression) to 9 (maximum compression):

```python
# Maximum compression
compressed = pdf_compression_service.compress_pdf(
    pdf_bytes,
    compression_level=9
)

# Balanced compression
compressed = pdf_compression_service.compress_pdf(
    pdf_bytes,
    compression_level=5
)

# No compression (useful for testing)
compressed = pdf_compression_service.compress_pdf(
    pdf_bytes,
    compression_level=0
)
```

### Advanced Options

```python
compressed = pdf_compression_service.compress_pdf(
    pdf_bytes,
    compression_level=9,           # Maximum compression
    optimize_images=True,          # Optimize embedded images
    image_quality=85,              # JPEG quality (1-100)
    image_dpi=150,                 # Target DPI for images
    remove_duplicates=True,        # Remove duplicate objects
    compress_streams=True          # Compress content streams
)
```

## Image Optimization

### Basic Image Optimization

```python
# Optimize images with default settings
compressed = pdf_compression_service.compress_pdf(
    pdf_bytes,
    optimize_images=True
)
```

### Custom Image Settings

```python
# High quality (larger file size)
compressed = pdf_compression_service.compress_pdf(
    pdf_bytes,
    optimize_images=True,
    image_quality=95,  # High quality
    image_dpi=300      # High DPI
)

# Balanced quality
compressed = pdf_compression_service.compress_pdf(
    pdf_bytes,
    optimize_images=True,
    image_quality=85,  # Good quality
    image_dpi=150      # Standard DPI
)

# Maximum compression (lower quality)
compressed = pdf_compression_service.compress_pdf(
    pdf_bytes,
    optimize_images=True,
    image_quality=60,  # Lower quality
    image_dpi=72       # Screen DPI
)
```

### Image Optimization Guidelines

- **Print Quality**: Use DPI 300, Quality 95
- **Screen Display**: Use DPI 150, Quality 85
- **Web/Email**: Use DPI 72, Quality 75
- **Maximum Compression**: Use DPI 72, Quality 60

## Font Optimization

### Basic Font Optimization

```python
optimized = pdf_compression_service.optimize_fonts(pdf_bytes)
```

### Custom Font Settings

```python
optimized = pdf_compression_service.optimize_fonts(
    pdf_bytes,
    subset_fonts=True,   # Create font subsets (only used characters)
    embed_fonts=True     # Embed fonts in PDF
)
```

### Font Optimization Benefits

- **Subset Fonts**: Reduces file size by including only used characters
- **Embed Fonts**: Ensures consistent display across all devices
- **Remove Unused Fonts**: Eliminates fonts that aren't used

## PDF Streaming

### Basic Streaming

```python
# Stream PDF in chunks
for chunk in pdf_compression_service.stream_pdf(pdf_bytes):
    # Process chunk
    process_chunk(chunk)
```

### Custom Chunk Size

```python
# Stream with 4KB chunks
for chunk in pdf_compression_service.stream_pdf(pdf_bytes, chunk_size=4096):
    send_to_client(chunk)

# Stream with 16KB chunks (faster for large files)
for chunk in pdf_compression_service.stream_pdf(pdf_bytes, chunk_size=16384):
    send_to_client(chunk)
```

### Streaming Use Cases

- **Large PDFs**: Stream files larger than 10MB
- **Network Transfer**: Reduce memory usage during transfer
- **Progressive Loading**: Start displaying PDF before complete download
- **Bandwidth Optimization**: Send data in manageable chunks

## PDF Encryption

### Basic Encryption

```python
# Encrypt with user password
encrypted = pdf_compression_service.encrypt_pdf(
    pdf_bytes,
    user_password="secret123"
)
```

### Advanced Encryption

```python
# Encrypt with permissions
encrypted = pdf_compression_service.encrypt_pdf(
    pdf_bytes,
    user_password="user123",      # Password to open PDF
    owner_password="owner456",    # Password to change permissions
    permissions={
        'print': True,            # Allow printing
        'modify': False,          # Disallow modifications
        'copy': False,            # Disallow copying content
        'annotate': False         # Disallow annotations
    }
)
```

### Permission Options

- **print**: Allow/disallow printing
- **modify**: Allow/disallow document modifications
- **copy**: Allow/disallow copying text and graphics
- **annotate**: Allow/disallow adding annotations

### Encryption Use Cases

- **Confidential Documents**: Protect sensitive information
- **Copyright Protection**: Prevent unauthorized copying
- **Read-Only Distribution**: Allow viewing but not editing
- **Controlled Printing**: Allow viewing but not printing

## Metadata Management

### Add Metadata

```python
metadata = {
    '/Title': 'Solar System Proposal',
    '/Author': 'Solar Calculator Pro',
    '/Subject': 'PV System Design',
    '/Keywords': 'solar, pv, proposal',
    '/Creator': 'Solar Calculator Pro',
    '/Producer': 'PDF Compression Service'
}

updated = pdf_compression_service.manage_metadata(
    pdf_bytes,
    metadata=metadata
)
```

### Remove Metadata

```python
# Remove all metadata
cleaned = pdf_compression_service.manage_metadata(
    pdf_bytes,
    remove_metadata=True
)
```

### Standard Metadata Fields

- **/Title**: Document title
- **/Author**: Document author
- **/Subject**: Document subject
- **/Keywords**: Document keywords (comma-separated)
- **/Creator**: Application that created the document
- **/Producer**: Application that produced the PDF
- **/CreationDate**: Date document was created
- **/ModDate**: Date document was last modified

## Complete Optimization

### One-Step Optimization

```python
result = pdf_compression_service.optimize_pdf_complete(pdf_bytes)

print(f"Original size: {result['original_size_bytes']} bytes")
print(f"Optimized size: {result['optimized_size_bytes']} bytes")
print(f"Reduction: {result['size_reduction_percent']:.1f}%")

# Save optimized PDF
with open('optimized.pdf', 'wb') as f:
    f.write(result['optimized_pdf'])
```

### Custom Complete Optimization

```python
result = pdf_compression_service.optimize_pdf_complete(
    pdf_bytes,
    options={
        'compression_level': 9,
        'optimize_images': True,
        'image_quality': 85,
        'image_dpi': 150,
        'remove_duplicates': True,
        'compress_streams': True,
        'optimize_fonts': True,
        'subset_fonts': True,
        'embed_fonts': True,
        'add_metadata': True,
        'metadata': {
            '/Title': 'Optimized Document',
            '/Author': 'Your Name'
        }
    }
)
```

### Result Structure

```python
{
    'optimized_pdf': bytes,              # Optimized PDF data
    'original_size_bytes': int,          # Original file size
    'optimized_size_bytes': int,         # Optimized file size
    'size_reduction_bytes': int,         # Bytes saved
    'size_reduction_percent': float,     # Percentage saved
    'original_info': dict,               # Original PDF info
    'optimized_info': dict,              # Optimized PDF info
    'options_used': dict                 # Options that were applied
}
```

## API Reference

### REST API Endpoints

#### POST /api/v1/pdf-compression/compress

Compress a PDF file.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/pdf-compression/compress" \
  -F "file=@input.pdf" \
  -F "options={
    \"compression_level\": 9,
    \"optimize_images\": true,
    \"image_quality\": 85
  }"
```

**Response:** Compressed PDF file

#### POST /api/v1/pdf-compression/optimize-fonts

Optimize fonts in a PDF.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/pdf-compression/optimize-fonts" \
  -F "file=@input.pdf" \
  -F "options={
    \"subset_fonts\": true,
    \"embed_fonts\": true
  }"
```

**Response:** PDF with optimized fonts

#### POST /api/v1/pdf-compression/stream

Stream a PDF in chunks.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/pdf-compression/stream" \
  -F "file=@input.pdf" \
  -F "chunk_size=8192"
```

**Response:** Streaming PDF response

#### POST /api/v1/pdf-compression/encrypt

Encrypt a PDF with password protection.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/pdf-compression/encrypt" \
  -F "file=@input.pdf" \
  -F "options={
    \"user_password\": \"secret123\",
    \"allow_print\": true,
    \"allow_modify\": false
  }"
```

**Response:** Encrypted PDF file

#### POST /api/v1/pdf-compression/metadata

Manage PDF metadata.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/pdf-compression/metadata" \
  -F "file=@input.pdf" \
  -F "options={
    \"title\": \"My Document\",
    \"author\": \"John Doe\"
  }"
```

**Response:** PDF with updated metadata

#### GET /api/v1/pdf-compression/info

Get information about a PDF.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/pdf-compression/info" \
  -F "file=@input.pdf"
```

**Response:**
```json
{
  "filename": "input.pdf",
  "num_pages": 10,
  "size_bytes": 1048576,
  "size_kb": 1024.0,
  "size_mb": 1.0,
  "is_encrypted": false,
  "metadata": {},
  "page_sizes": [...]
}
```

#### POST /api/v1/pdf-compression/optimize-complete

Complete PDF optimization.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/pdf-compression/optimize-complete" \
  -F "file=@input.pdf" \
  -F "options={
    \"compression_level\": 9,
    \"optimize_images\": true,
    \"optimize_fonts\": true
  }"
```

**Response:** Fully optimized PDF with statistics in headers

## Best Practices

### 1. Choose Appropriate Compression Level

- **Level 9**: Maximum compression, slower processing
- **Level 5-7**: Balanced compression and speed
- **Level 0-3**: Minimal compression, faster processing

### 2. Optimize Images Wisely

- **Print documents**: High quality (DPI 300, Quality 95)
- **Screen viewing**: Medium quality (DPI 150, Quality 85)
- **Email/web**: Lower quality (DPI 72, Quality 75)

### 3. Use Font Subsetting

- Always enable font subsetting for smaller file sizes
- Only embed fonts when cross-platform compatibility is critical

### 4. Stream Large Files

- Stream PDFs larger than 10MB
- Use appropriate chunk sizes (4KB-16KB)

### 5. Protect Sensitive Documents

- Always encrypt confidential PDFs
- Use strong passwords (minimum 8 characters)
- Set appropriate permissions

### 6. Add Meaningful Metadata

- Include title, author, and subject
- Add keywords for searchability
- Include creation date and version info

### 7. Test Optimization Results

- Always verify PDF quality after optimization
- Check that all content is intact
- Test on target devices/platforms

### 8. Monitor File Sizes

- Track compression ratios
- Identify optimization opportunities
- Balance quality vs. file size

## Performance Considerations

### Memory Usage

- Large PDFs (>50MB) may require significant memory
- Use streaming for very large files
- Process PDFs in batches if handling multiple files

### Processing Time

- Compression level affects processing time
- Image optimization is the most time-consuming operation
- Font optimization is relatively fast

### Optimization Guidelines

| File Size | Recommended Approach |
|-----------|---------------------|
| < 1MB | Full optimization |
| 1-10MB | Standard compression |
| 10-50MB | Compression + streaming |
| > 50MB | Streaming only |

## Troubleshooting

### Common Issues

**Issue**: Compressed PDF is larger than original
- **Solution**: Disable image optimization or use higher quality settings

**Issue**: PDF appears corrupted after compression
- **Solution**: Reduce compression level or disable certain optimizations

**Issue**: Fonts look different after optimization
- **Solution**: Disable font subsetting or ensure fonts are embedded

**Issue**: Encrypted PDF cannot be opened
- **Solution**: Verify password is correct and encryption settings

**Issue**: Streaming fails for large files
- **Solution**: Increase chunk size or available memory

## Examples

### Example 1: Compress for Email

```python
# Optimize for email (small file size)
result = pdf_compression_service.optimize_pdf_complete(
    pdf_bytes,
    options={
        'compression_level': 9,
        'optimize_images': True,
        'image_quality': 75,
        'image_dpi': 72,
        'optimize_fonts': True
    }
)
```

### Example 2: Compress for Print

```python
# Optimize for print (maintain quality)
result = pdf_compression_service.optimize_pdf_complete(
    pdf_bytes,
    options={
        'compression_level': 7,
        'optimize_images': True,
        'image_quality': 95,
        'image_dpi': 300,
        'optimize_fonts': True
    }
)
```

### Example 3: Secure Document

```python
# Encrypt and compress
compressed = pdf_compression_service.compress_pdf(pdf_bytes)
encrypted = pdf_compression_service.encrypt_pdf(
    compressed,
    user_password="secret123",
    permissions={'print': True, 'modify': False}
)
```

## Requirements

- Python 3.8+
- PyPDF2 or pypdf
- Pillow (PIL)
- ReportLab

## Related Documentation

- [PDF Generation Guide](PDF_GENERATION_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Security Guide](SECURITY_GUIDE.md)

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review the [API Reference](#api-reference)
- Contact support team

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Requirements**: 1.3, 11.3
