"""
PDF Configuration Schemas
Pydantic models for PDF configuration and options
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class PDFType(str, Enum):
    """PDF type enumeration"""
    STANDARD_PV = "standard_pv"
    EXTENDED_PV = "extended_pv"
    STANDARD_WP = "standard_wp"
    EXTENDED_WP = "extended_wp"
    MULTI_PDF = "multi_pdf"


class ComponentType(str, Enum):
    """Component type enumeration"""
    DIAGRAM = "diagram"
    CALCULATION = "calculation"
    DOCUMENT = "document"
    IMAGE = "image"
    DATASHEET = "datasheet"
    TABLE = "table"
    CHART = "chart"
    TEXT = "text"


class ColorScheme(str, Enum):
    """Color scheme enumeration"""
    DEFAULT = "default"
    BLUE = "blue"
    GREEN = "green"
    ORANGE = "orange"
    PURPLE = "purple"
    CUSTOM = "custom"


class FontFamily(str, Enum):
    """Font family enumeration"""
    HELVETICA = "Helvetica"
    TIMES = "Times-Roman"
    COURIER = "Courier"
    ARIAL = "Arial"
    VERDANA = "Verdana"


class LogoPosition(BaseModel):
    """Logo position configuration"""
    x: float = Field(..., description="X coordinate in points")
    y: float = Field(..., description="Y coordinate in points")
    width: float = Field(..., description="Logo width in points")
    height: float = Field(..., description="Logo height in points")
    page: int = Field(1, description="Page number for logo placement")


class WatermarkConfig(BaseModel):
    """Watermark configuration"""
    enabled: bool = Field(False, description="Enable watermark")
    text: str = Field("", description="Watermark text")
    opacity: float = Field(0.1, ge=0.0, le=1.0, description="Watermark opacity")
    rotation: float = Field(45.0, description="Watermark rotation in degrees")
    font_size: int = Field(60, description="Watermark font size")
    color: str = Field("#CCCCCC", description="Watermark color")


class PageConfig(BaseModel):
    """Individual page configuration"""
    page_number: int = Field(..., description="Page number")
    enabled: bool = Field(True, description="Enable this page")
    components: List[str] = Field(default_factory=list, description="Component IDs on this page")
    custom_header: Optional[str] = Field(None, description="Custom header text")
    custom_footer: Optional[str] = Field(None, description="Custom footer text")


class ComponentConfig(BaseModel):
    """Component configuration"""
    component_id: str = Field(..., description="Unique component identifier")
    component_type: ComponentType = Field(..., description="Component type")
    enabled: bool = Field(True, description="Enable this component")
    page: int = Field(..., description="Page number")
    position: Dict[str, float] = Field(..., description="Position coordinates (x, y)")
    size: Optional[Dict[str, float]] = Field(None, description="Size (width, height)")
    data_source: Optional[str] = Field(None, description="Data source identifier")
    options: Dict[str, Any] = Field(default_factory=dict, description="Component-specific options")


class CompanySelection(BaseModel):
    """Company selection for multi-PDF"""
    company_id: int = Field(..., description="Company database ID")
    company_name: str = Field(..., description="Company name")
    logo_path: Optional[str] = Field(None, description="Path to company logo")
    logo_position: Optional[LogoPosition] = Field(None, description="Logo position override")
    color_scheme: Optional[ColorScheme] = Field(None, description="Company-specific color scheme")
    custom_colors: Optional[Dict[str, str]] = Field(None, description="Custom color values")


class ProductRotationConfig(BaseModel):
    """Product rotation configuration for multi-PDF"""
    enabled: bool = Field(True, description="Enable product rotation")
    avoid_duplicate_brands: bool = Field(True, description="Avoid duplicate brands across offers")
    avoid_duplicate_products: bool = Field(True, description="Avoid duplicate products across offers")
    rotation_strategy: str = Field("sequential", description="Rotation strategy: sequential, random, optimized")
    product_categories: List[str] = Field(default_factory=list, description="Categories to rotate")


class PriceIncreaseConfig(BaseModel):
    """Price increase configuration for multi-PDF"""
    enabled: bool = Field(True, description="Enable price increase")
    increase_percentage: float = Field(7.0, ge=0.0, le=100.0, description="Price increase percentage")
    apply_to_base_price: bool = Field(True, description="Apply to base price from calculator")
    compound_increases: bool = Field(True, description="Compound increases for each offer")
    min_price: Optional[float] = Field(None, description="Minimum price threshold")
    max_price: Optional[float] = Field(None, description="Maximum price threshold")


class PDFConfigurationRequest(BaseModel):
    """Complete PDF configuration request"""
    # Basic settings
    pdf_type: PDFType = Field(..., description="PDF type to generate")
    project_id: Optional[int] = Field(None, description="Project ID for data")
    
    # Page configuration
    pages: List[PageConfig] = Field(default_factory=list, description="Page configurations")
    
    # Component configuration
    components: List[ComponentConfig] = Field(default_factory=list, description="Component configurations")
    
    # Styling
    color_scheme: ColorScheme = Field(ColorScheme.DEFAULT, description="Color scheme")
    custom_colors: Optional[Dict[str, str]] = Field(None, description="Custom color values")
    font_family: FontFamily = Field(FontFamily.HELVETICA, description="Font family")
    font_size_base: int = Field(10, ge=6, le=20, description="Base font size")
    
    # Logo configuration
    logo_positions: Dict[int, LogoPosition] = Field(default_factory=dict, description="Logo positions per page")
    
    # Watermark
    watermark: Optional[WatermarkConfig] = Field(None, description="Watermark configuration")
    
    # Multi-PDF specific
    companies: List[CompanySelection] = Field(default_factory=list, description="Companies for multi-PDF")
    product_rotation: Optional[ProductRotationConfig] = Field(None, description="Product rotation config")
    price_increase: Optional[PriceIncreaseConfig] = Field(None, description="Price increase config")
    
    # Advanced options
    include_3d_visualization: bool = Field(True, description="Include 3D visualization")
    include_charts: bool = Field(True, description="Include charts")
    include_calculations: bool = Field(True, description="Include detailed calculations")
    include_datasheets: bool = Field(False, description="Include product datasheets")
    include_documents: bool = Field(False, description="Include additional documents")
    
    # Output options
    compress_pdf: bool = Field(True, description="Compress PDF output")
    pdf_version: str = Field("1.7", description="PDF version")
    encryption: Optional[Dict[str, Any]] = Field(None, description="PDF encryption settings")


class PDFConfigurationResponse(BaseModel):
    """PDF configuration response"""
    config_id: str = Field(..., description="Configuration ID")
    pdf_type: PDFType = Field(..., description="PDF type")
    total_pages: int = Field(..., description="Total number of pages")
    enabled_pages: int = Field(..., description="Number of enabled pages")
    total_components: int = Field(..., description="Total number of components")
    enabled_components: int = Field(..., description="Number of enabled components")
    estimated_size_mb: float = Field(..., description="Estimated PDF size in MB")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    validation_warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class PDFPreviewRequest(BaseModel):
    """PDF preview request"""
    config_id: str = Field(..., description="Configuration ID")
    page_number: int = Field(1, ge=1, description="Page number to preview")
    resolution: int = Field(150, ge=72, le=300, description="Preview resolution DPI")


class PDFPreviewResponse(BaseModel):
    """PDF preview response"""
    config_id: str = Field(..., description="Configuration ID")
    page_number: int = Field(..., description="Page number")
    preview_image_base64: str = Field(..., description="Preview image as base64")
    width: int = Field(..., description="Preview width in pixels")
    height: int = Field(..., description="Preview height in pixels")


class PDFGenerationRequest(BaseModel):
    """PDF generation request"""
    config_id: str = Field(..., description="Configuration ID")
    output_format: str = Field("pdf", description="Output format: pdf, base64")
    filename: Optional[str] = Field(None, description="Custom filename")


class PDFGenerationResponse(BaseModel):
    """PDF generation response"""
    config_id: str = Field(..., description="Configuration ID")
    pdf_url: Optional[str] = Field(None, description="PDF download URL")
    pdf_base64: Optional[str] = Field(None, description="PDF as base64")
    filename: str = Field(..., description="Generated filename")
    size_bytes: int = Field(..., description="PDF size in bytes")
    page_count: int = Field(..., description="Number of pages")
    generation_time_ms: int = Field(..., description="Generation time in milliseconds")


class PDFConfigurationListResponse(BaseModel):
    """List of PDF configurations"""
    configurations: List[Dict[str, Any]] = Field(..., description="List of configurations")
    total: int = Field(..., description="Total number of configurations")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
