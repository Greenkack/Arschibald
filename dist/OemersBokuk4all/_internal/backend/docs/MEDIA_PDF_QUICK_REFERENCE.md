# Media PDF Service - Quick Reference

## Installation

```bash
pip install reportlab Pillow
```

## Basic Usage

### Single Image to PDF

```python
from backend.services.media_pdf_service import image_to_pdf_bytes

pdf_bytes = image_to_pdf_bytes("image.jpg")
```

### Photo with Title and Description

```python
from backend.services.media_pdf_service import photo_to_pdf_bytes

pdf_bytes = photo_to_pdf_bytes(
    "photo.jpg",
    title="Sunset",
    description="Beautiful sunset over mountains"
)
```

### Multiple Images

```python
from backend.services.media_pdf_service import multi_image_pdf

# One per page
pdf_bytes = multi_image_pdf(
    ["img1.jpg", "img2.jpg", "img3.jpg"],
    layout="one_per_page"
)

# Two per page
pdf_bytes = multi_image_pdf(
    ["img1.jpg", "img2.jpg", "img3.jpg"],
    layout="two_per_page"
)

# Grid (4 per page)
pdf_bytes = multi_image_pdf(
    ["img1.jpg", "img2.jpg", "img3.jpg"],
    layout="grid"
)
```

### Image Gallery

```python
from backend.services.media_pdf_service import image_gallery_pdf

images = [
    {
        'path': 'photo1.jpg',
        'title': 'Mountain View',
        'description': 'Sunrise over peaks'
    },
    {
        'path': 'photo2.jpg',
        'title': 'Forest Path',
        'description': 'Peaceful woodland trail'
    }
]

pdf_bytes = image_gallery_pdf(images, gallery_title="My Gallery")
```

## Service Class

```python
from backend.services.media_pdf_service import MediaPDFService

service = MediaPDFService()

# Single image
pdf_bytes = service.image_to_pdf_bytes(
    "image.jpg",
    include_metadata=True,
    optimize=True
)

# Photo
pdf_bytes = service.photo_to_pdf_bytes(
    "photo.jpg",
    title="Title",
    description="Description"
)

# Multi-image
pdf_bytes = service.multi_image_pdf(
    ["img1.jpg", "img2.jpg"],
    title="Collection",
    layout="one_per_page"
)

# Gallery
pdf_bytes = service.image_gallery_pdf(
    images,
    gallery_title="Gallery"
)
```

## Image Optimization

```python
from backend.services.media_pdf_service import ImageOptimizer
from PIL import Image

optimizer = ImageOptimizer()

# Load image
image = Image.open("photo.jpg")

# Optimize
optimized = optimizer.optimize_for_pdf(
    image,
    max_width=1920,
    max_height=1080
)

# Compress
compressed = optimizer.compress_image(optimized, quality=85)
```

## Metadata Extraction

```python
from backend.services.media_pdf_service import MediaPDFService
from PIL import Image

service = MediaPDFService()
image = Image.open("photo.jpg")

metadata = service._extract_image_metadata(image, "photo.jpg")

print(metadata.get_dimensions_str())  # "1920 x 1080 px"
print(metadata.get_aspect_ratio())    # 1.77
print(metadata.format)                # "JPEG"
print(metadata.size_bytes)            # File size in bytes
```

## Layout Options

| Layout | Images per Page | Best For |
|--------|----------------|----------|
| `one_per_page` | 1 | Detailed viewing, portfolios |
| `two_per_page` | 2 | Comparisons, before/after |
| `grid` | 4 | Contact sheets, thumbnails |

## Common Parameters

### image_to_pdf_bytes()

```python
pdf_bytes = image_to_pdf_bytes(
    image_path,              # Required: Path to image
    title=None,              # Optional: PDF title
    include_metadata=True,   # Include image metadata table
    optimize=True            # Optimize image for PDF
)
```

### photo_to_pdf_bytes()

