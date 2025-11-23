# 3D Export Formats Guide

## Overview

The Solar Calculator Pro application supports exporting 3D PV system models in multiple formats for various use cases including 3D printing, CAD software, web visualization, and documentation.

## Supported Formats

### 1. STL (Stereolithography)

**File Extension:** `.stl`  
**MIME Type:** `model/stl`  
**Binary:** Yes

**Description:**
STL is the standard format for 3D printing. It represents 3D geometry as a collection of triangular faces.

**Use Cases:**
- 3D printing of physical models
- Import into CAD software
- Manufacturing and prototyping
- Structural analysis

**Export Options:**
```python
{
    "binary": True,  # Binary STL (smaller file size)
    "ascii": False   # ASCII STL (human-readable)
}
```

**Example API Call:**
```bash
curl -X POST "http://localhost:8000/api/v1/export-3d/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "stl",
    "building_dims": {
      "length_m": 10.0,
      "width_m": 6.0,
      "wall_height_m": 6.0
    },
    "roof_config": {
      "type": "gable",
      "angle": 30.0,
      "orientation": "south"
    },
    "module_config": {
      "count": 20
    }
  }' \
  --output model.stl
```

---

### 2. OBJ (Wavefront)

**File Extension:** `.obj`  
**MIME Type:** `model/obj`  
**Binary:** No (Text-based)

**Description:**
OBJ is a universal 3D format supported by virtually all 3D modeling software. It's human-readable and can include material definitions.

**Use Cases:**
- Import into 3D modeling software (Blender, Maya, 3ds Max)
- Animation and rendering
- Game development
- Architectural visualization

**Export Options:**
```python
{
    "include_mtl": True,  # Include material file
    "include_normals": True,  # Include vertex normals
    "include_textures": False  # Include texture coordinates
}
```

**Example API Call:**
```bash
curl -X POST "http://localhost:8000/api/v1/export-3d/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "obj",
    "building_dims": {...},
    "roof_config": {...},
    "module_config": {...}
  }' \
  --output model.obj
```

---

### 3. GLTF/GLB (GL Transmission Format)

**File Extensions:** `.gltf` (JSON), `.glb` (Binary)  
**MIME Types:** `model/gltf+json`, `model/gltf-binary`  
**Binary:** GLB is binary, GLTF is JSON

**Description:**
GLTF is optimized for web and real-time applications. It's the "JPEG of 3D" - efficient, compact, and widely supported.

**Use Cases:**
- Web-based 3D viewers
- Augmented Reality (AR) applications
- Virtual Reality (VR) experiences
- Real-time rendering engines
- Mobile applications

**Export Options:**
```python
{
    "binary": True,  # Export as GLB (binary) vs GLTF (JSON)
    "embed_images": True,  # Embed textures in file
    "compress": True  # Apply Draco compression
}
```

**Example API Call (GLB):**
```bash
curl -X POST "http://localhost:8000/api/v1/export-3d/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "glb",
    "building_dims": {...},
    "roof_config": {...},
    "module_config": {...}
  }' \
  --output model.glb
```

**Example API Call (GLTF):**
```bash
curl -X POST "http://localhost:8000/api/v1/export-3d/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "gltf",
    "building_dims": {...},
    "roof_config": {...},
    "module_config": {...}
  }' \
  --output model.gltf
```

---

### 4. DXF (Drawing Exchange Format)

**File Extension:** `.dxf`  
**MIME Type:** `application/dxf`  
**Binary:** No (Text-based)

**Description:**
DXF is AutoCAD's exchange format, widely supported by CAD software. Perfect for architectural and engineering applications.

**Use Cases:**
- Import into AutoCAD
- Architectural planning
- Engineering drawings
- Construction documentation
- Technical specifications

**Export Options:**
```python
{
    "version": "R2018",  # DXF version (R12, R2000, R2018, etc.)
    "units": "Meters",  # Drawing units
    "include_layers": True,  # Organize by layers
    "precision": 3  # Decimal precision
}
```

**Layers:**
- `Building_Base`: Building footprint
- `Walls`: Building walls
- `Roof`: Roof structure
- `Roof_Ridge`: Roof ridge line (for gable roofs)
- `Roof_Face1`, `Roof_Face2`: Roof faces
- `PV_Modules`: Solar panel modules

**Example API Call:**
```bash
curl -X POST "http://localhost:8000/api/v1/export-3d/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "dxf",
    "building_dims": {...},
    "roof_config": {...},
    "module_config": {...},
    "options": {
      "version": "R2018",
      "units": "Meters"
    }
  }' \
  --output model.dxf
```

---

### 5. PDF 3D

**File Extension:** `.pdf`  
**MIME Type:** `application/pdf`  
**Binary:** Yes

**Description:**
PDF with embedded 3D model preview and project information. Perfect for documentation and presentations.

**Use Cases:**
- Project documentation
- Client presentations
- Technical reports
- Archival purposes
- Sharing with non-technical stakeholders

**Export Options:**
```python
{
    "include_3d_data": True,  # Embed 3D model data
    "image_quality": "high",  # Preview image quality (low, medium, high)
    "page_size": "A4",  # PDF page size
    "include_metadata": True  # Include project metadata
}
```

**PDF Contents:**
- Title and project information
- Building dimensions
- Roof configuration
- Module count and specifications
- High-quality 3D preview image
- Embedded 3D model data (optional)

