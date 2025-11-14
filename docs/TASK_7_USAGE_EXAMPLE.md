# Task 7: PDF Integration - Usage Examples

## Example 1: Basic PDF Generation with 3D Visualization

```python
from pdf_generator import PDFGenerator

# Prepare offer data
offer_data = {
    'offer_id': 'PV-2025-001',
    'date': '2025-01-30',
    'customer': {
        'name': 'Max Mustermann',
        'address': 'Musterstraße 123, 12345 Musterstadt'
    },
    'project_data': {
        'project_details': {
            'building_type': 'Einfamilienhaus',
            'roof_type': 'Satteldach',
            'roof_orientation': 'Süd',
            'roof_inclination_deg': 35.0,
            'roof_covering_type': 'Ziegel',
            'building_length_m': 12.0,
            'building_width_m': 8.0,
            'wall_height_m': 6.5
        }
    },
    'module_quantity': 25,
    'items': [
        {
            'description': 'PV-Module 400W',
            'quantity': 25,
            'unit_price': 250.0,
            'total': 6250.0
        },
        {
            'description': 'Wechselrichter 10kW',
            'quantity': 1,
            'unit_price': 2500.0,
            'total': 2500.0
        }
    ],
    'grand_total': 8750.0
}

# Define module order (including 3D visualization)
module_order = [
    {"id": "deckblatt"},
    {"id": "anschreiben"},
    {"id": "angebotspositionen"},
    {"id": "3d_visualisierung"},  # 3D visualization section
    {"id": "technische_daten"},
    {"id": "wirtschaftlichkeit"},
    {"id": "preisaufstellung"}
]

# Generate PDF
generator = PDFGenerator(
    offer_data=offer_data,
    module_order=module_order,
    theme_name="default",
    filename="angebot_mit_3d.pdf"
)

generator.generate_pdf()
print("PDF mit 3D-Visualisierung erstellt: angebot_mit_3d.pdf")
```

## Example 2: Custom 3D Image in PDF

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from utils.pdf_visual_inject import make_pv3d_image_flowable
from utils.pv3d import BuildingDims, LayoutConfig

# Create PDF document
doc = SimpleDocTemplate("custom_3d.pdf")
story = []
styles = getSampleStyleSheet()

# Add title
story.append(Paragraph("PV-Anlagen Visualisierung", styles['Title']))
story.append(Spacer(1, 1*cm))

# Prepare 3D visualization data
project_data = {
    'project_details': {
        'roof_type': 'Flachdach',
        'roof_orientation': 'Süd',
        'roof_inclination_deg': 0.0,
        'roof_covering_type': 'Bitumen'
    }
}

dims = BuildingDims(
    length_m=15.0,
    width_m=10.0,
    wall_height_m=7.0
)

layout = LayoutConfig(
    mode="auto",
    use_garage=False,
    use_facade=False
)

# Generate 3D image
image_flowable = make_pv3d_image_flowable(
    project_data=project_data,
    dims=dims,
    roof_type="Flachdach",
    module_quantity=30,
    layout_config=layout,
    width_cm=17.0
)

if image_flowable:
    story.append(image_flowable)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Abb. 1: 3D-Visualisierung der geplanten PV-Anlage auf Flachdach",
        styles['Normal']
    ))
else:
    story.append(Paragraph(
        "3D-Visualisierung konnte nicht erstellt werden.",
        styles['Normal']
    ))

# Build PDF
doc.build(story)
print("Custom PDF erstellt: custom_3d.pdf")
```

## Example 3: Direct PNG Bytes Access

```python
from utils.pdf_visual_inject import get_pv3d_png_bytes_for_pdf
from utils.pv3d import BuildingDims, LayoutConfig

# Prepare data
dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
layout = LayoutConfig(mode="auto")
project_data = {
    'project_details': {
        'roof_type': 'Satteldach',
        'roof_orientation': 'Süd',
        'roof_inclination_deg': 35.0
    }
}

# Get PNG bytes
png_bytes = get_pv3d_png_bytes_for_pdf(
    project_data=project_data,
    dims=dims,
    roof_type="Satteldach",
    module_quantity=20,
    layout_config=layout
)

if png_bytes:
    # Save to file
    with open("3d_visualization.png", "wb") as f:
        f.write(png_bytes)
    print(f"PNG saved: {len(png_bytes)} bytes")
    
    # Or use in custom PDF processing
    from io import BytesIO
    from reportlab.platypus import Image
    
    img_buffer = BytesIO(png_bytes)
    img = Image(img_buffer, width=17*cm, height=10.625*cm)
    # Add to your PDF story...
else:
    print("Failed to generate 3D visualization")
```

## Example 4: Manual Layout Configuration

```python
from utils.pdf_visual_inject import make_pv3d_image_flowable
from utils.pv3d import BuildingDims, LayoutConfig

# Create custom layout with garage and facade
dims = BuildingDims(length_m=12.0, width_m=8.0, wall_height_m=6.0)

