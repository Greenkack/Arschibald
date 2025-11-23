"""
3D Export Demo Script

Demonstrates all available 3D export formats.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.export_3d_service import Export3DService


def demo_all_formats():
    """Demonstrate all export formats."""
    
    print("=" * 80)
    print("3D Export Formats Demo")
    print("=" * 80)
    print()
    
    # Initialize service
    service = Export3DService()
    
    # Sample project data
    project_data = {}
    
    building_dims = {
        "length_m": 10.0,
        "width_m": 6.0,
        "wall_height_m": 6.0
    }
    
    roof_config = {
        "type": "gable",
        "angle": 30.0,
        "orientation": "south"
    }
    
    module_config = {
        "count": 20,
        "spacing": 0.02,
        "margin": 0.5
    }
    
    # Check supported formats
    print("Supported Formats:")
    print("-" * 80)
    for format_name, supported in service.supported_formats.items():
        status = "✓" if supported else "✗"
        print(f"  {status} {format_name.upper()}")
    print()
    
    # Demo each format
    formats_to_demo = ["stl", "obj", "gltf", "glb", "dxf", "pdf", "png", "jpg"]
    
    for format_name in formats_to_demo:
        if not service.is_format_supported(format_name):
            print(f"⊘ Skipping {format_name.upper()} (not supported)")
            continue
        
        print(f"Exporting {format_name.upper()}...")
        print("-" * 80)
        
        try:
            # Get format info
            info = service.get_format_info(format_name)
            print(f"  Name: {info['name']}")
            print(f"  Description: {info['description']}")
            print(f"  Use Cases: {', '.join(info['use_cases'])}")
            
            # Export
            file_bytes = service.export(
                format=format_name,
                project_data=project_data,
                building_dims=building_dims,
                roof_config=roof_config,
                module_config=module_config
            )
            
            # Save to file
            output_file = f"demo_model.{format_name}"
            with open(output_file, 'wb') as f:
                f.write(file_bytes)
            
            file_size_kb = len(file_bytes) / 1024
            print(f"  ✓ Exported: {output_file} ({file_size_kb:.1f} KB)")
            print()
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()
    
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)


def demo_stl_export():
    """Demonstrate STL export with options."""
    
    print("\n" + "=" * 80)
    print("STL Export Demo")
    print("=" * 80)
    print()
    
    service = Export3DService()
    
    project_data = {}
    building_dims = {"length_m": 10.0, "width_m": 6.0, "wall_height_m": 6.0}
    roof_config = {"type": "flat", "angle": 0.0, "orientation": "south"}
    module_config = {"count": 15}
    
    # Export STL
    print("Exporting STL for 3D printing...")
    stl_bytes = service.export_stl(
        project_data=project_data,
        building_dims=building_dims,
        roof_config=roof_config,
        module_config=module_config,
        options={"binary": True}
    )
    
    with open("model_for_printing.stl", 'wb') as f:
        f.write(stl_bytes)
    
    print(f"✓ STL exported: model_for_printing.stl ({len(stl_bytes) / 1024:.1f} KB)")
    print("  Ready for 3D printing!")


def demo_dxf_export():
    """Demonstrate DXF export for CAD."""
    
    print("\n" + "=" * 80)
    print("DXF Export Demo")
    print("=" * 80)
    print()
    
    service = Export3DService()
    
    project_data = {}
    building_dims = {"length_m": 12.0, "width_m": 8.0, "wall_height_m": 7.0}
    roof_config = {"type": "gable", "angle": 35.0, "orientation": "south"}
    module_config = {"count": 24}
    
    # Export DXF
    print("Exporting DXF for AutoCAD...")
    dxf_bytes = service.export_dxf(
        project_data=project_data,
        building_dims=building_dims,
        roof_config=roof_config,
        module_config=module_config,
        options={"version": "R2018", "units": "Meters"}
    )
    
    with open("model_for_cad.dxf", 'wb') as f:
        f.write(dxf_bytes)
    
    print(f"✓ DXF exported: model_for_cad.dxf ({len(dxf_bytes) / 1024:.1f} KB)")
    print("  Layers: Building_Base, Walls, Roof, PV_Modules")
    print("  Ready for AutoCAD import!")


def demo_web_export():
    """Demonstrate GLB export for web."""
    
    print("\n" + "=" * 80)
    print("GLB Export Demo (Web 3D)")
    print("=" * 80)
    print()
    
    service = Export3DService()
    
    project_data = {}
    building_dims = {"length_m": 10.0, "width_m": 6.0, "wall_height_m": 6.0}
    roof_config = {"type": "gable", "angle": 30.0, "orientation": "south"}
    module_config = {"count": 20}
    
    # Export GLB
    print("Exporting GLB for web visualization...")
    glb_bytes = service.export_gltf(
        project_data=project_data,
        building_dims=building_dims,
        roof_config=roof_config,
        module_config=module_config,
        binary=True,
        options={"compress": True}
    )
    
    with open("model_for_web.glb", 'wb') as f:
        f.write(glb_bytes)
    
    print(f"✓ GLB exported: model_for_web.glb ({len(glb_bytes) / 1024:.1f} KB)")
    print("  Ready for web 3D viewers, AR, and VR!")


def demo_image_export():
    """Demonstrate high-quality image export."""
    
    print("\n" + "=" * 80)
    print("Image Export Demo")
    print("=" * 80)
    print()
    
    service = Export3DService()
    
    project_data = {}
    building_dims = {"length_m": 10.0, "width_m": 6.0, "wall_height_m": 6.0}
    roof_config = {"type": "gable", "angle": 30.0, "orientation": "south"}
    module_config = {"count": 20}
    
    # Export PNG (high quality)
    print("Exporting high-quality PNG...")
    png_bytes = service.export_image(
        project_data=project_data,
        building_dims=building_dims,
        roof_config=roof_config,
        module_config=module_config,
        format="png",
        options={"width": 1920, "height": 1080, "scale": 2.0}
    )
    
    with open("model_highres.png", 'wb') as f:
        f.write(png_bytes)
    
    print(f"✓ PNG exported: model_highres.png ({len(png_bytes) / 1024:.1f} KB)")
    
    # Export JPG (compressed)
    print("Exporting compressed JPG...")
    jpg_bytes = service.export_image(
        project_data=project_data,
        building_dims=building_dims,
        roof_config=roof_config,
        module_config=module_config,
        format="jpg",
        options={"width": 1920, "height": 1080, "quality": 85}
    )
    
    with open("model_compressed.jpg", 'wb') as f:
        f.write(jpg_bytes)
    
    print(f"✓ JPG exported: model_compressed.jpg ({len(jpg_bytes) / 1024:.1f} KB)")
    print("  Ready for presentations and documentation!")


def demo_pdf_export():
    """Demonstrate PDF 3D export."""
    
    print("\n" + "=" * 80)
    print("PDF 3D Export Demo")
    print("=" * 80)
    print()
    
    service = Export3DService()
    
    project_data = {}
    building_dims = {"length_m": 10.0, "width_m": 6.0, "wall_height_m": 6.0}
    roof_config = {"type": "gable", "angle": 30.0, "orientation": "south"}
    module_config = {"count": 20}
    
    # Export PDF
    print("Exporting PDF with 3D model...")
    pdf_bytes = service.export_pdf_3d(
        project_data=project_data,
        building_dims=building_dims,
        roof_config=roof_config,
        module_config=module_config,
        options={"include_3d_data": True, "image_quality": "high"}
    )
    
    with open("model_documentation.pdf", 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✓ PDF exported: model_documentation.pdf ({len(pdf_bytes) / 1024:.1f} KB)")
    print("  Includes project info, 3D preview, and embedded model data!")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Solar Calculator Pro - 3D Export Demo")
    print("=" * 80)
    
    # Run all demos
    demo_all_formats()
    demo_stl_export()
    demo_dxf_export()
    demo_web_export()
    demo_image_export()
    demo_pdf_export()
    
    print("\n" + "=" * 80)
    print("All demos complete!")
    print("Check the current directory for exported files.")
    print("=" * 80)
