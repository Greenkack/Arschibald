"""
3D Screenshot for PDF Integration API

Provides REST API for 3D screenshot export:
- Screenshot export functionality
- Isometric standard view (45°)
- Automatic PDF integration
- Multiple view angles
- High-resolution export

Requirements: funktionen.txt - "Screenshot-/Export-Funktion"
Task: 273. 3D Screenshot for PDF Integration
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import io
import base64
import uuid

router = APIRouter(prefix="/3d/screenshot", tags=["3D Screenshot Export"])


# ==================== Enums ====================

class ViewAngle(str, Enum):
    ISOMETRIC = "isometric"
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BIRD_EYE = "bird_eye"
    CUSTOM = "custom"


class ImageFormat(str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"
    SVG = "svg"


class Resolution(str, Enum):
    LOW = "low"  # 800x600
    MEDIUM = "medium"  # 1280x960
    HIGH = "high"  # 1920x1440
    ULTRA = "ultra"  # 3840x2880
    CUSTOM = "custom"


# ==================== Pydantic Models ====================

class CameraPosition(BaseModel):
    """Camera position for custom view"""
    x: float = 0
    y: float = -20
    z: float = 15
    target_x: float = 0
    target_y: float = 0
    target_z: float = 3
    fov: float = Field(default=45, ge=10, le=120)


class ScreenshotConfig(BaseModel):
    """Screenshot configuration"""
    view_angle: ViewAngle = ViewAngle.ISOMETRIC
    custom_camera: Optional[CameraPosition] = None
    resolution: Resolution = Resolution.HIGH
    custom_width: Optional[int] = None
    custom_height: Optional[int] = None
    format: ImageFormat = ImageFormat.PNG
    quality: int = Field(default=90, ge=1, le=100)
    transparent_background: bool = False
    background_color: str = "#FFFFFF"
    show_dimensions: bool = False
    show_compass: bool = True
    show_shadow: bool = True
    antialiasing: bool = True


class ScreenshotRequest(BaseModel):
    """Request for screenshot generation"""
    scene_id: str
    config: ScreenshotConfig = ScreenshotConfig()
    include_metadata: bool = True


class MultiViewRequest(BaseModel):
    """Request for multiple view screenshots"""
    scene_id: str
    views: List[ViewAngle] = [ViewAngle.ISOMETRIC, ViewAngle.FRONT, ViewAngle.TOP]
    config: ScreenshotConfig = ScreenshotConfig()


class ScreenshotResult(BaseModel):
    """Screenshot result"""
    screenshot_id: str
    scene_id: str
    view_angle: ViewAngle
    width: int
    height: int
    format: ImageFormat
    file_size_bytes: int
    image_base64: Optional[str] = None
    download_url: str
    created_at: datetime


class PDFIntegrationConfig(BaseModel):
    """Configuration for PDF integration"""
    position_x_mm: float = 20
    position_y_mm: float = 100
    width_mm: float = 170
    height_mm: Optional[float] = None  # Auto-calculate from aspect ratio
    caption: Optional[str] = None
    page_number: int = 1
    border: bool = False
    shadow: bool = False


class PDFScreenshotRequest(BaseModel):
    """Request for PDF-ready screenshot"""
    scene_id: str
    view_angle: ViewAngle = ViewAngle.ISOMETRIC
    pdf_config: PDFIntegrationConfig = PDFIntegrationConfig()
    dpi: int = Field(default=300, ge=72, le=600)


# ==================== Helper Functions ====================

def generate_screenshot_id() -> str:
    return f"scr_{uuid.uuid4().hex[:8]}"


def get_resolution_dimensions(resolution: Resolution, custom_w: Optional[int] = None, custom_h: Optional[int] = None) -> tuple:
    """Get pixel dimensions for resolution"""
    resolutions = {
        Resolution.LOW: (800, 600),
        Resolution.MEDIUM: (1280, 960),
        Resolution.HIGH: (1920, 1440),
        Resolution.ULTRA: (3840, 2880)
    }
    
    if resolution == Resolution.CUSTOM and custom_w and custom_h:
        return (custom_w, custom_h)
    
    return resolutions.get(resolution, (1920, 1440))


def get_camera_for_view(view: ViewAngle) -> CameraPosition:
    """Get camera position for predefined view"""
    views = {
        ViewAngle.ISOMETRIC: CameraPosition(x=15, y=-15, z=12, target_x=0, target_y=0, target_z=3),
        ViewAngle.FRONT: CameraPosition(x=0, y=-25, z=5, target_x=0, target_y=0, target_z=5),
        ViewAngle.BACK: CameraPosition(x=0, y=25, z=5, target_x=0, target_y=0, target_z=5),
        ViewAngle.LEFT: CameraPosition(x=-25, y=0, z=5, target_x=0, target_y=0, target_z=5),
        ViewAngle.RIGHT: CameraPosition(x=25, y=0, z=5, target_x=0, target_y=0, target_z=5),
        ViewAngle.TOP: CameraPosition(x=0, y=0, z=30, target_x=0, target_y=0, target_z=0, fov=60),
        ViewAngle.BIRD_EYE: CameraPosition(x=20, y=-20, z=25, target_x=0, target_y=0, target_z=0, fov=50)
    }
    return views.get(view, views[ViewAngle.ISOMETRIC])


def generate_mock_image(width: int, height: int, format: ImageFormat) -> bytes:
    """Generate mock image data (placeholder)"""
    # In production, this would render the actual 3D scene
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
        <rect width="100%" height="100%" fill="#f0f0f0"/>
        <rect x="10%" y="30%" width="80%" height="50%" fill="#8B4513" stroke="#333" stroke-width="2"/>
        <polygon points="{width//2},{height*0.15} {width*0.1},{height*0.3} {width*0.9},{height*0.3}" fill="#CD853F" stroke="#333"/>
        <rect x="20%" y="40%" width="15%" height="20%" fill="#1E1E32"/>
        <rect x="40%" y="40%" width="15%" height="20%" fill="#1E1E32"/>
        <rect x="60%" y="40%" width="15%" height="20%" fill="#1E1E32"/>
        <text x="50%" y="95%" text-anchor="middle" font-size="14" fill="#666">3D Visualisierung - {width}x{height}</text>
    </svg>'''
    return svg_content.encode('utf-8')


# ==================== Mock Data Store ====================

_screenshots_store: Dict[str, ScreenshotResult] = {}


# ==================== API Endpoints ====================

@router.post("/capture")
async def capture_screenshot(request: ScreenshotRequest):
    """Capture screenshot of 3D scene."""
    width, height = get_resolution_dimensions(
        request.config.resolution,
        request.config.custom_width,
        request.config.custom_height
    )
    
    # Generate screenshot
    image_data = generate_mock_image(width, height, request.config.format)
    screenshot_id = generate_screenshot_id()
    
    result = ScreenshotResult(
        screenshot_id=screenshot_id,
        scene_id=request.scene_id,
        view_angle=request.config.view_angle,
        width=width,
        height=height,
        format=request.config.format,
        file_size_bytes=len(image_data),
        image_base64=base64.b64encode(image_data).decode() if request.include_metadata else None,
        download_url=f"/api/v1/3d/screenshot/download/{screenshot_id}",
        created_at=datetime.now()
    )
    
    _screenshots_store[screenshot_id] = result
    
    return {"screenshot": result}


@router.post("/capture/multi-view")
async def capture_multi_view(request: MultiViewRequest):
    """Capture screenshots from multiple view angles."""
    results = []
    
    for view in request.views:
        config = request.config.copy()
        config.view_angle = view
        
        width, height = get_resolution_dimensions(config.resolution)
        image_data = generate_mock_image(width, height, config.format)
        screenshot_id = generate_screenshot_id()
        
        result = ScreenshotResult(
            screenshot_id=screenshot_id,
            scene_id=request.scene_id,
            view_angle=view,
            width=width,
            height=height,
            format=config.format,
            file_size_bytes=len(image_data),
            download_url=f"/api/v1/3d/screenshot/download/{screenshot_id}",
            created_at=datetime.now()
        )
        
        _screenshots_store[screenshot_id] = result
        results.append(result)
    
    return {
        "screenshots": results,
        "total": len(results)
    }


@router.post("/for-pdf")
async def capture_for_pdf(request: PDFScreenshotRequest):
    """Capture screenshot optimized for PDF integration."""
    # Calculate dimensions based on DPI and mm size
    width_px = int(request.pdf_config.width_mm * request.dpi / 25.4)
    height_px = int(width_px * 0.75)  # 4:3 aspect ratio
    
    if request.pdf_config.height_mm:
        height_px = int(request.pdf_config.height_mm * request.dpi / 25.4)
    
    image_data = generate_mock_image(width_px, height_px, ImageFormat.PNG)
    screenshot_id = generate_screenshot_id()
    
    result = ScreenshotResult(
        screenshot_id=screenshot_id,
        scene_id=request.scene_id,
        view_angle=request.view_angle,
        width=width_px,
        height=height_px,
        format=ImageFormat.PNG,
        file_size_bytes=len(image_data),
        image_base64=base64.b64encode(image_data).decode(),
        download_url=f"/api/v1/3d/screenshot/download/{screenshot_id}",
        created_at=datetime.now()
    )
    
    _screenshots_store[screenshot_id] = result
    
    return {
        "screenshot": result,
        "pdf_config": request.pdf_config,
        "dpi": request.dpi,
        "ready_for_pdf": True
    }


@router.get("/download/{screenshot_id}")
async def download_screenshot(screenshot_id: str):
    """Download screenshot image."""
    if screenshot_id not in _screenshots_store:
        raise HTTPException(status_code=404, detail="Screenshot nicht gefunden")
    
    result = _screenshots_store[screenshot_id]
    image_data = generate_mock_image(result.width, result.height, result.format)
    
    media_types = {
        ImageFormat.PNG: "image/png",
        ImageFormat.JPEG: "image/jpeg",
        ImageFormat.WEBP: "image/webp",
        ImageFormat.SVG: "image/svg+xml"
    }
    
    return StreamingResponse(
        io.BytesIO(image_data),
        media_type=media_types.get(result.format, "image/png"),
        headers={"Content-Disposition": f"attachment; filename=screenshot_{screenshot_id}.{result.format.value}"}
    )


@router.get("/view-angles")
async def get_view_angles():
    """Get available view angles."""
    return {
        "view_angles": [
            {"id": "isometric", "name": "Isometrisch (45°)", "description": "Standard-Ansicht", "recommended": True},
            {"id": "front", "name": "Vorderansicht", "description": "Frontale Ansicht"},
            {"id": "back", "name": "Rückansicht", "description": "Ansicht von hinten"},
            {"id": "left", "name": "Linke Seite", "description": "Seitenansicht links"},
            {"id": "right", "name": "Rechte Seite", "description": "Seitenansicht rechts"},
            {"id": "top", "name": "Draufsicht", "description": "Ansicht von oben"},
            {"id": "bird_eye", "name": "Vogelperspektive", "description": "Schräge Draufsicht"},
            {"id": "custom", "name": "Benutzerdefiniert", "description": "Eigene Kameraposition"}
        ]
    }


@router.get("/resolutions")
async def get_resolutions():
    """Get available resolutions."""
    return {
        "resolutions": [
            {"id": "low", "name": "Niedrig", "width": 800, "height": 600, "use_case": "Vorschau"},
            {"id": "medium", "name": "Mittel", "width": 1280, "height": 960, "use_case": "Web"},
            {"id": "high", "name": "Hoch", "width": 1920, "height": 1440, "use_case": "PDF", "recommended": True},
            {"id": "ultra", "name": "Ultra", "width": 3840, "height": 2880, "use_case": "Druck"},
            {"id": "custom", "name": "Benutzerdefiniert", "width": None, "height": None, "use_case": "Spezial"}
        ]
    }


@router.get("/formats")
async def get_image_formats():
    """Get available image formats."""
    return {
        "formats": [
            {"id": "png", "name": "PNG", "supports_transparency": True, "recommended_for": "PDF"},
            {"id": "jpeg", "name": "JPEG", "supports_transparency": False, "recommended_for": "Web"},
            {"id": "webp", "name": "WebP", "supports_transparency": True, "recommended_for": "Web"},
            {"id": "svg", "name": "SVG", "supports_transparency": True, "recommended_for": "Skalierbar"}
        ]
    }


@router.get("/{screenshot_id}")
async def get_screenshot_info(screenshot_id: str):
    """Get screenshot information."""
    if screenshot_id not in _screenshots_store:
        raise HTTPException(status_code=404, detail="Screenshot nicht gefunden")
    
    return {"screenshot": _screenshots_store[screenshot_id]}


@router.delete("/{screenshot_id}")
async def delete_screenshot(screenshot_id: str):
    """Delete screenshot."""
    if screenshot_id not in _screenshots_store:
        raise HTTPException(status_code=404, detail="Screenshot nicht gefunden")
    
    del _screenshots_store[screenshot_id]
    return {"deleted": True, "screenshot_id": screenshot_id}


@router.get("/health/check")
async def health_check():
    """Health check for screenshot service."""
    return {
        "status": "healthy",
        "service": "screenshot-export",
        "screenshots_count": len(_screenshots_store),
        "timestamp": datetime.now().isoformat()
    }