layout = LayoutConfig(
    mode="manual",
    use_garage=True,
    use_facade=True,
    removed_indices=[0, 1, 5, 10],  # Remove specific modules
    garage_dims=(6.0, 3.0, 3.0),
    offset_main_xy=(0.0, 0.0),
    offset_garage_xy=(0.0, 0.0)
)

project_data = {
    'project_details': {
        'roof_type': 'Walmdach',
        'roof_orientation': 'West',
        'roof_inclination_deg': 30.0,
        'roof_covering_type': 'Schiefer'
    }
}

# Generate image with custom layout
image_flowable = make_pv3d_image_flowable(
    project_data=project_data,
    dims=dims,
    roof_type="Walmdach",
    module_quantity=40,
    layout_config=layout,
    width_cm=17.0
)

# Use in PDF...
```

## Example 5: Error Handling

```python
from utils.pdf_visual_inject import make_pv3d_image_flowable
from utils.pv3d import BuildingDims, LayoutConfig

def add_3d_visualization_to_pdf(story, project_data, styles):
    """
    Safely add 3D visualization to PDF with error handling
    """
    try:
        # Extract or use default dimensions
        dims = BuildingDims(
            length_m=project_data.get('building_length', 10.0),
            width_m=project_data.get('building_width', 6.0),
            wall_height_m=project_data.get('wall_height', 6.0)
        )
        
        layout = LayoutConfig(mode="auto")
        
        # Generate image
        image_flowable = make_pv3d_image_flowable(
            project_data=project_data,
            dims=dims,
            roof_type=project_data.get('roof_type', 'Flachdach'),
            module_quantity=project_data.get('module_quantity', 20),
            layout_config=layout,
            width_cm=17.0
        )
        
        if image_flowable:
            story.append(Paragraph("3D-Visualisierung", styles['Heading1']))
            story.append(Spacer(1, 0.5*cm))
            story.append(image_flowable)
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(
                "Abb.: 3D-Darstellung der geplanten PV-Anlage",
                styles['Normal']
            ))
            return True
        else:
            # Rendering failed, add placeholder
            story.append(Paragraph("3D-Visualisierung", styles['Heading1']))
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph(
                "Die 3D-Visualisierung konnte nicht erstellt werden. "
                "Bitte kontaktieren Sie uns für weitere Details.",
                styles['Normal']
            ))
            return False
            
    except Exception as e:
        # Log error and continue
        print(f"Error adding 3D visualization: {e}")
        story.append(Paragraph(
            "3D-Visualisierung vorübergehend nicht verfügbar.",
            styles['Normal']
        ))
        return False

# Usage
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("safe_pdf.pdf")
story = []
styles = getSampleStyleSheet()

project_data = {...}  # Your project data

success = add_3d_visualization_to_pdf(story, project_data, styles)
if success:
    print("3D visualization added successfully")
else:
    print("PDF generated without 3D visualization")

doc.build(story)
```

## Configuration Options

### BuildingDims Parameters
- `length_m`: Building length in meters (default: 10.0)
- `width_m`: Building width in meters (default: 6.0)
- `wall_height_m`: Wall height in meters (default: 6.0)

### LayoutConfig Parameters
- `mode`: "auto" or "manual" (default: "auto")
- `use_garage`: Add garage if modules don't fit (default: False)
- `use_facade`: Add facade modules if needed (default: False)
- `removed_indices`: List of module indices to remove (manual mode)
- `garage_dims`: Garage dimensions (L, W, H) in meters
- `offset_main_xy`: Main building offset (x, y)
- `offset_garage_xy`: Garage offset (x, y)

### Image Parameters
- `width_cm`: Image width in centimeters (default: 17.0)
- Aspect ratio: Fixed at 16:10 (1600×1000 pixels)
- Format: PNG
- Resolution: 1600×1000 pixels

## Troubleshooting

### Issue: "3D-Visualisierung nicht verfügbar"
**Solution**: Install PyVista and VTK:
```bash
pip install pyvista vtk
```

### Issue: Image not appearing in PDF
**Solution**: Check that:
1. PyVista is installed
2. project_data contains valid building information
3. module_quantity > 0
4. No exceptions in console output

### Issue: PDF generation fails
**Solution**: The integration is designed to fail gracefully. Check:
1. ReportLab is installed
2. File permissions for output directory
3. Console for specific error messages

## Performance Notes

- 3D rendering takes 1-2 seconds per image
- Off-screen rendering doesn't require display
- Images are generated at 1600×1000 resolution
- PNG compression keeps file sizes reasonable (typically 100-300 KB)

## Best Practices

1. **Always provide fallback**: Check if image_flowable is None
2. **Use sensible defaults**: Provide default building dimensions
3. **Log errors**: Capture exceptions for debugging
4. **Test without 3D**: Ensure PDF generates even if 3D fails
5. **Cache if possible**: Generate 3D images once, reuse in multiple PDFs
