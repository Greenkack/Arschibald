"""
Extended PV PDF Service with Optional Additional Pages

This service extends the standard 8-page PV PDF with optional additional pages (9+)
that can be dynamically activated based on user selection. Additional pages can include:
- Detailed calculations
- Additional diagrams
- Product datasheets from database
- Documents from database (individual per product)
- Images from database (dynamic)
- Extended visualizations

Author: Kiro AI
Date: 2025-01-22
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from io import BytesIO
from dataclasses import dataclass
from enum import Enum

try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False

from .standard_pv_pdf_service import (
    StandardPVPDFService,
    YMLCoordinateParser,
    TemplateLoader,
    PositioningEngine,
    PlaceholderSystem
)

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    """Types of components that can be added to extended PDF"""
    DETAILED_CALCULATION = "detailed_calculation"
    ADDITIONAL_DIAGRAM = "additional_diagram"
    PRODUCT_DATASHEET = "product_datasheet"
    DOCUMENT = "document"
    IMAGE = "image"
    EXTENDED_VISUALIZATION = "extended_visualization"


@dataclass
class ExtendedPageConfig:
    """Configuration for an extended page"""
    page_number: int  # Page number (9+)
    component_type: ComponentType
    component_id: Optional[str] = None  # ID for database lookup
    title: Optional[str] = None
    enabled: bool = True


@dataclass
class ComponentSelection:
    """User's selection of components to include in extended PDF"""
    include_detailed_calculations: bool = False
    include_additional_diagrams: bool = False
    include_product_datasheets: bool = False
    include_documents: bool = False
    include_images: bool = False
    include_extended_visualizations: bool = False
    
    # Specific selections
    selected_diagram_types: List[str] = None
    selected_product_ids: List[str] = None
    selected_document_ids: List[str] = None
    selected_image_ids: List[str] = None
    
    def __post_init__(self):
        if self.selected_diagram_types is None:
            self.selected_diagram_types = []
        if self.selected_product_ids is None:
            self.selected_product_ids = []
        if self.selected_document_ids is None:
            self.selected_document_ids = []
        if self.selected_image_ids is None:
            self.selected_image_ids = []


