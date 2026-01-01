"""
PDF Templates API Endpoints

Provides endpoints for managing PDF templates including:
- Listing available templates
- Uploading custom templates
- Updating template metadata
- Deleting templates
- Setting default templates
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import os
import json
from pathlib import Path
from datetime import datetime

from backend.services.pdf_service import get_pdf_service
from backend.core.auth_dependencies import get_current_user

router = APIRouter(prefix="/pdf", tags=["pdf"])


class TemplateMetadata(BaseModel):
    """Template metadata model"""
    name: str
    display_name: str
    description: str
    preview_image: Optional[str] = None
    is_custom: bool = False
    created_at: Optional[str] = None
    file_size: Optional[int] = None


class TemplateUpdateRequest(BaseModel):
    """Template update request model"""
    display_name: str
    description: str


# Template storage directory
TEMPLATES_DIR = Path("backend/pdf_templates")
TEMPLATES_METADATA_FILE = TEMPLATES_DIR / "templates_metadata.json"


def ensure_templates_dir():
    """Ensure templates directory exists"""
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    if not TEMPLATES_METADATA_FILE.exists():
        with open(TEMPLATES_METADATA_FILE, 'w') as f:
            json.dump({}, f)


def load_templates_metadata() -> dict:
    """Load templates metadata from file"""
    ensure_templates_dir()
    try:
        with open(TEMPLATES_METADATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_templates_metadata(metadata: dict):
    """Save templates metadata to file"""
    ensure_templates_dir()
    with open(TEMPLATES_METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)


def get_built_in_templates() -> List[TemplateMetadata]:
    """Get list of built-in templates"""
    pdf_service = get_pdf_service()
    templates = pdf_service.get_available_templates()
    
    return [
        TemplateMetadata(
            name=t['name'],
            display_name=t['display_name'],
            description=t['description'],
            is_custom=False
        )
        for t in templates
    ]


def get_custom_templates() -> List[TemplateMetadata]:
    """Get list of custom templates"""
    metadata = load_templates_metadata()
    templates = []
    
    for name, data in metadata.items():
        template_file = TEMPLATES_DIR / f"{name}.pdf"
        if template_file.exists():
            templates.append(TemplateMetadata(
                name=name,
                display_name=data.get('display_name', name),
                description=data.get('description', ''),
                is_custom=True,
                created_at=data.get('created_at'),
                file_size=template_file.stat().st_size
            ))
    
    return templates


@router.get("/templates", response_model=List[TemplateMetadata])
async def get_templates(current_user: dict = Depends(get_current_user)):
    """
    Get list of all available PDF templates (built-in and custom).
    
    Returns:
        List of template metadata
    """
    try:
        built_in = get_built_in_templates()
        custom = get_custom_templates()
        
        return built_in + custom
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": {"message": f"Failed to load templates: {str(e)}"}}
        )


@router.post("/templates/upload")
async def upload_template(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a custom PDF template.
    
    Args:
        file: Template file (PDF, HTML, or JSON)
        name: Template name
        description: Template description
        
    Returns:
        Success message with template metadata
    """
    try:
        ensure_templates_dir()
        
        # Validate file type
        allowed_types = ['application/pdf', 'text/html', 'application/json']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail={"error": {"message": "Invalid file type. Only PDF, HTML, and JSON files are allowed."}}
            )
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail={"error": {"message": "File size exceeds 10MB limit."}}
            )
        
        # Generate safe filename
        safe_name = name.replace(' ', '_').lower()
        file_extension = Path(file.filename).suffix
        template_file = TEMPLATES_DIR / f"{safe_name}{file_extension}"
        
        # Check if template already exists
        if template_file.exists():
            raise HTTPException(
                status_code=400,
                detail={"error": {"message": f"Template '{name}' already exists."}}
            )
        
        # Save file
        with open(template_file, 'wb') as f:
            f.write(content)
        
        # Save metadata
        metadata = load_templates_metadata()
        metadata[safe_name] = {
            'display_name': name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'file_type': file.content_type,
            'original_filename': file.filename
        }
        save_templates_metadata(metadata)
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "Template uploaded successfully",
                "template": {
                    "name": safe_name,
                    "display_name": name,
                    "description": description,
                    "file_size": len(content)
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": {"message": f"Failed to upload template: {str(e)}"}}
        )


