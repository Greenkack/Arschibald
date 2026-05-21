"""
PDF Compression Service Demonstration

This script demonstrates all features of the PDF compression service.
"""

import io
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image

from services.pdf_compression_service import pdf_compression_service


def create_sample_pdf() -> bytes:
    """Create a sample PDF for demonstration"""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    
    # Add multiple pages
    for i in range(5):
        pdf.drawString(100, 800, f"Page {i + 1}")
        pdf.drawString(100, 750, "This is a demonstration PDF")
        pdf.drawString(100, 700, "It contains multiple pages with text and images")
        
        # Add some shapes
        pdf.rect(100, 500, 400, 100, fill=1)
        pdf.circle(300, 400, 50, fill=1)
        
        pdf.showPage()
    
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def create_pdf_with_image() -> bytes:
    """Create a PDF with embedded image"""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    
    # Create a large test image
    img = Image.new('RGB', (2000, 1500), color='blue')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    pdf.drawString(100, 800, "PDF with High-Resolution Image")
    pdf.drawImage(img_buffer, 100, 300, width=400, height=300)
    pdf.showPage()
    
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def demo_basic_compression():
    """Demonstrate basic PDF compression"""
    print("\n" + "="*80)
    print("DEMO 1: Basic PDF Compression")
    print("="*80)
    
    # Create sample PDF
    pdf = create_sample_pdf()
    print(f"Original PDF size: {len(pdf):,} bytes")
    
    # Compress PDF
    compressed = pdf_compression_service.compress_pdf(pdf)
    print(f"Compressed PDF size: {len(compressed):,} bytes")
    
    reduction = (1 - len(compressed) / len(pdf)) * 100
    print(f"Size reduction: {reduction:.1f}%")
    
    # Verify PDF is still valid
    info = pdf_compression_service.get_pdf_info(compressed)
    print(f"Pages in compressed PDF: {info['num_pages']}")


def demo_image_optimization():
    """Demonstrate image optimization"""
    print("\n" + "="*80)
    print("DEMO 2: Image Optimization")
    print("="*80)
    
    # Create PDF with image
    pdf = create_pdf_with_image()
    print(f"Original PDF size: {len(pdf):,} bytes")
    
    # Compress with image optimization
    compressed = pdf_compression_service.compress_pdf(
        pdf,
        optimize_images=True,
        image_quality=75,
        image_dpi=150
    )
    print(f"Compressed PDF size: {len(compressed):,} bytes")
    
    reduction = (1 - len(compressed) / len(pdf)) * 100
    print(f"Size reduction: {reduction:.1f}%")


def demo_compression_levels():
    """Demonstrate different compression levels"""
    print("\n" + "="*80)
    print("DEMO 3: Compression Levels")
    print("="*80)
    
    pdf = create_sample_pdf()
    print(f"Original PDF size: {len(pdf):,} bytes\n")
    
    for level in [0, 3, 6, 9]:
        compressed = pdf_compression_service.compress_pdf(
            pdf,
            compression_level=level
        )
        reduction = (1 - len(compressed) / len(pdf)) * 100
        print(f"Level {level}: {len(compressed):,} bytes ({reduction:.1f}% reduction)")


def demo_font_optimization():
    """Demonstrate font optimization"""
    print("\n" + "="*80)
    print("DEMO 4: Font Optimization")
    print("="*80)
    
    pdf = create_sample_pdf()
    print(f"Original PDF size: {len(pdf):,} bytes")
    
    # Optimize fonts
    optimized = pdf_compression_service.optimize_fonts(
        pdf,
        subset_fonts=True,
        embed_fonts=True
    )
    print(f"Optimized PDF size: {len(optimized):,} bytes")
    
    reduction = (1 - len(optimized) / len(pdf)) * 100
    print(f"Size reduction: {reduction:.1f}%")


def demo_streaming():
    """Demonstrate PDF streaming"""
    print("\n" + "="*80)
    print("DEMO 5: PDF Streaming")
    print("="*80)
    
    pdf = create_sample_pdf()
    print(f"PDF size: {len(pdf):,} bytes")
    
    # Stream with different chunk sizes
    for chunk_size in [1024, 4096, 8192]:
        chunks = list(pdf_compression_service.stream_pdf(pdf, chunk_size=chunk_size))
        print(f"Chunk size {chunk_size}: {len(chunks)} chunks")