class ExtendedTemplateLoader(TemplateLoader):
    """Extended template loader for pages 9+"""
    
    def load_extended_template(self, page_number: int) -> Optional[bytes]:
        """
        Load an extended template PDF for pages 9+.
        
        Args:
            page_number: Page number (9+)
            
        Returns:
            PDF bytes or None if not found
        """
        # Extended templates use the same naming convention
        template_path = self.template_dir / f"nt_nt_{page_number:02d}.pdf"
        
        if not template_path.exists():
            # Try generic extended template
            template_path = self.template_dir / "nt_nt_extended.pdf"
            
        if not template_path.exists():
            logger.warning(f"Extended template not found for page {page_number}")
            return None
            
        try:
            with open(template_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading extended template {template_path}: {e}")
            return None


class DatasheetIntegration:
    """Integration with product database for datasheets"""
    
    def __init__(self, database_service=None):
        self.database_service = database_service
        
    def get_product_datasheet(self, product_id: str) -> Optional[bytes]:
        """
        Retrieve product datasheet from database.
        
        Args:
            product_id: Product ID
            
        Returns:
            PDF bytes of datasheet or None
        """
        if not self.database_service:
            logger.warning("Database service not available")
            return None
            
        try:
            # Query database for product datasheet
            # This is a placeholder - actual implementation depends on database schema
            datasheet = self.database_service.get_product_datasheet(product_id)
            
            if datasheet and 'pdf_bytes' in datasheet:
                return datasheet['pdf_bytes']
            
            logger.warning(f"No datasheet found for product {product_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving datasheet for product {product_id}: {e}")
            return None
    
    def get_all_product_datasheets(self, product_ids: List[str]) -> Dict[str, bytes]:
        """
        Retrieve multiple product datasheets.
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            Dictionary mapping product IDs to PDF bytes
        """
        datasheets = {}
        for product_id in product_ids:
            datasheet_bytes = self.get_product_datasheet(product_id)
            if datasheet_bytes:
                datasheets[product_id] = datasheet_bytes
        return datasheets


class DocumentIntegration:
    """Integration with database for documents"""
    
    def __init__(self, database_service=None):
        self.database_service = database_service
        
    def get_document(self, document_id: str) -> Optional[bytes]:
        """
        Retrieve document from database.
        
        Args:
            document_id: Document ID
            
        Returns:
            PDF bytes of document or None
        """
        if not self.database_service:
            logger.warning("Database service not available")
            return None
            
        try:
            # Query database for document
            document = self.database_service.get_document(document_id)
            
            if document and 'pdf_bytes' in document:
                return document['pdf_bytes']
            
            logger.warning(f"No document found with ID {document_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            return None
    
    def get_product_documents(self, product_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all documents associated with a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            List of document metadata dictionaries
        """
        if not self.database_service:
            return []
            
        try:
            return self.database_service.get_product_documents(product_id)
        except Exception as e:
            logger.error(f"Error retrieving documents for product {product_id}: {e}")
            return []


class ImageIntegration:
    """Integration with database for images"""
    
    def __init__(self, database_service=None):
        self.database_service = database_service
        
    def get_image(self, image_id: str) -> Optional[bytes]:
        """
        Retrieve image from database and convert to PDF.
        
        Args:
            image_id: Image ID
            
        Returns:
            PDF bytes containing the image or None
        """
        if not self.database_service:
            logger.warning("Database service not available")
            return None
            
        try:
            # Query database for image
            image = self.database_service.get_image(image_id)
            
            if image and 'image_bytes' in image:
                # Convert image to PDF
                return self._image_to_pdf(image['image_bytes'])
            
            logger.warning(f"No image found with ID {image_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving image {image_id}: {e}")
            return None
    
    def _image_to_pdf(self, image_bytes: bytes) -> bytes:
        """
        Convert image bytes to PDF.
        
        Args:
            image_bytes: Image data
            
        Returns:
            PDF bytes containing the image
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.utils import ImageReader
            from PIL import Image
            
            # Load image
            img = Image.open(BytesIO(image_bytes))
            
            # Create PDF
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            # Calculate dimensions to fit on page
            page_width, page_height = A4
            img_width, img_height = img.size
            
            # Scale image to fit page with margins
            margin = 50
            max_width = page_width - 2 * margin
            max_height = page_height - 2 * margin
            
            scale = min(max_width / img_width, max_height / img_height)
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            
            # Center image on page
            x = (page_width - scaled_width) / 2
            y = (page_height - scaled_height) / 2
            
            # Draw image
            img_reader = ImageReader(BytesIO(image_bytes))
            c.drawImage(img_reader, x, y, scaled_width, scaled_height)
            
            c.save()
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Error converting image to PDF: {e}")
            return b''


class ExtendedCalculationGenerator:
    """Generator for extended calculation pages"""
    
    def __init__(self, positioning_engine: PositioningEngine):
        self.positioning_engine = positioning_engine
        
    def generate_detailed_calculation_page(
        self,
        calculation_data: Dict[str, Any],
        template_bytes: bytes
    ) -> bytes:
        """
        Generate a page with detailed calculations.
        
        Args:
            calculation_data: Detailed calculation results
            template_bytes: Template PDF bytes
            
        Returns:
            PDF bytes with calculations
        """
        # Create overlay with calculation details
        elements = self._create_calculation_elements(calculation_data)
        overlay_bytes = self.positioning_engine.create_overlay(elements, calculation_data)
        
        # Merge with template
        return self.positioning_engine.merge_overlay_with_template(
            template_bytes,
            overlay_bytes
        )
    
    def _create_calculation_elements(
        self,
        calculation_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create text elements for detailed calculations.
        
        Args:
            calculation_data: Calculation data
            
        Returns:
            List of text elements with positioning
        """
        elements = []
        
        # Title
        elements.append({
            'text': 'Detaillierte Berechnungen',
            'position': {'x': 50, 'y': 50, 'x2': 550, 'y2': 70},
            'font': 'Helvetica-Bold',
            'font_size': 16,
            'color': 0x000000
        })
        
        # Add calculation details
        y_offset = 100
        for key, value in calculation_data.items():
            if isinstance(value, (int, float)):
                elements.append({
                    'text': f"{key}: {value}",
                    'position': {'x': 50, 'y': y_offset, 'x2': 550, 'y2': y_offset + 20},
                    'font': 'Helvetica',
                    'font_size': 11,
                    'color': 0x000000
                })
                y_offset += 25
        
        return elements


class ExtendedVisualizationGenerator:
    """Generator for extended visualization pages"""
    
    def __init__(self, positioning_engine: PositioningEngine):
        self.positioning_engine = positioning_engine
        
    def generate_visualization_page(
        self,
        visualization_data: Dict[str, Any],
        template_bytes: bytes
    ) -> bytes:
        """
        Generate a page with extended visualizations.
        
        Args:
            visualization_data: Visualization data
            template_bytes: Template PDF bytes
            
        Returns:
            PDF bytes with visualizations
        """
        # This would integrate with the 3D visualization service
        # For now, return template with title
        elements = [{
            'text': 'Erweiterte Visualisierungen',
            'position': {'x': 50, 'y': 50, 'x2': 550, 'y2': 70},
            'font': 'Helvetica-Bold',
            'font_size': 16,
            'color': 0x000000
        }]
        
        overlay_bytes = self.positioning_engine.create_overlay(elements, visualization_data)
        
        return self.positioning_engine.merge_overlay_with_template(
            template_bytes,
            overlay_bytes
        )


class ExtendedPVPDFService:
    """
    Service for generating extended PV PDF documents with optional additional pages.
    
    This service extends StandardPVPDFService to support:
    - Standard 8 pages (1-8) using base logic
    - Optional additional pages (9+) dynamically activated
    - Component selection system
    - Database integration for datasheets, documents, and images
    - Dynamic page generation based on user selection
    """
    
    def __init__(
        self,
        template_dir: str = "pdf_templates_static/notext",
        coords_dir: str = "coords",
        database_service=None
    ):
        # Initialize base service for standard pages
        self.standard_service = StandardPVPDFService(template_dir, coords_dir)
        
        # Initialize extended components
        self.extended_template_loader = ExtendedTemplateLoader(template_dir)
        self.coords_dir = Path(coords_dir)
        self.positioning_engine = PositioningEngine()
        
        # Initialize integrations
        self.datasheet_integration = DatasheetIntegration(database_service)
        self.document_integration = DocumentIntegration(database_service)
        self.image_integration = ImageIntegration(database_service)
        
        # Initialize generators
        self.calculation_generator = ExtendedCalculationGenerator(self.positioning_engine)
        self.visualization_generator = ExtendedVisualizationGenerator(self.positioning_engine)
        
    def generate_extended_pdf(
        self,
        data: Dict[str, Any],
        component_selection: ComponentSelection
    ) -> bytes:
        """
        Generate extended PDF with standard pages plus optional additional pages.
        
        Args:
            data: Dictionary containing all values for placeholders
            component_selection: User's selection of components to include
            
        Returns:
            Complete PDF bytes
        """
        if not PYPDF_AVAILABLE:
            logger.error("PyPDF not available, cannot generate PDF")
            return b''
        
        writer = PdfWriter()
        
        # Step 1: Generate standard 8 pages
        logger.info("Generating standard 8 pages...")
        standard_pdf_bytes = self.standard_service.generate_complete_pdf(data)
        
        if standard_pdf_bytes:
            try:
                standard_pdf = PdfReader(BytesIO(standard_pdf_bytes))
                for page in standard_pdf.pages:
                    writer.add_page(page)
                logger.info(f"Added {len(standard_pdf.pages)} standard pages")
            except Exception as e:
                logger.error(f"Error adding standard pages: {e}")
                return b''
        else:
            logger.error("Failed to generate standard pages")
            return b''
        
        # Step 2: Generate optional additional pages based on selection
        current_page_number = 9
        
        # Detailed calculations
        if component_selection.include_detailed_calculations:
            logger.info("Adding detailed calculations page...")
            calc_page = self._generate_detailed_calculations_page(
                current_page_number,
                data
            )
            if calc_page:
                self._add_page_to_writer(writer, calc_page)
                current_page_number += 1
        
        # Additional diagrams
        if component_selection.include_additional_diagrams:
            logger.info("Adding additional diagrams...")
            for diagram_type in component_selection.selected_diagram_types:
                diagram_page = self._generate_diagram_page(
                    current_page_number,
                    diagram_type,
                    data
                )
                if diagram_page:
                    self._add_page_to_writer(writer, diagram_page)
                    current_page_number += 1
        
        # Product datasheets
        if component_selection.include_product_datasheets:
            logger.info("Adding product datasheets...")
            for product_id in component_selection.selected_product_ids:
                datasheet_bytes = self.datasheet_integration.get_product_datasheet(product_id)
                if datasheet_bytes:
                    self._add_pdf_to_writer(writer, datasheet_bytes)
                    current_page_number += 1
        
        # Documents
        if component_selection.include_documents:
            logger.info("Adding documents...")
            for document_id in component_selection.selected_document_ids:
                document_bytes = self.document_integration.get_document(document_id)
                if document_bytes:
                    self._add_pdf_to_writer(writer, document_bytes)
                    current_page_number += 1
        
        # Images
        if component_selection.include_images:
            logger.info("Adding images...")
            for image_id in component_selection.selected_image_ids:
                image_pdf_bytes = self.image_integration.get_image(image_id)
                if image_pdf_bytes:
                    self._add_pdf_to_writer(writer, image_pdf_bytes)
                    current_page_number += 1
        
        # Extended visualizations
        if component_selection.include_extended_visualizations:
            logger.info("Adding extended visualizations...")
            viz_page = self._generate_extended_visualization_page(
                current_page_number,
                data
            )
            if viz_page:
                self._add_page_to_writer(writer, viz_page)
                current_page_number += 1
        
        # Write final PDF
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        
        logger.info(f"Extended PDF generated with {current_page_number - 1} total pages")
        return output.read()
    
    def _generate_detailed_calculations_page(
        self,
        page_number: int,
        data: Dict[str, Any]
    ) -> Optional[bytes]:
        """Generate detailed calculations page"""
        template_bytes = self.extended_template_loader.load_extended_template(page_number)
        if not template_bytes:
            return None
        
        return self.calculation_generator.generate_detailed_calculation_page(
            data,
            template_bytes
        )
    
    def _generate_diagram_page(
        self,
        page_number: int,
        diagram_type: str,
        data: Dict[str, Any]
    ) -> Optional[bytes]:
        """Generate diagram page"""
        # This would integrate with chart generation service
        template_bytes = self.extended_template_loader.load_extended_template(page_number)
        if not template_bytes:
            return None
        
        # For now, return template with title
        elements = [{
            'text': f'Diagramm: {diagram_type}',
            'position': {'x': 50, 'y': 50, 'x2': 550, 'y2': 70},
            'font': 'Helvetica-Bold',
            'font_size': 16,
            'color': 0x000000
        }]
        
        overlay_bytes = self.positioning_engine.create_overlay(elements, data)
        return self.positioning_engine.merge_overlay_with_template(
            template_bytes,
            overlay_bytes
        )
    
    def _generate_extended_visualization_page(
        self,
        page_number: int,
        data: Dict[str, Any]
    ) -> Optional[bytes]:
        """Generate extended visualization page"""
        template_bytes = self.extended_template_loader.load_extended_template(page_number)
        if not template_bytes:
            return None
        
        return self.visualization_generator.generate_visualization_page(
            data,
            template_bytes
        )
    
    def _add_page_to_writer(self, writer: PdfWriter, page_bytes: bytes):
        """Add a single page to PDF writer"""
        try:
            page_pdf = PdfReader(BytesIO(page_bytes))
            writer.add_page(page_pdf.pages[0])
        except Exception as e:
            logger.error(f"Error adding page: {e}")
    
    def _add_pdf_to_writer(self, writer: PdfWriter, pdf_bytes: bytes):
        """Add all pages from a PDF to writer"""
        try:
            pdf = PdfReader(BytesIO(pdf_bytes))
            for page in pdf.pages:
                writer.add_page(page)
        except Exception as e:
            logger.error(f"Error adding PDF: {e}")
    
    def get_available_components(
        self,
        product_ids: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get available components that can be added to extended PDF.
        
        Args:
            product_ids: Optional list of product IDs to get specific components
            
        Returns:
            Dictionary of available components by type
        """
        available = {
            'calculations': [
                {'id': 'detailed_roi', 'name': 'Detaillierte ROI-Berechnung'},
                {'id': 'detailed_production', 'name': 'Detaillierte Produktionsberechnung'},
                {'id': 'detailed_savings', 'name': 'Detaillierte Einsparungsberechnung'},
            ],
            'diagrams': [
                {'id': 'production_monthly', 'name': 'Monatliche Produktion'},
                {'id': 'consumption_analysis', 'name': 'Verbrauchsanalyse'},
                {'id': 'savings_projection', 'name': 'Einsparungsprognose'},
            ],
            'datasheets': [],
            'documents': [],
            'images': []
        }
        
        # Get product-specific components if product IDs provided
        if product_ids:
            for product_id in product_ids:
                # Get datasheets
                datasheet = self.datasheet_integration.get_product_datasheet(product_id)
                if datasheet:
                    available['datasheets'].append({
                        'id': product_id,
                        'name': f'Datenblatt {product_id}'
                    })
                
                # Get documents
                documents = self.document_integration.get_product_documents(product_id)
                for doc in documents:
                    available['documents'].append({
                        'id': doc.get('id'),
                        'name': doc.get('name', 'Dokument')
                    })
        
        return available


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize service
    service = ExtendedPVPDFService()
    
    # Sample data
    sample_data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Max Mustermann',
        'kunde_wohnort': 'Berlin',
        'kWp_anlage_anlage': '10,5 kWp',
        'langes_datum_heute': '22. Januar 2025',
        'total_price': 16999.00,
        'detailed_roi': 8.5,
        'annual_production': 12500,
        'annual_savings': 2100
    }
    
    # Component selection
    selection = ComponentSelection(
        include_detailed_calculations=True,
        include_additional_diagrams=True,
        selected_diagram_types=['production_monthly', 'savings_projection']
    )
    
    # Generate extended PDF
    pdf_bytes = service.generate_extended_pdf(sample_data, selection)
    
    if pdf_bytes:
        output_path = "test_extended_pv_pdf.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"Extended PDF generated successfully: {output_path}")
    else:
        logger.error("Failed to generate extended PDF")
