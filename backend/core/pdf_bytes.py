"""
PDF Byte Generation Core Module

This module provides the core functionality for generating PDF bytes from various data types.
It includes mixins for adding PDF generation capabilities to any data model.

Requirements: 14.5, 14.8
"""

import io
import base64
from typing import Any, Dict, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import mm, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation will be limited.")


class PDFMetadata:
    """PDF metadata container"""
    
    def __init__(
        self,
        title: str = "",
        author: str = "",
        subject: str = "",
        creator: str = "Solar Calculator Pro",
        keywords: List[str] = None,
        creation_date: Optional[datetime] = None
    ):
        self.title = title
        self.author = author
        self.subject = subject
        self.creator = creator
        self.keywords = keywords or []
        self.creation_date = creation_date or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            'title': self.title,
            'author': self.author,
            'subject': self.subject,
            'creator': self.creator,
            'keywords': ', '.join(self.keywords),
            'creation_date': self.creation_date.isoformat()
        }


class PDFRenderingEngine:
    """Core PDF rendering engine"""
    
    def __init__(self, page_size=A4):
        self.page_size = page_size
        self.styles = getSampleStyleSheet() if REPORTLAB_AVAILABLE else None
        self.width, self.height = page_size if REPORTLAB_AVAILABLE else (595, 842)
        
    def create_document(
        self,
        buffer: io.BytesIO,
        metadata: Optional[PDFMetadata] = None
    ) -> 'SimpleDocTemplate':
        """Create a PDF document with metadata"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation")
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Set metadata if provided
        if metadata:
            doc.title = metadata.title
            doc.author = metadata.author
            doc.subject = metadata.subject
            doc.creator = metadata.creator
        
        return doc
    
    def create_canvas(
        self,
        buffer: io.BytesIO,
        metadata: Optional[PDFMetadata] = None
    ) -> 'canvas.Canvas':
        """Create a PDF canvas for low-level drawing"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation")
        
        pdf_canvas = canvas.Canvas(buffer, pagesize=self.page_size)
        
        # Set metadata if provided
        if metadata:
            pdf_canvas.setTitle(metadata.title)
            pdf_canvas.setAuthor(metadata.author)
            pdf_canvas.setSubject(metadata.subject)
            pdf_canvas.setCreator(metadata.creator)
        
        return pdf_canvas
    
    def add_header(
        self,
        canvas_obj: 'canvas.Canvas',
        text: str,
        y_position: Optional[float] = None
    ):
        """Add header to PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        y_pos = y_position or (self.height - 1.5*cm)
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawString(2*cm, y_pos, text)
    
    def add_footer(
        self,
        canvas_obj: 'canvas.Canvas',
        text: str,
        page_number: Optional[int] = None
    ):
        """Add footer to PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        canvas_obj.setFont("Helvetica", 9)
        footer_text = text
        if page_number:
            footer_text += f" | Page {page_number}"
        
        canvas_obj.drawString(2*cm, 1.5*cm, footer_text)
    
    def format_german_number(self, value: float, decimals: int = 2) -> str:
        """Format number in German format (1.234,56)"""
        formatted = f"{value:,.{decimals}f}"
        # Replace comma with temp, dot with comma, temp with dot
        return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def create_table(
        self,
        data: List[List[Any]],
        col_widths: Optional[List[float]] = None,
        style: Optional[List] = None
    ) -> 'Table':
        """Create a formatted table"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation")
        
        table = Table(data, colWidths=col_widths)
        
        # Apply default style if none provided
        if style is None:
            style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]
        
        table.setStyle(TableStyle(style))
        return table


class PDFByteMixin(ABC):
    """
    Mixin class for adding PDF byte generation capabilities to any model.
    
    Classes using this mixin should implement the _render_to_pdf method.
    """
    
    def __init__(self):
        self._pdf_engine = PDFRenderingEngine()
        self._pdf_metadata = None
    
    def set_pdf_metadata(self, metadata: PDFMetadata):
        """Set PDF metadata for this instance"""
        self._pdf_metadata = metadata
    
    def get_pdf_metadata(self) -> PDFMetadata:
        """Get PDF metadata, creating default if not set"""
        if self._pdf_metadata is None:
            self._pdf_metadata = PDFMetadata(
                title=self._get_default_title(),
                subject=self._get_default_subject()
            )
        return self._pdf_metadata
    
    def to_pdf_bytes(self, metadata: Optional[PDFMetadata] = None) -> bytes:
        """
        Convert data to PDF bytes.
        
        Args:
            metadata: Optional PDF metadata. If not provided, uses instance metadata.
        
        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation")
        
        buffer = io.BytesIO()
        
        # Use provided metadata or instance metadata
        pdf_metadata = metadata or self.get_pdf_metadata()
        
        # Create document
        doc = self._pdf_engine.create_document(buffer, pdf_metadata)
        
        # Build content
        story = []
        self._render_to_pdf(story, doc)
        
        # Build PDF
        doc.build(story)
        
        # Get bytes
        buffer.seek(0)
        return buffer.getvalue()
    
    def to_pdf_base64(self, metadata: Optional[PDFMetadata] = None) -> str:
        """
        Convert data to base64-encoded PDF bytes.
        
        Args:
            metadata: Optional PDF metadata
        
        Returns:
            str: Base64-encoded PDF document
        """
        pdf_bytes = self.to_pdf_bytes(metadata)
        return base64.b64encode(pdf_bytes).decode('utf-8')
    
    def to_pdf_canvas(self, metadata: Optional[PDFMetadata] = None) -> bytes:
        """
        Generate PDF using low-level canvas API for more control.
        
        Args:
            metadata: Optional PDF metadata
        
        Returns:
            bytes: PDF document as bytes
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation")
        
        buffer = io.BytesIO()
        
        # Use provided metadata or instance metadata
        pdf_metadata = metadata or self.get_pdf_metadata()
        
        # Create canvas
        pdf_canvas = self._pdf_engine.create_canvas(buffer, pdf_metadata)
        
        # Render using canvas
        self._render_to_canvas(pdf_canvas)
        
        # Save
        pdf_canvas.save()
        
        # Get bytes
        buffer.seek(0)
        return buffer.getvalue()
    
    @abstractmethod
    def _render_to_pdf(self, story: List, doc: 'SimpleDocTemplate'):
        """
        Render content to PDF document.
        
        Subclasses must implement this method to define how their data
        should be rendered in the PDF.
        
        Args:
            story: List to append PDF elements to
            doc: The PDF document being built
        """
        pass
    
    def _render_to_canvas(self, canvas_obj: 'canvas.Canvas'):
        """
        Render content using canvas API.
        
        Subclasses can override this for low-level PDF control.
        Default implementation raises NotImplementedError.
        
        Args:
            canvas_obj: The PDF canvas to draw on
        """
        raise NotImplementedError(
            "Canvas rendering not implemented. Override _render_to_canvas or use _render_to_pdf."
        )
    
    def _get_default_title(self) -> str:
        """Get default PDF title. Override in subclasses."""
        return "Document"
    
    def _get_default_subject(self) -> str:
        """Get default PDF subject. Override in subclasses."""
        return "Generated Document"
    
    def save_pdf(self, filepath: str, metadata: Optional[PDFMetadata] = None):
        """
        Save PDF to file.
        
        Args:
            filepath: Path where PDF should be saved
            metadata: Optional PDF metadata
        """
        pdf_bytes = self.to_pdf_bytes(metadata)
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)


class SimplePDFDocument(PDFByteMixin):
    """
    Simple PDF document implementation for testing and basic use cases.
    """
    
    def __init__(self, title: str = "Document", content: str = ""):
        super().__init__()
        self.title = title
        self.content = content
    
    def _get_default_title(self) -> str:
        return self.title
    
    def _render_to_pdf(self, story: List, doc: 'SimpleDocTemplate'):
        """Render simple text content to PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        styles = getSampleStyleSheet()
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(self.title, title_style))
        story.append(Spacer(1, 12))
        
        # Add content
        content_style = styles['BodyText']
        for paragraph in self.content.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph, content_style))
                story.append(Spacer(1, 12))


