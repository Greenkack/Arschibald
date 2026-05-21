"""
PDF Template System (YML Coordinates) API

Provides REST API for PDF template system:
- YML coordinate parser
- Load notext PDF templates
- Position text elements from YML coordinates
- Support font size, color, format settings
- Multi-page coordinate system
- Template validation

Requirements: funktionen.txt - "PDF-Templating-System"
Task: 269. PDF Template System (YML Coordinates)
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid
import yaml

router = APIRouter(prefix="/pdf/templates", tags=["PDF Template System"])


# ==================== Enums ====================

class FontFamily(str, Enum):
    HELVETICA = "Helvetica"
    ARIAL = "Arial"
    TIMES = "Times-Roman"
    COURIER = "Courier"


class TextAlignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class ElementType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    LINE = "line"
    RECTANGLE = "rectangle"
    TABLE = "table"
    DYNAMIC_TEXT = "dynamic_text"


# ==================== Pydantic Models ====================

class Coordinate(BaseModel):
    """Coordinate in mm"""
    x: float = Field(ge=0, le=210)
    y: float = Field(ge=0, le=297)


class FontSettings(BaseModel):
    """Font settings"""
    family: FontFamily = FontFamily.HELVETICA
    size: float = Field(default=10, ge=4, le=72)
    color: str = "#000000"
    bold: bool = False
    italic: bool = False


class TextElement(BaseModel):
    """Text element definition"""
    id: str
    element_type: ElementType = ElementType.TEXT
    page: int = 1
    position: Coordinate
    width: Optional[float] = None
    height: Optional[float] = None
    content: Optional[str] = None
    placeholder: Optional[str] = None  # e.g., "{{customer_name}}"
    font: FontSettings = FontSettings()
    alignment: TextAlignment = TextAlignment.LEFT
    max_lines: int = 1
    line_height: float = 1.2


class ImageElement(BaseModel):
    """Image element definition"""
    id: str
    element_type: ElementType = ElementType.IMAGE
    page: int = 1
    position: Coordinate
    width: float
    height: float
    source: Optional[str] = None  # URL or placeholder
    placeholder: Optional[str] = None  # e.g., "{{company_logo}}"
    fit_mode: str = "contain"  # "contain", "cover", "stretch"


class LineElement(BaseModel):
    """Line element definition"""
    id: str
    element_type: ElementType = ElementType.LINE
    page: int = 1
    start: Coordinate
    end: Coordinate
    stroke_width: float = 0.5
    stroke_color: str = "#000000"
    dash_pattern: Optional[List[float]] = None


class TableElement(BaseModel):
    """Table element definition"""
    id: str
    element_type: ElementType = ElementType.TABLE
    page: int = 1
    position: Coordinate
    width: float
    columns: List[Dict[str, Any]]
    row_height: float = 8
    header_font: FontSettings = FontSettings(bold=True)
    cell_font: FontSettings = FontSettings()
    border_color: str = "#cccccc"
    header_bg_color: str = "#f0f0f0"
    alternate_row_color: Optional[str] = "#fafafa"


class PageTemplate(BaseModel):
    """Single page template"""
    page_number: int
    background_pdf: Optional[str] = None
    elements: List[Dict[str, Any]] = []


class PDFTemplate(BaseModel):
    """Complete PDF template"""
    id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    page_size: str = "A4"
    orientation: str = "portrait"
    margins: Dict[str, float] = {"top": 15, "right": 15, "bottom": 15, "left": 15}
    pages: List[PageTemplate] = []
    placeholders: List[str] = []
    created_at: datetime
    updated_at: datetime


class YMLTemplateUpload(BaseModel):
    """YML template upload"""
    name: str
    yml_content: str
    background_pdf_base64: Optional[str] = None


class TemplateValidationResult(BaseModel):
    """Template validation result"""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    element_count: int
    page_count: int
    placeholders_found: List[str] = []


# ==================== Mock Data Store ====================

_templates_store: Dict[str, PDFTemplate] = {}


def generate_template_id() -> str:
    return f"tpl_{uuid.uuid4().hex[:8]}"


# ==================== Helper Functions ====================

def parse_yml_template(yml_content: str) -> Dict[str, Any]:
    """Parse YML template content"""
    try:
        return yaml.safe_load(yml_content)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YML Parse-Fehler: {str(e)}")


def validate_template(template_data: Dict[str, Any]) -> TemplateValidationResult:
    """Validate template structure"""
    errors = []
    warnings = []
    placeholders = []
    element_count = 0
    page_count = 0
    
    # Check required fields
    if "name" not in template_data:
        errors.append("Feld 'name' fehlt")
    
    if "pages" not in template_data:
        errors.append("Feld 'pages' fehlt")
    else:
        page_count = len(template_data["pages"])
        for page in template_data["pages"]:
            if "elements" in page:
                for elem in page["elements"]:
                    element_count += 1
                    
                    # Check coordinates
                    if "position" in elem:
                        pos = elem["position"]
                        if pos.get("x", 0) < 0 or pos.get("x", 0) > 210:
                            warnings.append(f"Element {elem.get('id', '?')}: X-Koordinate außerhalb A4")
                        if pos.get("y", 0) < 0 or pos.get("y", 0) > 297:
                            warnings.append(f"Element {elem.get('id', '?')}: Y-Koordinate außerhalb A4")
                    
                    # Find placeholders
                    if "placeholder" in elem:
                        placeholders.append(elem["placeholder"])
                    if "content" in elem and "{{" in str(elem["content"]):
                        import re
                        found = re.findall(r'\{\{(\w+)\}\}', str(elem["content"]))
                        placeholders.extend(found)
    
    return TemplateValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        element_count=element_count,
        page_count=page_count,
        placeholders_found=list(set(placeholders))
    )


def create_template_from_yml(yml_data: Dict[str, Any]) -> PDFTemplate:
    """Create PDFTemplate from parsed YML"""
    template_id = generate_template_id()
    now = datetime.now()
    
    pages = []
    for page_data in yml_data.get("pages", []):
        pages.append(PageTemplate(
            page_number=page_data.get("page_number", len(pages) + 1),
            background_pdf=page_data.get("background_pdf"),
            elements=page_data.get("elements", [])
        ))
    
    # Extract all placeholders
    placeholders = []
    for page in pages:
        for elem in page.elements:
            if "placeholder" in elem:
                placeholders.append(elem["placeholder"])
    
    return PDFTemplate(
        id=template_id,
        name=yml_data.get("name", "Unbenannt"),
        description=yml_data.get("description"),
        version=yml_data.get("version", "1.0"),
        page_size=yml_data.get("page_size", "A4"),
        orientation=yml_data.get("orientation", "portrait"),
        margins=yml_data.get("margins", {"top": 15, "right": 15, "bottom": 15, "left": 15}),
        pages=pages,
        placeholders=list(set(placeholders)),
        created_at=now,
        updated_at=now
    )


# ==================== API Endpoints ====================

@router.get("/")
async def get_templates():
    """Get all templates."""
    return {
        "templates": list(_templates_store.values()),
        "total": len(_templates_store)
    }


@router.post("/upload")
async def upload_yml_template(upload: YMLTemplateUpload):
    """Upload and parse YML template."""
    # Parse YML
    yml_data = parse_yml_template(upload.yml_content)
    yml_data["name"] = upload.name
    
    # Validate
    validation = validate_template(yml_data)
    if not validation.valid:
        raise HTTPException(status_code=400, detail={"errors": validation.errors})
    
    # Create template
    template = create_template_from_yml(yml_data)
    _templates_store[template.id] = template
    
    return {
        "template": template,
        "validation": validation,
        "message": "Template erfolgreich hochgeladen"
    }


@router.post("/validate")
async def validate_yml_template(yml_content: str):
    """Validate YML template without saving."""
    yml_data = parse_yml_template(yml_content)
    validation = validate_template(yml_data)
    
    return {
        "validation": validation,
        "parsed_structure": {
            "name": yml_data.get("name"),
            "pages": len(yml_data.get("pages", [])),
            "has_backgrounds": any(p.get("background_pdf") for p in yml_data.get("pages", []))
        }
    }


@router.get("/{template_id}")
async def get_template(template_id: str):
    """Get specific template."""
    if template_id not in _templates_store:
        raise HTTPException(status_code=404, detail="Template nicht gefunden")
    
    return {"template": _templates_store[template_id]}


@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """Delete template."""
    if template_id not in _templates_store:
        raise HTTPException(status_code=404, detail="Template nicht gefunden")
    
    del _templates_store[template_id]
    return {"deleted": True, "template_id": template_id}


@router.get("/{template_id}/elements")
async def get_template_elements(template_id: str, page: Optional[int] = None):
    """Get template elements."""
    if template_id not in _templates_store:
        raise HTTPException(status_code=404, detail="Template nicht gefunden")
    
    template = _templates_store[template_id]
    elements = []
    
    for p in template.pages:
        if page is None or p.page_number == page:
            for elem in p.elements:
                elem["page"] = p.page_number
                elements.append(elem)
    
    return {
        "template_id": template_id,
        "elements": elements,
        "total": len(elements)
    }


@router.put("/{template_id}/elements/{element_id}")
async def update_element(template_id: str, element_id: str, element_data: Dict[str, Any]):
    """Update single element in template."""
    if template_id not in _templates_store:
        raise HTTPException(status_code=404, detail="Template nicht gefunden")
    
    template = _templates_store[template_id]
    
    for page in template.pages:
        for i, elem in enumerate(page.elements):
            if elem.get("id") == element_id:
                page.elements[i] = {**elem, **element_data}
                template.updated_at = datetime.now()
                return {"element": page.elements[i], "updated": True}
    
    raise HTTPException(status_code=404, detail="Element nicht gefunden")


@router.get("/{template_id}/placeholders")
async def get_template_placeholders(template_id: str):
    """Get all placeholders in template."""
    if template_id not in _templates_store:
        raise HTTPException(status_code=404, detail="Template nicht gefunden")
    
    template = _templates_store[template_id]
    
    return {
        "template_id": template_id,
        "placeholders": template.placeholders,
        "total": len(template.placeholders)
    }


@router.post("/{template_id}/render")
async def render_template(template_id: str, data: Dict[str, Any]):
    """Render template with data (preview)."""
    if template_id not in _templates_store:
        raise HTTPException(status_code=404, detail="Template nicht gefunden")
    
    template = _templates_store[template_id]
    
    # Check for missing placeholders
    missing = [p for p in template.placeholders if p.strip("{}") not in data]
    
    return {
        "template_id": template_id,
        "data_provided": list(data.keys()),
        "placeholders_filled": len(template.placeholders) - len(missing),
        "missing_placeholders": missing,
        "ready_to_generate": len(missing) == 0
    }


@router.get("/sample/yml")
async def get_sample_yml():
    """Get sample YML template."""
    sample = """name: Standard-Angebot
