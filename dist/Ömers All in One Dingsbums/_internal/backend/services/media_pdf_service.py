"""
Media PDF Bytes Generation Service

This service provides comprehensive PDF byte generation for images and photos
with optimization, metadata handling, and gallery export capabilities.

Requirements: 14.8
Task: 227
"""

import io
import base64
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path

from backend.core.pdf_bytes import (
    PDFMetadata,
    PDFRenderingEngine,
    REPORTLAB_AVAILABLE
)

if REPORTLAB_AVAILABLE:
    from reportlab.lib.pagesizes import A4, letter, landscape
    from reportlab.lib.units import cm, mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image as RLImage,
        PageBreak,
        KeepTogether
    )
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas

try:
    from PIL import Image, ImageOps, ImageEnhance
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow not installed. Image optimization will be limited.")


class ImageMetadata:
    """Container for image metadata"""

    def __init__(
        self,
        filename: str,
        width: int,
        height: int,
        format: str,
        mode: str,
        size_bytes: int,
        exif_data: Optional[Dict[str, Any]] = None,
        description: str = "",
        title: str = "",
        tags: List[str] = None
    ):
        self.filename = filename
        self.width = width
        self.height = height
        self.format = format
        self.mode = mode
        self.size_bytes = size_bytes
        self.exif_data = exif_data or {}
        self.description = description
        self.title = title or filename
        self.tags = tags or []
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            'filename': self.filename,
            'width': self.width,
            'height': self.height,
            'format': self.format,
            'mode': self.mode,
            'size_bytes': self.size_bytes,
            'size_mb': round(self.size_bytes / (1024 * 1024), 2),
            'exif_data': self.exif_data,
            'description': self.description,
            'title': self.title,
            'tags': self.tags,
            'created_at': self.created_at.isoformat()
        }

    def get_dimensions_str(self) -> str:
        """Get dimensions as string"""
        return f"{self.width} x {self.height} px"

    def get_aspect_ratio(self) -> float:
        """Calculate aspect ratio"""
        return self.width / self.height if self.height > 0 else 1.0


class ImageOptimizer:
    """Image optimization for PDF generation"""

    def __init__(self):
        self.max_width = 1920
        self.max_height = 1080
        self.quality = 85
        self.dpi = 150

    def optimize_for_pdf(
        self,
        image: 'Image.Image',
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ) -> 'Image.Image':
        """
        Optimize image for PDF inclusion.

        Args:
            image: PIL Image object
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels

        Returns:
            Optimized PIL Image
        """
        if not PIL_AVAILABLE:
            return image

        # Use provided dimensions or defaults
        max_w = max_width or self.max_width
        max_h = max_height or self.max_height

        # Convert to RGB if necessary
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')

        # Resize if too large
        if image.width > max_w or image.height > max_h:
            image.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

        # Auto-orient based on EXIF
        image = ImageOps.exif_transpose(image)

        # Enhance sharpness slightly
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)

        return image

    def compress_image(
        self,
        image: 'Image.Image',
        quality: Optional[int] = None
    ) -> bytes:
        """
        Compress image to JPEG bytes.

        Args:
            image: PIL Image object
            quality: JPEG quality (1-100)

        Returns:
            Compressed image bytes
        """
        if not PIL_AVAILABLE:
            return b''

        buffer = io.BytesIO()
        q = quality or self.quality

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        image.save(buffer, format='JPEG', quality=q, optimize=True)
        buffer.seek(0)
        return buffer.getvalue()


