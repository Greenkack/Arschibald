# PDF Compression Quick Reference

Fast reference for common PDF compression operations.

## Quick Start

```python
from services.pdf_compression_service import pdf_compression_service

# Read PDF
with open('input.pdf', 'rb') as f:
    pdf = f.read()

# Compress
compressed = pdf_compression_service.compress_pdf(pdf)

# Save
with open('output.pdf', 'wb') as f:
    f.write(compressed)
```

## Common Operations

### Basic Compression

```python
# Maximum compression
compressed = pdf_compression_service.compress_pdf(pdf, compression_level=9)

# Balanced compression
compressed = pdf_compression_service.compress_pdf(pdf, compression_level=5)
```

### Image Optimization

```python
# High quality (print)
compressed = pdf_compression_service.compress_pdf(
    pdf, optimize_images=True, image_quality=95, image_dpi=300
)

# Medium quality (screen)
compressed = pdf_compression_service.compress_pdf(
    pdf, optimize_images=True, image_quality=85, image_dpi=150
)

# Low quality (web/email)
compressed = pdf_compression_service.compress_pdf(
    pdf, optimize_images=True, image_quality=75, image_dpi=72
)
```

### Font Optimization

```python
optimized = pdf_compression_service.optimize_fonts(
    pdf, subset_fonts=True, embed_fonts=True
)
```

### Encryption

```python
# Simple encryption
encrypted = pdf_compression_service.encrypt_pdf(pdf, user_password="secret")

# With permissions
encrypted = pdf_compression_service.encrypt_pdf(
    pdf,
    user_password="user123",
    owner_password="owner456",
    permissions={'print': True, 'modify': False, 'copy': False}
)
```

### Metadata

```python
# Add metadata
updated = pdf_compression_service.manage_metadata(
    pdf,
    metadata={
        '/Title': 'My Document',
        '/Author': 'John Doe',
        '/Subject': 'Important Document'
    }
)

# Remove metadata
cleaned = pdf_compression_service.manage_metadata(pdf, remove_metadata=True)
```

### Complete Optimization

```python
result = pdf_compression_service.optimize_pdf_complete(pdf)

print(f"Reduced by {result['size_reduction_percent']:.1f}%")
with open('optimized.pdf', 'wb') as f:
    f.write(result['optimized_pdf'])
```

### Streaming

```python
# Stream in chunks
for chunk in pdf_compression_service.stream_pdf(pdf, chunk_size=8192):
    send_chunk(chunk)
```

### Get Info

```python
info = pdf_compression_service.get_pdf_info(pdf)
print(f"Pages: {info['num_pages']}")
print(f"Size: {info['size_mb']:.2f} MB")
print(f"Encrypted: {info['is_encrypted']}")
```

## API Endpoints

### Compress

```bash
curl -X POST "http://localhost:8000/api/v1/pdf-compression/compress" \
  -F "file=@input.pdf" \
  -o compressed.pdf
```

### Optimize Complete

```bash
curl -X POST "http://localhost:8000/api/v1/pdf-compression/optimize-complete" \
  -F "file=@input.pdf" \
  -o optimized.pdf
```

### Encrypt

```bash
curl -X POST "http://localhost:8000/api/v1/pdf-compression/encrypt" \
  -F "file=@input.pdf" \
  -F "options={\"user_password\": \"secret\"}" \
  -o encrypted.pdf
```

### Get Info

```bash
curl -X GET "http://localhost:8000/api/v1/pdf-compression/info" \
  -F "file=@input.pdf"
```

## Compression Levels

| Level | Compression | Speed | Use Case |
|-------|-------------|-------|----------|
| 0 | None | Fastest | Testing |
| 1-3 | Low | Fast | Quick compression |
| 4-6 | Medium | Balanced | General use |
| 7-9 | High | Slow | Maximum compression |

## Image Quality Guidelines

| Use Case | DPI | Quality | File Size |
|----------|-----|---------|-----------|
| Print | 300 | 95 | Large |
| Screen | 150 | 85 | Medium |
| Web | 72 | 75 | Small |
| Email | 72 | 60 | Smallest |

## Permissions

| Permission | Description |
|------------|-------------|
| print | Allow printing |
| modify | Allow modifications |
| copy | Allow copying content |
| annotate | Allow annotations |

## Common Patterns

### Email-Optimized PDF

```python
result = pdf_compression_service.optimize_pdf_complete(
    pdf,
    options={
        'compression_level': 9,
        'optimize_images': True,
        'image_quality': 75,
        'image_dpi': 72
    }
)
```

### Print-Quality PDF

```python
result = pdf_compression_service.optimize_pdf_complete(
    pdf,
    options={
        'compression_level': 7,
        'optimize_images': True,
        'image_quality': 95,
        'image_dpi': 300
    }
)
```

### Secure PDF

```python
compressed = pdf_compression_service.compress_pdf(pdf)
encrypted = pdf_compression_service.encrypt_pdf(
    compressed,
    user_password="secret",
    permissions={'print': True, 'modify': False}
)
```

## Error Handling

```python
try:
    compressed = pdf_compression_service.compress_pdf(pdf)
except Exception as e:
    print(f"Compression failed: {e}")
```

## Performance Tips

- Use streaming for files > 10MB
- Lower compression level for faster processing
- Disable image optimization if not needed
- Use appropriate chunk sizes for streaming

## Requirements

- PyPDF2 or pypdf
- Pillow (PIL)
- ReportLab

---

**See Also**: [Full Documentation](PDF_COMPRESSION_GUIDE.md)