description: 7-seitiges Standardangebot
version: "1.0"
page_size: A4
orientation: portrait
margins:
  top: 15
  right: 15
  bottom: 15
  left: 15

pages:
  - page_number: 1
    background_pdf: "templates/cover_background.pdf"
    elements:
      - id: company_logo
        type: image
        position: {x: 150, y: 15}
        width: 40
        height: 20
        placeholder: "{{company_logo}}"
      
      - id: title
        type: text
        position: {x: 20, y: 50}
        content: "ANGEBOT"
        font:
          family: Helvetica
          size: 24
          bold: true
          color: "#333333"
      
      - id: offer_number
        type: text
        position: {x: 20, y: 65}
        placeholder: "{{offer_number}}"
        font:
          size: 12
      
      - id: customer_name
        type: dynamic_text
        position: {x: 20, y: 100}
        placeholder: "{{customer_name}}"
        font:
          size: 14
          bold: true
      
      - id: customer_address
        type: dynamic_text
        position: {x: 20, y: 110}
        placeholder: "{{customer_address}}"
        font:
          size: 11
        max_lines: 3
        line_height: 1.3

  - page_number: 2
    elements:
      - id: section_title
        type: text
        position: {x: 20, y: 30}
        content: "Projektbeschreibung"
        font:
          size: 16
          bold: true