# Utility functions

def create_pdf_from_dict(
    data: Dict[str, Any],
    title: str = "Data Report",
    metadata: Optional[PDFMetadata] = None
) -> bytes:
    """
    Create a simple PDF from a dictionary of data.
    
    Args:
        data: Dictionary of data to include in PDF
        title: PDF title
        metadata: Optional PDF metadata
    
    Returns:
        bytes: PDF document as bytes
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is required for PDF generation")
    
    buffer = io.BytesIO()
    engine = PDFRenderingEngine()
    
    # Create metadata if not provided
    if metadata is None:
        metadata = PDFMetadata(title=title)
    
    doc = engine.create_document(buffer, metadata)
    story = []
    styles = getSampleStyleSheet()
    
    # Add title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))
    
    # Add data as table
    table_data = [['Key', 'Value']]
    for key, value in data.items():
        # Format numbers in German format if they are numeric
        if isinstance(value, (int, float)):
            value_str = engine.format_german_number(value)
        else:
            value_str = str(value)
        table_data.append([str(key), value_str])
    
    table = engine.create_table(table_data)
    story.append(table)
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()


def create_pdf_from_text(
    text: str,
    title: str = "Document",
    metadata: Optional[PDFMetadata] = None
) -> bytes:
    """
    Create a simple PDF from text content.
    
    Args:
        text: Text content
        title: PDF title
        metadata: Optional PDF metadata
    
    Returns:
        bytes: PDF document as bytes
    """
    doc = SimplePDFDocument(title=title, content=text)
    return doc.to_pdf_bytes(metadata)