class MediaPDFService:
    """
    Service for generating PDF bytes from images and photos.

    Features:
    - Single image to PDF conversion
    - Photo optimization for PDF
    - Image metadata extraction and inclusion
    - Multi-image PDF generation
    - Image gallery PDF export
    """

    def __init__(self):
        self.engine = PDFRenderingEngine()
        self.optimizer = ImageOptimizer()
        self.page_width = A4[0] if REPORTLAB_AVAILABLE else 595
        self.page_height = A4[1] if REPORTLAB_AVAILABLE else 842

    def image_to_pdf_bytes(
        self,
        image_path: Union[str, Path],
        metadata: Optional[PDFMetadata] = None,
        include_metadata: bool = True,
        optimize: bool = True
    ) -> bytes:
        """
        Convert a single image to PDF bytes.

        Args:
            image_path: Path to image file
            metadata: Optional PDF metadata
            include_metadata: Include image metadata in PDF
            optimize: Optimize image for PDF

        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE or not PIL_AVAILABLE:
            raise ImportError("reportlab and Pillow required for image PDF generation")

        # Load image
        image_path = Path(image_path)
        image = Image.open(image_path)

        # Extract image metadata
        img_metadata = self._extract_image_metadata(image, image_path.name)

        # Optimize if requested
        if optimize:
            image = self.optimizer.optimize_for_pdf(image)

        # Create PDF
        buffer = io.BytesIO()

        if metadata is None:
            metadata = PDFMetadata(
                title=f"Image - {img_metadata.title}",
                subject="Image Document"
            )

        doc = self.engine.create_document(buffer, metadata)
        story = []

        # Add title
        story.append(self._create_title(img_metadata.title))
        story.append(Spacer(1, 10))

        # Add image
        img_element = self._create_image_element(image, img_metadata)
        story.append(img_element)
        story.append(Spacer(1, 20))

        # Add metadata table if requested
        if include_metadata:
            story.append(self._create_metadata_table(img_metadata))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def photo_to_pdf_bytes(
        self,
        photo_path: Union[str, Path],
        title: str = "",
        description: str = "",
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Convert a photo to PDF with enhanced optimization.

        Args:
            photo_path: Path to photo file
            title: Photo title
            description: Photo description
            metadata: Optional PDF metadata

        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE or not PIL_AVAILABLE:
            raise ImportError("reportlab and Pillow required for photo PDF generation")

        # Load photo
        photo_path = Path(photo_path)
        photo = Image.open(photo_path)

        # Extract metadata
        img_metadata = self._extract_image_metadata(photo, photo_path.name)
        if title:
            img_metadata.title = title
        if description:
            img_metadata.description = description

        # Optimize for photo quality
        photo = self.optimizer.optimize_for_pdf(photo, max_width=2400, max_height=1800)

        # Create PDF
        buffer = io.BytesIO()

        if metadata is None:
            metadata = PDFMetadata(
                title=f"Photo - {img_metadata.title}",
                subject="Photo Document"
            )

        doc = self.engine.create_document(buffer, metadata)
        story = []

        # Add title
        story.append(self._create_title(img_metadata.title))
        story.append(Spacer(1, 10))

        # Add description if provided
        if img_metadata.description:
            story.append(self._create_description(img_metadata.description))
            story.append(Spacer(1, 10))

        # Add photo
        img_element = self._create_image_element(photo, img_metadata, max_width=18*cm)
        story.append(img_element)
        story.append(Spacer(1, 20))

        # Add metadata
        story.append(self._create_photo_metadata_table(img_metadata))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def multi_image_pdf(
        self,
        image_paths: List[Union[str, Path]],
        title: str = "Image Collection",
        layout: str = "one_per_page",
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF with multiple images.

        Args:
            image_paths: List of image file paths
            title: Document title
            layout: Layout style ('one_per_page', 'two_per_page', 'grid')
            metadata: Optional PDF metadata

        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE or not PIL_AVAILABLE:
            raise ImportError("reportlab and Pillow required for multi-image PDF")

        buffer = io.BytesIO()

        if metadata is None:
            metadata = PDFMetadata(
                title=title,
                subject="Multi-Image Document"
            )

        doc = self.engine.create_document(buffer, metadata)
        story = []

        # Add cover page
        story.append(self._create_cover_page(title, len(image_paths)))
        story.append(PageBreak())

        # Add images based on layout
        if layout == "one_per_page":
            story.extend(self._layout_one_per_page(image_paths))
        elif layout == "two_per_page":
            story.extend(self._layout_two_per_page(image_paths))
        elif layout == "grid":
            story.extend(self._layout_grid(image_paths))
        else:
            raise ValueError(f"Unknown layout: {layout}")

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def image_gallery_pdf(
        self,
        images: List[Dict[str, Any]],
        gallery_title: str = "Image Gallery",
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF image gallery with titles and descriptions.

        Args:
            images: List of dicts with 'path', 'title', 'description'
            gallery_title: Gallery title
            metadata: Optional PDF metadata

        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE or not PIL_AVAILABLE:
            raise ImportError("reportlab and Pillow required for gallery PDF")

        buffer = io.BytesIO()

        if metadata is None:
            metadata = PDFMetadata(
                title=gallery_title,
                subject="Image Gallery"
            )

        doc = self.engine.create_document(buffer, metadata)
        story = []

        # Add gallery cover
        story.append(self._create_gallery_cover(gallery_title, len(images)))
        story.append(PageBreak())

        # Add each image with its info
        for i, img_info in enumerate(images):
            img_path = Path(img_info['path'])
            img_title = img_info.get('title', img_path.name)
            img_desc = img_info.get('description', '')

            # Load and optimize image
            image = Image.open(img_path)
            img_metadata = self._extract_image_metadata(image, img_path.name)
            img_metadata.title = img_title
            img_metadata.description = img_desc

            image = self.optimizer.optimize_for_pdf(image)

            # Create gallery entry
            entry = self._create_gallery_entry(image, img_metadata, i + 1)
            story.extend(entry)

            # Page break after each image except last
            if i < len(images) - 1:
                story.append(PageBreak())

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _extract_image_metadata(
        self,
        image: 'Image.Image',
        filename: str
    ) -> ImageMetadata:
        """Extract metadata from image"""
        if not PIL_AVAILABLE:
            return ImageMetadata(
                filename=filename,
                width=0,
                height=0,
                format="unknown",
                mode="unknown",
                size_bytes=0
            )

        # Basic metadata
        width, height = image.size
        format_str = image.format or "unknown"
        mode = image.mode

        # EXIF data
        exif_data = {}
        try:
            exif = image._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = str(value)
        except (AttributeError, KeyError):
            pass

        # Estimate size
        buffer = io.BytesIO()
        image.save(buffer, format=format_str if format_str != "unknown" else "PNG")
        size_bytes = buffer.tell()

        return ImageMetadata(
            filename=filename,
            width=width,
            height=height,
            format=format_str,
            mode=mode,
            size_bytes=size_bytes,
            exif_data=exif_data
        )

    def _create_image_element(
        self,
        image: 'Image.Image',
        img_metadata: ImageMetadata,
        max_width: Optional[float] = None,
        max_height: Optional[float] = None
    ) -> RLImage:
        """Create ReportLab image element"""
        # Save image to buffer
        buffer = io.BytesIO()
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(buffer, format='JPEG', quality=self.optimizer.quality)
        buffer.seek(0)

        # Calculate dimensions
        max_w = max_width or (self.page_width - 4*cm)
        max_h = max_height or (self.page_height - 8*cm)

        # Maintain aspect ratio
        aspect = img_metadata.get_aspect_ratio()
        if img_metadata.width > max_w or img_metadata.height > max_h:
            if aspect > 1:  # Landscape
                width = max_w
                height = width / aspect
            else:  # Portrait
                height = max_h
                width = height * aspect
        else:
            width = img_metadata.width
            height = img_metadata.height

        # Create image element
        img_element = RLImage(buffer, width=width, height=height)
        return img_element

    def _create_title(self, title: str) -> Paragraph:
        """Create title paragraph"""
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ImageTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=10,
            alignment=TA_CENTER
        )
        return Paragraph(title, title_style)

    def _create_description(self, description: str) -> Paragraph:
        """Create description paragraph"""
        styles = getSampleStyleSheet()
        desc_style = ParagraphStyle(
            'ImageDescription',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        return Paragraph(description, desc_style)

    def _create_metadata_table(self, img_metadata: ImageMetadata) -> Table:
        """Create metadata table"""
        data = [
            ['Property', 'Value'],
            ['Filename', img_metadata.filename],
            ['Dimensions', img_metadata.get_dimensions_str()],
            ['Format', img_metadata.format],
            ['Size', f"{img_metadata.size_bytes / 1024:.1f} KB"],
        ]

        table = Table(data, colWidths=[8*cm, 10*cm])
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]
        table.setStyle(TableStyle(style))
        return table

    def _create_photo_metadata_table(self, img_metadata: ImageMetadata) -> Table:
        """Create detailed photo metadata table"""
        data = [
            ['Property', 'Value'],
            ['Filename', img_metadata.filename],
            ['Dimensions', img_metadata.get_dimensions_str()],
            ['Format', img_metadata.format],
            ['Size', f"{img_metadata.size_bytes / (1024*1024):.2f} MB"],
            ['Aspect Ratio', f"{img_metadata.get_aspect_ratio():.2f}"],
        ]

        # Add EXIF data if available
        if img_metadata.exif_data:
            for key in ['DateTime', 'Make', 'Model', 'FNumber', 'ExposureTime', 'ISOSpeedRatings']:
                if key in img_metadata.exif_data:
                    data.append([key, img_metadata.exif_data[key]])

        table = Table(data, colWidths=[8*cm, 10*cm])
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]
        table.setStyle(TableStyle(style))
        return table

    def _create_cover_page(self, title: str, image_count: int) -> KeepTogether:
        """Create cover page for multi-image PDF"""
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CoverTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        subtitle_style = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#4a4a4a'),
            alignment=TA_CENTER
        )
        
        elements = [
            Spacer(1, 8*cm),
            Paragraph(title, title_style),
            Spacer(1, 20),
            Paragraph(f"{image_count} Images", subtitle_style),
            Spacer(1, 10),
            Paragraph(datetime.now().strftime("%B %d, %Y"), subtitle_style),
        ]
        
        return KeepTogether(elements)

    def _create_gallery_cover(self, title: str, image_count: int) -> KeepTogether:
        """Create gallery cover page"""
        return self._create_cover_page(title, image_count)

    def _create_gallery_entry(
        self,
        image: 'Image.Image',
        img_metadata: ImageMetadata,
        index: int
    ) -> List:
        """Create gallery entry with image and info"""
        elements = []
        
        # Entry number and title
        styles = getSampleStyleSheet()
        entry_title_style = ParagraphStyle(
            'EntryTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=10
        )
        
        elements.append(Paragraph(f"{index}. {img_metadata.title}", entry_title_style))
        elements.append(Spacer(1, 10))
        
        # Description if available
        if img_metadata.description:
            elements.append(self._create_description(img_metadata.description))
            elements.append(Spacer(1, 10))
        
        # Image
        img_element = self._create_image_element(image, img_metadata, max_width=16*cm)
        elements.append(img_element)
        elements.append(Spacer(1, 15))
        
        # Metadata
        elements.append(self._create_metadata_table(img_metadata))
        
        return elements

    def _layout_one_per_page(self, image_paths: List[Union[str, Path]]) -> List:
        """Layout with one image per page"""
        elements = []
        
        for i, img_path in enumerate(image_paths):
            img_path = Path(img_path)
            image = Image.open(img_path)
            img_metadata = self._extract_image_metadata(image, img_path.name)
            image = self.optimizer.optimize_for_pdf(image)
            
            # Title
            elements.append(self._create_title(img_metadata.title))
            elements.append(Spacer(1, 20))
            
            # Image
            img_element = self._create_image_element(image, img_metadata)
            elements.append(img_element)
            elements.append(Spacer(1, 20))
            
            # Metadata
            elements.append(self._create_metadata_table(img_metadata))
            
            # Page break except for last image
            if i < len(image_paths) - 1:
                elements.append(PageBreak())
        
        return elements

    def _layout_two_per_page(self, image_paths: List[Union[str, Path]]) -> List:
        """Layout with two images per page"""
        elements = []
        
        for i in range(0, len(image_paths), 2):
            # First image
            img_path1 = Path(image_paths[i])
            image1 = Image.open(img_path1)
            img_metadata1 = self._extract_image_metadata(image1, img_path1.name)
            image1 = self.optimizer.optimize_for_pdf(image1)
            
            elements.append(self._create_title(img_metadata1.title))
            elements.append(Spacer(1, 10))
            img_element1 = self._create_image_element(
                image1, img_metadata1, max_width=16*cm, max_height=10*cm
            )
            elements.append(img_element1)
            elements.append(Spacer(1, 20))
            
            # Second image if available
            if i + 1 < len(image_paths):
                img_path2 = Path(image_paths[i + 1])
                image2 = Image.open(img_path2)
                img_metadata2 = self._extract_image_metadata(image2, img_path2.name)
                image2 = self.optimizer.optimize_for_pdf(image2)
                
                elements.append(self._create_title(img_metadata2.title))
                elements.append(Spacer(1, 10))
                img_element2 = self._create_image_element(
                    image2, img_metadata2, max_width=16*cm, max_height=10*cm
                )
                elements.append(img_element2)
            
            # Page break except for last page
            if i + 2 < len(image_paths):
                elements.append(PageBreak())
        
        return elements

    def _layout_grid(self, image_paths: List[Union[str, Path]]) -> List:
        """Layout with grid of images (4 per page)"""
        elements = []
        
        for i in range(0, len(image_paths), 4):
            page_images = image_paths[i:i+4]
            
            # Create 2x2 grid
            grid_data = []
            for j in range(0, len(page_images), 2):
                row = []
                for k in range(2):
                    if j + k < len(page_images):
                        img_path = Path(page_images[j + k])
                        image = Image.open(img_path)
                        img_metadata = self._extract_image_metadata(image, img_path.name)
                        image = self.optimizer.optimize_for_pdf(image)
                        
                        img_element = self._create_image_element(
                            image, img_metadata, max_width=8*cm, max_height=8*cm
                        )
                        row.append(img_element)
                    else:
                        row.append('')
                grid_data.append(row)
            
            # Create table for grid
            grid_table = Table(grid_data, colWidths=[9*cm, 9*cm])
            grid_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(grid_table)
            
            # Page break except for last page
            if i + 4 < len(image_paths):
                elements.append(PageBreak())
        
        return elements


# Convenience functions

def image_to_pdf_bytes(
    image_path: Union[str, Path],
    title: Optional[str] = None,
    include_metadata: bool = True,
    optimize: bool = True
) -> bytes:
    """
    Convenience function to convert image to PDF bytes.

    Args:
        image_path: Path to image file
        title: Optional PDF title
        include_metadata: Include image metadata
        optimize: Optimize image for PDF

    Returns:
        bytes: PDF document as bytes
    """
    service = MediaPDFService()
    
    metadata = None
    if title:
        metadata = PDFMetadata(title=title, subject="Image Document")
    
    return service.image_to_pdf_bytes(
        image_path,
        metadata=metadata,
        include_metadata=include_metadata,
        optimize=optimize
    )


def photo_to_pdf_bytes(
    photo_path: Union[str, Path],
    title: str = "",
    description: str = ""
) -> bytes:
    """
    Convenience function to convert photo to PDF bytes.

    Args:
        photo_path: Path to photo file
        title: Photo title
        description: Photo description

    Returns:
        bytes: PDF document as bytes
    """
    service = MediaPDFService()
    return service.photo_to_pdf_bytes(photo_path, title, description)


def multi_image_pdf(
    image_paths: List[Union[str, Path]],
    title: str = "Image Collection",
    layout: str = "one_per_page"
) -> bytes:
    """
    Convenience function to create multi-image PDF.

    Args:
        image_paths: List of image paths
        title: Document title
        layout: Layout style

    Returns:
        bytes: PDF document as bytes
    """
    service = MediaPDFService()
    return service.multi_image_pdf(image_paths, title, layout)


def image_gallery_pdf(
    images: List[Dict[str, Any]],
    gallery_title: str = "Image Gallery"
) -> bytes:
    """
    Convenience function to create image gallery PDF.

    Args:
        images: List of image dicts
        gallery_title: Gallery title

    Returns:
        bytes: PDF document as bytes
    """
    service = MediaPDFService()
    return service.image_gallery_pdf(images, gallery_title)
