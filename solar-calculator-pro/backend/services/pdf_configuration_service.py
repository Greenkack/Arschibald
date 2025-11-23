"""
PDF Configuration Service
Manages PDF configuration, validation, and generation orchestration
"""

import uuid
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.pdf_config_schemas import (
    PDFConfigurationRequest,
    PDFConfigurationResponse,
    PDFPreviewRequest,
    PDFPreviewResponse,
    PDFGenerationRequest,
    PDFGenerationResponse,
    PDFType,
    ComponentType,
    PageConfig,
    ComponentConfig
)


class PDFConfigurationService:
    """Service for managing PDF configurations"""
    
    def __init__(self):
        self.configurations: Dict[str, PDFConfigurationRequest] = {}
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for different PDF types"""
        return {
            PDFType.STANDARD_PV: {
                "required_pages": [1, 2, 3, 4, 5, 6, 7, 8],
                "max_pages": 8,
                "required_components": ["cover", "calculations", "pricing"],
                "optional_components": ["charts", "3d_viz", "datasheets"]
            },
            PDFType.EXTENDED_PV: {
                "required_pages": [1, 2, 3, 4, 5, 6, 7, 8],
                "max_pages": 20,
                "required_components": ["cover", "calculations", "pricing"],
                "optional_components": ["charts", "3d_viz", "datasheets", "documents", "images"]
            },
            PDFType.STANDARD_WP: {
                "required_pages": [1, 2, 3, 4, 5, 6, 7, 8],
                "max_pages": 8,
                "required_components": ["cover", "wp_calculations", "pricing"],
                "optional_components": ["charts", "cop_analysis"]
            },
            PDFType.EXTENDED_WP: {
                "required_pages": [1, 2, 3, 4, 5, 6, 7, 8],
                "max_pages": 20,
                "required_components": ["cover", "wp_calculations", "pricing"],
                "optional_components": ["charts", "cop_analysis", "datasheets", "documents"]
            },
            PDFType.MULTI_PDF: {
                "required_pages": [1, 2, 3, 4, 5, 6, 7, 8],
                "max_pages": 8,
                "required_components": ["cover", "calculations", "pricing"],
                "optional_components": ["charts", "3d_viz"],
                "requires_companies": True,
                "min_companies": 1,
                "max_companies": 20
            }
        }
    
    def create_configuration(
        self,
        config_request: PDFConfigurationRequest
    ) -> PDFConfigurationResponse:
        """
        Create and validate a new PDF configuration
        
        Args:
            config_request: PDF configuration request
            
        Returns:
            PDFConfigurationResponse with validation results
        """
        # Generate unique configuration ID
        config_id = str(uuid.uuid4())
        
        # Validate configuration
        validation_errors, validation_warnings = self._validate_configuration(config_request)
        
        # Calculate statistics
        total_pages = len(config_request.pages)
        enabled_pages = sum(1 for page in config_request.pages if page.enabled)
        total_components = len(config_request.components)
        enabled_components = sum(1 for comp in config_request.components if comp.enabled)
        
        # Estimate PDF size
        estimated_size_mb = self._estimate_pdf_size(config_request)
        
        # Store configuration if valid
        if not validation_errors:
            self.configurations[config_id] = config_request
        
        return PDFConfigurationResponse(
            config_id=config_id,
            pdf_type=config_request.pdf_type,
            total_pages=total_pages,
            enabled_pages=enabled_pages,
            total_components=total_components,
            enabled_components=enabled_components,
            estimated_size_mb=estimated_size_mb,
            validation_errors=validation_errors,
            validation_warnings=validation_warnings
        )
    
    def _validate_configuration(
        self,
        config: PDFConfigurationRequest
    ) -> tuple[List[str], List[str]]:
        """
        Validate PDF configuration
        
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        # Get validation rules for PDF type
        rules = self.validation_rules.get(config.pdf_type)
        if not rules:
            errors.append(f"Unknown PDF type: {config.pdf_type}")
            return errors, warnings
        
        # Validate pages
        if not config.pages:
            errors.append("No pages configured")
        else:
            page_numbers = [p.page_number for p in config.pages]
            
            # Check required pages
            for required_page in rules["required_pages"]:
                if required_page not in page_numbers:
                    errors.append(f"Required page {required_page} is missing")
            
            # Check max pages
            if len(page_numbers) > rules["max_pages"]:
                errors.append(f"Too many pages: {len(page_numbers)} (max: {rules['max_pages']})")
            
            # Check for duplicate page numbers
            if len(page_numbers) != len(set(page_numbers)):
                errors.append("Duplicate page numbers found")
        
        # Validate components
        if not config.components:
            warnings.append("No components configured")
        else:
            component_types = [c.component_type.value for c in config.components if c.enabled]
            
            # Check required components
            for required_comp in rules["required_components"]:
                if required_comp not in component_types:
                    warnings.append(f"Recommended component '{required_comp}' is missing")
        
        # Validate multi-PDF specific requirements
        if config.pdf_type == PDFType.MULTI_PDF:
            if not config.companies:
                errors.append("Multi-PDF requires at least one company")
            elif len(config.companies) < rules.get("min_companies", 1):
                errors.append(f"Multi-PDF requires at least {rules['min_companies']} companies")
            elif len(config.companies) > rules.get("max_companies", 20):
                errors.append(f"Multi-PDF supports maximum {rules['max_companies']} companies")
            
            # Validate product rotation
            if config.product_rotation and config.product_rotation.enabled:
                if len(config.companies) < 2:
                    warnings.append("Product rotation is most effective with 2+ companies")
            
            # Validate price increase
            if config.price_increase and config.price_increase.enabled:
                if config.price_increase.increase_percentage <= 0:
                    errors.append("Price increase percentage must be positive")
                if config.price_increase.increase_percentage > 50:
                    warnings.append("Price increase >50% may be unrealistic")
        
        # Validate logo positions
        for page_num, logo_pos in config.logo_positions.items():
            if logo_pos.x < 0 or logo_pos.y < 0:
                errors.append(f"Invalid logo position on page {page_num}: negative coordinates")
            if logo_pos.width <= 0 or logo_pos.height <= 0:
                errors.append(f"Invalid logo size on page {page_num}: must be positive")
        
        # Validate watermark
        if config.watermark and config.watermark.enabled:
            if not config.watermark.text:
                warnings.append("Watermark enabled but no text specified")
            if config.watermark.opacity < 0.05:
                warnings.append("Watermark opacity very low, may not be visible")
        
        # Validate font size
        if config.font_size_base < 8:
            warnings.append("Font size <8pt may be difficult to read")
        if config.font_size_base > 14:
            warnings.append("Font size >14pt may waste space")
        
        return errors, warnings
    
    def _estimate_pdf_size(self, config: PDFConfigurationRequest) -> float:
        """
        Estimate PDF file size in MB
        
        Args:
            config: PDF configuration
            
        Returns:
            Estimated size in MB
        """
        # Base size per page
        base_size_per_page = 0.1  # MB
        
        # Count enabled pages
        enabled_pages = sum(1 for page in config.pages if page.enabled)
        size = enabled_pages * base_size_per_page
        
        # Add size for components
        for component in config.components:
            if not component.enabled:
                continue
            
            if component.component_type == ComponentType.IMAGE:
                size += 0.5  # Images add ~0.5MB
            elif component.component_type == ComponentType.CHART:
                size += 0.2  # Charts add ~0.2MB
            elif component.component_type == ComponentType.DIAGRAM:
                size += 0.3  # Diagrams add ~0.3MB
            elif component.component_type == ComponentType.DOCUMENT:
                size += 1.0  # Documents add ~1MB
            elif component.component_type == ComponentType.DATASHEET:
                size += 0.5  # Datasheets add ~0.5MB
            else:
                size += 0.05  # Text/calculations add minimal size
        
        # Add size for 3D visualization
        if config.include_3d_visualization:
            size += 1.0
        
        # Adjust for compression
        if config.compress_pdf:
            size *= 0.6  # Compression reduces size by ~40%
        
        # Multi-PDF multiplier
        if config.pdf_type == PDFType.MULTI_PDF:
            size *= len(config.companies)
        
        return round(size, 2)
    
    def get_configuration(self, config_id: str) -> Optional[PDFConfigurationRequest]:
        """Get configuration by ID"""
        return self.configurations.get(config_id)
    
    def update_configuration(
        self,
        config_id: str,
        config_request: PDFConfigurationRequest
    ) -> PDFConfigurationResponse:
        """Update existing configuration"""
        if config_id not in self.configurations:
            raise ValueError(f"Configuration {config_id} not found")
        
        # Validate updated configuration
        validation_errors, validation_warnings = self._validate_configuration(config_request)
        
        # Update if valid
        if not validation_errors:
            self.configurations[config_id] = config_request
        
        # Calculate statistics
        total_pages = len(config_request.pages)
        enabled_pages = sum(1 for page in config_request.pages if page.enabled)
        total_components = len(config_request.components)
        enabled_components = sum(1 for comp in config_request.components if comp.enabled)
        estimated_size_mb = self._estimate_pdf_size(config_request)
        
        return PDFConfigurationResponse(
            config_id=config_id,
            pdf_type=config_request.pdf_type,
            total_pages=total_pages,
            enabled_pages=enabled_pages,
            total_components=total_components,
            enabled_components=enabled_components,
            estimated_size_mb=estimated_size_mb,
            validation_errors=validation_errors,
            validation_warnings=validation_warnings
        )
    
    def delete_configuration(self, config_id: str) -> bool:
        """Delete configuration"""
        if config_id in self.configurations:
            del self.configurations[config_id]
            return True
        return False
    
    def list_configurations(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List all configurations with pagination"""
        all_configs = list(self.configurations.items())
        total = len(all_configs)
        
        start = (page - 1) * page_size
        end = start + page_size
        page_configs = all_configs[start:end]
        
        configurations = [
            {
                "config_id": config_id,
                "pdf_type": config.pdf_type.value,
                "pages": len(config.pages),
                "components": len(config.components),
                "companies": len(config.companies) if config.companies else 0
            }
            for config_id, config in page_configs
        ]
        
        return {
            "configurations": configurations,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    def generate_preview(
        self,
        preview_request: PDFPreviewRequest
    ) -> PDFPreviewResponse:
        """
        Generate preview image for a specific page
        
        Args:
            preview_request: Preview request
            
        Returns:
            PDFPreviewResponse with preview image
        """
        config = self.get_configuration(preview_request.config_id)
        if not config:
            raise ValueError(f"Configuration {preview_request.config_id} not found")
        
        # TODO: Implement actual PDF preview generation
        # This would use the PDF generation service to create a preview
        # For now, return placeholder
        
        import base64
        placeholder_image = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        return PDFPreviewResponse(
            config_id=preview_request.config_id,
            page_number=preview_request.page_number,
            preview_image_base64=base64.b64encode(placeholder_image).decode(),
            width=800,
            height=1131  # A4 aspect ratio
        )
    
    def generate_pdf(
        self,
        generation_request: PDFGenerationRequest
    ) -> PDFGenerationResponse:
        """
        Generate PDF from configuration
        
        Args:
            generation_request: Generation request
            
        Returns:
            PDFGenerationResponse with PDF data
        """
        start_time = time.time()
        
        config = self.get_configuration(generation_request.config_id)
        if not config:
            raise ValueError(f"Configuration {generation_request.config_id} not found")
        
        # TODO: Implement actual PDF generation
        # This would orchestrate the PDF generation service
        # For now, return placeholder
        
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        filename = generation_request.filename or f"pdf_{generation_request.config_id}.pdf"
        
        return PDFGenerationResponse(
            config_id=generation_request.config_id,
            pdf_url=f"/api/v1/pdf/download/{generation_request.config_id}",
            pdf_base64=None if generation_request.output_format == "pdf" else "placeholder_base64",
            filename=filename,
            size_bytes=1024000,  # Placeholder: 1MB
            page_count=len([p for p in config.pages if p.enabled]),
            generation_time_ms=generation_time_ms
        )
    
    def get_default_configuration(self, pdf_type: PDFType) -> PDFConfigurationRequest:
        """
        Get default configuration for a PDF type
        
        Args:
            pdf_type: PDF type
            
        Returns:
            Default configuration
        """
        # Create default pages
        rules = self.validation_rules.get(pdf_type, {})
        required_pages = rules.get("required_pages", [1, 2, 3, 4, 5, 6, 7, 8])
        
        pages = [
            PageConfig(
                page_number=page_num,
                enabled=True,
                components=[],
                custom_header=None,
                custom_footer=None
            )
            for page_num in required_pages
        ]
        
        # Create default components
        components = []
        
        return PDFConfigurationRequest(
            pdf_type=pdf_type,
            project_id=None,
            pages=pages,
            components=components,
            companies=[],
            product_rotation=None,
            price_increase=None
        )
