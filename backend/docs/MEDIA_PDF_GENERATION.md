## Media PDF Generation Service

Comprehensive guide for generating PDF bytes from images and photos.

### Overview

The Media PDF Service provides powerful capabilities for converting images and photos into PDF documents with optimization, metadata handling, and various layout options.

### Features

- **Single Image to PDF**: Convert individual images to PDF with metadata
- **Photo Optimization**: Enhanced optimization for high-quality photos
- **Multi-Image PDFs**: Combine multiple images with flexible layouts
- **Image Galleries**: Create professional galleries with titles and descriptions
- **Metadata Extraction**: Automatic EXIF and image metadata extraction
- **Image Optimization**: Automatic resizing and compression for PDF

### Requirements

```python
# Required libraries
reportlab>=4.0.0
Pillow>=10.0.0
```

### Quick Start

#### Single Image to PDF

```python
from backend.services.media_pdf_service import image_to_pdf_bytes

# Convert image to PDF
pdf_bytes = image_to_pdf_bytes(
    "path/to/image.jpg",
    title="My Image",
    include_metadata=True,
    optimize=True
)

# Save PDF
with open("output.pdf", "wb") as f:
    f.write(pdf_bytes)
```

#### Photo to PDF with Description

```python
from backend.services.media_pdf_service import photo_to_pdf_bytes

# Convert photo with enhanced quality
pdf_bytes = photo_to_pdf_bytes(
    "path/to/photo.jpg",
    title="Sunset Over Mountains",
    description="A breathtaking view captured at golden hour"
)

# Save PDF
with open("photo.pdf", "wb") as f:
    f.write(pdf_bytes)
```

#### Multi-Image PDF

```python
from backend.services.media_pdf_service import multi_image_pdf

# Create PDF with multiple images
image_paths = [
    "image1.jpg",
    "image2.jpg",
    "image3.jpg",
    "image4.jpg"
]

# One image per page
pdf_bytes = multi_image_pdf(
    image_paths,
    title="My Photo Collection",
    layout="one_per_page"
)

# Two images per page
pdf_bytes = multi_image_pdf(
    image_paths,
    title="My Photo Collection",
    layout="two_per_page"
)

# Grid layout (4 per page)
pdf_bytes = multi_image_pdf(
    image_paths,
    title="My Photo Collection",
    layout="grid"
)
```

#### Image Gallery PDF

```python
from backend.services.media_pdf_service import image_gallery_pdf

# Create gallery with titles and descriptions
images = [
    {
        'path': 'photo1.jpg',
        'title': 'Mountain Sunrise',
        'description': 'Early morning light over the peaks'
    },
    {
        'path': 'photo2.jpg',
        'title': 'Forest Path',
        'description': 'A peaceful walk through nature'
    },
    {
        'path': 'photo3.jpg',
        'title': 'Ocean Waves',
        'description': 'The power of the sea'
    }
]

pdf_bytes = image_gallery_pdf(
    images,
    gallery_title="Nature Photography Gallery"
)
```

### Advanced Usage

#### Using the Service Class

```python
from backend.services.media_pdf_service import MediaPDFService
from backend.core.pdf_bytes import PDFMetadata

# Create service instance
service = MediaPDFService()

# Custom PDF metadata
metadata = PDFMetadata(
    title="My Image Collection",
    author="John Doe",
    subject="Photography",
    keywords=["nature", "landscape", "photography"]
)

# Generate PDF with custom metadata
pdf_bytes = service.image_to_pdf_bytes(
    "image.jpg",
    metadata=metadata,
    include_metadata=True,
    optimize=True
)
```

#### Image Optimization

```python
from backend.services.media_pdf_service import ImageOptimizer
from PIL import Image

# Create optimizer
optimizer = ImageOptimizer()

# Load image
image = Image.open("large_photo.jpg")

# Optimize for PDF
optimized = optimizer.optimize_for_pdf(
    image,
    max_width=1920,
    max_height=1080
)

# Compress to JPEG bytes
compressed = optimizer.compress_image(optimized, quality=85)
```

#### Metadata Extraction

```python
from backend.services.media_pdf_service import MediaPDFService
from PIL import Image

service = MediaPDFService()

# Load image
image = Image.open("photo.jpg")

# Extract metadata
metadata = service._extract_image_metadata(image, "photo.jpg")

# Access metadata
print(f"Dimensions: {metadata.get_dimensions_str()}")
print(f"Aspect Ratio: {metadata.get_aspect_ratio()}")
print(f"Format: {metadata.format}")
print(f"Size: {metadata.size_bytes / 1024:.1f} KB")

# Get as dictionary
metadata_dict = metadata.to_dict()
```

### Layout Options

#### One Per Page

Each image gets its own page with title and metadata table.

```python
pdf_bytes = multi_image_pdf(
    image_paths,
    layout="one_per_page"
)
```

**Best for:**
- Detailed image viewing
- Professional presentations
- Portfolio documents

#### Two Per Page

Two images per page, stacked vertically.

```python
pdf_bytes = multi_image_pdf(
    image_paths,
    layout="two_per_page"
)
```

**Best for:**
- Comparison documents
- Before/after presentations
- Space-efficient collections

#### Grid Layout

Four images per page in a 2x2 grid.

```python
pdf_bytes = multi_image_pdf(
    image_paths,
    layout="grid"
)
```

**Best for:**
- Contact sheets
- Quick reference documents
- Thumbnail collections

### Image Metadata

