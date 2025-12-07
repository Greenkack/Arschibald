"""
Demo: Media PDF Service

Demonstrates image and photo PDF byte generation capabilities.

Requirements: 14.8
Task: 227
"""

import sys
import os
from pathlib import Path
from PIL import Image
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.media_pdf_service import (
    MediaPDFService,
    ImageMetadata,
    ImageOptimizer,
    image_to_pdf_bytes,
    photo_to_pdf_bytes,
    multi_image_pdf,
    image_gallery_pdf,
    REPORTLAB_AVAILABLE,
    PIL_AVAILABLE
)


def create_demo_images(output_dir: Path) -> list:
    """Create demo images for testing"""
    output_dir.mkdir(exist_ok=True)
    
    images = []
    colors = [
        ('red', (255, 0, 0)),
        ('green', (0, 255, 0)),
        ('blue', (0, 0, 255)),
        ('yellow', (255, 255, 0)),
        ('purple', (128, 0, 128)),
        ('orange', (255, 165, 0))
    ]
    
    for name, color in colors:
        img = Image.new('RGB', (800, 600), color=color)
        img_path = output_dir / f"demo_{name}.jpg"
        img.save(img_path, 'JPEG', quality=90)
        images.append(img_path)
        print(f" Created {img_path.name}")
    
    return images


def demo_single_image_to_pdf():
    """Demo: Convert single image to PDF"""
    print("\n" + "="*60)
    print("DEMO 1: Single Image to PDF")
    print("="*60)
    
    if not (REPORTLAB_AVAILABLE and PIL_AVAILABLE):
        print(" Required libraries not available")
        return
    
    # Create demo image
    demo_dir = Path("backend/demo_output")
    demo_dir.mkdir(exist_ok=True)
    
    img = Image.new('RGB', (1024, 768), color='skyblue')
    img_path = demo_dir / "demo_single.jpg"
    img.save(img_path, 'JPEG')
    
    print(f"\n Created demo image: {img_path}")
    
    # Convert to PDF
    pdf_bytes = image_to_pdf_bytes(
        img_path,
        title="Demo Single Image",
        include_metadata=True,
        optimize=True
    )
    
    # Save PDF
    pdf_path = demo_dir / "demo_single_image.pdf"
    pdf_path.write_bytes(pdf_bytes)
    
    print(f" Generated PDF: {pdf_path}")
    print(f"  Size: {len(pdf_bytes) / 1024:.1f} KB")
    print(f"  Includes metadata: Yes")
    print(f"  Optimized: Yes")


def demo_photo_to_pdf():
    """Demo: Convert photo to PDF with enhanced optimization"""
    print("\n" + "="*60)
    print("DEMO 2: Photo to PDF with Metadata")
    print("="*60)
    
    if not (REPORTLAB_AVAILABLE and PIL_AVAILABLE):
        print(" Required libraries not available")
        return
    
    # Create demo photo
    demo_dir = Path("backend/demo_output")
    demo_dir.mkdir(exist_ok=True)
    
    img = Image.new('RGB', (1920, 1080), color='forestgreen')
    img_path = demo_dir / "demo_photo.jpg"
    img.save(img_path, 'JPEG', quality=95)
    
    print(f"\n Created demo photo: {img_path}")
    
    # Convert to PDF
    pdf_bytes = photo_to_pdf_bytes(
        img_path,
        title="Beautiful Landscape",
        description="A stunning view of the forest at sunset"
    )
    
    # Save PDF
    pdf_path = demo_dir / "demo_photo.pdf"
    pdf_path.write_bytes(pdf_bytes)
    
    print(f" Generated PDF: {pdf_path}")
    print(f"  Size: {len(pdf_bytes) / 1024:.1f} KB")
    print(f"  Title: Beautiful Landscape")
    print(f"  Description: Included")