@router.put("/templates/{template_name}")
async def update_template(
    template_name: str,
    update_data: TemplateUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update template metadata.
    
    Args:
        template_name: Name of the template to update
        update_data: Updated template metadata
        
    Returns:
        Success message
    """
    try:
        metadata = load_templates_metadata()
        
        if template_name not in metadata:
            raise HTTPException(
                status_code=404,
                detail={"error": {"message": f"Template '{template_name}' not found."}}
            )
        
        metadata[template_name]['display_name'] = update_data.display_name
        metadata[template_name]['description'] = update_data.description
        metadata[template_name]['updated_at'] = datetime.now().isoformat()
        
        save_templates_metadata(metadata)
        
        return JSONResponse(
            content={"message": "Template updated successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": {"message": f"Failed to update template: {str(e)}"}}
        )


@router.delete("/templates/{template_name}")
async def delete_template(
    template_name: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a custom template.
    
    Args:
        template_name: Name of the template to delete
        
    Returns:
        Success message
    """
    try:
        metadata = load_templates_metadata()
        
        if template_name not in metadata:
            raise HTTPException(
                status_code=404,
                detail={"error": {"message": f"Template '{template_name}' not found."}}
            )
        
        # Delete template file
        template_file = TEMPLATES_DIR / f"{template_name}.pdf"
        if template_file.exists():
            template_file.unlink()
        
        # Remove from metadata
        del metadata[template_name]
        save_templates_metadata(metadata)
        
        return JSONResponse(
            content={"message": "Template deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": {"message": f"Failed to delete template: {str(e)}"}}
        )


@router.post("/templates/{template_name}/set-default")
async def set_default_template(
    template_name: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Set a template as the default template.
    
    Args:
        template_name: Name of the template to set as default
        
    Returns:
        Success message
    """
    try:
        metadata = load_templates_metadata()
        
        # Check if template exists (built-in or custom)
        built_in_names = [t.name for t in get_built_in_templates()]
        if template_name not in metadata and template_name not in built_in_names:
            raise HTTPException(
                status_code=404,
                detail={"error": {"message": f"Template '{template_name}' not found."}}
            )
        
        # Clear previous default
        for name in metadata:
            if 'is_default' in metadata[name]:
                metadata[name]['is_default'] = False
        
        # Set new default
        if template_name in metadata:
            metadata[template_name]['is_default'] = True
        else:
            # For built-in templates, add to metadata
            metadata[template_name] = {
                'is_default': True,
                'is_built_in': True
            }
        
        save_templates_metadata(metadata)
        
        return JSONResponse(
            content={"message": f"Template '{template_name}' set as default"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": {"message": f"Failed to set default template: {str(e)}"}}
        )


@router.get("/templates/default")
async def get_default_template(current_user: dict = Depends(get_current_user)):
    """
    Get the default template.
    
    Returns:
        Default template metadata
    """
    try:
        metadata = load_templates_metadata()
        
        # Find default template
        for name, data in metadata.items():
            if data.get('is_default', False):
                if data.get('is_built_in', False):
                    # Return built-in template
                    built_in = get_built_in_templates()
                    for template in built_in:
                        if template.name == name:
                            return template
                else:
                    # Return custom template
                    custom = get_custom_templates()
                    for template in custom:
                        if template.name == name:
                            return template
        
        # If no default set, return first built-in template
        built_in = get_built_in_templates()
        if built_in:
            return built_in[0]
        
        raise HTTPException(
            status_code=404,
            detail={"error": {"message": "No templates available."}}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": {"message": f"Failed to get default template: {str(e)}"}}
        )