def demo_encryption():
    """Demonstrate PDF encryption"""
    print("\n" + "="*80)
    print("DEMO 6: PDF Encryption")
    print("="*80)
    
    pdf = create_sample_pdf()
    
    # Encrypt with password
    encrypted = pdf_compression_service.encrypt_pdf(
        pdf,
        user_password="user123",
        owner_password="owner456",
        permissions={
            'print': True,
            'modify': False,
            'copy': False,
            'annotate': False
        }
    )
    
    print(f"Original PDF size: {len(pdf):,} bytes")
    print(f"Encrypted PDF size: {len(encrypted):,} bytes")
    
    # Verify encryption
    info = pdf_compression_service.get_pdf_info(encrypted)
    print(f"Is encrypted: {info['is_encrypted']}")


def demo_metadata():
    """Demonstrate metadata management"""
    print("\n" + "="*80)
    print("DEMO 7: Metadata Management")
    print("="*80)
    
    pdf = create_sample_pdf()
    
    # Add metadata
    metadata = {
        '/Title': 'Demonstration PDF',
        '/Author': 'Solar Calculator Pro',
        '/Subject': 'PDF Compression Demo',
        '/Keywords': 'compression, optimization, demo',
        '/Creator': 'PDF Compression Service',
        '/Producer': 'Solar Calculator Pro'
    }
    
    updated = pdf_compression_service.manage_metadata(pdf, metadata=metadata)
    
    # Get info
    info = pdf_compression_service.get_pdf_info(updated)
    print("Metadata added:")
    for key, value in info['metadata'].items():
        print(f"  {key}: {value}")


def demo_complete_optimization():
    """Demonstrate complete optimization"""
    print("\n" + "="*80)
    print("DEMO 8: Complete Optimization")
    print("="*80)
    
    pdf = create_pdf_with_image()
    
    # Complete optimization
    result = pdf_compression_service.optimize_pdf_complete(
        pdf,
        options={
            'compression_level': 9,
            'optimize_images': True,
            'image_quality': 85,
            'image_dpi': 150,
            'optimize_fonts': True,
            'add_metadata': True,
            'metadata': {
                '/Title': 'Fully Optimized PDF',
                '/Author': 'Demo Script'
            }
        }
    )
    
    print(f"Original size: {result['original_size_bytes']:,} bytes")
    print(f"Optimized size: {result['optimized_size_bytes']:,} bytes")
    print(f"Size reduction: {result['size_reduction_bytes']:,} bytes")
    print(f"Reduction percentage: {result['size_reduction_percent']:.1f}%")
    print(f"\nOriginal pages: {result['original_info']['num_pages']}")
    print(f"Optimized pages: {result['optimized_info']['num_pages']}")


def demo_pdf_info():
    """Demonstrate PDF information extraction"""
    print("\n" + "="*80)
    print("DEMO 9: PDF Information")
    print("="*80)
    
    pdf = create_sample_pdf()
    info = pdf_compression_service.get_pdf_info(pdf)
    
    print(f"Number of pages: {info['num_pages']}")
    print(f"Size: {info['size_bytes']:,} bytes ({info['size_kb']:.2f} KB, {info['size_mb']:.2f} MB)")
    print(f"Is encrypted: {info['is_encrypted']}")
    print(f"\nPage sizes:")
    for i, size in enumerate(info['page_sizes']):
        print(f"  Page {i + 1}: {size['width']:.1f} x {size['height']:.1f} points")


def main():
    """Run all demonstrations"""
    print("\n" + "="*80)
    print("PDF COMPRESSION SERVICE DEMONSTRATION")
    print("="*80)
    
    try:
        demo_basic_compression()
        demo_image_optimization()
        demo_compression_levels()
        demo_font_optimization()
        demo_streaming()
        demo_encryption()
        demo_metadata()
        demo_complete_optimization()
        demo_pdf_info()
        
        print("\n" + "="*80)
        print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"\nError during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