def demo_multi_image_pdf():
    """Demo: Multi-image PDF with different layouts"""
    print("\n" + "="*60)
    print("DEMO 3: Multi-Image PDF (Different Layouts)")
    print("="*60)
    
    if not (REPORTLAB_AVAILABLE and PIL_AVAILABLE):
        print(" Required libraries not available")
        return
    
    # Create demo images
    demo_dir = Path("backend/demo_output")
    images = create_demo_images(demo_dir)
    
    print(f"\n Created {len(images)} demo images")
    
    # Layout 1: One per page
    print("\n Layout 1: One image per page")
    pdf_bytes_1 = multi_image_pdf(
        images,
        title="Image Collection - One Per Page",
        layout="one_per_page"
    )
    pdf_path_1 = demo_dir / "demo_multi_one_per_page.pdf"
    pdf_path_1.write_bytes(pdf_bytes_1)
    print(f"   Generated: {pdf_path_1.name} ({len(pdf_bytes_1) / 1024:.1f} KB)")
    
    # Layout 2: Two per page
    print("\n Layout 2: Two images per page")
    pdf_bytes_2 = multi_image_pdf(
        images,
        title="Image Collection - Two Per Page",
        layout="two_per_page"
    )
    pdf_path_2 = demo_dir / "demo_multi_two_per_page.pdf"
    pdf_path_2.write_bytes(pdf_bytes_2)
    print(f"   Generated: {pdf_path_2.name} ({len(pdf_bytes_2) / 1024:.1f} KB)")
    
    # Layout 3: Grid (4 per page)
    print("\n Layout 3: Grid layout (4 per page)")
    pdf_bytes_3 = multi_image_pdf(
        images,
        title="Image Collection - Grid",
        layout="grid"
    )
    pdf_path_3 = demo_dir / "demo_multi_grid.pdf"
    pdf_path_3.write_bytes(pdf_bytes_3)
    print(f"   Generated: {pdf_path_3.name} ({len(pdf_bytes_3) / 1024:.1f} KB)")


def demo_image_gallery():
    """Demo: Image gallery PDF with titles and descriptions"""
    print("\n" + "="*60)
    print("DEMO 4: Image Gallery PDF")
    print("="*60)
    
    if not (REPORTLAB_AVAILABLE and PIL_AVAILABLE):
        print(" Required libraries not available")
        return
    
    # Create demo images
    demo_dir = Path("backend/demo_output")
    image_paths = create_demo_images(demo_dir)
    
    # Create gallery data
    gallery_images = [
        {
            'path': str(image_paths[0]),
            'title': 'Sunset Over Mountains',
            'description': 'A breathtaking view of the sunset casting warm colors over the mountain range.'
        },
        {
            'path': str(image_paths[1]),
            'title': 'Forest Path',
            'description': 'A peaceful path winding through the dense forest.'
        },
        {
            'path': str(image_paths[2]),
            'title': 'Ocean Waves',
            'description': 'The powerful waves of the ocean crashing against the shore.'
        },
        {
            'path': str(image_paths[3]),
            'title': 'Desert Dunes',
            'description': 'Golden sand dunes stretching as far as the eye can see.'
        },
        {
            'path': str(image_paths[4]),
            'title': 'Mountain Lake',
            'description': 'A crystal clear lake reflecting the surrounding mountains.'
        },
        {
            'path': str(image_paths[5]),
            'title': 'Autumn Colors',
            'description': 'Vibrant autumn foliage painting the landscape in warm hues.'
        }
    ]
    
    print(f"\n  Creating gallery with {len(gallery_images)} images")
    
    # Generate gallery PDF
    pdf_bytes = image_gallery_pdf(
        gallery_images,
        gallery_title="Nature Photography Gallery"
    )
    
    # Save PDF
    pdf_path = demo_dir / "demo_image_gallery.pdf"
    pdf_path.write_bytes(pdf_bytes)
    
    print(f" Generated gallery PDF: {pdf_path}")
    print(f"  Size: {len(pdf_bytes) / 1024:.1f} KB")
    print(f"  Images: {len(gallery_images)}")
    print(f"  Includes: Titles, descriptions, and metadata")