The service automatically extracts and includes:

- **Basic Metadata:**
  - Filename
  - Dimensions (width x height)
  - Format (JPEG, PNG, etc.)
  - Color mode (RGB, RGBA, etc.)
  - File size

- **EXIF Data** (when available):
  - Camera make and model
  - Date/time taken
  - Exposure settings
  - ISO speed
  - F-number
  - GPS coordinates

### Optimization Features

#### Automatic Optimization

- **Resizing**: Large images automatically resized to optimal dimensions
- **Format Conversion**: All images converted to RGB for PDF compatibility
- **Compression**: JPEG compression with quality control
- **Orientation**: Auto-rotation based on EXIF data
- **Sharpening**: Slight sharpness enhancement

#### Custom Optimization

```python
optimizer = ImageOptimizer()

# Set custom parameters
optimizer.max_width = 2400
optimizer.max_height = 1800
optimizer.quality = 90
optimizer.dpi = 300

# Optimize image
optimized = optimizer.optimize_for_pdf(image)
```

### Error Handling

```python
from backend.services.media_pdf_service import (
    MediaPDFService,
    REPORTLAB_AVAILABLE,
    PIL_AVAILABLE
)

# Check library availability
if not REPORTLAB_AVAILABLE:
    print("reportlab not installed")
    # Handle gracefully

if not PIL_AVAILABLE:
    print("Pillow not installed")
    # Handle gracefully

# Handle file errors
try:
    pdf_bytes = image_to_pdf_bytes("nonexistent.jpg")
except FileNotFoundError:
    print("Image file not found")
except Exception as e:
    print(f"Error: {e}")
```

### Performance Tips

1. **Optimize Before Batch Processing**
   ```python
   # Pre-optimize images for faster PDF generation
   optimizer = ImageOptimizer()
   optimized_images = [
       optimizer.optimize_for_pdf(Image.open(path))
       for path in image_paths
   ]
   ```

2. **Use Appropriate Layouts**
   - Grid layout is fastest for many images
   - One per page provides best quality

3. **Control Image Quality**
   ```python
   # Lower quality for smaller files
   optimizer.quality = 75  # Default is 85
   
   # Higher quality for professional use
   optimizer.quality = 95
   ```

4. **Limit Image Dimensions**
   ```python
   # Smaller max dimensions = faster processing
   optimizer.max_width = 1280
   optimizer.max_height = 720
   ```

### Integration Examples

#### With File Upload

```python
from fastapi import UploadFile

async def upload_and_convert(file: UploadFile):
    # Save uploaded file
    temp_path = f"temp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    # Convert to PDF
    pdf_bytes = image_to_pdf_bytes(temp_path)
    
    # Clean up
    os.remove(temp_path)
    
    return pdf_bytes
```

#### With Database Storage

```python
def store_image_pdf(image_path: str, db_session):
    # Generate PDF
    pdf_bytes = image_to_pdf_bytes(image_path)
    
    # Store in database
    pdf_record = PDFDocument(
        filename=f"{Path(image_path).stem}.pdf",
        content=pdf_bytes,
        size=len(pdf_bytes),
        created_at=datetime.now()
    )
    
    db_session.add(pdf_record)
    db_session.commit()
```

#### With API Endpoint

```python
from fastapi import APIRouter, Response

router = APIRouter()

@router.post("/api/v1/images/to-pdf")
async def convert_image_to_pdf(image_path: str):
    pdf_bytes = image_to_pdf_bytes(image_path)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=image.pdf"
        }
    )
```

### Testing

```python
import pytest
from backend.services.media_pdf_service import MediaPDFService

def test_image_to_pdf():
    service = MediaPDFService()
    pdf_bytes = service.image_to_pdf_bytes("test_image.jpg")
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b'%PDF')

def test_multi_image_pdf():
    service = MediaPDFService()
    images = ["img1.jpg", "img2.jpg", "img3.jpg"]
    
    pdf_bytes = service.multi_image_pdf(images, layout="grid")
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
```

### Troubleshooting

#### Issue: "reportlab not installed"

```bash
pip install reportlab
```

#### Issue: "Pillow not installed"

```bash
pip install Pillow
```

#### Issue: Large PDF file sizes

```python
# Reduce quality
optimizer = ImageOptimizer()
optimizer.quality = 70
optimizer.max_width = 1280
optimizer.max_height = 720
```

#### Issue: Slow processing

```python
# Use grid layout for many images
pdf_bytes = multi_image_pdf(
    image_paths,
    layout="grid"  # Faster than one_per_page
)
```

### Best Practices

1. **Always optimize images** before PDF generation
2. **Include metadata** for professional documents
3. **Use appropriate layouts** based on use case
4. **Handle errors gracefully** with try-except blocks
5. **Clean up temporary files** after processing
6. **Test with various image formats** (JPEG, PNG, etc.)
7. **Validate image paths** before processing
8. **Use meaningful titles** and descriptions
9. **Consider file size** vs quality tradeoffs
10. **Cache optimized images** for repeated use

### API Reference

See the full API documentation in the service file docstrings.

### Related Services

- **ChartPDFService**: Generate PDFs from charts
- **PDFByteMixin**: Base PDF generation functionality
- **UniversalDataService**: Unified data and PDF management

### Support

For issues or questions:
- Check the demo file: `backend/demo_media_pdf.py`
- Run tests: `pytest backend/tests/test_media_pdf_service.py`
- Review examples in this documentation