**Example API Call:**
```bash
curl -X POST "http://localhost:8000/api/v1/export-3d/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf",
    "building_dims": {...},
    "roof_config": {...},
    "module_config": {...},
    "options": {
      "include_3d_data": true,
      "image_quality": "high"
    }
  }' \
  --output model.pdf
```

---

### 6. PNG/JPG (Images)

**File Extensions:** `.png`, `.jpg`  
**MIME Types:** `image/png`, `image/jpeg`  
**Binary:** Yes

**Description:**
High-quality raster images of the 3D model. Perfect for documentation, presentations, and web use.

**Use Cases:**
- Documentation and reports
- Presentations and proposals
- Website and marketing materials
- Social media sharing
- Email attachments

**Export Options:**
```python
{
    "width": 1920,  # Image width in pixels
    "height": 1080,  # Image height in pixels
    "scale": 2.0,  # Scaling factor for higher resolution
    "quality": 95,  # JPEG quality (1-100, only for JPG)
    "transparent": False  # Transparent background (PNG only)
}
```

**Example API Call (PNG):**
```bash
curl -X POST "http://localhost:8000/api/v1/export-3d/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "png",
    "building_dims": {...},
    "roof_config": {...},
    "module_config": {...},
    "options": {
      "width": 1920,
      "height": 1080,
      "scale": 2.0
    }
  }' \
  --output model.png
```

**Example API Call (JPG):**
```bash
curl -X POST "http://localhost:8000/api/v1/export-3d/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "jpg",
    "building_dims": {...},
    "roof_config": {...},
    "module_config": {...},
    "options": {
      "width": 1920,
      "height": 1080,
      "quality": 90
    }
  }' \
  --output model.jpg
```

---

## API Reference

### Get Supported Formats

```http
GET /api/v1/export-3d/formats
```

**Response:**
```json
{
  "stl": true,
  "obj": true,
  "gltf": true,
  "glb": true,
  "dxf": true,
  "pdf": true,
  "png": true,
  "jpg": true
}
```

### Get Format Information

```http
GET /api/v1/export-3d/formats/{format}
```

**Response:**
```json
{
  "name": "STL (Stereolithography)",
  "description": "Standard format for 3D printing",
  "mime_type": "model/stl",
  "extension": ".stl",
  "use_cases": ["3D printing", "CAD import", "Manufacturing"],
  "binary": true,
  "supported": true
}
```

### Export 3D Model

```http
POST /api/v1/export-3d/export
```

**Request Body:**
```json
{
  "format": "stl",
  "project_data": {},
  "building_dims": {
    "length_m": 10.0,
    "width_m": 6.0,
    "wall_height_m": 6.0
  },
  "roof_config": {
    "type": "gable",
    "angle": 30.0,
    "orientation": "south"
  },
  "module_config": {
    "count": 20,
    "spacing": 0.02,
    "margin": 0.5
  },
  "options": {}
}
```

**Response:**
Binary file data with appropriate Content-Type header.

---

## Format Comparison

| Format | File Size | Quality | Compatibility | Best For |
|--------|-----------|---------|---------------|----------|
| STL | Medium | High | Excellent | 3D Printing |
| OBJ | Medium | High | Excellent | 3D Modeling |
| GLTF | Small | High | Good | Web/AR/VR |
| GLB | Small | High | Good | Web/AR/VR |
| DXF | Small | Medium | Excellent | CAD Software |
| PDF | Large | Medium | Universal | Documentation |
| PNG | Medium | High | Universal | Images |
| JPG | Small | Medium | Universal | Images |

---

## Best Practices

### 1. Choose the Right Format

- **3D Printing:** Use STL
- **CAD Software:** Use DXF or OBJ
- **Web Visualization:** Use GLB
- **Documentation:** Use PDF or PNG
- **Presentations:** Use PNG or JPG

### 2. Optimize File Size

- Use binary formats (STL, GLB) for smaller files
- Adjust image resolution based on use case
- Use JPEG for smaller image files (with quality trade-off)

### 3. Quality Settings

- Use high resolution (1920x1080 or higher) for presentations
- Use medium resolution (1280x720) for web
- Use low resolution (800x600) for thumbnails

### 4. Error Handling

Always check the response status:
- 200: Success
- 400: Invalid request (unsupported format, invalid parameters)
- 500: Server error (export failed)

---

## Troubleshooting

### Format Not Supported

**Error:** "Format 'xyz' is not supported"

**Solution:** Check available formats with `GET /api/v1/export-3d/formats`

### Export Failed

**Error:** "Export failed: ..."

**Possible Causes:**
1. Invalid building dimensions (must be > 0)
2. Invalid roof angle (must be 0-90 degrees)
3. Invalid module count (must be > 0)
4. Missing required dependencies

**Solution:** Validate input parameters and check server logs

### Large File Size

**Problem:** Exported file is too large

**Solutions:**
1. Use binary formats (GLB instead of GLTF)
2. Reduce image resolution
3. Use JPEG instead of PNG for images
4. Reduce module count for testing

---

## Dependencies

The following Python packages are required for full format support:

```
trimesh>=3.20.0  # For OBJ, GLTF/GLB export
ezdxf>=1.0.0     # For DXF export
reportlab>=3.6.0 # For PDF export
Pillow>=9.0.0    # For image processing
plotly>=5.0.0    # For 3D visualization
```

Install with:
```bash
pip install trimesh ezdxf reportlab Pillow plotly
```

---

## Examples

See the `backend/demo_export_3d.py` file for complete working examples of all export formats.

---

## Support

For issues or questions:
- Check the API documentation: `/docs`
- Review server logs for detailed error messages
- Contact support with export request details