"""
    return {"sample_yml": sample}


@router.get("/element-types")
async def get_element_types():
    """Get available element types."""
    return {
        "element_types": [
            {"id": "text", "name": "Text", "description": "Statischer Text"},
            {"id": "dynamic_text", "name": "Dynamischer Text", "description": "Text mit Platzhalter"},
            {"id": "image", "name": "Bild", "description": "Bild oder Logo"},
            {"id": "line", "name": "Linie", "description": "Horizontale oder vertikale Linie"},
            {"id": "rectangle", "name": "Rechteck", "description": "Rechteck oder Box"},
            {"id": "table", "name": "Tabelle", "description": "Datentabelle"}
        ]
    }


@router.get("/fonts")
async def get_available_fonts():
    """Get available fonts."""
    return {
        "fonts": [
            {"id": "Helvetica", "name": "Helvetica", "styles": ["normal", "bold", "italic"]},
            {"id": "Arial", "name": "Arial", "styles": ["normal", "bold", "italic"]},
            {"id": "Times-Roman", "name": "Times Roman", "styles": ["normal", "bold", "italic"]},
            {"id": "Courier", "name": "Courier", "styles": ["normal", "bold"]}
        ]
    }


@router.get("/health/check")
async def health_check():
    """Health check for PDF template service."""
    return {
        "status": "healthy",
        "service": "pdf-template-system",
        "templates_count": len(_templates_store),
        "timestamp": datetime.now().isoformat()
    }