```python
pdf_bytes = photo_to_pdf_bytes(
    photo_path,              # Required: Path to photo
    title="",                # Photo title
    description=""           # Photo description
)
```

### multi_image_pdf()

```python
pdf_bytes = multi_image_pdf(
    image_paths,             # Required: List of image paths
    title="Image Collection", # Document title
    layout="one_per_page"    # Layout: one_per_page, two_per_page, grid
)
```

### image_gallery_pdf()

```python
pdf_bytes = image_gallery_pdf(
    images,                  # Required: List of dicts with path, title, description
    gallery_title="Gallery"  # Gallery title
)
```

## Error Handling

```python
from backend.services.media_pdf_service import (
    REPORTLAB_AVAILABLE,
    PIL_AVAILABLE
)

if not REPORTLAB_AVAILABLE:
    print("Install reportlab: pip install reportlab")

if not PIL_AVAILABLE:
    print("Install Pillow: pip install Pillow")

try:
    pdf_bytes = image_to_pdf_bytes("image.jpg")
except FileNotFoundError:
    print("Image not found")
except Exception as e:
    print(f"Error: {e}")
```

## Optimization Settings

```python
optimizer = ImageOptimizer()

# Adjust settings
optimizer.max_width = 1920      # Max width in pixels
optimizer.max_height = 1080     # Max height in pixels
optimizer.quality = 85          # JPEG quality (1-100)
optimizer.dpi = 150             # DPI for PDF
```

## Save PDF to File

```python
# Get PDF bytes
pdf_bytes = image_to_pdf_bytes("image.jpg")

# Save to file
with open("output.pdf", "wb") as f:
    f.write(pdf_bytes)

# Or using Path
from pathlib import Path
Path("output.pdf").write_bytes(pdf_bytes)
```

## FastAPI Integration

```python
from fastapi import APIRouter, Response

router = APIRouter()

@router.post("/images/to-pdf")
async def convert_image(image_path: str):
    pdf_bytes = image_to_pdf_bytes(image_path)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=image.pdf"
        }
    )
```

## Testing

```python
import pytest

def test_image_to_pdf():
    pdf_bytes = image_to_pdf_bytes("test.jpg")
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b'%PDF')

def test_multi_image():
    pdf_bytes = multi_image_pdf(
        ["img1.jpg", "img2.jpg"],
        layout="grid"
    )
    assert len(pdf_bytes) > 0
```

## Performance Tips

1. **Use grid layout** for many images (fastest)
2. **Lower quality** for smaller files (quality=70)
3. **Reduce max dimensions** for faster processing
4. **Pre-optimize** images before batch processing
5. **Clean up** temporary files after use

## Common Use Cases

### Portfolio PDF

```python
images = [
    {'path': f'portfolio_{i}.jpg', 'title': f'Project {i}', 'description': '...'}
    for i in range(1, 11)
]
pdf_bytes = image_gallery_pdf(images, "My Portfolio")
```

### Product Catalog

```python
products = ["product1.jpg", "product2.jpg", "product3.jpg"]
pdf_bytes = multi_image_pdf(products, "Product Catalog", layout="grid")
```

### Before/After Comparison

```python
images = ["before.jpg", "after.jpg"]
pdf_bytes = multi_image_pdf(images, "Renovation", layout="two_per_page")
```

### Photo Album

```python
photos = [
    {'path': 'vacation1.jpg', 'title': 'Beach Day', 'description': 'Sunny afternoon'},
    {'path': 'vacation2.jpg', 'title': 'Mountain Hike', 'description': 'Summit view'}
]
pdf_bytes = image_gallery_pdf(photos, "Vacation 2024")
```

## Requirements

- Python 3.10+
- reportlab >= 4.0.0
- Pillow >= 10.0.0

## Related

- `ChartPDFService` - Generate PDFs from charts
- `PDFByteMixin` - Base PDF functionality
- `UniversalDataService` - Unified data management
