"""
PDF Preview and Debug Tools API

Provides REST API for PDF preview and debugging:
- PDF preview in browser
- Quick preview (reduced) mode
- Full page-by-page preview
- Zoom functionality
- Layer overlay debug mode (grid)
- Coordinate verification tool

Requirements: funktionen.txt - "PDF-Vorschau-Funktion"
Task: 268. PDF Preview and Debug Tools
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import io
import base64

router = APIRouter(prefix="/pdf/preview", tags=["PDF Preview & Debug"])


# ==================== Enums ====================

class PreviewMode(str, Enum):
    QUICK = "quick"
    FULL = "full"
    DEBUG = "debug"


class OverlayType(str, Enum):
    NONE = "none"
    GRID = "grid"
    COORDINATES = "coordinates"
    MARGINS = "margins"
    SAFE_ZONES = "safe_zones"


class ZoomLevel(str, Enum):
    FIT_PAGE = "fit_page"
    FIT_WIDTH = "fit_width"
    PERCENT_50 = "50"
    PERCENT_75 = "75"
    PERCENT_100 = "100"
    PERCENT_150 = "150"
    PERCENT_200 = "200"


# ==================== Pydantic Models ====================

class PreviewRequest(BaseModel):
    """Request for PDF preview"""
    pdf_id: Optional[str] = None
    pdf_data: Optional[str] = None  # Base64 encoded PDF
    mode: PreviewMode = PreviewMode.FULL
    start_page: int = 1
    end_page: Optional[int] = None
    zoom: ZoomLevel = ZoomLevel.FIT_PAGE
    overlay: OverlayType = OverlayType.NONE


class PagePreview(BaseModel):
    """Single page preview data"""
    page_number: int
    width_px: int
    height_px: int
    thumbnail_base64: Optional[str] = None
    elements: List[Dict[str, Any]] = []


class PreviewResult(BaseModel):
    """Preview result"""
    pdf_id: str
    total_pages: int
    pages: List[PagePreview]
    mode: PreviewMode
    zoom_level: str
    overlay_enabled: bool


class CoordinatePoint(BaseModel):
    """Coordinate point for verification"""
    x_mm: float
    y_mm: float
    page: int = 1
    label: Optional[str] = None


class CoordinateVerification(BaseModel):
    """Coordinate verification request"""
    pdf_id: str
    points: List[CoordinatePoint]
    show_crosshairs: bool = True
    show_labels: bool = True


class DebugOverlay(BaseModel):
    """Debug overlay configuration"""
    overlay_type: OverlayType
    grid_spacing_mm: float = 10.0
    show_coordinates: bool = True
    show_margins: bool = True
    margin_mm: float = 15.0
    color: str = "#FF0000"
    opacity: float = 0.5


class ElementPosition(BaseModel):
    """Element position in PDF"""
    element_id: str
    element_type: str
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float
    page: int
    content: Optional[str] = None


class PDFAnalysis(BaseModel):
    """PDF analysis result"""
    pdf_id: str
    total_pages: int
    page_size_mm: Dict[str, float]
    elements: List[ElementPosition]
    fonts_used: List[str]
    images_count: int
    total_text_blocks: int


# ==================== Helper Functions ====================

def generate_mock_page_preview(page_num: int, width: int = 595, height: int = 842) -> PagePreview:
    """Generate mock page preview"""
    return PagePreview(
        page_number=page_num,
        width_px=width,
        height_px=height,
        thumbnail_base64=None,  # Would be actual thumbnail in production
        elements=[
            {"type": "text", "x": 50, "y": 50, "content": f"Seite {page_num}"},
            {"type": "image", "x": 100, "y": 200, "width": 200, "height": 150}
        ]
    )


def generate_grid_overlay_svg(width_mm: float, height_mm: float, spacing_mm: float) -> str:
    """Generate SVG grid overlay"""
    lines = []
    
    # Vertical lines
    x = 0
    while x <= width_mm:
        lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height_mm}" stroke="#ccc" stroke-width="0.5"/>')
        x += spacing_mm
    
    # Horizontal lines
    y = 0
    while y <= height_mm:
        lines.append(f'<line x1="0" y1="{y}" x2="{width_mm}" y2="{y}" stroke="#ccc" stroke-width="0.5"/>')
        y += spacing_mm
    
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_mm} {height_mm}">
        {"".join(lines)}
    </svg>'''


def analyze_pdf_structure(pdf_id: str) -> PDFAnalysis:
    """Analyze PDF structure (mock)"""
    return PDFAnalysis(
        pdf_id=pdf_id,
        total_pages=7,
        page_size_mm={"width": 210, "height": 297},
        elements=[
            ElementPosition(element_id="title_1", element_type="text", x_mm=20, y_mm=30, width_mm=170, height_mm=10, page=1, content="Angebot"),
            ElementPosition(element_id="logo_1", element_type="image", x_mm=150, y_mm=15, width_mm=40, height_mm=20, page=1),
            ElementPosition(element_id="table_1", element_type="table", x_mm=20, y_mm=100, width_mm=170, height_mm=80, page=3),
        ],
        fonts_used=["Helvetica", "Helvetica-Bold", "Arial"],
        images_count=5,
        total_text_blocks=45
    )


# ==================== API Endpoints ====================

@router.post("/generate")
async def generate_preview(request: PreviewRequest):
    """Generate PDF preview."""
    pdf_id = request.pdf_id or f"preview_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Determine page range
    total_pages = 7  # Mock
    start = request.start_page
    end = request.end_page or total_pages
    
    # Generate page previews
    pages = []
    for page_num in range(start, min(end + 1, total_pages + 1)):
        if request.mode == PreviewMode.QUICK and page_num > 3:
            break  # Quick mode only shows first 3 pages
        pages.append(generate_mock_page_preview(page_num))
    
    return PreviewResult(
        pdf_id=pdf_id,
        total_pages=total_pages,
        pages=pages,
        mode=request.mode,
        zoom_level=request.zoom.value,
        overlay_enabled=request.overlay != OverlayType.NONE
    )


@router.get("/page/{pdf_id}/{page_number}")
async def get_page_preview(
    pdf_id: str,
    page_number: int,
    zoom: ZoomLevel = ZoomLevel.FIT_PAGE,
    overlay: OverlayType = OverlayType.NONE
):
    """Get single page preview."""
    page = generate_mock_page_preview(page_number)
    
    overlay_svg = None
    if overlay == OverlayType.GRID:
        overlay_svg = generate_grid_overlay_svg(210, 297, 10)
    
    return {
        "page": page,
        "overlay_svg": overlay_svg,
        "zoom": zoom.value
    }


@router.get("/thumbnail/{pdf_id}/{page_number}")
async def get_page_thumbnail(pdf_id: str, page_number: int, size: int = Query(default=200, le=500)):
    """Get page thumbnail image."""
    # Mock thumbnail - in production would generate actual thumbnail
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{int(size * 1.414)}">
        <rect width="100%" height="100%" fill="#f0f0f0"/>
        <text x="50%" y="50%" text-anchor="middle" fill="#666">Seite {page_number}</text>
    </svg>'''
    
    return StreamingResponse(
        io.BytesIO(svg_content.encode()),
        media_type="image/svg+xml"
    )


@router.post("/debug/overlay")
async def apply_debug_overlay(pdf_id: str, overlay: DebugOverlay):
    """Apply debug overlay to PDF preview."""
    overlay_svg = None
    
    if overlay.overlay_type == OverlayType.GRID:
        overlay_svg = generate_grid_overlay_svg(210, 297, overlay.grid_spacing_mm)
    elif overlay.overlay_type == OverlayType.MARGINS:
        margin = overlay.margin_mm
        overlay_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297">
            <rect x="{margin}" y="{margin}" width="{210-2*margin}" height="{297-2*margin}" 
                  fill="none" stroke="{overlay.color}" stroke-width="0.5" stroke-dasharray="5,5"/>
        </svg>'''
    
    return {
        "pdf_id": pdf_id,
        "overlay_type": overlay.overlay_type.value,
        "overlay_svg": overlay_svg,
        "settings": overlay
    }


@router.post("/debug/coordinates")
async def verify_coordinates(verification: CoordinateVerification):
    """Verify coordinates on PDF."""
    results = []
    
    for point in verification.points:
        results.append({
            "point": point,
            "pixel_x": int(point.x_mm * 2.83465),  # mm to points at 72 DPI
            "pixel_y": int(point.y_mm * 2.83465),
            "valid": 0 <= point.x_mm <= 210 and 0 <= point.y_mm <= 297
        })
    
    # Generate crosshair SVG
    crosshair_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297">'
    for point in verification.points:
        if verification.show_crosshairs:
            crosshair_svg += f'''
                <line x1="{point.x_mm-5}" y1="{point.y_mm}" x2="{point.x_mm+5}" y2="{point.y_mm}" stroke="red" stroke-width="0.5"/>
                <line x1="{point.x_mm}" y1="{point.y_mm-5}" x2="{point.x_mm}" y2="{point.y_mm+5}" stroke="red" stroke-width="0.5"/>
            '''
        if verification.show_labels and point.label:
            crosshair_svg += f'<text x="{point.x_mm+3}" y="{point.y_mm-3}" font-size="3" fill="red">{point.label}</text>'
    crosshair_svg += '</svg>'
    
    return {
        "pdf_id": verification.pdf_id,
        "points_verified": len(results),
        "results": results,
        "crosshair_svg": crosshair_svg
    }


@router.get("/analyze/{pdf_id}")
async def analyze_pdf(pdf_id: str):
    """Analyze PDF structure and elements."""
    return analyze_pdf_structure(pdf_id)


@router.get("/elements/{pdf_id}")
async def get_pdf_elements(pdf_id: str, page: Optional[int] = None, element_type: Optional[str] = None):
    """Get PDF elements with positions."""
    analysis = analyze_pdf_structure(pdf_id)
    elements = analysis.elements
    
    if page:
        elements = [e for e in elements if e.page == page]
    if element_type:
        elements = [e for e in elements if e.element_type == element_type]
    
    return {
        "pdf_id": pdf_id,
        "elements": elements,
        "total": len(elements)
    }


@router.get("/viewer/{pdf_id}")
async def get_pdf_viewer(pdf_id: str):
    """Get embedded PDF viewer HTML."""
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>PDF Vorschau - {pdf_id}</title>
    <style>
        body {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; }}
        .toolbar {{ background: #333; color: white; padding: 10px; margin-bottom: 10px; }}
        .page-container {{ border: 1px solid #ccc; margin: 10px 0; background: white; }}
        .controls {{ display: flex; gap: 10px; align-items: center; }}
        button {{ padding: 5px 15px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="toolbar">
        <div class="controls">
            <button onclick="prevPage()">← Zurück</button>
            <span>Seite <span id="currentPage">1</span> von 7</span>
            <button onclick="nextPage()">Weiter →</button>
            <select onchange="setZoom(this.value)">
                <option value="fit">Seite anpassen</option>
                <option value="100">100%</option>
                <option value="150">150%</option>
                <option value="200">200%</option>
            </select>
            <label><input type="checkbox" onchange="toggleGrid(this.checked)"> Raster</label>
        </div>
    </div>
    <div id="pageContainer" class="page-container">
        <p style="padding: 20px;">PDF Vorschau für: {pdf_id}</p>
    </div>
    <script>
        let currentPage = 1;
        function prevPage() {{ if(currentPage > 1) currentPage--; updatePage(); }}
        function nextPage() {{ if(currentPage < 7) currentPage++; updatePage(); }}
        function updatePage() {{ document.getElementById('currentPage').textContent = currentPage; }}
        function setZoom(level) {{ console.log('Zoom:', level); }}
        function toggleGrid(show) {{ console.log('Grid:', show); }}
    </script>
</body>
</html>'''
    
    return HTMLResponse(content=html_content)


@router.get("/zoom-levels")
async def get_zoom_levels():
    """Get available zoom levels."""
    return {
        "zoom_levels": [
            {"id": "fit_page", "name": "Seite anpassen", "value": None},
            {"id": "fit_width", "name": "Breite anpassen", "value": None},
            {"id": "50", "name": "50%", "value": 0.5},
            {"id": "75", "name": "75%", "value": 0.75},
            {"id": "100", "name": "100%", "value": 1.0},
            {"id": "150", "name": "150%", "value": 1.5},
            {"id": "200", "name": "200%", "value": 2.0}
        ]
    }


@router.get("/overlay-types")
async def get_overlay_types():
    """Get available overlay types."""
    return {
        "overlay_types": [
            {"id": "none", "name": "Kein Overlay"},
            {"id": "grid", "name": "Raster", "description": "Millimeter-Raster"},
            {"id": "coordinates", "name": "Koordinaten", "description": "X/Y Koordinatenanzeige"},
            {"id": "margins", "name": "Ränder", "description": "Seitenränder anzeigen"},
            {"id": "safe_zones", "name": "Sichere Bereiche", "description": "Druckbare Bereiche"}
        ]
    }


@router.get("/health/check")
async def health_check():
    """Health check for PDF preview service."""
    return {
        "status": "healthy",
        "service": "pdf-preview-debug",
        "timestamp": datetime.now().isoformat()
    }