def demo_image_optimization():
    """Demo: Image optimization for PDF"""
    print("\n" + "="*60)
    print("DEMO 5: Image Optimization")
    print("="*60)
    
    if not PIL_AVAILABLE:
        print(" Pillow not available")
        return
    
    # Create large image
    print("\n Creating large test image...")
    large_img = Image.new('RGB', (4000, 3000), color='coral')
    
    print(f"  Original size: {large_img.width} x {large_img.height} px")
    
    # Optimize
    optimizer = ImageOptimizer()
    optimized = optimizer.optimize_for_pdf(large_img, max_width=1920, max_height=1080)
    
    print(f"  Optimized size: {optimized.width} x {optimized.height} px")
    print(f"  Reduction: {(1 - (optimized.width * optimized.height) / (large_img.width * large_img.height)) * 100:.1f}%")
    
    # Compress
    compressed = optimizer.compress_image(optimized, quality=85)
    print(f"  Compressed size: {len(compressed) / 1024:.1f} KB")
    
    print("\n Optimization complete")


def demo_metadata_extraction():
    """Demo: Image metadata extraction"""
    print("\n" + "="*60)
    print("DEMO 6: Image Metadata Extraction")
    print("="*60)
    
    if not (REPORTLAB_AVAILABLE and PIL_AVAILABLE):
        print(" Required libraries not available")
        return
    
    # Create demo image
    demo_dir = Path("backend/demo_output")
    demo_dir.mkdir(exist_ok=True)
    
    img = Image.new('RGB', (1280, 720), color='teal')
    img_path = demo_dir / "demo_metadata.jpg"
    img.save(img_path, 'JPEG', quality=90)
    
    print(f"\n Extracting metadata from: {img_path.name}")
    
    # Extract metadata
    service = MediaPDFService()
    image = Image.open(img_path)
    metadata = service._extract_image_metadata(image, img_path.name)
    
    print("\nExtracted Metadata:")
    print(f"  Filename: {metadata.filename}")
    print(f"  Dimensions: {metadata.get_dimensions_str()}")
    print(f"  Format: {metadata.format}")
    print(f"  Mode: {metadata.mode}")
    print(f"  Size: {metadata.size_bytes / 1024:.1f} KB")
    print(f"  Aspect Ratio: {metadata.get_aspect_ratio():.2f}")
    
    # Convert to dict
    metadata_dict = metadata.to_dict()
    print(f"\n Metadata dictionary has {len(metadata_dict)} fields")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("MEDIA PDF SERVICE DEMO")
    print("Image and Photo PDF Byte Generation")
    print("="*60)
    
    if not REPORTLAB_AVAILABLE:
        print("\n  Warning: reportlab not installed")
        print("   Install with: pip install reportlab")
    
    if not PIL_AVAILABLE:
        print("\n  Warning: Pillow not installed")
        print("   Install with: pip install Pillow")
    
    if not (REPORTLAB_AVAILABLE and PIL_AVAILABLE):
        print("\n Cannot run demos without required libraries")
        return
    
    try:
        # Run demos
        demo_single_image_to_pdf()
        demo_photo_to_pdf()
        demo_multi_image_pdf()
        demo_image_gallery()
        demo_image_optimization()
        demo_metadata_extraction()
        
        print("\n" + "="*60)
        print(" ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\n Output files saved to: backend/demo_output/")
        print("\nGenerated PDFs:")
        print("  • demo_single_image.pdf - Single image with metadata")
        print("  • demo_photo.pdf - Photo with title and description")
        print("  • demo_multi_one_per_page.pdf - One image per page")
        print("  • demo_multi_two_per_page.pdf - Two images per page")
        print("  • demo_multi_grid.pdf - Grid layout (4 per page)")
        print("  • demo_image_gallery.pdf - Full gallery with descriptions")
        
    except Exception as e:
        print(f"\n Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
